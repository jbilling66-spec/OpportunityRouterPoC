"""CLI: qualify one document. `python run.py data/sample_rfp.txt`  (or a .pdf)"""
from __future__ import annotations
from dotenv import load_dotenv
load_dotenv()
import sys
import uuid
from src.graph import agent
from src.ingestion.pdf_loader import pdf_to_text

def main(path: str) -> None:
    text = pdf_to_text(path) if path.lower().endswith(".pdf") else open(path, encoding="utf-8").read()
    config = {"configurable": {"thread_id": str(uuid.uuid4())}}
    r = agent.invoke({"document_text": text, "source": "cli", "errors": []}, config)
    ex = r.get("extracted")
    sl_cls = r.get("service_line_classification")
    eng_cls = r.get("engagement_classification")
    qual, fit, routing = r.get("qualification"), r.get("fit"), r.get("routing")

    print("=" * 70)
    print(f"{getattr(ex,'organization','?')}  ·  {getattr(ex,'vertical','?')}")
    primary = sl_cls.primary if sl_cls else None
    if primary and eng_cls:
        print(f"CLASSIFIED: {primary.service_line.value} / {eng_cls.engagement_type} "
              f"(line {primary.confidence:.2f}, engagement {eng_cls.confidence:.2f})")
    else:
        print("CLASSIFIED: ?")
    print(f"FIT: {fit.score}/100 ({fit.band})" if fit else "FIT: ?")
    print("-" * 70)
    print(qual.decision_summary if qual else "")
    print(f"\nDEAL SHAPE: {qual.deal_shape}" if qual else "")
    print(f"\nROUTING → {routing.target_team}  (auto={routing.auto_routed})" if routing else "")
    print(f"  {routing.reason}" if routing else "")
    print("=" * 70)

if __name__ == "__main__":
    if len(sys.argv) != 2:
        print("usage: python run.py <document.txt|.pdf>"); raise SystemExit(1)
    main(sys.argv[1])
