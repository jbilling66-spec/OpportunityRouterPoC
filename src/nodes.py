"""Pipeline nodes + routers.

Two-tier flow:
  extract -> check_relevance -> classify_service_line (Tier 1, ranked)
          -> classify_engagement (Tier 2, per service line) -> qualify_with_skill
          -> score_fit -> route

The two classifier outputs are the routing key; the matching skill loads deterministically
inside qualify_with_skill via load_skill(service_line, engagement_type).
"""

from __future__ import annotations
from langgraph.types import interrupt
from . import routing
from .config import icp
from .llm import get_agent_llm
from .schemas import (
    EngagementClassification,
    ExtractedOpportunity,
    FitScore,
    Qualification,
    Relevance,
    RelevanceCheck,
    ReviewAction,
    ReviewDecision,
    RoutingDecision,
    ServiceLine,
    ServiceLineCandidate,
    ServiceLineClassification,
    ENGAGEMENT_TYPES,
)
from .skills.loader import load_skill
from .state import OpportunityState

# --- extract -----------------------------------------------------------------

_EXTRACT_SYS = (
    "You are a professional-services capture analyst. Extract the buying organization, the "
    "best-guess industry vertical, a one-paragraph summary a salesperson can act on in ten "
    "seconds, and the concrete scope signals. Record only what's stated; don't invent."
)


def extract(state: OpportunityState) -> dict:
    llm = get_agent_llm().with_structured_output(ExtractedOpportunity)
    try:
        result: ExtractedOpportunity = llm.invoke(
            [("system", _EXTRACT_SYS), ("human", state["document_text"])]
        )
    except Exception as exc:
        return {"extraction_status": "junk",
                "errors": state.get("errors", []) + [f"extract_failed: {exc}"]}
    return {"extracted": result,
            "extraction_status": "ok" if result.is_usable() else "junk"}


def route_after_extract(state: OpportunityState) -> str:
    return "check_relevance" if state.get("extraction_status") == "ok" else "insufficient_info"


# --- relevance gate: "is this even our kind of work?" ------------------------

_RELEVANCE_SYS = (
    "Decide whether this opportunity is plausibly deliverable by a professional-services firm "
    "whose service lines are: " + ", ".join(icp.SERVICE_LINES) + ". "
    "Return 'in_scope' if it could fit any of them, 'out_of_scope' ONLY for a clear non-fit "
    "(e.g. shipbuilding, physical construction labor, manufacturing a product), and 'uncertain' "
    "if it's borderline. Bias toward 'uncertain' over 'out_of_scope' — never discard something "
    "that might be real. Give a one-sentence reason."
)


def check_relevance(state: OpportunityState) -> dict:
    ex: ExtractedOpportunity = state["extracted"]
    llm = get_agent_llm().with_structured_output(RelevanceCheck)
    payload = f"SUMMARY: {ex.summary}\nVERTICAL: {ex.vertical}\nSCOPE:\n- " + "\n- ".join(ex.scope_signals)
    try:
        result: RelevanceCheck = llm.invoke([("system", _RELEVANCE_SYS), ("human", payload)])
    except Exception as exc:
        result = RelevanceCheck(verdict=Relevance.UNCERTAIN, reason=f"relevance_check_failed: {exc}")
    return {"relevance": result}


def route_after_relevance(state: OpportunityState) -> str:
    rel: RelevanceCheck = state["relevance"]
    return "discard" if rel.verdict == Relevance.OUT_OF_SCOPE else "classify_service_line"


def discard(state: OpportunityState) -> dict:
    """Terminal for clear non-fits. NOT deleted — surfaced in a 'Not a fit' lane with the reason."""
    rel: RelevanceCheck = state.get("relevance")
    reason = rel.reason if rel else "Outside the firm's service lines."
    return {"routing": RoutingDecision(
        target_team="not_a_fit", auto_routed=False, reason=f"Out of scope — {reason}")}


# --- Tier 1: classify SERVICE LINE (ranked) ----------------------------------

