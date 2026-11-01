#!/usr/bin/env python3
"""Scout: one consistent profile per ladder game, for BOTH teams, so analysts compare games on the same footing.

Usage:
    python3.12 -I tools/scout.py matches/ladder/summary/<id>__<OUR side>.json [more ...]
    python3.12 -I tools/scout.py --group <groupId>            # the 5 games of a ladder set (results/ladder-games.jsonl)
    python3.12 -I tools/scout.py --group <groupId> --json     # machine-readable (one object: {"games": [...], "set": {...}})
    python3.12 -I tools/scout.py ... --sections diff,fights   # only some sections (see SECTIONS)

"Us" is the team named by the file suffix (__A.json = teamA, __B.json = teamB), as written by tools/ladder_pull.py;
override with --us teamA|teamB. Works on local eval stats too (matches/<tag>/<map>__A.json).

Map geometry comes from maps/<map>.map26a, found by sha256 (= the stats file's match.mapHash), else by name.
Decoded and checked against all 230 ladder stats files: 4 terrain bitboards (bushes, walls, holes, altars) in
8x8 blocks, team A's spawn rectangle, and the stored half of the camps (the engine adds their symmetric images).
Camp-group ids are numbered the engine's way (each stored camp's group, then its mirror's), and they
matched all 26,323 capture positions. Distances are BFS steps (walls blocked; holes count as passable, since
dashes cross them), measured from each team's spawn tiles.

Definitions (fixed, so every game is measured the same way):
- phases: early <r300, mid r300-1000, late >r1000. "/100r" rates divide by the rounds actually played in the phase.
- gem race: tributed gems (teamTimelines submittedGems) at r250/r500/r1000/end; windows 0-250-500-750-1000-1500-end.
- gem pipeline per team: captured (camp gemCollection) + stolen (gemCollection from kills) - lost on death
  - carried at end = tributed. This identity holds exactly in every ladder file.
- side margin: a tile set is on A's (B's) side if it is nearer to that spawn by >= max(3, 10% of dA+dB) BFS
  steps, otherwise "mid". It is used for camp groups and altars (nearest tile), and for own/enemy half.
- location zones (relative to the acting team; for a death, the victim's team): "enemy spawn"/"own spawn" if
  within 6 steps of that spawn; "altar" if Chebyshev <= 3 of an altar; else own half / enemy half / mid
  (side margin). A kill's x,y is the victim's tile (it equals the death's x,y).
- counts: a Cassi & Issac death is 2 deaths but 1 kill (linked fate). Shop events carry the quantity in
  "value"; summing them matches itemsBought for every champion.
- fights: champion-caused deaths (both teams) chained when <= 10 rounds after the previous death of the fight and
  within Chebyshev 12 of it. Multi-kill: one champion's kills chained <= 10 rounds apart. Fed: >= 6 kills, <= 1 death.
- quiet stretch: >= 100 rounds in which none of a champion's 17 timeline metrics changed, minus the 61 rounds
  after each death (dead time). Positions are not in the stats file, so quiet means "no gold, gems, damage,
  healing or kills". Possible causes are a stuck pathfinder, waiting or guarding, or a long walk on a big map.
- gold sources: earnedGold timeline increments in rounds where the champion made a kill (kill), tributed
  (tribute; Marcella +2/gem), or anything else (camps).
- locks/crystals "used" = bought - held at end. The stats file has no consumable-use event.
"""
import argparse
import collections
import hashlib
import json
import os
import statistics
import struct
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
LADDER = os.path.join(ROOT, "results", "ladder-games.jsonl")
SUMMARY_DIR = os.path.join(ROOT, "matches", "ladder", "summary")
MAPS_DIR = os.path.join(ROOT, "maps")

PHASES = ((0, 300, "<300"), (300, 1000, "300-1000"), (1000, 10 ** 6, ">1000"))
RACE_CP = (250, 500, 1000)
WINDOWS = (0, 250, 500, 750, 1000, 1500, 10 ** 6)
GOLD_CP = (250, 500, 1000)
EMBLEM_CP = (500, 1000)
SPAWN_NEAR = 6
ALTAR_NEAR = 3
FIGHT_GAP = 10
FIGHT_DIST = 12
QUIET_MIN = 100
DEAD_ROUNDS = 61
SECTIONS = ("meta", "draft", "build", "economy", "farming", "tributes", "fights", "control", "fuel", "idle", "diff")

CAMP_NAME = {0: "Wolf", 1: "Elk", 2: "GemCl", 3: "GoldCl", 4: "Monolith", 5: "Golem"}
CAMP_GEMS = {0: 4, 1: 15, 2: 7, 3: 0, 4: 200, 5: 36}
CAMP_GOLD = {0: 40, 1: 90, 2: 0, 3: 20, 4: 300, 5: 160}
CONSUMABLE_ABBR = {"Altar Lock": "Lock", "Teleport Crystal": "TP"}


