"""Seed the running API with every sample document in data/.

Targets local by default; override for a deployed instance:
    python seed.py                                  # seeds http://127.0.0.1:8000
    python seed.py https://your-app.onrender.com    # seeds a deployed URL
    API_URL=https://your-app.onrender.com python seed.py   # same, via env var
"""
import glob, json, os, sys, urllib.request

# Endpoint is configurable: CLI arg > env var > local default. No hardcoded production URL.
BASE = (sys.argv[1] if len(sys.argv) > 1 else os.environ.get("API_URL", "http://127.0.0.1:8000")).rstrip("/")
API = f"{BASE}/qualify"

print(f"Seeding {API} ...\n")
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