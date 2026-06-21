"""Compare the two paths for a doc that fails via API: direct engine vs HTTP."""
from dotenv import load_dotenv
load_dotenv()
import uuid, json, urllib.request
from src.graph import agent

for name in ["sample_tax.txt", "sample_audit.txt"]:
    path = f"data/{name}"
    text = open(path, encoding="utf-8").read()
    print("=" * 60)
    print(f"{name}  ({len(text)} chars)")
    print("first 80 repr:", repr(text[:80]))

    # Path 1: direct through the engine
    r1 = agent.invoke(
        {"document_text": text, "source": "debug", "errors": []},
        {"configurable": {"thread_id": str(uuid.uuid4())}},
    )
    print("DIRECT ENGINE ->", r1.get("extraction_status"),
          "| org:", getattr(r1.get("extracted"), "organization", None))

    # Path 2: through the API, exactly like seed.py
    body = json.dumps({"document_text": text, "source": "seed"}).encode("utf-8")
    req = urllib.request.Request(
        "http://127.0.0.1:8000/qualify", data=body,
        headers={"Content-Type": "application/json"}, method="POST",
    )
    r2 = json.load(urllib.request.urlopen(req))
    print("VIA API       ->", r2.get("status"),
          "| org:", r2.get("organization"),
          "| reason:", r2.get("routing_reason"))