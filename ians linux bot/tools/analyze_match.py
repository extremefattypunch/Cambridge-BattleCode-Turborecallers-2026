#!/usr/bin/env python3
"""Detailed post-game analysis of cambc --statistics JSON files (the learning step after every experiment).

Usage:
    python3 tools/analyze_match.py matches/<tag>/<map>__A.json [more.json ...]   # one narrative per game
    python3 tools/analyze_match.py --summary matches/<tag>                         # compare wins vs losses
    python3 tools/analyze_match.py --summary matches/<tag> --games                 # plus one line per game

"Us" is the bot that was BOT_A in tools/eval.py: team A in <map>__A.json, team B in <map>__B.json
(override with --us teamA|teamB). A game report covers:
- the gem race (tributed gems at checkpoints, when the winner pulled ahead);
- the opening tempo (first camp clear, gem pickup, tribute, item and kill);
- each champion's line (kills, deaths, gems, damage, gold, emblems, wards, fuel suspensions);
- every death with its killer, location and gems lost;
- tribute habits.
The summary contrasts these metrics between our wins and losses, so you can see *why* games are lost.
"""
import argparse
import collections
import glob
import json
import os
import statistics
import sys

CHECKPOINTS = (100, 250, 500, 750, 1000, 1500, 2000)


def value_at(runs, rnd):
    """Value of a run-length-encoded timeline at a given round (runs start at round 0)."""
    t = 0
    last = 0
    for r in runs:
        if t + r["duration"] > rnd:
            return float(r["value"])
        t += r["duration"]
        last = float(r["value"])
    return last


def team_of(path, override):
    if override:
        return override
    return "teamA" if path.endswith("__A.json") else "teamB"


def entries(d, kind, team=None):
    for e in d["events"]:
        if e["kind"] != kind:
            continue
        own = e.get("owner", {})
        if team and own.get("team") != team:
            continue
        for x in e["entries"]:
            yield own, x


def first_round(d, kind, team):
    rounds = [x["timestamp"]["round"] for _, x in entries(d, kind, team)]
    return min(rounds) if rounds else None


def game_facts(path, us):
    d = json.load(open(path))
    them = "teamB" if us == "teamA" else "teamA"
    m = d["match"]
    tl = {t["owner"]: t["runs"] for t in d["teamTimelines"] if t["metric"] == "submittedGems"}
    gems_final = {t["team"]: int(t["submittedGems"]) for t in d["teams"]}
    facts = {
        "map": os.path.basename(path).rsplit("__", 1)[0], "path": path, "us": us,
        "win": m["outcome"] == us, "rounds": m["roundsCompleted"], "size": f"{m['width']}x{m['height']}",
        "gems_us": gems_final[us], "gems_them": gems_final[them],
        "race": {c: (value_at(tl.get(us, []), c), value_at(tl.get(them, []), c)) for c in CHECKPOINTS},
        "draft_us": [c["champion"] for c in d["roster"]["draft"] if c["team"] == us],
        "draft_them": [c["champion"] for c in d["roster"]["draft"] if c["team"] == them],
    }
    for side, team in (("us", us), ("them", them)):
        facts[f"first_clear_{side}"] = first_round(d, "campClear", team)
        facts[f"first_tribute_{side}"] = first_round(d, "gemSubmission", team)
        facts[f"first_item_{side}"] = first_round(d, "buyItem", team)
        facts[f"first_kill_{side}"] = first_round(d, "kill", team)
        tribs = [int(x["value"]) for _, x in entries(d, "gemSubmission", team)]
        facts[f"tributes_{side}"] = tribs
        deaths = [(o, x) for o, x in entries(d, "death", team)]
        facts[f"deaths_camp_{side}"] = sum(1 for _, x in deaths if x.get("context") == "camp")
        facts[f"deaths_champ_{side}"] = len(deaths) - facts[f"deaths_camp_{side}"]
        facts[f"gemloss_{side}"] = sum(int(x["value"]) for _, x in entries(d, "gemLoss", team))
        facts[f"clears_{side}"] = sum(1 for _ in entries(d, "campClear", team))
        facts[f"kills_{side}"] = sum(1 for _ in entries(d, "kill", team))
        facts[f"fuel_{side}"] = sum(1 for _ in entries(d, "fuelExhausted", team))
        facts[f"wards_{side}"] = sum(1 for _ in entries(d, "wardPlacement", team))
        facts[f"locks_{side}"] = sum(1 for _, x in entries(d, "buyConsumable", team)
                                     if "Lock" in str(x.get("target", {}).get("name", "")))
        champs = [c for c in d["champions"] if c["team"] == team]
        facts[f"monster_dmg_{side}"] = sum(float(c["metrics"]["monsterDamageDone"]) for c in champs)
        facts[f"champ_dmg_{side}"] = sum(float(c["metrics"]["championDamageDone"]) for c in champs)
        facts[f"gold_{side}"] = sum(int(c["metrics"]["earnedGold"]) for c in champs)
    facts["_d"] = d
    return facts


