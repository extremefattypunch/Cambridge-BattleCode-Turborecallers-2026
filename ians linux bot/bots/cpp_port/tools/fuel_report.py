#!/usr/bin/env python3
"""Per-turn fuel percentiles from cambc replays (.repl26a zips), for the C++ port's fuel budget.

Usage: python3 -I bots/cpp_port/tools/fuel_report.py REPLAY_OR_DIR [...] [--team a|b] [--budget 100000]

team-X.fuel = 13-byte header, then little-endian u64 values. The first 8 values are the budget table
(draft first turn, draft turn, first play turn, play turn) for each of the two teams. Every value after
that is the fuel used by one bot turn: draft turns and all of the team's champions, interleaved.
"at/over budget" includes each champion's first play turn, which may legitimately use up to 2x budget;
any other turn at the budget was suspended (fuelExhausted).
"""
import argparse
import os
import struct
import zipfile


def turns(path, team):
    data = zipfile.ZipFile(path).read(f"team-{team}.fuel")
    vals = [struct.unpack_from("<Q", data, 13 + 8 * i)[0] for i in range((len(data) - 13) // 8)]
    return vals[:8], vals[8:]


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("paths", nargs="+")
    ap.add_argument("--team", default="a")
    ap.add_argument("--budget", type=int, default=0, help="per-turn budget (default: from the header)")
    args = ap.parse_args()
    files = []
    for p in args.paths:
        if os.path.isdir(p):
            files += sorted(os.path.join(p, f) for f in os.listdir(p) if f.endswith(".repl26a"))
        else:
            files.append(p)
    for f in files:
        try:
            budgets, v = turns(f, args.team)
        except (KeyError, zipfile.BadZipFile) as e:
            print(f"{os.path.basename(f)}: {e}")
            continue
        budget = args.budget or budgets[3]
        play = sorted(x for x in v if 0 < x <= 2 * budget)  # drop the 100x draft turn
        if not play:
            continue
        n = len(play)
        q = lambda p: play[min(n - 1, int(p * n))]
        full = sum(1 for x in play if x >= budget)
        # the first 12 entries hold the draft turns (<= 5) and every champion's first play turn (<= 6, 2x budget)
        late = [x for x in v[12:] if 0 < x <= 2 * budget]
        exh = sum(1 for x in late if x >= budget)
        lmax = max(late) if late else 0
        print(f"{os.path.basename(f)[:60]:60s} team {args.team} turns {n:6d}  p50 {q(.5):7d}  p90 {q(.9):7d}  "
              f"p99 {q(.99):7d}  max {play[-1]:7d}  at/over budget {full} ({100.0 * full / n:.2f}%)  "
              f"after-first: max {lmax:7d} exhausted {exh}")


if __name__ == "__main__":
    main()
