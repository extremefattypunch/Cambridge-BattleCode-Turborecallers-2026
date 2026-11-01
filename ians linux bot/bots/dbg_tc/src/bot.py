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
# sf_pvp: threat weight of an enemy by channel (none, tribute, teleport, recall):
# a tributing enemy must cancel before it can hit back, a teleporting one cannot act.
CHAN_THREAT = (1.0, 0.5, 0.0, 1.0)
LOCK_MIN_GOLD = 40
USE_WARDS = True
LOCK_SIDE_MARGIN = 4  # proactively lock altars no farther from the enemy spawn than ours + this
# sf_pvp: shared-memory byte holding the team focus enemy ((index+1) << 5 | round & 31).
# Bytes 0..n_bodies-1 are the per-champion camp claims (n_bodies <= 6).
FOCUS_BYTE = 7
FOCUS_TTL = 3
ENEMY_SIGHT = 8  # enemies farther than own vision (seen only via the ward) are not threats

# sf_bank: census banking rule (INSIGHTS 2.3): bank >= BANK_ANY gems anywhere, >= BANK_NEAR
# within BANK_NEAR_D path tiles of an altar, >= BANK_CLOSE within BANK_CLOSE_D; halved when
# threatened (enemy seen within 14 in the last 40 rounds, ally died in the last 100, HP < 60%).
BANK_ANY = 30
BANK_NEAR = 15
BANK_NEAR_D = 15
BANK_CLOSE = 5
BANK_CLOSE_D = 4
BANK_LATE_ROUND = 1900
ALTAR_DANGER_PEN = 12
# Measure "altar within N" as the detour (me -> altar -> next target minus me -> target)
# rather than the raw path distance, so we bank when the altar is on the way.
BANK_DETOUR = True
BANK_DETOUR_NEAR_D = 8
BANK_DETOUR_CLOSE_D = 3
# Census rule counts any enemy seen within 14 as "threatened"; True = only sightings where the
# fight model would not engage (we are not the stronger side).
BANK_THREAT_LOSING_ONLY = False

# sf_bank: kill-time-ratio fight/flee model (INSIGHTS 2.8 / item 9).
# ratio = (time for us + allies to kill the target) / (time for nearby enemies + camps to kill us)
FIGHT_ENGAGE = 0.85        # engage when ratio <= this
FIGHT_ENGAGE_RICH = 0.7    # ... when we carry >= FIGHT_RICH_GEMS gems
FIGHT_RICH_GEMS = 30
FIGHT_CARRIER_BONUS = 0.15  # added when the target carries >= 15 gems
FIGHT_FLEE = 1.6           # clearly losing above this (1.0 when carrying >= FIGHT_RICH_GEMS)
RECALL_SAFE_MARGIN = 4     # recall only if every visible enemy is beyond its range + this
# Stall breaker: retreating from enemies we are not clearly losing to, turn after turn (e.g. a
# passive enemy group parked on the only altar), stops once self.stall exceeds STALL_LIMIT.
STALL_DECAY = 0.98
STALL_LIMIT = 25.0
# Chase guard: an enemy we "engage" for CHASE_MAX turns without landing a basic attack
# (unreachable, e.g. parked on blocked tiles) is ignored for CHASE_BAN rounds.
CHASE_MAX = 6
CHASE_BAN = 40
# sf_bank: camp safety. A group we died at is down-weighted for DEATH_MEMORY rounds.
DEATH_MEMORY = 250
DEATH_PENALTY = 0.3

# sf_draft: Bruiser builds on the main stat (INSIGHTS 2.2): (stat, weight) per champion.
_CT = cambc.ChampionType
BRUISER_ITEMS = {
    "S": (Item.BRUISER_SHARD_OF_STRENGTH, Item.BRUISER_EMBLEM_OF_STRENGTH),
    "H": (Item.BRUISER_SHARD_OF_HEALTH, Item.BRUISER_EMBLEM_OF_HEALTH),
    "F": (Item.BRUISER_SHARD_OF_FOCUS, Item.BRUISER_EMBLEM_OF_FOCUS),
}
BRUISER_PLAN = {
    int(_CT.VESPER_VALE): (("S", 2.0), ("H", 1.0)),
    int(_CT.VENDETTA): (("S", 2.0), ("H", 1.0)),
    int(_CT.TAVI): (("S", 2.0), ("H", 1.0)),
    int(_CT.HEART_OF_RUIN): (("H", 1.0), ("F", 1.0)),
    int(_CT.RYTH): (("H", 2.0), ("S", 1.0)),
    int(_CT.MARCELLA): (("F", 1.0), ("H", 1.0), ("S", 1.0)),
}
ITEMS_BRUISER = True
JUNGLE_FIRST = False
# sf_draft kit usage switches (each independent).
KIT_LANDING_DASH = True    # HoR: dash landing (1.5xF, radius 1, stun) onto camps/enemies
KIT_AOE_AIM = True         # Ryth (and other ground AoE): aim at the tile hitting most units
KIT_RESET_RETARGET = True  # attack reset only with a live target; retarget if the first died

