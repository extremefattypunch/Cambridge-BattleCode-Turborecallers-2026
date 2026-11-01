# cpp_port: C++ port of tb_merge_b, designed for the 100k fuel budget

**Status:** design only. `src/` still holds the untouched C++ starter template, created by
`./cli/cambc new cpp_port --lang cpp` so that the CMake build is already configured. The build globs
`src/**/*.cpp`, so new files compile automatically. Build with `./cli/cambc build cpp_port`.

**Source of truth for behaviour:** `bots/tb_merge_b/src/{bot,draft,main}.py` (live ladder champion, about 1,935 lines)
and its `NOTES.md`. The goal is **behavioural parity first**: same decisions and same constants. Fuel-driven
restructuring (below) changes *how* things are computed, never *what* is decided. The Python quirks we must
reproduce for parity are listed in §1.4. Fix them only after parity has been measured.

Fuel numbers in this file come from `bots/cpp_bench`, a micro-benchmark bot run as follows:
`./cli/cambc run cpp_bench starter-cpp --map 01big-world --fuel 20000000 --rounds 260 -o matches/cpp_bench/bigfuel`.
The raised quantum keeps each measurement inside one turn. The same run was repeated on 00gemfight (30x30) and with
`--release`, which gave identical numbers. The raw logs are `team-a.stdout` in the `matches/cpp_bench/*` replays.

---------------------------------------------------------------------------------------------------------------------

## 1. What tb_merge_b does (architecture summary)

### 1.1 Turn flow: `main.py` and `Bot.play_turn`
`main`: `draft.play()` during the draft; otherwise `bot.play_turn()` and then `bot.build_static_fields()`, which spends spare fuel
on cached fields. Any exception prints `bot error: ...`, and `end_turn()` is always called.

`play_turn` (single champion), in order:
1. **First call:** `init_static(me)` (§1.2). If less than `FUEL_FIRST_TURN_MIN` remains afterwards, shop if on spawn and return.
2. **Dead:** remember `died_at[target] = rnd` (once per death), clear our claim, run `update_alerts` (ally deaths), shop (shopping works while dead), and return.
3. `observe(me, rnd)`: refresh camp-group knowledge from vision.
4. **Channelling** (recall, tribute or teleport): return.
5. `try_ward(me)`. Then `shop(me)` if we are on spawn.
6. `threats(me)` gives three things:
   - `incoming` damage per round from awake camps in range and from enemies within range+1, ×0.8 with the Jungle emblem;
   - the `awake` camp list;
   - `enemies`, the visible enemies within `ENEMY_SIGHT`=8. Farther ones were seen only through the ward.
7. `try_lock(me, enemies)`, `update_alerts`, `stall *= 0.98`.
8. On spawn with hp < 92% and nothing incoming: wait (heal).
9. **Camp danger:**
   - `steps` = turns needed to leave every hitting camp's range.
   - `safe_finish`: we can kill the camps hitting us (`hit_hp / dps + 1` turns) with hp−60 to spare, and no enemies are near.
   - Otherwise, if `hp <= incoming*(steps+1)+60`: strike an adjacent melee enemy that dies to one basic attack, or else `retreat`. Return.
