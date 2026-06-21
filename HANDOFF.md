# Work Package Handoff — Opportunity Router (a cross-sell source multiplier)

Context transfer for building this in a fresh conversation (Claude desktop app + Claude Code).
Self-contained: assumes the next assistant has none of the prior thread. Pair this with
`DEPLOYMENT.md` (the one-day execution order).

---

## 0. How to use this handoff

1. Re-upload: `opportunity-router.zip` (repo) and `OpportunityRouter.jsx` (frontend, two views).
2. Paste the kickoff message (§11).
3. Follow `DEPLOYMENT.md` for the day's order. First task: fill the skill rubrics with real
   criteria + capability grounding, then stand it up.

> The repo is the **starting point**. It currently has the flat four-work-type model; the
> two-tier refactor (§4) is build step 2. Python is syntax-checked only — not yet run.

---

## 1. What this is

A coordination layer for an audit / tax / advisory / consulting / accounting firm — a
**cross-sell source multiplier.** The problem isn't that anyone can't read a PDF; it's that
opportunities get *heard* in one service line and die because nothing surfaces and routes them
to the others. This turns scattered, individually-heard opportunities into shared, routed,
reviewable deal flow. Core value: **communication across silos.**

Workflow: a **BDR** does the broad human catch-all (find RFP/RFI PDFs anywhere, upload them).
The **agent** does the expensive pass — extract → classify (service line, then engagement type)
→ qualify via the matching skill → score ICP fit → route to the right team with a compiled,
ready-to-work package. **Partners** review daily (accept / ignore / return). It's
**augmentation, not automation**: the human makes the go/no-go from a ten-second summary; the
agent makes that fast and the handoff accurate.

---

## 2. Why it's being built (strategy)

One asset, two applications:
- **Anthropic — Applied AI Architect:** weights architecture rigor, the eval flywheel, the
  human-in-the-loop posture, the executive-facing artifact, *and* the fact that this is a real
  coordination gap the builder's own firm lives with. Manage: tenure (~3 yrs vs 5+). 
- **LangChain — Deployed Engineer:** a deployed app on LangGraph + LangSmith *is* the demo;
  cost-discipline (single agent, not multi-agent) and client-fit framing matter.

---

## 3. Decided architecture & the reasoning (defend in interviews)

**Single agent, deterministic skill routing — not multi-agent.** Per Anthropic's published
guidance, multi-agent burns ~15× the tokens of chat and fits *parallel, independent* tasks;
dependent, shared-context workflows (this) are won by a single agent / deterministic pipeline.

