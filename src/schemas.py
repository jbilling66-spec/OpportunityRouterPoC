"""Structured schemas for the opportunity pipeline.

The pipeline turns a raw uploaded document into a routed, reviewable opportunity:
  extract -> classify work type -> qualify (via the matching skill) -> score ICP fit -> route.

WorkType is the routing key: the classifier's output deterministically selects which
skill loads, and the skill knows which downstream team to compile a package for.
"""

from __future__ import annotations

from enum import Enum
from typing import List, Optional

from pydantic import BaseModel, Field


class WorkType(str, Enum):
    IMPLEMENTATION = "implementation"          # net-new build / system implementation
    MANAGED_SERVICES = "managed_services"      # ongoing operate / support
    OPTIMIZATION = "optimization"              # tune / improve an existing system
    PRE_IMPLEMENTATION = "pre_implementation"  # advisory / readiness / roadmap
    UNCLEAR = "unclear"                        # classifier not confident -> human review

# --- Tier 1: service line (the routing key, generalized) ---------------------

class ServiceLine(str, Enum):
    """The firm's service lines — Tier 1 of the two-tier classifier.

    Values match config.icp.SERVICE_LINES AND the skills/ folder names, so the
    loader maps a ServiceLine straight to a directory — no lookup table needed.
    Two lines are built to full depth; UNCLEAR is the honest escape hatch when a
    deal isn't confidently one of them.
    """
    TECHNOLOGY_IMPLEMENTATION = "technology-implementation"
    AUDIT_ADVISORY = "audit-advisory"
    UNCLEAR = "unclear"                 # not confidently one of the supported lines -> human review


class ServiceLineCandidate(BaseModel):
    service_line: ServiceLine
    confidence: float = Field(description="0-1 confidence this is the right line.")
    reasoning: str = Field(description="One sentence: why this line.")


class ServiceLineClassification(BaseModel):
    """Tier-1 output as a RANKED list, not a single pick.

    The top candidate is the primary route; the remainder is the fallback queue
    the review loop offers in order (offer #1; if declined, #2; exhaust -> discard).
    """
    ranked_candidates: List[ServiceLineCandidate] = Field(
        description="Candidate service lines, best first. At least one entry."
    )

    @property
    def primary(self) -> Optional[ServiceLineCandidate]:
        return self.ranked_candidates[0] if self.ranked_candidates else None

    @property
    def fallback_queue(self) -> List[ServiceLineCandidate]:
        return self.ranked_candidates[1:]


# --- Tier 2: engagement type (service-line-specific, NOT a universal list) ----

# Adding a service line = adding a key here + a skills/<line>/ folder. Two lines
# are built deep; the rest stay north-star stubs until you author them.
ENGAGEMENT_TYPES: dict[ServiceLine, List[str]] = {
    ServiceLine.TECHNOLOGY_IMPLEMENTATION: [
        "implementation", "managed-services", "optimization", "pre-implementation",
    ],
    ServiceLine.AUDIT_ADVISORY: [
        "financial-statement-audit", "soc-reporting",
        "compliance-readiness", "strategy-advisory",
    ],
}


class EngagementClassification(BaseModel):
    """Tier-2 output. engagement_type is validated against the chosen line's set
    (ENGAGEMENT_TYPES[service_line]) inside the classifier node, so it always
    resolves to a real skills/<line>/<engagement>/ folder.
    """
    engagement_type: str = Field(description="A value from ENGAGEMENT_TYPES[service_line].")
    confidence: float = Field(description="0-1. Below the gate -> human review.")
    reasoning: str