10. `handle_enemies` (fight or flee, §1.3 #8). Return if it acted.
11. **Recall when safe.** Conditions:
    - hp < 45% (`low`), or rich: (gold ≥ 150 and gems < 8) or gold ≥ 400;
    - spawn more than 6 tiles away;
    - `recall_safe`.

    Then recall and clear the claim. If `low` but the recall conditions fail, step towards spawn.
12. **Distance setup:**
    - `sf_use` = we are not standing on `walk_block`.
    - Per-turn field: the full map when `!sf_use`; `compute_to` the `sf_dests()` while `sf_todo` is not empty; otherwise none (all distances come from the static fields).
    - `comp = comp_of(pos)`.
13. **Tribute decision** (when carrying gems):
    - `pick_altar` gives `(ad, pref)` (`ad` = 40 if no altar).
    - **go** if any of:
      - `rnd+ad+gems//10+12 >= 2000`;
      - team total (submitted + carried) ≥ 1000;
      - `rnd >= 1900`;
      - `bank_now(gems, BIG, thr)` (with `BANK_DETOUR` this only tests `gems >= 30*k`).
    - Otherwise `choose_target`: no target → go; else `go = bank_detour(gems, detour(...), thr)`.
    - On go: clear the claim and run `do_tribute(me, pref)`.
14. **Farming:**
    - `G = choose_target(...)` (reused from step 13). Write the claim.
    - `G` is None: tribute if carrying gems; else recall if gold ≥ 60 or hp < 70%.
    - Standing on any camp spawn tile while G is not "reward available": step off, towards G.
    - **G respawning:** wait on `dilate(G.tiles,1) − camp tiles − walk_block`.
    - **G alive, within 3, but no live camp visible:** mark it respawning for 10 rounds.
    - **G reward available:** capture by standing on a free spawn tile of G.
    - **Otherwise:**
      - `avoid` = the ranges of awake camps whose position is not one of G's spawn tiles;
      - attack a camp in range, else `go_to` the goals with `avoid`/`no_enter = alive tiles`. Goals are the alive tiles, or bush tiles next to unseen alive tiles (within 5), or for ranged champions the ring at attack range;
      - re-pick a target, attack, `cast_combat`, then `note_progress` (stuck guard).

### 1.2 Subsystems
| # | Subsystem | Python | What it does |
|---|---|---|---|
| 1 | **Static map analysis** | `init_static`, `Group`, `comp_of` | Computes these once on the first turn:<br>• `walk_block` = walls ∪ holes ∪ altars ∪ enemy spawn;<br>• our spawn tiles and the altar list;<br>• `altar_ring` and per-altar rings `altar_goals[i]`, each the Chebyshev-1 ring minus `walk_block`;<br>• one `Group` per engine camp group (camps, spawn tiles, base strength/range/hp, `value = gems + 0.25*gold`, `center` = the first camp's spawn tile);<br>• `all_camp_tiles`;<br>• `slot` = rank of our handle among the sorted ally handles;<br>• the sorted enemy handles;<br>• `lock_side` altars;<br>• `has_dash`;<br>• `need_crossing` (a group or an altar lies outside our walk component);<br>• the `sf_todo` build order.<br>`comp_of` caches flood-fill components (`reachable_tiles`). |
| 2 | **Distance-field cache** (sf_fuel) | `build_static_fields`, `sf_dests`, `group_dist`, `dist_field`, `target_order` | Builds one `DistanceField` per key over the static `walk_block`: the key is a group index (rooted at G.center) or `-2-i` (rooted at altar i's ring). Fields are built after `play_turn` while fuel > `FUEL_BUILD_FLOOR`. Order: `sf_todo.pop()` takes altar rings first, then groups from farthest to nearest. Walking distance is symmetric, so `field_G.get(pos)` is the distance pos→G. Until every field is built, a per-turn field from `pos` reaches the still-unbuilt keys' tiles. `reach_memo` memoises `can_reach`. |
| 3 | **Target scoring** | `choose_target`, `target_order`, `escape_ok`, `note_progress` | For each reachable group (unreachable ones use the cross-component estimate `cheb*1.5+12`), in order of upper bound `value*1.95/(d+6)` with the current target first:<br>• prune when the bound is below the best score, and stop below `FUEL_SCORE_FLOOR` once a best exists;<br>• `ttk = hp_left/(dps + 55*claims)`;<br>• solo-damage model (share 1.0/0.7, Jungle ×0.7); skip if hp < 60% unless it is the current target;<br>• hit-and-run cycles ≤ 4 with `escape_ok`, `extra = 30*cycles`;<br>• round-limit check;<br>• `cost = d + ttk + 6 + extra + wait`, `score = value/cost`;<br>• multipliers: ×1.5 reward available, ×0.6/0.3/1.2 claimed (reward / solo-able / needs help), ×1.3 current target, ×0.3 died here within 250 rounds;<br>• ties go to the lower index.<br>The stuck guard bans a group for 30 rounds after 6 farming turns with no move and no attack. |
| 4 | **Split-farm claims** | `read_claims`, `write_claim` | Shared bytes 0–5 (§7). Each champion counts the other slots' claims per group. |
| 5 | **Team focus** | `read_focus`, `write_focus` | Shared byte 7 holds the focused enemy with a 3-round TTL (§7). |
| 6 | **Banking / tribute** (sf_bank) | `update_alerts`, `threatened`, `pick_altar`, `detour`, `bank_detour`, `bank_now`, `do_tribute` | **Threatened:** an enemy was seen within 14 in the last 40 rounds, an ally died in the last 100, or hp < 60%. That halves the thresholds (`k=0.5`).<br>**`pick_altar`:** nearest altar by its static ring field; skip visible enemy-locked altars; +12 if an enemy was seen within 8 of it in the last 40 rounds.<br>**Detour rule:** bank when ≥ 15k gems and the detour (`ad + cheb(altar, G) − d(pos, G)`) ≤ 8, or ≥ 5k gems and detour ≤ 3.<br>**`do_tribute`:**<br>1. submit at an adjacent altar that is not enemy-locked;<br>2. otherwise handle locks: walk to the free ring, or `break_lock`;<br>3. use the `pref` ring if it has free tiles;<br>4. cross or recall if the goal is in another component;<br>5. `step_toward`. |
| 7 | **Camp danger and retreat** | step 9 of §1.1, `retreat` | `retreat` takes the adjacent tile minimising (danger, −camp margin, −min(enemy dist, 8), spawn dist). It dashes 2 tiles if that is strictly better on the first 3 keys. |
| 8 | **Fight/flee kill-time model** (sf_bank + sf_pvp) | `handle_enemies`, `champ_dps`, `enemy_dps`, `focus_bias`, `chan_kind`, `adjacent_melee`, `strike`, `recall_safe` | **Inputs:**<br>• `near` = enemies within 6, or within 8 if they are the team focus;<br>• `fight_dps` = Σ(str + 0.15·focus)·CHAN_THREAT;<br>• `threat` = enemies within range+2;<br>• `their_ttk = hp/(max(threat, fight_dps) + camp_inc)`;<br>• allies within 4 add 0.7·str.<br>**Engage** when `ratio = (kill + 0.5·approach)/their_ttk ≤ limit`. The limit is 0.85 (0.7 when we carry ≥ 30 gems) plus the excess of `focus_bias` over 0.8 (channel, focus target, carried gems), with a floor of 0.15 if the target carries ≥ 15 gems. We also engage an in-range enemy that dies to one hit.<br>**Target key:** `(tier, my_ttk/(1+gems/20), d)`.<br>**On engage:** `write_focus`, `stun_channel`, guard against the target leaving vision, dash/step/attack, `cast_combat`, then chase-guard bookkeeping (6 turns with no hit → ignore that enemy for 40 rounds).<br>**Otherwise:** stand and trade with an adjacent melee enemy, unless we are clearly losing and can escape. Then apply the stall breaker (hold once `stall > 25`). Then step away and recall once out of reach. |
| 9 | **Capture** | farming branch | Stand on a free spawn tile while the group is "reward available". Never idle on spawn tiles otherwise: that blocks the respawn. |
| 10 | **Camp safety** | `escape_ok`, `died_at`, `avoid`, bush goals, alive-not-seen | Hit-and-run needs an escape tile outside the camps' range. Death memory lasts 250 rounds. Avoid other awake camps' ranges. Reveal camps hidden in bushes. Treat a group whose camps are all dead but unseen as respawning. |
| 11 | **PvP channels** | `chan_kind`, `stun_channel` | Stun a tributing or teleporting enemy (not Marcella) unless we kill it before its channel ends. A recall is broken by damage alone when the enemy is in range. Order of tools: CC, then AoE with duration, then a dash with duration and radius ≥ 1. |
| 12 | **Altar locks** | `buy_lock`, `try_lock`, `locked_altars`, `break_lock` | Buy a lock at gold ≥ 40. **Reactive:** lock an altar within 2 where an enemy is tributing. **Proactive:** lock a `lock_side` altar within 2. Remember enemy-locked altars while they are out of sight. Attack the lock when no free altar is within 8 (or when forced). |
| 13 | **Wards** | `try_ward` | When the cooldown is 0: within 4 of an altar, ward next to it, unless a ward is already within 2 of that altar. Otherwise ward towards the enemy spawn, unless a ward is within 6. Candidates are the 5x5 tiles minus bad tiles, sorted by (cheb to anchor, non-bush). Try the first 3. |
| 14 | **Shop** | `shop`, `bruiser_item` | Buy a TP crystal if `need_crossing`, then `buy_lock`, then up to 12 item purchases:<br>• **Bruiser plan per champion:** finish a part-bought emblem, else buy the stat with the lowest `(shards+5·emblems)/weight`;<br>• **Default build:** Jungle shard, then Monster shard, then Power health and strength alternately. |
| 15 | **Draft** | `draft.py` | Priority: Vesper Vale, Vendetta, Marcella, Heart of Ruin, Ryth, Tavi, Varg, Ren, Willow, Stellar, Prism, Cassi and Issac. Draft memory is `b"tb_splitfarm v1"`. |
| 16 | **Kit casting** | `dps`, `cast_combat`, `kit_units`, `best_area_tile`, `aim_area`, `cast_landing_dash`, `reset_target`, `reset_and_hit`, `pick_camp_in_range` | One cast per turn, in priority order:<br>1. a shield if damage is incoming;<br>2. HoR's landing dash, aimed at the most weighted units;<br>3. damage, CC or AoE on the target. AoE is aimed at the best tile; spells that exclude movement are skipped after a move;<br>4. heal the lowest ally within 4 that is below 70%;<br>5. an attack reset only with a live target in range, re-targeting if the first hit killed it.<br>**`dps`:** str (×1.15 with the Monster emblem), plus str/8 for an attack reset, plus damage/8 for each damage spell. |

### 1.3 Constants
All module constants keep their names and values in `params.h` (`constexpr`):
- `BIG`, `MAX_ROUNDS`, the `STUCK_*`, `CHAN_THREAT`, `LOCK_*`, `FOCUS_*`, `ENEMY_SIGHT`, `BANK_*`, `ALTAR_DANGER_PEN`, `FIGHT_*`, `RECALL_SAFE_MARGIN`, `STALL_*`, `CHASE_*` and `DEATH_*` constants;
- `BRUISER_ITEMS`, `BRUISER_PLAN`, and the `KIT_*` and `ITEMS_*` switches;
- `SCORE_BOUND_MULT`, `UNREACHED`.

The Python fuel constants (`FUEL_BUILD_FLOOR=1M`, `FUEL_SCORE_FLOOR=800k`, `FUEL_FIRST_TURN_MIN=2M`) are replaced by
the C++ guards in §3.4.

### 1.4 Dead code and quirks
**Dead code (not ported):**
- `nearest_altar`, `altar_distance` and the sf_fuel whole-ring field (key −1, never queued);
- `randomness.py`;
- `retreat_turns` and `far_enemies`, which are written but never read;
- `last_print` / DEBUG dumps;
- the first `PRIORITY` list in draft.py, which is overwritten by the second.

**Quirks to reproduce for parity:**
1. `read_claims` scans bytes 0–6. Byte 6 is free and always 0.
2. The farming `avoid` test compares the awake camp's *current position* with G's *spawn tiles* (`cp not in G.hp`). A G camp that has moved off its spawn tile is avoided as if foreign.
3. With `BANK_DETOUR` on, `bank_now` is called with `ad = BIG`, so only the `BANK_ANY` rule can fire there.
4. `Group.center` is the first camp's spawn tile, not a centroid.
5. `threats()` puts **every** visible awake camp in `awake`, including camps seen only through our ward. `enemies` excludes champions farther than 8.
6. The cross-component estimate `d = cheb*1.5+12` is a float. Keep double arithmetic throughout the scoring.

---------------------------------------------------------------------------------------------------------------------

## 2. Benchmark results (bots/cpp_bench)

**Method:**
- The lowest-handle ally runs `bench::static_benches()` on its first turn, then `bench::vision_benches()` every 50 rounds while playing the starter.
- Each line is net fuel per call: the `fuel_remaining()` probe costs 5 and is subtracted.
- Values marked † include about 20–25 fuel of loop and index arithmetic (an empty loop iteration with a volatile store costs 7).

**Maps:** 01big-world is 100x100 with C = 13·13 = 169 chunks of 8x8 and 8,780 reachable tiles. 00gemfight is 30x30 with C = 16 and 781 reachable tiles.
**Budgets:** 100,000 per turn, 200,000 on the first play turn, and 10,000,000 on the first draft turn.

### 2.1 Measured costs (fuel per call)
| Operation | 100x100 | 30x30 | Notes |
|---|---:|---:|---|
| `fuel_remaining()` | 5 | 5 | |
| `round_number()` | 23 | 23 | |
| `me.position()` / `health()` / `state()` / `is_alive()` | 74 / 69 / 59 / 47 | same | Each getter is a separate `sdk_champion` call |
| raw `detail::sdk_champion` (all fields at once) | 32 | 32 | Optional fast path (§3.3) |
| `gold_count` / `gem_count` / `champion_name` | 51 / 44 / 38 | same | |
| `item_count()` | 378 | 378 | Returns an enum_map of 84 u32 by value |
| `abilities()` (array copy) | 105 | 105 | Cache once |
| `ability.is_ready()` / `cooldown()` / `damage_amount()` | 103 / 53 / 55 | same | |
| `ability.is_dash()` ×2 (cached variant) | 102 | 102 | Native `std::visit` |
| `consumable.count()` / `can_buy(item)` / `ward_cooldown()` | 46 / 136 / 46 | same | |
| `global_submitted_gems` | 20 | 20 | |
| `cambc::champions(team)` (5 handles, objects built) | 3,379 | 2,977 | About 600 per champion. **Cache at init** |
| `shared_memory.read(0, 8 bytes)` / `[7]` read / `[6]=v` | 31 / 34 / 30 | same | |
| **throw + catch `cambc::error`** | **3,764** | **3,969** | Never use exceptions for control flow |
| `bitboard()` (alloc + zero) / copy / `a\|b` (new) / `~a` | 390 / 389 / 418 / 391 | 261 / 260 / 289 / 262 | Allocation ≈ 200–230 |
| `a \|= b` / `a &= b` / `shift_right_into(1,out)` (no alloc) | 192 / 192 / 192 | 39 / 39 / 39 | ≈ 1.1·C + 20 |
| `shift_right(1)` / `shift_up(1)` (new board) | 394 | 265 | |
| `walk_block()` (4-way union) | 782 | 347 | |
| `dilate(r=1)` Python-style / with scratch boards | 3,917 / 1,990 | 2,593 / 528 | |
| `dilate(r=3)` Python-style | 11,341 | 6,802 | Memoise |
| `is_set` (SDK) † / native raw-chunk test † | 47 / 47 | 47 / 47 | The SDK call is no worse than native |
| `set` † | 32 | 32 | |
| `is_empty()` / `count()` | 205 / 202 | 52 / 49 | Proportional to C |
| `positions()` 9 / ~121 / 837 bits | 761 / 1,758 / 8,189 | 455 / 791 (49) / 2,951 (289) | ≈ 230 alloc + 4·C + 9 per bit |
| `positions_into(span)` 25 bits / `positions()` 25 bits | 229 / 905 | 67 / 513 (16 bits) | Use preallocated spans |
| `draw_chebyshev(p, 1 or 8)` (+ctor) | 413 / 421 | 284 / 287 | |
| `reachable_tiles(pos, 1)` | 404 | 275 | |
| `reachable_tiles(pos, W*H)` (whole component) | 27,950 | 1,138 | Once per component |
| `shadow_cast(pos, 10)` | 1,318 | 704 | |
| `export_linear_buffer` (bitboard) / `export_raw_buffer` | 1,756 / 2,053 | 391 / 403 | Linear = packed bits, row-major, LSB first |
| `distance_field()` construct | 3 | 3 | Lazy storage |
| **`df.compute` full map (8,780 tiles, 161 expansions)** | **29,954** | **1,129** (52 exp.) | |
| `df.compute` max_distance 5 / 10 / 20 / 40 | 3,587 / 4,432 / 6,122 / 9,502 | 374 / 454 / 614 / 934 | |
| `df.compute_to` destination at distance 10 / 30 / far | 4,432 / 7,812 / 29,782 | 454 / 774 / 1,110 | |
| Python `step_toward` pattern (goal at distance 30) | 11,307 | 3,134 | `compute_to` + `reachable_tiles(pos,1).positions()` + 8 `get`s |
| **Step along a cached static field** (8 neighbour `get`s + blocked `is_set`) | **586** | **530** | Replaces most `step_toward` fields |
| `df.compute` full map from an altar ring | 23,821 | 1,449 | |
| Static field build, including allocations (shallow group) | ≈ 5,100 base | ≈ 2,070 (≈ 40 exp.) | Base on 100x100 = alloc + temporaries + about 2.7k |
| `df.get` † / native lookup in an exported vector † | 51 / 30 | same | Exporting a field (22,837 / 2,362) does not pay off |
| `df.next_move_from` | 705 | 716 | |
| **Native queue BFS over the whole map** (u8 grid, 8 neighbours) | **1,571,373** | **135,356** | 50x slower than the host BFS |
| Native bitset BFS (u64 rows, frontier dilation) | 2,331,923 | 206,278 | |
| Native scan over 10k u16 (sum) | 80,032 | 7,232 | About 8 fuel per element |
| Native unpack of a packed mask to a u8 grid | 161,831 | 16,921 | |
| `map::camp_groups()` (24 groups / 92 camps; 19 / 36) | 32,178 | 19,214 | 25,195 in the draft. **Cache once** |
| `camp.base_stats()` / `group.spawn_tiles()` | 163 / 857 | 163 / 608 | Cache per camp type and per group |
| `map::altars().positions()` | 736 | 394 | |
| `std::cout` one short line | 260 | 260 | |
| `vision::visible_tiles` / `camp_tiles` / `awake_camp_tiles` / `teleport_tiles` / `champion_tiles(enemy)` | 452–502 | 252 | Each allocates. `*_into(out)` costs 189 / 36 |
| `vision::champion_tiles()` (both teams) | 1,089–1,189 | 549 | |
| Python `blocked_now` (walk ∪ champions ∪ camps ∪ teleports) | 3,377–3,627 | 1,511 | ≈ 1.5k with preallocated boards |
| `vision::champions(enemy)`: 0 / 1 / 2 visible | 486–1,042 / – / – | 486 / 1,595 / 2,351 | About 1,100 per visible champion (object construction) |
| `vision::champions(ally)` (2–5 visible, self included) | 2,580–3,485 | 2,342–3,435 | |
| Cached enemy objects: `is_visible()` on all 5 | 320 | 320 | **About 15x cheaper** than `vision::champions` |
| `vision::camps()`: 0 / 2–3 / 7–9 visible | 912–970 / 1,777–1,963 / – | 464 / – / 2,489–2,975 | About 300–400 per camp |
| Per camp: `state` / `health` / `position` / `is_visible` / `attack_range` | 49 / 51 / 53 / 58 / 176 | same | `attack_range()` is a `base_stats` call: cache it per type |
| Raw `detail::sdk_camp` (all fields) | 26 | 26 | |
| Enemy `position` / `is_submitting_gems` / `gem_count` / `health+strength+attack_range` | 81 / 63 / 50 / 216 | same | |
| `group.state()` (visible group) | 474–629 | 346–368 | It calls `sdk_vision` internally. Throws when out of vision |
| Python `observe` scan (`spawn_tiles() & vis` per group) | 28,044 (24 groups) | 11,521 (19) | **Do not port as is** |
| `vision::camp_groups()` | 36,231 | 23,096 | Never call it per turn |
| `has_altar_lock` / `in_vision` per altar | 64 / 43 | 68 / 47 | |
| `me.attack_tiles()` | 919 | 432 | Use `cheb(pos,t) <= range` instead; it is the same set |
| `vision::wards()` / `me.ward_positions()` / `vision::has_camp` | 101 / 115 / 48 | same | |

### 2.2 Cost model
- **Scalar SDK call:** 20–75 fuel. The host side is cheap, so SDK calls are *not* the bottleneck.
- **Host bitboard op:** about 1.1·C + 20 in place. Add about 220 when it returns a new board (aligned `operator new` + zeroing).
  Use `*_into` variants and long-lived scratch boards.
- **Host distance field:** about **C·(E + 16) + 300**, where E = BFS expansions (depth reached).
  - 100x100 full map: 169·(161+16) ≈ 29.9k ✓. A deep maze on 100x100 with E ≈ 400 would cost about 70k.
  - 30x30: 16·(52+16) ≈ 1.1k ✓.
  - 90x30 (00lanes): C = 48, so the full map costs about 6k.
- **Native wasm code:** about 1 fuel per instruction, which is about **8 fuel per trivial loop iteration**. Any per-tile pass over the whole map
  (10k tiles) costs about a full turn. Every map-wide operation must be a host call (bitboard algebra, `reachable_tiles`, `distance_field`).
  Native code is fine over small sets: units, candidate tiles, groups.
- **Exceptions:** about 3.8k each, so 26 caught errors use a whole turn. The Python bot leans on `try/except` everywhere. The port must not.
- **Python vs C++:** the Python champion uses p50 1.53M / p90 2.16M / p99 2.39M of its 2.5M budget on 01big-world
  (61% / 86% / 95%; `matches/fuelprobe-01big-world`). The C++ starter uses p50 28k / p99 41k of 100k on the same map
  (`matches/langprobe-01big-world`). Host work (fields, boards) costs about the same *fraction* of the budget in both languages,
  since the C++ budget is 25x smaller. A line-by-line translation would therefore be about as tight as the Python bot (which has
  about 80 fuelExhausted per game). The savings must come from: no per-turn full fields, field-following movement, cached handles,
  no exceptions, and preallocated boards.

---------------------------------------------------------------------------------------------------------------------

## 3. Fuel strategy

Notation: C = ⌈W/8⌉·⌈H/8⌉ (16 on 30x30, 48 on 90x30, 169 on 100x100), B = 100,000 (200,000 on the first play turn).

### 3.1 Cache at init (first play turn)
| Item | Python origin | Cost 100x100 | Cost 30x30 |
|---|---|---:|---:|
| `map::camp_groups()` → `Group`/`CampRec` (camp object, spawn, type) | `Group.__init__` | 32k | 19k |
| Base stats per **camp type** (6 calls), not per camp | `c.base_stats()` | 1k | 1k |
| Group spawn-tile boards (ctor + `set` per camp) + `all_camp_tiles` | `G.tiles` | ≈ 15k | ≈ 6k |
| Ally and enemy `champion` objects, sorted by handle (`slot`, `enemy_handles`) | `cambc.champions` | 6.7k | 6.3k |
| Ability metadata for our 2 slots (kind, range, radius, modifier, duration, exclusive): an `AbInfo` struct | `ab.info()` | 0.3k | 0.3k |
| `walk_block`, spawn, altars, rings, `altar_goals` | `init_static` | ≈ 7k | ≈ 2k |
| Home component (`reachable_tiles(pos, W*H)`) | `comp_of` | 28k | 1.1k |
| `need_crossing`: test each camp's spawn and each ring tile with `is_set` on the component (not `(G.tiles & home).is_empty()` per group, which costs 14k) | `init_static` | ≈ 3k | ≈ 1k |
| **Total init** | | **≈ 92k** | **≈ 37k** |

On turn 1 that leaves about 108k on 100x100: play the turn (shop on spawn, about 5–10k), then build static fields with the rest
(altar rings first: 2–3 fields). Mirror `FUEL_FIRST_TURN_MIN`: if fewer than **60,000** remain after init, shop and return.
All later static work runs **after** `play_turn` (§3.2).

**Memoised on demand, as in Python, never per turn:**
- other components;
- staging areas (`comp & dilate(tcomp, r)`: 4–11k);
- `escape_ok` zones;
- `can_reach` (keyed by group, component id and "has crystal or ≥ 10 gold").

Key the memos by component *id* (index into `comps`) instead of Python's `id(comp)`.

### 3.2 Static distance fields (spread over turns)
- Same keys and order as Python:
  - `sf_todo` = groups sorted by `cheb(center, spawn)`, then altars `-2-i`;
  - `pop()` from the back, so altar rings come first, then groups from farthest to nearest.

  A field is stored as a `cambc::distance_field` (field_bytes = 21.6 KB on 100x100; about 40 fields ≈ 0.9 MB). Move it, never copy it.
- **Cost estimate** before each build: `est = C·(E_hint·1.15 + 16) + 3000`.
  - `E_hint` = the largest expansion count seen so far (`compute_with_expansion_count`), initially `W + H`.
  - Build only while `fuel_remaining() > est + FUEL_BUILD_RESERVE` (10,000), in `main.cpp` after `play_turn`.
  - If a key's `est` exceeds what a quiet turn can offer (about 85k, which only happens on a deep 100x100 maze), split it into
    **bands** of K = 60 expansions:
    1. compute with `max_distance = K`, keeping `visited_K`;
    2. compute `visited_{K-1}` the same way. The frontier = `visited_K & ~visited_{K-1}`;
    3. the next band is rooted at the frontier, with walls = `walk_block ∪ (visited_K − frontier)`;
    4. lookup: `v0` if `visited0.is_set(p)`, else `K + v1`, and so on.

    Exact, because any path out of band 0 crosses a tile at distance exactly K. Implement this only if `fuel_report` shows such maps.
- **Expected schedule:**
  - 01big-world: 24 groups + 6 altars ≈ 30 fields × ≈ 30k ≈ 0.9M. With about 50–70k spare per turn, all are built by turn 15–20.
  - 30x30: 19 groups + 2–4 altars ≈ 23 × 2k ≈ 46k, all built on turn 1.
  - 90x30 (00lanes, the Python hot spot): ≈ 6k per field, done in 2–3 turns.
- **Turn field while `sf_todo` is not empty:** `compute_to(walk_block∖pos, {pos}, sf_dests, visited, max_distance = 60)`.
  - Cost ≤ C·76 + 300 (≈ 13k on 100x100; on 30x30 the whole map is ≤ 1.2k anyway).
  - Skip it entirely when `fuel_remaining() < 40,000` at that point.
  - Unbuilt groups beyond the cap fall back to the existing cross estimate `cheb·1.5 + 12` (which is ≥ the true distance in practice).
  - Never compute an uncapped full-map field per turn. When `!sf_use` (we stand on `walk_block`), use the same capped field.

### 3.3 Per-turn work: what changes from the Python
1. **Snapshot once per turn** (`Me` struct): pos, hp, max hp, str, focus, range, state flags, gold, gems, round.
   - With public getters this costs about 600 fuel. Behind `CAMBC_FAST_INFO`, one `detail::sdk_champion` costs 32. That struct is not public API,
     so keep the public path as the default and the fast path optional.
   - **Refresh `pos` and the action flags after any move, dash or attack.** The Python re-reads `me.position()` and `me.can_attack()` at
     each use, and `pick_camp_in_range` after `go_to` relies on that.
2. **Vision boards per turn**, each filled with `*_into(out)` into scratch boards owned by `Bot`:
   - `vis` (`visible_tiles`), `camp_occ` (`camp_tiles`), `awake_occ` (`awake_camp_tiles`), `champ_occ` (both teams), `tp_occ`;
   - `enemy_lock` (`altar_lock_tiles(team::enemy)`), which replaces every `has_altar_lock(a) && altar_lock_at(a).is_enemy()` pair (7 sites);
   - ≈ 7 × 190 ≈ 1.3k on 100x100 and ≈ 0.3k on 30x30, loaded lazily (e.g. `enemy_lock` only when it is used).
3. **Enemies and allies from cached handles:** `is_visible()` (64 each) and `is_alive()`, then only the getters each use needs.
   That is about 0.3k + 0.4k per visible enemy, instead of `vision::champions` (about 1.1k each).
   - `update_alerts` uses the cached ally objects' `is_alive()` (47 each) instead of re-enumerating `cambc::champions` (3.4k).
   - **Parity check (debug_block, free):** the cached visible set equals `vision::champions(team::enemy)`.
4. **Camps from cached handles.** `threats`/`observe`/`kit_units`/`reset_target` need the visible camps, not
   `vision::camps()` (about 350 per camp plus 900 base).
   - Get the positions with `awake_occ.positions_into(span)` (and `camp_occ` where all live camps are needed).
   - Map each position to a `CampRec` through a small sorted spawn-position table (binary search, about 70 fuel). Fall back to
     `vision::camp_at(p)` for a camp that is off its spawn tile.
   - Use the cached `range` and `base_strength`. `strength()` and `health()` are live calls (about 50 each), only for awake or targeted camps.
5. **`observe`:**
   - only groups with `cheb(center, pos) ≤ 10` (as in Python);
   - "group in vision" = any member spawn with `vis.is_set` (about 30 each), never `(G.tiles & vis)` (1.2k);
   - then `G.g.state()` (350–630), which can no longer throw;
   - then per camp `vis.is_set(p) && !vision::has_camp(p)` / `is_visible` / `state` / `health`.

   Expected ≤ 4k on 100x100.
6. **`blocked_now`:** computed at most once per turn into a scratch board, and recomputed only after we move:
   copy-assign `walk_block`, then `|=` champ_occ, camp_occ and tp_occ, then `set(pos,false)`. ≈ 1.0k on 100x100, versus 3.4–3.6k each time in Python.
7. **Movement (`step_toward`):**
   - **Fast path:** the goal belongs to a key with a built static field (group G, or altar i), and we are far from it
     (`cheb > LOCAL_RADIUS = 8`). Then pick the 8-neighbour with the lowest static value that is not in `blocked_now` and not in `avoid`.
     Cost ≈ 0.6k, versus 11k (d = 30) to 30k (far) for a dynamic field on 100x100.
   - **Otherwise, or when no neighbour improves** (a unit blocks the corridor): run the Python algorithm exactly (field rooted at
     `goals` with walls = blocked [∪ avoid], `compute_to` until `pos` is reached), with `max_distance = min(DYN_STEP_MAXD = 40, static_d + 6)`.
     Cost ≤ C·56 ≈ 9.5k on 100x100 and ≤ 0.9k on 30x30. Keep the avoid → no-avoid two-pass fallback.
   - Replace `stepable.reachable_tiles(pos, 1).positions()` with the 8 explicit neighbours plus an in-bounds check. The
     `stepable` mask still excludes `walls ∪ no_enter`.
8. **Attack range:** `cheb(pos, t) <= me.range` everywhere Python uses `me.attack_tiles().is_set(t)` (9 sites; saves 919 each).
9. **`choose_target`:**
   - native scoring over at most about 40 groups;
   - `group_dist` = static field `get` (51) or turn-field `get`;
   - bound pruning and the index tie-break are kept;
   - total ≤ 6k. `FUEL_SCORE_FLOOR = 20,000`.
10. **Kit casting:** cached `AbInfo` per slot. `is_ready()` once per slot per turn (103). Aim searches are native over ≤ 25 candidate
    tiles × ≤ 12 units (≤ 3k).
11. **Logging:** every debug print goes inside `debug_block({...})`. It is free in debug builds and compiled out in release and on the platform.
    The `bot error: ...` line in `main.cpp` stays a plain `std::cout`, the same text as Python (tools grep it).

### 3.4 Per-turn budgets and guards
Targets for 100x100 (the worst case). On 30x30 everything is 3–10x cheaper.

| Phase | Python functions | p50 target | Cap (guarded) |
|---|---|---:|---:|
| Snapshot + vision boards + comms read | `play_turn` head, `read_claims`, `read_focus` | 2.5k | 4k |
| `observe` + `threats` + `update_alerts` | | 4k | 8k |
| Danger / fight-flee / recall | step 9, `handle_enemies`, `retreat` | 2k | 10k |
| Turn field (only while `sf_todo` is not empty) | `dist_field` | 0 (≤ 13k early) | 13k |
| `pick_altar` + `choose_target` | | 4k | 8k |
| Movement (`blocked_now` + one step) | `step_toward`, `go_to`, `cross_toward`, `do_tribute` | 2k | 12k |
| Attack + `cast_combat` + kit aim | | 1k | 5k |
| Ward / lock / shop (only when relevant) | `try_ward`, `try_lock`, `shop` | 0.5k | 6k |
| **`play_turn` total** | | **≈ 18k** | **≈ 50k** |
| Static field builds (after `play_turn`) | `build_static_fields` | spare | `fuel − est > 10k` |

**Guards** (in `fuel.h`):
```cpp
constexpr std::uint64_t FUEL_HARD_FLOOR     =  4'000; // checkpoint: below this, stop and end the turn cleanly
constexpr std::uint64_t FUEL_RESERVE        =  8'000; // optional work needs est + this
constexpr std::uint64_t FUEL_SCORE_FLOOR    = 20'000; // choose_target: keep the best so far below this
constexpr std::uint64_t FUEL_TURNFIELD_MIN  = 40'000; // skip the capped turn field below this
constexpr std::uint64_t FUEL_BUILD_RESERVE  = 10'000; // static builds after play_turn
constexpr std::uint64_t FUEL_FIRST_TURN_MIN = 60'000; // after init_static on turn 1, else shop and return
constexpr int TURN_FIELD_MAXD = 60, DYN_STEP_MAXD = 40, LOCAL_RADIUS = 8;
inline std::uint64_t field_cost(int expansions) { return chunks() * (expansions + 16) + 300; }
inline bool afford(std::uint64_t est) { return cambc::fuel_remaining() > est + FUEL_RESERVE; }
```
- Call `checkpoint()` between the phases of §1.1. Below `FUEL_HARD_FLOOR` it returns from `play_turn`. A suspension mid-turn resumes next
  round with stale state, which is far worse than a skipped action.
- Every dynamic field call goes through one helper that clamps `max_distance` so that `field_cost(maxd) < fuel − FUEL_RESERVE`.
- **Profiler:** a RAII `FuelScope(id)` adds `fuel_remaining()` deltas (5 fuel per probe) into a static table per subsystem. The table is
  printed every 200 rounds inside `debug_block`, so printing is free. Check the replays with
  `python3 -I bots/cpp_port/tools/fuel_report.py matches/<tag>`. The acceptance criteria are in §8.

---------------------------------------------------------------------------------------------------------------------

## 4. File layout (`bots/cpp_port/src`)
| File | Contents |
|---|---|
| `main.cpp` | Loop: `is_draft()` → `play_draft()`; else `bot.play_turn()` then `bot.build_static_fields()`. Catch `std::exception` and `...` → `bot error: ...`. Always `end_turn()`. |
| `draft.h/.cpp` | `PRIORITY` (`champion_draft` enum), `draft_memory = "tb_splitfarm v1"`. Each pick is in a try/catch and falls through to the next. |
| `params.h` | Every Python constant, `constexpr`, same names; `BRUISER_PLAN` as a switch over `champion_type`. |
| `fuel.h` | Guards and constants from §3.4, `chunks()`, `field_cost()`, `afford()`, `checkpoint()`, `FuelScope` profiler. |
| `state.h` | `cheb()`, `handle_of(champion)`, `CampRec`, `Group`, `AbInfo`, `Me` (turn snapshot), `UnitView` (enemy/ally/camp snapshot), `Target` (camp or champion + pos/hp), `Scratch` (preallocated boards and `positions_into` buffers), `struct Bot` with all persistent state. |
| `map_static.cpp` | `init_static`, `comp_of` (→ comp id), `staging`, `escape_ok`, `can_reach`, the static field cache (`build_static_fields`, `sf_dests`, `group_dist`, `altar_dist`), `turn_field`, `dilate_into`. |
| `sensing.cpp` | `snapshot`, per-turn vision boards, `observe`, `threats`, `update_alerts`, cached visible enemies/allies/camps. |
| `movement.cpp` | `blocked_now` cache, `step_toward` (fast path + bounded dynamic), `go_to`, `cross_toward`, `step_off_spawn_tile`, `try_move`. |
| `targeting.cpp` | `target_order`, `choose_target`, `note_progress`, `alive_tiles`, `pick_camp_in_range`, farming goals (bush and ranged rings). |
| `banking.cpp` | `threatened`, `pick_altar`, `detour`, `bank_detour`, `bank_now`, `do_tribute`. |
| `combat.cpp` | `dps`, `champ_dps`, `enemy_dps`, `recall_safe`, `adjacent_melee`, `strike`, `retreat`, `danger_step` (step 9), `handle_enemies`, `cast_combat`, the kit helpers (`kit_units`, `best_area_tile`, `aim_area`, `cast_landing_dash`, `reset_target`, `reset_and_hit`), `try_attack`, `try_cast`. |
| `pvp.cpp` | `chan_kind`, `focus_bias`, `stun_channel`, `try_lock`, `locked_altars`, `break_lock`, `try_ward`. |
| `comms.cpp` | Shared-memory layout (§7): `read_comms` (one 8-byte read per turn), `write_claim`, `read_focus`, `write_focus`. |
| `shop.cpp` | `shop`, `bruiser_item`, `buy_lock`. |
| `bot.h/.cpp` | `Bot::play_turn()`: the flow of §1.1, with `checkpoint()` between phases. |
| `tools/fuel_report.py` (not compiled) | Per-turn fuel percentiles from replays. |

Remove the starter's `random.h` (unused; Python `randomness.py` was unused too).

---------------------------------------------------------------------------------------------------------------------

## 5. Python function → C++ mapping
| Python (`bot.py` unless noted) | C++ | Notes |
|---|---|---|
| `dilate(bb, r)` | `map_static.cpp: void dilate_into(const bitboard&, int r, bitboard& out, Scratch&)` | `shift_*_into` + `\|=` into scratch: 2.0k instead of 3.9k per radius step (100x100) |
| `cheb(a, b)` | `state.h: inline int cheb(vec2, vec2)` | `chebyshev_distance` returns int64 |
| `class Group` | `state.h: struct Group { idx, camp_group g, std::vector<CampRec> camps, bitboard tiles, vec2 center, gems, gold, double strength, int rng, n, status, ready; std::vector<double> hp, maxhp; double value; }` | The `hp`/`maxhp` dicts keyed by spawn tile become vectors parallel to `camps`. Quirk 2 (§1.4) needs a "spawn-tile ∈ G" test, done by a linear scan over `camps` |
| `Group.hp_left`, `alive_strength` | member functions | |
| `Bot.__init__` | `struct Bot` members | Dicts keyed by handle/idx (`banned`, `died_at`, `chase_turns`, `chase_ban`, `ally_alive`, `altar_seen`, `escape_cache`, `reach_memo`, `cross_cache`) become small vectors or `std::unordered_map`, sized by groups, altars and champions |
| `init_static` | `map_static.cpp: void Bot::init_static()` | Adds the cached champion objects, `AbInfo`, per-type camp stats and the spawn-position index (§3.1) |
| `comp_of` | `int Bot::comp_of(vec2)` | `std::vector<bitboard> comps`. Returns an index |
| `read_claims` / `write_claim` | `comms.cpp` | §7 |
| `observe` | `sensing.cpp: observe()` | §3.3 item 5 |
| `threats` | `sensing.cpp: threats(Turn&)` | Fills `incoming`, `awake` (`CampView` list), `enemies` (`UnitView` list) |
| `jungle` | `Me::jungle` (from `item_count()` at most once per turn) | |
| `blocked_now` | `movement.cpp: const bitboard& blocked_now()` | Cached per turn and per position |
| `step_toward` | `movement.cpp: bool step_toward(const bitboard& goals, const bitboard* avoid, const bitboard* no_enter, FieldHint hint = {})` | §3.3 item 7 |
| `dist_field` | `map_static.cpp: turn_field()` | Capped (§3.2) |
| `build_static_fields`, `sf_dests`, `group_dist` | `map_static.cpp` | Same keys: group idx; altar `-2-i` stored as `altar_fields[i]` |
| `target_order` | `targeting.cpp` | `std::stable_sort` on −bound (Python `sort` is stable), then move the current target to the front |
| `dash_ability`, `crystal` | `combat.cpp` helpers | Cached slot index, plus `is_ready()` / `count()` |
| `staging`, `cross_toward`, `go_to`, `can_reach` | `movement.cpp` / `map_static.cpp` | Memo keyed by `(comp_id, tcomp_id, r)`. `cands` sorted with `std::stable_sort` by cheb |
| `shop`, `bruiser_item`, `buy_lock` | `shop.cpp` | `item_count()` once per shop loop pass (378), not per test |
| `dps`, `cast_combat`, `kit_units`, `best_area_tile`, `aim_area`, `cast_landing_dash`, `reset_target`, `reset_and_hit` | `combat.cpp` | `Target` abstraction for `use(camp)` vs `use(champion)` |
| `pick_camp_in_range`, `alive_tiles` | `targeting.cpp` | Range by `cheb` |
| `choose_target`, `note_progress`, `escape_ok` | `targeting.cpp` / `map_static.cpp` | Double arithmetic. Same multiplier order |
| `update_alerts`, `threatened`, `pick_altar`, `detour`, `bank_detour`, `bank_now`, `do_tribute` | `banking.cpp` | Rounds stored as `int64` (Python uses `-BIG` sentinels) |
| `retreat` | `combat.cpp` | Lexicographic key: `std::tuple<double,int,int,int>`. Candidates are `pos` first, then neighbours in row-major order. Python's `min` returns the first minimum, so use `std::min_element` |
| `enemy_dps`, `champ_dps`, `recall_safe`, `adjacent_melee`, `strike`, `handle_enemies` | `combat.cpp` | |
| `chan_kind`, `focus_bias`, `stun_channel` | `pvp.cpp` | `remaining_channel_time()` throws (code 115) unless channelling: call it only for `chan_kind ∈ {1,2}` |
| `read_focus`, `write_focus` | `comms.cpp` | |
| `try_lock`, `locked_altars`, `break_lock`, `try_ward` | `pvp.cpp` | `enemy_lock` board. `vision::altar_lock_at(a)` only for the lock we attack |
| `play_turn` | `bot.cpp: Bot::play_turn()` | |
| `nearest_altar`, `altar_distance`, `randomness.below` | — | Dead code |
| `main.py: main` | `main.cpp` | Static fields are built after `play_turn` |
| `draft.py: play` | `draft.cpp: play_draft()` | |

---------------------------------------------------------------------------------------------------------------------

## 6. SDK mapping: Python `cambc` → C++ `cambc::` (`sdk/cpp/cambc.h`)

**Error handling.** The C++ SDK has **no result types**:
- Engine failures throw `cambc::error`, a `std::runtime_error` with `.code()` → `cambc::error_code` and `.message()`.
- SDK-side checks throw `std::invalid_argument` (a self-only action on another champion; `cancel_*` when not channelling),
  `std::out_of_range` (`enum_map::operator[]` uses `.at`; `buff_collection::get`; shared memory out of range),
  `std::bad_variant_access` (`ability.get<T>()` of the wrong kind) and `std::bad_optional_access` (`info().value()` on an empty slot).
- As in Python, the bool actions (`move`, `move_absolute`, `move_towards`, `place_ward`, `ability::use`, `consumable::use`) return
  false **only** for a newly revealed hidden obstruction. Known-invalid actions throw.
- The `is_visible()` / `vision::has_*()` / `in_vision()` queries swallow not-in-vision errors and return false.
- Python's `except Exception` becomes `catch (const std::exception&)`. Each caught throw costs about 3.8k, so actions go through `try_*` helpers
  that check their preconditions first and catch only as a last resort, logging inside `debug_block`.

| Python | C++ | Notes / cost |
|---|---|---|
| `cambc.me()` | `cambc::self()` → `champion&` | Static instance. No cost |
| `cambc.is_draft()`, `cambc.end_turn()` | same names | |
| `cambc.round_number()` | `cambc::round_number()` → `uint32_t` | 23. Store as `int64` |
| `cambc.fuel_remaining()` | `cambc::fuel_remaining()` → `uint64_t` | 5 |
| `cambc.global_submitted_gems(Team.ALLY)` | `cambc::global_submitted_gems(team::ally)` | 20 |
| `cambc.champions(Team.X)` (all, hidden too) | `cambc::champions(team::x)` → `vector<champion>` | About 600 per champion. Cache at init |
| `int(c)` (handle) | `static_cast<uint32_t>(static_cast<cambc::handle_champion_t>(c))` | Wrap it in `handle_of()` |
| `me.position()` / `health()` / `max_health()` / `strength()` / `focus()` / `attack_range()` | same names (float, int32 for range) | 50–75 each. Snapshot once per turn |
| `me.can_move()` / `can_attack()` / `is_recalling()` / `is_submitting_gems()` / `is_teleporting()` / `is_alive()` | same | Each is a separate `sdk_champion`. Use `state()` once, then `.contains(champion_state::x)` |
| `me.gold_count()` / `gem_count()` / `champion_name()` | same; `champion_name()` → `champion_type` | `champion_type::marcella` etc. |
| `me.item_count()[int(Item.X)]` | `me.item_count()[cambc::item_type::x]` | Returns `enum_map` by value (378). Call once |
| `Item.BRUISER_SHARD_OF_STRENGTH` … | `cambc::item_type::bruiser_shard_of_strength` … | All lower snake case |
| `me.consumables()[int(Cons.TP_CRYSTAL)]` | `me.consumables()[cambc::consumable_type::tp_crystal]` | `.count()` (46), `.use(vec2)` → bool |
| `me.can_buy(item, 1)` / `me.can_buy(Cons.X)` | `me.can_buy(item, 1)` / `me.can_buy(cambc::consumable_type::x)` | Overloads |
| `me.buy(item, 1)` / `me.buy(Cons.X)` | `me.buy(item, 1)` / `me.buy(cons)` | void. Throws |
| `me.abilities()` | `me.abilities()` → `std::array<ability,2>` copy | 105. Cache at init |
| `ab.is_ready()` | same | 103. Once per slot per turn |
| `ab.is_dash()/is_cc()/is_damage()/is_aoe_damage()/is_heal()/is_shield()/is_attack_reset()` | same | Native |
| `ab.info().range/radius/modifier/duration/exclusive_with_movement` | `ab.info()` → `const std::optional<ability_info>&` (a `std::variant` of 7 structs) | Read with `std::visit` + `if constexpr (requires { v.radius; })` into `AbInfo` at init. Throws for out-of-vision enemy abilities |
| `ab.damage_amount()` | same | 55 |
| `ab.use(None)` / `ab.use(vec2)` / `ab.use(unit)` | `ab.use()` / `ab.use(vec2)` / `ab.use(const champion&)` / `ab.use(const camp&)` | Typed overloads, so `Target` carries the kind |
| `me.attack(unit_or_lock)` | `me.attack(const unit&)` / `me.attack(const altar_lock&)` | void. Throws. Check `can_attack` + `cheb ≤ range` first |
| `me.attack_tiles().is_set(t)` | `cheb(pos, t) <= range` | Same set (`attack_tiles_into` = `draw_chebyshev(position, attack_range)`). Saves 919 |
| `me.move_absolute(t)` | same → bool | |
| `me.recall()` / `me.submit_gems(a)` | same, void | Throws. Pre-check: not on spawn; gems > 0, altar adjacent and not enemy-locked |
| `me.place_ward(t)` / `me.ward_cooldown()` / `me.ward_positions()` | same | 115 for the positions vector |
| `me.buffs().has_shield()` | same | One call loads all buffs |
| `e.is_visible()` | same | 64. Never throws |
| `e.remaining_channel_time()` | same | **Throws if not channelling** (code 115, seen in the benchmark) |
| `e.gem_count()` / `e.is_submitting_gems()` … on enemies | same | Need vision |
| `cambc.vision.champions(Team.X)` | `cambc::vision::champions(team::x)` | About 1.1k per visible champion. Prefer cached objects + `is_visible()` |
| `cambc.vision.camps()` | `cambc::vision::camps()` | About 350 per camp + base. Prefer the `awake_occ`/`camp_occ` boards + cached `CampRec` |
| `c.state()` / `is_dead()` / `is_awake()` / `health()` / `strength()` / `position()` / `is_visible()` / `kind()` / `spawn_position()` | same (`camp_state` has `is_dead/is_alive/is_awake/is_asleep`) | About 50 each. `spawn_position`/`kind` are free |
| `c.attack_range()`, `c.base_stats()` | same | 176 / 163. Cache per `camp_type` |
| `game_map.camp_groups()` | `cambc::map::camp_groups()` → `vector<camp_group>` | **32k on 100x100**. Once at init. Same engine order, so the group index in shared memory is identical |
| `g.gem_value()/gold_value()/camps()/spawn_tiles()` | same (`camps()` → `span<const camp>`) | `spawn_tiles()` builds a new board each call (857). Cache |
| `G.g.state()` + `isinstance(st, CampGroupRespawning)` | `g.state()` → `std::variant<camp_group_alive, camp_group_reward_available, camp_group_respawning>`; `std::get_if<cambc::map::camp_group_respawning>(&st)->timer` | Throws if no member spawn tile is visible: pre-check with `vis` |
| `game_map.walls()/holes()/altars()/bushes()/spawn_region(t)` | `cambc::map::walls()` … → `const bitboard&` | Cached and const, so it cannot be mutated by accident |
| `game_map.width()/height()` | `cambc::map::width()/height()` | |
| `cambc.vision.visible_tiles()/camp_tiles()/champion_tiles()/teleport_tiles()/ward_tiles()` | same, plus `*_into(out)` (and `awake_camp_tiles`, `altar_lock_tiles(team)`) | 450–500 new, 190 `_into` on 100x100 |
| `cambc.vision.has_altar_lock(a) and altar_lock_at(a).is_enemy()` | `enemy_lock.is_set(a)` with `enemy_lock = vision::altar_lock_tiles(team::enemy)` | One board per turn |
| `cambc.vision.altar_lock_at(a)` | same → `altar_lock` | Throws if none (pre-check with the board) |
| `cambc.vision.in_vision(p)` / `has_camp(p)` | same | 43 / 48 |
| `Bitboard()` / `.copy()` | `cambc::bitboard{}` (zeroed) / copy-construct | 390. `bitboard{cambc::uninitialized}` when an `_into` call overwrites it |
| `\| & ~ \|= &=`, `shift_right/shift_up`, `draw_chebyshev`, `set/is_set/is_empty/count/positions`, `reachable_tiles` | same names; plus `*_into`, `positions_into(span)` | `reachable_tiles(origin, uint16_t)`; `draw_chebyshev(center, float)` |
| `DistanceField()` / `compute(walls, roots, visited)` / `compute_to(walls, roots, dests, visited)` / `get(p)` | `cambc::distance_field` with the same argument order, plus `max_distance` and `*_with_expansion_count` | `get` → `uint16_t`, `distance_field::unreachable` = 65535 |
| `cambc.shared_memory.read(0, buf)` | `cambc::shared_memory.read(0, std::span<std::byte>{buf})` | 31 |
| `cambc.shared_memory[7]` / `[i] = v` / `.write(slot, bytes([v]))` | `std::uint8_t(cambc::shared_memory[7])` / `cambc::shared_memory[i] = std::uint8_t(v)` | 30–34 |
| `cambc.draft.current_draft(Team.ALLY)` / `cambc.draft.pick(D.X)` | `cambc::draft::current_draft(team::ally)` / `cambc::draft::pick(champion_draft::x)` | `pick` throws on failure |
| `cambc.draft_memory.submit(b"...")` | `cambc::draft_memory = std::string_view("...")` | Draft only. Throws otherwise |
| `cambc.ChampionDraft.VESPER_VALE` … | `cambc::champion_draft::vesper_vale`, `vendetta`, `marcella`, `heart_of_ruin`, `ryth`, `tavi`, `varg`, `ren`, `willow`, `stellar`, `prism`, `cassi_and_issac` | |
| `Vec2(x, y)` / dict key | `cambc::vec2{x, y}` / `std::hash<vec2>` exists | Prefer index arrays |

**Further C++ pitfalls:**
- SDK getters return `float`. Do the model arithmetic in `double` to match the Python thresholds.
- Use `std::stable_sort` wherever Python sorts: `target_order`, retreat dash candidates, ward candidates, crossing landing tiles.
  `positions()` is row-major in both SDKs.
- Never copy `distance_field` (it deep-copies 21.6 KB) or `std::vector<champion>` in hot paths.

---------------------------------------------------------------------------------------------------------------------

## 7. Memory layouts (identical to tb_merge_b)

### 7.1 Shared memory (8 bytes, team-wide, whole match)
| Byte | Writer | Encoding | Reader |
|---|---|---|---|
| 0–5 | The champion with `slot = s` | `0` = no claim, else `group_index + 1`. `group_index` = position in `map::camp_groups()`; an index ≥ 255 writes 0. Written every farming turn; cleared (0) when dead, banking, recalling or idle | `read_claims` counts other slots' bytes over **0..6** (quirk 1) |
| 6 | — | Free, always 0. Do not use it until parity has been measured. Later candidate: an enemy-sighting beacon (HANDOFF §5.7) | |
| 7 | Any champion that engages | `((enemy_idx + 1) << 5) \| (round & 31)`. `enemy_idx` = index in the ascending-sorted enemy handles; written only if `enemy_idx < 7` | `read_focus`: none if `v == 0` or `(round − (v & 31)) mod 32 > FOCUS_TTL (3)`; else the handle `enemy_handles[(v >> 5) − 1]` |

- **Slot:** `slot = min(index of own handle in ascending-sorted ally handles, 7)`. There are at most 6 bodies (5 picks with Cassi and Issac), so slots are 0–5.
- **C++:** one `shared_memory.read(0, 8)` per turn into `Comms` (31 fuel); single-byte writes (30 fuel).
  The modular test must use signed arithmetic: `((int64)rnd − (v & 31)) mod 32`, with a non-negative modulo, as in Python.

### 7.2 Draft memory (1,024 bytes, written by the draft bot, read-only for champions)
| Bytes | Content |
|---|---|
| 0–14 | ASCII `tb_splitfarm v1` (no terminator), written on every draft turn as Python does |
| 15–1023 | Zero. Champions do not read draft memory in tb_merge_b |

**Optional later use (not part of the parity port):** the draft bot has 10M fuel on its first turn and the full map.
It could precompute compact tables into bytes 16+ behind a version byte. For example, u8 path distances among group centres, altars and
spawn: 40 points → 780 bytes, which would make the `detour` altar→G leg exact. It must stay behind a version check so that old readers are unaffected.

---------------------------------------------------------------------------------------------------------------------

## 8. Implementation order and validation
1. `params.h`, `state.h`, `fuel.h`, `comms.cpp`, `draft.cpp`, `main.cpp`. Build and smoke run against `starter-cpp`.
2. `map_static.cpp` (init, components, static fields, turn field), `sensing.cpp`, `movement.cpp`.
   Port `step_toward` exactly first; add the fast path second and A/B it.
3. `targeting.cpp` and the farming branch, with no PvP: smoke on the quick maps against `sf_base`.
4. `banking.cpp`, `shop.cpp`. 5. `combat.cpp`. 6. `pvp.cpp`.
7. **Parity:** `python3 tools/eval.py cpp_port tb_merge_b --maps sprint --jobs 4 --tag cpp_port-parity --keep`.
   - Expect about 50% with `botFaults 0`.
   - Read the `bot error` lines in `team-a.stdout`.
   - `postmortems/match_metrics.py matches/cpp_port-parity` must show **fuelExhausted = 0**.
8. **Fuel acceptance**, from `python3 -I bots/cpp_port/tools/fuel_report.py matches/cpp_port-parity`:
   - **01big-world:** p50 ≤ 30k, p99 ≤ 75k, and no turn other than first turns at the budget;
   - **30x30 maps:** p99 ≤ 30k.
   - Also run once with `--release` (`./cli/cambc run cpp_port tb_merge_b --map 01big-world --release`): the platform mode.
9. Only after parity: enable the C++-only improvements, one per A/B as in HANDOFF §6. Candidates:
   - the static-field fast path, if it was not already needed for fuel;
   - spending the freed fuel on deeper fight evaluation;
   - draft-memory distance tables.
