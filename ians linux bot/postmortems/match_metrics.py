#!/usr/bin/env python3
# Per-game metrics from tools/eval.py statistics JSON (our own match output, not downloaded data).
import json, sys, glob, os, collections
# usage: python3 postmortems/match_metrics.py matches/<tag>   (reads every <map>__<side>.json written by tools/eval.py)
# Reports, for the bot that was BOT_A in eval.py: gems lost by killer kind, mean tribute size,
# deaths by killer kind, fuel exhaustions, wards, consumables bought, bot faults.
tot = collections.Counter(); tribs = []
for p in sorted(glob.glob(os.path.join(sys.argv[1], "*__[AB].json"))):
    d = json.load(open(p)); me = "teamA" if p.endswith("__A.json") else "teamB"
    for e in d["events"]:
        if e.get("owner", {}).get("team") != me: continue
        k = e["kind"]
        for x in e["entries"]:
            v = float(x.get("value") or 0); t = x.get("target"); tk = t.get("kind", "?") if isinstance(t, dict) else x.get("context", "?")
            if k == "gemLoss": tot["gemsLost_to_" + tk] += v
            elif k == "death": tot["deaths_by_" + tk] += 1
            elif k == "gemSubmission": tribs.append(v)
            elif k in ("fuelExhausted", "wardPlacement", "botFault"): tot[k] += 1
            elif k == "buyConsumable": tot["consumablesBought"] += 1
n = max(1, len(glob.glob(os.path.join(sys.argv[1], "*__[AB].json"))))
print(f"games {n}  tributes {len(tribs)}  mean tribute {sum(tribs)/max(1,len(tribs)):.1f}  "
      f"small(<10) {sum(1 for t in tribs if t < 10)}")
for k, v in sorted(tot.items()): print(f"  {k:32s} {v:8.0f}  ({v/n:.1f}/game)")