class ExtractedOpportunity(BaseModel):
    """Facts pulled from the uploaded document, before qualification."""

    organization: Optional[str] = Field(None, description="The buying organization.")
    vertical: Optional[str] = Field(
        None, description="Best-guess industry vertical (see config/icp.py TARGET_VERTICALS)."
    )
    summary: str = Field(
        description="One paragraph a salesperson can read to make the call in ten seconds."
    )
    scope_signals: List[str] = Field(
        default_factory=list, description="Concrete scope statements that define the work."
    )
    estimated_value: Optional[str] = Field(None)
    timeline: Optional[str] = Field(None)
    response_deadline: Optional[str] = Field(None)

    def is_usable(self) -> bool:
        return bool(self.scope_signals) or bool(self.summary.strip())


class WorkTypeClassification(BaseModel):
    work_type: WorkType
    confidence: float = Field(description="0-1. Below the gate threshold -> human review, not auto-route.")
    reasoning: str


class FitScore(BaseModel):
    """ICP fit, scored against config/icp.py + the work-type skill's criteria."""

    score: int = Field(description="0-100 fit score.")
    band: str = Field(description="'strong' | 'qualified' | 'weak' | 'pass'.")
    firmographic_notes: str = Field(description="Size / geography fit vs. the ICP.")
    vertical_fit: str
    flags: List[str] = Field(default_factory=list, description="Disqualifiers or cautions.")


class Qualification(BaseModel):
    """The skill's output: the read on the deal + the package for the downstream team."""

    decision_summary: str = Field(description="The top-of-readout paragraph. Lead with the verdict.")
    deal_shape: str = Field(description="Engagement model, likely size, term, commercial structure.")
    team_package: dict = Field(
        default_factory=dict,
        description="Structured inputs the routed-to team needs (skill-specific).",
    )
    open_questions: List[str] = Field(default_factory=list)


class RoutingDecision(BaseModel):
    target_team: str
    auto_routed: bool = Field(description="False when confidence/fit gates it to human review first.")
    reason: str


class ReviewStatus(str, Enum):
    NEW = "new"
    UNDER_REVIEW = "under_review"
    ACCEPTED = "accepted"
    IGNORED = "ignored"                          # noisy signal: could be mis-route OR not interested
    RETURNED_FOR_REANALYSIS = "returned"         # GOLD eval label: routing was wrong


class ReviewAction(str, Enum):
    """What a service-line leader does with an offered opportunity.

    ACCEPT and DECLINE are terminal; only RETURN advances the cursor and drives the loop.
    """
    ACCEPT = "accept"     # correctly routed AND wanted -> this team takes it (terminal)
    DECLINE = "decline"   # correctly routed but passing -> "Not a fit" lane (terminal, NOT a label)
    RETURN = "return"     # MISROUTED, not my line -> advance to next ranked candidate (gold eval label)


class ReviewDecision(BaseModel):
    """One human action on an offered opportunity.

    DECLINE is a clean business 'no' on a correct route — it ends the opportunity and is not a
    training signal. RETURN means the classifier was wrong; it advances the offer to the next
    ranked service line and is captured as a gold-labeled correction for the LangSmith dataset.
    On a RETURN the leader may also name where it actually belongs (corrected_service_line),
    which makes a richer label: both the wrong answer and the right one.
    """
    action: ReviewAction
    offered_service_line: ServiceLine = Field(description="Which ranked candidate this was offered to.")
    corrected_service_line: Optional[ServiceLine] = Field(
        default=None,
        description="On RETURN only: where the leader says it actually belongs. Optional but valuable.")
    note: str = Field(default="", description="Optional reviewer note / reason.")


class Relevance(str, Enum):
    IN_SCOPE = "in_scope"          # plausibly deliverable by one of the firm's service lines
    OUT_OF_SCOPE = "out_of_scope"  # clear non-fit (e.g. shipbuilding for an accounting firm)
    UNCERTAIN = "uncertain"        # borderline — do NOT discard; let it flow to human review


class RelevanceCheck(BaseModel):
    """The relevance gate's verdict. Calibrated to discard only CLEAR non-fits."""
    verdict: Relevance
    reason: str = Field(description="Why it's in/out of scope, in one sentence.")