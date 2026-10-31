"""tb_deathball: the whole team farms one camp group at a time.

A leader (first living ally in roster order) scores every camp group by value per
estimated time (travel + clear time from team DPS + capture), rejects groups that
are too dangerous for the team's current HP, and publishes the chosen group in
shared memory. Everyone converges on that group, engages together, captures,
tributes when their bag justifies it, and retreats / recalls when low.
"""
import cambc
from cambc import game_map

Team, Item = cambc.Team, cambc.ItemType
Vec2, Bitboard, DistanceField = cambc.Vec2, cambc.Bitboard, cambc.DistanceField

# CampType -> (health, strength, range)
CAMP_STATS = {
    0: (1350, 20, 3),     # wolf
    1: (2400, 60, 4),     # elk
    2: (120, 0, 0),       # gem cluster
    3: (120, 0, 0),       # gold cluster
    4: (20000, 200, 5),   # monolith
    5: (5000, 120, 4),    # golem
}

MELEE_BUILD = ([Item.JUNGLE_SHARD_OF_HEALTH] * 5 + [Item.MONSTER_SHARD_OF_STRENGTH] * 5
               + [Item.POWER_SHARD_OF_STRENGTH, Item.POWER_SHARD_OF_HEALTH] * 20)
RANGED_BUILD = ([Item.MONSTER_SHARD_OF_STRENGTH] * 5 + [Item.JUNGLE_SHARD_OF_HEALTH] * 5
                + [Item.POWER_SHARD_OF_STRENGTH, Item.POWER_SHARD_OF_HEALTH] * 20)
HEALER_BUILD = ([Item.JUNGLE_SHARD_OF_HEALTH] * 5 + [Item.POWER_SHARD_OF_FOCUS] * 6
                + [Item.POWER_SHARD_OF_HEALTH, Item.POWER_SHARD_OF_FOCUS] * 20)

WILLOW = 8
SPLIT = True
SPLIT_MIN = 4
DEBUG = False
TRIBUTE_GEMS = 18
END_ROUND = 1870
SHOP_GOLD = 150


def cheb(a, b):
    return a.chebyshev_distance(b)


def tiles_around(position, radius):
    tiles = Bitboard()
    tiles.draw_chebyshev(position, radius)
    return tiles


class GroupInfo:
    __slots__ = ("idx", "group", "tiles", "positions", "gems", "gold", "hp", "sum_str",
                 "max_str", "max_range", "free", "respawn")


