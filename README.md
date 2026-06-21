# Opportunity Router — a cross-sell source multiplier

A professional-services firm hears opportunities in a hundred corners and loses them because
there's no mechanism to surface and route them across service lines. This is that mechanism:
a BDR drops in an RFP/RFI, the agent extracts and classifies it, a matching **skill** qualifies
it and compiles a team-ready package, it **scores ICP fit**, and it **routes** the opportunity to
the right practice — with a human-in-the-loop review step where a service-line leader confirms,
declines, or corrects the call.

It's augmentation, not automation, of the decision that carries risk: a leader still makes the
go/no-go. The agent makes the qualified summary appear in seconds, preps the handoff, and learns
from every correction.

## Architecture

A single shared-context LangGraph agent with a **two-tier classifier** and a cyclic
human-in-the-loop review loop:


Two-tier classification is the core design: **Tier 1** picks the service line (the routing key),
**Tier 2** picks the engagement type within that line (which selects the qualifying skill). A
two-gate confidence check means low-confidence calls go to human review rather than guessing —
the system defers when uncertain instead of misrouting.

Specialization happens *inside one shared-context agent* via deterministically loaded skills, not
multiple agents — the right call for a dependent, shared-context workflow (multi-agent burns far
more tokens and shines only for parallel, independent tasks).

## Scope (deliberate)

Two service lines are built to full depth — **technology-implementation** and **audit-advisory** —
each with four engagement-type skills (eight total). The classifier returns `unclear` for anything
not confidently one of these, routing it to human review. This is intentional: prove the two-tier
pattern on two lines well, degrade gracefully on the rest. Adding a line = a `ServiceLine` enum
value + `ENGAGEMENT_TYPES` entry + a `skills/<line>/` folder.

## Skills are the heart (`src/skills/<line>/<engagement>/SKILL.md`)

Eight web-grounded skill rubrics, each encoding the qualification logic, the ICP signals that
matter *for that engagement type*, deal-shape heuristics, and the package to compile for the
downstream team. They load deterministically off the classifier (auditable, reproducible). Each is
grounded in the firm's real published capabilities and fact-checked, not invented.

## The eval flywheel

When a leader marks a routed opportunity **return — misrouted** (`POST /review/{id}` with `return`,
optionally naming the correct line), that's a gold-labeled correction destined for the LangSmith
routing dataset, so routing accuracy is *measured* and improves over time. **Decline** (correct
route, passing) and **accept** (correct route, taken) are terminal and not training labels.

## Web app

A React dashboard (`static/index.html`, served by FastAPI) over the engine:

- **Pipeline dashboard** — every processed opportunity, filterable by service line (the POV lens)
  plus an `unclear` filter for the human-review pile.
- **Detail view** — click a deal for the full readout: decision summary, deal shape, ranked
  service-line candidates with reasoning, fit, routing, and the compiled team package.
- **Review lane** — accept / decline / reassign actions that resume the paused graph through the
  web layer, closing the human-in-the-loop live.
- **Upload** — drop a `.txt` or `.pdf`, the pipeline runs, the new deal appears.

## Endpoints (`api.py`)

| Endpoint | Purpose |
|---|---|
| `GET /` | the dashboard |
| `GET /opportunities` | dashboard feed (optional `?service_line=` filter) |
| `GET /opportunities/{id}` | one opportunity's full detail |
| `POST /qualify` | run the pipeline on raw text |
| `POST /upload` | upload a `.txt`/`.pdf` → run the pipeline |
| `POST /review/{id}` | leader action: accept / decline / return (human-in-the-loop + eval label) |

## State (demo)

The opportunity list is in-memory; the LangGraph checkpointer holds paused-review state within a
server session. This is a deliberate demo scope: production would persist opportunities in a
database and swap the checkpointer for a durable store (SqliteSaver/PostgresSaver) so paused
reviews survive restarts. The checkpointer abstraction makes that a contained change.

## Run it

```bash
conda activate opprouter            # or your venv; Python 3.11
pip install -r requirements.txt
# set ANTHROPIC_API_KEY in .env
python run.py data/sample_rfp.txt   # CLI smoke test
uvicorn api:app --reload            # serving layer + dashboard at http://127.0.0.1:8000
python seed.py                      # load sample opportunities into the dashboard
```

## ICP (`src/config/icp.py`)

Enterprise / upper-mid-market, US-headquartered preferred. Verticals: energy, construction,
communications & media, financial services, health care, government (federal + state & local),
higher education, life sciences, real estate, tribal & gaming. Tune freely.