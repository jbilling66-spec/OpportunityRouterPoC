"""Pipeline nodes + routers.

Two-tier flow:
  extract -> check_relevance -> classify_service_line (Tier 1, ranked)
          -> classify_engagement (Tier 2, per service line) -> qualify_with_skill
          -> score_fit -> route

The two classifier outputs are the routing key; the matching skill loads deterministically
inside qualify_with_skill via load_skill(service_line, engagement_type).
"""

from __future__ import annotations

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


# --- terminal: couldn't parse the document -----------------------------------

def insufficient_info(state: OpportunityState) -> dict:
    return {"routing": RoutingDecision(
        target_team="human_review", auto_routed=False,
        reason="Document could not be parsed into a usable opportunity.")}