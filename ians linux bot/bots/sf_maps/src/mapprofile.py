"""Map-archetype profile (sf_maps).

Computed once in the draft (full map visible, huge fuel budget) and written to
draft memory; champions decode it in init_static.  Content-based only (never
map names).  Layout (zero-padded 1024 bytes):
  [0] MAGIC 0xA7   [1] VERSION   [2] flags
  [3] jackpot group idx (255 none)   [4] herd group idx (255 none)
  [5] number of gate groups k   [6..6+k) gate group idxs (<= 16)
  [22] number of enclosed groups m [23..23+m) enclosed group idxs (<= 32)
flags: 1 JACKPOT, 2 GATED (every altar needs a camp killed), 4 HERD (huge
group holds most gems), 8 BRAWL (harmless group holds >= 50% gems),
16 ENCLOSED (some gem groups unreachable on foot unless camps die).
"""
import cambc
from cambc import game_map

MAGIC = 0xA7
VERSION = 1
F_JACKPOT = 1
F_GATED = 2
F_HERD = 4
F_BRAWL = 8
F_ENCLOSED = 16
NONE = 255


class Profile:
    __slots__ = ("flags", "jackpot", "herd", "gates", "enclosed")

    def __init__(self):
        self.flags = 0
        self.jackpot = NONE
        self.herd = NONE
        self.gates = []
        self.enclosed = []

    def has(self, f):
        return (self.flags & f) != 0

    def encode(self):
        b = bytearray(64)
        b[0] = MAGIC
        b[1] = VERSION
        b[2] = self.flags & 0xFF
        b[3] = self.jackpot & 0xFF
        b[4] = self.herd & 0xFF
        g = [x for x in self.gates if x < 255][:16]
        b[5] = len(g)
        for i, x in enumerate(g):
            b[6 + i] = x
        e = [x for x in self.enclosed if x < 255][:32]
        b[22] = len(e)
        for i, x in enumerate(e):
            b[23 + i] = x
        return bytes(b)

    @staticmethod
    def decode(data):
        if data is None or len(data) < 64 or data[0] != MAGIC or data[1] != VERSION:
            return None
        p = Profile()
        p.flags = data[2]
        p.jackpot = data[3]
        p.herd = data[4]
        k = min(16, data[5])
        p.gates = [data[6 + i] for i in range(k)]
        m = min(32, data[22])
        p.enclosed = [data[23 + i] for i in range(m)]
        return p

    def __repr__(self):
        return "Profile(flags=%d jackpot=%d herd=%d gates=%s enclosed=%s)" % (
            self.flags, self.jackpot, self.herd, self.gates, self.enclosed)


def _reach(blk, start_bb, area):
    """Union of walk components of the start tiles (start tiles themselves walkable)."""
    out = cambc.Bitboard()
    for p in start_bb.positions():
        if out.is_set(p):
            continue
        b = blk.copy()
        b.set(p, False)
        r = b.reachable_tiles(p, area)
        r.set(p)
        out |= r
    return out


def compute(team=None):
    """Full-map analysis; costs a few M fuel (draft has ~250M)."""
    Team = cambc.Team
    if team is None:
        team = Team.ALLY
    enemy = Team.ENEMY if team == Team.ALLY else Team.ALLY
    W, H = game_map.width(), game_map.height()
    area = W * H
    groups = list(game_map.camp_groups())
    p = Profile()
    if not groups:
        return p
    static = game_map.walls() | game_map.holes() | game_map.altars() | game_map.spawn_region(enemy)
    camps_bb = cambc.Bitboard()
    info = []
    total_gems = 0
    for g in groups:
        tiles = g.spawn_tiles().copy()
        camps_bb |= tiles
        strength = 0.0
        hp = 0.0
        for c in g.camps():
            st = c.base_stats()
            strength += st.base_strength
            hp += st.base_health
        info.append((tiles, g.gem_value(), strength, hp, len(g)))
        total_gems += g.gem_value()
    spawn = game_map.spawn_region(team)
    ring = cambc.Bitboard()
    for a in game_map.altars().positions():
        ring.draw_chebyshev(a, 1)
    ring = ring & ~static
    free_reach = _reach(static, spawn, area)          # camps passable
    blk2 = static | camps_bb
    camp_reach = _reach(blk2, spawn, area)            # camps block
    edge = camp_reach.copy()
    h = edge | edge.shift_right(1) | edge.shift_right(-1)
    edge = h | h.shift_up(1) | h.shift_up(-1)         # dilate 1
    # jackpot / brawl / herd
    best = max(range(len(info)), key=lambda i: info[i][1])
    bt, bg, bs, bh, bn = info[best]
    if total_gems > 0:
        frac = bg / float(total_gems)
        if bg >= 60 and frac >= 0.35:
            if bs <= 0:
                p.flags |= F_JACKPOT
                p.jackpot = best
                if frac >= 0.5:
                    p.flags |= F_BRAWL
            elif bn >= 8 or bh >= 15000:
                p.flags |= F_HERD
                p.herd = best
            else:
                p.flags |= F_JACKPOT
                p.jackpot = best
    # enclosed groups: walkable when camps are passable, but no tile touches the
    # area reachable with camps blocking
    for i, (tiles, gems, s, hp, n) in enumerate(info):
        if (tiles & free_reach).is_empty():
            continue
        if (tiles & edge).is_empty():
            p.enclosed.append(i)
    if p.enclosed:
        p.flags |= F_ENCLOSED
    # gated altars: altar ring reachable only once some camp group dies
    if not (ring & free_reach).is_empty() and (ring & camp_reach).is_empty():
        p.flags |= F_GATED
        for i, (tiles, gems, s, hp, n) in enumerate(info):
            if (tiles & edge).is_empty():
                continue
            b2 = blk2 & ~tiles
            r2 = _reach(b2, spawn, area)
            if not (ring & r2).is_empty():
                p.gates.append(i)
        if not p.gates:
            # two-layer gate: take every group touching the reachable edge near altars
            for i, (tiles, gems, s, hp, n) in enumerate(info):
                if not (tiles & edge).is_empty() and s > 0:
                    p.gates.append(i)
    return p


def load():
    try:
        data = bytes(cambc.DraftMemoryBuffer())
    except Exception:
        try:
            data = bytes(cambc.draft_memory)
        except Exception:
            data = None
    return Profile.decode(data)
