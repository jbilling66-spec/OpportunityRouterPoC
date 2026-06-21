"""Routing: service line -> downstream team, gated by confidence at both tiers.

This is where the human-in-the-loop gate lives: high-confidence, real-fit opportunities get a
target team and fire the webhook; low-confidence, 'unclear', or stub-line cases are flagged for
human review instead of guessing. The Tier-1 service line is the routing key; the Tier-2
engagement type drove which skill qualified it.
"""
from __future__ import annotations
from .config import icp
from .schemas import (ServiceLine, ServiceLineClassification, EngagementClassification,
                      FitScore, Qualification, RoutingDecision, ExtractedOpportunity)
from . import notifications

# Service line -> the team that owns the response. Tune to the firm's org.
TEAM_MAP = {
    ServiceLine.TECHNOLOGY_IMPLEMENTATION: "delivery / proposal team",
    ServiceLine.AUDIT_ADVISORY: "assurance / audit engagement team",
    ServiceLine.TAX: "tax practice",
    ServiceLine.ACCOUNTING: "outsourced accounting",
    ServiceLine.RISK_ADVISORY: "risk advisory",
}


def decide(sl_cls: ServiceLineClassification, eng_cls: EngagementClassification,
           fit: FitScore, qual: Qualification,
           extracted: ExtractedOpportunity | None) -> RoutingDecision:
    primary = sl_cls.primary
    gate = icp.AUTO_ROUTE_CONFIDENCE_GATE

    # Gate 1: no confident service line (none, 'unclear', or below the gate) -> human review.
    if primary is None or primary.service_line == ServiceLine.UNCLEAR \
            or primary.confidence < gate:
        conf = f"{primary.confidence:.2f}" if primary else "n/a"
        return RoutingDecision(
            target_team="human_review", auto_routed=False,
            reason=f"Service-line confidence {conf} below gate {gate} — partner confirms before routing.")

    # Gate 2: service line is confident, but the engagement type isn't -> human review.
    if eng_cls.confidence < gate:
        return RoutingDecision(
            target_team="human_review", auto_routed=False,
            reason=f"Service line '{primary.service_line.value}' confident, but engagement "
                   f"'{eng_cls.engagement_type}' confidence {eng_cls.confidence:.2f} below gate — partner confirms.")

    # Both tiers clear -> route. The human still makes the go/no-go; this is a jump-start, not a verdict.
    team = TEAM_MAP.get(primary.service_line, "human_review")
    notifications.notify_routed(team, qual, fit, extracted)
    return RoutingDecision(
        target_team=team, auto_routed=True,
        reason=f"Routed to {team}: {primary.service_line.value} / {eng_cls.engagement_type} "
               f"(line {primary.confidence:.2f}, engagement {eng_cls.confidence:.2f}), fit {fit.score}/{fit.band}.")