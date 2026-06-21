"""Ideal Customer Profile — the firm's targeting config.

This is the firmographic + vertical layer of the ICP, captured from the vision. The
finer, work-type-specific fit judgment lives in each skill's SKILL.md (those are where
you encode what makes a *strong* implementation deal vs. a managed-services one).

Tune freely — this file is meant to be owned and edited.
"""

# --- Firmographics -----------------------------------------------------------

SEGMENTS = ["enterprise", "upper_mid_market"]
# Mid-market only qualifies when it leans toward enterprise. Pure SMB is a pass.
MID_MARKET_RULE = "Mid-market qualifies only when it trends toward enterprise scale."

GEOGRAPHY = {
    "preferred": "US-headquartered",
    "acceptable": "Globally-operating firms that are home-based in the US / have major US operations",
    "pass": "No meaningful US presence",
}

# --- Target verticals --------------------------------------------------------

TARGET_VERTICALS = [
    "Energy",
    "Construction",
    "Communications & Media",
    "Financial Services",
    "Health Care",
    "Government — Federal",
    "Government — State & Local",
    "Higher Education",
    "Life Sciences",
    "Real Estate",
    "Tribal & Gaming",
]

# --- Fit weighting (TEMPLATE — tune to taste) --------------------------------
# How much each dimension moves the 0-100 fit score. Starting point only.
FIT_WEIGHTS = {
    "firmographic": 35,   # right size + US-based
    "vertical": 25,       # in a target vertical
    "engagement_fit": 30,  # graded by the engagement skill's rubric  [FILL IN per skill]
    "deal_signals": 10,   # value / timeline / urgency
}

# Score at/above which an opportunity is "strong" enough to surface prominently.
STRONG_FIT_THRESHOLD = 70

# Classifier confidence below which we do NOT auto-route — flag for human review.
AUTO_ROUTE_CONFIDENCE_GATE = 0.75


# --- Service lines (grounds the relevance gate: "is this even our kind of work?") -----
# The firm's service lines. The relevance gate judges in/out-of-scope against these.
# This is also Tier-1 of the two-tier classifier.
#
# SCOPE NOTE: Two service lines are built to full depth (engagement-type classification +
# grounded SKILL.md rubrics). The first-tier classifier chooses between these two or returns
# UNCLEAR for anything that isn't confidently one of them — which routes to human review rather
# than guessing. This is a deliberate scope choice: prove the two-tier pattern on two lines well,
# and degrade gracefully on everything else.
SERVICE_LINES = [
    "technology-implementation",   # ERP/cloud system selection, build, optimization, advisory
    "audit-advisory",              # financial-statement audit, SOC, compliance readiness, strategy
]