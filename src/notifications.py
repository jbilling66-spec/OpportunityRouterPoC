"""Outbound webhook — the routing delivery mechanism.

When an opportunity routes, post a compiled, team-ready package to a Slack-compatible
webhook so the right service line sees it with everything they need to start. Fails silently.
This is decision-SUPPORT: the partner still makes the go/no-go.
"""
from __future__ import annotations
import os
import httpx

def notify_routed(team, qual, fit, extracted=None) -> bool:
    url = os.environ.get("ROUTING_WEBHOOK_URL")
    if not url:
        return False
    org = getattr(extracted, "organization", None) or "Opportunity"
    text = (f":inbox_tray: *New opportunity → {team}*  ({org}, fit {fit.score}/{fit.band})\n"
            f"{qual.decision_summary}\n_Deal shape:_ {qual.deal_shape}")
    try:
        httpx.post(url, json={"text": text}, timeout=5)
        return True
    except httpx.HTTPError:
        return False
