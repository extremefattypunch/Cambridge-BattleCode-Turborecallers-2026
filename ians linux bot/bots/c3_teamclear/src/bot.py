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
DIAG = False         # h_earlyfight: per-turn opening log (diagnostics only; False in tests)
DIAG_UNTIL = 320
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

# ---- q24_combo patch 3, from h_earlyfight_all (v3 = h_earlyfight v2 rule applied all game).
# h_earlyfight (STRATEGIES Q12): opening-phase group fight rule. Diag games vs sf_bank showed our
# early deaths are a lone (mostly non-dash melee) champion standing adjacent to an enemy melee while
# 2-5 enemies are within 6, and allies 3-6 tiles away not committing (each ally's own kill-time
# ratio is ~1.0 because it ignores that the enemy damage is split over our whole group).
# For rnd < EARLY_ROUNDS the local fight (me + allies within GROUP_R vs enemies within GROUP_R) is
# scored as (sum hp x sum dps) ours / theirs:
#  >= GROUP_ADV   -> commit: engage limit + GROUP_ENGAGE_BONUS, never "clearly losing", stand and trade
#  <= GROUP_DISADV -> regroup: engage only a kill-now target, no stand-and-trade unless it dies in
#                     2 hits, step away toward the nearest visible ally (else our spawn)
EARLY_ROUNDS = 2000          # h_earlyfight_all: group rule for the whole game (v3 variant)
GROUP_R = 7
GROUP_ADV = 1.4
GROUP_DISADV = 0.75
GROUP_ENGAGE_BONUS = 0.4
GROUP_REGROUP_D = 4        # regroup steps when a (stronger) enemy group member is within this
# v2 (after the v1 sprint, 18W-22L): v1 committed on "advantage" counting allies 7 tiles away that
# never joined (our Marcella dived alone into 3 enemies on 00gemfight), chased far targets with the
# bonus, and in "regroup" stepped without hitting back (retreat tile ties -> stood still, 0 damage).
GROUP_ADV_R = 4            # allies counted for "advantage" (close enough to join this turn)
GROUP_BONUS_D = 2          # engage bonus only for targets within attack range + this

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
# ---- q24_combo patch 1, from h_3pick (only the lock-memory fix; trio mode not ported):
# pick_altar also skips altars remembered as enemy-locked (fixes the lock oscillation).
LOCK_MEMORY_FIX = True

# ---- q24_combo patch 2, from h_goldtie v2 (STRATEGIES Q2): gold-tiebreak play.
# At round 2000 equal tributed gems (in practice 0-0) are decided by lifetime gold earned,
# then kills, then Team B wins.
# no_tribute: no altar has a ring tile we can reach without clearing a "guard" group (monolith
# next to the altar: 02guardians / 01boss-battle; the 48-wolf ring of 02the-pack) -> gems are
# worthless: value groups by gold, never walk off to bank, Treasure emblem first, ignore
# carried gems in the fight model.
GOLD_GUARD_STR = 200     # a camp group with this much total strength ...
GOLD_GUARD_HP = 15000    # ... or this much total HP is a guard (never cleared by our model)
# stalled: both teams still at 0 tributed gems from GOLD_STALL_ROUND on (also when no_tribute).
GOLD_STALL_ROUND = 300
# chip mode (no_tribute or stalled): after GOLD_IDLE_TURNS healthy turns in a row with no
# target at all (02gift-wrapping: every group fails the solo safety model), allow up to
# GOLD_CHIP_CYCLES hit-and-run cycles per group instead of 4 (camps do not heal while asleep).
GOLD_IDLE_TURNS = 12
GOLD_CHIP_CYCLES = 30
# q24_combo: h_goldtie printed a slot-0 "GOLDTIE no_tribute ..." stdout line at init in every
# game (diagnostic); it is behind this switch, off.
GOLD_LOG = False
# q24_combo integration of patches 1+2: do_tribute's fallback ring and break_lock only consider
# altars init_gold found usable.  A no-op unless some (not all) altars are guard-only (none of
# the 70 local maps: h_goldtie flags all altars usable on 67 maps and none on 3).
TRIBUTE_USABLE_ONLY = True
TREASURE_ITEMS = {
    "S": (Item.TREASURE_SHARD_OF_STRENGTH, Item.TREASURE_EMBLEM_OF_STRENGTH),
    "H": (Item.TREASURE_SHARD_OF_HEALTH, Item.TREASURE_EMBLEM_OF_HEALTH),
    "F": (Item.TREASURE_SHARD_OF_FOCUS, Item.TREASURE_EMBLEM_OF_FOCUS),
}

# ---- q24_combo patch 4, from h_fightfuel (Q13): fuel caching / capping; PROF and VALIDATE off.
# h_fightfuel: per-section fuel profiler (PROF=True only for profiling runs; prints are
# wrapped in debug_block, fuel-free in debug builds).  A checkpoint whose fuel_remaining
# is higher than the previous one means the bot was suspended inside that section.
# h_fightfuel (Q13): fuel floors for optional fight work (remaining fuel this turn)
FUEL_RETREAT_DASH = 350000   # below this, retreat skips the 2-tile dash search (plain step only)
FUEL_KIT_AIM = 400000        # below this, area spells aim at the target and HoR skips the landing dash
OBSERVE_FAST = True          # observe(): camp presence from the camp_tiles bitboard, 1 API call per camp
THREATS_FAST = True          # threats(): only awake camps (awake_camp_tiles bitboard), not every visible camp
RETREAT_FAST = True          # retreat(): enemy/camp data read once, only sources that can reach a candidate
KIT_FAST = True              # kit_units(): bitboards, only units within reach of the cast
VALIDATE = False   # debug only: run old and new versions side by side and print mismatches
PROF = False
PROF_MIN = 1500000   # print turns that used at least this much (or were suspended)
_prof = []

