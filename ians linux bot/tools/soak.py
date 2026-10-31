#!/usr/bin/env python3
"""Continuous soak testing: the current champion vs a rotating opponent pool on random maps.

Usage:
    python3 tools/soak.py [--jobs N] [--maps-per-batch K] [--iterations I]   # run (I=0: forever)
    python3 tools/soak.py --report [--last N]                                # summarise results

Each batch reads results/CHAMPION, picks the next opponent from the pool (bots that exist under bots/),
plays K random maps from maps/ both sides via tools/eval.py, and appends one JSON line per game to
matches/soak/soak.jsonl (gitignored). The report shows the champion's win rate per map and per opponent,
which points improvement work at the weakest maps and match-ups.
"""
import argparse
import collections
import datetime
import glob
import json
import os
import random
import shutil
import subprocess
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
EVAL = os.path.join(ROOT, "tools", "eval.py")
OUT = os.path.join(ROOT, "matches", "soak")
LOG = os.path.join(OUT, "soak.jsonl")
POOL = ["sf_bank", "tb_merge_a", "tb_aggro", "imit_test", "lad_vcst", "lad_svrc", "sf_base", "tb_economy",
        "starter-python"]


def champion():
    return open(os.path.join(ROOT, "results", "CHAMPION")).read().strip()


def all_maps():
    return sorted(f[:-7] for f in os.listdir(os.path.join(ROOT, "maps")) if f.endswith(".map26a"))


def run_batch(i, champ, opp, maps, jobs):
    tag = f"soak-batch-{i % 4}"
    folder = os.path.join(ROOT, "matches", tag)
    shutil.rmtree(folder, ignore_errors=True)
    subprocess.run([sys.executable, "-I", EVAL, champ, opp, "--maps", ",".join(maps), "--jobs", str(jobs),
                    "--tag", tag], cwd=ROOT, capture_output=True, text=True)
    now = datetime.datetime.now(datetime.timezone.utc).isoformat(timespec="seconds")
    rows = []
    for p in sorted(glob.glob(os.path.join(folder, "*__[AB].json"))):
        name = os.path.basename(p)[:-5]
        m, side = name.rsplit("__", 1)
        d = json.load(open(p))
        me = "teamA" if side == "A" else "teamB"
        gems = {t["team"]: int(t["submittedGems"]) for t in d["teams"]}
        deaths = collections.Counter()
        for c in d["champions"]:
            deaths[c["team"]] += int(c["metrics"]["deaths"])
        other = "teamB" if me == "teamA" else "teamA"
        rows.append({"time": now, "champion": champ, "opponent": opp, "map": m, "side": side,
                     "win": d["match"]["outcome"] == me, "gems": gems[me], "gems_opp": gems[other],
                     "rounds": d["match"]["roundsCompleted"], "deaths": deaths[me], "deaths_opp": deaths[other],
                     "faults": int(d.get("diagnostics", {}).get("botFaults", {}).get(me, 0))})
    os.makedirs(OUT, exist_ok=True)
    with open(LOG, "a") as f:
        for r in rows:
            f.write(json.dumps(r) + "\n")
    return rows


def report(last):
    if not os.path.exists(LOG):
        sys.exit("no soak results yet")
    rows = [json.loads(l) for l in open(LOG) if l.strip()]
    champ = champion()
    rows = [r for r in rows if r["champion"] == champ][-last:]
    if not rows:
        sys.exit(f"no soak results for champion {champ}")
    w = sum(r["win"] for r in rows)
    print(f"champion {champ}: {w}/{len(rows)} ({100 * w / len(rows):.0f}%) over last {len(rows)} soak games, "
          f"faults {sum(r['faults'] for r in rows)}")
    for key in ("opponent", "map"):
        agg = collections.defaultdict(lambda: [0, 0, 0, 0])
        for r in rows:
            a = agg[r[key]]
            a[0] += r["win"]
            a[1] += 1
            a[2] += r["gems"]
            a[3] += r["gems_opp"]
        print(f"\nby {key} (worst first)")
        for k, (wins, n, g, go) in sorted(agg.items(), key=lambda kv: (kv[1][0] / kv[1][1], kv[1][1])):
            print(f"  {k:28s} {wins:3d}/{n:<3d} ({100 * wins / n:3.0f}%)  gems {g / n:5.0f} vs {go / n:5.0f}")


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--jobs", type=int, default=3)
    ap.add_argument("--maps-per-batch", type=int, default=6)
    ap.add_argument("--iterations", type=int, default=0)
    ap.add_argument("--report", action="store_true")
    ap.add_argument("--last", type=int, default=2000)
    args = ap.parse_args()
    if args.report:
        report(args.last)
        return
    maps = all_maps()
    i = 0
    while args.iterations == 0 or i < args.iterations:
        champ = champion()
        pool = [b for b in POOL if b != champ and os.path.isdir(os.path.join(ROOT, "bots", b))]
        if not pool:
            sys.exit("empty opponent pool")
        opp = pool[i % len(pool)]
        rng = random.Random(i * 7919 + len(maps))
        batch = rng.sample(maps, min(args.maps_per_batch, len(maps)))
        rows = run_batch(i, champ, opp, batch, args.jobs)
        w = sum(r["win"] for r in rows)
        print(f"[{datetime.datetime.now():%H:%M}] batch {i}: {champ} vs {opp}: {w}/{len(rows)}", flush=True)
        i += 1


if __name__ == "__main__":
    main()
