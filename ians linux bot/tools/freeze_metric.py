#!/usr/bin/env python3
"""Freeze detector for cambc match statistics (Q21).

A champion is *idle* in a round when it is alive and none of its activity counters change:
monster/champion damage done or taken, healing, shielding, gems collected or submitted,
gold earned or spent, kills, assists, deaths. A *frozen stretch* is a run of consecutive idle
rounds at least --min rounds long (default 150: longer than walking across any map without
touching a camp). Dead rounds (death + RESPAWN 60) never count as idle.

The stats JSON has no positions, so this measures "did nothing for a long time", which
catches the respawn-rule 2-cycle (0 damage for ~1,800 rounds) and other stalls alike.

Usage:
  python3 -I tools/freeze_metric.py matches/<tag>            # every <map>__<side>.json
  python3 -I tools/freeze_metric.py file1.json file2.json    # explicit files
  options: --min N (stretch length), --per-game (one line per game), --team A|B|both
Output: per game frozen champion-rounds for "us" (the eval's first bot) and "them",
plus totals. The eval's first bot is teamA in <map>__A.json and teamB in <map>__B.json.
"""
import argparse
import glob
import json
import os
import sys

ACTIVITY = ("monsterDamageDone", "monsterDamageTaken", "championDamageDone", "championDamageTaken",
            "healingDone", "healingReceived", "shieldingDone", "collectedGems", "submittedGems",
            "earnedGold", "spentGold", "kills", "assists", "deaths")
RESPAWN = 60


def expand(runs, n):
    out = []
    for r in runs:
        out.extend([r["value"]] * r["duration"])
    return out[:n] + [out[-1] if out else "0"] * max(0, n - len(out))


def game_freeze(path, min_len):
    d = json.load(open(path))
    n = d["championTimelines"][0]["sampleCount"] if d["championTimelines"] else 0
    rounds = d["match"]["roundsCompleted"]
    series = {}
    names = {}
    for t in d["championTimelines"]:
        o = t["owner"]
        names[o["id"]] = (o["team"], o["name"])
        series.setdefault(o["id"], {})[t["metric"]] = expand(t["runs"], n)
    res = {}
    for cid, m in series.items():
        team, name = names[cid]
        dead = [False] * n
        if "deaths" in m:
            dv = m["deaths"]
            for r in range(1, n):
                if dv[r] != dv[r - 1]:
                    for k in range(r, min(n, r + RESPAWN + 1)):
                        dead[k] = True
        frozen = 0
        longest = 0
        stretches = []
        run_start = None
        for r in range(1, n):
            active = dead[r] or any(m[k][r] != m[k][r - 1] for k in ACTIVITY if k in m)
            if not active:
                if run_start is None:
                    run_start = r
            if active or r == n - 1:
                if run_start is not None:
                    end = r if active else r + 1
                    ln = end - run_start
                    if ln >= min_len:
                        frozen += ln
                        stretches.append((run_start, end))
                    longest = max(longest, ln)
                    run_start = None
        res[cid] = {"team": team, "name": name, "frozen": frozen, "longest": longest,
                    "stretches": stretches}
    return res, rounds, d["match"].get("outcome")


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("paths", nargs="+")
    ap.add_argument("--min", type=int, default=150)
    ap.add_argument("--per-game", action="store_true")
    ap.add_argument("--champs", action="store_true", help="list frozen stretches per champion")
    args = ap.parse_args()
    files = []
    for p in args.paths:
        if os.path.isdir(p):
            files += sorted(f for f in glob.glob(os.path.join(p, "*__*.json")))
        else:
            files.append(p)
    tot = {"us": 0, "them": 0}
    games = {"us": 0, "them": 0}
    cr = {"us": 0, "them": 0}
    rows = []
    for f in files:
        base = os.path.basename(f)[:-5]
        side = base.rsplit("__", 1)[-1] if "__" in base else "A"
        us_team = "teamA" if side == "A" else "teamB"
        try:
            res, rounds, outcome = game_freeze(f, args.min)
        except Exception as e:  # noqa
            print(f"skip {f}: {e}", file=sys.stderr)
            continue
        fr = {"us": 0, "them": 0}
        nch = {"us": 0, "them": 0}
        for cid, r in res.items():
            k = "us" if r["team"] == us_team else "them"
            fr[k] += r["frozen"]
            nch[k] += 1
        for k in fr:
            tot[k] += fr[k]
            cr[k] += nch[k] * rounds
            if fr[k] > 0:
                games[k] += 1
        won = outcome == us_team
        rows.append((base, fr["us"], fr["them"], "W" if won else "L"))
        if args.per_game and (fr["us"] or fr["them"]):
            print(f"{base:40s} {'W' if won else 'L'}  frozen us {fr['us']:5d}  them {fr['them']:5d}")
        if args.champs:
            for cid, r in sorted(res.items()):
                if r["stretches"]:
                    k = "us" if r["team"] == us_team else "them"
                    print(f"   {k:4s} {r['name']:14s} frozen {r['frozen']:5d} stretches {r['stretches']}")
    print(f"FREEZE (idle stretches >= {args.min} rounds) over {len(rows)} games: "
          f"us {tot['us']} champ-rounds ({100.0 * tot['us'] / max(1, cr['us']):.1f}% of alive-or-dead time, "
          f"{games['us']} games affected)  them {tot['them']} ({100.0 * tot['them'] / max(1, cr['them']):.1f}%, "
          f"{games['them']} games)")


if __name__ == "__main__":
    main()
