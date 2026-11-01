#!/usr/bin/env python3
"""First round where two games' champion timelines differ, and which champion/metric.

Local games are deterministic, so for a candidate and a byte-identical flag-off control (same module
size, same fuel until the patched branch runs) the first difference marks where the patch fired.
A divergence at round 1-5 instead means turn-1 fuel chaos from a different module size.
Usage: python3 -I tools/firstdiff.py control.json candidate.json"""
import json, sys
def load(f):
    d = json.load(open(f)); n = d["championTimelines"][0]["sampleCount"]; out = {}
    for t in d["championTimelines"]:
        v = []
        for r in t["runs"]: v.extend([r["value"]] * r["duration"])
        out[(t["owner"]["team"], t["owner"]["name"], t["metric"])] = v
    return out, n
a, na = load(sys.argv[1]); b, nb = load(sys.argv[2])
best = None
for k in a:
    if k not in b: continue
    x, y = a[k], b[k]
    for r in range(min(len(x), len(y))):
        if x[r] != y[r]:
            if best is None or r < best[0]: best = (r, k, x[r], y[r])
            break
print(sys.argv[1].split("/")[-1], "first diff", best)
