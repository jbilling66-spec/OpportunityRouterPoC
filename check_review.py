"""Check which opportunities are paused at a resumable interrupt vs gate-routed."""
import json, urllib.request

r = json.load(urllib.request.urlopen("http://127.0.0.1:8000/opportunities"))
for o in r["opportunities"]:
    has_offer = o.get("current_offer") is not None
    print(f"{o['organization'] or 'UNPARSED':32s} status={o['status']:13s} "
          f"offer={'YES' if has_offer else 'no '} "
          f"team={o.get('target_team') or '—'}")