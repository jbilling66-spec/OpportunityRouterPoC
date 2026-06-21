"""Evaluators. The headline metric is routing/classification correctness, fed by partner
send-backs (the gold labels from /review 'return')."""
from __future__ import annotations

def classification_correct(outputs: dict, reference_outputs: dict) -> dict:
    pred = (outputs.get("work_type") or "").lower()
    exp = (reference_outputs.get("work_type") or "").lower()
    return {"key": "classification_correct", "score": 1.0 if pred == exp and pred else 0.0}

def routed_to_right_team(outputs: dict, reference_outputs: dict) -> dict:
    pred = (outputs.get("target_team") or "").lower()
    exp = (reference_outputs.get("target_team") or "").lower()
    return {"key": "routed_to_right_team", "score": 1.0 if pred == exp and pred else 0.0}

def fit_score_sane(outputs: dict) -> dict:
    s = outputs.get("fit_score")
    return {"key": "fit_score_sane", "score": 1.0 if isinstance(s, int) and 0 <= s <= 100 else 0.0}

ALL_EVALUATORS = [classification_correct, routed_to_right_team, fit_score_sane]
