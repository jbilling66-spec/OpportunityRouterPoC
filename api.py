"""FastAPI serving layer — the web front door to the Opportunity Router engine.

Run it:
    uvicorn api:app --reload

Endpoints
  GET  /health                 liveness check
  GET  /opportunities          list every processed opportunity (the dashboard feed)
  GET  /opportunities/{id}     one opportunity's full detail (the readout)
  POST /qualify                run the pipeline on document text; pauses at the review interrupt
  POST /upload                 accept a PDF, extract text, run the pipeline
  POST /review/{id}            leader action: accept | decline | return  (drives the ranked-offer loop)

State note (demo): processed opportunities live in an in-memory dict (OPPS), and paused graph
state lives in the InMemorySaver checkpointer keyed by thread_id. Both survive across requests
but NOT across a server restart (InMemorySaver holds checkpoints in process memory). The
checkpointer is swappable for SqliteSaver/PostgresSaver to survive restarts in production, where
OPPS would also become a DB-backed store. No auth: synthetic data only; the service-line filter
is a view lens, not access control.
"""
from __future__ import annotations

from dotenv import load_dotenv
load_dotenv()

import os
import tempfile
import threading
import uuid
from contextlib import asynccontextmanager
from pathlib import Path
from typing import Optional

from fastapi import FastAPI, UploadFile
from fastapi.concurrency import run_in_threadpool
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel

from langgraph.types import Command

from src.graph import agent
from src.ingestion.pdf_loader import pdf_to_text
from src.schemas import ServiceLine

@asynccontextmanager
async def lifespan(app: FastAPI):
    # Optional demo convenience: when SEED_ON_STARTUP is truthy, populate the dashboard with the
    # bundled sample documents on boot — so a cold visitor never lands on an empty board on a host
    # whose free tier wipes in-memory state on idle spin-down. Runs in a background thread so it
    # never blocks startup; off by default so normal deploys pay nothing.
    if os.environ.get("SEED_ON_STARTUP", "").strip().lower() in ("1", "true", "yes"):
        threading.Thread(target=_seed_samples, daemon=True).start()
    yield


app = FastAPI(title="Opportunity Router — a cross-sell source multiplier", lifespan=lifespan)

# CORS allowlist from env (comma-separated); unset or "*" leaves it open, which is fine for the
# synthetic-data demo. Set ALLOWED_ORIGINS to your frontend domain to lock it down in production.
_origins_env = os.environ.get("ALLOWED_ORIGINS", "*").strip()
_allow_origins = ["*"] if _origins_env in ("", "*") else [o.strip() for o in _origins_env.split(",")]
app.add_middleware(CORSMiddleware, allow_origins=_allow_origins, allow_methods=["*"], allow_headers=["*"])

# In-memory store of processed opportunities, keyed by the thread_id used to run/resume the graph.
# Demo-only: a real deployment persists this. thread_id doubles as the opportunity id.
OPPS: dict[str, dict] = {}


# --- shaping the engine's result into JSON the browser can render ------------

def _candidates(sl_cls) -> list[dict]:
    if not sl_cls:
        return []
    return [{"service_line": c.service_line.value,
             "confidence": round(c.confidence, 2),
             "reasoning": c.reasoning}
            for c in sl_cls.ranked_candidates]


def _review_log(result: dict) -> list[dict]:
    out = []
    for d in result.get("review_log", []) or []:
        out.append({
            "action": d.action.value,
            "offered_service_line": d.offered_service_line.value,
            "corrected_service_line": d.corrected_service_line.value if d.corrected_service_line else None,
            "note": d.note,
        })
    return out


def _pending_offer(result: dict) -> Optional[dict]:
    """If the graph is paused at the review interrupt, return the offer payload; else None."""
    intr = result.get("__interrupt__")
    if not intr:
        return None
    return intr[0].value


def _snapshot(thread_id: str, result: dict) -> dict:
    """The full record for one opportunity: the readout + status + any pending review offer."""
    ex = result.get("extracted")
    sl_cls = result.get("service_line_classification")
    eng_cls = result.get("engagement_classification")
    qual = result.get("qualification")
    fit = result.get("fit")
    routing = result.get("routing")
    primary = sl_cls.primary if sl_cls else None
    offer = _pending_offer(result)

    if offer is not None:
        status = "needs_review"          # paused at the interrupt, waiting on a leader
    elif routing is not None:
        status = "routed"                # loop finished (accept/decline/exhausted)
    else:
        status = "processed"

    return {
        "id": thread_id,
        "status": status,
        "organization": getattr(ex, "organization", None),
        "vertical": getattr(ex, "vertical", None),
        "summary": getattr(ex, "summary", None),
        "service_line": primary.service_line.value if primary else None,
        "service_line_confidence": round(primary.confidence, 2) if primary else None,
        "engagement_type": getattr(eng_cls, "engagement_type", None),
        "engagement_confidence": round(eng_cls.confidence, 2) if eng_cls else None,
        "ranked_candidates": _candidates(sl_cls),
        "fit_score": getattr(fit, "score", None),
        "fit_band": getattr(fit, "band", None),
        "decision_summary": getattr(qual, "decision_summary", None),
        "deal_shape": getattr(qual, "deal_shape", None),
        "team_package": getattr(qual, "team_package", None),
        "target_team": getattr(routing, "target_team", None),
        "auto_routed": getattr(routing, "auto_routed", None),
        "routing_reason": getattr(routing, "reason", None),
        "current_offer": offer,          # {offered_to, team, offer_index, remaining_after_this, ...} or None
        "review_log": _review_log(result),
    }