_SERVICE_LINE_SYS = (
    "Classify which of the firm's service lines this opportunity belongs to. The service lines "
    "are:\n"
    "- technology-implementation: ERP/cloud system selection, build, optimization, run/support\n"
    "- audit-advisory: financial-statement audit, SOC reporting, compliance readiness, strategy\n"
    "- tax: tax compliance, planning, provision\n"
    "- accounting: outsourced accounting, financial reporting\n"
    "- risk-advisory: risk, controls, regulatory\n"
    "Return a RANKED list of the plausible service lines, best first, each with a 0-1 confidence "
    "and a one-sentence reason. Include a line only if it's genuinely plausible. If none fits, "
    "return a single candidate with service_line 'unclear'."
)


def classify_service_line(state: OpportunityState) -> dict:
    ex: ExtractedOpportunity = state["extracted"]
    llm = get_agent_llm().with_structured_output(ServiceLineClassification)
    payload = f"SUMMARY: {ex.summary}\nVERTICAL: {ex.vertical}\nSCOPE SIGNALS:\n- " + "\n- ".join(ex.scope_signals)
    try:
        result: ServiceLineClassification = llm.invoke(
            [("system", _SERVICE_LINE_SYS), ("human", payload)]
        )
    except Exception as exc:
        result = ServiceLineClassification(ranked_candidates=[
            ServiceLineCandidate(service_line=ServiceLine.UNCLEAR, confidence=0.0,
                                 reasoning=f"classify_service_line_failed: {exc}")
        ])
    return {"service_line_classification": result}


# --- Tier 2: classify ENGAGEMENT TYPE (constrained to the chosen service line) ----

def classify_engagement(state: OpportunityState) -> dict:
    ex: ExtractedOpportunity = state["extracted"]
    sl_cls: ServiceLineClassification = state["service_line_classification"]
    primary = sl_cls.primary

    # No confident line, or a stub line we haven't authored engagement types for yet:
    # don't guess — emit an 'unclear' engagement so the route gate sends it to a human, and
    # the skill loader degrades to "" gracefully.
    if primary is None or primary.service_line == ServiceLine.UNCLEAR:
        return {"engagement_classification": EngagementClassification(
            engagement_type="unclear", confidence=0.0,
            reasoning="No confident service line; engagement not classified.")}

    allowed = ENGAGEMENT_TYPES.get(primary.service_line, [])
    if not allowed:
        return {"engagement_classification": EngagementClassification(
            engagement_type="unclear", confidence=0.0,
            reasoning=f"{primary.service_line.value} is a north-star stub — no engagement types authored yet.")}

    sys = (
        f"The opportunity is in the '{primary.service_line.value}' service line. Classify it into "
        f"exactly ONE engagement type from this list: {', '.join(allowed)}. "
        "Give a 0-1 confidence and a one-sentence reason. Use only a value from the list."
    )
    payload = f"SUMMARY: {ex.summary}\nSCOPE SIGNALS:\n- " + "\n- ".join(ex.scope_signals)
    llm = get_agent_llm().with_structured_output(EngagementClassification)
    try:
        result: EngagementClassification = llm.invoke([("system", sys), ("human", payload)])
    except Exception as exc:
        return {"engagement_classification": EngagementClassification(
            engagement_type="unclear", confidence=0.0, reasoning=f"classify_engagement_failed: {exc}")}

    # Guard: if the model returned a type outside the allowed set, don't trust it — gate to human.
    if result.engagement_type not in allowed:
        result = EngagementClassification(
            engagement_type=result.engagement_type, confidence=0.0,
            reasoning=f"Returned '{result.engagement_type}' not in {primary.service_line.value} set — gated.")
    return {"engagement_classification": result}


# --- qualify via the deterministically-loaded skill --------------------------

