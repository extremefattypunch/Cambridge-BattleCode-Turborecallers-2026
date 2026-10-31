"""tb_aggro: camp farming core with opportunistic PvP ("farm + punish")."""
import cambc
from cambc import game_map, Team, Vec2, Bitboard, DistanceField

IT = cambc.ItemType
CT = cambc.ConsumableType
UNREACHED_LIMIT = 10000

# kind -> (hp, strength, range)
CAMP_STATS = {0: (1350, 20, 3), 1: (2400, 60, 4), 2: (120, 0, 0), 3: (120, 0, 0),
              4: (20000, 200, 5), 5: (5000, 120, 4)}

BUILD = [
    (IT.JUNGLE_SHARD_OF_STRENGTH, 5),
    (IT.MONSTER_SHARD_OF_STRENGTH, 5),
    (IT.DURABILITY_SHARD_OF_HEALTH, 5),
    (IT.JUNGLE_SHARD_OF_HEALTH, 5),
    (IT.POWER_SHARD_OF_STRENGTH, 1000),
]


def cheb(a, b):
    return a.chebyshev_distance(b)


def disk(position, radius):
    b = Bitboard()
    b.draw_chebyshev(position, radius)
    return b


class Group:
    __slots__ = ("idx", "obj", "handle", "tiles", "center", "hp", "dps", "rng", "gems", "gold",
                 "field", "respawn_until", "danger", "known_hp")


