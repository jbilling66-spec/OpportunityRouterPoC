"""Run the routing eval. `python evals/dataset.py` then `python evals/run_eval.py`."""
from __future__ import annotations
import uuid
from langsmith import evaluate
from evals.dataset import DATASET_NAME
from evals.evaluators import ALL_EVALUATORS
from src.graph import agent

def target(inputs: dict) -> dict:
    # The graph is compiled with a checkpointer, so invoke needs a thread_id. It runs up to the
    # review interrupt (route has already executed by then), and we read the two-tier
    # classification + routing off the returned state.
    config = {"configurable": {"thread_id": str(uuid.uuid4())}}
    r = agent.invoke({"document_text": inputs["document_text"], "source": "eval", "errors": []}, config)
    sl_cls = r.get("service_line_classification")
    eng_cls = r.get("engagement_classification")
    fit, routing = r.get("fit"), r.get("routing")
    primary = sl_cls.primary if sl_cls else None
    return {"service_line": primary.service_line.value if primary else None,
            "engagement_type": eng_cls.engagement_type if eng_cls else None,
            "target_team": routing.target_team if routing else None,
            "fit_score": fit.score if fit else None}

def main():
    res = evaluate(target, data=DATASET_NAME, evaluators=ALL_EVALUATORS,
                   experiment_prefix="opp-routing", max_concurrency=2)
    print(f"done: {res.experiment_name}")

if __name__ == "__main__":
    main()
