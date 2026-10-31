"""tb_splitfarm: split-map efficient camp farmer.

Each champion independently scores every camp group (value / time) and
publishes its current target in team shared memory (one byte per champion
slot).  Groups already claimed by an ally are heavily discounted, so the team
naturally spreads over the map and farms in parallel.  A strict HP model is
used before engaging and while fighting: never start a fight we cannot finish,
step out of camp range (they do not chase and fall asleep) when the fight turns
bad, and recall to heal once safe.  Hole-separated areas are reached with a
dash or a TP crystal.
"""
import cambc
from cambc import game_map

Team = cambc.Team
Vec2 = cambc.Vec2
Bitboard = cambc.Bitboard
DistanceField = cambc.DistanceField
Item = cambc.ItemType
Cons = cambc.ConsumableType

BIG = 10 ** 6
MAX_ROUNDS = 2000
DEBUG = False
# ---- fuel (sf_fuel): Python costs ~150-400 fuel per bytecode and ~3k per API call, a
# full-map DistanceField ~750k on 100x100; the per-turn budget is 2.5M.
UNREACHED = 65535               # DistanceField.get() of a tile the search never reached
FUEL_BUILD_FLOOR = 1000000      # build one more cached static field only above this fuel
FUEL_SCORE_FLOOR = 800000       # stop optional target scoring below this (keep best so far)
FUEL_FIRST_TURN_MIN = 2000000   # after init_static, act on turn 1 only with this much fuel left
SCORE_BOUND_MULT = 1.95         # >= product of every score multiplier > 1 in choose_target
# ---- stuck guard (sf_fuel, INSIGHTS item 12)
STUCK_TURNS = 6                 # farming turns in a row with no move and no attack on one group
STUCK_BAN = 30                  # -> skip that group for this many rounds


def dilate(bb, r):
    out = bb.copy()
    for _ in range(r):
        h = out | out.shift_right(1) | out.shift_right(-1)
        out = h | h.shift_up(1) | h.shift_up(-1)
    return out


def cheb(a, b):
    return a.chebyshev_distance(b)


class Group:
    __slots__ = ("idx", "g", "camps", "tiles", "center", "gems", "gold", "maxhp", "strength",
                 "rng", "n", "status", "ready", "hp", "value")

    def __init__(self, idx, g):
        self.idx = idx
        self.g = g
        self.camps = []
        self.tiles = g.spawn_tiles().copy()
        self.gems = g.gem_value()
        self.gold = g.gold_value()
        self.maxhp = {}
        self.strength = 0.0
        self.rng = 0
        for c in g.camps():
            st = c.base_stats()
            p = c.spawn_position()
            self.camps.append((c, p, st.base_strength, st.base_attack_range))
            self.maxhp[p] = st.base_health
            self.strength += st.base_strength
            self.rng = max(self.rng, st.base_attack_range)
        self.n = len(self.camps)
        self.center = self.camps[0][1] if self.camps else Vec2(0, 0)
        # status: 0 alive (assumed), 1 reward available, 2 respawning
        self.status = 0
        self.ready = 0
        self.hp = dict(self.maxhp)
        self.value = self.gems + 0.25 * self.gold

    def hp_left(self):
        return sum(self.hp.values())

    def alive_strength(self):
        s = 0.0
        for c, p, st, r in self.camps:
            if self.hp.get(p, 0) > 0:
                s += st
        return s


