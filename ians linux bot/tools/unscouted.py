#!/usr/bin/env python3
"""List real ladder match sets that have no scouting note yet, newest first, as JSON args for
tools/workflows/ladder_scout.js.

Usage:
    python3 tools/unscouted.py [--since ISO-TIME] [--limit N]

A set is scouted when it has a folder results/real-matches/<date>_<HHMM>_<opponent>_<group8>/ with a
notes.md (or, from before the 1 Nov reorganisation, a results/ladder/scouting/<date>-<group8>-*.md note,
which tools/organize_notes.py then moves). Only sets whose 5 games are all finished and logged are listed.
"""
import argparse
import collections
import json
import os

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
LOG = os.path.join(ROOT, "results", "ladder-games.jsonl")
REAL = os.path.join(ROOT, "results", "real-matches")
LEGACY = os.path.join(ROOT, "results", "ladder", "scouting")


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--since", default="2026-10-31T23:45", help="only sets that finished after this (UTC)")
    ap.add_argument("--limit", type=int, default=6)
    args = ap.parse_args()
    done = set()
    if os.path.isdir(REAL):
        done |= {d.rsplit("_", 1)[-1] for d in os.listdir(REAL) if os.path.isfile(os.path.join(REAL, d, "notes.md"))}
    if os.path.isdir(LEGACY):
        done |= {f.split("-")[3] for f in os.listdir(LEGACY) if f.endswith(".md")}
    sets = collections.defaultdict(list)
    for line in open(LOG):
        if line.strip():
            r = json.loads(line)
            if (r["time"] or "") >= args.since:
                sets[r["group"]].append(r)
    out = []
    for group, rows in sorted(sets.items(), key=lambda kv: max(r["time"] for r in kv[1]), reverse=True):
        if group[:8] in done or len(rows) < 5:
            continue
        wins = sum(r["res"] == "win" for r in rows)
        out.append({"group": group, "time": min(r["time"] for r in rows)[11:16], "v": rows[0]["v"],
                    "opp": rows[0]["opp"], "rec": f"{wins}-{len(rows) - wins}"})
    print(json.dumps(out[:args.limit]))


if __name__ == "__main__":
    main()
