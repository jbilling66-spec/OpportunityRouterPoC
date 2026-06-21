"""StateGraph assembly — single-agent spine + relevance gate + two-tier routing + review loop.

START -> extract
           |-(junk)------> insufficient_info -> END
           |-(ok)--------> check_relevance
                              |-(out_of_scope)-> discard -> END        ("Not a fit" lane, with reason)
                              |-(in/uncertain)-> classify_service_line   (Tier 1, ranked)
                                                 -> classify_engagement  (Tier 2, per service line)
                                                 -> qualify_with_skill -> score_fit -> route
                                                 -> review  <-------------------+   (interrupt: leader acts)
                                                      |-(return, not exhausted)-+   (the cycle)
                                                      |-(accept/decline/exhausted)-> END

The review node offers the opportunity to the top-ranked service line and pauses via interrupt().
A RETURN advances the cursor and loops back to re-offer the next candidate; accept, decline, or an
exhausted list ends the run. This back-edge is what makes the graph a true stateful cycle, not a DAG.

Compiled with an in-memory checkpointer so interrupt() can persist state across the human pause
within a server session. The checkpointer is swappable: SqliteSaver or PostgresSaver would persist
paused workflows across restarts in production — a one-line change here.
"""
from __future__ import annotations
from langgraph.graph import StateGraph, START, END
from langgraph.checkpoint.memory import InMemorySaver
from .state import OpportunityState
from .nodes import (extract, route_after_extract, check_relevance, route_after_relevance,
                    discard, classify_service_line, classify_engagement,
                    qualify_with_skill, score_fit, route, review, route_after_review,
                    insufficient_info)

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
    g.add_node("review", review)
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
    g.add_edge("route", "review")
    g.add_conditional_edges("review", route_after_review,
                            {"review": "review", "done": END})
    g.add_edge("discard", END)
    g.add_edge("insufficient_info", END)
    return g.compile(checkpointer=InMemorySaver())

agent = build_graph()