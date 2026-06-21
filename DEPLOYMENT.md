# Deployment Plan — Opportunity Router (one-day portfolio demo)

Target: a clickable public demo (Vercel frontend + Render backend), synthetic data, no auth,
**with a recorded walkthrough as the safety net.** LangSmith is wired through as the
observability layer, not an afterthought.

The order below is designed so you have something *whole* at every stop — if time runs out,
you ship what you've reached, and it still demos.

---

## Ground rules for the day

- **These estimates assume you're directing Claude Code, not hand-writing.** The build steps
  (2–4) compress a lot — roughly half — because they're well-specified code generation. The
  saved hours don't vanish, they **move**: the parts Claude Code does *not* speed up are
  authoring the real skill criteria (your judgment), reviewing output well enough to walk it in
  an interview, and the deploy (external systems — cold starts, env vars, CORS). Bank the saved
  build time into judgment and the recording, not "done early." Realistic: steps 1–4 in ~3–4
  focused hours, which makes deploy *and* recording achievable in one day rather than stretch.
- **Synthetic data only.** No real client documents. This removes auth, security, and
  confidentiality from scope entirely — the whole reason a public demo is the right call.
- **The recording is the deliverable that always works.** Live deploys get flaky (cold
  starts, rate limits). A 3-minute screen recording lands in any interview regardless. Treat
  the live URL as the bonus, the recording as the floor.
- **Stop-points are real.** Each step's "Done when" is a place you could stop and still have a
  coherent thing to show.

---

## Step 1 — Run the existing repo locally (≈30 min)

```bash
python -m venv .venv && source .venv/bin/activate      # Python 3.11 / 3.12
pip install -r requirements.txt
cp .env.example .env     # ANTHROPIC_API_KEY, LANGSMITH_API_KEY, LANGSMITH_PROJECT
set -a && source .env && set +a
python run.py data/sample_rfp.txt
uvicorn api:app --reload      # then open http://127.0.0.1:8000/docs
```
**LangSmith check:** open your LangSmith project — the run from `run.py` should already be
there as a full trace (extract → classify → qualify → score → route). If it is, observability
is live; everything you build next inherits it automatically.
**Done when:** the pipeline runs end to end and you can see the trace in LangSmith.

## Step 2 — Two-tier classifier + two service lines deep (≈2–3 hr)

The build detail is in `HANDOFF.md §Architecture`. In short: add a **service-line** classifier
before the engagement-type one; reorganize skills to `skills/<service_line>/<engagement>/SKILL.md`;
build **technology-implementation** (already have its 4 engagement skills) and **audit & advisory**
(new). Ground each skill with a pasted "what we offer" capability blurb from the firm's site.
The **relevance gate** (catches clear non-fits like a shipbuilding RFP → "Not a fit") is already
wired into the spine — just ground it by tuning `SERVICE_LINES` in `config/icp.py`.
**Done when:** an audit/compliance RFP routes to advisory, an ERP RFP routes to delivery, and a
shipbuilding RFP lands as "Not a fit" — all visible in the trace.

## Step 3 — Wire the UI + PDF upload + SQLite (≈2 hr)

- Wire `OpportunityRouter.jsx` to the API: dashboard ← results, readout ← `/qualify/stream` (SSE).
- Add **drag-drop PDF upload** → `POST /upload` → new card appears in the dashboard.
- Add **SQLite** (`store.py`): persist each result, serve the dashboard from it, update status on
  review. Seed a few sample opportunities on startup so the demo never opens empty.
- Add a **"Not a fit" lane** to the dashboard for relevance-gate discards (visible, with reason).
**Done when:** you can drop a PDF in the browser and watch it qualify, route, and persist.

## Step 4 — Research agent on the Claude Agent SDK (≈1.5–2 hr)

Built on the **Claude Agent SDK** (deliberately a different framework from the LangGraph spine —
"use both"): web search + a system prompt defining the fields (firmographics, recent triggers,
leadership, tech footprint, likely needs, outreach hooks). On-demand from the readout via
`POST /research/{id}`. **Must cite sources and flag uncertainty.** Wrapped in LangSmith's
`@traceable` so it shows up alongside the spine. Spec in `HANDOFF.md §5`.
- **Footprint caveat:** the Agent SDK wraps the Claude Code runtime (Node/CLI), so it's heavier
  to deploy. If the deploy fights you, run this **locally for the recording** — only the spine
  must be deployed. Verify the SDK's tool names/options against current docs.
**Done when:** clicking the button returns a sourced prospect profile, traced in LangSmith.

## Step 5 — Deploy (first stretch goal; ≈1–1.5 hr)

**Backend → Render** (Web Service from the repo):
- Build: `pip install -r requirements.txt`
- Start: `uvicorn api:app --host 0.0.0.0 --port $PORT`
- Env: `ANTHROPIC_API_KEY`, `LANGSMITH_TRACING=true`, `LANGSMITH_API_KEY`, `LANGSMITH_PROJECT`,
  `ROUTING_WEBHOOK_URL` (optional)
- Caveats (be aware, they're fine for a demo): free tier **spins down on idle** (cold start
  ~30–60s — warm it before recording), and the disk is **ephemeral** (SQLite resets on
  redeploy — fine because you seed sample data on startup).

**Frontend → Vercel:**
- Set the API base URL env var to your Render URL.
- Build: `npm run build`, output `dist`.
- Lock backend CORS to the Vercel domain (currently `*` for dev).
**Done when:** the Vercel URL loads and talks to the Render backend.

## Step 6 — Record the 3-minute walkthrough (the safety net; ≈30 min)

Script: (1) the problem in one line — opportunities heard in one service line die because
nothing routes them; (2) drop a PDF, watch it classify service line → engagement type → route;
(3) open the readout, click "Build prospect profile"; (4) **cut to LangSmith** — show the live
trace lighting up the path, then the routing eval experiment with scores; (5) one line on the
architecture decision (single agent + deterministic skills, not multi-agent) and the eval
flywheel (partner send-backs become labels).
**Done when:** you have a clean recording. This is your floor — everything above is upside.

---

## LangSmith observability — explicit setup

- **Tracing is automatic.** Env vars on, and every spine run traces with zero added code; each is
  tagged `opportunity-router`. The classifier nodes trace too.
- **The Agent SDK research agent reports in too** via `@traceable` — same project, with its
  internal tool steps captured into the run.
- **Unified depth (the architect line):** for full per-tool-call depth across both runtimes, set
  `LANGSMITH_OTEL_ENABLED=true` and point an OTEL exporter at LangSmith's OTLP endpoint — both
  frameworks report into one pane, vendor-neutral. Verify the Agent SDK's OTEL emission first;
  the `@traceable` path is the baseline that always works.
- **The dashboard is native — you configure, not build.** Traces, latency, token cost, error
  rate. Optionally turn on one automation rule (online evaluator / alert) on the tag.
- **Capture a trace for the recording** — the trace lighting up is the observability story.
- **Stretch only:** surfacing LangSmith metrics back into your own React dashboard via the API.

---

## If you only get halfway

Steps 1–4 (local, working, uploadable, with research) are the impressive core and are very
doable in a day. Steps 5–6 are deploy + recording. If the live deploy fights you, **stop and
record locally** — a recording of the local app plus a live LangSmith trace is a complete,
convincing portfolio piece on its own.
