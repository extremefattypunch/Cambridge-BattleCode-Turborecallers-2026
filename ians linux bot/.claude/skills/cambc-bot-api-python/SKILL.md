---
name: cambc-bot-api-python
description: Reference for writing, debugging and testing Python bots for Cambridge Battlecode 2026a (cambc) with `import cambc`. Use when editing anything under bots/*/src, calling the cambc SDK (Champion, Ability, Consumable, Camp, CampGroup, game_map, vision, draft, Bitboard, DistanceField, ItemType, constants, shared/draft memory), interpreting cambc.Error codes or action failures, optimising Python fuel use, or running the cambc CLI (run, run-batch, statistics, bundle, submit, view). Signatures were verified against sdk/python/_cambc.pyi and sdk/python/cambc/*.py and behaviour was probed on the live engine. Bundles the full official BotAPIPython.md.
---

# cambc Python bot API (SDK 4.0.0, engine 2.0.0)

**Ground truth, in order:** `sdk/python/cambc/__init__.py` (Champion, Ability, …), `sdk/python/cambc/{game_map,vision,draft,debug,constants}.py`,
the native stubs in `sdk/python/_cambc.pyi` (Vec2, Bitboard, DistanceField, records), then `references/BotAPIPython.md` (the official docs).
To search the docs, use `## cambc.<Class>` for class/module sections (e.g. `## cambc.Champion`, `## cambc.vision`, `## cambc.game_map.CampGroup`)
and `### <method>` for members. Example: `grep -n "^## cambc\.\|^### move_towards" references/BotAPIPython.md`, then read about 25 lines from the hit.
The top `## cambc` section lists every module-level type and function. Docs tag calls with **gameplay** (champion bots only, not draft) and **vision** (target must be visible).
Game mechanics are in the **cambc-game-rules** skill. Coordinates: `Vec2(x, y)` with **+y = north**. Distances are Chebyshev.

## 1. Bot layout and lifecycle
```
bots/<name>/src/main.py         # entry point; runs when the game starts. Other modules must NOT import it.
bots/<name>/src/*.py            # your modules: compiled AND imported at build/snapshot time (_precompile.py)
bots/<name>/pyrightconfig.json  # {"extraPaths": ["../../sdk/python"]} for type checking
```
- **Never call the engine at module import time** in non-main modules (no `game_map.walls()`, `Bitboard()`, `cambc.me()` at top level). They are executed inside a snapshot where engine calls trap, which gives `PreloadError`. Do that work lazily on the first turn.
- Each bot **instance** is either the team's **draft bot** (`cambc.is_draft()` is True, there is no champion) or **one champion** (one instance per champion; Cassi and Issac are two).
  Python globals are per instance. Nothing flows from draft to champions except **draft memory** (1,024 B), and champions share only **shared memory** (8 B).
- The stdlib is preloaded (cheap to import). There are no third-party packages (no numpy). WASI randomness is **always zero in matches**, so seed your own PRNG from map or position (see the starter's `randomness.py`).
- Create a bot with `./cli/cambc new <name> --lang python` (it copies the starter from `sdk/templates/python`).

```python
import cambc
import draft                      # your module (draft logic)
from bot import Bot               # your module; Bot.__init__ must not touch the engine at import time

def main():
    bot = Bot()
    while True:
        try:
            if cambc.is_draft():
                draft.play()           # called once per draft round
            else:
                bot.play_turn()        # one champion's turn
        except Exception as error:     # cambc.Error, ValueError, …: log and still yield
            print(f"bot error: {error!r}", flush=True)
        cambc.end_turn()               # ALWAYS end the turn (also flushes stdout/stderr)

if __name__ == "__main__":
    main()
```

## 2. Draft
```python
n     = cambc.draft.team_size()                        # 3-5 picks (Cassi&Issac = 1 pick, 2 champions)
mine  = cambc.draft.current_draft(cambc.Team.ALLY)     # list of ChampionDraft ints, in pick order
seen  = cambc.draft.current_draft(cambc.Team.ENEMY)    # opponent picks revealed so far (simultaneous picking)
cambc.draft_memory.submit(b"plan")                     # bytes-like, <=1024 B; replaces earlier submissions; draft only
cambc.draft.pick(cambc.ChampionDraft.VARG)             # exactly one per draft round; a 2nd call raises DRAFT_ALREADY_PICKED
```
- The map is fully available during the draft: `game_map.*` and `game_map.camp_groups()` (with gold/gem values). `vision.*` and `cambc.champions()` are **not** available (they raise `API_NOT_INITIALIZED`). `cambc.me()` raises `ValueError`.
- `round_number()` is 0…n−1 during the draft, and gameplay starts at round 1. The first draft turn has about 250M fuel, later draft turns about 2.5M.
- Designs: `cambc.Champion.design(ChampionType.X)`, or `cambc.champion_designs[ChampionType.X]` (13 entries). They give `.base_stats()`, `.abilities()[i].info()`, `.passive()`. Live-state calls raise.
- **`ChampionDraft` ≠ `ChampionType`**: draft index ≥4 maps to type = index + 1 (CASSI_AND_ISSAC=3 → CASSI 3 and ISSAC 4). Heart of Ruin (draft 11) is pickable, although the starter's `range(11)` excludes it.
- Reading in gameplay: `data = bytes(cambc.draft_memory)` gives **1,024 bytes, zero-padded**, so encode your own length or format.
  `cambc.draft_memory` is read once and cached. `cambc.DraftMemoryBuffer()` re-reads. Its `is_empty()` isn't a reliable "nothing submitted" test.

## 3. Module-level API (`cambc.*`)
| Call | Returns / notes |
|---|---|
| `me()` | your `Champion` (ValueError in draft) |
| `is_draft()` | bool |
| `champions(team: Team = None)` | **all** champions, including hidden ones (allies first). Use `vision.champions()` for visible only |
| `round_number()` / `fuel_remaining()` | int |
| `global_submitted_gems(team)` | team's tributed gems |
| `end_turn()` / `resign()` | yield the turn / forfeit |
| `debug_block(fn)` | runs `fn` fuel-free in debug builds, **skipped in `--release` and on the platform**. Usable as a decorator |
| `get_item_enum(family: ItemFamily, stat: ItemStat, shard=True)` | ItemType (shard=False → emblem) |
| `shared_memory` | `SharedMemoryBuffer`: `[i]`, `[i]=v` (byte), `.read(off, bytearray)`, `.write(off, bytes)`, `.size()` → 8 |
| `draft_memory`, `DraftMemoryBuffer()` | `bytes(...)`, `[i]`, `len`, `.submit(data)` (draft only) |
| submodules | `cambc.draft`, `cambc.game_map`, `cambc.vision`, `cambc.constants`, `cambc.debug` |

## 4. Champion (`cambc.me()`, `vision.champions()`, `cambc.champions()`)
**Queries.** `champion_name()→ChampionType` and `team()→Team` work without vision. Most others raise `Error(API_NOT_IN_VISION)` when hidden.
- `position()→Vec2`, `health()`, `max_health()`, `strength()`, `focus()` (float), `attack_range()→int`, `is_alive()`, `is_visible()`, `is_ally()`, `is_enemy()`
- `state()→ChampionState` flags, plus `can_move()`, `can_attack()`, `can_cast()`, `is_recalling()`, `is_submitting_gems()`, `is_teleporting()`, `has_completed_turn()`
- `restrictions()→BuffRestrictions` (MOVE/ATTACK/CAST/SHOP/CONSUMABLE/WARD), `buffs()→BuffCollection` (`has_stun()`, `has_shield()`, `get(BuffShield).value`, iterable)
- `remaining_channel_time()`, `gem_count()`, `item_count()→list[int]` (indexed by ItemType), `consumables()→(Consumable, Consumable)` (indexed by ConsumableType)
- `abilities()→(Ability, Ability)`, `passive()→PassiveType`, `base_stats()→ChampionStats` (`vision_radius, base_move_speed, base_attack_range, base_health, health_growth, base_strength, strength_growth, base_focus, focus_growth, camp_damage_multiplier`)
- `attack_tiles()→Bitboard` (Chebyshev attack range around the current position), `visible_tiles()`, `visible_tiles_from(pos)`, and the `*_into(…, out)` variants
- `prev_priority()` (this round), `priority()` (from next round)
- **Self only:** `gold_count()`, `ward_positions()→list[Vec2]`, `ward_cooldown()→int`, `ward_placement_tiles()→Bitboard` (5×5), `can_buy(item, count=1)→bool`, `can_sell()→bool`

**Actions** (self only; calling them on another champion raises `ValueError("action is only available for self")`):
| Signature | Returns | Notes |
|---|---|---|
| `move(delta: Vec2)` | bool | destination = position + delta |
| `move_absolute(destination: Vec2)` | bool | adjacent tile (move speed 1) |
| `move_towards(target: Vec2)` | bool | SDK BFS around walls, holes, altars, enemy spawn, visible units and teleports. It treats `target` as free: **when adjacent to an occupied target it tries to step onto it and raises.** Stop at your desired range yourself. False if already there, can't move, or no route |
| `attack(target: Unit \| AltarLock)` | None | visible, in range, attack allowance left |
| `abilities()[slot].use(target=None)` | bool | see §5 |
| `consumables()[ConsumableType.X].use(destination=None)` | bool | TP crystal (True = channel started) or altar lock on an altar within 2 |
| `buy(kind: ItemType \| ConsumableType, count: int = 1)` | None | items in bulk; consumables only with count=1; emblems aren't purchasable |
| `sell(kind: ItemType, count=1)` | None | Tavi on spawn only |
| `recall()` / `cancel_recall()` | None | cancel raises **ValueError** if not recalling |
| `submit_gems(altar: Vec2)` / `cancel_submit_gems()` | None | pass the **altar tile**; you must be within Chebyshev 1 (SUBMIT_GEMS_RANGE) |
| `place_ward(destination: Vec2)` | bool | within 2; your own tile is allowed |
| `set_priority(priority: int)` | None | applies from next round; higher acts first |
| `end_turn()` | None | same as `cambc.end_turn()` |

## 5. Ability (`me.abilities()[0|1]`)
- `slot()`, `cooldown()` (0 = ready, 8 right after a cast), `is_on_cooldown()`, `is_ready()` (has ability, cooldown 0 and CAN_CAST. It does **not** check targets or whether an attack reset is legal yet)
- `info(kind=None)→AbilityInfo|None`, `get(AbilityDamage)→typed record` (TypeError if it's the wrong kind), `has(kind)`, `is_attack_reset() / is_damage() / is_aoe_damage() / is_cc() / is_heal() / is_dash() / is_shield()`
- `valid_targets()→AbilityTargetMask` (CAMPS=1, ENEMIES=2, ALLIES=4, SELF=8, GROUND=16), plus `can_target_camps / enemies / allies / self / ground()`
- `valid_tiles()→Bitboard` (Chebyshev cast range; ignores vision and occupancy; **ValueError for range-less abilities** like attack reset), `mask_into(out)`
- `damage_amount(target: Champion = None)`, `heal_amount(target=None)`, `shield_amount(target=None)`: predicted values (with a target, after mitigation and capped by HP)
- **How to call `use`:** damage, CC and heal take a unit, `use(enemy_or_camp_or_ally)`. AoE and dash take a tile, `use(Vec2(x, y))`. Attack reset and shields take nothing, `use()`.
  Wrong target type raises `SPELL_CAST_BAD_TARGET` / `BAD_DESTINATION`.
- Record fields. Common: `max_cooldown, valid_targets, exclusive_with_movement`. Then `AbilityDamage(range, modifier)`, `AbilityAoeDamage(range, modifier, radius, duration)`, `AbilityCc(range, modifier, duration)`,
  `AbilityHeal(range, modifier)`, `AbilityDash(range, radius, modifier, duration)`, `AbilityShield(range, modifier, duration)`, `AbilityAttackReset(enhanced_attack)`.
  Buff records: `BuffShield(duration, value)`, `BuffStun(duration)`, `BuffEnhancedAttack(duration)`.

## 6. Camps, camp groups, wards, teleports, locks
- **Camp** (Unit): `kind()→CampType`, `is_wolf/elk/golem/monolith/gem_cluster/gold_cluster()`, `spawn_position()` (static, no vision needed), `camp_group()`,
  `state()→CampState` (DEAD / ALIVE = **awake** / ASLEEP), `is_dead()`, `is_alive()` (awake or asleep), `is_awake()`, `is_asleep()`, `health()`, `max_health()`, `strength()`, `position()`,
  `attack_range()`, `base_stats()→CampStats`, `is_visible()`, `buffs()`, `attack_tiles()`. Live state needs vision. `int(camp)` gives the handle.
- **CampGroup** (`game_map.camp_groups()`, `vision.camp_groups()`, `camp.camp_group()`): iterable or `camps()`, `len()`, `gold_value()`, `gem_value()`, `max_respawn_timer()`,
  `spawn_tiles()→Bitboard` (**cached, don't mutate**), `spawn_tiles_into(out)`,
  `state()` → `game_map.CampGroupAlive()` / `CampGroupRewardAvailable()` / `CampGroupRespawning(timer)`. Test with `isinstance`. It raises `API_NOT_IN_VISION` unless one of the group's spawn tiles is visible.
  `capture_state()` → `.timer` (remaining time, or 5 when not capturing) and `.state: CampGroupCaptureType` (NO_CAPTURE_AVAILABLE 0, ALLY_CAPTURING 1, CONTESTED 2, ENEMY_CAPTURING 3, CAPTURE_AVAILABLE 4).
- **Ward** snapshot: `owner()`, `position()`, `team()`, `is_ally()`, `is_enemy()`, `remaining_time()` (None means permanent), `visible_tiles()`, static `Ward.visible_tiles_from(pos)`.
- **Teleport** (an in-progress TP channel): `champion()`, `team()`, `position()` (reserved destination), `remaining_time()`, `visible_tiles()`.
- **AltarLock**: `position()`, `team()`, `is_ally()`, `is_enemy()`, `hits_remaining()`. Break it with `me.attack(lock)` (5 hits).

## 7. `cambc.game_map` (static; also works during the draft)
`width()`, `height()`, `is_in_bounds(pos)`, `symmetry()→Symmetry` (HORIZONTAL 0 / VERTICAL 1 / ROTATIONAL180 2), `reflect_horizontal(pos)`, `reflect_vertical(pos)`, `rotate_180(pos)`,
`walls()`, `bushes()`, `holes()`, `altars()`, `spawn_region(Team.ALLY|ENEMY)` → Bitboard. **All of these are cached shared objects:** use `|`/`&` (which make new boards) or `.copy()`, and **never** `|=` or `.set()` on them directly.
`camp_groups()→tuple[CampGroup]`, `camp(pos)→Camp` (`IndexError` if no camp spawns there). Altar tiles: `game_map.altars().positions()`.

## 8. `cambc.vision` (your champion's own vision plus your own ward; not allies')
- Bitboards: `visible_tiles()`, `champion_tiles(team=None)`, `camp_tiles()`, `awake_camp_tiles()`, `asleep_camp_tiles()`, `ward_tiles(team=None)`, `teleport_tiles()`, `altar_lock_tiles(team=None)`.
  Each has a `*_into(out, …)` form, e.g. `champion_tiles_into(out, team=None)`.
- Lists: `champions(team=None)` (visible, including yourself and visible allies), `camps()`, `camp_groups()` (≥1 spawn tile visible), `wards(team=None)`, `teleports()`, `altar_locks(team=None)`.
- Point queries: `in_vision(pos)` (raises if out of bounds), `has_champion(pos)`, `has_camp(pos)`, `has_ward(pos, team=None)`, `has_teleport(pos)`, `has_altar_lock(pos)`.
  `champion_at(pos)`, `camp_at(pos)`, `ward_at(pos, team=None)`, `teleport_at(pos)`, `altar_lock_at(pos)` **raise** if there's nothing there or the tile is hidden, so test with `has_*` first.

## 9. Vec2 and Bitboard
- **Vec2**: `Vec2(x, y)`, `.x`, `.y`, `+ - * //`, unary `-`, `==`, hashable; `chebyshev_distance(o)`, `length_squared()`, `dot(o)`, `cross(o)`, `rotate_cw()` / `rotate_ccw()` (45°).
  `reflect_horizontal()`, `reflect_vertical()` and `rotate_180()` are *map position* transforms. Directions: `Vec2.NORTH` (0,1), `NORTH_EAST`, `EAST` (1,0), `SOUTH_EAST`, `SOUTH`, `SOUTH_WEST`, `WEST`, `NORTH_WEST`.
- **Bitboard** is a map-sized bitset. `Bitboard()` is empty and sized to the map, so create it at runtime, not at import time. `& | ^ ~` return new boards. `&= |= ^=` work in place. `==` is supported.
  `copy()`, `clear()`, `fill()`, `set(pos, value=True)`, `toggle(pos)`, `is_set(pos)` (Error off-map), `is_empty()`, `count()`, `positions()→list[Vec2]` (row-major), `width()`, `height()`, `print()`.
  `shift_right(n)` and `shift_up(n)` return copies (negative n shifts left or down). `reflect(symmetry)`, `reflect_horizontal()`, `reflect_vertical()`, `rotate_180()` also return copies.
  **`draw_chebyshev(center, radius)` and `draw_circle(center, radius)` mutate in place and return None.**
  `walls.reachable_tiles(origin, distance, frontier=None, scratch=None)→Bitboard` is an 8-direction flood **treating `self` as walls**, so call it on a blocked-tiles board, not on the class as the docs' example suggests.
  `opaque.shadow_cast(origin, distance)→Bitboard` gives the tiles visible from origin (game-accurate if `opaque = walls() | bushes()`, though bush interiors are special).
  Every transform has a `*_into(…, out)` variant that avoids allocation. Raw and linear buffers: `export_linear_buffer()` / `import_linear_buffer(b)` (one byte per tile, row-major) are handy for packing.
- Dilate by 1 with `b | b.shift_right(1) | b.shift_right(-1)`, then the same with `shift_up`. Neighbourhood of a tile: `t = Bitboard(); t.draw_chebyshev(p, r)`.

## 10. DistanceField (native BFS: the main pathfinding tool)
```python
blocked = (game_map.walls() | game_map.holes() | game_map.altars() | game_map.spawn_region(cambc.Team.ENEMY)
           | vision.champion_tiles() | vision.camp_tiles() | vision.teleport_tiles())
blocked.set(me.position(), False)          # your own tile must not be a wall (blocked is a fresh board, so safe)
goals = ...                                # Bitboard of target tiles (roots, distance 0)
blocked &= ~goals                          # roots must not be walls
field = cambc.DistanceField()
field.compute(blocked, goals, cambc.Bitboard())               # (walls, roots, visited_out, max_distance=…)
# or field.compute_to(blocked, goals, destinations, visited, max_distance) to stop once destinations are reached
step = field.next_move_from(me.position())  # direction delta toward the nearest root; None at a root or if unreached
if step is not None and me.can_move():
    me.move(step)
```
- `get(pos)→int` returns 0 at roots and **65535 if unreached** *(probe)*. `next_moves_from(pos)→list[Vec2]` gives every optimal delta (compass order from north). Also: `set`, `copy()`, `copy_from(src, mask=None)`, `compute_with_expansion_count`, `compute_to_with_expansion_count`, `print()`.
- **Reuse fields across turns** (e.g. distance-to-altars from static terrain), and only recompute when goals or obstacles change. The starter's `move_towards_closest` is a good template.

## 11. Items, consumables, enums, constants
- `ItemType.<FAMILY>_SHARD_OF_<STAT>` / `<FAMILY>_EMBLEM_OF_<STAT>`, where FAMILY is MONSTER, POWER, DURABILITY, TREASURE, JUNGLE, HOME, BRUISER, TRIBUTE, CAPTURE, PROSPECTOR, HUNTER, SKIRMISH, GREED or COLLECTORS,
  and STAT is STRENGTH, FOCUS or HEALTH. The id is `family*6 + stat*2 + emblem` (ItemStat: STRENGTH 0, FOCUS 1, HEALTH 2), and `ItemType.COUNT` is 84.
  Methods: `.name`, `info()`, `cost()` (shard 30), `combine_count()` (5, Greed 25), `result()`, `health_points()`, `strength_points()`, `focus_points()` (in shard units), `passive()→ItemPassive|None`, `passive_magnitude()`, `is_purchasable()` (False for emblems).
- `ConsumableType.TP_CRYSTAL` and `ConsumableType.ALTAR_LOCK` have `cost()` 10, `carry_limit()` 1 and `.name`. Use them as `me.consumables()[ConsumableType.ALTAR_LOCK].count()` and `.use(pos)`.
- Enums: `Team` (ALLY 0, ENEMY 1, relative to you; `Team.opponent(t)`), `ChampionType`, `ChampionDraft`, `CampType` (WOLF 0, ELK 1, GEM_CLUSTER 2, GOLD_CLUSTER 3, MONOLITH 4, GOLEM 5),
  `CampState`, `PassiveType`, `AbilityKind` (ATTACK_RESET 1 … SHIELD 7), `BuffTypes`, `ItemFamily`, `ItemStat`, `ItemPassive`, `CampGroupCaptureType`, `ErrorCode`.
  Every enum has `X.to_string(v)`. Flag sets (`ChampionState`, `AbilityTargetMask`, `BuffRestrictions`) support `Flag.X in value`, `|`, `&` and `int()`.
  ChampionState bits: ALIVE 1, RECALLING 2, SUBMITTING_GEMS 4, CAN_MOVE 8, CAN_ATTACK 16, COMPLETED_TURN 32, RECALL_STARTED 64, SUBMIT_GEMS_STARTED 128, RECALL_CANCELLED 256, SUBMIT_GEMS_CANCELLED 512, CAN_CAST 2048, TELEPORTING 4096.
  A fresh alive turn is 2073. CAN_CAST clears after a cast. CAN_MOVE is False while channelling.
- `cambc.constants.X` gives CAPTURE_TIME 5, RECALL_TIME 5, RESPAWN_TIME 60, SUBMIT_GEMS_RANGE 1, WARD_PLACEMENT_RADIUS 2.0, WARD_VISION_RADIUS 6.0, WARD_COOLDOWN 10, ALTAR_LOCK_HITS 5, TP_CRYSTAL_TIME 3,
  KILL_GOLD 100, MAX_ROUNDS 2000, WINNING_GEMS 1000, SHARED_MEMORY_BYTES 8, DRAFT_MEMORY_BYTES 1024, and others (full list in cambc-game-rules §15). `constants.passive_abilities.*` holds the passive tuning values.

## 12. Errors: what returns False and what raises
- Engine failures raise **`cambc.Error`**, which has `.code` (an `ErrorCode` int) and `.message`. Print it with `ErrorCode.to_string(e.code)`.
- **Bool actions:** `move`, `move_absolute`, `move_towards`, `place_ward`, `Ability.use` and `Consumable.use` return **True on success**.
  They return **False only for a newly revealed hidden obstruction** (no allowance, cooldown or item is spent, and the tile is revealed for the round, so retry another tile). `move_towards` also returns False for no-op or no-route cases.
  **Known-invalid actions raise `Error`.**
- **None actions** (`attack`, `buy`, `sell`, `recall`, `submit_gems`, `set_priority`, `draft.pick`, `draft_memory.submit`) **raise on any failure**. Check preconditions first.
- **Python-side errors:** `ValueError` from `me()` during the draft, from actions on a non-self champion, from `cancel_recall`/`cancel_submit_gems` when not channelling, and from `valid_tiles()` without a range.
  `IndexError` from `game_map.camp(pos)`, `BuffCollection.get()` and shared memory out of range. `TypeError` from `buy(consumable, count != 1)`.
- Codes seen in probes (all prefixed `INVALID_ACTION_` except `API_*` and `DRAFT_*`):
  - `MOVE_BAD_DESTINATION` (wall, or "Known occupied destination"), `MOVE_ALREADY_MOVED` (2nd walk)
  - `SPELL_CAST_ALREADY_CAST` (2nd cast in a turn), `SPELL_CAST_CANT_CAST` (attack reset while the attack is unused), `SPELL_CAST_BAD_TARGET` / `SPELL_CAST_BAD_DESTINATION` (wrong or missing target)
  - `IS_RECALLING` (acting while recalling), `SUBMIT_GEMS_NO_GEMS`, `BUY_ITEM_INVALID_ITEM` (emblem), `BUY_CONSUMABLE_NOT_ENOUGH_GOLD`
  - `API_NOT_IN_VISION` (hidden unit or group), `API_NOT_INITIALIZED` (gameplay API in draft), `DRAFT_ALREADY_PICKED`
- Other codes worth handling (from the `ErrorCode` enum): `MOVE_OUT_OF_RANGE`, `MOVE_EXCLUSIVE_SPELL_CAST`, `SPELL_CAST_ALREADY_MOVED`, `SPELL_CAST_ON_COOLDOWN`, `SPELL_CAST_OUT_OF_RANGE`,
  `ATTACK_ALREADY_ATTACKED`, `ATTACK_OUT_OF_RANGE`, `SUBMIT_GEMS_ALTAR_LOCKED`, `SUBMIT_GEMS_OUT_OF_RANGE`, `BUY_*_NOT_ON_SPAWN`, `BUY_CONSUMABLE_INVENTORY_FULL`,
  `PLACE_WARD_NO_CHARGES`, `PLACE_WARD_OUT_OF_RANGE`, `ALTAR_LOCK_OUT_OF_RANGE`, `RECALL_ALREADY_USED`, `CANCEL_CHANNEL_ALREADY_USED`.
- Hidden units: `cambc.champions(Team.ENEMY)` lists everyone, but `.position()` and similar raise unless `is_visible()`.
- **If an exception escapes `main()`, that bot stops running.** The rules say a draft bot that crashes before picking gets random picks. Wrap each turn in try/except and always `end_turn()`.

## 13. Fuel tips (Python: 2.5M per turn, about 250M on the first draft turn, about 5M on the first play turn)
- CPython runs interpreted inside WASM, so every Python bytecode op costs fuel. **Push work into native calls**: Bitboard algebra, `reachable_tiles`, `shadow_cast`, `DistanceField.compute*`, `positions()`, `count()`.
  Avoid per-tile Python loops over the whole map (100×100 = 10k tiles).
- Cache static data on your Bot instance: terrain masks, camp groups and their spawn tiles, altar list, distance fields to altars and spawn. Compute them on the first play turn (2× fuel).
  The draft's 100× budget can only reach champions through 1,024 bytes of draft memory.
- Use `*_into(out)` variants with preallocated Bitboards in hot paths. Avoid repeated `me()` and `.position()` calls by storing them in locals.
- Guard optional planning with `if cambc.fuel_remaining() < margin:`. Running out suspends the bot **mid-code**, and it resumes next round with stale state.
- Measure with `--release`, because `debug_block` work is free only in debug builds. Per-turn fuel usage is in the replay zip (`team-a.fuel`, binary) and statistics.
- `move_towards` builds a fresh DistanceField and blocked mask on every call. Fine occasionally, but wasteful when called for many candidate targets.

## 14. Debugging
- `print()` goes to the replay bundle. A `.repl26a` file is a **zip** containing `replay.repl26a`, `team-a.stdout`, `team-b.stdout`, `team-a.debug`, `team-b.debug`, `team-a.fuel` and `team-b.fuel`.
  Read logs with `unzip -p replays/<file>.repl26a team-a.stdout`. All of a team's bots (draft plus every champion) **interleave in one file**, so tag lines with `me().champion_name()`.
  `--log-limit` defaults to 1 MiB per stream.
- `cambc.debug.draw_dot(pos, 0xRRGGBB)` and `cambc.debug.draw_line(a, b, 0xRRGGBB)` show in the visualiser until your next turn (draft drawings clear each draft round). View with `./cli/cambc view [replay]`.

## 15. CLI (run from the workspace root: `cd "/home/ianpoon/Cambridge-BattleCode-Turborecallers-2026/ians linux bot"`; the binary is `./cli/cambc`)
- `./cli/cambc run <botA> <botB> [--map NAME] [--rounds N] [--view] [--release] [--fuel N] [-o DIR] [--statistics PATH [--json]] [--log-limit BYTES]`
  - Bots are names under `bots/` or paths to a bot directory. `--map 00anvil` resolves `maps/00anvil.map26a`. With no `--map` it uses the alphabetically first map.
  - It prints a result table (gems, kills, deaths, gold earned, crashes, draft) and the replay path (default `replays/`). `--rounds` gives "Unfinished … no result".
  - `--statistics out.json --json` writes a match summary (only for **completed** matches) with keys `match` (`outcome`, `roundsCompleted`, …), `teams` (`submittedGems`), `champions[].metrics`
    (`earnedGold`, `kills`, `deaths`, `submittedGems`, `collectedGems`, `monsterDamageDone`, `championDamageDone/Taken`, …), `roster`, `events`, `heatmaps`, `championTimelines`, `teamTimelines`, `diagnostics.botFaults`.
    `cambc summary FILE` converts a binary summary to JSON.
- `./cli/cambc run-batch manifest.txt --jobs 8 [--release] [--rounds N] [--timeout SECS] [--json]`. Each manifest line is
  `BOT_A BOT_B MAP_FILE REPLAY_PATH [--statistics PATH] [--json]`, whitespace-separated, with "double quotes" for paths containing spaces.
  **Paths are resolved relative to the manifest file's directory**, and MAP must be a file path (e.g. `maps/00anvil.map26a`), not a bare map name. Example, with the manifest in the workspace root:
  `bots/mybot bots/starter-python maps/00anvil.map26a replays/b1.repl26a --statistics replays/b1.json --json`. A full 2,000-round match of near-idle bots took about 10 s, and real bots are slower.
- `./cli/cambc build <bot> [--release]`, `./cli/cambc bundle <bot> [-o DIR | --output FILE.zip]` (source zip for upload), `./cli/cambc submit <bot> [-n "note"]` (needs `cambc login`),
  `./cli/cambc maps pull`, `./cli/cambc view [replay]`, `./cli/cambc new <name> --lang python`.

## 16. Gotchas checklist
1. Names that differ from what you might guess: there is no `Champion.use`, `can_attack(target)` or `can_move(dir)`.
   `can_attack()`, `can_move()` and `can_cast()` take **no args** (allowance flags only). Range checks use `me.attack_tiles().is_set(t.position())` or `chebyshev_distance`.
   Spells go through `me.abilities()[i].use(...)` and consumables through `me.consumables()[ConsumableType.X].use(pos)`.
2. The tribute call is `submit_gems(altar_tile)` and the cancel is `cancel_submit_gems()`. There's no generic cancel; use `cancel_recall()` or `cancel_submit_gems()`.
3. Ranged champions: moving consumes the attack and vice versa. "Excludes walking" spells (most damage spells) can't be paired with a walk. Attack resets only after attacking.
4. `game_map.walls()`, `altars()`, `spawn_region()` and `CampGroup.spawn_tiles()` are **shared cached objects**. In-place edits corrupt them for the rest of the game.
5. `vision.champion_at` / `camp_at` raise on empty or hidden tiles, and `CampGroup.state()` raises when out of vision. Check `has_*` or `is_visible()` first.
6. Draft memory reads back as 1,024 zero-padded bytes, and draft-time Python state is lost. `Champion.design()` takes `ChampionType`, not `ChampionDraft`.
7. `Bitboard.reachable_tiles` / `shadow_cast` are instance methods, where the instance is the wall/opaque mask. The docs' `bc.Bitboard.reachable_tiles(...)` example is misleading.
8. `move_towards(target)` raises when the target is occupied and adjacent. Approach to range, then attack.
9. `set_priority` affects the **next** round. Use `prev_priority()` to read the current one.
10. `random` is deterministic (zero seed) in matches, and there's no wall-clock. Use your own seeded PRNG.