def _run_and_store(text: str, source: str) -> dict:
    thread_id = str(uuid.uuid4())
    config = {"configurable": {"thread_id": thread_id}}
    result = agent.invoke({"document_text": text, "source": source, "errors": []}, config)
    snap = _snapshot(thread_id, result)
    OPPS[thread_id] = snap
    return snap


def _seed_samples() -> None:
    """Run every bundled sample document through the pipeline so the dashboard isn't empty.
    Best-effort: a failure on one document (e.g. missing API key) is logged and skipped, not fatal.
    Invoked from the lifespan hook only when SEED_ON_STARTUP is set."""
    data_dir = Path(__file__).resolve().parent / "data"
    for path in sorted(data_dir.glob("*.txt")):
        try:
            _run_and_store(path.read_text(encoding="utf-8"), "seed")
        except Exception as exc:  # never let seeding crash the server
            print(f"[seed] skipped {path.name}: {exc}")


# --- endpoints ---------------------------------------------------------------

@app.get("/health")
def health() -> dict:
    return {"status": "ok"}


@app.get("/opportunities")
def list_opportunities(service_line: Optional[str] = None) -> dict:
    """The dashboard feed. Optional ?service_line= filters to one line (the POV lens)."""
    items = list(OPPS.values())
    if service_line:
        items = [o for o in items if o.get("service_line") == service_line]
    return {"opportunities": items, "service_lines": [s.value for s in ServiceLine]}


@app.get("/opportunities/{opportunity_id}")
def get_opportunity(opportunity_id: str) -> dict:
    return OPPS.get(opportunity_id, {"error": "not found"})


class QualifyRequest(BaseModel):
    document_text: str
    source: str = "api"


@app.post("/qualify")
def qualify(req: QualifyRequest) -> dict:
    return _run_and_store(req.document_text, req.source)


def _process_upload(raw: bytes, filename: str) -> dict:
    """Decode/parse the uploaded bytes and run the pipeline. Blocking (PDF parse + LLM calls)."""
    name = (filename or "").lower()
    if name.endswith(".pdf"):
        with tempfile.NamedTemporaryFile(suffix=".pdf", delete=False) as tmp:
            tmp.write(raw)
            tmp_path = tmp.name
        text = pdf_to_text(tmp_path)
    else:
        # plain text (.txt or anything decodable) — decode directly, no PDF parsing
        text = raw.decode("utf-8", errors="replace")
    return _run_and_store(text, "upload")


@app.post("/upload")
async def upload(file: UploadFile) -> dict:
    raw = await file.read()
    # PDF parsing and the pipeline are blocking and slow; run them off the event loop so a single
    # upload doesn't stall other requests (e.g. /health) on a single-worker deploy.
    return await run_in_threadpool(_process_upload, raw, file.filename or "")


class ReviewRequest(BaseModel):
    action: str                                  # "accept" | "decline" | "return"
    corrected_service_line: Optional[str] = None  # on "return", optional gold-label hint
    note: Optional[str] = None


@app.post("/review/{opportunity_id}")
def review(opportunity_id: str, req: ReviewRequest) -> dict:
    """Resume the paused graph for this opportunity with the leader's decision.

    Uses the checkpointer: the thread_id (== opportunity_id) locates the paused state, and
    Command(resume=...) feeds the decision back into the review() node. A 'return' advances the
    ranked offer and re-pauses (or exhausts); accept/decline terminate.
    """
    if opportunity_id not in OPPS:
        return {"error": "not found"}
    config = {"configurable": {"thread_id": opportunity_id}}
    decision = {"action": req.action}
    if req.corrected_service_line:
        decision["corrected_service_line"] = req.corrected_service_line
    if req.note:
        decision["note"] = req.note
    result = agent.invoke(Command(resume=decision), config)
    snap = _snapshot(opportunity_id, result)
    OPPS[opportunity_id] = snap
    return snap


# --- serve the dashboard webpage --------------------------------------------
# The API serves data (above) AND the dashboard page (here), so one server does both.
from fastapi.responses import FileResponse

# Absolute path so the page serves regardless of the process's working directory.
_DASHBOARD = Path(__file__).resolve().parent / "static" / "index.html"


@app.get("/")
def dashboard() -> FileResponse:
    return FileResponse(_DASHBOARD)