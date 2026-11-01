#!/usr/bin/env python3
"""Pull our new ranked ladder games with the cambc CLI (no browser) and log them.

Usage:
    python3 tools/ladder_pull.py [--max-pages N]

Needs a `cambc login` session. For every finished ranked game not yet in results/ladder-games.jsonl:
- saves its statistics to matches/ladder/summary/<matchId>__<A|B>.json, where the suffix is OUR side, so
  `tools/analyze_match.py` and `--summary` treat our team as "us" without flags;
- appends one row in ladder_log.py's format (scores and rounds from the statistics, our bot version from
  `cambc submissions list` = the newest upload created before the game).
Ratings come from `cambc ladder` at pull time, so `opp_rating` is the opponent's CURRENT rating and
`our_rating_after` is our current rating (exact only for the newest set). Then prints ladder_log.py's summary.
Games carry no submission id, and an upload stays `queued` until verified, so the bot version of a game is
the newest version whose ACTIVATION time is before it. Activation times live in results/ladder-versions.json;
a version is recorded the first time a pull sees it active. Its activation time is when the previously live version
went inactive (that version's `statusAt`); the new version's own `statusAt` can be refreshed later, so it only
serves as a fallback.
"""
import argparse
import json
import os
import shutil
import subprocess
import sys
import time

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(ROOT, "tools"))
from ladder_log import CHAMPS, LOG, ME  # noqa: E402

CAMBC = os.path.join(ROOT, "cli", "cambc")
if not os.path.exists(CAMBC):
    CAMBC = os.environ.get("CAMBC") or shutil.which("cambc") or CAMBC
OUT = os.path.join(ROOT, "matches", "ladder", "summary")
VERSIONS = os.path.join(ROOT, "results", "ladder-versions.json")


def cli_json(*args):
    proc = subprocess.run([CAMBC, *args, "--json"], capture_output=True, text=True)
    if proc.returncode != 0:
        sys.exit(f"cambc {' '.join(args)} failed: {proc.stderr.strip()[-500:]}")
    return json.loads(proc.stdout)


def activations(subs):
    acts = json.load(open(VERSIONS)) if os.path.exists(VERSIONS) else {}
    for s in subs:
        if s["active"] and str(s["version"]) not in acts:
            prev = max((int(v) for v in acts), default=None)
            prev_sub = next((p for p in subs if p["version"] == prev and not p["active"]), None)
            acts[str(s["version"])] = prev_sub["statusAt"] if prev_sub else s["statusAt"]
            with open(VERSIONS, "w") as f:
                json.dump(acts, f, indent=1)
    return acts


def ratings():
    by_id, page = {}, 1
    while True:
        d = cli_json("ladder", "--page", str(page), "--limit", "100")
        for t in d["teams"]:
            by_id[t["teamId"]] = t["rating"]
        if len(d["teams"]) < 100:
            return by_id
        page += 1


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--max-pages", type=int, default=20, help="pages of 50 matches to scan")
    args = ap.parse_args()
    seen = set()
    if os.path.exists(LOG):
        seen = {json.loads(l)["id"] for l in open(LOG) if l.strip()}

    new, cursor = [], None
    for _ in range(args.max_pages):
        extra = ["--cursor", cursor] if cursor else []
        d = cli_json("matches", "list", "--team", "me", "--kind", "ranked", "--limit", "50", *extra)
        page = [m for m in d["matches"] if m["status"] == "finished"]
        fresh = [m for m in page if m["matchId"] not in seen]
        new += fresh
        cursor = d.get("nextCursor")
        if not cursor or (page and not fresh):
            break
    if not new:
        print("no new ranked games")
    else:
        acts = activations(cli_json("submissions", "list")["submissions"])
        rating = ratings()
        os.makedirs(OUT, exist_ok=True)
        with open(LOG, "a") as f:
            for m in sorted(new, key=lambda m: m["finishedAt"] or ""):
                me = next(t for t in m["teams"] if t["teamId"] == ME)
                op = next(t for t in m["teams"] if t["teamId"] != ME)
                if me["result"] not in ("win", "loss"):
                    continue
                side = me["side"].upper()
                path = os.path.join(OUT, f"{m['matchId']}__{side}.json")
                if not os.path.exists(path):
                    for attempt in range(6):  # the site rate-limits summary downloads (HTTP 429)
                        proc = subprocess.run([CAMBC, "matches", "summary", m["matchId"], "--json", "-o", path],
                                              capture_output=True, text=True)
                        if proc.returncode == 0 or "429" not in proc.stderr:
                            break
                        time.sleep(2 + 3 * attempt)
                    if proc.returncode != 0:
                        print(f"skip {m['matchId']}: summary failed: {proc.stderr.strip()[-200:]}")
                        continue
                st = json.load(open(path))
                gems = {t["team"]: int(t["submittedGems"]) for t in st["teams"]}
                us_team = "team" + side
                them_team = "teamB" if side == "A" else "teamA"
                live = [int(v) for v, t in acts.items() if t <= m["createdAt"]]
                version = max(live) if live else None
                row = {"id": m["matchId"], "group": m["groupId"], "time": m["finishedAt"], "v": version,
                       "opp": op["name"], "opp_rating": round(rating.get(op["teamId"], 0)),
                       "our_rating_after": round(rating.get(ME, 0)), "map": m["map"], "side": me["side"],
                       "res": me["result"], "us": gems[us_team], "them": gems[them_team],
                       "rounds": st["match"]["roundsCompleted"], "end": m["endReason"],
                       "udraft": [CHAMPS[int(x)] for x in me["draftPicks"]],
                       "odraft": [CHAMPS[int(x)] for x in op["draftPicks"]]}
                f.write(json.dumps(row) + "\n")
                seen.add(m["matchId"])
                print(f"+ {row['time'][:16]} v{version} {row['res']:4s} {row['us']:5}-{row['them']:<5} "
                      f"{row['map']:22s} vs {row['opp'][:20]} ({row['opp_rating']})  {path}")
    sys.stdout.flush()
    subprocess.run([sys.executable, os.path.join(ROOT, "tools", "ladder_log.py")])


if __name__ == "__main__":
    main()