# ---- h_teamclear (STRATEGIES Q26): team bootstrap for camp groups no champion can clear alone.
# tb_merge_b's camp-safety check only counts allies that already claim a group (c), so a group
# every champion rejects at c=0 is never claimed and never cleared (02gift-wrapping: 0 clears,
# 0 monster damage all game; ladder 0-1028 and 16-1006).  (1) TEAM_CLEAR: when the solo check
# fails, find the smallest team k (me + claimers + idle alive allies) for which the same direct
# check passes with k-1 allies hitting, and score the group per champion (value / k).
# (2) TEAM_MUSTER: before waking such a group, wait on a ring outside its range until enough
# champions stand near it (sleeping camps neither wake nor heal); a muster that does not fill
# bans the group for a while.  (3) TEAM_NEAR_DANGER: in a team fight the flee check uses the
# nearest-champion camp model (a camp hits only the nearest champion), as in sf_maps.
TEAM_CLEAR = True
TEAM_MUSTER = True
TEAM_NEAR_DANGER = False
# Tank capacity: camps focus the nearest champion, who flees at about s*(rng+1)+60 HP, so a team
# of k absorbs at most k*(maxhp - s*(rng+1) - 80) before everyone has fled (the hit-and-run
# budget).  The team check needs the group's damage s*ttk*share to fit in that too (excludes
# the 160-strength 2-elk+2-wolf groups: 3 camp deaths and no clear in the first test).
TEAM_TANK_CHECK = True
# Wrapped groups (a ring of camps around a wall tile) hide camps behind the wall.  TEAM_WRAP_FIX:
# (a) once the target group is awake, its unseen, believed-alive camps count as awake threats in
#     range (Vendetta died at 360 HP to an elk she could not see, with incoming=20);
# (b) "no alive camp visible within 3 of the centre -> respawning" only when every believed-alive
#     camp tile is in view (champions idled for 1,960 rounds beside a live wolf behind the wall);
# (c) standing on a dead camp's tile of the target group is allowed while that group is alive (it
#     cannot respawn until the whole group is cleared), so the path round the wall is walkable.
TEAM_WRAP_FIX = True
TEAM_DEBUG = True
TEAM_MAX_STR = 250        # structure gate: never team-assault a group stronger than this,
TEAM_MAX_HP = 15000       # with this much total HP, or containing a monolith (boss groups)
TEAM_MUSTER_COST = 10.0   # rounds added to a team option's cost for gathering
TEAM_COMMIT_WAIT = 15     # rounds at the ring with too few allies claiming the group -> ban it
TEAM_MUSTER_WAIT = 30     # rounds at the ring without enough allies near -> ban it (v1: 60)
TEAM_BAN = 150
DEAD_MARK = 255           # claim byte of a dead champion (not idle, not a claim)
# Shared byte 6 (free in tb_merge_b): bit s set = the champion in slot s stands within its claimed
# group's range + 4.  The muster counts these present claimers as well as the allies it can see
# (v1 screen, 02harvest: a weak champion waited 60-170 rounds at a ring while stronger claimers
# fought the same group out of its vision).
PRESENT_BYTE = 6


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
                 "rng", "n", "status", "ready", "hp", "value", "boss", "ring", "zone")

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
        # h_teamclear structure gate (boss groups: monolith, or too strong / too much HP)
        boss = self.strength > TEAM_MAX_STR or sum(self.maxhp.values()) >= TEAM_MAX_HP
        if not boss:
            for c, p, st, r in self.camps:
                try:
                    if c.is_monolith():
                        boss = True
                        break
                except Exception:
                    pass
        self.boss = boss
        self.ring = None   # muster ring / zone bitboards, built on first use
        self.zone = None

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
        self.sfields = {}   # static distance fields: group idx -> field rooted at its centre, -1 -> altar ring,
                            # -2-i -> ring of altar_goals[i] (tb_merge_b, for sf_bank's pick_altar)
        self.sf_todo = []   # keys still to build (until empty, a per-turn field is used instead)
        self.sf_use = False  # this turn may use sfields (False only if we stand on a walk_block tile)
        self.reach_memo = {}  # (group idx, id(comp), has crystal or 10 gold) -> can_reach result
        self.stuck = 0        # consecutive no-progress farming turns on group stuck_idx
        self.stuck_idx = -1
        self.banned = {}      # group idx -> round until which choose_target skips it
        # sf_bank alert state
        self.last_enemy_near = -BIG
        self.last_enemy_danger = -BIG
        self.last_ally_death = -BIG
        self.altar_seen = {}
        self.ally_alive = {}
        self.pref_altar = None
        self.escape_cache = {}
        self.died_at = {}
        self.was_dead = False
        self.stall = 0.0
        self.holding = False
        self.chase_turns = {}
        self.chase_ban = {}
        self.enemy_handles = []
        self.enemy_locked = set()
        self.far_enemies = []
        self.lock_side = []
        # h_teamclear state
        self.n_bodies = 1
        self.idle_allies = 0      # alive allies whose claim byte is 0 (set by read_claims)
        self.last_claims = {}
        self.team_need = 0        # champions needed near the current target before waking it
        self.muster_idx = -1
        self.muster_since = 0
        self.muster_last = -BIG
        self.hidden_hp = None
        self.present = False
        self.claim_buf = None

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
        self.spawn_pts = self.spawn.positions()
        self.altar_goals = []
        for a in self.altars:
            r1 = Bitboard()
            r1.draw_chebyshev(a, 1)
            self.altar_goals.append((a, r1 & ~self.walk_block))
        self.groups = [Group(i, g) for i, g in enumerate(game_map.camp_groups())]
        self.all_camp_tiles = Bitboard()
        for G in self.groups:
            self.all_camp_tiles |= G.tiles
        self.area = game_map.width() * game_map.height()
        handles = sorted(int(c) for c in cambc.champions(Team.ALLY))
        self.n_bodies = len(handles)
        try:
            self.slot = handles.index(int(me))
        except ValueError:
            self.slot = 0
        self.slot = min(self.slot, 7)
        try:
            self.enemy_handles = sorted(int(c) for c in cambc.champions(Team.ENEMY))
            self.enemy_spawn = game_map.spawn_region(Team.ENEMY).positions()[0]
            self.lock_side = [a for a in self.altars if cheb(a, self.enemy_spawn)
                              <= cheb(a, self.spawn.positions()[0]) + LOCK_SIDE_MARGIN]
        except Exception:
            self.enemy_spawn = Vec2(game_map.width() // 2, game_map.height() // 2)
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
                                               key=lambda G: cheb(G.center, sp0))] + \
            [-2 - i for i in range(len(self.altar_goals))]
        # tb_merge_b: per-altar ring fields (-2-i) replace sf_fuel's whole-ring field (-1);
        # sf_bank's pick_altar needs the distance to each altar, altar_distance() is unused
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
        idle = 0
        self.claim_buf = buf
        for s in range(PRESENT_BYTE):
            if s == self.slot:
                continue
            v = buf[s]
            if v == DEAD_MARK:
                continue  # h_teamclear: dead ally
            if v:
                claims[v - 1] = claims.get(v - 1, 0) + 1
            elif s < self.n_bodies:
                idle += 1
        self.idle_allies = idle
        self.last_claims = claims
        return claims

    def write_dead(self):
        """h_teamclear: mark this slot dead so allies do not count it as available."""
        self.set_present(False)
        try:
            cambc.shared_memory.write(self.slot, bytes([DEAD_MARK]))
        except Exception:
            pass

    def set_present(self, flag):
        """h_teamclear: publish whether I stand near my claimed group (bit slot of byte 6)."""
        if flag == self.present:
            return
        self.present = flag
        try:
            m = cambc.shared_memory[PRESENT_BYTE]
            bit = 1 << self.slot
            cambc.shared_memory[PRESENT_BYTE] = (m | bit) if flag else (m & ~bit & 0xFF)
        except Exception:
            pass

    def group_zone(self, G):
        if G.zone is None:
            G.zone = dilate(G.tiles, G.rng + 4)
        return G.zone

    def write_claim(self, idx):
        try:
            v = 0 if idx is None or idx >= DEAD_MARK - 1 else idx + 1
            if v == 0 and TEAM_CLEAR:
                self.set_present(False)
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
        self.hidden_hp = None
        G = self.target
        if TEAM_WRAP_FIX and G is not None and G.status == 0 and awake:
            # h_teamclear: the target group is awake (a group wakes as a whole) -> its unseen,
            # believed-alive camps are awake too and hit us if we are in their range
            seen = None
            for c, cp, r, s in awake:
                if cp in G.hp:
                    seen = set(t[1] for t in awake)
                    break
            if seen is not None:
                for c, p, st, r in G.camps:
                    if st <= 0 or p in seen or G.hp.get(p, 0) <= 0:
                        continue
                    try:
                        if c.is_visible():
                            continue
                    except Exception:
                        pass
                    awake.append((c, p, r, st))
                    if self.hidden_hp is None:
                        self.hidden_hp = {}
                    self.hidden_hp[p] = G.hp.get(p, 0)
                    if cheb(p, pos) <= r:
                        inc += st
        enemies = []
        self.far_enemies = []
        for e in cambc.vision.champions(Team.ENEMY):
            try:
                if not e.is_alive():
                    continue
                ep = e.position()
                if cheb(ep, pos) > ENEMY_SIGHT:
                    self.far_enemies.append(e)  # seen via our ward only
                    continue
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
            if key <= -2:
                roots |= self.altar_goals[-2 - key][1]
            elif key < 0:
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
            if key <= -2:
                dests |= self.altar_goals[-2 - key][1]
            elif key < 0:
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
        self.buy_lock(me)
        for _ in range(12):
            try:
                counts = me.item_count()
                item = self.bruiser_item(me, counts)
                if item is not None:
                    pass
                elif counts[int(Item.JUNGLE_EMBLEM_OF_STRENGTH)] == 0:
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

    def bruiser_item(self, me, counts):
        """sf_draft: Bruiser shards of the champion's main stat (INSIGHTS item 5).

        Finishes a partly bought emblem first, then buys the stat whose shard
        total is lowest relative to its weight.  None = use the default build.
        """
        try:
            plan = BRUISER_PLAN.get(int(me.champion_name()))
        except Exception:
            plan = None
        if not plan or not ITEMS_BRUISER:
            return None
        if JUNGLE_FIRST and counts[int(Item.JUNGLE_EMBLEM_OF_STRENGTH)] == 0:
            return Item.JUNGLE_SHARD_OF_STRENGTH
        best = None
        best_key = None
        for i, (stat, w) in enumerate(plan):
            shard, emblem = BRUISER_ITEMS[stat]
            part = counts[int(shard)]
            if part % 5:
                return shard
            key = ((part + 5 * counts[int(emblem)]) / w, i)
            if best_key is None or key < best_key:
                best_key = key
                best = shard
        return best

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
                elif KIT_LANDING_DASH and ab.is_dash() and ab.info().modifier > 0:
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
        if KIT_LANDING_DASH and (target is not None or incoming > 0):
            if self.cast_landing_dash(me, target):
                return
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
                        if KIT_AOE_AIM:
                            tp = self.aim_area(me, pos, info.range, info.radius, tp)
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
            if KIT_RESET_RETARGET:
                self.reset_and_hit(me, abilities, target)
                return
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

    # ------------------------------------------------- sf_draft kit helpers
    def kit_units(self):
        """(position, weight) of units an area hit would touch: awake camps and
        camps of the current target group +1, enemy champions +2 (+4 while
        channelling), sleeping camps of other groups -3 (do not wake them)."""
        units = []
        tg = self.target.tiles if self.target is not None else None
        try:
            for c in cambc.vision.camps():
                try:
                    if c.is_dead():
                        continue
                    if c.is_awake() or (tg is not None and tg.is_set(c.spawn_position())):
                        w = 1.0
                    else:
                        w = -3.0
                    units.append((c.position(), w))
                except Exception:
                    pass
            for e in cambc.vision.champions(Team.ENEMY):
                try:
                    if not e.is_alive():
                        continue
                    w = 2.0
                    if e.is_recalling() or e.is_submitting_gems() or e.is_teleporting():
                        w = 4.0
                    units.append((e.position(), w))
                except Exception:
                    pass
        except Exception:
            pass
        return units

    def best_area_tile(self, cands, units, radius, bonus_pos=None):
        best = None
        bs = 0.0
        for t in cands.positions():
            sc = 0.0
            for p, w in units:
                if cheb(p, t) <= radius:
                    sc += w
            if bonus_pos is not None and cheb(bonus_pos, t) <= 1:
                sc += 0.5
            if sc > bs:
                bs = sc
                best = t
        return best, bs

    def aim_area(self, me, pos, rng, radius, fallback):
        """Ground AoE (Ryth stun): the tile in cast range hitting the most units."""
        try:
            units = self.kit_units()
            pos_bb = Bitboard()
            for p, w in units:
                if w > 0:
                    pos_bb.set(p)
            if pos_bb.is_empty():
                return fallback
            near = Bitboard()
            near.draw_chebyshev(pos, rng)
            cands = dilate(pos_bb, radius) & near
            best, bs = self.best_area_tile(cands, units, radius)
            if best is not None:
                return best
        except Exception:
            pass
        return fallback

    def cast_landing_dash(self, me, target):
        """HoR slot 1: dash landing 1.5xF in radius 1 + stun, aimed at the most units."""
        try:
            dash = None
            for ab in me.abilities():
                if ab.is_dash() and ab.is_ready():
                    info = ab.info()
                    if info.radius > 0 and info.modifier > 0:
                        dash = ab
                    break
            if dash is None:
                return False
            if me.health() < me.max_health() * 0.35:
                return False
            pos = me.position()
            units = self.kit_units()
            pos_bb = Bitboard()
            for p, w in units:
                if w > 0:
                    pos_bb.set(p)
            if pos_bb.is_empty():
                return False
            near = Bitboard()
            near.draw_chebyshev(pos, 2)
            cands = dilate(pos_bb, info.radius) & near & ~self.blocked_now(me) & ~self.walk_block
            cands.set(pos, False)
            tpos = None
            try:
                if target is not None and target.is_visible():
                    tpos = target.position()
            except Exception:
                tpos = None
            best, bs = self.best_area_tile(cands, units, info.radius, tpos)
            if best is None or bs < 1.0:
                return False
            if not dash.use(best):
                return False
            if me.can_attack():
                nxt = self.reset_target(me, target)
                if nxt is not None:
                    try:
                        me.attack(nxt)
                    except Exception:
                        pass
            return True
        except Exception:
            return False

    def reset_target(self, me, target):
        """A unit in basic-attack range worth hitting: the target if alive, else the
        weakest awake / target-group camp, else an enemy champion."""
        tiles = me.attack_tiles()
        try:
            if target is not None and target.is_visible() and target.health() > 0 \
                    and tiles.is_set(target.position()):
                return target
        except Exception:
            pass
        tg = self.target.tiles if self.target is not None else None
        best = None
        try:
            for e in cambc.vision.champions(Team.ENEMY):
                try:
                    if e.is_alive() and tiles.is_set(e.position()):
                        if best is None or e.health() < best.health():
                            best = e
                except Exception:
                    pass
            if best is not None:
                return best
            for c in cambc.vision.camps():
                try:
                    if c.is_dead() or not tiles.is_set(c.position()):
                        continue
                    if not (c.is_awake() or (tg is not None and tg.is_set(c.spawn_position()))):
                        continue
                    if best is None or c.health() < best.health():
                        best = c
                except Exception:
                    pass
        except Exception:
            pass
        return best

    def reset_and_hit(self, me, abilities, target):
        """Attack reset (Vendetta/Vesper/Ryth/Tavi/Marcella-enhanced) only when a live
        unit is in range; re-target if the first hit killed the target (Vendetta's
        kill refreshes her cooldowns, so the reset is usually ready again)."""
        for ab in abilities:
            try:
                if not (ab.is_attack_reset() and ab.is_ready()):
                    continue
                nxt = self.reset_target(me, target)
                if nxt is None:
                    return False
                if ab.use(None):
                    if me.can_attack():
                        me.attack(nxt)
                    return True
            except Exception:
                pass
        return False

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
        avail = 1 + self.idle_allies  # h_teamclear: me + idle alive allies (+ claimers per group)
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
            k_team = 0
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
                        cycles = BIG
                        if budget > 0:
                            per_cycle = budget / (s * dmg_mult) * tdps
                            cycles = hl / per_cycle
                        if cycles <= 4 and self.escape_ok(G, comp):
                            extra = cycles * 30.0
                        else:
                            # h_teamclear (1): no solo way in -> smallest team that makes the
                            # direct check pass, from the allies that are free to join
                            if not TEAM_CLEAR or G.boss:
                                continue
                            k_team = self.team_k(G, s, hl, dps, hp, maxhp, dmg_mult, c + 2, avail + c)
                            if not k_team:
                                continue
                            ttk = hl / (dps + 55.0 * (k_team - 1))
                            extra = TEAM_MUSTER_COST
            if rnd + d + ttk + 8 > MAX_ROUNDS:
                continue
            cost = d + ttk + 6 + extra + wait
            score = G.value / cost
            if k_team:
                score /= k_team  # per-champion share of a team clear
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
            if G.status != 1 and rnd - self.died_at.get(G.idx, -BIG) < DEATH_MEMORY:
                score *= DEATH_PENALTY
            if score > best_score or (score == best_score and best is not None and G.idx < best.idx):
                best_score = score
                best = G
                self.dbg_k = k_team
        if TEAM_DEBUG and best is not None and getattr(self, "dbg_k", 0):
            print("TEAMPICK r", rnd, "s", self.slot, "g", best.idx, "k", self.dbg_k, flush=True)
        self.dbg_k = 0
        self.team_need = self.muster_need(me, best, hp, maxhp, dps, dmg_mult, comp) \
            if TEAM_MUSTER and best is not None and best.status == 0 else 0
        if TEAM_DEBUG:
            print("TC r", rnd, "s", self.slot, "pos", pos, "hp", int(hp), "tgt",
                  None if best is None else (best.idx, best.status, int(best.hp_left())),
                  "need", self.team_need, "c", None if best is None else claims.get(best.idx, 0),
                  "idle", self.idle_allies, "sc", round(best_score, 3), flush=True)
        return best

    def team_k(self, G, s, hl, dps, hp, maxhp, dmg_mult, kmin, kmax):
        """h_teamclear: smallest team size k in [kmin, kmax] for which choose_target's direct
        camp-safety check passes with k-1 allies hitting (team dps = dps + 55(k-1), camp damage
        shared k ways) and, with TEAM_TANK_CHECK, the k champions' tank budgets cover the
        group's damage; 0 if none."""
        share = 1.0 if G.n == 1 else 0.7
        cap = hp - 150
        if TEAM_TANK_CHECK:
            cap = min(cap, maxhp - s * dmg_mult * (G.rng + 1) - 80)
        if cap <= 0:
            return 0
        for k in range(max(2, kmin), min(kmax, self.n_bodies) + 1):
            if s * (hl / (dps + 55.0 * (k - 1))) * share * dmg_mult / k <= cap:
                return k
        return 0

    def muster_need(self, me, G, hp, maxhp, dps, dmg_mult, comp):
        """h_teamclear (2): champions (me included) that must stand near a still-sleeping, full-HP
        group before it is woken: 0 when I could clear it alone (direct or hit-and-run with no
        allies), else the smallest team for which the direct check passes, independent of how
        many allies claim it now (so the 3rd joiner, whose check passes with c=2, still waits
        for the others instead of waking the group alone)."""
        if G.boss:
            return 0
        s = G.strength
        if s <= 0:
            return 0
        hl = sum(G.maxhp.values())
        if G.hp_left() < hl:
            return 0
        share = 1.0 if G.n == 1 else 0.7
        if s * (hl / dps) * share * dmg_mult <= hp - 150:
            return 0
        budget = maxhp - s * dmg_mult * (G.rng + 1) - 80
        if budget > 0 and hl / (budget / (s * dmg_mult) * dps) <= 4 and self.escape_ok(G, comp):
            return 0
        return self.team_k(G, s, hl, dps, hp, maxhp, dmg_mult, 2, self.n_bodies)

    def muster(self, me, G, rnd, awake):
        """h_teamclear (2) muster gate.  Before waking a group that needs a team, wait on a ring
        just outside its range until team_need champions (me included) stand near it.  Sleeping
        camps neither wake nor heal, so waiting only costs time.  Once at the ring, too few
        claimers for TEAM_COMMIT_WAIT rounds, or too few champions near for TEAM_MUSTER_WAIT
        rounds, bans the group for TEAM_BAN rounds.  Returns True if the turn was used."""
        if G.hp_left() < sum(G.maxhp.values()):
            return False
        for c, cp, r, s in awake:
            if cp in G.hp:
                return False  # already awake: fight
        if G.ring is None:
            G.ring = dilate(G.tiles, G.rng + 3) & ~dilate(G.tiles, G.rng) & ~self.walk_block \
                & ~self.all_camp_tiles
        if G.ring.is_empty():
            return False
        zone = self.group_zone(G)
        pos = me.position()
        near = 1
        try:
            for a in cambc.vision.champions(Team.ALLY):
                if int(a) != int(me) and a.is_alive() and zone.is_set(a.position()):
                    near += 1
        except Exception:
            pass
        buf = self.claim_buf
        if buf is not None and near < self.team_need:
            # claimers that report standing near G (seen or not)
            pm = buf[PRESENT_BYTE]
            near_sh = 1
            for s in range(PRESENT_BYTE):
                if s != self.slot and buf[s] == G.idx + 1 and (pm >> s) & 1:
                    near_sh += 1
            near = max(near, near_sh)
        if near >= self.team_need:
            return False
        if self.muster_idx != G.idx or rnd - self.muster_last > 10 or not zone.is_set(pos):
            self.muster_idx = G.idx
            self.muster_since = rnd  # the clock runs only while I wait near the group
        self.muster_last = rnd
        waited = rnd - self.muster_since
        committed = 1 + self.last_claims.get(G.idx, 0)
        if waited >= TEAM_MUSTER_WAIT or (committed < self.team_need and waited >= TEAM_COMMIT_WAIT):
            self.banned[G.idx] = rnd + TEAM_BAN
            self.muster_idx = -1
            self.target = None
            self.write_claim(None)
            if TEAM_DEBUG:
                print("MUSTER-BAN r", rnd, "slot", self.slot, "g", G.idx, "near", near,
                      "committed", committed, "need", self.team_need, flush=True)
            return True
        print("MUSTER r", rnd, "s", self.slot, "g", G.idx, "near", near, "need", self.team_need,
              "committed", committed, "waited", waited, flush=True)
        if not G.ring.is_set(pos):
            self.go_to(me, G.ring)
        return True

    def nearest_incoming(self, me, awake):
        """h_teamclear (3), from sf_maps: an awake camp only hits the nearest champion."""
        pos = me.position()
        inc = 0.0
        champs = []
        try:
            for ch in cambc.vision.champions():
                try:
                    if int(ch) != int(me) and ch.is_alive():
                        champs.append(ch.position())
                except Exception:
                    pass
        except Exception:
            pass
        for c, cp, r, s in awake:
            d = cheb(cp, pos)
            if d > r:
                continue
            if any(cheb(cp, q) < d for q in champs):
                continue
            inc += s
        if self.jungle(me):
            inc *= 0.8
        return inc

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

    def escape_ok(self, G, comp):
        """Hit-and-run needs a walkable tile outside the group's range on the side we attack from
        (small islands inside an elk's range 4 were a repeated camp death)."""
        key = (G.idx, id(comp))
        v = self.escape_cache.get(key)
        if v is None:
            zone = Bitboard()
            for c, p, st, r in G.camps:
                if r > 0 and st > 0:
                    zone.draw_chebyshev(p, r)
            stand = dilate(G.tiles, 1) & ~self.walk_block & ~self.all_camp_tiles
            area = comp
            if (stand & comp).is_empty():
                area = self.comp_of(G.center)
            v = not (area & ~zone & ~self.all_camp_tiles).is_empty()
            self.escape_cache[key] = v
        return v

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

    # ------------------------------------------------------- sf_bank: banking
    def update_alerts(self, me, rnd, enemies):
        """Remember recent enemy sightings (near me / near each altar) and ally deaths."""
        if enemies:
            pos = me.position()
            for e in enemies:
                try:
                    ep = e.position()
                except Exception:
                    continue
                if cheb(ep, pos) <= 14:
                    self.last_enemy_near = rnd
                for a in self.altars:
                    if cheb(ep, a) <= 8:
                        self.altar_seen[a] = rnd
        try:
            for a in cambc.champions(Team.ALLY):
                h = int(a)
                alive = a.is_alive()
                if self.ally_alive.get(h, True) and not alive:
                    self.last_ally_death = rnd
                self.ally_alive[h] = alive
        except Exception:
            pass

    def threatened(self, rnd, hp, maxhp):
        seen = self.last_enemy_danger if BANK_THREAT_LOSING_ONLY else self.last_enemy_near
        return (rnd - seen <= 40 or rnd - self.last_ally_death <= 100
                or hp < maxhp * 0.6)

    def pick_altar(self, field, visited, rnd, pos=None):
        """Nearest usable altar by path (+penalty where enemies were seen recently).
        Returns (effective distance, goal tiles) or (BIG, None)."""
        best = BIG
        best_goals = None
        for i, (a, goals) in enumerate(self.altar_goals):
            try:
                if cambc.vision.has_altar_lock(a) and cambc.vision.altar_lock_at(a).is_enemy():
                    continue
            except Exception:
                pass
            d = BIG
            sf = self.sfields.get(-2 - i) if self.sf_use else None
            if sf is not None:
                # tb_merge_b: sf_fuel static field rooted at this altar's ring (exact, symmetric)
                v = sf.get(pos)
                if v < UNREACHED:
                    d = v
            elif visited is not None:
                for t in goals.positions():
                    if visited.is_set(t):
                        v = field.get(t)
                        if v < d:
                            d = v
            if d >= BIG:
                continue
            if rnd - self.altar_seen.get(a, -BIG) <= 40:
                d += ALTAR_DANGER_PEN
            if d < best:
                best = d
                best_goals = goals
                self.pref_altar = a
        return best, best_goals

    def detour(self, ad, field, visited, G, pos=None):
        """Extra walking to bank on the way to group G (Chebyshev for the altar->G leg)."""
        a = self.pref_altar
        if a is None or G is None:
            return ad
        gd = self.group_dist(G, pos, field, visited)  # tb_merge_b: sf_fuel-safe distance
        if gd is None:
            return ad
        return max(0, ad + cheb(a, G.center) - gd)

    def bank_detour(self, gems, det, threatened):
        k = 0.5 if threatened else 1.0
        if det <= BANK_DETOUR_NEAR_D and gems >= BANK_NEAR * k:
            return True
        if det <= BANK_DETOUR_CLOSE_D and gems >= BANK_CLOSE * k:
            return True
        return False

    def bank_now(self, gems, ad, threatened):
        k = 0.5 if threatened else 1.0
        if gems >= BANK_ANY * k:
            return True
        if ad <= BANK_NEAR_D and gems >= BANK_NEAR * k:
            return True
        if ad <= BANK_CLOSE_D and gems >= BANK_CLOSE * k:
            return True
        return False

    def do_tribute(self, me, pref=None):
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
        ring = self.altar_ring
        locked = self.locked_altars()
        if locked:
            free = Bitboard()
            for a in self.altars:
                if a not in locked:
                    free.draw_chebyshev(a, 1)
            free &= ~self.walk_block
            reach_free = not (free & self.comp_of(pos)).is_empty()
            if self.break_lock(me, locked, not reach_free):
                return True
            if reach_free:
                ring = free
        # sf_bank: preferred altar (pick_altar already skips enemy-locked ones)
        if pref is not None and not (pref & ~self.blocked_now(me)).is_empty():
            ring = pref
        goals = ring & ~self.blocked_now(me)
        if goals.is_empty():
            goals = ring
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
        epos = []
        for e in enemies:
            try:
                epos.append(e.position())
            except Exception:
                pass
        spawn_pts = self.spawn_pts

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
            # sf_bank: then away from enemies, then toward our spawn (heals at turn end)
            emd = min(epos and [min(cheb(ep, t), 8) for ep in epos] or [8])
            return (d, -md, -emd, min(cheb(p, t) for p in spawn_pts))

        cands = [pos] + [t for t in blocked.reachable_tiles(pos, 1).positions() if t != pos]
        dash = self.dash_ability(me)
        if dash is not None:
            near = Bitboard()
            near.draw_chebyshev(pos, 2)
            far = near & ~blocked & ~self.walk_block
            dcands = sorted(far.positions(), key=danger)
            if dcands and danger(dcands[0])[:3] < danger(pos)[:3]:
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

    # ------------------------------------------------- sf_bank: fight / flee
    def enemy_dps(self, e):
        try:
            return e.strength() + 0.15 * e.focus()
        except Exception:
            return 50.0

    def champ_dps(self, me):
        """Our damage per round against champions (no Monster bonus)."""
        d = me.strength()
        for ab in me.abilities():
            try:
                if ab.is_attack_reset():
                    d += me.strength() / 8.0
                elif ab.is_damage() or ab.is_cc() or ab.is_aoe_damage():
                    d += ab.damage_amount() / 8.0
            except Exception:
                pass
        return max(1.0, d)

    def recall_safe(self, me, enemies):
        """True when no visible enemy could reach us during a recall channel."""
        pos = me.position()
        for e in enemies:
            try:
                if cheb(e.position(), pos) <= e.attack_range() + RECALL_SAFE_MARGIN:
                    return False
            except Exception:
                pass
        return True

    def adjacent_melee(self, me, enemies):
        """Lowest-HP adjacent melee enemy we can hit right now (running only gives it free hits)."""
        if not me.can_attack():
            return None
        pos = me.position()
        tiles = me.attack_tiles()
        best = None
        for e in enemies:
            try:
                ep = e.position()
                if e.attack_range() <= 1 and cheb(ep, pos) <= 1 and tiles.is_set(ep):
                    if best is None or e.health() < best.health():
                        best = e
            except Exception:
                pass
        return best

    def strike(self, me, target, incoming):
        """Stand and hit target (attack + one combat cast)."""
        attacked = False
        try:
            if me.can_attack() and me.attack_tiles().is_set(target.position()):
                me.attack(target)
                attacked = True
        except Exception:
            pass
        self.cast_combat(me, target, False, incoming, attacked)
        return True

    def handle_enemies(self, me, enemies, awake, incoming, hp, maxhp):
        """Chase and kill weaker enemy champions nearby; step away from stronger ones.

        tb_merge_b: sf_bank's kill-time fight/flee model decides engage/retreat; sf_pvp's
        focus_bias (channel / team focus / carried gems) raises the engage limit and orders
        targets, and CHAN_THREAT discounts channelling enemies' damage."""
        pos = me.position()
        my_str = self.champ_dps(me)
        near = []
        threat = 0.0
        fight_dps = 0.0
        focus = self.read_focus()
        for e in enemies:
            try:
                d = cheb(e.position(), pos)
                cw = CHAN_THREAT[self.chan_kind(e)]
                if d <= 6 or (d <= 8 and int(e) == focus):
                    near.append((e, d))
                    fight_dps += self.enemy_dps(e) * cw
                if d <= e.attack_range() + 2:
                    threat += e.strength() * cw
            except Exception:
                pass
        if not near:
            return False
        camp_inc = 0.0
        for c, cp, r, s in awake:
            if cheb(cp, pos) <= r:
                camp_inc += s
        ally_str = 0.0
        n_allies = 0
        for a in cambc.vision.champions(Team.ALLY):
            try:
                if int(a) != int(me) and a.is_alive() and cheb(a.position(), pos) <= 6:
                    n_allies += 1
                    if cheb(a.position(), pos) <= 4:
                        ally_str += a.strength() * 0.7
            except Exception:
                pass
        gems = me.gem_count()
        rich = gems >= FIGHT_RICH_GEMS
        their_ttk = hp / max(1.0, max(threat, fight_dps) + camp_inc)
        best = None
        best_key = None
        best_ratio = BIG
        best_ttk = 0.0
        rnd = cambc.round_number()
        for e, d in near:
            try:
                eh = e.health()
                kill = eh / (my_str + ally_str)
                my_ttk = kill + max(0, d - me.attack_range()) * 0.5
                ratio = my_ttk / max(0.1, their_ttk)
                best_ratio = min(best_ratio, kill / max(0.1, their_ttk))
                limit = FIGHT_ENGAGE_RICH if rich else FIGHT_ENGAGE
                # sf_pvp bias on top of sf_bank's limit (0.8 is focus_bias's neutral ratio);
                # the carried-gem part subsumes sf_bank's FIGHT_CARRIER_BONUS
                pr, tier, eg = self.focus_bias(e, focus, gems)
                bonus = max(0.0, pr - 0.8)
                if eg >= 15:
                    bonus = max(bonus, FIGHT_CARRIER_BONUS)
                limit += bonus
                if self.chase_ban.get(int(e), -BIG) > rnd:
                    continue
                if ratio <= limit or eh <= my_str and d <= me.attack_range():
                    key = (tier, my_ttk / (1.0 + eg / 20.0), d)
                    if best_key is None or key < best_key:
                        best_key = key
                        best = e
                        best_ttk = kill + max(0, d - me.attack_range())
            except Exception:
                pass
        clearly_losing = (best_ratio > (1.0 if rich else FIGHT_FLEE)
                          or len(near) > n_allies + 1)
        if best is None:
            self.last_enemy_danger = rnd
        if best is not None:
            self.write_focus(best)
            moved = self.stun_channel(me, best, best_ttk)
            try:
                best.position()
            except Exception:
                return True  # the stun killed the target or it left vision: this turn is spent
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
            h = int(best)
            if attacked:
                self.chase_turns[h] = 0
            else:
                self.chase_turns[h] = self.chase_turns.get(h, 0) + 1
                if self.chase_turns[h] > CHASE_MAX:
                    self.chase_turns[h] = 0
                    self.chase_ban[h] = cambc.round_number() + CHASE_BAN
            return True
        # never turn our back on an adjacent melee enemy we can hit (it follows and hits anyway),
        # unless clearly losing and a dash or our spawn (full heal) offers a real escape
        adj = self.adjacent_melee(me, [e for e, d in near])
        if adj is not None:
            escape = self.dash_ability(me) is not None or \
                min(cheb(p, pos) for p in self.spawn.positions()) <= 2
            if not (clearly_losing and escape):
                return self.strike(me, adj, incoming)
        # stall breaker: when we keep backing off from enemies we are not clearly losing to,
        # hold our ground (carry on farming / banking) instead
        if self.stall > STALL_LIMIT:
            self.holding = True
        elif self.stall < STALL_LIMIT * 0.4:
            self.holding = False
        if not clearly_losing and self.holding:
            return False
        # unfavourable: if they can hit us (or we are clearly losing), step away
        # (and recall only once out of reach)
        if threat > 0 or (clearly_losing and (len(near) > n_allies + 1 or rich)):
            if not clearly_losing:
                self.stall += 1.0
            if hp < maxhp * 0.5 and incoming == 0 and not self.spawn.is_set(pos) \
                    and self.recall_safe(me, enemies):
                try:
                    me.recall()
                    return True
                except Exception:
                    pass
            self.retreat(me, awake, [e for e, d in near])
            return True
        return False

    # --------------------------------------------- sf_pvp: focus, locks, wards
    def chan_kind(self, e):
        """0 none, 1 tribute, 2 teleport, 3 recall (a stun cancels all three)."""
        try:
            if e.is_submitting_gems():
                return 1
            if e.is_teleporting():
                return 2
            if e.is_recalling():
                return 3
        except Exception:
            pass
        return 0

    def focus_bias(self, e, focus, my_gems):
        """(engage ratio, priority tier, enemy gems): channellers, then team focus, then rest."""
        ch = self.chan_kind(e)
        try:
            eg = e.gem_count()
        except Exception:
            eg = 0
        ratio = 0.8
        tier = 2
        if ch == 1 or ch == 2:
            ratio, tier = 1.2, 0
        elif ch == 3:
            ratio, tier = 1.0, 0
        ratio += min(0.3, eg / 100.0)
        if focus is not None and int(e) == focus:
            ratio += 0.2
            tier = min(tier, 1)
        if my_gems >= 30 and ch == 0:
            ratio = min(ratio, 0.8)
        return ratio, tier, eg

    def read_focus(self):
        try:
            v = cambc.shared_memory[FOCUS_BYTE]
        except Exception:
            return None
        if not v or (cambc.round_number() - (v & 31)) % 32 > FOCUS_TTL:
            return None
        i = (v >> 5) - 1
        if 0 <= i < len(self.enemy_handles):
            return self.enemy_handles[i]
        return None

    def write_focus(self, e):
        try:
            i = self.enemy_handles.index(int(e))
        except ValueError:
            return
        if i < 7:
            try:
                cambc.shared_memory[FOCUS_BYTE] = ((i + 1) << 5) | (cambc.round_number() & 31)
            except Exception:
                pass

    def stun_channel(self, me, e, ttk):
        """Stun a channelling enemy (not Marcella) before moving when we cannot kill it first."""
        ch = self.chan_kind(e)
        if ch == 0:
            return False
        try:
            if e.champion_name() == cambc.ChampionType.MARCELLA:
                return False
            tp = e.position()
        except Exception:
            return False
        pos = me.position()
        if ch == 3 and me.can_attack() and me.attack_tiles().is_set(tp):
            return False  # damage alone cancels a recall
        if ch != 3:
            try:
                left = e.remaining_channel_time()
            except Exception:
                left = 1
            if ttk < left:
                return False  # keep it channelling and take the bag
        for ab in me.abilities():
            try:
                if not ab.is_ready():
                    continue
                info = ab.info()
                if ab.is_cc():
                    if cheb(tp, pos) <= info.range and ab.use(e):
                        return True
                elif ab.is_aoe_damage() and info.duration > 0:
                    if cheb(tp, pos) <= info.range and ab.use(tp):
                        return True
                elif ab.is_dash() and info.duration > 0 and info.radius >= 1:
                    land = Bitboard()
                    land.draw_chebyshev(tp, int(info.radius))
                    reach = Bitboard()
                    reach.draw_chebyshev(pos, int(info.range))
                    for t in (land & reach & ~self.blocked_now(me)).positions():
                        if ab.use(t):
                            return True
            except Exception:
                pass
        return False

    def buy_lock(self, me):
        try:
            if me.consumables()[int(Cons.ALTAR_LOCK)].count() == 0 and \
                    me.gold_count() >= LOCK_MIN_GOLD and me.can_buy(Cons.ALTAR_LOCK):
                me.buy(Cons.ALTAR_LOCK)
        except Exception:
            pass

    def try_lock(self, me, enemies):
        """Lock an altar within 2 where a visible enemy is tributing (cancels its channel)."""
        try:
            lock = me.consumables()[int(Cons.ALTAR_LOCK)]
            if lock.count() == 0:
                return False
        except Exception:
            return False
        pos = me.position()
        for e in enemies:
            try:
                if not e.is_submitting_gems():
                    continue
                ep = e.position()
            except Exception:
                continue
            for a in self.altars:
                if cheb(a, ep) <= 1 and cheb(a, pos) <= 2:
                    try:
                        if cambc.vision.has_altar_lock(a):
                            continue
                        if lock.use(a):
                            if DEBUG:
                                print("LOCK", cambc.round_number(), a, flush=True)
                            return True
                    except Exception:
                        pass
        # proactive: deny an enemy-side altar we pass by (our team can still tribute there)
        for a in self.lock_side:
            if cheb(a, pos) <= 2:
                try:
                    if cambc.vision.has_altar_lock(a):
                        continue
                    if lock.use(a):
                        return True
                except Exception:
                    pass
        return False

    def locked_altars(self):
        """Altars last seen with an enemy lock (remembered while out of sight)."""
        for a in self.altars:
            try:
                if not cambc.vision.in_vision(a):
                    continue
                if cambc.vision.has_altar_lock(a) and cambc.vision.altar_lock_at(a).is_enemy():
                    self.enemy_locked.add(a)
                else:
                    self.enemy_locked.discard(a)
            except Exception:
                pass
        return self.enemy_locked

    def break_lock(self, me, locked, force):
        """Hit an adjacent enemy lock when no free altar is close; True if we attacked."""
        pos = me.position()
        free_d = min([cheb(a, pos) for a in self.altars if a not in locked] or [BIG])
        if (free_d <= 8 and not force) or not me.can_attack():
            return False
        tiles = me.attack_tiles()
        for a in locked:
            try:
                if tiles.is_set(a) and cambc.vision.has_altar_lock(a):
                    me.attack(cambc.vision.altar_lock_at(a))
                    return True
            except Exception:
                pass
        return False

    def try_ward(self, me):
        """Place the ward whenever it is charged: by the altar when banking, else ahead."""
        try:
            if not USE_WARDS or me.ward_cooldown() > 0:
                return False
            wp = me.ward_positions()
        except Exception:
            return False
        pos = me.position()
        alt = None
        ad = BIG
        for a in self.altars:
            d = cheb(a, pos)
            if d < ad:
                ad, alt = d, a
        if alt is not None and ad <= 4:
            anchor = alt
            if wp and cheb(wp[0], alt) <= 2:
                return False
        else:
            if wp and cheb(wp[0], pos) <= 6:
                return False
            anchor = self.enemy_spawn
        area = Bitboard()
        area.draw_chebyshev(pos, 2)
        bad = (game_map.walls() | game_map.holes() | game_map.altars() | cambc.vision.ward_tiles()
               | cambc.vision.champion_tiles() | cambc.vision.camp_tiles())
        bad.set(pos, False)
        bush = game_map.bushes()
        cands = sorted((area & ~bad).positions(),
                       key=lambda t: (cheb(t, anchor), 0 if bush.is_set(t) else 1))
        for t in cands[:3]:
            try:
                if me.place_ward(t):
                    return True
            except Exception:
                pass
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
            if not self.was_dead and self.target is not None:
                self.died_at[self.target.idx] = rnd
            self.was_dead = True
            if TEAM_CLEAR:
                self.write_dead()
            else:
                self.write_claim(None)
            self.update_alerts(me, rnd, ())
            try:
                self.shop(me)
            except Exception:
                pass
            return
        if self.was_dead and TEAM_CLEAR:
            self.write_claim(None)  # clear the dead mark
        self.was_dead = False
        self.observe(me, rnd)
        if me.is_recalling() or me.is_submitting_gems() or me.is_teleporting():
            return
        self.try_ward(me)
        pos = me.position()
        at_spawn = self.spawn.is_set(pos)
        if at_spawn:
            self.shop(me)

        incoming, awake, enemies = self.threats(me)
        self.try_lock(me, enemies)
        hp = me.health()
        maxhp = me.max_health()
        self.update_alerts(me, rnd, enemies)
        self.stall *= STALL_DECAY

        # Heal up fully on spawn before leaving.
        if at_spawn and hp < maxhp * 0.92 and incoming == 0:
            return

        # ---- danger handling: never die to camps
        if TEAM_NEAR_DANGER and incoming > 0 and not enemies and self.target is not None \
                and self.last_claims.get(self.target.idx, 0) > 0:
            # h_teamclear (3): in a team fight a camp only hits the nearest champion
            incoming = self.nearest_incoming(me, awake)
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
                        if self.hidden_hp:
                            hit_hp += self.hidden_hp.get(cp, 0)
            finish_turns = hit_hp / self.dps(me) + 1
            safe_finish = finish_turns * incoming < hp - 60 and not enemies
            if TEAM_DEBUG:
                print("TCD r", rnd, "s", self.slot, "pos", pos, "hp", int(hp), "inc", incoming,
                      "steps", steps, "hit_hp", int(hit_hp), "safe", safe_finish, flush=True)
            if not safe_finish and hp <= incoming * (steps + 1) + 60:
                # sf_bank: an adjacent melee enemy that dies to our next hit is finished, not fled
                adj = self.adjacent_melee(me, enemies) if enemies else None
                if adj is not None and adj.health() <= me.strength():
                    self.strike(me, adj, incoming)
                    return
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
            if (low or rich) and spawn_d > 6 and self.recall_safe(me, enemies):
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
        pref = None
        if gems > 0:
            self.pref_altar = None
            ad, pref = self.pick_altar(field, visited, rnd, pos)
            if ad >= BIG:
                ad = 40
            total = cambc.global_submitted_gems(Team.ALLY) + gems
            thr = self.threatened(rnd, hp, maxhp)
            go = (rnd + ad + gems // 10 + 12 >= MAX_ROUNDS or total >= 1000 or rnd >= BANK_LATE_ROUND
                  or self.bank_now(gems, BIG if BANK_DETOUR else ad, thr))
            if not go:
                tgt = self.choose_target(me, rnd, field, visited, comp)
                chosen = True
                if tgt is None:
                    go = True
                elif BANK_DETOUR:
                    go = self.bank_detour(gems, self.detour(ad, field, visited, tgt, pos), thr)
            if go:
                self.write_claim(None)
                self.do_tribute(me, pref)
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
        if TEAM_CLEAR and G is not None:
            self.set_present(G.status == 0 and self.group_zone(G).is_set(pos))
        if G is None:
            if gems > 0:
                self.do_tribute(me, pref)
            elif not at_spawn and (me.gold_count() >= 60 or hp < maxhp * 0.7):
                try:
                    me.recall()
                except Exception:
                    pass
            return

        if G.status != 1 and self.all_camp_tiles.is_set(pos) \
                and not (TEAM_WRAP_FIX and G.status == 0 and G.tiles.is_set(pos)):
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
            if not seen_alive and TEAM_WRAP_FIX:
                vis = cambc.vision.visible_tiles()
                for c, p, st, r in G.camps:
                    if G.hp.get(p, 0) > 0 and not vis.is_set(p):
                        seen_alive = True  # hidden (e.g. behind the group's wall), not proven dead
                        break
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

        # h_teamclear (2): gather before waking a group that needs a team
        if self.team_need > 1 and self.muster(me, G, rnd, awake):
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