**Skills carry specialization, not sub-agents.** SKILL.md bundles load via progressive
disclosure. Because the classifier decides the type explicitly, skills load **deterministically**
off that output (auditable, reproducible — good for the readout's provenance and for evals). The
files are authored Agent-SDK-compatible, so they stay drop-in for native model-invocation later.

**Framework answer ("why not the Claude Agent SDK?"):** tools chosen by client fit/portability;
LangGraph for an explicit, inspectable state machine; LangSmith for framework-agnostic
observability; author SDK-compatible skills, load them deterministically for auditability. And
note: the project uses **both** — the Claude Agent SDK powers the decoupled research agent (§5),
so the answer isn't "LangChain over Anthropic's SDK," it's "each framework where it fits."

**Relevance gate (handles "doesn't fit the mold at all").** Right after extraction, before
service-line classification, a gate asks *"is this even our kind of work?"* — grounded in the
firm's service lines (`config/icp.py SERVICE_LINES`). It returns in_scope (continue),
out_of_scope (clear non-fit → a **"Not a fit" terminal** with the reason recorded), or uncertain
(borderline → flows on to classification, where the confidence gate catches it for human review).
**Calibrated to discard only CLEAR non-fits** — a shipbuilding RFP at an accounting firm gets
labeled out-of-scope with a reason instead of force-fit into a service line. Discarded items are
**not deleted** — they land in a visible "Not a fit" lane so a partner can still override.
Design principle for the stress-test question: never silently trash a real opportunity (a missed
deal is invisible and unrecoverable; a misroute just costs ten seconds), so ambiguity → human,
not the bin. (Already wired into the spine: `check_relevance` node + `discard` terminal.)

---

## 4. Two-tier classification (the generalization)

The four work-types (implementation, managed services, optimization, pre-implementation) are
just the **technology-delivery** lens — not the whole firm. So classification is two tiers:

```
Tier 1: SERVICE LINE      (technology-implementation | audit-advisory | tax | accounting | ...)
Tier 2: ENGAGEMENT TYPE   (per service line — NOT a universal list)
```

Engagement types are service-line-specific: tech-delivery has implementation / MS / optimization
/ pre-implementation; audit-advisory has its own (e.g. financial-statement audit, SOC reporting,
compliance readiness, strategy advisory); tax has its own (compliance vs planning vs provision).

This maps one-to-one onto the skills tree, which is why it's *less* complexity, not more:
```
skills/<service_line>/<engagement_type>/SKILL.md
```
Adding a service line = adding a folder; the classifier and spine don't change.

**Build for the slice: TWO service lines deep** — `technology-implementation` (its 4 engagement
skills already exist) and `audit-advisory` (new). Everything else = clearly-marked stubs (north
star). Don't author every line's judgment — that's how it balloons.

**Capability grounding (the lean win):** instead of hand-authoring every rubric, paste the firm's
real published "what we offer" capability blurb into each skill as grounding context, so matching
is anchored in actual services. (Full "upload sites in the UI → auto-build skills" is a
fast-follow, not day one.)

Refactor steps: add a `ServiceLine` enum + a service-line classifier node before the
engagement-type classifier; make `skills/loader.py` navigate two levels; add the `audit-advisory`
skill folder with grounded rubric templates.

---

## 5. Research agent — built on the Claude Agent SDK (use both frameworks)

A **separate** agent — the one place a web-facing, autonomous pattern is justified (read-heavy
enrichment, not the spine). Deliberately built on the **Claude Agent SDK**, NOT LangGraph, so the
project uses **both frameworks, each where it fits**: LangGraph for the deterministic, auditable
qualification spine; the Agent SDK for the autonomous, web-facing research agent where its native
tool loop + web search shine. That tool-choice-by-fit decision is a strong interview point and
demonstrates fluency with Anthropic's own SDK alongside the LangChain stack. (`src/research/profile_agent.py`.)

System prompt defines the fields to surface: firmographics, recent triggers, leadership, tech
footprint, likely needs, outreach hooks. Returns a parsed profile dict.

- **Decoupled:** on-demand from the readout ("Build prospect profile") → `POST /research/{id}`.
  Never inside the qualification graph.
- **Observability stays intertwined:** the research call is wrapped in LangSmith's `@traceable`,
  so even though it's a *different runtime*, it appears in the **same LangSmith project** as the
  spine — one pane of glass across both frameworks. (This is the honest answer to "how do you
  observe the non-LangGraph agent?")
- **Grounded + honest:** web-search-backed, **cites sources, flags uncertainty.** A
  confidently-wrong profile about a real company is an outreach liability.
- **Runtime footprint (honest tradeoff):** the Agent SDK wraps the Claude Code runtime (Node/CLI),
  so it's heavier to deploy than a plain API call. Worth it for the dual-framework story; if the
  deploy fights you, run the research agent **locally for the recording** — the LangGraph spine is
  what must be deployed. Verify the SDK's tool names/options against current docs (it evolves).
- Keep the simple single-agent shape; the orchestrator-worker parallel version is "later if
  research gets broad," not today.

---

## 6. Persistence, UI, ingestion

- **SQLite** (`store.py`): one file, no server. Persist each result, serve the dashboard from it,
  update status on review. Seed sample data on startup so the demo never opens empty. (Postgres
  is a later, internal-deployment concern.)
- **UI = the platform surface.** `OpportunityRouter.jsx` is two views (triage dashboard +
  per-opportunity readout). Add **drag-drop PDF upload** → `POST /upload`. Add a **"Not a fit"
  lane** in the dashboard for relevance-gate discards (visible, with reason, partner-overridable).
  Visual identity is the builder's to own — restyle freely.
- **Ingestion is source-agnostic.** Manual PDF upload is the first adapter; the pipeline only
  sees `document_text`. Harden OCR/large-doc handling as needed.

---

## 7. LangSmith — unified observability across both frameworks (first-class)

**Everything reports into LangSmith — the question is depth, not presence.**
- **Spine: automatic + deep.** Env vars on → every run traces (every node, Claude call, skill
  load), tagged `opportunity-router`, zero added code. Node-level spans natively.
- **Agent SDK research agent: traced via `@traceable`,** so it appears in the *same* project; its
  internal tool/step events are captured into the run so you see what it did inside the loop.
- **For uniform per-tool-call depth across both runtimes → the OpenTelemetry bridge.** LangSmith
  ingests OTLP traces: set `LANGSMITH_OTEL_ENABLED=true` and point an OTEL exporter at LangSmith's
  OTLP endpoint, and any OTEL-emitting runtime's spans flow in with full depth — vendor-neutral,
  no lock-in. This is the "agents shouldn't be an observability island" pattern, and **"I unified
  observability across two agent runtimes via OpenTelemetry into one LangSmith pane" is a strong
  architect-level line.** Honest caveat: verify what the Agent SDK actually emits (GenAI OTEL
  conventions are still maturing); the `@traceable` path is the guaranteed-works baseline.
- **The dashboard is native — configure, don't build.** Traces, latency, token cost, error rate
  are there. Optionally turn on one automation rule (online evaluator / alert) on the tag.
- **The recording must show a trace + an eval run** — that's the observability story.
- **Stretch only:** embedding LangSmith metrics into the React app via the LangSmith API.

---

## 8. The eval flywheel

A partner "return — mis-routed" (`POST /review/{id}` action `return`) is a gold-labeled
correction → grows the LangSmith routing dataset → classification/routing accuracy is measured
and improves. "Ignore" is noisy (recorded, not a label). The human-in-the-loop for correctness
doubles as the data engine. **Out-of-scope cases are eval cases too:** the seed dataset includes
a shipbuilding RFP expected to land as `not_a_fit`, so the relevance gate is tested, not assumed —
useful when a reviewer stress-tests with a deliberate bad fit.

---

## 9. ICP & verticals (what the skills grade against)

**Firmographics:** enterprise / upper-mid-market (mid-market only when it leans enterprise);
US-headquartered preferred. **Verticals (10):** Energy · Construction · Communications & Media ·
Financial Services · Health Care · Government (Federal + State & Local) · Higher Education ·
Life Sciences · Real Estate · Tribal & Gaming. (In `src/config/icp.py`.) Per-engagement fit
criteria live in each skill as `[FILL IN]` templates — real domain judgment, author them first.

---

## 10. Scope discipline & the one-day cut

North star: firm-wide, all service lines, partners reviewing daily. Buildable slice (one day):
two service lines deep, upload→classify→qualify→route→review, simple research agent, deployed,
recorded. See `DEPLOYMENT.md` for the ordered execution plan with stop-points. Build the slice;
keep the vision as north star; be ready to say which is which.

> This is a strong scaffold, not a finished portfolio piece. The version that survives an
> interview is the one filled with real criteria, run, and walkable line by line. Start with the
> skills — they're the most genuinely yours.

---

## 11. Kickoff message to paste into the new conversation

> Continuing a build — full context in `HANDOFF.md`, execution order in `DEPLOYMENT.md`, plus the
> repo (`opportunity-router.zip`) and frontend (`OpportunityRouter.jsx`). It's a
> professional-services "cross-sell source multiplier": a BDR uploads RFP/RFI PDFs; a single-agent
> LangGraph pipeline extracts → classifies service line then engagement type → qualifies via a
> deterministically-loaded skill → scores ICP fit → routes to the right team, with a partner
> review loop feeding a LangSmith eval flywheel, plus a decoupled web-search research agent for
> prospect profiles. LangSmith tracing is wired throughout. It's a one-day public portfolio demo
> (Vercel + Render) for an Anthropic Applied AI Architect and a LangChain Deployed Engineer
> application. Read the handoff and DEPLOYMENT.md, then let's start at Step 1: run it locally and
> confirm traces, then build the two-tier classifier with my two service lines. I'm in the
> desktop app with Claude Code.