def qualify_with_skill(state: OpportunityState) -> dict:
    ex: ExtractedOpportunity = state["extracted"]
    sl_cls: ServiceLineClassification = state["service_line_classification"]
    eng: EngagementClassification = state["engagement_classification"]
    primary = sl_cls.primary
    service_line = primary.service_line if primary else ServiceLine.UNCLEAR
    engagement_type = eng.engagement_type

    skill_instructions = load_skill(service_line, engagement_type)
    if not skill_instructions:
        skill_instructions = (
            "(No authored skill rubric for this engagement type yet — qualify conservatively from "
            "general professional-services judgment and flag for human review.)"
        )

    sys = (
        "You are qualifying a professional-services opportunity. Follow the skill instructions "
        "below exactly. Produce the decision summary (lead with the verdict, ten-second read), "
        "the deal shape, and the team_package the skill specifies.\n\n"
        f"=== SKILL: {service_line.value} / {engagement_type} ===\n{skill_instructions}"
    )
    human = (
        f"ORGANIZATION: {ex.organization}\nVERTICAL: {ex.vertical}\n"
        f"SUMMARY: {ex.summary}\nSCOPE:\n- " + "\n- ".join(ex.scope_signals) +
        f"\nVALUE: {ex.estimated_value}\nTIMELINE: {ex.timeline}"
    )
    llm = get_agent_llm().with_structured_output(Qualification)
    try:
        result: Qualification = llm.invoke([("system", sys), ("human", human)])
    except Exception as exc:
        result = Qualification(
            decision_summary="Qualification failed; sending to human review.",
            deal_shape="unknown", open_questions=[f"qualify_failed: {exc}"],
        )
    return {"qualification": result}


# --- score ICP fit -----------------------------------------------------------

_FIT_SYS = (
    "Score this opportunity's fit against the firm's ICP. Firmographics: enterprise or "
    "upper-mid-market, US-headquartered preferred. Target verticals: "
    + ", ".join(icp.TARGET_VERTICALS) + ". Give a 0-100 score, a band "
    "('strong'|'qualified'|'weak'|'pass'), and flag any disqualifiers."
)


def score_fit(state: OpportunityState) -> dict:
    ex: ExtractedOpportunity = state["extracted"]
    qual: Qualification = state["qualification"]
    llm = get_agent_llm().with_structured_output(FitScore)
    human = (
        f"ORG: {ex.organization}\nVERTICAL: {ex.vertical}\n"
        f"DEAL SHAPE: {qual.deal_shape}\nSUMMARY: {ex.summary}"
    )
    try:
        result: FitScore = llm.invoke([("system", _FIT_SYS), ("human", human)])
    except Exception as exc:
        result = FitScore(score=0, band="pass", firmographic_notes="scoring failed",
                          vertical_fit="unknown", flags=[f"fit_failed: {exc}"])
    return {"fit": result}


# --- route (with the confidence/fit gate) ------------------------------------

def route(state: OpportunityState) -> dict:
    sl_cls: ServiceLineClassification = state["service_line_classification"]
    eng_cls: EngagementClassification = state["engagement_classification"]
    fit: FitScore = state["fit"]
    qual: Qualification = state["qualification"]
    decision = routing.decide(sl_cls, eng_cls, fit, qual, state.get("extracted"))
    return {"routing": decision}

# --- review: ranked-offer human-in-the-loop (the cycle) ----------------------

def _team_for(service_line) -> str:
    return routing.TEAM_MAP.get(service_line, "human_review")


