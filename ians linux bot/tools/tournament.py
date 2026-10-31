#!/usr/bin/env python3
"""Round-robin tournament between bots using tools/eval.py (both sides per map).

Usage:
    python3 tools/tournament.py BOT1 BOT2 [BOT3 ...] [--maps quick|sprint|all|a,b] [--jobs N]

Prints a pairwise win-rate matrix (row bot's win % vs column bot) and an overall ranking
by total wins, with average tributed gems as the tiebreak.
"""
import argparse
import itertools
import os
import re
import subprocess
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
EVAL = os.path.join(ROOT, "tools", "eval.py")
SUMMARY = re.compile(r"SUMMARY (\S+) vs (\S+): (\d+)W-(\d+)L .*avg gems (\d+) vs (\d+)")


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("bots", nargs="+")
    ap.add_argument("--maps", default="quick")
    ap.add_argument("--jobs", type=int, default=8)
    args = ap.parse_args()
    if len(args.bots) < 2:
        sys.exit("need at least two bots")

    wins = {b: 0 for b in args.bots}
    games = {b: 0 for b in args.bots}
    gems = {b: 0 for b in args.bots}
    matrix = {}
    for a, b in itertools.combinations(args.bots, 2):
        proc = subprocess.run([sys.executable, "-I", EVAL, a, b, "--maps", args.maps, "--jobs", str(args.jobs),
                               "--tag", f"rr-{a}-vs-{b}"], capture_output=True, text=True, cwd=ROOT)
        m = SUMMARY.search(proc.stdout)
        if not m:
            print(f"{a} vs {b}: FAILED\n{proc.stdout[-2000:]}\n{proc.stderr[-2000:]}")
            continue
        w, l, ga, gb = int(m.group(3)), int(m.group(4)), int(m.group(5)), int(m.group(6))
        n = w + l
        matrix[(a, b)] = w / n
        matrix[(b, a)] = l / n
        wins[a] += w
        wins[b] += l
        games[a] += n
        games[b] += n
        gems[a] += ga * n
        gems[b] += gb * n
        print(m.group(0), flush=True)

    width = max(len(b) for b in args.bots) + 2
    print("\nwin% (row vs column)")
    print(" " * width + "".join(f"{b[:10]:>11s}" for b in args.bots))
    for a in args.bots:
        cells = "".join(f"{'-':>11s}" if a == b else f"{100 * matrix.get((a, b), float('nan')):10.0f}%"
                        for b in args.bots)
        print(f"{a:{width}s}{cells}")
    print("\nRANKING")
    for b in sorted(args.bots, key=lambda b: (wins[b], gems[b]), reverse=True):
        g = max(1, games[b])
        print(f"  {b:{width}s} {wins[b]:4d}/{games[b]:<4d} wins ({100 * wins[b] / g:.0f}%)  avg gems {gems[b] / g:.0f}")


if __name__ == "__main__":
    main()
