"""Seed eval dataset. In production this GROWS from partner send-backs (mis-routed = gold label).
These few examples are a starting harness; replace/extend with real labeled opportunities."""
from __future__ import annotations
from langsmith import Client

DATASET_NAME = "opportunity-routing-v1"

# [FILL IN] Replace with real (document -> correct service_line / engagement_type / team) examples,
# and append every partner 'return' (mis-route) here as a regression test. engagement_type values
# must match ENGAGEMENT_TYPES[service_line] in src/schemas.py. Two service lines are built deep;
# the shipbuilding example exercises the relevance gate (a clear non-fit must be discarded).
TECH = "delivery / proposal team"            # routing.TEAM_MAP[technology-implementation]
AUDIT = "assurance / audit engagement team"  # routing.TEAM_MAP[audit-advisory]

EXAMPLES = [
    # --- technology-implementation: all four engagement types ---
    {"inputs": {"document_text": "RFP: stand up a new cloud ERP for a US energy company; "
                "select platform, design, build, go live in 12 months."},
     "outputs": {"service_line": "technology-implementation", "engagement_type": "implementation",
                 "target_team": TECH}},
    {"inputs": {"document_text": "RFI: ongoing application support and monitoring for our "
                "already-live financial system; 3-year managed services engagement with SLAs."},
     "outputs": {"service_line": "technology-implementation", "engagement_type": "managed-services",
                 "target_team": TECH}},
    {"inputs": {"document_text": "Our live ERP underperforms; we want an assessment and "
                "remediation to optimize the financial close and reporting on the existing system."},
     "outputs": {"service_line": "technology-implementation", "engagement_type": "optimization",
                 "target_team": TECH}},
    {"inputs": {"document_text": "We're early — need a roadmap and readiness assessment before "
                "selecting any system for our higher-ed institution."},
     "outputs": {"service_line": "technology-implementation", "engagement_type": "pre-implementation",
                 "target_team": TECH}},
    # --- audit-advisory ---
    {"inputs": {"document_text": "RFP: independent audit of our consolidated financial statements "
                "for FY2025 under US GAAP for a publicly traded health care company."},
     "outputs": {"service_line": "audit-advisory", "engagement_type": "financial-statement-audit",
                 "target_team": AUDIT}},
    {"inputs": {"document_text": "We need a SOC 2 Type II report for our SaaS platform to share "
                "with enterprise customers; assess controls over a 6-month observation period."},
     "outputs": {"service_line": "audit-advisory", "engagement_type": "soc-reporting",
                 "target_team": AUDIT}},
    {"inputs": {"document_text": "Help us prepare for an upcoming regulatory compliance examination "
                "and assess the readiness of our internal controls against the framework."},
     "outputs": {"service_line": "audit-advisory", "engagement_type": "compliance-readiness",
                 "target_team": AUDIT}},
    # --- relevance gate: a clear non-fit must be discarded, not force-routed ---
    {"inputs": {"document_text": "RFP: design and construct two offshore patrol vessels including "
                "hull fabrication, propulsion, and sea trials over 36 months."},
     "outputs": {"target_team": "not_a_fit"}},  # relevance gate should discard (shipbuilding)
]

def main():
    c = Client()
    try:
        ds = c.read_dataset(dataset_name=DATASET_NAME)
        print(f"exists: {ds.id}")
    except Exception:
        ds = c.create_dataset(dataset_name=DATASET_NAME, description="Opportunity routing eval set.")
        c.create_examples(inputs=[e["inputs"] for e in EXAMPLES],
                           outputs=[e["outputs"] for e in EXAMPLES], dataset_id=ds.id)
        print(f"created {DATASET_NAME} with {len(EXAMPLES)} examples")

if __name__ == "__main__":
    main()