class Bot:
    def __init__(self):
        self.ready = False
        self.build = None
        self.build_idx = 0
        self.target = -1           # target group index (leader's own choice)
        self.target_score = 0.0
        self.avail = None          # per group: round at which group is expected alive
        self.reward_ready = None   # per group: last seen reward-available round
        self.wait_turns = 0
        self.wait_target = -1
        self.stuck = 0
        self.squad_id = 0
        self.healing = False
        self.my_index = 0
        self.hazard = None
        self.why = 0

    # ------------------------------------------------------------------ setup
    def init_static(self):
        me = cambc.me()
        self.static_blocked = (game_map.walls() | game_map.holes() | game_map.altars()
                               | game_map.spawn_region(Team.ENEMY))
        self.ally_spawn = game_map.spawn_region(Team.ALLY)
        self.altars = list(game_map.altars().positions())
        adj = Bitboard()
        for a in self.altars:
            adj |= tiles_around(a, 1)
        adj &= ~self.static_blocked
        self.altar_adj = list(adj.positions())
        self.groups = []
        for i, group in enumerate(game_map.camp_groups()):
            g = GroupInfo()
            g.idx = i
            g.group = group
            g.tiles = group.spawn_tiles()
            g.positions = list(g.tiles.positions())
            g.gems = group.gem_value()
            g.gold = group.gold_value()
            hp = s = mx = rg = 0
            for camp in group.camps():
                st = CAMP_STATS.get(int(camp.kind()), (2000, 60, 4))
                hp += st[0]
                s += st[1]
                mx = max(mx, st[1])
                rg = max(rg, st[2])
            g.hp, g.sum_str, g.max_str, g.max_range = hp, s, mx, rg
            g.free = s == 0
            g.respawn = group.max_respawn_timer()
            self.groups.append(g)
        self.avail = [0] * len(self.groups)
        self.hazard_until = [-1] * len(self.groups)
        self.pos_group = {}
        for g in self.groups:
            for p in g.positions:
                self.pos_group[(p.x, p.y)] = g.idx
        if DEBUG:
            for g in self.groups:
                print("G", g.idx, [(int(c), int(c.kind()), c.spawn_position().x, c.spawn_position().y) for c in g.group.camps()], g.gems, g.gold)
        self.reward_ready = [-1000] * len(self.groups)
        name = int(me.champion_name())
        self.ranged = me.attack_range() > 1
        if name == WILLOW:
            self.build = HEALER_BUILD
        elif self.ranged:
            self.build = RANGED_BUILD
        else:
            self.build = MELEE_BUILD
        self.ready = True

    # -------------------------------------------------------------- knowledge
    def update_knowledge(self, now):
        visible = cambc.vision.visible_tiles()
        for g in self.groups:
            if (g.tiles & visible).is_empty():
                continue
            try:
                state = g.group.state()
            except Exception:
                continue
            if isinstance(state, game_map.CampGroupRespawning):
                self.avail[g.idx] = now + state.timer
            elif isinstance(state, game_map.CampGroupRewardAvailable):
                self.avail[g.idx] = 0
                self.reward_ready[g.idx] = now
            else:
                self.avail[g.idx] = 0

    def team_info(self):
        allies = cambc.champions(Team.ALLY)
        alive = []
        for c in allies:
            try:
                if c.is_alive():
                    alive.append(c)
            except Exception:
                alive.append(c)
        # Squads: with enough bodies alive, split by roster parity into two balls.
        squad_id, squad = 0, alive
        if SPLIT and len(alive) >= SPLIT_MIN:
            try:
                me = cambc.me()
                sq = ([], [])
                for c in alive:
                    sq[allies.index(c) % 2].append(c)
                if len(sq[0]) >= 2 and len(sq[1]) >= 2:
                    squad_id = allies.index(me) % 2
                    squad = sq[squad_id]
            except Exception:
                squad_id, squad = 0, alive
        self.squad_id = squad_id
        alive = squad
        dps = 0.0
        hp = 0.0
        for c in alive:
            try:
                dps += c.strength() + c.focus() * 0.2
            except Exception:
                try:
                    bs = c.base_stats()
                    dps += bs.base_strength + bs.base_focus * 0.2
                except Exception:
                    dps += 50
            try:
                hp += c.health()
            except Exception:
                try:
                    hp += c.base_stats().base_health * 0.8
                except Exception:
                    hp += 800
        return allies, alive, max(dps, 30.0), hp

    # ------------------------------------------------------------- targeting
    def choose_target(self, now, dist_field, visited, dps, team_hp, n_alive, exclude=-1):
        best, best_score = -1, 0.0
        cur_score = -1.0
        for g in self.groups:
            if g.idx == exclude:
                continue
            travel = None
            for p in g.positions:
                if visited.is_set(p):
                    d = dist_field.get(p)
                    if travel is None or d < travel:
                        travel = d
            if travel is None:
                continue
            if self.hazard_until[g.idx] >= now:
                continue
            reward_known = now - self.reward_ready[g.idx] <= 3
            wait = self.avail[g.idx] - now - travel
            if wait > 25:
                continue
            wait = max(0, wait)
            if reward_known:
                clear = 0.0
                danger = 0.0
            else:
                clear = g.hp / dps
                # Damage the team soaks: camps die one at a time, so roughly half the time all alive.
                danger = g.sum_str * clear * 0.6
            if danger > team_hp * 0.55:
                continue
            value = g.gems + g.gold * 0.12
            if value <= 0:
                continue
            score = value / (travel + clear + wait + 6.0)
            if g.idx == self.target:
                cur_score = score
            if score > best_score:
                best, best_score = g.idx, score
        if self.target >= 0 and cur_score > 0 and best_score < cur_score * 1.35:
            return self.target, cur_score
        return best, best_score

    # -------------------------------------------------------------- movement
    def dynamic_blocked(self):
        blocked = (self.static_blocked | cambc.vision.champion_tiles()
                   | cambc.vision.camp_tiles() | cambc.vision.teleport_tiles())
        blocked.set(cambc.me().position(), False)
        return blocked

    def move_to_goals(self, goals, blocked=None, avoid=True):
        me = cambc.me()
        origin = me.position()
        if not me.can_move() or goals.is_set(origin):
            return False
        if blocked is None:
            blocked = self.dynamic_blocked()
        if avoid and self.hazard is not None and not self.hazard.is_empty():
            blocked = blocked | self.hazard
            blocked.set(origin, False)
        goals = goals & (~blocked | cambc.vision.camp_tiles())
        if goals.is_empty():
            return False
        reachable = blocked.reachable_tiles(origin, 1)
        best = origin
        for attempt in range(2):
            walls = blocked & ~goals
            if attempt == 1:
                # Allies move: path through them, but only step onto free tiles.
                walls = walls & ~cambc.vision.champion_tiles(Team.ALLY)
            field = DistanceField()
            seen = Bitboard()
            field.compute_to(walls, goals, tiles_around(origin, 0), seen)
            if not seen.is_set(origin):
                continue
            best_d = field.get(origin)
            for p in reachable.positions():
                if seen.is_set(p):
                    d = field.get(p)
                    if d < best_d:
                        best, best_d = p, d
            if best != origin:
                break
        if best == origin:
            return False
        try:
            return me.move_absolute(best)
        except Exception:
            return False

    def retreat(self, threats):
        me = cambc.me()
        if not me.can_move() or not threats:
            return False
        origin = me.position()
        blocked = self.dynamic_blocked()
        reachable = blocked.reachable_tiles(origin, 1)
        best, best_v = origin, None
        for p in [origin] + list(reachable.positions()):
            v = 0
            for pos, rng in threats:
                d = cheb(p, pos)
                v += min(d - rng, 3) * 10 + d
            if self.ally_spawn.is_set(p):
                v += 5
            if best_v is None or v > best_v:
                best, best_v = p, v
        if best != origin:
            try:
                return me.move_absolute(best)
            except Exception:
                return False
        return False

    # ---------------------------------------------------------------- combat
    def try_attack(self, target):
        me = cambc.me()
        try:
            if (me.can_attack() and target.is_visible() and target.health() > 0
                    and me.attack_tiles().is_set(target.position())):
                me.attack(target)
                return True
        except Exception:
            pass
        return False

    def cast_offensive(self, target, moved):
        """Cast a damage / stun spell on target; returns True on success."""
        me = cambc.me()
        for ab in me.abilities():
            try:
                if not ab.is_ready():
                    continue
                info = ab.info()
                if info is None:
                    continue
                if moved and getattr(info, "exclusive_with_movement", False):
                    continue
                if ab.is_damage() or ab.is_cc():
                    is_champ = isinstance(target, cambc.Champion)
                    if is_champ and not ab.can_target_enemies():
                        continue
                    if not is_champ and not ab.can_target_camps():
                        continue
                    if cheb(me.position(), target.position()) > int(info.range):
                        continue
                    if ab.use(target):
                        return True
                elif ab.is_aoe_damage():
                    if cheb(me.position(), target.position()) > int(info.range):
                        continue
                    if ab.use(target.position()):
                        return True
            except Exception:
                continue
        return False

    def cast_support(self, in_combat, attacked):
        """Heal allies, shield self, reset attacks."""
        me = cambc.me()
        for ab in me.abilities():
            try:
                if not ab.is_ready():
                    continue
                if ab.is_heal():
                    info = ab.info()
                    best, best_missing = None, 0.0
                    for c in cambc.vision.champions(Team.ALLY):
                        if c == me:
                            continue
                        try:
                            missing = c.max_health() - c.health()
                            if c.health() <= 0:
                                continue
                        except Exception:
                            continue
                        if cheb(me.position(), c.position()) <= int(info.range) and missing > best_missing:
                            best, best_missing = c, missing
                    if best is not None and best_missing >= me.focus() * 1.5:
                        if ab.use(best):
                            return True
                elif ab.is_shield():
                    if in_combat and me.health() < me.max_health() * 0.85:
                        if ab.use(None):
                            return True
                elif ab.is_attack_reset():
                    if attacked:
                        if ab.use(None):
                            return True
            except Exception:
                continue
        return False

    def buy_items(self):
        me = cambc.me()
        for _ in range(12):
            if self.build_idx >= len(self.build):
                return
            item = self.build[self.build_idx]
            try:
                if me.gold_count() < item.cost() or not me.can_buy(item, 1):
                    return
                me.buy(item, 1)
                self.build_idx += 1
            except Exception:
                self.build_idx += 1

    def note_stuck(self, gi, now):
        # Repeatedly unable to approach a target (blocked chokepoint, enemy parked on
        # the path...): give up on it for a while so the leader picks another.
        self.stuck += 1
        if self.stuck >= 6:
            self.hazard_until[gi] = now + 40
            self.target = -1
            self.stuck = 0

    # --------------------------------------------------------------- the turn
    def play_turn(self):
        if not self.ready:
            self.init_static()
        me = cambc.me()
        now = cambc.round_number()

        if not me.is_alive():
            try:
                self.buy_items()
            except Exception:
                pass
            self.why = 366; return

        self.update_knowledge(now)
        allies, alive, dps, team_hp = self.team_info()
        my_pos = me.position()
        slot = 0 if self.squad_id == 0 else 5
        other_slot = 5 if self.squad_id == 0 else 0

        # Leader = first living squad member in roster order.
        leader = alive[0] if alive else me
        is_leader = leader == me
        try:
            me.set_priority((100 if self.squad_id == 0 else 90) if is_leader else 10)
        except Exception:
            pass

        # Awake camps: each projects a hazard zone over the tiles it can hit.
        awake = []   # (camp, group idx, range, strength)
        try:
            for camp in cambc.vision.camps():
                try:
                    if camp.is_awake() and camp.health() > 0:
                        st = CAMP_STATS.get(int(camp.kind()), (0, 60, 4))
                        if st[1] > 0:
                            sp = camp.spawn_position()
                            gi = self.pos_group.get((sp.x, sp.y), -1)
                            awake.append((camp, gi, st[2], camp.strength()))
                except Exception:
                    continue
        except Exception:
            pass
        zones = []
        for camp, gi, rng, stren in awake:
            zone = tiles_around(camp.position(), rng + 1)
            zones.append((zone, gi))
            for g in self.groups:
                if g.idx != gi and not (g.tiles & zone).is_empty():
                    self.hazard_until[g.idx] = now + 3

        # Distance field from me over static terrain (cheap native op).
        dist_field = DistanceField()
        visited = Bitboard()
        dist_field.compute(self.static_blocked, tiles_around(my_pos, 0), visited)

        # Plan: leader computes and publishes, followers read.
        target = -1
        if is_leader:
            # Respawn reports from followers (they may see what we cannot).
            try:
                rep = bytearray(3)
                cambc.shared_memory.read(2, rep)
                if rep[0] > 0 and (now - rep[2]) & 0xFF <= 2 and rep[0] - 1 < len(self.groups):
                    gi = rep[0] - 1
                    self.avail[gi] = max(self.avail[gi], now + rep[1])
                    if self.target == gi:
                        self.target = -1
            except Exception:
                pass
            exclude = -1
            try:
                od = bytearray(2)
                cambc.shared_memory.read(other_slot, od)
                if (now - od[1]) & 0xFF <= 2 and od[0] > 0:
                    exclude = od[0] - 1
            except Exception:
                exclude = -1
            if exclude == self.target and self.squad_id == 1:
                self.target = -1
            target, score = self.choose_target(now, dist_field, visited, dps, team_hp, len(alive),
                                               exclude if self.squad_id == 1 or self.target != exclude else -1)
            self.target, self.target_score = target, score
            try:
                cambc.shared_memory.write(slot, bytes([(target + 1) & 0xFF, now & 0xFF]))
            except Exception:
                pass
        else:
            try:
                data = bytearray(2)
                cambc.shared_memory.read(slot, data)
                if (now - data[1]) & 0xFF <= 3 and data[0] > 0:
                    target = data[0] - 1
            except Exception:
                target = -1
            if 0 <= target < len(self.groups) and self.hazard_until[target] >= now:
                target = -1
            if target < 0 or target >= len(self.groups):
                target, score = self.choose_target(now, dist_field, visited, dps, team_hp, len(alive))
                self.target = target
            elif not visited.is_set(self.groups[target].positions[0]) and not any(
                    visited.is_set(p) for p in self.groups[target].positions):
                target, score = self.choose_target(now, dist_field, visited, dps, team_hp, len(alive))
                self.target = target

        if DEBUG and now % 20 == 0:
            print("R", now, "lead" if is_leader else "fol", int(me.champion_name()), "tgt", target,
                  "pos", my_pos.x, my_pos.y, "hp", int(me.health()), "gems", me.gem_count(), "gold", me.gold_count(),
                  "rec", me.is_recalling(), "sub", me.is_submitting_gems(),
                  "awake", [(c.position().x, c.position().y, gi) for c, gi, r, st in awake],
                  "hz", [(int(z.count()), gi) for z, gi in zones], "why", self.why, "heal", self.healing, "cm", me.can_move(), "ca", me.can_attack())
        hazard = Bitboard()
        for zone, gi in zones:
            if gi != target:
                hazard |= zone
        self.hazard = hazard

        if me.is_recalling() or me.is_submitting_gems() or me.is_teleporting():
            self.why = 446; return
        if not me.can_move() and not me.can_attack() and not me.can_cast():
            self.why = 448; return

        # Standing where a non-target awake camp can hit us: leave first.
        if hazard.is_set(my_pos) and me.can_move():
            blocked = self.dynamic_blocked()
            if self.move_to_goals(~hazard & ~blocked, blocked, avoid=False):
                self.why = 454; return

        at_spawn = self.ally_spawn.is_set(my_pos)
        if at_spawn:
            self.buy_items()

        hp, max_hp = me.health(), me.max_health()

        # Threats: awake camps and visible enemies.
        threats = []
        incoming = 0.0
        for camp, gi, rng, stren in awake:
            try:
                threats.append((camp.position(), rng))
                if cheb(camp.position(), my_pos) <= rng:
                    incoming += stren
            except Exception:
                pass
        enemies = []
        try:
            enemies = [e for e in cambc.vision.champions(Team.ENEMY) if e.health() > 0]
        except Exception:
            enemies = []
        for e in enemies:
            try:
                if cheb(e.position(), my_pos) <= 4:
                    threats.append((e.position(), e.attack_range() + 1))
                    incoming += e.strength()
            except Exception:
                pass

        # Heal up at spawn before leaving.
        if at_spawn and self.healing:
            if hp >= max_hp * 0.92 or not threats == []:
                self.healing = False
            else:
                self.why = 490; return
        # Low HP: retreat out of range, then recall.
        low = hp < max(max_hp * 0.3, incoming * 2.5)
        if low and not at_spawn:
            in_danger = any(cheb(p, my_pos) <= r + 1 for p, r in threats)
            if in_danger:
                # Use shield / heal if available before running.
                self.cast_support(True, False)
                self.retreat(threats)
                self.why = 499; return
            if hp < max_hp * 0.5:
                try:
                    me.recall()
                    self.healing = True
                except Exception:
                    pass
                self.why = 506; return
        if at_spawn and hp < max_hp * 0.6:
            self.healing = True
            self.why = 509; return

        moved = False
        attacked = False

        # 1) Enemy champions in range: focus the weakest.
        if enemies:
            in_range = []
            for e in enemies:
                try:
                    if e.is_visible() and me.attack_tiles().is_set(e.position()):
                        in_range.append(e)
                except Exception:
                    pass
            try:
                spell_targets = [e for e in enemies if cheb(e.position(), my_pos) <= 4]
                if spell_targets:
                    weakest = min(spell_targets, key=lambda e: e.health())
                    self.cast_offensive(weakest, False)
                if in_range:
                    weakest = min(in_range, key=lambda e: e.health())
                    if self.try_attack(weakest):
                        attacked = True
                        self.cast_support(True, True)
                        self.try_attack(weakest)
                        self.why = 534; return
            except Exception:
                pass

        # 2) Tribute when the bag justifies it.
        gems = me.gem_count()
        if gems > 0 and self.altars:
            near_d = None
            for p in self.altar_adj:
                if visited.is_set(p):
                    d = dist_field.get(p)
                    if near_d is None or d < near_d:
                        near_d = d
            if near_d is None:
                want = False
            else:
                want = (gems >= TRIBUTE_GEMS or now >= END_ROUND or near_d <= 2
                        or (gems >= 8 and near_d <= 6))
            if want:
                # Submit at the closest reachable unlocked altar.
                for a in self.altars:
                    if cheb(a, my_pos) <= 1:
                        try:
                            if not cambc.vision.has_altar_lock(a):
                                me.submit_gems(a)
                                self.why = 555; return
                        except Exception:
                            pass
                goals = Bitboard()
                for a in self.altars:
                    try:
                        if cambc.vision.has_altar_lock(a):
                            continue
                    except Exception:
                        pass
                    goals |= tiles_around(a, 1)
                if self.move_to_goals(goals):
                    moved = True
                    self.why = 568; return

        # 2b) Shopping trip: recall to spend a pile of gold when not mid-fight.
        if (not at_spawn and gems <= 3 and not threats and now < END_ROUND - 80
                and self.build_idx < len(self.build) and me.gold_count() >= SHOP_GOLD):
            engaged = False
            if target >= 0:
                for p in self.groups[target].positions:
                    if cheb(p, my_pos) <= 7:
                        engaged = True
                        break
            if not engaged:
                try:
                    me.recall()
                    self.healing = True
                    self.why = 1001; return
                except Exception:
                    pass

        # 3) Farm the team target.
        if target < 0:
            # Nothing worth doing: wait at spawn / heal.
            if not at_spawn:
                self.move_to_goals(self.ally_spawn)
            self.why = 575; return
        g = self.groups[target]
        # Visible alive camps of the target group.
        group_camps = []
        try:
            for camp in cambc.vision.camps():
                try:
                    if g.tiles.is_set(camp.spawn_position()) and camp.health() > 0:
                        group_camps.append(camp)
                except Exception:
                    continue
        except Exception:
            group_camps = []

        group_visible = not (g.tiles & cambc.vision.visible_tiles()).is_empty()
        if group_visible and not group_camps:
            # Group cleared (or respawning): capture by standing on a spawn tile.
            try:
                state = g.group.state()
            except Exception:
                state = None
            if isinstance(state, game_map.CampGroupRewardAvailable):
                if g.tiles.is_set(my_pos):
                    self.why = 598; return
                if not self.move_to_goals(g.tiles):
                    # Tiles full: stay close.
                    self.move_to_goals(tiles_around(g.positions[0], 2) & ~g.tiles)
                self.why = 602; return
            if isinstance(state, game_map.CampGroupRespawning):
                # Leader will pick a new target next turn; tell it what we see.
                self.avail[g.idx] = now + state.timer
                if is_leader:
                    self.target = -1
                else:
                    try:
                        cambc.shared_memory.write(2, bytes([g.idx + 1, min(255, max(0, state.timer)), now & 0xFF]))
                    except Exception:
                        pass
                # Never block the respawn by standing on its spawn tiles.
                if g.tiles.is_set(my_pos):
                    self.move_to_goals(~g.tiles & ~self.static_blocked)
                self.why = 606; return
            if DEBUG:
                print("odd state", now, target, state)

        if not group_camps:
            if self.move_to_goals(g.tiles):
                self.stuck = 0
            else:
                self.note_stuck(g.idx, now)
            self.why = 610; return

        # Engagement gate: wait for the ball before waking a dangerous sleeping group.
        any_awake = False
        for c in group_camps:
            try:
                if c.is_awake():
                    any_awake = True
                    break
            except Exception:
                pass
        if not any_awake and g.max_str > 20:
            near = 0
            for c in alive:
                try:
                    if cheb(c.position(), my_pos) <= 5:
                        near += 1
                except Exception:
                    pass
            needed = min(len(alive), 3)
            if self.wait_target != target:
                self.wait_target, self.wait_turns = target, 0
            if near < needed and self.wait_turns < 12:
                self.wait_turns += 1
                # Hold position just outside aggro ranges (sleeping camps don't attack anyway).
                dmin = min(cheb(c.position(), my_pos) for c in group_camps)
                if dmin > g.max_range + 2:
                    self.move_to_goals(tiles_around(group_camps[0].position(), g.max_range + 2))
                self.why = 636; return

        # Choose camp: lowest health in attack range; else nearest.
        in_range = []
        try:
            atk = me.attack_tiles()
            in_range = [c for c in group_camps if atk.is_set(c.position())]
        except Exception:
            pass
        if in_range:
            focus = min(in_range, key=lambda c: c.health())
        else:
            focus = min(group_camps, key=lambda c: (cheb(c.position(), my_pos), c.health()))

        # Spells first (before moving: some spells exclude walking).
        if self.cast_offensive(focus, False):
            pass
        if in_range:
            if self.try_attack(focus):
                attacked = True
                if self.cast_support(True, True):
                    self.try_attack(focus)
            else:
                self.cast_support(True, False)
            if not self.ranged and not attacked:
                pass
            self.why = 663; return

        # Move into range of the focus camp.
        rng = me.attack_range()
        goals = Bitboard()
        for c in group_camps:
            goals |= tiles_around(c.position(), rng)
        moved = self.move_to_goals(goals)
        if moved:
            self.stuck = 0
        elif any_awake is False:
            self.note_stuck(g.idx, now)
        self.cast_support(any_awake, False)
        if not self.ranged:
            try:
                atk = me.attack_tiles()
                for c in sorted(group_camps, key=lambda c: c.health()):
                    if atk.is_set(c.position()):
                        if self.try_attack(c):
                            if self.cast_support(True, True):
                                self.try_attack(c)
                        break
            except Exception:
                pass
