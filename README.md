# Opportunity Router — a cross-sell source multiplier

A professional-services firm hears opportunities in a hundred corners and loses them because
there's no mechanism to surface and route them across service lines. This is that mechanism: a
BDR uploads any RFP/RFI PDF, the agent extracts and **classifies the work type**, a matching
**skill** qualifies it and compiles a team-ready package, it **scores ICP fit**, and it
**routes** the opportunity (with the package) to the right practice for a partner to act on.

It's augmentation, not automation, of the decision that carries risk: the salesperson still
makes the go/no-go from a ten-second summary. The agent makes that summary appear in seconds
and preps the handoff so the moment they say "go," the right teams already have what they need.

## Architecture (single agent, deterministic skill routing)

```
upload PDF → extract → classify work type → qualify (load matching SKILL.md) → score ICP fit → route
                 └─(junk)→ insufficient_info → human review
```

Work-type specialization happens *inside one shared-context agent* via a deterministically
loaded skill — not multiple agents. That's the right call for a dependent, shared-context
workflow (multi-agent burns ~15× the tokens and shines only for parallel, independent tasks).

## Skills are the heart (`src/skills/*/SKILL.md`)

Four authored, Agent-SDK-compatible skill bundles — implementation, managed-services,
optimization, pre-implementation — each encoding the qualification rubric, the ICP signals
that matter *for that work type*, the deal-shape heuristics, and the package to compile for
its downstream team. They load deterministically off the classifier (auditable, reproducible),
and stay drop-in for native model-invocation later. **The `[FILL IN]` markers are where your
domain judgment goes** — they're templates, deliberately.

## The eval flywheel

When a partner marks a routed opportunity "return — mis-routed" (`POST /review/{id}` with
`return`), that's a gold-labeled correction. It feeds the LangSmith routing dataset, so
classification/routing accuracy is *measured* and improves over time. ("Ignore" is noisier —
recorded, not used as a label.)

## Endpoints (`api.py`)

| Endpoint | Purpose |
|---|---|
| `POST /upload` | BDR uploads a PDF → extract → full pipeline |
| `POST /qualify` | Run the pipeline on raw text |
| `POST /qualify/stream` | SSE — one event per node (live trace / lifecycle hooks) |
| `POST /review/{id}` | Partner action: accept / ignore / return (human-in-the-loop + eval label) |

## Run it

```bash
python -m venv .venv && source .venv/bin/activate          # Python 3.11 / 3.12
pip install -r requirements.txt
cp .env.example .env   # ANTHROPIC_API_KEY, LANGSMITH_API_KEY, (optional) ROUTING_WEBHOOK_URL
set -a && source .env && set +a
python run.py data/sample_rfp.txt        # smoke test
uvicorn api:app --reload                 # serving layer + /docs
python evals/dataset.py && python evals/run_eval.py
```

## ICP (`src/config/icp.py`)

Enterprise / upper-mid-market, US-headquartered preferred. Verticals: energy, construction,
communications & media, financial services, health care, government (federal + state & local),
higher education, life sciences, real estate, tribal & gaming. Tune the file freely.

## North star vs. buildable slice

The full vision is a firm-wide, multi-service-line hub partners review daily. The honest
*buildable slice* is one service line, end to end: upload → classify → qualify → route →
partner review → accept/return. Build the slice; keep the vision as the north star; be ready
to say which is which.

> Nothing here has been run end-to-end yet — syntax-checked only. First local step is to stand
> it up with real keys. PDF ingestion is a pragmatic baseline; harden OCR/large-doc handling
> as you go.