# ---- c3_teamclear patch 5, from h_teamclear v2 (STRATEGIES Q26; all parts, same flag values).
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
# c3_teamclear: q24's chip mode (h_goldtie, gold play only) is the other bootstrap for these
# groups.  Where the normal solo check fails, choose_target computes both the team option and
# (in chip mode) the chip option (long solo hit-and-run) and keeps the cheaper per-champion
# cost; with chip mode off this is exactly h_teamclear, with no team option exactly q24.  A chip
# pick never musters (muster_need does not know chip mode and would ban the group).
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
TEAM_DEBUG = False
TEAM_MAX_STR = 250        # structure gate: never team-assault a group stronger than this,
TEAM_MAX_HP = 15000       # with this much total HP, or containing a monolith (boss groups)
TEAM_MUSTER_COST = 10.0   # rounds added to a team option's cost for gathering
TEAM_COMMIT_WAIT = 15     # rounds at the ring with too few allies claiming the group -> ban it
TEAM_MUSTER_WAIT = 30     # rounds at the ring without enough allies near -> ban it (v1: 60)
TEAM_BAN = 150
DEAD_MARK = 255           # claim byte of a dead champion (not idle, not a claim)
# Shared byte 6 (free in tb_merge_b and q24_combo): bit s set = the champion in slot s stands
# within its claimed group's range + 4.  The muster counts these present claimers as well as the
# allies it can see (v1 screen, 02harvest: a weak champion waited 60-170 rounds at a ring while
# stronger claimers fought the same group out of its vision).
# Shared memory map (8 bytes): 0-5 claims (0 idle, group idx+1, DEAD_MARK dead; at most 6 bodies:
# 5 picks + Cassi/Issac's extra body), 6 presence bits (this patch), 7 focus (sf_pvp, FOCUS_BYTE).
PRESENT_BYTE = 6


def pm(label):
    if PROF:
        _prof.append((label, cambc.fuel_remaining()))