# ----------------------------------------------------------------------------------------------- map file
def _bitboard(b, off, bw, bh):
    """Run-length bitboard over 8x8 blocks (blocks row-major, bit = (y%8)*8 + x%8), u16 runs off/on/off..."""
    area, tot, on, cells = bw * bh * 64, 0, False, set()
    while tot < area:
        v = struct.unpack_from("<H", b, off)[0]
        off += 2
        if on:
            for i in range(tot, tot + v):
                blk, bit = divmod(i, 64)
                cells.add(((blk % bw) * 8 + bit % 8, (blk // bw) * 8 + bit // 8))
        tot += v
        on = not on
    return cells, off


_MAP_CACHE = {}


def load_map(path):
    if path not in _MAP_CACHE:
        _MAP_CACHE[path] = _load_map(path)
    return _MAP_CACHE[path]


def _load_map(path):
    b = open(path, "rb").read()
    sym, picks = b[0x48], b[0x49]
    w, h, nbush = struct.unpack_from("<HHH", b, 0x4A)
    bw, bh = (w + 7) // 8, (h + 7) // 8
    off, layers = 0x50, []
    for _ in range(4):  # bushes, walls, holes, altars
        cells, off = _bitboard(b, off, bw, bh)
        layers.append(cells)
    tot = 0  # bush-cluster id grid: (value u16, count u16) row-major runs
    while tot < w * h:
        tot += struct.unpack_from("<HH", b, off)[1]
        off += 4
    for _ in range(nbush):  # per-cluster bitboards
        _, off = _bitboard(b, off, bw, bh)
    x0, y0, x1, y1 = struct.unpack_from("<HHHH", b, off)
    off += 8
    n = b[off]
    off += 1
    stored = [tuple(b[off + 3 * i: off + 3 * i + 3]) for i in range(n)]  # (camp type, x, y)

    def mirror(p):
        if sym == 0:
            return (w - 1 - p[0], p[1])
        if sym == 1:
            return (p[0], h - 1 - p[1])
        return (w - 1 - p[0], h - 1 - p[1])

    spawn = {"teamA": {(x, y) for x in range(x0, x1) for y in range(y0, y1)}}
    spawn["teamB"] = {mirror(p) for p in spawn["teamA"]}
    camps = {}
    for t, x, y in stored:
        camps[(x, y)] = t
        camps.setdefault(mirror((x, y)), t)
    comp, members = {}, []
    for p in camps:
        if p in comp:
            continue
        comp[p] = len(members)
        stack, ms = [p], []
        while stack:
            q = stack.pop()
            ms.append(q)
            for dx, dy in ((1, 0), (-1, 0), (0, 1), (0, -1)):
                r = (q[0] + dx, q[1] + dy)
                if r in camps and r not in comp:
                    comp[r] = comp[p]
                    stack.append(r)
        members.append(ms)
    order = []
    for _, x, y in stored:
        for p in ((x, y), mirror((x, y))):
            if comp[p] not in order:
                order.append(comp[p])
    groups = []
    for c in order:
        tiles = sorted(members[c])
        types = collections.Counter(camps[t] for t in tiles)
        groups.append({"tiles": tiles, "types": types,
                       "gems": sum(CAMP_GEMS[t] * k for t, k in types.items()),
                       "gold": sum(CAMP_GOLD[t] * k for t, k in types.items()),
                       "center": (round(sum(t[0] for t in tiles) / len(tiles)), round(sum(t[1] for t in tiles) / len(tiles))),
                       "label": "+".join(f"{CAMP_NAME[t]}{'x%d' % k if k > 1 else ''}" for t, k in sorted(types.items()))})
    m = {"w": w, "h": h, "sym": ("horizontal", "vertical", "rot180")[sym] if sym < 3 else str(sym), "picks": picks,
         "bushes": layers[0], "walls": layers[1], "holes": layers[2], "altars": sorted(layers[3]),
         "spawn": spawn, "groups": groups}
    m["dist"] = {t: _bfs(m, spawn[t]) for t in ("teamA", "teamB")}
    blocked = m["walls"] | set(m["altars"])
    m["dist"]["altar"] = _bfs(m, {(a[0] + dx, a[1] + dy) for a in m["altars"] for dx in (-1, 0, 1) for dy in (-1, 0, 1)
                                  if (a[0] + dx, a[1] + dy) not in blocked and 0 <= a[0] + dx < w and 0 <= a[1] + dy < h})
    return m


def _bfs(m, sources):
    w, h = m["w"], m["h"]
    blocked = m["walls"] | set(m["altars"])
    dist = {s: 0 for s in sources}
    frontier = list(sources)
    while frontier:
        nxt = []
        for x, y in frontier:
            d = dist[(x, y)] + 1
            for dx in (-1, 0, 1):
                for dy in (-1, 0, 1):
                    p = (x + dx, y + dy)
                    if p in dist or not (0 <= p[0] < w and 0 <= p[1] < h) or p in blocked:
                        continue
                    dist[p] = d
                    nxt.append(p)
        frontier = nxt
    return dist


def find_map(stats, name_hint):
    want = stats["match"].get("mapHash")
    cands = []
    if name_hint:
        cands.append(os.path.join(MAPS_DIR, name_hint.replace("_", "-") + ".map26a"))
    if os.path.isdir(MAPS_DIR):
        cands += [os.path.join(MAPS_DIR, f) for f in sorted(os.listdir(MAPS_DIR)) if f.endswith(".map26a")]
    by_name = None
    for p in cands:
        if not os.path.exists(p):
            continue
        if want and hashlib.sha256(open(p, "rb").read()).hexdigest() == want:
            return p, True
        if by_name is None and name_hint and os.path.basename(p) == name_hint.replace("_", "-") + ".map26a":
            by_name = p
    return by_name, False


# ----------------------------------------------------------------------------------------------- helpers
def value_at(runs, rnd):
    """Value of a run-length timeline after round rnd (sample i = after round i), as in analyze_match.py."""
    t, last = 0, 0.0
    for r in runs:
        if t + r["duration"] > rnd:
            return float(r["value"])
        t += r["duration"]
        last = float(r["value"])
    return last


def change_rounds(runs):
    out, t = [], 0
    for i, r in enumerate(runs):
        if i:
            out.append(t)
        t += r["duration"]
    return out


def cheb(a, b):
    return max(abs(a[0] - b[0]), abs(a[1] - b[1]))


def phase_of(r):
    for i, (lo, hi, _) in enumerate(PHASES):
        if lo <= r < hi:
            return i
    return len(PHASES) - 1


def phase_len(i, rounds):
    lo, hi, _ = PHASES[i]
    return max(0, min(hi, rounds + 1) - lo)


def per100(n, rounds):
    return round(100.0 * n / rounds, 2) if rounds > 0 else None


def mean(xs):
    return round(statistics.mean(xs), 1) if xs else None


def median(xs):
    return round(statistics.median(xs), 1) if xs else None


def item_abbr(name):
    if name in CONSUMABLE_ABBR:
        return CONSUMABLE_ABBR[name]
    parts = name.split()
    if len(parts) >= 4 and parts[1] in ("Shard", "Emblem"):
        return parts[0][:3] + parts[-1][0]
    return name


def family_stat(name):
    """'Bruiser Emblem of Strength' -> 'Bruiser:Str'."""
    parts = name.split()
    return f"{parts[0]}:{parts[-1][:3]}" if len(parts) >= 4 else name


def fmt_counter(c):
    return ", ".join(f"{k} {v}" for k, v in sorted(c.items(), key=lambda kv: (-kv[1], kv[0]))) or "-"


def nz(v, dash="-"):
    return dash if v is None else v


def side_margin(da, db):
    return max(3, round(0.1 * (da + db)))


def fmt_multi(mk):
    return "; ".join(f"{n} {'+'.join(map(str, v))}" for n, v in mk.items())


def other(team):
    return "teamB" if team == "teamA" else "teamA"


# ----------------------------------------------------------------------------------------------- ladder rows
_ROWS = None


def ladder_rows():
    global _ROWS
    if _ROWS is None:
        _ROWS = []
        if os.path.exists(LADDER):
            for line in open(LADDER):
                line = line.strip()
                if line:
                    try:
                        _ROWS.append(json.loads(line))
                    except ValueError:
                        pass
    return _ROWS


def row_for(match_id):
    for r in ladder_rows():
        if r.get("id") == match_id:
            return r
    return None


# ----------------------------------------------------------------------------------------------- game model
class Game:
    def __init__(self, path, us_override=None):
        self.path = path
        base = os.path.basename(path)
        self.d = json.load(open(path))
        if us_override:
            self.us = us_override
        elif base.endswith("__B.json") or base.endswith("-b.json"):
            self.us = "teamB"
        else:
            self.us = "teamA"
        self.them = other(self.us)
        self.id = base.rsplit("__", 1)[0] if "__" in base else base.rsplit(".", 1)[0]
        self.row = row_for(self.id)
        m = self.d["match"]
        self.rounds = m["roundsCompleted"]
        self.outcome = m["outcome"]
        self.lab = {self.us: "us", self.them: "them"}
        hint = self.row["map"] if self.row else (self.id if os.path.exists(
            os.path.join(MAPS_DIR, self.id.replace("_", "-") + ".map26a")) else None)
        mp, exact = find_map(self.d, hint)
        self.map_name = (self.row or {}).get("map") or (os.path.basename(mp)[:-7] if mp else "?")
        self.map = load_map(mp) if mp else None
        self.map_exact = exact
        if self.map and (self.map["w"], self.map["h"]) != (m["width"], m["height"]):
            self.map = None
        # champions
        self.champs = {}
        for c in self.d["roster"]["champions"]:
            self.champs[c["id"]] = {"id": c["id"], "name": c["name"], "team": c["team"], "pick": c.get("draftPick", 0)}
        for c in self.d["champions"]:
            self.champs.setdefault(c["id"], {"id": c["id"], "name": c["name"], "team": c["team"], "pick": 99})
            self.champs[c["id"]]["final"] = c
        self.tl = collections.defaultdict(dict)
        for t in self.d["championTimelines"]:
            self.tl[t["owner"]["id"]][t["metric"]] = t["runs"]
        self.team_tl = {t["owner"]: t["runs"] for t in self.d["teamTimelines"] if t["metric"] == "submittedGems"}
        self.final_gems = {t["team"]: int(t["submittedGems"]) for t in self.d["teams"]}
        # events, flattened
        self.ev = collections.defaultdict(list)
        for e in self.d["events"]:
            own = e.get("owner") or {}
            for x in e["entries"]:
                ts = x.get("timestamp", {})
                self.ev[e["kind"]].append({
                    "r": ts.get("round", 0), "o": ts.get("ordinal", 0), "cid": own.get("id"), "team": own.get("team"),
                    "name": own.get("name"), "x": x.get("x"), "y": x.get("y"), "value": x.get("value"),
                    "ctx": x.get("context"), "target": x.get("target"), "amount": x.get("amount")})
        for k in self.ev:
            self.ev[k].sort(key=lambda e: (e["r"], e["o"]))

    def team_champs(self, team):
        return sorted((c for c in self.champs.values() if c["team"] == team), key=lambda c: (c["pick"], c["id"]))

    # ---- geometry
    def dists(self, p):
        if not self.map or p is None or p[0] is None:
            return None, None
        out = []
        for t in ("teamA", "teamB"):
            dd = self.map["dist"][t]
            if p in dd:
                out.append(dd[p])
            else:
                near = [dd[q] + 1 for q in ((p[0] + a, p[1] + b) for a in (-1, 0, 1) for b in (-1, 0, 1)) if q in dd]
                out.append(min(near) if near else min(cheb(p, s) for s in self.map["spawn"][t]))
        return out[0], out[1]

    def altar_dist(self, tiles):
        dd = self.map["dist"]["altar"]
        vals = [dd[t] + 1 for t in tiles if t in dd]
        return min(vals) if vals else min(cheb(t, a) for t in tiles for a in self.map["altars"]) if self.map["altars"] else None

    def zone(self, p, team):
        """Location class of tile p from team's point of view."""
        da, db = self.dists(p)
        if da is None:
            return "?"
        own, enemy = (da, db) if team == "teamA" else (db, da)
        if enemy <= SPAWN_NEAR:
            return "enemy spawn"
        if own <= SPAWN_NEAR:
            return "own spawn"
        if any(cheb(p, a) <= ALTAR_NEAR for a in self.map["altars"]):
            return "altar"
        if abs(own - enemy) < side_margin(own, enemy):
            return "mid"
        return "own half" if own < enemy else "enemy half"

    def side_of_tiles(self, tiles):
        """'A' / 'B' / 'mid' for a set of tiles (camp group, altar)."""
        da = min(self.dists(t)[0] for t in tiles)
        db = min(self.dists(t)[1] for t in tiles)
        mg = side_margin(da, db)
        return ("A" if db - da >= mg else "B" if da - db >= mg else "mid"), da, db

    @staticmethod
    def rel_side(side, team):
        if side == "mid":
            return "mid"
        return "own" if side == team[-1] else "enemy"


# ----------------------------------------------------------------------------------------------- sections
def sec_meta(g):
    r = g.row or {}
    us_g, th_g = g.final_gems.get(g.us, 0), g.final_gems.get(g.them, 0)
    end = r.get("end") or ("gems" if max(us_g, th_g) >= 1000 else "tiebreak")
    m = g.map
    meta = {"id": g.id, "group": r.get("group"), "time": r.get("time"), "version": r.get("v"), "opp": r.get("opp"),
            "opp_rating": r.get("opp_rating"), "map": g.map_name, "size": f"{g.d['match']['width']}x{g.d['match']['height']}",
            "us": g.us, "result": "win" if g.outcome == g.us else "loss", "winner": g.lab.get(g.outcome, g.outcome),
            "score_us": us_g, "score_them": th_g, "rounds": g.rounds, "end": end,
            "map_found": bool(m), "map_hash_match": g.map_exact,
            "faults": g.d.get("diagnostics", {}).get("botFaults", {})}
    if m:
        meta["symmetry"] = m["sym"]
        meta["picks"] = m["picks"]
        meta["spawn"] = {g.lab[t]: [min(x for x, _ in m["spawn"][t]), min(y for _, y in m["spawn"][t]),
                                    max(x for x, _ in m["spawn"][t]), max(y for _, y in m["spawn"][t])] for t in ("teamA", "teamB")}
        meta["altars"] = []
        for i, a in enumerate(m["altars"]):
            side, da, db = g.side_of_tiles([a])
            meta["altars"].append({"i": i, "pos": a, "side": side, "dA": da, "dB": db})
        meta["camp_groups"] = len(m["groups"])
    return meta


def sec_draft(g):
    out = {}
    for t in (g.us, g.them):
        out[g.lab[t]] = [c["champion"] for c in g.d["roster"]["draft"] if c["team"] == t]
    return out


def qty(e):
    """Shop events carry the quantity in "value" (one buyItem can be 10 shards; one itemCombination 2 emblems)."""
    try:
        return int(e["value"])
    except (TypeError, ValueError):
        return 1


def sec_build(g):
    out = {}
    for t in (g.us, g.them):
        team = {"champions": {}, "emblems": {}, "shards": {}}
        emb_ev = [e for e in g.ev["itemCombination"] if e["team"] == t]
        shard_ev = [e for e in g.ev["buyItem"] if e["team"] == t]
        for cp in EMBLEM_CP + (10 ** 6,):
            key = "end" if cp == 10 ** 6 else f"r{cp}"
            c = collections.Counter()
            for e in emb_ev:
                if e["r"] <= cp:
                    c[family_stat(e["target"]["name"])] += qty(e)
            team["emblems"][key] = dict(c)
            team["shards"][key] = sum(qty(e) for e in shard_ev if e["r"] <= cp)
        for c in g.team_champs(t):
            cid = c["id"]
            buys = []
            for kind, tag in (("buyItem", "shard"), ("buyConsumable", "cons"), ("itemCombination", "emblem"), ("sellItem", "sell")):
                for e in g.ev[kind]:
                    if e["cid"] == cid:
                        tgt = e["target"] if isinstance(e["target"], dict) else {}
                        buys.append({"r": e["r"], "o": e["o"], "kind": tag, "name": tgt.get("name", str(e["target"])),
                                     "n": qty(e), "gold": e.get("amount")})
            buys.sort(key=lambda b: (b["r"], b["o"]))
            visits = []
            for b in buys:
                if not visits or b["r"] - visits[-1]["r_last"] > 1:
                    visits.append({"r": b["r"], "r_last": b["r"], "items": collections.OrderedDict(), "emblems": []})
                v = visits[-1]
                v["r_last"] = b["r"]
                key = item_abbr(b["name"])
                if b["kind"] == "emblem":
                    v["emblems"] += [key] * b["n"]
                else:
                    key = ("sell:" + key) if b["kind"] == "sell" else key
                    v["items"][key] = v["items"].get(key, 0) + b["n"]
            fin = c.get("final", {})
            team["champions"][c["name"]] = {
                "purchases": [{k: b[k] for k in ("r", "kind", "name", "n", "gold")} for b in buys],
                "visits": [{"r": v["r"], "items": dict(v["items"]), "emblems": v["emblems"]} for v in visits],
                "first_buy": buys[0]["r"] if buys else None,
                "emblems_end": {family_stat(i["item"]): int(i["quantity"]) for i in fin.get("items", []) if "Emblem" in i["item"]},
                "emblems_by": {f"r{cp}": sum(qty(e) for e in emb_ev if e["cid"] == cid and e["r"] <= cp) for cp in EMBLEM_CP},
            }
        out[g.lab[t]] = team
    return out


def sec_economy(g):
    out = {}
    kills_r = collections.defaultdict(set)
    for e in g.ev["kill"]:
        kills_r[e["cid"]].add(e["r"])
    trib_r = collections.defaultdict(set)
    for e in g.ev["gemSubmission"]:
        trib_r[e["cid"]].add(e["r"])
    for t in (g.us, g.them):
        team = {"champions": {}, "team": {}}
        tot = collections.Counter()
        for c in g.team_champs(t):
            runs = g.tl[c["id"]].get("earnedGold", [])
            fin = c.get("final", {}).get("metrics", {})
            row = {f"r{cp}": int(value_at(runs, cp)) for cp in GOLD_CP}
            row["end"] = int(fin.get("earnedGold", value_at(runs, g.rounds)))
            row["spent"] = int(fin.get("spentGold", 0))
            row["unspent_end"] = int(fin.get("gold", 0))
            src = collections.Counter()
            tt, prev = 0, None
            for run in runs:
                v = int(float(run["value"]))
                if prev is not None and v > prev:
                    rr = tt
                    if rr in kills_r[c["id"]]:
                        src["kill"] += v - prev
                    elif rr in trib_r[c["id"]]:
                        src["tribute"] += v - prev
                    else:
                        src["camps"] += v - prev
                prev = v
                tt += run["duration"]
            row["sources"] = dict(src)
            team["champions"][c["name"]] = row
            for k in ("r250", "r500", "r1000", "end", "spent", "unspent_end"):
                tot[k] += row[k]
            for k, v in src.items():
                tot["src_" + k] += v
        team["team"] = dict(tot)
        out[g.lab[t]] = team
    return out


def captures(g, team):
    """Distinct (round, group) captures of a team, with gems and participating champions."""
    caps = collections.OrderedDict()
    for e in g.ev["gemCollection"]:
        if e["team"] != team or e["ctx"] != "campGroup":
            continue
        gid = (e["target"] or {}).get("id")
        k = (e["r"], gid)
        if k not in caps:
            caps[k] = {"r": e["r"], "gid": gid, "gems": 0, "who": [], "pos": (e["x"], e["y"])}
        caps[k]["gems"] += int(e["value"])
        caps[k]["who"].append(e["name"])
    return list(caps.values())


def sec_farming(g):
    out = {"groups": []}
    clears = {t: [e for e in g.ev["campClear"] if e["team"] == t] for t in (g.us, g.them)}
    caps = {t: captures(g, t) for t in (g.us, g.them)}
    gside = {}
    if g.map:
        for gid, grp in enumerate(g.map["groups"]):
            side, da, db = g.side_of_tiles(grp["tiles"])
            gside[gid] = side
    for t in (g.us, g.them):
        team = {"clears": len(clears[t]), "captures": len(caps[t]), "by_phase": [], "by_side": {}, "champions": {}}
        for i, (lo, hi, name) in enumerate(PHASES):
            pl = phase_len(i, g.rounds)
            if pl <= 0:
                continue
            ncl = sum(1 for e in clears[t] if phase_of(e["r"]) == i)
            ncap = [c for c in caps[t] if phase_of(c["r"]) == i]
            team["by_phase"].append({"phase": name, "rounds": pl, "clears": ncl, "clears_per100": per100(ncl, pl),
                                     "captures": len(ncap), "camp_gems": sum(c["gems"] for c in ncap),
                                     "camp_gems_per100": per100(sum(c["gems"] for c in ncap), pl)})
        if g.map:
            bs = collections.Counter()
            for e in clears[t]:
                bs["clear_" + g.rel_side(gside.get((e["target"] or {}).get("id"), "mid"), t)] += 1
            for c in caps[t]:
                s = g.rel_side(gside.get(c["gid"], "mid"), t)
                bs["cap_" + s] += 1
                bs["capgems_" + s] += c["gems"]
                if c["gid"] is not None and c["gid"] < len(g.map["groups"]):
                    bs["capgold_" + s] += g.map["groups"][c["gid"]]["gold"]
            team["by_side"] = dict(bs)
        # captures of groups whose last clear was by the enemy (a capture steal)
        last_clear = {}
        steals = 0
        for e in sorted(clears[g.us] + clears[g.them], key=lambda e: (e["r"], e["o"])):
            last_clear.setdefault((e["target"] or {}).get("id"), []).append((e["r"], e["team"]))
        for c in caps[t]:
            prior = [tm for r, tm in last_clear.get(c["gid"], []) if r <= c["r"]]
            if prior and prior[-1] != t:
                steals += 1
        team["capture_steals"] = steals
        for c in g.team_champs(t):
            fm = c.get("final", {}).get("metrics", {})
            camp_g = sum(int(e["value"]) for e in g.ev["gemCollection"] if e["cid"] == c["id"] and e["ctx"] == "campGroup")
            kill_g = sum(int(e["value"]) for e in g.ev["gemCollection"] if e["cid"] == c["id"] and e["ctx"] != "campGroup")
            lost = sum(int(e["value"]) for e in g.ev["gemLoss"] if e["cid"] == c["id"])
            team["champions"][c["name"]] = {
                "clears": sum(1 for e in clears[t] if e["cid"] == c["id"]),
                "capture_shares": sum(1 for e in g.ev["gemCollection"] if e["cid"] == c["id"] and e["ctx"] == "campGroup"),
                "collected": int(fm.get("collectedGems", 0)), "from_camps": camp_g, "from_kills": kill_g,
                "submitted": int(fm.get("submittedGems", 0)), "lost": lost, "carried_end": int(fm.get("gems", 0)),
                "monster_dmg": round(float(fm.get("monsterDamageDone", 0))), "monster_taken": round(float(fm.get("monsterDamageTaken", 0)))}
        out[g.lab[t]] = team
    if g.map:
        for gid, grp in enumerate(g.map["groups"]):
            side, da, db = g.side_of_tiles(grp["tiles"])
            row = {"gid": gid, "label": grp["label"], "gems": grp["gems"], "gold": grp["gold"], "center": grp["center"],
                   "dA": da, "dB": db, "dAltar": g.altar_dist(grp["tiles"]), "side": side}
            for t in (g.us, g.them):
                row[g.lab[t] + "_clears"] = sum(1 for e in clears[t] if (e["target"] or {}).get("id") == gid)
                row[g.lab[t] + "_caps"] = sum(1 for c in caps[t] if c["gid"] == gid)
                row[g.lab[t] + "_first"] = min((c["r"] for c in caps[t] if c["gid"] == gid), default=None)
            out["groups"].append(row)
    return out


def sec_tributes(g):
    out = {}
    for t in (g.us, g.them):
        tr = [e for e in g.ev["gemSubmission"] if e["team"] == t]
        sizes = [int(e["value"]) for e in tr]
        rounds = [e["r"] for e in tr]
        gaps = [b - a for a, b in zip(rounds, rounds[1:])]
        losses = [e for e in g.ev["gemLoss"] if e["team"] == t]
        team = {"count": len(tr), "total": sum(sizes), "mean": mean(sizes), "median": median(sizes),
                "max": max(sizes) if sizes else 0, "big30": sum(1 for s in sizes if s >= 30),
                "first": rounds[0] if rounds else None, "gap_median": median(gaps), "gap_mean": mean(gaps),
                "by_phase": [{"phase": n, "count": sum(1 for e in tr if phase_of(e["r"]) == i),
                              "gems": sum(int(e["value"]) for e in tr if phase_of(e["r"]) == i)}
                             for i, (_, _, n) in enumerate(PHASES) if phase_len(i, g.rounds) > 0],
                "lost_to_champs": sum(int(e["value"]) for e in losses if e["ctx"] != "camp"),
                "lost_to_camps": sum(int(e["value"]) for e in losses if e["ctx"] == "camp"),
                "deaths_with_gems": sum(1 for e in losses if int(e["value"]) > 0),
                "carried_end": sum(int(c.get("final", {}).get("metrics", {}).get("gems", 0)) for c in g.team_champs(t)),
                "champions": {}, "altars": {}}
        for c in g.team_champs(t):
            s = [int(e["value"]) for e in tr if e["cid"] == c["id"]]
            team["champions"][c["name"]] = {"count": len(s), "gems": sum(s), "mean": mean(s)}
        if g.map:
            for e in tr:
                p = (e["x"], e["y"])
                i = g.map["altars"].index(p) if p in g.map["altars"] else -1
                a = team["altars"].setdefault(str(i), {"pos": p, "count": 0, "gems": 0})
                a["count"] += 1
                a["gems"] += int(e["value"])
            for k, a in team["altars"].items():
                if k != "-1":
                    a["side"] = g.rel_side(g.side_of_tiles([a["pos"]])[0], t)
        out[g.lab[t]] = team
    return out


def fights_ledger(g):
    deaths = [e for e in g.ev["death"] if e["ctx"] != "camp"]
    fights = []
    for e in deaths:
        p = (e["x"], e["y"])
        f = fights[-1] if fights else None
        if f and e["r"] - f["r_last"] <= FIGHT_GAP and cheb(p, f["last_pos"]) <= FIGHT_DIST:
            pass
        else:
            f = {"r_first": e["r"], "r_last": e["r"], "deaths": [], "last_pos": p}
            fights.append(f)
        f["r_last"] = e["r"]
        f["last_pos"] = p
        killer = e["target"] if isinstance(e["target"], dict) else {}
        f["deaths"].append({"r": e["r"], "victim": e["name"], "team": e["team"], "killer": killer.get("name"),
                            "pos": p})
    loss = {(e["cid"], e["r"]): int(e["value"]) for e in g.ev["gemLoss"]}
    vid = {(e["name"], e["team"], e["r"]): e["cid"] for e in deaths}
    out = []
    for f in fights:
        if len(f["deaths"]) < 2:
            continue
        xs = [d["pos"] for d in f["deaths"]]
        c = (round(sum(p[0] for p in xs) / len(xs)), round(sum(p[1] for p in xs) / len(xs)))
        row = {"r": f["r_first"], "r_end": f["r_last"], "pos": c, "zone_us": g.zone(c, g.us)}
        for t in (g.us, g.them):
            ds = [d for d in f["deaths"] if d["team"] == t]
            row[g.lab[t] + "_lost"] = [f"{d['victim']}<-{d['killer']}" for d in ds]
            row[g.lab[t] + "_gems_dropped"] = sum(loss.get((vid[(d["victim"], t, d["r"])], d["r"]), 0) for d in ds)
        nu, nt = len(row["us_lost"]), len(row["them_lost"])
        row["won_by"] = "us" if nt > nu else "them" if nu > nt else "even"
        out.append(row)
    return out


def sec_fights(g):
    out = {}
    for t in (g.us, g.them):
        team = {"champions": {}, "death_zones": collections.Counter(), "kill_zones": collections.Counter(),
                "killed_by": collections.Counter(), "camp_deaths": 0, "fed": [], "multikills": {}}
        for c in g.team_champs(t):
            cid = c["id"]
            row = {}
            for kind in ("kill", "death", "assist"):
                evs = [e for e in g.ev[kind] if e["cid"] == cid]
                row[kind + "s"] = len(evs)
                row[kind + "s_by_phase"] = [sum(1 for e in evs if phase_of(e["r"]) == i)
                                            for i in range(len(PHASES)) if phase_len(i, g.rounds) > 0]
            row["camp_deaths"] = sum(1 for e in g.ev["death"] if e["cid"] == cid and e["ctx"] == "camp")
            fm = c.get("final", {}).get("metrics", {})
            row["champ_dmg"] = round(float(fm.get("championDamageDone", 0)))
            row["champ_taken"] = round(float(fm.get("championDamageTaken", 0)))
            row["healing"] = round(float(fm.get("healingDone", 0)))
            row["shielding"] = round(float(fm.get("shieldingDone", 0)))
            kr = [e["r"] for e in g.ev["kill"] if e["cid"] == cid]
            streaks, cur = [], 1
            for a, b in zip(kr, kr[1:]):
                if b - a <= FIGHT_GAP:
                    cur += 1
                else:
                    if cur >= 2:
                        streaks.append(cur)
                    cur = 1
            if cur >= 2:
                streaks.append(cur)
            if streaks:
                team["multikills"][c["name"]] = streaks
            if row["kills"] >= 6 and row["deaths"] <= 1:
                team["fed"].append(f"{c['name']} {row['kills']}/{row['deaths']}")
            team["champions"][c["name"]] = row
        for e in g.ev["death"]:
            if e["team"] != t:
                continue
            if e["ctx"] == "camp":
                team["camp_deaths"] += 1
                team["killed_by"]["camp"] += 1
                team["death_zones"][g.zone((e["x"], e["y"]), t) + " (camp)"] += 1
            else:
                team["killed_by"][(e["target"] or {}).get("name", "?") if isinstance(e["target"], dict) else "?"] += 1
                team["death_zones"][g.zone((e["x"], e["y"]), t)] += 1
        for e in g.ev["kill"]:
            if e["team"] == t:
                team["kill_zones"][g.zone((e["x"], e["y"]), t)] += 1
        for k in ("death_zones", "kill_zones", "killed_by"):
            team[k] = dict(team[k])
        out[g.lab[t]] = team
    out["ledger"] = fights_ledger(g)
    return out


def sec_control(g):
    out = {}
    for t in (g.us, g.them):
        wards = [e for e in g.ev["wardPlacement"] if e["team"] == t]
        team = {"wards": len(wards), "ward_zones": dict(collections.Counter(g.zone((e["x"], e["y"]), t) for e in wards)),
                "wards_in_bush": sum(1 for e in wards if g.map and (e["x"], e["y"]) in g.map["bushes"]),
                "wards_after_r10": sum(1 for e in wards if e["r"] > 10), "champions": {}}
        for k, name in (("locks", "Altar Lock"), ("crystals", "Teleport Crystal")):
            bought = held = 0
            first = None
            for c in g.team_champs(t):
                fin = c.get("final", {})
                bought += sum(int(x["quantity"]) for x in fin.get("consumablesBought", []) if x["consumable"] == name)
                held += sum(int(x["quantity"]) for x in fin.get("consumables", []) if x["consumable"] == name)
            for e in g.ev["buyConsumable"]:
                if e["team"] == t and (e["target"] or {}).get("name") == name:
                    first = e["r"] if first is None else min(first, e["r"])
            team[k] = {"bought": bought, "held_end": held, "used_est": bought - held, "first_buy": first}
        for c in g.team_champs(t):
            team["champions"][c["name"]] = sum(1 for e in wards if e["cid"] == c["id"])
        out[g.lab[t]] = team
    return out


def sec_fuel(g):
    out = {}
    for t in (g.us, g.them):
        evs = [e for e in g.ev["fuelExhausted"] if e["team"] == t]
        out[g.lab[t]] = {"total": len(evs), "after_r1": sum(1 for e in evs if e["r"] > 1),
                         "champions": {c["name"]: [e["r"] for e in evs if e["cid"] == c["id"]][:8] for c in g.team_champs(t)
                                       if any(e["cid"] == c["id"] for e in evs)},
                         "faults": g.d.get("diagnostics", {}).get("botFaults", {}).get(t, 0),
                         "resigned": any(e["team"] == t for e in g.ev["resignation"])}
    return out


def sec_idle(g):
    out = {}
    end = g.rounds
    for t in (g.us, g.them):
        team = {"champions": {}, "quiet_rounds": 0}
        for c in g.team_champs(t):
            ch = set()
            for runs in g.tl[c["id"]].values():
                ch.update(change_rounds(runs))
            deaths = [e["r"] for e in g.ev["death"] if e["cid"] == c["id"]]
            ch.update(deaths)
            pts = sorted(r for r in ch if r <= end)
            pts = [0] + pts + [end]
            stretches = []
            for a, b in zip(pts, pts[1:]):
                if b - a < QUIET_MIN:
                    continue
                dead = sum(max(0, min(b, d + DEAD_ROUNDS) - max(a, d)) for d in deaths)
                q = b - a - dead
                if q >= QUIET_MIN:
                    stretches.append({"from": a, "to": b, "quiet": q})
            tot = sum(s["quiet"] for s in stretches)
            longest = max(stretches, key=lambda s: s["quiet"]) if stretches else None
            team["champions"][c["name"]] = {"quiet_rounds": tot, "stretches": len(stretches), "longest": longest}
            team["quiet_rounds"] += tot
        out[g.lab[t]] = team
    return out


def gold_at(g, c, r):
    if r >= g.rounds:
        return float(c.get("final", {}).get("metrics", {}).get("earnedGold", value_at(g.tl[c["id"]].get("earnedGold", []), r)))
    return value_at(g.tl[c["id"]].get("earnedGold", []), r)


def phase_pipeline(g, t):
    rows = []
    for i, (lo, hi, name) in enumerate(PHASES):
        if phase_len(i, g.rounds) <= 0:
            continue
        inph = lambda e: e["team"] == t and phase_of(e["r"]) == i  # noqa: E731
        rows.append({
            "phase": name,
            "camp_gems": sum(int(e["value"]) for e in g.ev["gemCollection"] if inph(e) and e["ctx"] == "campGroup"),
            "kill_gems": sum(int(e["value"]) for e in g.ev["gemCollection"] if inph(e) and e["ctx"] != "campGroup"),
            "lost_gems": sum(int(e["value"]) for e in g.ev["gemLoss"] if inph(e)),
            "tributed": sum(int(e["value"]) for e in g.ev["gemSubmission"] if inph(e)),
            "clears": sum(1 for e in g.ev["campClear"] if inph(e)),
            "kills": sum(1 for e in g.ev["kill"] if inph(e)),
            "deaths": sum(1 for e in g.ev["death"] if inph(e)),
            "gold": int(sum(gold_at(g, c, min(hi - 1, g.rounds)) - gold_at(g, c, lo - 1) for c in g.team_champs(t))),
        })
    return rows


def sec_diff(g, prof):
    us_r, th_r = g.team_tl.get(g.us, []), g.team_tl.get(g.them, [])
    win = g.lab.get(g.outcome, "?")
    race = {}
    for cp in RACE_CP:
        if cp <= g.rounds:
            race[f"r{cp}"] = [int(value_at(us_r, cp)), int(value_at(th_r, cp))]
    race["end"] = [g.final_gems.get(g.us, 0), g.final_gems.get(g.them, 0)]
    windows = []
    for lo, hi in zip(WINDOWS, WINDOWS[1:]):
        if lo > g.rounds:
            break
        h = min(hi, g.rounds)
        gap = lambda r: value_at(us_r, r) - value_at(th_r, r)  # noqa: E731
        windows.append({"w": f"{lo}-{h if hi < 10 ** 6 else 'end'}", "gap_change": int(gap(h) - gap(lo))})
    # last round at which the eventual winner was not strictly ahead
    wr, lr = (us_r, th_r) if win == "us" else (th_r, us_r)
    ahead_from = None
    for r in range(g.rounds, -1, -1):
        if value_at(wr, r) <= value_at(lr, r):
            ahead_from = r + 1 if r < g.rounds else None
            break
    else:
        ahead_from = 0
    pipe = {"us": phase_pipeline(g, g.us), "them": phase_pipeline(g, g.them)}
    swing = None
    if windows:
        sign = 1 if win == "us" else -1
        swing = max(windows, key=lambda w: sign * w["gap_change"])
    # biggest source of the winner's edge per phase (winner minus loser; positive = helps the winner)
    edges = []
    for i, ph in enumerate(pipe["us"]):
        w_, l_ = (ph, pipe["them"][i]) if win == "us" else (pipe["them"][i], ph)
        src = {"camp gems": w_["camp_gems"] - l_["camp_gems"], "gems taken in kills": w_["kill_gems"] - l_["kill_gems"],
               "gems lost on death (loser lost more)": l_["lost_gems"] - w_["lost_gems"]}
        top = max(src.items(), key=lambda kv: kv[1])
        edges.append({"phase": ph["phase"], "tributed_gap": w_["tributed"] - l_["tributed"], "sources": src,
                      "top_source": top[0], "top_value": top[1]})
    if swing is not None and (1 if win == "us" else -1) * swing["gap_change"] <= 0:
        swing = None
    gold_race = {}
    for cp in RACE_CP + (g.rounds,):
        if cp <= g.rounds:
            gold_race["end" if cp == g.rounds else f"r{cp}"] = [
                int(sum(gold_at(g, c, cp) for c in g.team_champs(t))) for t in (g.us, g.them)]
    tie = race["end"][0] == race["end"][1]
    decided = "gems" if not tie else ("gold" if gold_race["end"][0] != gold_race["end"][1] else "kills/side")
    tempo = {}
    for t in (g.us, g.them):
        first = lambda kind, pred=lambda e: True: min((e["r"] for e in g.ev[kind] if e["team"] == t and pred(e)), default=None)  # noqa: E731
        tempo[g.lab[t]] = {"clear": first("campClear"), "capture": first("gemCollection", lambda e: e["ctx"] == "campGroup"),
                           "tribute": first("gemSubmission"), "kill": first("kill"), "death": first("death"),
                           "item": first("buyItem"), "emblem": first("itemCombination")}
    flags = diff_flags(g, prof, win)
    return {"winner": win, "decided_by": decided, "race": race, "gold_race": gold_race, "windows": windows,
            "winner_ahead_from": ahead_from, "widest_swing": swing, "pipeline": pipe, "edges": edges, "tempo": tempo,
            "style": {s: style(g, prof, s) for s in ("us", "them")}, "flags": flags}


def style(g, prof, side):
    """A fixed fingerprint of how a team played (numbers only; same fields for every game)."""
    fa, fi, tr, co, bu = (prof.get(k) for k in ("farming", "fights", "tributes", "control", "build"))
    rounds = max(1, g.rounds)
    kills = sum(c["kills"] for c in fi[side]["champions"].values())
    kz = fi[side]["kill_zones"]
    deep = kz.get("enemy half", 0) + kz.get("enemy spawn", 0)
    bs = fa[side].get("by_side", {})
    caps = sum(bs.get(f"cap_{k}", 0) for k in ("own", "mid", "enemy"))
    fam = collections.Counter()
    for k, v in bu[side]["emblems"].get("end", {}).items():
        fam[k.split(":")[0]] += v
    return {"clears_per100": per100(fa[side]["clears"], rounds), "kills_per100": per100(kills, rounds),
            "kills_in_enemy_half_pct": round(100 * deep / kills) if kills else None,
            "enemy_side_caps_pct": round(100 * bs.get("cap_enemy", 0) / caps) if caps else None,
            "tributes": tr[side]["count"], "tribute_mean": tr[side]["mean"],
            "emblem_families": dict(fam.most_common(3)), "locks_used": co[side]["locks"]["used_est"],
            "tp_bought": co[side]["crystals"]["bought"], "wards": co[side]["wards"]}


def diff_flags(g, prof, win):
    """Notable contrasts between the teams, worded neutrally (evidence, not causes)."""
    f = []
    tr, fa, fi, co, ec, bu, idl, fu = (prof.get(k) for k in ("tributes", "farming", "fights", "control", "economy",
                                                            "build", "idle", "fuel"))
    for side in ("us", "them"):
        o = "them" if side == "us" else "us"
        if tr:
            a, b = tr[side]["first"], tr[o]["first"]
            if a and b and b - a >= 50:
                f.append(f"{side} tributed first by {b - a} rounds (r{a} vs r{b})")
            if tr[side]["lost_to_champs"] + tr[side]["lost_to_camps"] >= 60:
                f.append(f"{side} lost {tr[side]['lost_to_champs']} gems to champions and {tr[side]['lost_to_camps']} to camps on death")
            if tr[side]["carried_end"] >= 40:
                f.append(f"{side} ended carrying {tr[side]['carried_end']} unbanked gems")
        if fa and "by_side" in fa[side]:
            bs = fa[side]["by_side"]
            if bs.get("cap_enemy", 0) >= 3:
                f.append(f"{side} captured {bs['cap_enemy']} camps on the enemy side ({bs.get('capgems_enemy', 0)} gems, "
                         f"{bs.get('capgold_enemy', 0)} base gold)")
            if fa[side]["capture_steals"] >= 3:
                f.append(f"{side} captured {fa[side]['capture_steals']} groups the other team had cleared")
        if fi:
            if fi[side]["fed"]:
                f.append(f"{side} fed champion(s): {', '.join(fi[side]['fed'])}")
            dz = fi[side]["death_zones"]
            if dz.get("enemy spawn", 0) >= 3:
                f.append(f"{side} died {dz['enemy spawn']}x near the enemy spawn (diving)")
            if dz.get("own spawn", 0) >= 3:
                f.append(f"{side} died {dz['own spawn']}x near its own spawn (spawn-camped)")
            if fi[side]["camp_deaths"] >= 3:
                f.append(f"{side} lost {fi[side]['camp_deaths']} champions to camps")
            mk = sum(len(v) for v in fi[side]["multikills"].values())
            if mk >= 3:
                f.append(f"{side} had {mk} multi-kills: {fmt_multi(fi[side]['multikills'])}")
        if ec and ec[side]["team"].get("unspent_end", 0) >= 300:
            f.append(f"{side} ended with {ec[side]['team']['unspent_end']} gold unspent")
        if co:
            if co[side]["locks"]["used_est"] >= 3 and co[o]["locks"]["used_est"] <= 1:
                f.append(f"{side} used ~{co[side]['locks']['used_est']} altar locks vs {co[o]['locks']['used_est']}")
            if co[side]["crystals"]["bought"] >= 2:
                f.append(f"{side} bought {co[side]['crystals']['bought']} teleport crystals")
        if fu and fu[side]["after_r1"] > 0:
            f.append(f"{side} fuelExhausted after r1: {fu[side]['after_r1']}")
        if idl and idl[side]["quiet_rounds"] >= 300:
            worst = max(idl[side]["champions"].items(), key=lambda kv: kv[1]["quiet_rounds"])
            f.append(f"{side} quiet champion-rounds {idl[side]['quiet_rounds']} (most: {worst[0]} {worst[1]['quiet_rounds']})")
    if fa:
        for i, (us_p, th_p) in enumerate(zip(fa["us"]["by_phase"], fa["them"]["by_phase"])):
            a, b = us_p["clears_per100"] or 0, th_p["clears_per100"] or 0
            if max(a, b) >= 1 and abs(a - b) >= 0.35 * max(a, b):
                f.append(f"clears/100r {us_p['phase']}: us {a} vs them {b}")
    if bu:
        for cp in ("r500", "r1000"):
            a = sum(bu["us"]["emblems"].get(cp, {}).values())
            b = sum(bu["them"]["emblems"].get(cp, {}).values())
            if abs(a - b) >= 3:
                f.append(f"emblems by {cp}: us {a} vs them {b}")
    if ec:
        a, b = ec["us"]["team"].get("r500", 0), ec["them"]["team"].get("r500", 0)
        if max(a, b) and abs(a - b) >= 0.25 * max(a, b):
            f.append(f"earned gold by r500: us {a} vs them {b}")
    return f


def profile(g, sections):
    prof = {}
    fns = {"meta": sec_meta, "draft": sec_draft, "build": sec_build, "economy": sec_economy, "farming": sec_farming,
           "tributes": sec_tributes, "fights": sec_fights, "control": sec_control, "fuel": sec_fuel, "idle": sec_idle}
    need = set(sections)
    if "diff" in need:
        need |= {"tributes", "farming", "fights", "control", "economy", "build", "idle", "fuel"}
    need.add("meta")
    for k in SECTIONS:
        if k in need and k in fns:
            prof[k] = fns[k](g)
    if "diff" in need:
        prof["diff"] = sec_diff(g, prof)
    return prof


# ----------------------------------------------------------------------------------------------- text output
def fmt_visits(visits, limit=14):
    parts = []
    for v in visits[:limit]:
        items = " ".join(f"{k}{'x%d' % n if n > 1 else ''}" for k, n in v["items"].items())
        emb = (" =>" + ",".join(v["emblems"])) if v["emblems"] else ""
        parts.append(f"r{v['r']} {items}{emb}".strip())
    more = f" | ... +{len(visits) - limit} visits" if len(visits) > limit else ""
    return (" | ".join(parts) + more) or "- (never shopped)"


def print_text(prof, sections, out=sys.stdout):
    p = lambda *a: print(*a, file=out)  # noqa: E731
    m = prof["meta"]
    us_side = m["us"][-1]
    p(f"\n{'=' * 118}")
    p(f"=== {m['map']} {m['size']} ({m.get('symmetry', '?')}, {m.get('picks', '?')} picks)  {m['result'].upper()} "
      f"{m['score_us']}-{m['score_them']}  r{m['rounds']} ({m['end']})  us=team{us_side} vs {m.get('opp') or '?'}"
      f" ({m.get('opp_rating') or '?'})  v{m.get('version') or '?'}  id {m['id'][:8]}")
    if not m["map_found"]:
        p("    (map file not found: zones/sides unavailable)")
    elif not m["map_hash_match"]:
        p("    (WARNING: map file matched by name only, hash differs: geometry may be stale)")
    if "meta" in sections and m.get("altars") is not None:
        alt = "  ".join(f"#{a['i']}{tuple(a['pos'])}{a['side']}" for a in m["altars"])
        sp = lambda b: f"x{b[0]}-{b[2]},y{b[1]}-{b[3]}"  # noqa: E731
        p(f"MAP   spawn us(team{us_side}) {sp(m['spawn']['us'])} them {sp(m['spawn']['them'])}; altars (side A/B/mid): {alt}; "
          f"{m['camp_groups']} camp groups")
    if "draft" in prof and "draft" in sections:
        d = prof["draft"]
        p(f"DRAFT us:   {', '.join(d['us'])}\n      them: {', '.join(d['them'])}")
    if "diff" in sections:
        print_diff(prof, p)
    if "economy" in sections:
        e = prof["economy"]
        p("-- ECONOMY  earned gold r250/r500/r1000/end | spent | unspent at end | sources kill/tribute/camps")
        for side in ("us", "them"):
            t = e[side]["team"]
            p(f"  {side:4s} TEAM {t.get('r250', 0):6d} {t.get('r500', 0):6d} {t.get('r1000', 0):6d} {t.get('end', 0):6d} | "
              f"{t.get('spent', 0):5d} | {t.get('unspent_end', 0):4d} | {t.get('src_kill', 0)}/{t.get('src_tribute', 0)}/{t.get('src_camps', 0)}")
            for name, r in e[side]["champions"].items():
                s = r["sources"]
                p(f"       {name:14s}{r['r250']:5d} {r['r500']:6d} {r['r1000']:6d} {r['end']:6d} | {r['spent']:5d} | "
                  f"{r['unspent_end']:4d} | {s.get('kill', 0)}/{s.get('tribute', 0)}/{s.get('camps', 0)}")
    if "build" in sections:
        b = prof["build"]
        p("-- BUILD  (shop visits: rN items, xN = count, =>emblem completed; Lock = altar lock, TP = teleport crystal)")
        for side in ("us", "them"):
            t = b[side]
            p(f"  {side}: emblems r500 [{fmt_counter(t['emblems'].get('r500', {}))}]  r1000 "
              f"[{fmt_counter(t['emblems'].get('r1000', {}))}]  end [{fmt_counter(t['emblems'].get('end', {}))}]")
            for name, c in t["champions"].items():
                p(f"     {name:14s} {fmt_visits(c['visits'])}")
    if "farming" in sections:
        f = prof["farming"]
        p("-- FARMING  clears/100r & camp gems per phase | captures by camp side (own/mid/enemy) | capture steals")
        for side in ("us", "them"):
            t = f[side]
            ph = "  ".join(f"{x['phase']}: {x['clears_per100']}/100r ({x['clears']}cl, {x['camp_gems']}g)" for x in t["by_phase"])
            bs = t.get("by_side", {})
            p(f"  {side:4s} clears {t['clears']:3d} captures {t['captures']:3d} | {ph}")
            if bs:
                p(f"       captures own/mid/enemy {bs.get('cap_own', 0)}/{bs.get('cap_mid', 0)}/{bs.get('cap_enemy', 0)} "
                  f"(gems {bs.get('capgems_own', 0)}/{bs.get('capgems_mid', 0)}/{bs.get('capgems_enemy', 0)}, base gold "
                  f"{bs.get('capgold_own', 0)}/{bs.get('capgold_mid', 0)}/{bs.get('capgold_enemy', 0)}), "
                  f"clears own/mid/enemy {bs.get('clear_own', 0)}/{bs.get('clear_mid', 0)}/{bs.get('clear_enemy', 0)}, "
                  f"steals {t['capture_steals']}")
        p("  gems per champion: collected = camps + kills | submitted | lost | carried end | clears | monster dmg done/taken")
        for side in ("us", "them"):
            for name, c in f[side]["champions"].items():
                p(f"     {side:4s} {name:14s} {c['collected']:4d} = {c['from_camps']:4d} + {c['from_kills']:3d} | {c['submitted']:4d} | "
                  f"{c['lost']:3d} | {c['carried_end']:3d} | {c['clears']:3d} | {c['monster_dmg']}/{c['monster_taken']}")
        if f["groups"]:
            us_l, th_l = ("A", "B") if us_side == "A" else ("B", "A")
            rows = sorted(f["groups"], key=lambda r: -(r["us_caps"] + r["them_caps"] + r["us_clears"] + r["them_clears"]))
            active = [r for r in rows if r["us_caps"] + r["them_caps"] + r["us_clears"] + r["them_clears"]]
            p(f"  camp groups (us=team{us_l}; d = BFS steps from each spawn / to nearest altar; side = clearly nearer spawn)")
            p("     gid label                  gems @center    dA/dB/alt side | us clr/cap first | them clr/cap first")
            for r in active[:18]:
                side = r["side"] if r["side"] == "mid" else ("us" if r["side"] == us_l else "them")
                p(f"     g{r['gid']:<3d}{r['label'][:22]:22s}{r['gems']:4d}g @{tuple(r['center'])!s:9s} {r['dA']:3d}/{r['dB']:<3d}/{nz(r['dAltar']):<3} {side:4s} | "
                  f"{r['us_clears']:2d}/{r['us_caps']:<2d} {str(r['us_first'] or '-'):>5s} | {r['them_clears']:2d}/{r['them_caps']:<2d} "
                  f"{str(r['them_first'] or '-'):>5s}")
            idle = [r for r in rows if not (r["us_caps"] + r["them_caps"] + r["us_clears"] + r["them_clears"])]
            if len(active) > 18 or idle:
                p(f"     ... {max(0, len(active) - 18)} more active, {len(idle)} never touched: "
                  + ", ".join(f"g{r['gid']}({r['label'][:12]},{r['gems']}g)" for r in idle[:8]))
    if "tributes" in sections:
        t = prof["tributes"]
        p("-- TRIBUTES  count | total | mean/median/max | >=30 | first | gap median/mean | per phase | lost on death champ/camp | carried end")
        for side in ("us", "them"):
            x = t[side]
            ph = " ".join(f"{q['count']}x/{q['gems']}g" for q in x["by_phase"])
            p(f"  {side:4s} {x['count']:3d} | {x['total']:4d} | {nz(x['mean'])}/{nz(x['median'])}/{x['max']} | {x['big30']:2d} | "
              f"{nz(x['first'])} | {nz(x['gap_median'])}/{nz(x['gap_mean'])} | {ph} | {x['lost_to_champs']}/{x['lost_to_camps']} "
              f"({x['deaths_with_gems']} deaths) | {x['carried_end']}")
            if x["altars"]:
                p("       by altar: " + "  ".join(f"#{k}{tuple(a['pos'])}{a.get('side', '')}: {a['count']}x {a['gems']}g"
                                                  for k, a in sorted(x["altars"].items())))
            p("       by champion: " + ", ".join(f"{n} {c['count']}x{nz(c['mean'])}" for n, c in x["champions"].items()))
    if "fights" in sections:
        fi = prof["fights"]
        ph_names = "/".join(n for i, (_, _, n) in enumerate(PHASES) if phase_len(i, m["rounds"]) > 0)
        p(f"-- FIGHTS  K/D/A per champion (by phase {ph_names}) | camp deaths | champ dmg done/taken | heal/shield")
        for side in ("us", "them"):
            for name, c in fi[side]["champions"].items():
                p(f"     {side:4s} {name:14s} {c['kills']:2d}/{c['deaths']:2d}/{c['assists']:2d} "
                  f"(K {'/'.join(map(str, c['kills_by_phase']))} D {'/'.join(map(str, c['deaths_by_phase']))}) | "
                  f"{c['camp_deaths']} | {c['champ_dmg']}/{c['champ_taken']} | {c['healing']}/{c['shielding']}")
        for side in ("us", "them"):
            x = fi[side]
            p(f"  {side:4s} deaths by zone: {fmt_counter(x['death_zones'])}")
            p(f"       kills by zone:  {fmt_counter(x['kill_zones'])}")
            p(f"       killed by: {fmt_counter(x['killed_by'])}"
              + (f" | FED: {', '.join(x['fed'])}" if x["fed"] else "")
              + (f" | multi-kills (kills per streak): {fmt_multi(x['multikills'])}" if x["multikills"] else ""))
        led = fi["ledger"]
        if led:
            big = sorted(sorted(led, key=lambda r: -(len(r["us_lost"]) + len(r["them_lost"])))[:12], key=lambda r: r["r"])
            p(f"  fights with >=2 deaths: {len(led)} (us won {sum(r['won_by'] == 'us' for r in led)}, them won "
              f"{sum(r['won_by'] == 'them' for r in led)}, even {sum(r['won_by'] == 'even' for r in led)}); biggest:")
            for r in big:
                p(f"     r{r['r']}-{r['r_end']} @{tuple(r['pos'])} [{r['zone_us']} for us] us lost {len(r['us_lost'])} "
                  f"({r['us_gems_dropped']}g) them lost {len(r['them_lost'])} ({r['them_gems_dropped']}g) -> {r['won_by']}: "
                  f"us[{', '.join(r['us_lost'])}] them[{', '.join(r['them_lost'])}]")
    if "control" in sections:
        c = prof["control"]
        p("-- MAP CONTROL  wards (after r10) by zone, in bush | altar locks bought/held/used~ first | TP crystals")
        for side in ("us", "them"):
            x = c[side]
            p(f"  {side:4s} wards {x['wards']} ({x['wards_after_r10']} after r10) [{fmt_counter(x['ward_zones'])}] bush {x['wards_in_bush']} | "
              f"locks {x['locks']['bought']}/{x['locks']['held_end']}/{x['locks']['used_est']} first r{nz(x['locks']['first_buy'])} | "
              f"TP {x['crystals']['bought']}/{x['crystals']['held_end']}/{x['crystals']['used_est']}")
    if "fuel" in sections:
        fu = prof["fuel"]
        p("-- FUEL  fuelExhausted total (after r1) | faults | per champion first rounds")
        for side in ("us", "them"):
            x = fu[side]
            p(f"  {side:4s} {x['total']} ({x['after_r1']}) | faults {x['faults']}{' RESIGNED' if x['resigned'] else ''} | "
              + ("; ".join(f"{n} {r}" for n, r in x["champions"].items()) or "-"))
    if "idle" in sections:
        q = prof["idle"]
        p(f"-- QUIET  champion-rounds with no metric change for >={QUIET_MIN} rounds while alive (stuck/waiting/long walks)")
        for side in ("us", "them"):
            x = q[side]
            items = [f"{n} {c['quiet_rounds']}" + (f" (longest r{c['longest']['from']}-{c['longest']['to']})" if c["longest"] else "")
                     for n, c in x["champions"].items() if c["quiet_rounds"]]
            p(f"  {side:4s} total {x['quiet_rounds']}: " + ("; ".join(items) or "-"))


def print_diff(prof, p):
    d = prof["diff"]
    m = prof["meta"]
    race = "  ".join(f"{k} {a}-{b} ({a - b:+d})" for k, (a, b) in d["race"].items())
    gold = "  ".join(f"{k} {a}-{b} ({a - b:+d})" for k, (a, b) in d["gold_race"].items())
    ahead = (f"ahead on gems for good from r{d['winner_ahead_from']}" if d["winner_ahead_from"] is not None
             else "never ahead on gems")
    p(f"-- DIFFERENCE  winner: {d['winner']} (decided by {d['decided_by']}), {ahead}")
    p(f"  gem race us-them:  {race}")
    p(f"  gold race us-them: {gold}  (lifetime earned gold = tiebreak #2)")
    p("  gap change per window (us-them): " + "  ".join(f"{w['w']}: {w['gap_change']:+d}" for w in d["windows"])
      + (f"   widest swing to winner: {d['widest_swing']['w']}" if d["widest_swing"] else ""))
    keys = ("clear", "capture", "tribute", "kill", "death", "item", "emblem")
    p("  opening (first round) us/them: " + "  ".join(f"{k} {nz(d['tempo']['us'][k])}/{nz(d['tempo']['them'][k])}" for k in keys))
    for side in ("us", "them"):
        s = d["style"][side]
        p(f"  style {side:4s}: clears {s['clears_per100']}/100r, kills {s['kills_per100']}/100r "
          f"({nz(s['kills_in_enemy_half_pct'])}% in enemy half/spawn), enemy-side caps {nz(s['enemy_side_caps_pct'])}%, "
          f"tributes {s['tributes']} x {nz(s['tribute_mean'])}, emblems {fmt_counter(s['emblem_families'])}, "
          f"locks used ~{s['locks_used']}, TP {s['tp_bought']}, wards {s['wards']}")
    p(f"  {'per phase (us/them)':22s}" + "".join(f"{x['phase']:>18s}" for x in d["pipeline"]["us"]))
    for k, lab in (("camp_gems", "camp gems captured"), ("kill_gems", "gems taken in kills"), ("lost_gems", "gems lost on death"),
                   ("tributed", "gems tributed"), ("clears", "camp clears"), ("kills", "kills"), ("deaths", "deaths"),
                   ("gold", "gold earned")):
        p(f"  {lab:22s}" + "".join(f"{str(u[k]) + '/' + str(t[k]):>18s}" for u, t in zip(d["pipeline"]["us"], d["pipeline"]["them"])))
    for e in d["edges"]:
        p(f"  {e['phase']:>9s}: winner tributed {e['tributed_gap']:+d}; biggest source: {e['top_source']} {e['top_value']:+d} "
          f"(camp {e['sources']['camp gems']:+d}, kills {e['sources']['gems taken in kills']:+d}, "
          f"loser's extra losses {e['sources']['gems lost on death (loser lost more)']:+d})")
    if d["flags"]:
        p("  notable: " + "\n           ".join(d["flags"]))


def print_set(games_prof, p=print):
    p(f"\n{'#' * 118}\nSET SUMMARY ({len(games_prof)} games)  record "
      f"{sum(1 for x in games_prof if x['meta']['result'] == 'win')}-{sum(1 for x in games_prof if x['meta']['result'] != 'win')}")
    p(f"{'map':22s} {'res':4s} {'score':>9s} {'r':>5s} {'r250':>9s} {'r500':>9s} {'r1000':>10s} {'ahead':>6s} "
      f"{'clr/100 us-th':>14s} {'K/D us':>7s} {'K/D th':>7s} {'1stTrib':>9s} {'trib mean':>10s} {'lost us/th':>11s} {'invade us/th':>12s} "
      f"{'widest swing':>16s} {'by':>5s}")
    for x in games_prof:
        m, d = x["meta"], x.get("diff", {})
        race = d.get("race", {})
        rr = lambda k: f"{race[k][0] - race[k][1]:+d}" if k in race else "-"  # noqa: E731
        fa, fi, tr = x.get("farming"), x.get("fights"), x.get("tributes")
        clr = (f"{per100(fa['us']['clears'], m['rounds'])}-{per100(fa['them']['clears'], m['rounds'])}" if fa else "-")
        kd = lambda s: f"{sum(c['kills'] for c in fi[s]['champions'].values())}/{sum(c['deaths'] for c in fi[s]['champions'].values())}" if fi else "-"  # noqa: E731
        ft = f"{nz(tr['us']['first'])}/{nz(tr['them']['first'])}" if tr else "-"
        tm = f"{nz(tr['us']['mean'])}/{nz(tr['them']['mean'])}" if tr else "-"
        sw = d.get("widest_swing")
        sw = f"{sw['w']}:{sw['gap_change']:+d}" if sw else "-"
        lost = (f"{tr['us']['lost_to_champs'] + tr['us']['lost_to_camps']}/{tr['them']['lost_to_champs'] + tr['them']['lost_to_camps']}"
                if tr else "-")
        inv = (f"{fa['us'].get('by_side', {}).get('cap_enemy', 0)}/{fa['them'].get('by_side', {}).get('cap_enemy', 0)}" if fa else "-")
        p(f"{m['map'][:22]:22s} {m['result'][:4]:4s} {m['score_us']:>4d}-{m['score_them']:<4d} {m['rounds']:5d} {rr('r250'):>9s} "
          f"{rr('r500'):>9s} {rr('r1000'):>10s} {str(nz(d.get('winner_ahead_from'))):>6s} {clr:>14s} {kd('us'):>7s} {kd('them'):>7s} "
          f"{ft:>9s} {tm:>10s} {lost:>11s} {inv:>12s} {sw:>16s} {d.get('decided_by', '-')[:5]:>5s}")
    opp = collections.Counter(tuple(x["draft"]["them"]) for x in games_prof if "draft" in x)
    if opp:
        p("opponent drafts: " + "; ".join(f"{', '.join(k)} x{v}" for k, v in opp.most_common()))


def set_summary(games_prof):
    rows = []
    for x in games_prof:
        m, d = x["meta"], x.get("diff", {})
        rows.append({"id": m["id"], "map": m["map"], "result": m["result"], "score": [m["score_us"], m["score_them"]],
                     "rounds": m["rounds"], "race": d.get("race"), "gold_race": d.get("gold_race"),
                     "decided_by": d.get("decided_by"), "winner_ahead_from": d.get("winner_ahead_from"),
                     "widest_swing": d.get("widest_swing"), "style": d.get("style"), "flags": d.get("flags")})
    return {"games": len(games_prof), "wins": sum(1 for x in games_prof if x["meta"]["result"] == "win"), "rows": rows}


# ----------------------------------------------------------------------------------------------- main
def group_paths(gid):
    rows = [r for r in ladder_rows() if r.get("group", "").startswith(gid)]
    if not rows:
        sys.exit(f"no games of group {gid} in {LADDER}")
    paths, missing = [], []
    for r in sorted(rows, key=lambda r: r.get("time", "")):
        p = os.path.join(SUMMARY_DIR, f"{r['id']}__{r['side'].upper()}.json")
        (paths if os.path.exists(p) else missing).append(p if os.path.exists(p) else r["id"])
    for mid in missing:
        side = next(r["side"].upper() for r in rows if r["id"] == mid)
        print(f"# missing stats for {mid}: cambc matches summary {mid} --json -o "
              f"matches/ladder/summary/{mid}__{side}.json", file=sys.stderr)
    return paths


def main():
    ap = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    ap.add_argument("paths", nargs="*")
    ap.add_argument("--group", action="append", default=[], help="ladder match-group id (prefix ok); repeatable")
    ap.add_argument("--json", action="store_true", help="print JSON instead of text")
    ap.add_argument("--us", choices=["teamA", "teamB"])
    ap.add_argument("--sections", default=",".join(SECTIONS), help="comma list from: " + ",".join(SECTIONS))
    args = ap.parse_args()
    sections = [s.strip() for s in args.sections.split(",") if s.strip()]
    bad = [s for s in sections if s not in SECTIONS]
    if bad:
        sys.exit(f"unknown sections {bad}; choose from {SECTIONS}")
    paths = list(args.paths)
    for gid in args.group:
        got = group_paths(gid)
        if not got:
            print(f"# group {gid}: no stats files present yet", file=sys.stderr)
        paths += got
    if not paths:
        ap.error("give stats JSON paths or --group (with downloaded stats)")
    profs = []
    for path in paths:
        g = Game(path, args.us)
        prof = profile(g, sections)
        profs.append(prof)
        if not args.json:
            print_text(prof, sections)
    if args.json:
        json.dump({"games": profs, "set": set_summary(profs) if len(profs) > 1 else None}, sys.stdout,
                  default=lambda o: sorted(o) if isinstance(o, set) else str(o))
        print()
    elif len(profs) > 1:
        print_set(profs)


if __name__ == "__main__":
    main()
