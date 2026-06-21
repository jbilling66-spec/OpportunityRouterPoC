"""Quick API tester: POST the sample RFP to /qualify and pretty-print the result."""
import json, urllib.request

text = open("data/sample_rfp.txt", encoding="utf-8").read()
body = json.dumps({"document_text": text, "source": "api"}).encode("utf-8")

req = urllib.request.Request(
    "http://127.0.0.1:8000/qualify",
    data=body,
    headers={"Content-Type": "application/json"},
    method="POST",
)
with urllib.request.urlopen(req) as resp:
    result = json.load(resp)

print(json.dumps(result, indent=2))
