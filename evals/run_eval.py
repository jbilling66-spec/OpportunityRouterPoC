"""Run the routing eval. `python evals/dataset.py` then `python evals/run_eval.py`."""
from __future__ import annotations
from langsmith import evaluate
from evals.dataset import DATASET_NAME
from evals.evaluators import ALL_EVALUATORS
from src.graph import agent

def target(inputs: dict) -> dict:
    r = agent.invoke({"document_text": inputs["document_text"], "source": "eval", "errors": []})
    cls, fit, routing = r.get("classification"), r.get("fit"), r.get("routing")
    return {"work_type": cls.work_type.value if cls else None,
            "target_team": routing.target_team if routing else None,
            "fit_score": fit.score if fit else None}

def main():
    res = evaluate(target, data=DATASET_NAME, evaluators=ALL_EVALUATORS,
                   experiment_prefix="opp-routing", max_concurrency=2)
    print(f"done: {res.experiment_name}")

if __name__ == "__main__":
    main()
