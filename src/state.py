"""Pipeline state. Status flags drive routing and stay visible in the trace."""
from __future__ import annotations
import operator
from typing import Annotated, List, Optional, TypedDict
from .schemas import (ExtractedOpportunity, ServiceLineClassification,
                      EngagementClassification, FitScore, Qualification,
                      RoutingDecision, RelevanceCheck, ReviewDecision)

class OpportunityState(TypedDict, total=False):
    # input
    document_text: str
    source: str                       # "upload" | "email" | ...  (source-agnostic ingestion)
    # pipeline outputs
    extracted: Optional[ExtractedOpportunity]
    extraction_status: Optional[str]  # "ok" | "junk"
    relevance: Optional[RelevanceCheck]                                # relevance gate verdict
    service_line_classification: Optional[ServiceLineClassification]   # Tier 1 (ranked candidates)
    engagement_classification: Optional[EngagementClassification]      # Tier 2 (per service line)
    qualification: Optional[Qualification]
    fit: Optional[FitScore]
    routing: Optional[RoutingDecision]
    # review loop
    offer_index: int                                                   # cursor into ranked candidates
    review_log: Annotated[List[ReviewDecision], operator.add]          # accumulates across loop passes (reducer)
    errors: List[str]
