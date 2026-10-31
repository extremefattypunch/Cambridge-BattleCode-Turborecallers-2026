#!/usr/bin/env python3
"""Gauntlet: evaluate one candidate bot against a pool of reference bots and log the result.

Usage:
    python3 tools/gauntlet.py CANDIDATE [--pool a,b,c] [--maps quick|sprint|all|a,b] [--jobs N] [--note TEXT]

Default pool: the current champion (see results/CHAMPION) plus the other reference bots in
DEFAULT_POOL. Each pairing runs tools/eval.py (both sides per map). Prints a table and appends one
JSON line per run to results/gauntlet.jsonl (git-tracked, so improvement history survives handoffs):
    {"time", "commit", "candidate", "maps", "note", "results": {opp: {"wins","losses","gems_for","gems_against"}},
     "total_wins", "total_games"}
Promotion rule used so far: a candidate replaces the champion when it beats the champion >= 55% on
--maps sprint (40 games) AND does not lose ground vs the rest of the pool.
"""
import argparse
import datetime
import json
import os
import re
import subprocess
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
EVAL = os.path.join(ROOT, "tools", "eval.py")
RESULTS = os.path.join(ROOT, "results")
DEFAULT_POOL = ["sf_base", "tb_deathball", "tb_aggro", "tb_economy", "starter-python"]
SUMMARY = re.compile(r"SUMMARY (\S+) vs (\S+): (\d+)W-(\d+)L .*avg gems (\d+) vs (\d+)")


def champion():
    path = os.path.join(RESULTS, "CHAMPION")
    if os.path.exists(path):
        return open(path).read().strip() or None
    return None


def git_commit():
    try:
        return subprocess.run(["git", "rev-parse", "--short", "HEAD"], cwd=ROOT, capture_output=True,
                              text=True).stdout.strip()
    except OSError:
        return ""


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("candidate")
    ap.add_argument("--pool", default=None)
    ap.add_argument("--maps", default="sprint")
    ap.add_argument("--jobs", type=int, default=8)
    ap.add_argument("--note", default="")
    args = ap.parse_args()

    if args.pool:
        pool = [p.strip() for p in args.pool.split(",") if p.strip()]
    else:
        pool = list(DEFAULT_POOL)
        champ = champion()
        if champ and champ not in pool:
            pool.insert(0, champ)
    pool = [p for p in pool if p != args.candidate]

    results = {}
    for opp in pool:
        proc = subprocess.run([sys.executable, "-I", EVAL, args.candidate, opp, "--maps", args.maps,
                               "--jobs", str(args.jobs), "--tag", f"g-{args.candidate}-vs-{opp}"],
                              capture_output=True, text=True, cwd=ROOT)
        m = SUMMARY.search(proc.stdout)
        if not m:
            print(f"{opp:20s} FAILED\n{proc.stdout[-1500:]}\n{proc.stderr[-1500:]}")
            results[opp] = None
            continue
        results[opp] = {"wins": int(m.group(3)), "losses": int(m.group(4)),
                        "gems_for": int(m.group(5)), "gems_against": int(m.group(6))}
        r = results[opp]
        n = r["wins"] + r["losses"]
        print(f"{opp:20s} {r['wins']:>3d}W-{r['losses']}L ({100 * r['wins'] / max(1, n):3.0f}%)  "
              f"gems {r['gems_for']} vs {r['gems_against']}", flush=True)

    ok = [r for r in results.values() if r]
    total_w = sum(r["wins"] for r in ok)
    total_n = sum(r["wins"] + r["losses"] for r in ok)
    print(f"GAUNTLET {args.candidate}: {total_w}/{total_n} ({100 * total_w / max(1, total_n):.0f}%) on maps={args.maps}")

    os.makedirs(RESULTS, exist_ok=True)
    with open(os.path.join(RESULTS, "gauntlet.jsonl"), "a") as f:
        f.write(json.dumps({
            "time": datetime.datetime.now(datetime.timezone.utc).isoformat(timespec="seconds"),
            "commit": git_commit(), "candidate": args.candidate, "maps": args.maps, "note": args.note,
            "results": results, "total_wins": total_w, "total_games": total_n,
        }) + "\n")


if __name__ == "__main__":
    main()
