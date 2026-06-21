import json, urllib.request, sys
path = sys.argv[1] if len(sys.argv) > 1 else "data/sample_ambiguous.txt"
text = open(path, encoding="utf-8").read()
body = json.dumps({"document_text": text, "source": "seed"}).encode("utf-8")
req = urllib.request.Request("http://127.0.0.1:8000/qualify", data=body,
                             headers={"Content-Type": "application/json"}, method="POST")
r = json.load(urllib.request.urlopen(req))
print("ORG:", r.get("organization"))
print("CANDIDATES:")
for c in r.get("ranked_candidates", []):
    print(f"  {c['confidence']:.2f}  {c['service_line']}")
print("STATUS:", r.get("status"))