class Bot:
    def __init__(self):
        self.ready = False
        self.build_bought = [0] * len(BUILD)
        self.target = -1
        self.wait_turns = 0
        self.last_hp = None
        self.skip_until = {}
        self.danger_zone = None
        self.stall_g, self.stall_best, self.stall_n = -1, 0, 0
        self.danger_memory = {}
        self.team_n = 3

    # ------------------------------------------------------------------ setup
    def setup(self):
        me = cambc.me()
        self.static_blocked = (game_map.walls() | game_map.holes() | game_map.altars()
                               | game_map.spawn_region(Team.ENEMY))
        self.my_spawn = game_map.spawn_region(Team.ALLY)
        self.enemy_spawn = game_map.spawn_region(Team.ENEMY)
        self.altars = game_map.altars().positions()
        walls = self.static_blocked
        # Distance to any altar approach tile.
        approach = Bitboard()
        for a in self.altars:
            approach |= disk(a, 1)
        approach &= ~walls
        self.altar_field = DistanceField()
        self.altar_field.compute(walls, approach, Bitboard())
        self.spawn_field = DistanceField()
        self.spawn_field.compute(walls, self.my_spawn, Bitboard())
        self.groups = []
        self.group_by_handle = {}
        for i, g in enumerate(game_map.camp_groups()):
            gr = Group()
            gr.idx = i
            gr.obj = g
            gr.handle = int(g)
            gr.tiles = g.spawn_tiles()
            ps = gr.tiles.positions()
            cx = sum(p.x for p in ps) // len(ps)
            cy = sum(p.y for p in ps) // len(ps)
            gr.center = min(ps, key=lambda p: abs(p.x - cx) + abs(p.y - cy))
            hp = dps = rng = 0
            danger = False
            for c in g.camps():
                h, s, r = CAMP_STATS.get(int(c.kind()), (3000, 100, 4))
                hp += h
                dps += s
                rng = max(rng, r)
                if int(c.kind()) == 4:
                    danger = True
            gr.hp, gr.dps, gr.rng = hp, dps, rng
            gr.known_hp = hp
            gr.gems, gr.gold = g.gem_value(), g.gold_value()
            gr.respawn_until = -1
            gr.danger = danger
            f = DistanceField()
            f.compute(walls & ~gr.tiles, gr.tiles, Bitboard())
            gr.field = f
            self.groups.append(gr)
            self.group_by_handle[gr.handle] = gr
        handles = sorted(int(c) for c in cambc.champions(Team.ALLY))
        self.slot = min(handles.index(int(me)), 5) if int(me) in handles else 0
        self.team_n = max(1, len(handles))
        unreached = self.spawn_field.get(game_map.walls().positions()[0]) if not game_map.walls().is_empty() else -1
        print("setup groups", len(self.groups), "team", self.team_n, "unreached", unreached)
        name = me.champion_name()
        self.ranged = me.attack_range() > 1
        self.name = name
        self.ready = True

    # --------------------------------------------------------------- helpers
    def blocked_now(self):
        blocked = (self.static_blocked | cambc.vision.champion_tiles()
                   | cambc.vision.camp_tiles() | cambc.vision.teleport_tiles())
        blocked.set(self.pos, False)
        return blocked

    def move_to_goals(self, goals):
        dz = self.danger_zone
        if dz is not None and not dz.is_empty():
            if self._move_to_goals(goals, dz):
                return True
        return self._move_to_goals(goals, None)

    def _move_to_goals(self, goals, dz):
        me = self.me
        if not me.can_move() or goals.is_set(self.pos):
            return False
        blocked = self.blocked_now()
        if dz is not None:
            blocked |= dz & ~goals
            blocked.set(self.pos, False)
        goals = goals & (~blocked | cambc.vision.camp_tiles() | cambc.vision.champion_tiles())
        if goals.is_empty():
            return False
        field = DistanceField()
        field.compute_to(blocked & ~goals, goals, disk(self.pos, 0), Bitboard())
        reach = blocked.reachable_tiles(self.pos, 1).positions()
        best = self.pos
        bestd = field.get(self.pos)
        for p in reach:
            d = field.get(p)
            if d < bestd:
                best, bestd = p, d
        if best == self.pos:
            return False
        try:
            return me.move_absolute(best)
        except Exception:
            return False

    def retreat(self, threats):
        """Step to the reachable tile that maximises distance from threats, prefer home."""
        me = self.me
        if not me.can_move() or not threats:
            return False
        blocked = self.blocked_now()
        best = self.pos
        best_key = None
        for p in [self.pos] + blocked.reachable_tiles(self.pos, 1).positions():
            margin = min(cheb(p, tp) - tr for tp, tr in threats)
            key = (min(margin, 2), -self.spawn_field.get(p))
            if best_key is None or key > best_key:
                best, best_key = p, key
        if best == self.pos:
            return False
        try:
            return me.move_absolute(best)
        except Exception:
            return False

    def buy(self):
        me = self.me
        try:
            if me.gold_count() >= 40 and me.consumables()[CT.ALTAR_LOCK].count() == 0 \
                    and me.can_buy(CT.ALTAR_LOCK):
                me.buy(CT.ALTAR_LOCK)
        except Exception:
            pass
        for i, (item, n) in enumerate(BUILD):
            while self.build_bought[i] < n:
                if not me.can_buy(item, 1):
                    return
                me.buy(item, 1)
                self.build_bought[i] += 1

    def threats(self, enemies, awake_camps):
        out = []
        for c in awake_camps:
            out.append((c.position(), c.attack_range()))
        for e in enemies:
            out.append((e.position(), max(e.attack_range(), 3)))
        return out

    # ------------------------------------------------------------- abilities
    def cast_on(self, target, want_kinds, allow_exclusive=True):
        me = self.me
        if not me.can_cast():
            return False
        tpos = target.position() if not isinstance(target, Vec2) else target
        for ab in me.abilities():
            try:
                info = ab.info()
                if info is None or ab.cooldown() > 0:
                    continue
                if info.exclusive_with_movement and not allow_exclusive:
                    continue
                kind = None
                if ab.is_cc():
                    kind = "cc"
                elif ab.is_damage():
                    kind = "dmg"
                elif ab.is_aoe_damage():
                    kind = "aoe"
                if kind not in want_kinds:
                    continue
                rng = getattr(info, "range", 0)
                if cheb(self.pos, tpos) > rng:
                    continue
                if kind == "aoe":
                    ok = ab.use(tpos)
                else:
                    ok = ab.use(target)
                if ok:
                    return True
            except Exception:
                continue
        return False

    def self_cast(self, kinds):
        me = self.me
        if not me.can_cast():
            return False
        for ab in me.abilities():
            try:
                if ab.info() is None or ab.cooldown() > 0:
                    continue
                if ("reset" in kinds and ab.is_attack_reset()) or ("shield" in kinds and ab.is_shield()):
                    if ab.use(None):
                        return True
            except Exception:
                continue
        return False

    def basic_attack(self, target):
        me = self.me
        if not me.can_attack():
            return False
        if cheb(self.pos, target.position()) > me.attack_range():
            return False
        try:
            me.attack(target)
        except Exception:
            return False
        # attack reset for a free second hit
        try:
            if target.is_visible() and target.health() > 0 and self.self_cast(("reset",)):
                if me.can_attack():
                    me.attack(target)
        except Exception:
            pass
        return True

    # ----------------------------------------------------------------- turn
    def play_turn(self):
        if not self.ready:
            self.setup()
        me = self.me = cambc.me()
        rnd = cambc.round_number()
        if not me.is_alive():
            try:
                self.buy()
            except Exception:
                pass
            return
        self.pos = me.position()
        if rnd % 250 == 0:
            print("R", rnd, "s", self.slot, "pos", self.pos.x, self.pos.y, "hp", int(me.health()), "tgt", self.target,
                  "wait", self.wait_turns, "gems", me.gem_count(), "mem", list(self.read_commits()))
        if me.is_recalling() or me.is_teleporting():
            return
        hp, mhp = me.health(), me.max_health()
        at_spawn = self.my_spawn.is_set(self.pos)
        if at_spawn:
            try:
                self.buy()
            except Exception as e:
                print("buy err", e)

        enemies = []
        for e in cambc.vision.champions(Team.ENEMY):
            try:
                if e.is_alive() and e.health() > 0:
                    enemies.append(e)
            except Exception:
                pass
        camps = cambc.vision.camps()
        awake = []
        for c in camps:
            try:
                if c.is_awake():
                    awake.append(c)
            except Exception:
                pass

        # Submitting gems: keep going unless something is badly wrong.
        if me.is_submitting_gems():
            self.punish_tribute(enemies)
            return

        allies_near = 1
        for a in cambc.vision.champions(Team.ALLY):
            if int(a) != int(me):
                try:
                    if cheb(a.position(), self.pos) <= 5:
                        allies_near += 1
                except Exception:
                    pass
        enemies_near = [e for e in enemies if cheb(e.position(), self.pos) <= 5]

        # ---------------- low health: get out of range, then recall
        in_camp_range = [c for c in awake if cheb(c.position(), self.pos) <= c.attack_range()]
        low = hp < mhp * 0.38
        outnumbered = len(enemies_near) > allies_near and hp < mhp * 0.6
        if at_spawn and hp < mhp * 0.9 and not enemies_near:
            return  # heal up on spawn
        if (low or outnumbered) and not at_spawn:
            # finish off a nearly dead enemy in range rather than run
            for e in enemies_near:
                if e.health() <= me.strength() and cheb(e.position(), self.pos) <= me.attack_range():
                    self.basic_attack(e)
                    return
            thr = self.threats(enemies_near, awake)
            dangerous = [t for t in thr if cheb(t[0], self.pos) <= t[1] + 1]
            if dangerous:
                self.self_cast(("shield",))
                self.retreat(thr)
                return
            try:
                me.recall()
            except Exception as e:
                print("recall err", e)
            return

        # ---------------- PvP
        if enemies and self.fight(enemies, enemies_near, allies_near, hp, mhp):
            return

        # ---------------- tribute
        gems = me.gem_count()
        if gems > 0:
            adist = self.altar_field.get(self.pos)
            want = (gems >= 30 or adist <= 4 or (gems >= 12 and adist <= 12)
                    or rnd > 1850 or self.target < 0)
            if want and adist < UNREACHED_LIMIT:
                if self.go_tribute(enemies):
                    return

        self.farm(camps, awake, allies_near, hp, mhp, rnd)

    # ------------------------------------------------------------------ PvP
    def fight(self, enemies, enemies_near, allies_near, hp, mhp):
        me = self.me
        my_str = me.strength()

        def score(e):
            s = e.health()
            try:
                g = e.gem_count()
                s -= g * 20
            except Exception:
                pass
            try:
                if e.is_submitting_gems() or e.is_recalling():
                    s -= 300
            except Exception:
                pass
            return s

        # interrupt channels with stuns whenever possible
        for e in enemies:
            try:
                if e.is_recalling() or e.is_submitting_gems():
                    if self.cast_on(e, ("cc",), allow_exclusive=True):
                        break
            except Exception:
                pass
        # altar lock on enemy tributes
        self.punish_tribute(enemies)

        favourable = (len(enemies_near) <= allies_near and hp >= mhp * 0.45)
        in_range = [e for e in enemies if cheb(e.position(), self.pos) <= me.attack_range()]
        if in_range:
            tgt = min(in_range, key=score)
            killable = tgt.health() <= my_str * 2
            if favourable or killable or hp >= tgt.health() * 1.3:
                self.cast_on(tgt, ("cc", "dmg", "aoe"), allow_exclusive=True)
                if self.basic_attack(tgt):
                    # melee may still move: stick to target
                    return True
                return True
        if not favourable:
            return False
        # chase a worthwhile target
        cands = []
        for e in enemies_near:
            try:
                worth = e.health() < e.max_health() * 0.55
                try:
                    worth = worth or e.gem_count() >= 8
                except Exception:
                    pass
                try:
                    worth = worth or e.is_submitting_gems() or e.is_recalling()
                except Exception:
                    pass
                if worth and not self.enemy_spawn.is_set(e.position()):
                    cands.append(e)
            except Exception:
                pass
        if not cands or me.gem_count() >= 20:
            return False
        tgt = min(cands, key=score)
        # spell from range first if possible
        if self.cast_on(tgt, ("cc", "dmg"), allow_exclusive=self.ranged):
            if not me.can_move():
                return True
        goal = disk(tgt.position(), me.attack_range()) & ~self.static_blocked
        if self.move_to_goals(goal):
            self.pos = me.position()
            if cheb(self.pos, tgt.position()) <= me.attack_range():
                self.basic_attack(tgt)
            return True
        return False

    def punish_tribute(self, enemies):
        me = self.me
        try:
            lock = me.consumables()[CT.ALTAR_LOCK]
            if lock.count() == 0:
                return
        except Exception:
            return
        for e in enemies:
            try:
                if not e.is_submitting_gems():
                    continue
                ep = e.position()
                for a in self.altars:
                    if cheb(a, ep) <= 1 and cheb(a, self.pos) <= 2 and not cambc.vision.has_altar_lock(a):
                        if lock.use(a):
                            print("altar lock placed", a)
                            return
            except Exception:
                continue

    # -------------------------------------------------------------- tribute
    def go_tribute(self, enemies):
        me = self.me
        goals = Bitboard()
        for a in self.altars:
            try:
                if cambc.vision.has_altar_lock(a):
                    lk = cambc.vision.altar_lock_at(a)
                    if lk.is_enemy():
                        continue
            except Exception:
                pass
            if cheb(self.pos, a) <= 1:
                try:
                    me.submit_gems(a)
                    return True
                except Exception as e:
                    print("submit err", e)
                    continue
            goals |= disk(a, 1)
        goals &= ~self.static_blocked
        if goals.is_empty():
            return False
        return self.move_to_goals(goals)

    # ----------------------------------------------------------------- farm
    def update_groups(self, camps, rnd):
        visible = cambc.vision.visible_tiles()
        alive_hp = {}
        for c in camps:
            try:
                h = c._group
                alive_hp[h] = alive_hp.get(h, 0) + c.health()
            except Exception:
                pass
        for g in self.groups:
            if (g.tiles & visible).is_empty():
                continue
            try:
                st = g.obj.state()
            except Exception:
                continue
            if isinstance(st, game_map.CampGroupRespawning):
                g.respawn_until = rnd + max(st.timer, 3)
                g.known_hp = g.hp
            elif isinstance(st, game_map.CampGroupRewardAvailable):
                g.respawn_until = -2  # capture pending
                g.known_hp = 0
            else:
                g.respawn_until = -1
                if g.handle in alive_hp:
                    g.known_hp = alive_hp[g.handle]

    def group_status(self, g, rnd):
        """'alive', 'capture' or 'gone'."""
        if g.respawn_until == -2:
            return "capture"
        if g.respawn_until > rnd:
            return "gone"
        return "alive"

    def read_commits(self):
        data = bytearray(8)
        try:
            cambc.shared_memory.read(0, data)
        except Exception:
            pass
        return data

    def write_commit(self, idx, ready=False):
        try:
            cambc.shared_memory.write(self.slot, bytes([((idx + 1) & 0x7F) | (0x80 if ready else 0)]))
        except Exception:
            pass

    def needed_helpers(self, g, my_str, mhp):
        for n in range(1, 7):
            if self.feasible(g, n, my_str, mhp):
                return n
        return 99

    def feasible(self, g, helpers, my_str, my_hp):
        if g.dps == 0:
            return True
        if g.danger:
            return False
        team_dps = my_str * helpers * (0.9 if helpers > 1 else 1.0)
        turns = g.known_hp / max(team_dps, 1.0)
        incoming = turns * g.dps * 0.75  # jungle/stuns/retreat rotation
        budget = my_hp * 0.6 + (helpers - 1) * my_hp * 0.5
        return incoming <= budget

    def farm(self, camps, awake, allies_near, hp, mhp, rnd):
        me = self.me
        self.update_groups(camps, rnd)
        # remember awake heavy camps (elk/golem/monolith) for a few rounds
        for c in awake:
            try:
                if int(c.kind()) in (1, 4, 5):
                    self.danger_memory[int(c)] = (c.position(), c.attack_range() + 1, rnd + 4, c._group)
            except Exception:
                pass
        dz = Bitboard()
        for k in list(self.danger_memory.keys()):
            p, r, until, gh = self.danger_memory[k]
            if until < rnd:
                del self.danger_memory[k]
                continue
            if self.target >= 0 and gh == self.groups[self.target].handle:
                continue
            dz |= disk(p, r)
        self.danger_zone = dz
        commits = self.read_commits()
        my_str = me.strength()
        best = None
        best_score = -1.0
        for g in self.groups:
            status = self.group_status(g, rnd)
            if status == "gone":
                continue
            d = g.field.get(self.pos)
            if d >= UNREACHED_LIMIT:
                continue
            if self.skip_until.get(g.idx, -1) > rnd:
                continue
            in_dz = not dz.is_empty() and not (g.tiles & dz).is_empty()
            committed = sum(1 for s in range(6) if s != self.slot and (commits[s] & 0x7F) == g.idx + 1)
            helpers = 1 + committed
            if status == "capture":
                val = g.gems * 3 + g.gold * 0.5
                sc = val / (d + 6.0)
            else:
                solo = self.feasible(g, 1, my_str, mhp)
                if not solo and not self.feasible(g, max(helpers, self.team_n), my_str, mhp):
                    continue
                val = g.gems * 3 + g.gold * 0.5 + 1
                h = max(helpers, 1 if solo else self.team_n)
                kill = g.known_hp / max(my_str * h, 1.0)
                sc = val / (d + kill + 6.0)
                if not solo:
                    sc *= 0.6 if committed == 0 else 2.0
                elif committed:
                    sc *= 1.2
                if g.idx == self.target:
                    sc *= 1.3  # stickiness
            if in_dz:
                sc *= 0.2
            if sc > best_score:
                best, best_score = g, sc
        # never stand on spawn tiles of a respawning group (it blocks the respawn)
        for g in self.groups:
            if g.respawn_until > rnd and g.tiles.is_set(self.pos) and me.can_move():
                self.retreat([(self.pos, 0)])
                break
        if best is None:
            self.target = -1
            self.write_commit(-1)
            # nothing to do: go home / idle near spawn
            if not self.my_spawn.is_set(self.pos):
                self.move_to_goals(self.my_spawn.copy())
            return
        self.target = best.idx
        self.write_commit(best.idx)
        g = best

        # Attack camps of our target group that are in range (lowest hp first).
        my_camps = [c for c in camps if getattr(c, "_group", None) == g.handle]
        # also defend against any awake camp hitting us
        hitting = [c for c in awake if cheb(c.position(), self.pos) <= c.attack_range()
                   and getattr(c, "_group", None) != g.handle]
        if hitting:
            # stray awake camp: fight it if its group is feasible here, else back off
            # and give up on the current target for a while (avoids oscillation)
            hc = min(hitting, key=lambda c: c.health())
            hg = self.group_by_handle.get(getattr(hc, "_group", -1))
            if hg is not None and not hg.danger and self.feasible(hg, max(1, allies_near), my_str, mhp):
                self.target = hg.idx
                self.write_commit(hg.idx, True)
                g = hg
                my_camps = [c for c in camps if getattr(c, "_group", None) == g.handle]
            else:
                thr = [(c.position(), c.attack_range()) for c in hitting]
                self.skip_until[g.idx] = rnd + 40
                if self.retreat(thr):
                    return
        rng = me.attack_range()
        # Dangerous group that we cannot solo: wait outside its range for allies.
        if g.dps > 0 and not self.feasible(g, 1, my_str, mhp):
            group_awake = any(c in awake for c in my_camps)
            need = self.needed_helpers(g, my_str, mhp)
            ready = sum(1 for s in range(6) if s != self.slot and commits[s] == ((g.idx + 1) | 0x80))
            d = g.field.get(self.pos)
            if not group_awake and ready + 1 < need and allies_near < need:
                if d <= g.rng + 2:
                    self.write_commit(g.idx, True)
                    self.wait_turns += 1
                    if self.wait_turns < 40:
                        return
                    self.skip_until[g.idx] = rnd + 60
                    self.wait_turns = 0
                    self.write_commit(-1)
                    return
                else:
                    self.move_to_goals(g.tiles.copy())
                    return
            if d <= g.rng + 2:
                self.write_commit(g.idx, True)
        else:
            self.wait_turns = 0
        inr = [c for c in my_camps if cheb(c.position(), self.pos) <= rng]
        # stall detection: no progress towards the target for a while -> skip it
        dcur = g.field.get(self.pos)
        status = self.group_status(g, rnd)
        if inr or (status == "capture" and g.tiles.is_set(self.pos)):
            self.stall_n = 0
            self.stall_best = dcur
        elif self.stall_g != g.idx or dcur < self.stall_best:
            self.stall_g, self.stall_best, self.stall_n = g.idx, dcur, 0
        else:
            self.stall_n += 1
            if self.stall_n > 20:
                self.skip_until[g.idx] = rnd + 120
                self.stall_n = 0
                self.write_commit(-1)
        if inr:
            tgt = min(inr, key=lambda c: c.health())
            self.cast_on(tgt, ("cc", "dmg", "aoe"), allow_exclusive=True)
            self.self_cast(("shield",)) if hp < mhp * 0.8 else None
            self.basic_attack(tgt)
            return
        # Move toward the group: live camps first, else spawn tiles (capture).
        goals = Bitboard()
        for c in my_camps:
            goals.set(c.position())
        if goals.is_empty():
            goals = g.tiles.copy()
            if status != "capture":
                hidden = goals & ~cambc.vision.visible_tiles()
                if not hidden.is_empty():
                    goals = hidden
                else:
                    goals.set(self.pos, False)
                    if goals.is_empty():
                        goals = g.tiles.copy()
        moved = self.move_to_goals(goals)
        if moved:
            self.pos = me.position()
            inr = [c for c in my_camps if c.is_visible() and cheb(c.position(), self.pos) <= rng]
            if inr and not self.ranged:
                self.basic_attack(min(inr, key=lambda c: c.health()))
