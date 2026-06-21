"""FastAPI serving layer.

    uvicorn api:app --reload

Endpoints
  GET  /health
  POST /qualify          run the pipeline on document text, return the routed result
  POST /qualify/stream   SSE — emit each node as it executes (lifecycle hooks / live trace)
  POST /upload           accept a PDF, extract text, run the pipeline  (the BDR's entry point)
  POST /review/{id}      partner action: accept | ignore | return  (the human-in-the-loop)

The /review endpoint is the eval flywheel: a 'return' (mis-routed) is a GOLD label that
feeds the LangSmith dataset, so routing accuracy is measured and improves over time. 'ignore'
is noisier (could be mis-route or just not interested), so it's recorded but not used as a label.
"""

from __future__ import annotations

import json
import tempfile
from typing import Optional

from fastapi import FastAPI, UploadFile
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import StreamingResponse
from pydantic import BaseModel

from src.graph import agent
from src.ingestion.pdf_loader import pdf_to_text
from src.research.profile_agent import research_prospect
from src.schemas import ReviewStatus

app = FastAPI(title="Opportunity Router — a cross-sell source multiplier")
app.add_middleware(CORSMiddleware, allow_origins=["*"], allow_methods=["*"], allow_headers=["*"])

RUN_CONFIG = {"tags": ["opportunity-router"], "metadata": {"surface": "api"}}


class QualifyRequest(BaseModel):
    document_text: str
    source: str = "upload"


def _result_payload(result: dict) -> dict:
    ex, qual, fit, cls, routing = (
        result.get("extracted"), result.get("qualification"),
        result.get("fit"), result.get("classification"), result.get("routing"),
    )
    return {
        "organization": getattr(ex, "organization", None),
        "vertical": getattr(ex, "vertical", None),
        "summary": getattr(ex, "summary", None),
        "work_type": getattr(cls, "work_type", None) and cls.work_type.value,
        "confidence": getattr(cls, "confidence", None),
        "fit_score": getattr(fit, "score", None),
        "fit_band": getattr(fit, "band", None),
        "decision_summary": getattr(qual, "decision_summary", None),
        "deal_shape": getattr(qual, "deal_shape", None),
        "team_package": getattr(qual, "team_package", None),
        "target_team": getattr(routing, "target_team", None),
        "auto_routed": getattr(routing, "auto_routed", None),
        "routing_reason": getattr(routing, "reason", None),
    }


@app.get("/health")
def health() -> dict:
    return {"status": "ok"}


@app.post("/qualify")
def qualify(req: QualifyRequest) -> dict:
    result = agent.invoke(
        {"document_text": req.document_text, "source": req.source, "errors": []},
        config=RUN_CONFIG,
    )
    return _result_payload(result)


@app.post("/upload")
async def upload(file: UploadFile) -> dict:
    with tempfile.NamedTemporaryFile(suffix=".pdf", delete=False) as tmp:
        tmp.write(await file.read())
        tmp_path = tmp.name
    text = pdf_to_text(tmp_path)
    result = agent.invoke({"document_text": text, "source": "upload", "errors": []},
                          config=RUN_CONFIG)
    return _result_payload(result)


def _sse(event: str, data: dict) -> str:
    return f"event: {event}\ndata: {json.dumps(data, default=str)}\n\n"


@app.post("/qualify/stream")
def qualify_stream(req: QualifyRequest) -> StreamingResponse:
    def gen():
        final = {}
        for chunk in agent.stream(
            {"document_text": req.document_text, "source": req.source, "errors": []},
            stream_mode="updates", config=RUN_CONFIG,
        ):
            for node, update in chunk.items():
                final.update(update)
                payload = {"node": node}
                if update.get("classification"):
                    payload["work_type"] = update["classification"].work_type.value
                if update.get("fit"):
                    payload["fit_score"] = update["fit"].score
                if update.get("routing"):
                    payload["target_team"] = update["routing"].target_team
                yield _sse("node", payload)
        yield _sse("done", _result_payload(final))

    return StreamingResponse(gen(), media_type="text/event-stream")


class ReviewRequest(BaseModel):
    action: str  # "accept" | "ignore" | "return"
    note: Optional[str] = None


@app.post("/review/{opportunity_id}")
def review(opportunity_id: str, req: ReviewRequest) -> dict:
    """Partner action. A 'return' is the gold eval label; persist it for the dataset.
    Persistence is left to your store (DB/queue); this records the intent."""
    status = {
        "accept": ReviewStatus.ACCEPTED,
        "ignore": ReviewStatus.IGNORED,
        "return": ReviewStatus.RETURNED_FOR_REANALYSIS,
    }.get(req.action, ReviewStatus.UNDER_REVIEW)
    is_eval_label = status == ReviewStatus.RETURNED_FOR_REANALYSIS
    # [FILL IN] persist {opportunity_id, status, note}; if is_eval_label, append to eval dataset.
    return {"opportunity_id": opportunity_id, "status": status.value,
            "captured_as_eval_label": is_eval_label}


class ResearchRequest(BaseModel):
    organization: str
    context: str = ""


@app.post("/research/{opportunity_id}")
async def research(opportunity_id: str, req: ResearchRequest) -> dict:
    """On-demand prospect research via the Claude Agent SDK agent (decoupled from the spine).
    Wired to the readout's 'Build prospect profile' button. Traced into LangSmith via @traceable."""
    profile = await research_prospect(req.organization, req.context)
    return {"opportunity_id": opportunity_id, "profile": profile}
