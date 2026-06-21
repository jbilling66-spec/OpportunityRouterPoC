"""Prospect-research agent — built on the CLAUDE AGENT SDK (deliberately not LangGraph).

Why a different framework here: the qualification spine is a deterministic, auditable LangGraph
pipeline; this is an autonomous, web-facing research agent where the Agent SDK's native tool
loop + web search shine. "Use both, each where it fits" — and unify their observability so the
project shows range without becoming an observability island.

OBSERVABILITY — everything lands in LangSmith, with depth:
- This function is wrapped in LangSmith's @traceable, so the run appears in the SAME LangSmith
  project as the spine.
- The agent's internal tool/step events are captured below and attached to the run, so you see
  WHAT it did inside the loop, not just the final profile.
- For full per-tool-call nested spans across both runtimes, use the OpenTelemetry bridge:
  set LANGSMITH_OTEL_ENABLED=true and point an OTEL exporter at LangSmith's OTLP endpoint
  (see DEPLOYMENT.md / HANDOFF §7). That's the vendor-neutral "one pane of glass" path.
  Verify what telemetry the Agent SDK emits — GenAI OTEL conventions are still maturing.

HONEST NOTES: the Agent SDK API (tool names, message shapes, options) evolves and is NOT
runnable in this sandbox — verify against current docs. The lazy import keeps the rest of the
app runnable without the SDK installed.
"""
from __future__ import annotations

import json

from langsmith import traceable

RESEARCH_SYSTEM = (
    "You are a B2B prospect-research analyst. Research the given organization using web search "
    "and return ONLY a JSON object with keys: firmographics, recent_triggers (news/events that "
    "create a need), leadership, tech_footprint, likely_needs, outreach_hooks, sources (URLs you "
    "actually used), uncertainties (what you could NOT confirm). Cite sources for claims and be "
    "explicit about what is unverified — a confidently wrong profile is worse than an incomplete one."
)


def _extract_tool_events(message) -> list[dict]:
    """Best-effort capture of tool/search events from a streamed SDK message, for trace depth.
    Defensive because the SDK message shape evolves — verify against current docs."""
    events = []
    blocks = getattr(message, "content", None) or []
    if not isinstance(blocks, (list, tuple)):
        return events
    for b in blocks:
        btype = getattr(b, "type", None) or (b.get("type") if isinstance(b, dict) else None)
        if btype in ("tool_use", "server_tool_use", "web_search_tool_result"):
            name = getattr(b, "name", None) or (b.get("name") if isinstance(b, dict) else btype)
            events.append({"tool": name, "type": btype})
    return events


@traceable(name="prospect_research_agent", run_type="chain")
async def research_prospect(organization: str, context: str = "") -> dict:
    """Run the Agent SDK research agent for one organization; return a parsed profile dict.
    Traced into LangSmith via @traceable; internal tool steps captured into the run."""
    try:
        from claude_agent_sdk import query, ClaudeAgentOptions
    except ImportError as e:
        raise RuntimeError("claude-agent-sdk not installed; see requirements.txt") from e

    options = ClaudeAgentOptions(
        system_prompt=RESEARCH_SYSTEM,
        allowed_tools=["WebSearch"],   # native web search — verify tool name vs. current SDK
        max_turns=6,
    )
    prompt = f"Research this prospect: {organization}.\nOpportunity context: {context}"

    text = ""
    trace_steps: list[dict] = []
    async for message in query(prompt=prompt, options=options):
        trace_steps.extend(_extract_tool_events(message))
        chunk = getattr(message, "text", None)
        if chunk:
            text += chunk

    raw = text.strip().removeprefix("```json").removeprefix("```").removesuffix("```").strip()
    try:
        profile = json.loads(raw)
    except Exception:
        profile = {"profile_text": text, "uncertainties": ["Could not parse structured JSON."]}

    # Attach the internal steps so they're visible inside the LangSmith run.
    profile["_trace_steps"] = trace_steps
    return profile
