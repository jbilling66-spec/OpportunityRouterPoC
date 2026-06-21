"""Evaluators. The headline metric is two-tier routing/classification correctness, fed by partner
send-backs (the gold labels from /review 'return')."""
from __future__ import annotations

def service_line_correct(outputs: dict, reference_outputs: dict) -> dict:
    """Tier 1: did we pick the right service line (the routing key)?"""
    pred = (outputs.get("service_line") or "").lower()
    exp = (reference_outputs.get("service_line") or "").lower()
    return {"key": "service_line_correct", "score": 1.0 if pred == exp and pred else 0.0}

def engagement_type_correct(outputs: dict, reference_outputs: dict) -> dict:
    """Tier 2: within the line, the right engagement type (which skill qualified it)?"""
    pred = (outputs.get("engagement_type") or "").lower()
    exp = (reference_outputs.get("engagement_type") or "").lower()
    return {"key": "engagement_type_correct", "score": 1.0 if pred == exp and pred else 0.0}

def routed_to_right_team(outputs: dict, reference_outputs: dict) -> dict:
    pred = (outputs.get("target_team") or "").lower()
    exp = (reference_outputs.get("target_team") or "").lower()
    return {"key": "routed_to_right_team", "score": 1.0 if pred == exp and pred else 0.0}

def fit_score_sane(outputs: dict) -> dict:
    s = outputs.get("fit_score")
    return {"key": "fit_score_sane", "score": 1.0 if isinstance(s, int) and 0 <= s <= 100 else 0.0}

ALL_EVALUATORS = [service_line_correct, engagement_type_correct, routed_to_right_team, fit_score_sane]