def lead_change(f):
    """First checkpoint from which the eventual winner stays ahead."""
    winner_is_us = f["win"]
    stay = None
    for c in CHECKPOINTS:
        a, b = f["race"][c]
        ahead = a > b if winner_is_us else b > a
        if ahead and stay is None:
            stay = c
        elif not ahead:
            stay = None
    return stay


def report(f):
    d, us = f["_d"], f["us"]
    them = "teamB" if us == "teamA" else "teamA"
    res = "WIN" if f["win"] else "LOSS"
    print(f"\n=== {f['map']} ({f['size']})  {res}  {f['gems_us']}-{f['gems_them']}  rounds {f['rounds']}  [us={us}]")
    print(f"draft us:   {', '.join(f['draft_us'])}\ndraft them: {', '.join(f['draft_them'])}")
    print("gem race (tributed, us-them): " + "  ".join(f"r{c}:{int(a)}-{int(b)}" for c, (a, b) in f["race"].items()
                                                       if c <= f["rounds"] + 1))
    print(f"winner ahead from round: {lead_change(f)}")
    print("opening tempo (first round)   us / them")
    for k in ("clear", "tribute", "item", "kill"):
        print(f"  first {k:8s} {str(f['first_' + k + '_us']):>6s} / {str(f['first_' + k + '_them'])}")
    for side, team in (("us", us), ("them", them)):
        tr = f[f"tributes_{side}"]
        mean = statistics.mean(tr) if tr else 0
        print(f"{side:4s}: clears {f['clears_' + side]:3d}  kills {f['kills_' + side]:3d}  deaths camp/champ "
              f"{f['deaths_camp_' + side]}/{f['deaths_champ_' + side]}  gems lost {f['gemloss_' + side]:4d}  "
              f"tributes {len(tr)} (mean {mean:.1f})  monsterDmg {f['monster_dmg_' + side]:.0f}  "
              f"champDmg {f['champ_dmg_' + side]:.0f}  gold {f['gold_' + side]}  wards {f['wards_' + side]}  "
              f"locks {f['locks_' + side]}  fuelExh {f['fuel_' + side]}")
    print("per champion: name team | K/D | collected/submitted gems | monsterDmg | champDmg done/taken | gold earned | emblems")
    for c in d["champions"]:
        mt = c["metrics"]
        emblems = [f"{i['item'].replace(' Emblem of ', ':')}x{i['quantity']}" for i in c.get("items", [])
                   if "Emblem" in i["item"]]
        tag = "us  " if c["team"] == us else "them"
        print(f"  {tag} {c['name']:13s} {mt['kills']}/{mt['deaths']} | {mt['collectedGems']}/{mt['submittedGems']} | "
              f"{float(mt['monsterDamageDone']):.0f} | {float(mt['championDamageDone']):.0f}/"
              f"{float(mt['championDamageTaken']):.0f} | {mt['earnedGold']} | {' '.join(emblems)}")
    deaths = sorted(((x["timestamp"]["round"], o, x) for o, x in entries(d, "death")), key=lambda t: t[0])
    losses = {(x["timestamp"]["round"], o.get("name")): int(x["value"]) for o, x in entries(d, "gemLoss")}
    if deaths:
        print("deaths (round victim(team) <- killer @x,y gemsLost):")
        for rnd, o, x in deaths[:40]:
            t = x.get("target") or {}
            killer = t.get("name") or f"camp#{t.get('id')}" if isinstance(t, dict) else str(t)
            side = "us" if o.get("team") == us else "them"
            print(f"  r{rnd:5d} {o.get('name')}({side}) <- {killer} @{x.get('x')},{x.get('y')} "
                  f"lost {losses.get((rnd, o.get('name')), 0)}")
        if len(deaths) > 40:
            print(f"  ... {len(deaths) - 40} more")


