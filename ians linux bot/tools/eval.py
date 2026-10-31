#!/usr/bin/env python3
"""Head-to-head evaluation harness for cambc bots.

Plays BOT_A against BOT_B on a set of maps, from both sides (A as team A, then A as
team B), via `cambc run-batch`, and prints per-match results plus a summary.

Usage (run from anywhere):
    python3 tools/eval.py BOT_A BOT_B [--maps quick|all|name1,name2,...] [--jobs N] [--tag TAG]
                                      [--one-side] [--keep]

BOT_A / BOT_B are directory names under bots/ (e.g. starter-python).
Map sets: "quick" = a fixed 12-map diverse sample (default), "all" = every map in maps/,
"sprint" = 20-map sample, or a comma-separated list of map names (without .map26a).
Results land in matches/<TAG>/ (default tag: A-vs-B). Replays are deleted unless --keep.
Exit summary line starts with "SUMMARY" so callers can grep it.
"""
import argparse
import json
import os
import shutil
import subprocess
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
# Prefer the workspace binary; fall back to a cambc on PATH (e.g. `pip install cambc` on a cluster).
CAMBC = os.path.join(ROOT, "cli", "cambc")
if not os.path.exists(CAMBC):
    CAMBC = os.environ.get("CAMBC") or shutil.which("cambc") or CAMBC

QUICK = [
    "00anvil", "00gemfight", "01islands", "02arena", "00monolith", "01elk-arena",
    "00lanes", "02famine", "01gold-rush", "00crater", "02the-pond", "adgato-gemcombat3",
]
SPRINT = QUICK + [
    "00quadrants", "01big-world", "02harvest", "00corners", "01starvation",
    "02guardians", "00stampede", "01concentrated-wealth",
]


def all_maps():
    return sorted(f[:-len(".map26a")] for f in os.listdir(os.path.join(ROOT, "maps")) if f.endswith(".map26a"))


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("bot_a")
    ap.add_argument("bot_b")
    ap.add_argument("--maps", default="quick")
    ap.add_argument("--jobs", type=int, default=4)
    ap.add_argument("--tag", default=None)
    ap.add_argument("--one-side", action="store_true", help="only play A as team A")
    ap.add_argument("--keep", action="store_true", help="keep replay files")
    ap.add_argument("--rounds", type=int, default=None)
    args = ap.parse_args()

    for b in (args.bot_a, args.bot_b):
        if not os.path.isdir(os.path.join(ROOT, "bots", b)):
            sys.exit(f"no such bot: bots/{b}")

    if args.maps == "quick":
        maps = QUICK
    elif args.maps == "sprint":
        maps = SPRINT
    elif args.maps == "all":
        maps = all_maps()
    else:
        maps = [m.strip() for m in args.maps.split(",") if m.strip()]
    for m in maps:
        if not os.path.exists(os.path.join(ROOT, "maps", m + ".map26a")):
            sys.exit(f"no such map: {m}")

    tag = args.tag or f"{args.bot_a}-vs-{args.bot_b}"
    out = os.path.join(ROOT, "matches", tag)
    os.makedirs(out, exist_ok=True)
    # Manifest paths are resolved relative to the manifest's directory, and the
    # manifest is whitespace-separated, so keep everything relative (ROOT has spaces).
    rel = "../.."
    rows = []
    games = []
    for m in maps:
        sides = [(args.bot_a, args.bot_b, "A")] if args.one_side else [
            (args.bot_a, args.bot_b, "A"), (args.bot_b, args.bot_a, "B")]
        for ta, tb, a_side in sides:
            name = f"{m}__{a_side}"
            rows.append(f"{rel}/bots/{ta} {rel}/bots/{tb} {rel}/maps/{m}.map26a "
                        f"{name}.repl26a --statistics {name}.json")
            games.append((m, a_side, name))
    manifest = os.path.join(out, "manifest.txt")
    with open(manifest, "w") as f:
        f.write("\n".join(rows) + "\n")
    for _, _, name in games:
        p = os.path.join(out, name + ".json")
        if os.path.exists(p):
            os.remove(p)

    cmd = [CAMBC, "run-batch", manifest, "--jobs", str(args.jobs), "--json", "--color", "never",
           "--log-limit", "0"]
    if args.rounds:
        cmd += ["--rounds", str(args.rounds)]
    proc = subprocess.run(cmd, cwd=ROOT, capture_output=True, text=True)
    if proc.returncode != 0:
        sys.stderr.write(proc.stdout[-3000:] + proc.stderr[-3000:])

    wins = losses = 0
    a_gems = b_gems = 0
    a_deaths = b_deaths = 0
    faults = 0
    print(f"{'map':28s} side  result  gemsA gemsB round  deathsA deathsB  draftA")
    for m, a_side, name in games:
        p = os.path.join(out, name + ".json")
        if not os.path.exists(p):
            print(f"{m:28s} {a_side}     MISSING (build/run failure?)")
            losses += 1
            continue
        d = json.load(open(p))
        a_team = "teamA" if a_side == "A" else "teamB"
        gems = {t["team"]: int(t["submittedGems"]) for t in d["teams"]}
        deaths = {"teamA": 0, "teamB": 0}
        for c in d["champions"]:
            deaths[c["team"]] += int(c["metrics"]["deaths"])
        b_team = "teamB" if a_team == "teamA" else "teamA"
        won = d["match"]["outcome"] == a_team
        wins += won
        losses += not won
        a_gems += gems[a_team]
        b_gems += gems[b_team]
        a_deaths += deaths[a_team]
        b_deaths += deaths[b_team]
        bf = d.get("diagnostics", {}).get("botFaults", {})
        faults += int(bf.get(a_team, 0))
        draft = ",".join(c["champion"] for c in d["roster"]["draft"] if c["team"] == a_team)
        print(f"{m:28s} {a_side}     {'WIN ' if won else 'loss'}    {gems[a_team]:5d} {gems[b_team]:5d} "
              f"{d['match']['roundsCompleted']:5d}  {deaths[a_team]:7d} {deaths[b_team]:7d}  {draft}")
        if not args.keep:
            r = os.path.join(out, name + ".repl26a")
            if os.path.exists(r):
                os.remove(r)
    n = max(1, wins + losses)
    print(f"SUMMARY {args.bot_a} vs {args.bot_b}: {wins}W-{losses}L ({100*wins/n:.0f}%)  "
          f"avg gems {a_gems/n:.0f} vs {b_gems/n:.0f}  avg deaths {a_deaths/n:.1f} vs {b_deaths/n:.1f}  "
          f"botFaults(A) {faults}")


if __name__ == "__main__":
    main()
