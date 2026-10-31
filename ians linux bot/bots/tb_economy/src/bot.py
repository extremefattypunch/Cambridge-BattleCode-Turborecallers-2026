"""tb_economy champion logic: safe farming, smart targets, items and abilities."""
import cambc
from cambc import game_map

Team, Item = cambc.Team, cambc.ItemType
CT = cambc.ChampionType

# kind -> (hp, strength, range)
CAMP_STATS = {0: (1350, 20, 3), 1: (2400, 60, 4), 2: (120, 0, 0), 3: (120, 0, 0),
              4: (20000, 200, 5), 5: (5000, 120, 4)}

MELEE_TANKS = (CT.RYTH, CT.VENDETTA, CT.ISSAC, CT.MARCELLA, CT.REN, CT.VARG, CT.HEART_OF_RUIN)
CASTERS = (CT.STELLAR, CT.PRISM)

FAR = 100000
DEBUG = False

# Tunables
TRIBUTE_GEMS = 25
GOLD_W = 0.12
DANGER_MULT = 3.0
TRIBUTE_NEAR = 6
LOW_HP = 0.35
ENGAGE_HP = 0.55
HOLD_MAX = 25


def build_for(kind):
    if kind in MELEE_TANKS:
        return ([Item.JUNGLE_SHARD_OF_HEALTH] * 5 + [Item.MONSTER_SHARD_OF_STRENGTH] * 5
                + [Item.DURABILITY_SHARD_OF_HEALTH] * 5), Item.POWER_SHARD_OF_STRENGTH
    if kind in CASTERS:
        return ([Item.JUNGLE_SHARD_OF_HEALTH] * 5 + [Item.MONSTER_SHARD_OF_FOCUS] * 5), Item.POWER_SHARD_OF_FOCUS
    return ([Item.JUNGLE_SHARD_OF_HEALTH] * 5 + [Item.MONSTER_SHARD_OF_STRENGTH] * 5), Item.POWER_SHARD_OF_STRENGTH


def tiles_around(position, radius):
    tiles = cambc.Bitboard()
    tiles.draw_chebyshev(position, radius)
    return tiles


class GroupInfo:
    __slots__ = ("group", "index", "tiles", "positions", "gems", "gold", "hp", "strength", "rng", "center")

    def __init__(self, group, index):
        self.group = group
        self.index = index
        self.tiles = group.spawn_tiles()
        self.positions = self.tiles.positions()
        self.gems = group.gem_value()
        self.gold = group.gold_value()
        hp = st = rng = 0
        for camp in group.camps():
            try:
                k = int(camp.kind())
            except Exception:
                k = 0
            h, s, r = CAMP_STATS.get(k, (1350, 20, 3))
            hp += h
            st += s
            rng = max(rng, r)
        self.hp, self.strength, self.rng = hp, st, rng
        self.center = self.positions[0]


