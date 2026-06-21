"""Seed eval dataset. In production this GROWS from partner send-backs (mis-routed = gold label).
These few examples are a starting harness; replace/extend with real labeled opportunities."""
from __future__ import annotations
from langsmith import Client

DATASET_NAME = "opportunity-routing-v1"

# [FILL IN] Replace with real (document -> correct work_type / team) examples,
# and append every partner 'return' (mis-route) here as a regression test.
EXAMPLES = [
    {"inputs": {"document_text": "RFP: stand up a new cloud ERP for a US energy company; "
                "select platform, design, build, go live in 12 months."},
     "outputs": {"work_type": "implementation", "target_team": "delivery / proposal team"}},
    {"inputs": {"document_text": "RFI: ongoing application support and monitoring for our "
                "already-live financial system; 3-year managed services with SLAs."},
     "outputs": {"work_type": "managed_services", "target_team": "managed-services + pricing"}},
    {"inputs": {"document_text": "Our live ERP underperforms; we want an assessment and "
                "remediation to optimize close and reporting."},
     "outputs": {"work_type": "optimization", "target_team": "optimization practice"}},
    {"inputs": {"document_text": "We're early — need a roadmap and readiness assessment before "
                "selecting any system for our higher-ed institution."},
     "outputs": {"work_type": "pre_implementation", "target_team": "advisory / strategy"}},
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
