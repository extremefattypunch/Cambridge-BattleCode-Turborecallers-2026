#!/usr/bin/env python3
"""Camp-economy metrics (Q28 / h_tempo) from cambc stats JSON.

us = eval's first bot: teamA in *__A.json / *-a.json, teamB in *__B.json / *-b.json.
Per team: camp taken/dealt, collected gems per champion per 100 rounds, monster damage per
monster-active champion-round by phase, active fraction, rounds to 500/1000 tributed gems,
deaths, kills, jungle-emblem round, fuelExhausted.
usage: python3.12 -I tools/camp_metrics.py [--games] [--maps m1,m2] paths(dirs or files)...
"""
import glob
import json
import os
import re
import statistics
import sys

PHASES = ((0, 300), (300, 600), (600, 1000), (1000, 2001))


def expand(runs, n):
    out = []
    for r in runs:
        out.extend([float(r["value"])] * r["duration"])
    if not out:
        out = [0.0]
    return out[:n] + [out[-1]] * max(0, n - len(out))


def us_of(path):
    b = os.path.basename(path)
    if b.endswith("__A.json") or b.endswith("-a.json"):
        return "teamA"
    if b.endswith("__B.json") or b.endswith("-b.json"):
        return "teamB"
    return None


def map_of(path):
    b = os.path.basename(path)
    b = re.sub(r"(__[AB]|-[ab])\.json$", "", b)
    return b


def game(path):
    d = json.load(open(path))
    us = us_of(path)
    them = "teamB" if us == "teamA" else "teamA"
    rounds = d["match"]["roundsCompleted"]
    n = rounds + 1
    ser = {}
    names = {}
    for t in d["championTimelines"]:
        o = t["owner"]
        names[o["id"]] = (o["team"], o["name"])
        ser.setdefault(o["id"], {})[t["metric"]] = expand(t["runs"], n)
    sub = {}
    for t in d["teamTimelines"]:
        if t["metric"] == "submittedGems":
            sub[t["owner"]] = expand(t["runs"], n)
    final = {t["team"]: int(t["submittedGems"]) for t in d["teams"]}
    out = {"map": map_of(path), "path": path, "rounds": rounds, "outcome": d["match"]["outcome"],
           "faults": d["diagnostics"].get("botFaults", {})}
    for side, team in (("us", us), ("them", them)):
        champs = [cid for cid, (tm, nm) in names.items() if tm == team]
        r = {"score": final.get(team, 0), "n": len(champs)}
        dealt = sum(ser[c].get("monsterDamageDone", [0])[-1] for c in champs)
        taken = sum(ser[c].get("monsterDamageTaken", [0])[-1] for c in champs)
        r["dealt"] = dealt
        r["taken"] = taken
        r["ratio"] = taken / dealt if dealt else float("nan")
        coll = sum(ser[c].get("collectedGems", [0])[-1] for c in champs)
        r["gemrate"] = coll / max(1, len(champs)) / max(1, rounds) * 100.0
        r["deaths"] = sum(ser[c].get("deaths", [0])[-1] for c in champs)
        r["kills"] = sum(ser[c].get("kills", [0])[-1] for c in champs)
        r["gold"] = sum(ser[c].get("earnedGold", [0])[-1] for c in champs)
        act = [0] * len(PHASES)
        dmg = [0.0] * len(PHASES)
        crs = [0] * len(PHASES)
        for c in champs:
            md = ser[c].get("monsterDamageDone")
            if not md:
                continue
            for i in range(1, n):
                inc = md[i] - md[i - 1]
                for k, (a, b) in enumerate(PHASES):
                    if a <= i < b:
                        crs[k] += 1
                        if inc > 0:
                            act[k] += 1
                            dmg[k] += inc
                        break
        r["dpr"] = [dmg[k] / act[k] if act[k] else None for k in range(len(PHASES))]
        r["actfrac"] = [act[k] / crs[k] if crs[k] else None for k in range(len(PHASES))]
        tl = sub.get(team, [0])
        r["r500"] = next((i for i, v in enumerate(tl) if v >= 500), None)
        r["r1000"] = next((i for i, v in enumerate(tl) if v >= 1000), rounds if final.get(team, 0) >= 1000 else None)
        r["g300"] = tl[min(300, len(tl) - 1)]
        jr = []
        fuel = 0
        for e in d["events"]:
            if e["owner"].get("team") != team:
                continue
            if e["kind"] == "itemCombination":
                for x in e["entries"]:
                    if "Jungle Emblem" in (x["target"].get("name") or ""):
                        jr.append(x["timestamp"]["round"])
                        break
            elif e["kind"] == "fuelExhausted":
                fuel += len(e["entries"])
        r["jungle_r"] = sorted(jr)
        r["fuel"] = fuel
        out[side] = r
    su, st = out["us"]["score"], out["them"]["score"]
    out["res"] = "W" if su > st else ("L" if su < st else "T")
    return out