class Bot:
    def __init__(self):
        self.inited = False
        self.kind = None
        self.build = None
        self.build_idx = 0
        self.tail_item = None
        self.groups = []
        self.respawn_until = {}
        self.target = None
        self.static_blocked = None
        self.altars = []
        self.spawn = None
        self.melee = False
        self.slot = 0
        self.retreating = False
        self.need = 0
        self.alive_allies = []
        self.leader_slot = 0
        self.hold = 0

    # ------------------------------------------------------------------ setup
    def init(self, me):
        self.kind = me.champion_name()
        self.build, self.tail_item = build_for(self.kind)
        self.melee = me.attack_range() <= 1
        self.static_blocked = (game_map.walls() | game_map.holes() | game_map.altars()
                               | game_map.spawn_region(Team.ENEMY))
        self.altars = game_map.altars().positions()
        self.spawn = game_map.spawn_region(Team.ALLY)
        self.groups = [GroupInfo(g, i) for i, g in enumerate(game_map.camp_groups())]
        try:
            ids = sorted(int(c) for c in cambc.champions(Team.ALLY))
            self.slot = ids.index(int(me)) % 8
        except Exception:
            self.slot = 0
        self.inited = True

    # ------------------------------------------------------------------ shop
    def buy_items(self, me):
        for _ in range(40):
            if self.build_idx < len(self.build):
                item = self.build[self.build_idx]
            else:
                item = self.tail_item
            try:
                if not me.can_buy(item, 1):
                    return
                me.buy(item, 1)
            except Exception:
                return
            self.build_idx += 1

    # ------------------------------------------------------------------ helpers
    def ally_list(self):
        out = []
        for c in self.alive_allies:
            try:
                c.position()
                out.append(c)
            except Exception:
                pass
        return out

    def blocked_now(self, me):
        blocked = (self.static_blocked | cambc.vision.champion_tiles()
                   | cambc.vision.camp_tiles() | cambc.vision.teleport_tiles())
        blocked.set(me.position(), False)
        return blocked

    def move_to_goals(self, me, goals):
        origin = me.position()
        if not me.can_move() or goals.is_set(origin):
            return False
        blocked = self.blocked_now(me)
        goals = goals & (~blocked | cambc.vision.camp_tiles())
        if goals.is_empty():
            return False
        field = cambc.DistanceField()
        field.compute_to(blocked & ~goals, goals, tiles_around(origin, 0), cambc.Bitboard())
        reachable = blocked.reachable_tiles(origin, me.base_stats().base_move_speed)
        cur = field.get(origin)
        best = origin
        bestd = cur
        for p in reachable.positions():
            d = field.get(p)
            if d < bestd:
                best, bestd = p, d
        if best == origin:
            return False
        # Try a dash for long trips.
        if bestd > 3 and self.try_dash_towards(me, field, blocked):
            return True
        try:
            return me.move_absolute(best)
        except Exception:
            return False

    def try_dash_towards(self, me, field, blocked):
        try:
            for ab in me.abilities():
                if not ab.is_dash() or not ab.is_ready():
                    continue
                info = ab.info()
                if getattr(info, "modifier", 0) > 0:
                    return False  # landing-damage dash (Heart of Ruin) saved for fights
                origin = me.position()
                cur = field.get(origin)
                cands = tiles_around(origin, 2) & ~blocked
                best, bestd = None, cur - 1
                for p in cands.positions():
                    d = field.get(p)
                    if d < bestd:
                        best, bestd = p, d
                if best is not None:
                    return bool(ab.use(best))
        except Exception:
            pass
        return False

    def threats(self, me):
        """Awake visible camps that can hit me plus nearby enemy champions."""
        pos = me.position()
        out = []
        try:
            for camp in cambc.vision.camps():
                if camp.is_awake() and camp.strength() > 0:
                    if pos.chebyshev_distance(camp.position()) <= camp.attack_range() + 1:
                        out.append(camp)
        except Exception:
            pass
        try:
            for ch in cambc.vision.champions(Team.ENEMY):
                if ch.is_alive() and pos.chebyshev_distance(ch.position()) <= 4:
                    out.append(ch)
        except Exception:
            pass
        return out

    def flee(self, me, threats):
        if not me.can_move():
            return False
        pos = me.position()
        blocked = self.blocked_now(me)
        reachable = blocked.reachable_tiles(pos, 1)
        best, bestscore = None, None
        for p in [pos] + reachable.positions():
            score = 0
            for t in threats:
                d = p.chebyshev_distance(t.position())
                try:
                    r = t.attack_range()
                except Exception:
                    r = 3
                score += min(d - r - 1, 0) * 10 + min(d, 8)
            if self.spawn.is_set(p):
                score += 50
            if bestscore is None or score > bestscore:
                best, bestscore = p, score
        if best is not None and best != pos:
            try:
                return me.move_absolute(best)
            except Exception:
                return False
        return False

    # ------------------------------------------------------------------ abilities
    def cast_support(self, me, threats):
        """Shield / heal / stun before attacking."""
        if not me.can_cast():
            return
        pos = me.position()
        hpfrac = me.health() / max(1.0, me.max_health())
        for ab in me.abilities():
            try:
                if not ab.is_ready():
                    continue
                if ab.is_shield():
                    if threats and hpfrac < 0.9:
                        if ab.use(None):
                            return
                elif ab.is_heal():
                    best, bestf = None, 0.65
                    for ally in self.ally_list():
                        if int(ally) == int(me) or not ally.is_alive():
                            continue
                        if pos.chebyshev_distance(ally.position()) > 4:
                            continue
                        f = ally.health() / max(1.0, ally.max_health())
                        if f < bestf:
                            best, bestf = ally, f
                    if best is not None and ab.use(best):
                        return
                elif ab.is_cc():
                    # Stun the strongest awake attacker in range (or an enemy champion).
                    best, bests = None, 0
                    for t in threats:
                        if pos.chebyshev_distance(t.position()) > 4:
                            continue
                        try:
                            s = t.strength()
                        except Exception:
                            s = 0
                        if isinstance(t, cambc.Champion):
                            s += 50
                        if s > bests:
                            best, bests = t, s
                    if best is not None and ab.use(best):
                        return
            except Exception:
                pass

    def cast_damage(self, me, target_group):
        """Single-target and AoE damage on camps of our target / enemy champions."""
        if not me.can_cast():
            return False
        pos = me.position()
        try:
            camps = [c for c in cambc.vision.camps() if c.is_alive() and c.health() > 0]
        except Exception:
            camps = []
        tg_tiles = target_group.tiles if target_group is not None else None
        enemies = []
        try:
            enemies = [e for e in cambc.vision.champions(Team.ENEMY) if e.is_alive()]
        except Exception:
            pass
        for ab in me.abilities():
            try:
                if not ab.is_ready():
                    continue
                if ab.is_damage() or (ab.is_cc() and getattr(ab.info(), "modifier", 0) > 0 and False):
                    rng = ab.info().range
                    best, bestv = None, -1
                    for e in enemies:
                        if pos.chebyshev_distance(e.position()) <= rng:
                            v = 5000 - e.health()
                            if v > bestv:
                                best, bestv = e, v
                    for c in camps:
                        if pos.chebyshev_distance(c.position()) > rng:
                            continue
                        if not (c.is_awake() or (tg_tiles is not None and tg_tiles.is_set(c.spawn_position()))):
                            continue
                        v = 1000 + (c.max_health() - c.health()) / 10.0
                        if v > bestv:
                            best, bestv = c, v
                    if best is not None:
                        if self.melee and ab.info().exclusive_with_movement:
                            # Only if we already have something in melee reach.
                            if not any(pos.chebyshev_distance(c.position()) <= 1 for c in camps) and \
                                    not any(pos.chebyshev_distance(e.position()) <= 1 for e in enemies):
                                continue
                        if ab.use(best):
                            return True
                elif ab.is_aoe_damage():
                    info = ab.info()
                    rng = int(info.range)
                    rad = int(info.radius) if info.radius else 1
                    units = []
                    for c in camps:
                        if c.is_awake() or (tg_tiles is not None and tg_tiles.is_set(c.spawn_position())):
                            units.append(c.position())
                    for e in enemies:
                        units.append(e.position())
                    if not units:
                        continue
                    best, bestn = None, 0
                    cands = tiles_around(pos, rng)
                    for u in units:
                        if pos.chebyshev_distance(u) > rng + rad:
                            continue
                        for dx in range(-rad, rad + 1):
                            for dy in range(-rad, rad + 1):
                                p = cambc.Vec2(u.x + dx, u.y + dy)
                                if not game_map.is_in_bounds(p) or not cands.is_set(p):
                                    continue
                                n = 0
                                for w in units:
                                    if p.chebyshev_distance(w) <= rad:
                                        n += 1
                                if n > bestn:
                                    best, bestn = p, n
                    if best is not None:
                        if self.melee and info.exclusive_with_movement:
                            if not any(pos.chebyshev_distance(c.position()) <= 1 for c in camps):
                                continue
                        if ab.use(best):
                            return True
                elif ab.is_cc():
                    rng = ab.info().range
                    best, bestv = None, -1
                    for c in camps:
                        if pos.chebyshev_distance(c.position()) > rng:
                            continue
                        if not (c.is_awake() or (tg_tiles is not None and tg_tiles.is_set(c.spawn_position()))):
                            continue
                        v = c.strength()
                        if v > bestv:
                            best, bestv = c, v
                    for e in enemies:
                        if pos.chebyshev_distance(e.position()) <= rng:
                            best, bestv = e, 9999
                    if best is not None:
                        if self.melee and ab.info().exclusive_with_movement:
                            if not any(pos.chebyshev_distance(c.position()) <= 1 for c in camps):
                                continue
                        if ab.use(best):
                            return True
                elif ab.is_dash() and getattr(ab.info(), "modifier", 0) > 0 and target_group is not None:
                    # Heart of Ruin: landing damage + stun onto our target's camps.
                    units = [c.position() for c in camps if tg_tiles.is_set(c.spawn_position()) or c.is_awake()]
                    if not units:
                        continue
                    blocked = self.blocked_now(me)
                    best, bestn = None, 0
                    for p in (tiles_around(pos, 2) & ~blocked).positions():
                        n = sum(1 for u in units if p.chebyshev_distance(u) <= 1)
                        if n > bestn:
                            best, bestn = p, n
                    if best is not None and ab.use(best):
                        return True
            except Exception:
                pass
        return False

    def attack_best(self, me, target_group):
        """Basic attack: enemy champion (low hp) or camp (prefer target group, low hp)."""
        if not me.can_attack():
            return False
        tiles = me.attack_tiles()
        best, bestv = None, None
        try:
            for e in cambc.vision.champions(Team.ENEMY):
                if e.is_alive() and tiles.is_set(e.position()):
                    v = 100000 - e.health()
                    if bestv is None or v > bestv:
                        best, bestv = e, v
        except Exception:
            pass
        tg = target_group.tiles if target_group is not None else None
        try:
            for c in cambc.vision.camps():
                if not c.is_alive() or c.health() <= 0 or not tiles.is_set(c.position()):
                    continue
                ours = tg is not None and tg.is_set(c.spawn_position())
                if not ours and not c.is_awake():
                    # Do not wake unrelated camps unless they are harmless.
                    if c.strength() > 0:
                        continue
                v = 50000 - c.health() + (20000 if ours else 0) + (30000 if c.strength() == 0 else 0)
                if bestv is None or v > bestv:
                    best, bestv = c, v
        except Exception:
            pass
        if best is None:
            return False
        try:
            me.attack(best)
        except Exception:
            return False
        # Attack reset for a double hit.
        try:
            for ab in me.abilities():
                if ab.is_attack_reset() and ab.is_ready() and me.can_cast():
                    if best.is_alive() and best.health() > 0 and ab.use(None):
                        if me.can_attack():
                            me.attack(best)
                    break
        except Exception:
            pass
        return True

    # ------------------------------------------------------------------ targeting
    def update_group_memory(self):
        r = cambc.round_number()
        visible = cambc.vision.visible_tiles()
        for gi in self.groups:
            if (gi.tiles & visible).is_empty():
                continue
            try:
                st = gi.group.state()
            except Exception:
                continue
            if isinstance(st, game_map.CampGroupRespawning):
                self.respawn_until[gi.index] = r + st.timer
            else:
                self.respawn_until.pop(gi.index, None)

    def my_dps(self, me):
        return max(20.0, me.strength()) + me.focus() * 0.2

    def ally_targets(self):
        out = {}
        try:
            data = bytearray(8)
            cambc.shared_memory.read(0, data)
            for i in range(8):
                if i != self.slot and data[i]:
                    out[data[i] - 1] = out.get(data[i] - 1, 0) + 1
        except Exception:
            pass
        return out

    def publish_target(self, gi):
        try:
            v = 0 if gi is None else (gi.index % 255) + 1
            cambc.shared_memory.write(self.slot, bytes([v]))
        except Exception:
            pass

    def choose_target(self, me):
        r = cambc.round_number()
        pos = me.position()
        field = cambc.DistanceField()
        roots = cambc.Bitboard()
        roots.set(pos)
        field.compute(self.static_blocked, roots, cambc.Bitboard())
        allies = self.ally_targets()
        n_allies = max(0, len(self.alive_allies) - 1)
        hp = me.health()
        dps = self.my_dps(me)
        jungle = 0.7 if self.build_idx >= 5 and self.build and self.build[0] == Item.JUNGLE_SHARD_OF_HEALTH else 1.0
        best, bestscore, bestneed = None, 0.0, 0
        fb, fbscore = None, None
        visible = cambc.vision.visible_tiles()
        leader = self.slot == self.leader_slot
        for gi in self.groups:
            ru = self.respawn_until.get(gi.index)
            d = FAR
            for p in gi.positions:
                v = field.get(p)
                if 0 <= v < d:
                    d = v
            if d > 10000:
                continue
            wait = 0
            if ru is not None and ru > r + max(0, d - 3):
                # Respawning: standing on its spawn tiles would delay it forever.
                continue
            helpers = allies.get(gi.index % 255, 0)
            remaining_hp = gi.hp
            if not (gi.tiles & visible).is_empty():
                try:
                    tot = 0.0
                    for c in gi.group.camps():
                        if c.is_visible() and c.is_alive():
                            tot += c.health()
                    remaining_hp = tot
                except Exception:
                    pass
            value = gi.gems + gi.gold * GOLD_W
            need = 0
            if gi.strength > 0:
                need = -1
                for h in range(0, n_allies + 1):
                    kill = remaining_hp / (dps * (1 + 0.9 * h))
                    danger = gi.strength * kill * jungle / (1 + 0.5 * h)
                    if danger <= hp * DANGER_MULT:
                        need = h
                        break
                if need < 0:
                    # Fallback candidate: least dangerous reachable fight.
                    if gi.strength < 200:
                        fsc = -remaining_hp * gi.strength - d
                        if fbscore is None or fsc > fbscore:
                            fb, fbscore = gi, fsc
                    continue
                if need > helpers and not leader and helpers == 0:
                    continue
            team = 1 + max(need, helpers)
            kill = remaining_hp / (dps * (1 + 0.9 * (team - 1)))
            score = value / (d + kill + max(0, wait) + 8.0) / (1 + 0.5 * max(0, need - helpers))
            if self.target is not None and gi.index == self.target.index:
                score *= 1.25
            if helpers:
                if need > 0:
                    score *= 1.0 + 0.3 * min(helpers, need)
                else:
                    score /= 1.0 + 0.6 * helpers
            if score > bestscore:
                best, bestscore, bestneed = gi, score, need
        if best is None and fb is not None:
            best, bestneed = fb, n_allies
        self.need = bestneed
        return best

    # ------------------------------------------------------------------ main
    def go_tribute(self, me):
        pos = me.position()
        goals = cambc.Bitboard()
        for altar in self.altars:
            try:
                if cambc.vision.has_altar_lock(altar):
                    continue
            except Exception:
                pass
            if pos.chebyshev_distance(altar) <= cambc.constants.SUBMIT_GEMS_RANGE:
                try:
                    me.submit_gems(altar)
                    return True
                except Exception:
                    continue
            goals |= tiles_around(altar, cambc.constants.SUBMIT_GEMS_RANGE)
        return self.move_to_goals(me, goals)

    def nearest_altar_dist(self, me):
        pos = me.position()
        return min((pos.chebyshev_distance(a) for a in self.altars), default=FAR)

    def play_turn(self):
        me = cambc.me()
        if not self.inited:
            self.init(me)

        if not me.is_alive():
            self.buy_items(me)
            self.target = None
            return
        if me.is_recalling() or me.is_submitting_gems() or me.is_teleporting():
            # Cancel a recall if we're being hit (it would be interrupted anyway).
            return

        pos = me.position()
        at_spawn = self.spawn.is_set(pos)
        if at_spawn:
            self.buy_items(me)

        self.update_group_memory()
        try:
            allies_all = sorted(cambc.champions(Team.ALLY), key=int)
            ids = [int(c) for c in allies_all]
            self.alive_allies = [c for c in allies_all if c.is_alive()]
            self.leader_slot = ids.index(int(self.alive_allies[0])) % 8 if self.alive_allies else 0
        except Exception:
            self.alive_allies = [me]
            self.leader_slot = self.slot
        hpfrac = me.health() / max(1.0, me.max_health())
        threats = self.threats(me)

        # Wait on spawn to heal before going back out.
        if at_spawn and hpfrac < 0.95 and not threats:
            return

        self.cast_support(me, threats)

        # Low health: get out of range, then recall.
        if hpfrac < LOW_HP and not at_spawn:
            self.target = None
            self.publish_target(None)
            hitting = [t for t in threats]
            if hitting:
                if me.gem_count() > 0 and self.nearest_altar_dist(me) <= 1:
                    self.go_tribute(me)
                    return
                self.attack_best(me, None) if not self.melee and not me.can_move() else None
                if not self.flee(me, hitting):
                    self.attack_best(me, None)
                return
            try:
                me.recall()
            except Exception:
                pass
            return

        gems = me.gem_count()
        r = cambc.round_number()
        want_tribute = gems > 0 and (gems >= TRIBUTE_GEMS or self.nearest_altar_dist(me) <= TRIBUTE_NEAR
                                     or r >= 1850 or (hpfrac < 0.5 and gems >= 10))

        target = self.target
        # Re-evaluate target every turn (cheap enough), with stickiness.
        try:
            target = self.choose_target(me)
        except Exception as e:
            print("choose err", e, flush=True)
        if (target is None) != (self.target is None) or (target is not None and target.index != self.target.index):
            self.hold = 0
        self.target = target
        self.publish_target(target)
        if DEBUG and target is not None and target.tiles.is_set(pos) and r % 10 == 0:
            try:
                print("ON", r, self.kind, pos, target.index, target.group.state(), target.group.capture_state(), self.respawn_until.get(target.index), flush=True)
            except Exception as e:
                print("ONERR", r, e, flush=True)
        if DEBUG and r % 100 == 0:
            print("dbg", r, self.kind, pos, "hp", int(me.health()), "gems", gems, "need", self.need, "hold", self.hold, "tgt",
                  None if target is None else (target.index, target.gems, target.hp, target.center), flush=True)

        # Fight things already in range first.
        self.cast_damage(me, target)
        attacked = self.attack_best(me, target)

        if want_tribute and not threats:
            if self.go_tribute(me):
                return
        if attacked and not self.melee:
            return
        if not me.can_move():
            return

        if target is None:
            if gems > 0:
                self.go_tribute(me)
            return

        # If target group is dead and capturable, stand on a spawn tile.
        goals = target.tiles.copy()
        try:
            alive = target.tiles & cambc.vision.camp_tiles()
            if not alive.is_empty():
                goals = alive
        except Exception:
            pass
        if hpfrac < ENGAGE_HP and target.strength > 0:
            # Not healthy enough to start a dangerous fight: go heal.
            engaged = any(not isinstance(t, cambc.Champion) for t in threats)
            if not engaged:
                if gems > 0:
                    self.go_tribute(me)
                    return
                try:
                    me.recall()
                except Exception:
                    pass
                return
        if target.strength > 0 and self.need > 0:
            near = 0
            for ally in self.ally_list():
                if int(ally) != int(me) and ally.is_alive() and pos.chebyshev_distance(ally.position()) <= 5:
                    near += 1
            dmin = min(pos.chebyshev_distance(p) for p in target.positions)
            awake = any(not isinstance(t, cambc.Champion) for t in threats)
            if near < self.need and not awake and dmin <= target.rng + 3 and self.hold < HOLD_MAX:
                self.hold += 1
                return
            if near >= self.need:
                self.hold = 0
        else:
            self.hold = 0
        moved = self.move_to_goals(me, goals)
        if moved:
            self.cast_damage(me, target)
            self.attack_best(me, target)
