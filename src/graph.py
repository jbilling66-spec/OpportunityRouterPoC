"""StateGraph assembly — the single-agent spine with a relevance gate + two-tier deterministic routing.

START -> extract
           |-(junk)------> insufficient_info -> END
           |-(ok)--------> check_relevance
                              |-(out_of_scope)-> discard -> END        ("Not a fit" lane, with reason)
                              |-(in/uncertain)-> classify_service_line   (Tier 1, ranked)
                                                 -> classify_engagement  (Tier 2, per service line)
                                                 -> qualify_with_skill -> score_fit -> route -> END

The relevance gate catches clear non-fits BEFORE they're force-fit into a service line. Tier 1
picks the service line (ranked); Tier 2 picks the engagement type within it; the matching skill
then loads deterministically. Low confidence at either tier -> human review, not a guess.
"""
from __future__ import annotations
from langgraph.graph import StateGraph, START, END
from .state import OpportunityState
from .nodes import (extract, route_after_extract, check_relevance, route_after_relevance,
                    discard, classify_service_line, classify_engagement,
                    qualify_with_skill, score_fit, route, insufficient_info)

def build_graph():
    g = StateGraph(OpportunityState)
    g.add_node("extract", extract)
    g.add_node("check_relevance", check_relevance)
    g.add_node("discard", discard)
    g.add_node("classify_service_line", classify_service_line)
    g.add_node("classify_engagement", classify_engagement)
    g.add_node("qualify_with_skill", qualify_with_skill)
    g.add_node("score_fit", score_fit)
    g.add_node("route", route)
    g.add_node("insufficient_info", insufficient_info)

    g.add_edge(START, "extract")
    g.add_conditional_edges("extract", route_after_extract,
                            {"check_relevance": "check_relevance", "insufficient_info": "insufficient_info"})
    g.add_conditional_edges("check_relevance", route_after_relevance,
                            {"classify_service_line": "classify_service_line", "discard": "discard"})
    g.add_edge("classify_service_line", "classify_engagement")
    g.add_edge("classify_engagement", "qualify_with_skill")
    g.add_edge("qualify_with_skill", "score_fit")
    g.add_edge("score_fit", "route")
    g.add_edge("route", END)
    g.add_edge("discard", END)
    g.add_edge("insufficient_info", END)
    return g.compile()

agent = build_graph()