def collect(paths):
    files = []
    for p in paths:
        if os.path.isdir(p):
            files += sorted(glob.glob(os.path.join(p, "*.json")))
        else:
            files.append(p)
    return [f for f in files if us_of(f)]


def fmt(x, w=6, p=0):
    if x is None:
        return "-".rjust(w)
    if isinstance(x, float) and x != x:
        return "nan".rjust(w)
    return f"{x:{w}.{p}f}"


def main():
    args = sys.argv[1:]
    show = "--games" in args
    args = [a for a in args if a != "--games"]
    maps = None
    if "--maps" in args:
        i = args.index("--maps")
        maps = set(args[i + 1].split(","))
        del args[i:i + 2]
    games = [game(f) for f in collect(args)]
    if maps:
        games = [g for g in games if g["map"] in maps]
    if show:
        print("map              res  us-them      rnd | ratio us/them | gemrate us/them | r1000 us/them | D us/them K us/them | dprP3 us/them | jungle_r(us)")
        for g in games:
            u, t = g["us"], g["them"]
            print(f"{g['map'][:16]:16} {g['res']}  {u['score']:4}-{t['score']:<4} {g['rounds']:5} | "
                  f"{fmt(u['ratio'],5,2)} {fmt(t['ratio'],5,2)} | {fmt(u['gemrate'],5,1)} {fmt(t['gemrate'],5,1)} | "
                  f"{fmt(u['r1000'],5)} {fmt(t['r1000'],5)} | {u['deaths']:3.0f} {t['deaths']:3.0f}  {u['kills']:3.0f} {t['kills']:3.0f} | "
                  f"{fmt(u['dpr'][3],4)} {fmt(t['dpr'][3],4)} | {u['jungle_r'][:5]}")
    if not games:
        print("no games")
        return
    w = sum(g["res"] == "W" for g in games)
    l = sum(g["res"] == "L" for g in games)
    print(f"games {len(games)}  W{w} L{l} T{len(games)-w-l}  botFaults "
          f"{sum(sum(g['faults'].values()) for g in games)}")
    for side in ("us", "them"):
        rs = [g[side] for g in games]
        def m(key, f=lambda v: v):
            v = [f(r[key]) for r in rs if r[key] is not None and not (isinstance(r[key], float) and r[key] != r[key])]
            return statistics.mean(v) if v else None
        tk = sum(r["taken"] for r in rs)
        dl = sum(r["dealt"] for r in rs)
        dpr = []
        af = []
        for k in range(len(PHASES)):
            v = [r["dpr"][k] for r in rs if r["dpr"][k] is not None]
            dpr.append(statistics.mean(v) if v else None)
            v = [r["actfrac"][k] for r in rs if r["actfrac"][k] is not None]
            af.append(statistics.mean(v) if v else None)
        r1k = [r["r1000"] for r in rs if r["r1000"] is not None]
        r5 = [r["r500"] for r in rs if r["r500"] is not None]
        print(f"{side:4} ratio(pooled) {tk/dl if dl else float('nan'):.3f} ratio(mean) {fmt(m('ratio'),5,3)} "
              f"gemrate {fmt(m('gemrate'),5,2)} score {fmt(m('score'),5)} gems@300 {fmt(m('g300'),4)} "
              f"deaths {fmt(m('deaths'),4,1)} kills {fmt(m('kills'),4,1)} gold {fmt(m('gold'),6)} fuelEx {sum(r['fuel'] for r in rs)} "
              f"| dpr P0-3 {' '.join(fmt(x,4) for x in dpr)} | act {' '.join(fmt(x,4,2) for x in af)} "
              f"| r500 n={len(r5)} mean {fmt(statistics.mean(r5) if r5 else None,5)} r1000 n={len(r1k)} mean {fmt(statistics.mean(r1k) if r1k else None,5)}")


if __name__ == "__main__":
    main()