def summary(folder, show_games):
    paths = sorted(glob.glob(os.path.join(folder, "*__[AB].json")))
    if not paths:
        sys.exit(f"no statistics JSON in {folder}")
    facts = [game_facts(p, None if False else team_of(p, None)) for p in paths]
    groups = {"WINS": [f for f in facts if f["win"]], "LOSSES": [f for f in facts if not f["win"]]}
    keys = ["gems_us", "gems_them", "rounds", "first_clear_us", "first_clear_them", "first_tribute_us",
            "first_tribute_them", "clears_us", "clears_them", "kills_us", "kills_them", "deaths_camp_us",
            "deaths_champ_us", "deaths_champ_them", "gemloss_us", "gemloss_them", "monster_dmg_us",
            "monster_dmg_them", "champ_dmg_us", "champ_dmg_them", "gold_us", "gold_them", "fuel_us"]
    print(f"{folder}: {len(groups['WINS'])} wins, {len(groups['LOSSES'])} losses\n")
    print(f"{'metric (mean)':22s} {'WINS':>10s} {'LOSSES':>10s}")
    for k in keys:
        row = []
        for g in ("WINS", "LOSSES"):
            vals = [f[k] for f in groups[g] if f[k] is not None]
            row.append(f"{statistics.mean(vals):10.1f}" if vals else f"{'-':>10s}")
        print(f"{k:22s} {row[0]} {row[1]}")
    for g in ("WINS", "LOSSES"):
        tr = [t for f in groups[g] for t in f["tributes_us"]]
        if tr:
            print(f"mean tribute ({g.lower()}): {statistics.mean(tr):.1f} over {len(tr)} tributes")
    for c in (250, 500, 1000):
        for g in ("WINS", "LOSSES"):
            vals = [f["race"][c][0] - f["race"][c][1] for f in groups[g] if f["rounds"] >= c]
            if vals:
                print(f"gem lead at r{c} ({g.lower()}): {statistics.mean(vals):+.0f}")
    opp = collections.Counter(ch for f in groups["LOSSES"] for ch in f["draft_them"])
    if opp:
        print("opponent champions in our losses:", ", ".join(f"{k} {v}" for k, v in opp.most_common()))
    if show_games:
        print("\nper game:")
        for f in facts:
            print(f"  {f['map']:24s} {'W' if f['win'] else 'L'} {f['gems_us']:5d}-{f['gems_them']:<5d} r{f['rounds']:<5d} "
                  f"K/D {f['kills_us']}/{f['deaths_camp_us'] + f['deaths_champ_us']} vs {f['kills_them']}/"
                  f"{f['deaths_camp_them'] + f['deaths_champ_them']}  ahead-from r{lead_change(f)}")


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("paths", nargs="+")
    ap.add_argument("--summary", action="store_true")
    ap.add_argument("--games", action="store_true")
    ap.add_argument("--us", choices=["teamA", "teamB"])
    args = ap.parse_args()
    if args.summary:
        for folder in args.paths:
            summary(folder, args.games)
        return
    for p in args.paths:
        report(game_facts(p, team_of(p, args.us)))


if __name__ == "__main__":
    main()
