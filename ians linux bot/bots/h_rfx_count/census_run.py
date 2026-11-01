"""Q21 trigger census: h_rfx_count (tb_merge_b + counters) vs tb_merge_b on every map, both sides,
with bot stdout kept; sums the final Q21C counters of the counting team per game."""
import json, os, subprocess, sys, zipfile, collections
ROOT = os.getcwd()
out = os.path.join(ROOT, "matches", "q21-count")
rel = os.path.relpath(ROOT, os.path.realpath(out))
assert not any(c.isspace() for c in rel), rel
maps = sorted(f[:-7] for f in os.listdir(os.path.join(ROOT, "maps")) if f.endswith(".map26a"))
rows, games = [], []
for m in maps:
    for a, b, side in (("h_rfx_count", "tb_merge_b", "A"), ("tb_merge_b", "h_rfx_count", "B")):
        name = f"{m}__{side}"
        rows.append(f"{rel}/bots/{a} {rel}/bots/{b} {rel}/maps/{m}.map26a {name}.repl26a --statistics {name}.json")
        games.append((m, side, name))
open(os.path.join(out, "manifest.txt"), "w").write("\n".join(rows) + "\n")
cambc = os.path.join(ROOT, "cli", "cambc")
p = subprocess.run([cambc, "run-batch", os.path.join(out, "manifest.txt"), "--jobs", sys.argv[1] if len(sys.argv) > 1 else "16",
                    "--json", "--color", "never"], cwd=ROOT, capture_output=True, text=True)
if p.returncode:
    print(p.stdout[-2000:], p.stderr[-2000:])
res = {}
tot = [0] * 5
for m, side, name in games:
    z = os.path.join(out, name + ".repl26a")
    if not os.path.exists(z):
        print("missing", name); continue
    t = "team-a.stdout" if side == "A" else "team-b.stdout"
    try:
        txt = zipfile.ZipFile(z).read(t).decode(errors="replace").replace("\x00", "")
    except Exception as e:
        print("bad", name, e); continue
    last = {}
    for line in txt.splitlines():
        f = line.split()
        if f and f[0] == "Q21C":
            last[int(f[2])] = [int(x) for x in f[3:8]]
    s = [sum(v[i] for v in last.values()) for i in range(5)]
    res[name] = s
    for i in range(5):
        tot[i] += s[i]
    os.remove(z)  # keep only the stats json + summary
json.dump(res, open(os.path.join(out, "summary.json"), "w"), indent=1)
for name, s in sorted(res.items(), key=lambda kv: -kv[1][0]):
    if s[0] or s[2]:
        print(f"{name:34s} rule_nonresp {s[0]:6d} rule_resp {s[1]:5d} unseen_fresh {s[2]:6d} unseen_stale {s[3]:5d}")
aff0 = sum(1 for s in res.values() if s[0] > 0)
aff2 = sum(1 for s in res.values() if s[2] > 0)
print(f"Q21 CENSUS over {len(res)} games: respawn-rule firings on NON-respawning tiles {tot[0]} ({aff0} games), "
      f"on respawning tiles {tot[1]}; unseen-alive guess with fresh Alive state {tot[2]} ({aff2} games), stale {tot[3]}")