def prof_flush(tag):
    if not PROF or not _prof:
        return
    marks = list(_prof)
    del _prof[:]
    out = []
    used = 0
    susp = None
    for i in range(1, len(marks)):
        d = marks[i - 1][1] - marks[i][1]
        if d < 0:
            susp = marks[i][0]
            d += 2500000
        used += d
        if d >= 50000:
            out.append("%s:%dk" % (marks[i][0], d // 1000))
    if used >= PROF_MIN or susp is not None:
        line = "PF %s used=%dk susp=%s | %s" % (tag, used // 1000, susp, " ".join(out))
        cambc.debug_block(lambda: print(line, flush=True))


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
        # h_goldtie state
        self.no_tribute = False
        self.altar_ok = set()
        self.stalled = False
        self.stall_done = False
        self.idle = 0
        self.chip = False
        self.tribute_altars = ()   # q24_combo: set by init_gold (TRIBUTE_USABLE_ONLY)
        self.tribute_ring = None
        # h_fightfuel state
        self.camp_rng = {}
        self.esrc = None    # h_fightfuel: per-turn [(enemy, position, range, strength)] from threats()
        self.spawn_cd = {}  # h_fightfuel: tile -> Chebyshev distance to our spawn region (static memo)
        # h_teamclear state (all per-turn values are refreshed before use in the same turn:
        # idle_allies / last_claims / claim_buf by read_claims at the top of choose_target,
        # team_need at the end of choose_target, hidden_hp by threats)
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
        # h_fightfuel: spawn tile -> attack range (static per camp type)
        self.camp_rng = {}
        for G in self.groups:
            for c, p, st, r in G.camps:
                self.camp_rng[p] = r
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
        self.init_gold(home)
        self.inited = True
        if (DEBUG or DIAG) and self.slot == 0:
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

    def init_gold(self, home):
        """h_goldtie: which altars can we ever tribute at?  An altar is usable when one of its
        ring tiles that is not a guard group's spawn tile is reachable from our spawn by
        walking around walls, holes and guard groups, or lies in another walk component the
        dash / TP crossing logic can reach.  No usable altar -> no_tribute (gold-tiebreak play)."""
        guard = Bitboard()
        for G in self.groups:
            if G.n and (G.strength >= GOLD_GUARD_STR or sum(G.maxhp.values()) >= GOLD_GUARD_HP):
                guard |= G.tiles
        sp0 = self.spawn_pts[0]
        blk = self.walk_block | guard
        blk.set(sp0, False)
        reach = blk.reachable_tiles(sp0, self.area)
        reach.set(sp0)
        ok = set()
        for i, (a, goals) in enumerate(self.altar_goals):
            free = goals & ~guard
            if free.is_empty():
                continue  # every walkable ring tile is a guard's spawn tile (02guardians)
            if not (free & reach).is_empty() or (free & home).is_empty():
                # reachable around the guards, or on another island: the crossing logic and
                # pick_altar's distance fields decide exactly as in tb_merge_b
                ok.add(i)
            # else: in our walk component but enclosed by guard tiles (02the-pack's wolf ring)
        self.altar_ok = ok
        self.no_tribute = not ok
        # q24_combo integration (TRIBUTE_USABLE_ONLY): the altars do_tribute / break_lock may walk
        # to.  pick_altar skips unusable (h_goldtie) and remembered-locked (h_3pick) altars; when
        # it finds none, do_tribute's fallback ring must not send carriers to a guard-only altar
        # either.  Identical to every altar unless SOME (not all) altars are guard-only.
        if TRIBUTE_USABLE_ONLY and ok and len(ok) < len(self.altar_goals):
            self.tribute_altars = [a for i, (a, g) in enumerate(self.altar_goals) if i in ok]
            tr = Bitboard()
            for i in ok:
                tr |= self.altar_goals[i][1]
            self.tribute_ring = tr
        else:
            self.tribute_altars = self.altars
            self.tribute_ring = self.altar_ring
        if self.no_tribute:
            for G in self.groups:
                # value = gold; never target a guard: killing the gate (02guardians monolith)
                # opened the altar and the enemy tributed the gems it took from us (v1: 0-11, 0-101)
                G.value = 0.0 if not (G.tiles & guard).is_empty() else float(G.gold)
        if GOLD_LOG and self.slot == 0:
            print("GOLDTIE no_tribute", self.no_tribute, "altars", len(self.altar_goals),
                  "usable", sorted(ok), "guard_tiles", guard.count(), flush=True)

    def gold_play(self):
        """Gold-tiebreak behaviour switches (oscillation fix, chip mode) are on."""
        return self.no_tribute or self.stalled

    def blocks_respawn(self, pos):
        """Would standing on this camp tile delay a respawn?  Only a respawning group's tiles do:
        a dead camp of a group that is still alive never respawns on its own.  In gold play the
        old rule (any camp tile) made champions step on a dead cluster of a half-cleared group,
        get pushed back off toward G.center and repeat for 1,700 rounds (01yellow-brick-road)."""
        if not self.gold_play():
            return True
        for H in self.groups:
            if H.status == 2 and H.tiles.is_set(pos):
                return True
        return False

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
        if VALIDATE:
            snap = [(G.status, G.ready, dict(G.hp)) for G in self.groups]
            self.observe_fast(me, rnd)
            fast = [(G.status, G.ready, dict(G.hp)) for G in self.groups]
            for G, (a, b, h) in zip(self.groups, snap):
                G.status, G.ready, G.hp = a, b, h
            self.observe_slow(me, rnd)
            for G, f in zip(self.groups, fast):
                if (G.status, G.ready, G.hp) != f:
                    msg = "VAL observe r%d g%d slow=%s fast=%s" % (rnd, G.idx, (G.status, G.ready, sorted(G.hp.values())), (f[0], f[1], sorted(f[2].values())))
                    cambc.debug_block(lambda: print(msg, flush=True))
            return
        if OBSERVE_FAST:
            return self.observe_fast(me, rnd)
        return self.observe_slow(me, rnd)

    def observe_slow(self, me, rnd):
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

    def observe_fast(self, me, rnd):
        """observe() with the camp-presence test on bitboards: a visible spawn tile without a
        camp -> 0 HP (as before), a camp on it -> its health (1 API call instead of ~5)."""
        pos = me.position()
        vis = None
        ct = None
        for G in self.groups:
            if G.status == 2 and rnd >= G.ready:
                G.status = 0
                G.hp = dict(G.maxhp)
            if cheb(G.center, pos) > 10:
                continue
            if vis is None:
                vis = cambc.vision.visible_tiles()
                ct = cambc.vision.camp_tiles()
            gv = G.tiles & vis
            if gv.is_empty():
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
                hp = G.hp
                for c, p, s, r in G.camps:
                    try:
                        if gv.is_set(p):
                            if not ct.is_set(p):
                                hp[p] = 0
                            else:
                                hp[p] = c.health()
                        elif c.is_visible():
                            hp[p] = 0 if c.state().is_dead() else c.health()
                    except Exception:
                        pass

    def threats(self, me):
        """Incoming damage per round from awake camps and enemy champions in range."""
        if VALIDATE:
            fi, fa, fe = self.threats_fast(me)
            si, sa, se = self.threats_slow(me)
            ka = sorted((str(cp), r, s) for c, cp, r, s in fa)
            kb = sorted((str(cp), r, s) for c, cp, r, s in sa)
            if abs(fi - si) > 1e-6 or ka != kb or [int(e) for e in fe] != [int(e) for e in se]:
                msg = "VAL threats r%d inc %s/%s awake %s / %s en %d/%d" % (cambc.round_number(), si, fi, kb, ka, len(se), len(fe))
                cambc.debug_block(lambda: print(msg, flush=True))
            self.threats_fast(me)  # restore esrc / far_enemies
            return fi, fa, fe
        if THREATS_FAST:
            return self.threats_fast(me)
        return self.threats_slow(me)

    def threats_slow(self, me):
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
        inc = self.wrap_hidden(pos, awake, inc)  # h_teamclear TEAM_WRAP_FIX (a)
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

    def threats_fast(self, me):
        """threats() over the awake_camp_tiles bitboard (asleep camps never deal damage), and
        each visible enemy's position / range / strength read once for the whole turn."""
        pos = me.position()
        inc = 0.0
        awake = []
        try:
            aw = cambc.vision.awake_camp_tiles()
            if not aw.is_empty():
                rngs = self.camp_rng
                for cp in aw.positions():
                    try:
                        c = cambc.vision.camp_at(cp)
                        r = rngs.get(c.spawn_position())
                        if r is None:
                            r = c.attack_range()
                        s = c.strength()
                        awake.append((c, cp, r, s))
                        if cheb(cp, pos) <= r:
                            inc += s
                    except Exception:
                        pass
        except Exception:
            pass
        inc = self.wrap_hidden(pos, awake, inc)  # h_teamclear TEAM_WRAP_FIX (a)
        enemies = []
        esrc = []
        self.far_enemies = []
        for e in cambc.vision.champions(Team.ENEMY):
            try:
                if not e.is_alive():
                    continue
                ep = e.position()
                d = cheb(ep, pos)
                if d > ENEMY_SIGHT:
                    self.far_enemies.append(e)  # seen via our ward only
                    continue
                enemies.append(e)
                er = e.attack_range()
                es = e.strength()
                esrc.append((e, ep, er, es))
                if d <= er + 1:
                    inc += es
            except Exception:
                pass
        self.esrc = esrc
        if self.jungle(me):
            # Jungle emblem: 30% less camp damage (approximate on the total).
            inc *= 0.8
        return inc, awake, enemies

    def wrap_hidden(self, pos, awake, inc):
        """h_teamclear TEAM_WRAP_FIX (a), shared by threats_slow and threats_fast (c3_teamclear:
        h_teamclear had it inline in tb_merge_b's threats, which q24 split in two).  The target
        group is awake (a group wakes as a whole) -> its unseen, believed-alive camps are awake
        too and hit us if we are in their range: append them to awake (their handles are not in
        vision, so the danger check reads their HP from self.hidden_hp) and add their strength
        to inc.  Reads only this turn's data: awake from this turn's threats, G.status / G.hp
        from this turn's observe; self.target is the group chosen last turn (as in h_teamclear)."""
        self.hidden_hp = None
        G = self.target
        if TEAM_WRAP_FIX and G is not None and G.status == 0 and awake:
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
        return inc

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
            if G.n == 0 or G.value <= 0 or (banned and banned.get(G.idx, 0) > now):
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
                item = self.treasure_item(me, counts)
                if item is None:
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

    def treasure_item(self, me, counts):
        """h_goldtie: with no_tribute, a Treasure emblem (+10% gold; Vesper 33% -> 43%) of the
        champion's main stat comes first.  Spent gold still counts as earned gold."""
        if not self.no_tribute:
            return None
        try:
            plan = BRUISER_PLAN.get(int(me.champion_name()))
        except Exception:
            plan = None
        shard, emblem = TREASURE_ITEMS[plan[0][0] if plan else "S"]
        if counts[int(emblem)] > 0:
            return None
        return shard

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
    def kit_units(self, pos=None, reach=None):
        """(position, weight) of units an area hit would touch: awake camps and
        camps of the current target group +1, enemy champions +2 (+4 while
        channelling), sleeping camps of other groups -3 (do not wake them)."""
        if VALIDATE and pos is not None:
            a = sorted((str(p), w) for p, w in self.kit_units_fast(pos, reach))
            b = sorted((str(p), w) for p, w in self.kit_units() if cheb(p, pos) <= reach)
            if a != b:
                msg = "VAL kit r%d slow=%s fast=%s" % (cambc.round_number(), b, a)
                cambc.debug_block(lambda: print(msg, flush=True))
        if KIT_FAST and pos is not None:
            return self.kit_units_fast(pos, reach)
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

    def kit_units_fast(self, pos, reach):
        """kit_units() restricted to units within `reach` of pos (cast range + area radius:
        nothing farther can be hit), camps classified by the awake/asleep bitboards."""
        units = []
        try:
            near = Bitboard()
            near.draw_chebyshev(pos, reach)
            aw = cambc.vision.awake_camp_tiles() & near
            asl = cambc.vision.asleep_camp_tiles() & near
            if self.target is not None:
                tg = self.target.tiles
                aw |= asl & tg
                asl &= ~tg
            for p in aw.positions():
                units.append((p, 1.0))
            for p in asl.positions():
                units.append((p, -3.0))
            en = cambc.vision.champion_tiles(Team.ENEMY) & near
            if not en.is_empty():
                for p in en.positions():
                    try:
                        e = cambc.vision.champion_at(p)
                        w = 2.0
                        if e.is_recalling() or e.is_submitting_gems() or e.is_teleporting():
                            w = 4.0
                        units.append((p, w))
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
            if KIT_FAST and cambc.fuel_remaining() < FUEL_KIT_AIM:
                return fallback
            units = self.kit_units(pos, rng + radius)
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
            if KIT_FAST and cambc.fuel_remaining() < FUEL_KIT_AIM:
                return False
            pos = me.position()
            units = self.kit_units(pos, 2 + int(info.radius))
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
        if VALIDATE:
            a = self.reset_target_fast(tiles, tg)
            b = self.reset_target_slow(tiles, tg)
            ka = None if a is None else (type(a).__name__, int(a))
            kb = None if b is None else (type(b).__name__, int(b))
            if ka != kb:
                msg = "VAL reset r%d slow=%s fast=%s" % (cambc.round_number(), kb, ka)
                cambc.debug_block(lambda: print(msg, flush=True))
            return a
        if KIT_FAST:
            return self.reset_target_fast(tiles, tg)
        return self.reset_target_slow(tiles, tg)

    def reset_target_slow(self, tiles, tg):
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

    def reset_target_fast(self, tiles, tg):
        """reset_target() fallback over bitboards: only units inside our attack tiles are read
        (it used to read every visible camp, ~1M fuel with a ward up)."""
        best = None
        bh = 0.0
        try:
            en = cambc.vision.champion_tiles(Team.ENEMY) & tiles
            for p in en.positions():
                try:
                    e = cambc.vision.champion_at(p)
                    h = e.health()
                    if best is None or h < bh:
                        best, bh = e, h
                except Exception:
                    pass
            if best is not None:
                return best
            cs = cambc.vision.awake_camp_tiles()
            if tg is not None:
                cs |= cambc.vision.asleep_camp_tiles() & tg
            cs &= tiles
            for p in cs.positions():
                try:
                    c = cambc.vision.camp_at(p)
                    h = c.health()
                    if best is None or h < bh:
                        best, bh = c, h
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
        best_chip = False   # c3_teamclear: best came from the chip-mode fallback (never musters)
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
            chip_pick = False
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
                            if TEAM_CLEAR and not G.boss:
                                k_team = self.team_k(G, s, hl, dps, hp, maxhp, dmg_mult, c + 2, avail + c)
                            # c3_teamclear: q24's chip mode (h_goldtie: 30 hit-and-run cycles
                            # instead of 4) is the other bootstrap.  Same test and cost as q24.
                            # When both exist, keep the cheaper per-champion cost (the team cost
                            # is k x the team's own cost, as score /= k below).
                            chip_ok = self.chip and cycles <= GOLD_CHIP_CYCLES \
                                and self.escape_ok(G, comp)
                            if k_team and chip_ok:
                                ttk_k = hl / (dps + 55.0 * (k_team - 1))
                                if k_team * (d + ttk_k + 6 + TEAM_MUSTER_COST + wait) \
                                        > d + ttk + 6 + cycles * 30.0 + wait:
                                    k_team = 0
                            if k_team:
                                ttk = hl / (dps + 55.0 * (k_team - 1))
                                extra = TEAM_MUSTER_COST
                            elif chip_ok:
                                extra = cycles * 30.0
                                chip_pick = True
                            else:
                                continue
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
                best_chip = chip_pick
        # h_teamclear (2); c3_teamclear: a chip-mode pick hits and runs alone by design, so it
        # never waits for a team (muster_need ignores chip mode and would ban the group after
        # TEAM_COMMIT_WAIT rounds with nobody else committed)
        self.team_need = self.muster_need(me, best, hp, maxhp, dps, dmg_mult, comp) \
            if TEAM_MUSTER and best is not None and best.status == 0 and not best_chip else 0
        if TEAM_DEBUG:
            print("TC r", rnd, "s", self.slot, "pos", pos, "hp", int(hp), "tgt",
                  None if best is None else (best.idx, best.status, int(best.hp_left())),
                  "need", self.team_need, "c", None if best is None else claims.get(best.idx, 0),
                  "idle", self.idle_allies, "sc", round(best_score, 3), "chip", best_chip, flush=True)
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
        rounds, bans the group for TEAM_BAN rounds.  Returns True if the turn was used.
        c3_teamclear: reads only this turn's data (awake from threats, allies from vision,
        claim_buf / last_claims from read_claims in this turn's choose_target)."""
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
            # claimers that report standing near G (seen or not).  c3_teamclear: h_teamclear's
            # local name `pm` is renamed `pbits` (pm is h_fightfuel's profiler function here)
            pbits = buf[PRESENT_BYTE]
            near_sh = 1
            for s in range(PRESENT_BYTE):
                if s != self.slot and buf[s] == G.idx + 1 and (pbits >> s) & 1:
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
        # h_3pick: skip altars REMEMBERED as enemy-locked, not only those locked in sight now.
        # Before, a locked altar just out of vision was picked (short distance), do_tribute
        # (which remembers locks) still walked to it via pref, the lock came into view, the far
        # altar was picked, we stepped away, lost sight of the lock... a 2-cycle that froze
        # carriers for hundreds of rounds (01broken-curve, 02the-pond, 01the-farm).
        mem = self.locked_altars() if LOCK_MEMORY_FIX else ()
        for i, (a, goals) in enumerate(self.altar_goals):
            if a in mem:
                continue
            try:
                if cambc.vision.has_altar_lock(a) and cambc.vision.altar_lock_at(a).is_enemy():
                    continue
            except Exception:
                pass
            if i not in self.altar_ok:
                continue  # h_goldtie: ring only reachable through a guard group
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
        ring = self.tribute_ring  # q24_combo: == altar_ring unless some altars are guard-only
        locked = self.locked_altars()
        if locked:
            free = Bitboard()
            for a in self.tribute_altars:
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

    def retreat(self, me, awake, enemies, rally=None, dry=False):
        """Step to the adjacent tile with the least incoming damage (ties: toward rally points,
        h_earlyfight's regroup, else toward our spawn).

        q24_combo: h_earlyfight's `rally` (last tie-break = distance to the nearest visible ally
        instead of our spawn) is carried into h_fightfuel's retreat_fast and its VALIDATE harness."""
        if VALIDATE and not dry:
            a = self.retreat_fast(me, awake, enemies, rally=rally, dry=True)
            fa = self._dfn
            b = self.retreat(me, awake, enemies, rally=rally, dry=True)
            fb = self._dfn
            if a != b:
                pos0 = me.position()
                nb = Bitboard()
                nb.draw_chebyshev(pos0, 2)
                diffs = []
                for t in nb.positions():
                    x, y = fa(t), fb(t)
                    if x != y:
                        diffs.append((str(t), y, x))
                live = []
                for e in enemies:
                    try:
                        live.append((int(e), str(e.position()), e.attack_range(), e.strength()))
                    except Exception as ex:
                        live.append((int(e), "ERR %s" % ex))
                cached = [(int(e), str(ep), er, es) for e, ep, er, es in (self.esrc or [])]
                msg = "VAL retreat r%d slow=%s fast=%s diffs(slow,fast)=%s live=%s cached=%s" % (cambc.round_number(), b, a, diffs[:2], live, cached)
                cambc.debug_block(lambda: print(msg, flush=True))
            return self.retreat_fast(me, awake, enemies, rally=rally)
        if RETREAT_FAST and not dry:
            return self.retreat_fast(me, awake, enemies, rally=rally)
        pos = me.position()
        blocked = self.blocked_now(me)
        epos = []
        for e in enemies:
            try:
                epos.append(e.position())
            except Exception:
                pass
        spawn_pts = rally if rally else self.spawn_pts

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

        if dry:
            self._dfn = danger
        cands = [pos] + [t for t in blocked.reachable_tiles(pos, 1).positions() if t != pos]
        dash = self.dash_ability(me)
        dl = []
        if dash is not None:
            near = Bitboard()
            near.draw_chebyshev(pos, 2)
            far = near & ~blocked & ~self.walk_block
            dcands = sorted(far.positions(), key=danger)
            if dcands and danger(dcands[0])[:3] < danger(pos)[:3]:
                if dry:
                    dl = [str(t) for t in dcands[:4] if cheb(t, pos) >= 2]
                for t in dcands[:4]:
                    if dry:
                        break
                    if cheb(t, pos) < 2:
                        continue
                    try:
                        if dash.use(t):
                            return True
                    except Exception:
                        continue
        if dry:
            return (dl, str(min(cands, key=danger)))
        if not me.can_move():
            return False
        best = min(cands, key=danger)
        if best != pos:
            try:
                return me.move_absolute(best)
            except Exception:
                return False
        return False

    def retreat_fast(self, me, awake, enemies, rally=None, dry=False):
        """retreat() with the same ordering (damage, camp-range margin, enemy distance, spawn
        distance) but every enemy read once, only camps that can matter within 2 tiles, each
        candidate scored once, and no dash search when the turn's fuel is low.

        q24_combo: with h_earlyfight's `rally` (regroup), the last key is the distance to the
        nearest rally point, exactly as retreat(); it changes every turn, so it is only memoised
        per call (memo), never in the static spawn-distance memo self.spawn_cd."""
        pos = me.position()
        blocked = self.blocked_now(me)
        hs = set()
        for e in enemies:
            try:
                hs.add(int(e))
            except Exception:
                pass
        src = []   # enemies: (position, reach, strength)
        cache = self.esrc
        if cache is not None:
            for e, ep, er, es in cache:
                h = int(e)
                if h in hs:
                    src.append((ep, er + 1, es))
                    hs.discard(h)
        if hs:
            for e in enemies:
                try:
                    if int(e) in hs:
                        src.append((e.position(), e.attack_range() + 1, e.strength()))
                except Exception:
                    pass
        # camps that can matter for a candidate within 2 tiles: those whose range can reach it
        # (cheb - r <= 2) and every possible minimiser of the camp-range margin md (a camp's
        # margin changes by at most 2 between pos and a candidate) -> md is exact
        cm = []
        m0 = None
        for c, cp, r, s in awake:
            k = cheb(cp, pos) - r
            cm.append((k, cp, r, s))
            if m0 is None or k < m0:
                m0 = k
        csrc = []
        if cm:
            lim = max(2, m0 + 4)
            for k, cp, r, s in cm:
                if k <= lim:
                    csrc.append((cp, r, s))
        spawn_pts = self.spawn_pts
        scd = self.spawn_cd
        memo = {}
        rpts = rally if rally else None

        def danger(t):
            v = memo.get(t)
            if v is not None:
                return v
            d = 0.0
            md = None
            for cp, r, s in csrc:
                k = cheb(cp, t)
                if k <= r:
                    d += s
                k -= r
                if md is None or k < md:
                    md = k
            emd = 8
            for ep, rr, s in src:
                k = cheb(ep, t)
                if k <= rr:
                    d += s
                if k < emd:
                    emd = k
            if rpts is not None:
                sd = min(cheb(p, t) for p in rpts)
            else:
                sd = scd.get(t)
                if sd is None:
                    sd = scd[t] = min(cheb(p, t) for p in spawn_pts)
            v = (d, -(md or 0), -emd, sd)
            memo[t] = v
            return v

        if dry:
            self._dfn = danger
        cands = [pos] + [t for t in blocked.reachable_tiles(pos, 1).positions() if t != pos]
        dash = self.dash_ability(me)
        dl = []
        if dash is not None and (dry or cambc.fuel_remaining() > FUEL_RETREAT_DASH):
            near = Bitboard()
            near.draw_chebyshev(pos, 2)
            far = near & ~blocked & ~self.walk_block
            dcands = sorted(far.positions(), key=danger)
            if dcands and danger(dcands[0])[:3] < danger(pos)[:3]:
                if dry:
                    dl = [str(t) for t in dcands[:4] if cheb(t, pos) >= 2]
                for t in dcands[:4]:
                    if dry:
                        break
                    if cheb(t, pos) < 2:
                        continue
                    try:
                        if dash.use(t):
                            return True
                    except Exception:
                        continue
        if dry:
            return (dl, str(min(cands, key=danger)))
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

    def group_balance(self, me, pos, enemies, hp):
        """h_earlyfight: (ours / theirs) local fighting strength, sum(hp) x sum(dps), over me +
        allies within GROUP_R (resp. GROUP_ADV_R for the second ratio) and enemies within GROUP_R;
        plus every visible ally's position.  Returns (ratio_far, ratio_near, rally)."""
        us_hp = float(hp)
        us_dps = self.enemy_dps(me)
        nr_hp = us_hp
        nr_dps = us_dps
        rally = []
        try:
            for a in cambc.vision.champions(Team.ALLY):
                try:
                    if int(a) == int(me) or not a.is_alive():
                        continue
                    ap = a.position()
                    if self.chan_kind(a) in (2, 3):
                        continue  # teleporting / recalling allies are leaving the fight
                    rally.append(ap)
                    da = cheb(ap, pos)
                    if da <= GROUP_R:
                        us_hp += a.health()
                        us_dps += self.enemy_dps(a)
                    if da <= GROUP_ADV_R:
                        nr_hp += a.health()
                        nr_dps += self.enemy_dps(a)
                except Exception:
                    pass
        except Exception:
            pass
        th_hp = 0.0
        th_dps = 0.0
        for e in enemies:
            try:
                if cheb(e.position(), pos) > GROUP_R:
                    continue
                th_hp += e.health()
                th_dps += self.enemy_dps(e) * CHAN_THREAT[self.chan_kind(e)]
            except Exception:
                pass
        if th_hp <= 0 or th_dps <= 0:
            return float(BIG), float(BIG), rally
        return (us_hp * us_dps) / (th_hp * th_dps), (nr_hp * nr_dps) / (th_hp * th_dps), rally

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
        pm("he_near")
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
        gems = 0 if self.no_tribute else me.gem_count()  # h_goldtie: untributable gems
        rich = gems >= FIGHT_RICH_GEMS
        their_ttk = hp / max(1.0, max(threat, fight_dps) + camp_inc)
        best = None
        best_key = None
        best_ratio = BIG
        best_ttk = 0.0
        rnd = cambc.round_number()
        adv = dis = False
        rally = None
        if rnd < EARLY_ROUNDS:
            gb, gb_near, rally = self.group_balance(me, pos, [e for e, d in near], hp)
            adv = gb_near >= GROUP_ADV
            dis = gb <= GROUP_DISADV
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
                kill_now = eh <= my_str and d <= me.attack_range()
                if dis and not kill_now:
                    continue  # h_earlyfight: outnumbered locally -> no new fights
                if adv and d <= me.attack_range() + GROUP_BONUS_D:
                    limit += GROUP_ENGAGE_BONUS
                if ratio <= limit or kill_now:
                    key = (tier, my_ttk / (1.0 + eg / 20.0), d)
                    if best_key is None or key < best_key:
                        best_key = key
                        best = e
                        best_ttk = kill + max(0, d - me.attack_range())
            except Exception:
                pass
        pm("he_eval")
        if PROF:
            self.ptag += " near%d eng%d" % (len(near), best is not None)
        clearly_losing = (best_ratio > (1.0 if rich else FIGHT_FLEE)
                          or len(near) > n_allies + 1)
        if adv:
            clearly_losing = False
        elif dis:
            clearly_losing = True
        if best is None:
            self.last_enemy_danger = rnd
        if best is not None:
            self.write_focus(best)
            moved = self.stun_channel(me, best, best_ttk)
            pm("he_stun")
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
            pm("he_move")
            attacked = False
            try:
                if me.can_attack() and me.attack_tiles().is_set(best.position()):
                    me.attack(best)
                    attacked = True
            except Exception:
                pass
            self.cast_combat(me, best, moved, incoming, attacked)
            pm("he_cast")
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
            if dis:
                # h_earlyfight: trading 1-vs-many only feeds their kill chain; finish it only if
                # it dies in two hits, else walk back toward our allies
                if adj.health() <= 2 * my_str:
                    return self.strike(me, adj, incoming)
            elif adv or not (clearly_losing and escape):
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
        regroup = dis and min(d for e, d in near) <= GROUP_REGROUP_D
        if threat > 0 or regroup or (clearly_losing and (len(near) > n_allies + 1 or rich)):
            if not clearly_losing:
                self.stall += 1.0
            if hp < maxhp * 0.5 and incoming == 0 and not self.spawn.is_set(pos) \
                    and self.recall_safe(me, enemies):
                try:
                    me.recall()
                    return True
                except Exception:
                    pass
            pm("he_pre_retreat")
            moved = self.retreat(me, awake, [e for e, d in near], rally if dis else None)
            pm("he_retreat")
            if dis:
                self.hit_while_leaving(me, [e for e, d in near], moved, incoming)
            return True
        return False

    def hit_while_leaving(self, me, enemies, moved, incoming):
        """h_earlyfight v2: after a regroup step, still hit the weakest enemy in reach (melee can
        walk and attack in one turn; a ranged champion that walked cannot attack anyway)."""
        try:
            if not me.can_attack():
                return
            tiles = me.attack_tiles()
        except Exception:
            return
        best = None
        for e in enemies:
            try:
                if e.is_alive() and tiles.is_set(e.position()):
                    if best is None or e.health() < best.health():
                        best = e
            except Exception:
                pass
        if best is None:
            return
        try:
            me.attack(best)
        except Exception:
            return
        self.cast_combat(me, best, moved, incoming, True)

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
            eg = 0 if self.no_tribute else e.gem_count()
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
        free_d = min([cheb(a, pos) for a in self.tribute_altars if a not in locked] or [BIG])
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

    def diag(self, me, rnd, incoming, enemies):
        try:
            pos = me.position()
            al = []
            for a in cambc.vision.champions(Team.ALLY):
                if int(a) != int(me) and a.is_alive():
                    al.append("%s@%d,%d" % (str(a.champion_name()).split('.')[-1][:4], a.position().x, a.position().y))
            en = []
            for e in enemies:
                en.append("%s@%d,%d:%d/g%d" % (str(e.champion_name()).split('.')[-1][:4], e.position().x,
                                               e.position().y, e.health(), e.gem_count()))
            print("D r%d %s @%d,%d hp%d/%d g%d gold%d tgt%s inc%d A[%s] E[%s]" % (
                rnd, str(me.champion_name()).split('.')[-1][:4], pos.x, pos.y, me.health(), me.max_health(),
                me.gem_count(), me.gold_count(), None if self.target is None else self.target.idx, incoming,
                " ".join(al), " ".join(en)), flush=True)
        except Exception as ex:
            print("diag err", ex, flush=True)

    # ------------------------------------------------------------------- turn
    def pm_end(self, label):
        pm(label)

    def prof(self):
        if PROF:
            prof_flush(getattr(self, "ptag", "?"))

    debug_tb = False

    def play_turn(self):
        pm("start")
        # q24_combo: the per-turn enemy cache (h_fightfuel) is only valid for the turn that
        # filled it; threats() refills it every turn before any reader (retreat_fast) runs, and
        # clearing it here guarantees no path can ever read last turn's positions.
        self.esrc = None
        me = cambc.me()
        if PROF:
            try:
                self.ptag = "r%d %s" % (cambc.round_number(), str(me.champion_name()).split(".")[-1])
            except Exception:
                self.ptag = "?"
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
        pm("observe")
        if not self.no_tribute and rnd >= GOLD_STALL_ROUND and not self.stall_done:
            # h_goldtie: nobody has tributed yet -> the game is heading for the gold tiebreak.
            # Tributed gems never decrease, so the first tribute ends this for good.
            self.stalled = (cambc.global_submitted_gems(Team.ALLY) == 0
                            and cambc.global_submitted_gems(Team.ENEMY) == 0)
            if not self.stalled:
                self.stall_done = True
                self.chip = False
        if me.is_recalling() or me.is_submitting_gems() or me.is_teleporting():
            return
        self.try_ward(me)
        pm("ward")
        pos = me.position()
        at_spawn = self.spawn.is_set(pos)
        if at_spawn:
            self.shop(me)
            pm("shop")

        incoming, awake, enemies = self.threats(me)
        pm("threats")
        if PROF:
            self.ptag += " en%d aw%d inc%d" % (len(enemies), len(awake), int(incoming))
        if DIAG and rnd < DIAG_UNTIL:
            self.diag(me, rnd, incoming, enemies)
        self.try_lock(me, enemies)
        pm("lock")
        hp = me.health()
        maxhp = me.max_health()
        self.update_alerts(me, rnd, enemies)
        pm("alerts")
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
                pm("danger_retreat")
                return
        pm("danger")

        # ---- fight or avoid enemy champions
        if enemies and self.handle_enemies(me, enemies, awake, incoming, hp, maxhp):
            pm("he_end")
            return
        pm("he_none")

        # ---- recall to heal / shop when safe
        if incoming == 0 and not at_spawn:
            spawn_d = min(cheb(p, pos) for p in self.spawn.positions())
            low = hp < maxhp * 0.45
            carried = 0 if self.no_tribute else me.gem_count()
            rich = (me.gold_count() >= 150 and carried < 8) or me.gold_count() >= 400
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

        pm("recall")
        self.sf_use = not self.walk_block.is_set(pos)
        if not self.sf_use:
            field, visited = self.dist_field(me)
            pm("field_full")
        elif self.sf_todo:
            field, visited = self.dist_field(me, self.sf_dests())
            pm("field_dests")
        else:
            field, visited = None, None  # cached static fields (group_dist / altar_distance)
        comp = self.comp_of(pos)
        pm("comp")

        # ---- tribute decision
        gems = me.gem_count()
        tgt = None
        chosen = False
        pref = None
        if gems > 0 and not self.no_tribute:  # h_goldtie: nowhere to bank -> keep farming gold
            self.pref_altar = None
            ad, pref = self.pick_altar(field, visited, rnd, pos)
            pm("pick_altar")
            if ad >= BIG:
                ad = 40
            total = cambc.global_submitted_gems(Team.ALLY) + gems
            thr = self.threatened(rnd, hp, maxhp)
            go = (rnd + ad + gems // 10 + 12 >= MAX_ROUNDS or total >= 1000 or rnd >= BANK_LATE_ROUND
                  or self.bank_now(gems, BIG if BANK_DETOUR else ad, thr))
            if not go:
                tgt = self.choose_target(me, rnd, field, visited, comp)
                pm("choose_bank")
                chosen = True
                if tgt is None:
                    go = True
                elif BANK_DETOUR:
                    go = self.bank_detour(gems, self.detour(ad, field, visited, tgt, pos), thr)
            if go:
                self.write_claim(None)
                self.do_tribute(me, pref)
                pm("tribute")
                return

        # ---- farming
        G = tgt if chosen else self.choose_target(me, rnd, field, visited, comp)
        pm("choose")
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
        if self.gold_play():
            # h_goldtie chip mode: healthy but nothing passes the solo safety model for a while
            if G is None and hp >= maxhp * 0.9:
                self.idle += 1
                if self.idle >= GOLD_IDLE_TURNS and not self.chip:
                    self.chip = True
                    if DEBUG:
                        print("GOLDTIE chip mode", rnd, self.slot, flush=True)
            else:
                self.idle = 0
        if G is None:
            if gems > 0 and not self.no_tribute:
                self.do_tribute(me, pref)
            elif not at_spawn and (me.gold_count() >= 60 or hp < maxhp * 0.7):
                try:
                    me.recall()
                except Exception:
                    pass
            return

        if G.status != 1 and self.all_camp_tiles.is_set(pos) \
                and not (TEAM_WRAP_FIX and G.status == 0 and G.tiles.is_set(pos)) \
                and self.blocks_respawn(pos):
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
            pm("muster")
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
            pm("farm_goals")
            moved = self.go_to(me, goals, avoid, alive)
            pm("farm_goto")
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
            pm("farm_cast")
        self.note_progress(G, rnd, moved or attacked)
