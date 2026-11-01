#!/usr/bin/env python3
"""Low-HP freeze detector (STRATEGIES V3L-2, results/experiments/2026-11-01-h_shortcut.md).

Lists frozen stretches (tools/freeze_metric.py's definition: alive and no activity counter changes)
that START with the champion at low HP, the signature of the 01shortcut stuck champion (a low-HP
champion that can't walk home idles off-spawn with no regeneration).
HP deficit = cumulative (monster + champion damage taken - healing received - shielding done) since
the last death. Spawn healing counts in healingReceived (checked on a traced game); the self-shield
term keeps Heart of Ruin from over-counting. "low" = deficit >= FRAC x the champion's BASE HP.
Health shards raise max HP, so the bot may not consider itself low (false positives: confirm with a
trace, e.g. 00great-wall A Ryth, 00the-line B Vendetta, 01broken-curve B Vesper were not 'low').
Usage: python3 -I tools/lowhp_freeze.py [--min N] [--frac F] <dir or files>...
'us' = the eval's first bot (teamA in <map>__A.json, teamB in <map>__B.json)."""
import glob, json, os, sys
BASE = {"Vesper Vale": 1000, "Vendetta": 1000, "Marcella": 1200, "Heart of Ruin": 1000, "Ryth": 1200,
        "Tavi": 900, "Varg": 1000, "Ren": 900, "Willow": 700, "Stellar": 650, "Prism": 700, "Cassi": 600, "Issac": 900}
ACT = ("monsterDamageDone", "monsterDamageTaken", "championDamageDone", "championDamageTaken", "healingDone",
       "healingReceived", "shieldingDone", "collectedGems", "submittedGems", "earnedGold", "spentGold", "kills",
       "assists", "deaths")
args = sys.argv[1:]
mn, frac = 150, 0.5
while args and args[0].startswith("--"):
    if args[0] == "--min": mn = int(args[1])
    if args[0] == "--frac": frac = float(args[1])
    args = args[2:]
files = []
for p in args:
    files += sorted(glob.glob(os.path.join(p, "*__*.json"))) if os.path.isdir(p) else [p]
def expand(runs, n):
    out = []
    for r in runs: out.extend([r["value"]] * r["duration"])
    return (out + [out[-1] if out else "0"] * n)[:n]
tot = {"us": 0, "them": 0}; ng = {"us": set(), "them": set()}
for f in files:
    d = json.load(open(f)); base = os.path.basename(f)[:-5]
    side = base.rsplit("__", 1)[-1]; us = "teamA" if side == "A" else "teamB"
    n = d["championTimelines"][0]["sampleCount"]
    ser, names = {}, {}
    for t in d["championTimelines"]:
        o = t["owner"]; names[o["id"]] = (o["team"], o["name"])
        ser.setdefault(o["id"], {})[t["metric"]] = [float(x) for x in expand(t["runs"], n)]
    for cid, m in ser.items():
        team, name = names[cid]; k = "us" if team == us else "them"
        z = [0.0] * n
        cum = [m.get("monsterDamageTaken", z)[r] + m.get("championDamageTaken", z)[r] - m.get("healingReceived", z)[r] - m.get("shieldingDone", z)[r] for r in range(n)]
        dv = m.get("deaths", z); dead = [False] * n; basel = [0.0] * n; b = 0.0
        for r in range(n):
            if r and dv[r] != dv[r - 1]:
                b = cum[r]
                for j in range(r, min(n, r + 61)): dead[j] = True
            basel[r] = b
        run = None
        for r in range(1, n):
            act = dead[r] or any(m[a][r] != m[a][r - 1] for a in ACT if a in m)
            if not act and run is None: run = r
            if (act or r == n - 1) and run is not None:
                end = r if act else r + 1
                if end - run >= mn:
                    deficit = cum[run] - basel[run]
                    bh = BASE.get(name, 1000)
                    if deficit >= frac * bh:
                        tot[k] += end - run; ng[k].add(base)
                        print("%-28s %-4s %-14s idle r%d-%d (%d) hp_deficit %d/%d gems %d%s" % (base, k, name, run, end, end - run, deficit, bh, m.get("gems", z)[run], "  <- to end" if end >= n - 1 else ""))
                run = None
print("LOWHP-FREEZE (>= %d rounds, deficit >= %.0f%% base HP) over %d games: us %d champ-rounds in %d games, them %d in %d games"
      % (mn, 100 * frac, len(files), tot["us"], len(ng["us"]), tot["them"], len(ng["them"])))
