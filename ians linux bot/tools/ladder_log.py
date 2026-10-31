#!/usr/bin/env python3
"""Append real ladder games to results/ladder-games.jsonl and summarise our record.

Usage:
    python3 tools/ladder_log.py [match-group JSON files ...] [--version N]

Each input file is a JSON list of /api/v1/match-groups/<id> responses (the dump the loop posts from the
logged-in browser to matches/ladder/raw/). Games are de-duplicated by match id. The summary prints the
record per bot version, by team size (number of drafted champions), and the live version's losses with
opponent drafts, which is where new strategy hypotheses come from.
"""
import argparse
import collections
import json
import os

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
LOG = os.path.join(ROOT, "results", "ladder-games.jsonl")
ME = "1b0ef7ff-3dd5-472f-877c-c07d01f9cc99"  # Turbo Recallers team id
CHAMPS = ["Ryth", "Vesper", "Vendetta", "Cassi&Issac", "Stellar", "Prism", "Marcella", "Willow", "Ren", "Varg",
          "Tavi", "HoR"]


def rows_from(groups):
    for d in groups:
        g = d["group"]
        me = next(s for s in g["sides"] if s["teamId"] == ME)
        op = next(s for s in g["sides"] if s["teamId"] != ME)
        for m in d.get("matches", []):
            ms = next(s for s in m["sides"] if s["teamId"] == ME)
            os_ = next(s for s in m["sides"] if s["teamId"] != ME)
            draft = lambda s: [CHAMPS[int(x)] for x in (s.get("draft") or [])]
            yield {"id": m["id"], "group": g["id"], "time": m.get("finishedAt"), "v": me["version"],
                   "opp": op["teamName"], "opp_rating": round(op.get("ratingBefore") or 0),
                   "our_rating_after": round(me.get("ratingAfter") or 0), "map": m["map"], "side": ms["side"],
                   "res": ms["result"], "us": ms["score"], "them": os_["score"], "rounds": m["rounds"],
                   "end": m["endReason"], "udraft": draft(ms), "odraft": draft(os_)}


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("files", nargs="*")
    ap.add_argument("--version", type=int, default=None, help="version to detail (default: newest)")
    args = ap.parse_args()
    seen = set()
    if os.path.exists(LOG):
        seen = {json.loads(l)["id"] for l in open(LOG) if l.strip()}
    added = 0
    with open(LOG, "a") as f:
        for path in args.files:
            for r in rows_from(json.load(open(path))):
                if r["id"] in seen or r["res"] not in ("win", "loss"):
                    continue
                seen.add(r["id"])
                f.write(json.dumps(r) + "\n")
                added += 1
    rows = [json.loads(l) for l in open(LOG) if l.strip()]
    print(f"appended {added}; {len(rows)} games logged")
    by_v = collections.defaultdict(list)
    for r in rows:
        by_v[r["v"]].append(r)
    for v, rs in sorted(by_v.items(), key=lambda kv: kv[0] or 0):
        w = sum(r["res"] == "win" for r in rs)
        size = collections.defaultdict(lambda: [0, 0])
        for r in rs:
            size[len(r["udraft"])][0] += r["res"] == "win"
            size[len(r["udraft"])][1] += 1
        latest = max(rs, key=lambda r: r["time"] or "")
        print(f"v{v}: {w}W-{len(rs) - w}L  by team size " +
              " ".join(f"{k}-pick {a}/{n}" for k, (a, n) in sorted(size.items())) +
              f"  rating after latest set {latest['our_rating_after']}")
    v = args.version or max(by_v)
    print(f"v{v} losses:")
    for r in sorted(by_v[v], key=lambda r: r["time"] or ""):
        if r["res"] == "loss":
            print(f"  {r['opp'][:20]:20s} ({r['opp_rating']}) {r['map']:22s} {r['us']:5}-{r['them']:<5} r{r['rounds']:<5} "
                  f"{r['end']:14s} them: {','.join(r['odraft'])}")


if __name__ == "__main__":
    main()