class Bot:
    def __init__(self):
        self.inited = False
        self.target = None
        self.slot = 0
        self.comps = []
        self.cross_cache = {}
        self.need_crossing = False
        self.has_dash = False
        self.retreat_turns = 0
        self.last_print = 0
        self.sfields = {}   # static distance fields: group idx -> field rooted at its centre, -1 -> altar ring
        self.sf_todo = []   # keys still to build (until empty, a per-turn field is used instead)
        self.sf_use = False  # this turn may use sfields (False only if we stand on a walk_block tile)
        self.reach_memo = {}  # (group idx, id(comp), has crystal or 10 gold) -> can_reach result
        self.stuck = 0        # consecutive no-progress farming turns on group stuck_idx
        self.stuck_idx = -1
        self.banned = {}      # group idx -> round until which choose_target skips it

    # ------------------------------------------------------------------ setup
    def init_static(self, me):
        self.walk_block = (game_map.walls() | game_map.holes() | game_map.altars()
                           | game_map.spawn_region(Team.ENEMY))
        self.spawn = game_map.spawn_region(Team.ALLY).copy()
        self.altars = game_map.altars().positions()
        ring = Bitboard()
        for a in self.altars:
            ring.draw_chebyshev(a, 1)
        self.altar_ring = ring & ~self.walk_block
        self.groups = [Group(i, g) for i, g in enumerate(game_map.camp_groups())]
        self.all_camp_tiles = Bitboard()
        for G in self.groups:
            self.all_camp_tiles |= G.tiles
        self.area = game_map.width() * game_map.height()
        handles = sorted(int(c) for c in cambc.champions(Team.ALLY))
        try:
            self.slot = handles.index(int(me))
        except ValueError:
            self.slot = 0
        self.slot = min(self.slot, 7)
        for ab in me.abilities():
            try:
                if ab.is_dash():
                    self.has_dash = True
            except Exception:
                pass
        home = self.comp_of(self.spawn.positions()[0])
        self.need_crossing = any((G.tiles & home).is_empty() for G in self.groups) or \
            (self.altar_ring & home).is_empty()
        # build order: pop() from the end -> altar ring first, then groups farthest from our
        # spawn (the per-turn field then only has to reach the near, still-unbuilt ones)
        sp0 = self.spawn.positions()[0]
        self.sf_todo = [G.idx for G in sorted((G for G in self.groups if G.n > 0),
                                               key=lambda G: cheb(G.center, sp0))] + [-1]
        self.inited = True
        if DEBUG and self.slot == 0:
            W, H = game_map.width(), game_map.height()
            walls, holes, bush = game_map.walls(), game_map.holes(), game_map.bushes()
            alt, sp, esp = game_map.altars(), self.spawn, game_map.spawn_region(Team.ENEMY)
            camps = Bitboard()
            for G in self.groups:
                camps |= G.tiles
            for y in range(H):
                row = []
                for x in range(W):
                    v = Vec2(x, y)
                    ch = '.'
                    if walls.is_set(v): ch = '#'
                    elif holes.is_set(v): ch = 'o'
                    elif alt.is_set(v): ch = 'A'
                    elif sp.is_set(v): ch = 'S'
                    elif esp.is_set(v): ch = 'E'
                    elif camps.is_set(v): ch = 'c'
                    elif bush.is_set(v): ch = '"'
                    row.append(ch)
                print(''.join(row), flush=True)
            for G in self.groups:
                print("GROUP", G.idx, G.center, G.n, [int(c.kind()) for c, p, st, r in G.camps], G.gems, G.gold, G.strength, flush=True)

    def comp_of(self, pos):
        for c in self.comps:
            if c.is_set(pos):
                return c
        blk = self.walk_block.copy()
        blk.set(pos, False)
        c = blk.reachable_tiles(pos, self.area)
        c.set(pos)
        self.comps.append(c)
        return c

    # ----------------------------------------------------------- shared memory
    def read_claims(self):
        buf = bytearray(8)
        try:
            cambc.shared_memory.read(0, buf)
        except Exception:
            return {}
        claims = {}
        for s in range(8):
            if s != self.slot and buf[s]:
                claims[buf[s] - 1] = claims.get(buf[s] - 1, 0) + 1
        return claims

    def write_claim(self, idx):
        try:
            v = 0 if idx is None or idx >= 255 else idx + 1
            cambc.shared_memory.write(self.slot, bytes([v]))
        except Exception:
            pass

    # -------------------------------------------------------------- knowledge
    def observe(self, me, rnd):
        pos = me.position()
        vis = None
        for G in self.groups:
            if G.status == 2 and rnd >= G.ready:
                G.status = 0
                G.hp = dict(G.maxhp)
            if cheb(G.center, pos) > 10:
                continue
            if vis is None:
                vis = cambc.vision.visible_tiles()
            if (G.tiles & vis).is_empty():
                continue
            try:
                st = G.g.state()
            except Exception:
                continue
            if isinstance(st, game_map.CampGroupRespawning):
                G.status = 2
                G.ready = rnd + st.timer
                G.hp = dict(G.maxhp)
            elif isinstance(st, game_map.CampGroupRewardAvailable):
                G.status = 1
                for p in G.hp:
                    G.hp[p] = 0
            else:
                G.status = 0
                for c, p, s, r in G.camps:
                    try:
                        if vis.is_set(p) and not cambc.vision.has_camp(p):
                            G.hp[p] = 0
                        elif c.is_visible():
                            G.hp[p] = 0 if c.state().is_dead() else c.health()
                            if DEBUG and G.hp[p] > 0 and G.hp[p] < G.maxhp[p] and c.state().is_asleep():
                                print("ASLEEP-DAMAGED", rnd, p, G.hp[p], flush=True)
                    except Exception:
                        pass

    def threats(self, me):
        """Incoming damage per round from awake camps and enemy champions in range."""
        pos = me.position()
        inc = 0.0
        awake = []
        for c in cambc.vision.camps():
            try:
                if not c.is_awake():
                    continue
                cp = c.position()
                r = c.attack_range()
                awake.append((c, cp, r, c.strength()))
                if cheb(cp, pos) <= r:
                    inc += c.strength()
            except Exception:
                pass
        enemies = []
        for e in cambc.vision.champions(Team.ENEMY):
            try:
                if not e.is_alive():
                    continue
                ep = e.position()
                enemies.append(e)
                if cheb(ep, pos) <= e.attack_range() + 1:
                    inc += e.strength()
            except Exception:
                pass
        if self.jungle(me):
            # Jungle emblem: 30% less camp damage (approximate on the total).
            inc *= 0.8
        return inc, awake, enemies

    def jungle(self, me):
        try:
            return me.item_count()[int(Item.JUNGLE_EMBLEM_OF_STRENGTH)] > 0
        except Exception:
            return False

    # --------------------------------------------------------------- movement
    def blocked_now(self, me):
        blocked = (self.walk_block | cambc.vision.champion_tiles() | cambc.vision.camp_tiles()
                   | cambc.vision.teleport_tiles())
        blocked.set(me.position(), False)
        return blocked

    def step_toward(self, me, goals, avoid=None, no_enter=None):
        if not me.can_move():
            return False
        pos = me.position()
        if goals.is_set(pos) or goals.is_empty():
            return False
        blocked = self.blocked_now(me)
        if no_enter is not None:
            ne = no_enter & ~goals
            ne.set(pos, False)
            blocked |= ne
        for av in ((avoid,) if avoid is None else (avoid, None)):
            walls = blocked & ~goals
            if av is not None:
                walls |= av & ~goals
                walls.set(pos, False)
            field = DistanceField()
            start = Bitboard()
            start.set(pos)
            visited = Bitboard()
            field.compute_to(walls, goals, start, visited)
            if not visited.is_set(pos):
                continue
            cur = field.get(pos)
            best = None
            bd = cur
            stepable = walls if no_enter is None else (walls | no_enter)
            stepable.set(pos, False)
            for t in stepable.reachable_tiles(pos, 1).positions():
                if t == pos or not visited.is_set(t):
                    continue
                v = field.get(t)
                if v < bd:
                    bd = v
                    best = t
            if best is not None:
                try:
                    return me.move_absolute(best)
                except Exception:
                    return False
        return False

    def dist_field(self, me, dests=None):
        field = DistanceField()
        roots = Bitboard()
        roots.set(me.position())
        visited = Bitboard()
        blk = self.walk_block.copy()
        blk.set(me.position(), False)
        if dests is not None:
            # exact for every tile in dests (BFS stops once they are all reached)
            field.compute_to(blk, roots, dests, visited)
            return field, visited
        field.compute(blk, roots, visited)
        return field, visited

    # ------------------------------------------------- fuel: static field cache
    def build_static_fields(self, floor=FUEL_BUILD_FLOOR):
        """Spend spare fuel on cached distance fields over the static walk mask, one rooted
        at each camp group centre and one at the altar ring.  Walking distance is symmetric,
        so field_G.get(pos) equals the per-turn field-from-pos value at G.center exactly;
        once all are built the ~750k per-turn full-map field is no longer needed."""
        todo = self.sf_todo
        while todo and cambc.fuel_remaining() > floor:
            key = todo[-1]
            roots = Bitboard()
            if key < 0:
                roots |= self.altar_ring
            else:
                roots.set(self.groups[key].center)
            field = DistanceField()
            field.compute(self.walk_block & ~roots, roots, Bitboard())
            self.sfields[key] = field
            todo.pop()

    def sf_dests(self):
        """Tiles the per-turn field must still reach: centres of unbuilt groups (+ altar ring)."""
        dests = Bitboard()
        for key in self.sf_todo:
            if key < 0:
                dests |= self.altar_ring
            else:
                dests.set(self.groups[key].center)
        return dests

    def group_dist(self, G, pos, field, visited):
        """Walking distance pos -> G.center, None if not in our walk component."""
        sf = self.sfields.get(G.idx) if self.sf_use else None
        if sf is not None:
            v = sf.get(pos)
            return None if v >= UNREACHED else v
        if visited.is_set(G.center):
            return field.get(G.center)
        return None

    def target_order(self, me, pos, field, visited, comp):
        """[(score upper bound, group, distance)] for reachable groups: current target first,
        then best bound first.  cost >= d + 6 and SCORE_BOUND_MULT covers every multiplier,
        so choose_target skips groups whose bound is below its best score without changing
        the result (ties still go to the lowest group index, as in the original loop)."""
        out = []
        cg = None
        banned = self.banned
        now = cambc.round_number() if banned else 0
        for G in self.groups:
            if G.n == 0 or (banned and banned.get(G.idx, 0) > now):
                continue
            d = self.group_dist(G, pos, field, visited)
            if d is None:
                # can_reach depends only on (G, comp, crystal-or-10-gold): memoize it
                if cg is None:
                    cg = self.crystal(me) is not None or me.gold_count() >= 10
                key = (G.idx, id(comp), cg)
                ok = self.reach_memo.get(key)
                if ok is None:
                    ok = self.reach_memo[key] = self.can_reach(me, G, comp)
                if not ok:
                    continue
                d = cheb(pos, G.center) * 1.5 + 12
            out.append((G.value * SCORE_BOUND_MULT / (d + 6), G.idx, G, d))
        out.sort(key=lambda t: -t[0])
        # score the current target first: it usually wins (x1.3) and lets the bound prune more
        for i, t in enumerate(out):
            if t[2] is self.target:
                if i:
                    out.insert(0, out.pop(i))
                break
        return out

    def dash_ability(self, me):
        for ab in me.abilities():
            try:
                if ab.is_dash() and ab.is_ready():
                    return ab
            except Exception:
                pass
        return None

    def crystal(self, me):
        try:
            c = me.consumables()[int(Cons.TP_CRYSTAL)]
            return c if c.count() > 0 else None
        except Exception:
            return None

    def staging(self, comp, tcomp, r):
        key = (id(comp), id(tcomp), r)
        st = self.cross_cache.get(key)
        if st is None:
            st = comp & dilate(tcomp, r)
            self.cross_cache[key] = st
        return st

    def cross_toward(self, me, goals, comp):
        """Move toward goals in another walk component using dash or TP crystal."""
        pos = me.position()
        gpos = goals.positions()
        if not gpos:
            return False
        target_comp = self.comp_of(gpos[0])
        dash = self.dash_ability(me)
        crystal = self.crystal(me)
        st2 = self.staging(comp, target_comp, 2) if self.has_dash else None
        st3 = self.staging(comp, target_comp, 3)
        if st2 is not None and not st2.is_empty() and (crystal is None or st2.is_set(pos) or dash is not None):
            staging, r = st2, 2
        elif not st3.is_empty():
            if crystal is None:
                if me.gold_count() >= 10 and not self.spawn.is_set(pos):
                    try:
                        me.recall()
                        return True
                    except Exception:
                        return False
                return False
            staging, r = st3, 3
        else:
            return False
        if staging.is_set(pos):
            blocked = self.blocked_now(me)
            near = Bitboard()
            near.draw_chebyshev(pos, r)
            land = near & target_comp & ~blocked
            gc = gpos[0]
            cands = sorted(land.positions(), key=lambda t: cheb(t, gc))
            if dash is not None:
                for t in cands:
                    if cheb(t, pos) > 2:
                        continue
                    try:
                        if dash.use(t):
                            return True
                    except Exception:
                        continue
            if crystal is not None:
                for t in cands:
                    try:
                        if crystal.use(t):
                            return True
                    except Exception:
                        continue
            return False
        return self.step_toward(me, staging)

    def go_to(self, me, goals, avoid=None, no_enter=None):
        comp = self.comp_of(me.position())
        local = goals & comp
        if local.is_empty():
            return self.cross_toward(me, goals, comp)
        return self.step_toward(me, local, avoid, no_enter)

    def can_reach(self, me, G, comp):
        if not (G.tiles & comp).is_empty():
            return True
        tcomp = self.comp_of(G.center)
        if self.has_dash and not self.staging(comp, tcomp, 2).is_empty():
            return True
        if (self.crystal(me) is not None or me.gold_count() >= 10) and \
                not self.staging(comp, tcomp, 3).is_empty():
            return True
        return False

    # ------------------------------------------------------------------- shop
    def shop(self, me):
        try:
            if self.need_crossing and self.crystal(me) is None:
                if me.can_buy(Cons.TP_CRYSTAL):
                    me.buy(Cons.TP_CRYSTAL)
        except Exception:
            pass
        for _ in range(12):
            try:
                counts = me.item_count()
                if counts[int(Item.JUNGLE_EMBLEM_OF_STRENGTH)] == 0:
                    item = Item.JUNGLE_SHARD_OF_STRENGTH
                elif counts[int(Item.MONSTER_EMBLEM_OF_STRENGTH)] == 0:
                    item = Item.MONSTER_SHARD_OF_STRENGTH
                elif counts[int(Item.POWER_SHARD_OF_HEALTH)] < counts[int(Item.POWER_SHARD_OF_STRENGTH)]:
                    item = Item.POWER_SHARD_OF_HEALTH
                else:
                    item = Item.POWER_SHARD_OF_STRENGTH
                if not me.can_buy(item, 1):
                    return
                me.buy(item, 1)
            except Exception:
                return

    # ----------------------------------------------------------------- combat
    def dps(self, me):
        d = me.strength()
        try:
            if me.item_count()[int(Item.MONSTER_EMBLEM_OF_STRENGTH)] > 0:
                d *= 1.15
        except Exception:
            pass
        bonus = 0.0
        for ab in me.abilities():
            try:
                if ab.is_attack_reset():
                    bonus += me.strength() / 8.0
                elif ab.is_damage() or ab.is_cc() or ab.is_aoe_damage():
                    bonus += ab.damage_amount() / 8.0
            except Exception:
                pass
        return max(1.0, d + bonus)

    def cast_combat(self, me, target, moved, incoming, attacked):
        """One cast per turn: shield if taking damage, else damage, else attack reset."""
        abilities = me.abilities()
        pos = me.position()
        for ab in abilities:
            try:
                if ab.is_shield() and ab.is_ready() and incoming > 0 and not me.buffs().has_shield():
                    if ab.use(None):
                        return
            except Exception:
                pass
        if target is not None:
            for ab in abilities:
                try:
                    if not ab.is_ready():
                        continue
                    if not (ab.is_damage() or ab.is_cc() or ab.is_aoe_damage()):
                        continue
                    info = ab.info()
                    if info.exclusive_with_movement and moved:
                        continue
                    tp = target.position()
                    if cheb(tp, pos) > info.range:
                        continue
                    if ab.is_aoe_damage() and not ab.is_cc():
                        if ab.use(tp):
                            return
                    else:
                        if ab.use(target):
                            return
                except Exception:
                    pass
        for ab in abilities:
            try:
                if ab.is_heal() and ab.is_ready():
                    best = None
                    for a in cambc.vision.champions(Team.ALLY):
                        if int(a) == int(me) or not a.is_alive():
                            continue
                        if cheb(a.position(), pos) <= 4 and a.health() < a.max_health() * 0.7:
                            if best is None or a.health() < best.health():
                                best = a
                    if best is not None and ab.use(best):
                        return
            except Exception:
                pass
        if attacked and target is not None:
            for ab in abilities:
                try:
                    if ab.is_attack_reset() and ab.is_ready():
                        if ab.use(None):
                            if me.can_attack() and target.is_visible() and target.health() > 0 \
                                    and me.attack_tiles().is_set(target.position()):
                                me.attack(target)
                            return
                except Exception:
                    pass

    def pick_camp_in_range(self, me, G):
        tiles = me.attack_tiles()
        best = None
        for c, p, s, r in G.camps:
            try:
                if not c.is_visible() or c.state().is_dead():
                    continue
                if tiles.is_set(c.position()):
                    if best is None or c.health() < best.health():
                        best = c
            except Exception:
                pass
        return best

    def alive_tiles(self, G):
        b = Bitboard()
        for c, p, s, r in G.camps:
            if G.hp.get(p, 1) > 0:
                b.set(p)
        return b

    # -------------------------------------------------------------- decisions
    def choose_target(self, me, rnd, field, visited, comp):
        claims = self.read_claims()
        hp = me.health()
        dps = self.dps(me)
        dmg_mult = 0.7 if self.jungle(me) else 1.0
        maxhp = me.max_health()
        best = None
        best_score = 0.0
        pos = me.position()
        for bound, _, G, d in self.target_order(me, pos, field, visited, comp):
            if bound < best_score:
                continue
            if best is not None and cambc.fuel_remaining() < FUEL_SCORE_FLOOR:
                break
            if G.status == 2 and G.ready > rnd + d:
                continue
            wait = max(0, G.ready - rnd - d) if G.status == 2 else 0
            c = claims.get(G.idx, 0)
            extra = 0.0
            solo_ok = True
            if G.status == 1:
                ttk = 0.0
            else:
                hl = G.hp_left() if G.status == 0 else sum(G.maxhp.values())
                s = G.alive_strength() if G.status == 0 else G.strength
                tdps = dps + c * 55.0
                ttk = hl / tdps
                if s > 0:
                    share = 1.0 if G.n == 1 else 0.7
                    dmg_solo = s * (hl / dps) * share * dmg_mult
                    solo_ok = dmg_solo <= hp - 150
                    dmg = s * ttk * share * dmg_mult / (1 + c)
                    if not (self.target is G) and hp < maxhp * 0.6:
                        continue
                    if dmg > hp - 150:
                        budget = maxhp - s * dmg_mult * (G.rng + 1) - 80
                        if budget <= 0:
                            continue
                        per_cycle = budget / (s * dmg_mult) * tdps
                        cycles = hl / per_cycle
                        if cycles > 4:
                            continue
                        extra = cycles * 30.0
            if rnd + d + ttk + 8 > MAX_ROUNDS:
                continue
            cost = d + ttk + 6 + extra + wait
            score = G.value / cost
            if G.status == 1:
                score *= 1.5
            if c:
                if G.status == 1:
                    score *= 0.6
                elif solo_ok:
                    score *= 0.3
                else:
                    score *= 1.2
            if self.target is G:
                score *= 1.3
            if score > best_score or (score == best_score and best is not None and G.idx < best.idx):
                best_score = score
                best = G
        return best

    def note_progress(self, G, rnd, progress):
        """Stuck guard: STUCK_TURNS farming turns in a row without a move or an attack on the
        same group (e.g. its only path is blocked by a sleeping camp or a parked champion, or
        we stand in range without a hittable camp) -> skip that group for STUCK_BAN rounds."""
        if progress:
            self.stuck = 0
            return
        if self.stuck_idx != G.idx:
            self.stuck_idx = G.idx
            self.stuck = 0
        self.stuck += 1
        if self.stuck >= STUCK_TURNS:
            self.banned[G.idx] = rnd + STUCK_BAN
            self.stuck = 0

    def nearest_altar(self, me):
        best = None
        bd = BIG
        pos = me.position()
        for a in self.altars:
            try:
                if cambc.vision.has_altar_lock(a) and cambc.vision.altar_lock_at(a).is_enemy():
                    continue
            except Exception:
                pass
            d = cheb(a, pos)
            if d < bd:
                bd = d
                best = a
        return best, bd

    def altar_distance(self, field, visited, pos=None):
        if self.sf_use and -1 in self.sfields:
            v = self.sfields[-1].get(pos)
            return BIG if v >= UNREACHED else v
        best = BIG
        for t in self.altar_ring.positions():
            if visited.is_set(t):
                v = field.get(t)
                if v < best:
                    best = v
        return best

    def do_tribute(self, me):
        pos = me.position()
        for a in self.altars:
            if cheb(a, pos) <= 1:
                try:
                    if cambc.vision.has_altar_lock(a) and cambc.vision.altar_lock_at(a).is_enemy():
                        continue
                except Exception:
                    pass
                try:
                    me.submit_gems(a)
                    return True
                except Exception as e:
                    print("submit failed", e, flush=True)
        goals = self.altar_ring & ~self.blocked_now(me)
        if goals.is_empty():
            goals = self.altar_ring
        comp = self.comp_of(pos)
        if (goals & comp).is_empty():
            if self.cross_toward(me, goals, comp):
                return True
            if not self.spawn.is_set(pos):
                try:
                    me.recall()
                    return True
                except Exception:
                    pass
            return False
        return self.step_toward(me, goals & comp)

    def retreat(self, me, awake, enemies):
        """Step to the adjacent tile with the least incoming damage."""
        pos = me.position()
        blocked = self.blocked_now(me)

        def danger(t):
            d = 0.0
            for c, cp, r, s in awake:
                if cheb(cp, t) <= r:
                    d += s
            for e in enemies:
                try:
                    if cheb(e.position(), t) <= e.attack_range() + 1:
                        d += e.strength()
                except Exception:
                    pass
            md = min([cheb(cp, t) - r for c, cp, r, s in awake] or [0])
            return (d, -md)

        cands = [pos] + [t for t in blocked.reachable_tiles(pos, 1).positions() if t != pos]
        dash = self.dash_ability(me)
        if dash is not None:
            near = Bitboard()
            near.draw_chebyshev(pos, 2)
            far = near & ~blocked & ~self.walk_block
            dcands = sorted(far.positions(), key=danger)
            if dcands and danger(dcands[0]) < danger(pos):
                for t in dcands[:4]:
                    if cheb(t, pos) < 2:
                        continue
                    try:
                        if dash.use(t):
                            return True
                    except Exception:
                        continue
        if not me.can_move():
            return False
        best = min(cands, key=danger)
        if best != pos:
            try:
                return me.move_absolute(best)
            except Exception:
                return False
        return False

    def handle_enemies(self, me, enemies, awake, incoming, hp, maxhp):
        """Chase and kill weaker enemy champions nearby; step away from stronger ones."""
        pos = me.position()
        my_str = max(1.0, me.strength())
        near = []
        threat = 0.0
        for e in enemies:
            try:
                d = cheb(e.position(), pos)
                if d <= 6:
                    near.append((e, d))
                if d <= e.attack_range() + 2:
                    threat += e.strength() * (1.0 if e.attack_range() <= 1 else 1.0)
            except Exception:
                pass
        if not near:
            return False
        camp_inc = 0.0
        for c, cp, r, s in awake:
            if cheb(cp, pos) <= r:
                camp_inc += s
        ally_str = 0.0
        for a in cambc.vision.champions(Team.ALLY):
            try:
                if int(a) != int(me) and a.is_alive() and cheb(a.position(), pos) <= 4:
                    ally_str += a.strength() * 0.7
            except Exception:
                pass
        best = None
        best_key = None
        for e, d in near:
            try:
                eh = e.health()
                my_ttk = eh / (my_str + ally_str) + max(0, d - me.attack_range())
                their_ttk = hp / max(1.0, threat + camp_inc)
                if my_ttk <= their_ttk * 0.8:
                    key = (my_ttk, d)
                    if best_key is None or key < best_key:
                        best_key = key
                        best = e
            except Exception:
                pass
        if best is not None:
            moved = False
            tiles = me.attack_tiles()
            if not tiles.is_set(best.position()):
                dash = self.dash_ability(me)
                if dash is not None and cheb(best.position(), pos) >= 3:
                    blocked = self.blocked_now(me)
                    ring = Bitboard()
                    ring.draw_chebyshev(pos, 2)
                    adj = Bitboard()
                    adj.draw_chebyshev(best.position(), me.attack_range())
                    for t in (ring & adj & ~blocked).positions():
                        try:
                            if dash.use(t):
                                moved = True
                                break
                        except Exception:
                            continue
                if not moved:
                    goal = Bitboard()
                    goal.set(best.position())
                    moved = self.step_toward(me, goal)
            attacked = False
            try:
                if me.can_attack() and me.attack_tiles().is_set(best.position()):
                    me.attack(best)
                    attacked = True
            except Exception:
                pass
            self.cast_combat(me, best, moved, incoming, attacked)
            return True
        # unfavourable: if they can hit us, step away (and recall once out of reach)
        if threat > 0:
            if hp < maxhp * 0.5 and incoming == 0 and not self.spawn.is_set(pos):
                try:
                    me.recall()
                    return True
                except Exception:
                    pass
            self.retreat(me, awake, [e for e, d in near])
            return True
        return False

    # ------------------------------------------------------------------- turn
    def play_turn(self):
        me = cambc.me()
        if not self.inited:
            self.init_static(me)
            if cambc.fuel_remaining() < FUEL_FIRST_TURN_MIN and me.is_alive():
                # init used most of the 2x first-turn budget: shop now and let main.py spend
                # the rest on static fields instead of being suspended mid-decision
                if self.spawn.is_set(me.position()):
                    self.shop(me)
                return
        rnd = cambc.round_number()
        if not me.is_alive():
            self.write_claim(None)
            try:
                self.shop(me)
            except Exception:
                pass
            return
        self.observe(me, rnd)
        if me.is_recalling() or me.is_submitting_gems() or me.is_teleporting():
            return
        pos = me.position()
        at_spawn = self.spawn.is_set(pos)
        if at_spawn:
            self.shop(me)

        incoming, awake, enemies = self.threats(me)
        hp = me.health()
        maxhp = me.max_health()

        # Heal up fully on spawn before leaving.
        if at_spawn and hp < maxhp * 0.92 and incoming == 0:
            return

        # ---- danger handling: never die to camps
        if incoming > 0:
            steps = 1
            for c, cp, r, s in awake:
                if cheb(cp, pos) <= r:
                    steps = max(steps, r - cheb(cp, pos) + 1)
            # can we finish the camps hitting us quickly?
            hit_hp = 0.0
            for c, cp, r, s in awake:
                if cheb(cp, pos) <= r:
                    try:
                        hit_hp += c.health()
                    except Exception:
                        pass
            finish_turns = hit_hp / self.dps(me) + 1
            safe_finish = finish_turns * incoming < hp - 60 and not enemies
            if not safe_finish and hp <= incoming * (steps + 1) + 60:
                self.retreat_turns = 3
                self.retreat(me, awake, enemies)
                return

        # ---- fight or avoid enemy champions
        if enemies and self.handle_enemies(me, enemies, awake, incoming, hp, maxhp):
            return

        # ---- recall to heal / shop when safe
        if incoming == 0 and not at_spawn:
            spawn_d = min(cheb(p, pos) for p in self.spawn.positions())
            low = hp < maxhp * 0.45
            rich = (me.gold_count() >= 150 and me.gem_count() < 8) or me.gold_count() >= 400
            if (low or rich) and spawn_d > 6:
                try:
                    me.recall()
                    self.write_claim(None)
                    return
                except Exception:
                    pass
            elif low:
                self.step_toward(me, self.spawn)
                return

        self.sf_use = not self.walk_block.is_set(pos)
        if not self.sf_use:
            field, visited = self.dist_field(me)
        elif self.sf_todo:
            field, visited = self.dist_field(me, self.sf_dests())
        else:
            field, visited = None, None  # cached static fields (group_dist / altar_distance)
        comp = self.comp_of(pos)

        # ---- tribute decision
        gems = me.gem_count()
        tgt = None
        chosen = False
        if gems > 0:
            ad = self.altar_distance(field, visited, pos)
            if ad >= BIG:
                ad = 40
            total = cambc.global_submitted_gems(Team.ALLY) + gems
            go = (gems >= 35 or ad <= 4 or rnd + ad + gems // 10 + 12 >= MAX_ROUNDS or total >= 1000
                  or (gems >= 12 and hp < maxhp * 0.6) or (gems >= 10 and enemies))
            if not go:
                tgt = self.choose_target(me, rnd, field, visited, comp)
                chosen = True
                if tgt is None:
                    go = True
            if go:
                self.write_claim(None)
                self.do_tribute(me)
                return

        # ---- farming
        G = tgt if chosen else self.choose_target(me, rnd, field, visited, comp)
        self.target = G
        if DEBUG and rnd - self.last_print >= 100:
            self.last_print = rnd
            print("r", rnd, "slot", self.slot, "pos", pos, "hp", int(hp), "gold", me.gold_count(),
                  "gems", gems, "tgt", None if G is None else (G.idx, G.center, G.status, G.gems),
                  "ncomps", len(self.comps), "cross", self.need_crossing, "dash", self.has_dash,
                  "crystal", self.crystal(me) is not None, "vis", -1 if visited is None else visited.count(), "comp", comp.count(), flush=True)
            if G is not None:
                info = []
                for c, p, st, r in G.camps:
                    try:
                        info.append((p, G.hp.get(p), c.is_visible(), str(c.state()) if c.is_visible() else '-', c.kind()))
                    except Exception as e:
                        info.append((p, 'err', str(e)))
                print("   G", G.idx, info, flush=True)
        self.write_claim(None if G is None else G.idx)
        if G is None:
            if gems > 0:
                self.do_tribute(me)
            elif not at_spawn and (me.gold_count() >= 60 or hp < maxhp * 0.7):
                try:
                    me.recall()
                except Exception:
                    pass
            return

        if G.status != 1 and self.all_camp_tiles.is_set(pos):
            # never block a camp's respawn by standing on its spawn tile
            off = self.blocked_now(me).reachable_tiles(pos, 1) & ~self.all_camp_tiles & ~self.walk_block
            off.set(pos, False)
            cands = off.positions()
            if cands and me.can_move():
                try:
                    me.move_absolute(min(cands, key=lambda t: cheb(t, G.center)))
                except Exception:
                    pass
                return
        if G.status == 2:
            ring = dilate(G.tiles, 1) & ~self.all_camp_tiles & ~self.walk_block
            if not ring.is_set(pos):
                self.go_to(me, ring)
            return
        if G.status == 0 and cheb(G.center, pos) <= 3:
            seen_alive = False
            for c, p, st, r in G.camps:
                try:
                    if c.is_visible() and not c.state().is_dead():
                        seen_alive = True
                        break
                except Exception:
                    pass
            if not seen_alive:
                G.status = 2
                G.ready = rnd + 10
                return
        if G.status == 1:
            # capture: stand on a free spawn tile of the group
            if G.tiles.is_set(pos):
                return
            free = G.tiles & ~self.blocked_now(me)
            if free.is_empty():
                free = G.tiles
            self.go_to(me, free)
            return

        # avoid walking into range of other awake camps
        avoid = None
        for c, cp, r, s in awake:
            if G.hp.get(cp) is None or cp not in G.hp:
                if avoid is None:
                    avoid = Bitboard()
                avoid.draw_chebyshev(cp, r)

        moved = False
        target = self.pick_camp_in_range(me, G)
        ranged = me.attack_range() > 1
        if target is None:
            alive = self.alive_tiles(G)
            if alive.is_empty():
                alive = G.tiles
            goals = alive
            if cheb(G.center, pos) <= 5:
                unseen = alive & ~cambc.vision.visible_tiles()
                if not unseen.is_empty():
                    bush_goals = dilate(unseen, 1) & game_map.bushes() & ~alive & ~self.walk_block
                    if not bush_goals.is_empty():
                        goals = bush_goals
            if ranged and goals is alive:
                rng_goals = dilate(alive, me.attack_range()) & ~alive & ~self.walk_block
                if not rng_goals.is_empty():
                    goals = rng_goals
            moved = self.go_to(me, goals, avoid, alive)
            target = self.pick_camp_in_range(me, G)
        attacked = False
        if target is not None and me.can_attack():
            try:
                me.attack(target)
                attacked = True
            except Exception:
                pass
        if target is not None or incoming > 0:
            self.cast_combat(me, target, moved, incoming, attacked)
        self.note_progress(G, rnd, moved or attacked)