def review(state: OpportunityState) -> dict:
    """Offer the opportunity to the current ranked candidate's team and pause for the leader.

    interrupt() persists state and surfaces the offer; the leader resumes with
    Command(resume={"action": "accept|decline|return", "corrected_service_line": <opt>, "note": <opt>}).
    - accept  -> terminal: this team takes it.
    - decline -> terminal: correctly routed, passed -> "Not a fit" lane. NOT an eval label.
    - return  -> misrouted: log the gold label, advance the cursor, loop to offer the next candidate;
                 if the ranked list is exhausted, land in "Not a fit" (no team claimed it).

    review_log uses a reducer (operator.add) in state, so each pass returns ONLY the new
    decision in a one-element list; LangGraph appends it. Paths that record nothing return [].
    """
    sl_cls: ServiceLineClassification = state["service_line_classification"]
    candidates = sl_cls.ranked_candidates
    i = state.get("offer_index", 0)

    # Cursor past the end (or nothing to offer) -> no team claimed it.
    if not candidates or i >= len(candidates):
        return {"offer_index": i, "review_log": [],
                "routing": RoutingDecision(
                    target_team="not_a_fit", auto_routed=False,
                    reason="No remaining ranked service line claimed this opportunity.")}

    offered = candidates[i]
    team = _team_for(offered.service_line)
    ex = state.get("extracted")

    # PAUSE. Everything above this line is a pure read of state, so it's safe to replay on resume.
    raw = interrupt({
        "opportunity": getattr(ex, "organization", "?"),
        "offered_to": offered.service_line.value,
        "team": team,
        "offer_index": i,
        "remaining_after_this": len(candidates) - i - 1,
        "instructions": "Respond with action: accept | decline | return "
                        "(+ optional corrected_service_line, note).",
    })

    action = ReviewAction(raw.get("action", "decline"))
    decision = ReviewDecision(
        action=action,
        offered_service_line=offered.service_line,
        corrected_service_line=(ServiceLine(raw["corrected_service_line"])
                                if raw.get("corrected_service_line") else None),
        note=raw.get("note", ""),
    )

    if action == ReviewAction.ACCEPT:
        return {"review_log": [decision], "offer_index": i,
                "routing": RoutingDecision(target_team=team, auto_routed=False,
                                           reason=f"Accepted by {team} (offer #{i+1}).")}

    if action == ReviewAction.DECLINE:
        return {"review_log": [decision], "offer_index": i,
                "routing": RoutingDecision(target_team="not_a_fit", auto_routed=False,
                                           reason=f"Declined by {team} — correctly routed, passed.")}

    # RETURN: misroute -> advance the cursor; exhaustion -> not_a_fit.
    next_i = i + 1
    if next_i >= len(candidates):
        return {"review_log": [decision], "offer_index": next_i,
                "routing": RoutingDecision(target_team="not_a_fit", auto_routed=False,
                                           reason="Returned by every ranked service line — no team claimed it.")}
    return {"review_log": [decision], "offer_index": next_i,
            "routing": RoutingDecision(
                target_team=_team_for(candidates[next_i].service_line), auto_routed=False,
                reason=f"Returned by {team}; re-offering to {candidates[next_i].service_line.value}.")}

    # PAUSE. Everything above this line is a pure read of state, so it's safe to replay on resume.
    # On resume, `raw` is the dict the leader supplied via Command(resume=...).
    raw = interrupt({
        "opportunity": getattr(ex, "organization", "?"),
        "offered_to": offered.service_line.value,
        "team": team,
        "offer_index": i,
        "remaining_after_this": len(candidates) - i - 1,
        "instructions": "Respond with action: accept | decline | return "
                        "(+ optional corrected_service_line, note).",
    })

    action = ReviewAction(raw.get("action", "decline"))
    decision = ReviewDecision(
        action=action,
        offered_service_line=offered.service_line,
        corrected_service_line=(ServiceLine(raw["corrected_service_line"])
                                if raw.get("corrected_service_line") else None),
        note=raw.get("note", ""),
    )
    new_log = log + [decision]

    if action == ReviewAction.ACCEPT:
        return {"review_log": new_log, "offer_index": i,
                "routing": RoutingDecision(target_team=team, auto_routed=False,
                                           reason=f"Accepted by {team} (offer #{i+1}).")}

    if action == ReviewAction.DECLINE:
        return {"review_log": new_log, "offer_index": i,
                "routing": RoutingDecision(target_team="not_a_fit", auto_routed=False,
                                           reason=f"Declined by {team} — correctly routed, passed.")}

    # RETURN: misroute -> advance the cursor; exhaustion -> not_a_fit.
    next_i = i + 1
    if next_i >= len(candidates):
        return {"review_log": new_log, "offer_index": next_i,
                "routing": RoutingDecision(target_team="not_a_fit", auto_routed=False,
                                           reason="Returned by every ranked service line — no team claimed it.")}
    return {"review_log": new_log, "offer_index": next_i,
            "routing": RoutingDecision(
                target_team=_team_for(candidates[next_i].service_line), auto_routed=False,
                reason=f"Returned by {team}; re-offering to {candidates[next_i].service_line.value}.")}


def route_after_review(state: OpportunityState) -> str:
    """Loop or finish. Only an un-exhausted RETURN loops back to offer the next candidate."""
    log = state.get("review_log", [])
    if not log:
        return "done"
    last = log[-1]
    if last.action != ReviewAction.RETURN:
        return "done"                       # accept or decline -> terminal
    candidates = state["service_line_classification"].ranked_candidates
    return "review" if state.get("offer_index", 0) < len(candidates) else "done"


# --- terminal: couldn't parse the document -----------------------------------

def insufficient_info(state: OpportunityState) -> dict:
    return {"routing": RoutingDecision(
        target_team="human_review", auto_routed=False,
        reason="Document could not be parsed into a usable opportunity.")}