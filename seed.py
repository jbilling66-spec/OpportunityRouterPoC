"""Seed the running API with every sample document in data/.
Run with the server up:  python seed.py
"""
import glob, json, os, urllib.request

API = "http://127.0.0.1:8000/qualify"

for path in sorted(glob.glob("data/*.txt")):
    text = open(path, encoding="utf-8").read()
    body = json.dumps({"document_text": text, "source": "seed"}).encode("utf-8")
    req = urllib.request.Request(API, data=body,
                                 headers={"Content-Type": "application/json"}, method="POST")
    with urllib.request.urlopen(req) as resp:
        r = json.load(resp)
    org = r.get("organization") or "UNPARSED"
    sl = r.get("service_line") or "—"
    eng = r.get("engagement_type") or "—"
    fit = r.get("fit_score")
    status = r.get("status")
    print(f"{os.path.basename(path):24s} -> {org:32s} {sl}/{eng}  fit={fit}  [{status}]")

print("\nDone. Refresh the dashboard.")