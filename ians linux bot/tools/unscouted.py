#!/usr/bin/env python3.12
"""List real ladder matches that have no note yet, newest first, as JSON args for
tools/workflows/ladder_scout.js; with --claim, also claim them so no other run scouts them.

Usage:
    python3.12 tools/unscouted.py [--since ISO-TIME] [--limit N] [--claim]

A match (5 games vs one team in one match group) is done when results/real-matches/<folder>/notes.md
exists, where <folder> = <YYYY-MM-DD>_<HHMM UTC>_<opponent-slug>_<group8> (the same name
tools/organize_notes.py uses). Notes still in the pre-1-Nov place results/ladder/scouting/ also count.
--claim writes <folder>/.claim (gitignored); a claim younger than 3 hours hides the match from later runs,
so a crashed run's matches come back by themselves. Only matches whose 5 games are all logged are listed.
"""
import argparse
import json
import os
import sys
import time

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from organize_notes import LOG, REAL, OLD_SCOUT, real_folder  # noqa: E402

CLAIM_TTL = 3 * 3600


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--since", default="2026-10-31T23:45", help="only matches that started after this (UTC)")
    ap.add_argument("--limit", type=int, default=6)
    ap.add_argument("--claim", action="store_true", help="claim the listed matches for this run")
    args = ap.parse_args()
    done, claimed = set(), set()
    if os.path.isdir(REAL):
        for d in os.listdir(REAL):
            if os.path.isfile(os.path.join(REAL, d, "notes.md")):
                done.add(d.rsplit("_", 1)[-1])
            c = os.path.join(REAL, d, ".claim")
            if os.path.exists(c) and time.time() - os.path.getmtime(c) < CLAIM_TTL:
                claimed.add(d.rsplit("_", 1)[-1])
    if os.path.isdir(OLD_SCOUT):
        done |= {f.split("-")[3] for f in os.listdir(OLD_SCOUT) if f.endswith(".md") and f.count("-") >= 3}
    sets = {}
    for line in open(LOG):
        if line.strip():
            r = json.loads(line)
            if (r["time"] or "") >= args.since:
                sets.setdefault(r["group"], []).append(r)
    out = []
    for group, rows in sorted(sets.items(), key=lambda kv: max(r["time"] for r in kv[1]), reverse=True):
        if group[:8] in done or group[:8] in claimed or len(rows) < 5:
            continue
        wins = sum(r["res"] == "win" for r in rows)
        out.append({"group": group, "time": min(r["time"] for r in rows)[:16].replace("T", " "),
                    "v": rows[0]["v"], "opp": rows[0]["opp"], "rec": f"{wins}-{len(rows) - wins}",
                    "folder": real_folder(rows)})
    out = out[:args.limit]
    if args.claim:
        for s in out:
            os.makedirs(os.path.join(REAL, s["folder"]), exist_ok=True)
            with open(os.path.join(REAL, s["folder"], ".claim"), "w") as f:
                f.write(time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()) + "\n")
    print(json.dumps(out))


if __name__ == "__main__":
    main()
