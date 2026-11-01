# cpp_port: C++ port of tb_merge_b

**Status (31 Oct):** complete faithful port, builds clean, no `bot error` lines and **0 fuel exhaustions** in every
local game so far (Python tb_merge_b: about 87 per game in the same matches). It plays at parity with the Python
champion: quick 13W-11L (54%), sprint 20W-20L (50%), and won the release-mode (platform) check on 01big-world.
Nothing is submitted. The design and the fuel benchmarks are in `DESIGN.md`.

## Layout (`src/`, about 3,200 lines)
| File | Contents |
|---|---|
| `params.h` | Every tb_merge_b constant (same names and values) plus the C++ fuel guards |
| `bot.h` | `Group`/`CampRec`/`AbInfo`/`Unit`/`CampView`/`Tgt`, the `Bot` class, scratch boards, debug profiler (`PROF`) |
| `core.cpp` | Champion snapshot, raw SDK wrappers, lazy per-epoch vision boards, `blocked_now`, `init_static`, walk components, `staging`, `can_reach`, `escape_ok`, static-field cache (`build_static_fields`, `sf_dests`, `turn_field`, `group_dist`), shared-memory comms |
| `sense.cpp` | `observe`, `threats`, `update_alerts`, `threatened` |
| `move.cpp` | `step_toward`, `go_to`, `cross_toward`, banking (`pick_altar`, `detour`, `bank_now`, `bank_detour`, `do_tribute`, `locked_altars`, `break_lock`) |
| `combat.cpp` | `dps`, `champ_dps`, `cast_combat`, kit helpers, `reset_target`/`reset_and_hit`, `pick_camp_in_range`, `retreat`, `recall_safe`, `adjacent_melee`, `strike`, `handle_enemies`, `chan_kind`, `focus_bias`, `stun_channel` |
| `target.cpp` | `choose_target`, `note_progress`, `shop`/`bruiser_item`/`buy_lock`, `try_lock`, `try_ward` |
| `bot.cpp` | `Bot::play_turn` (the flow of `Bot.play_turn`) |
| `draft.cpp`, `main.cpp` | Draft priority list + `tb_splitfarm v1` draft memory; turn loop (`play_turn`, then `build_static_fields`, `bot error:` logging, always `end_turn`) |
| `tools/fuel_report.py` | Per-turn fuel percentiles from replays; `after-first` = turns after the first 12 entries (draft + first play turns), `exhausted` = such turns at the budget |

## What is ported (all of tb_merge_b's behaviour)
Draft priority, shop (TP crystal when crossing is needed, altar lock, Bruiser plan per champion, default
Jungle/Monster/Power build), split-farm target scoring with shared-memory claims (bytes 0-5), the fuel-aware
static distance-field cache (group centres and per-altar rings, same build order), census banking with the detour
rule, `pick_altar` with the altar-danger penalty, `do_tribute` with lock handling, the camp-danger step (finish or
retreat, adjacent-melee strike), the sf_bank kill-time fight/flee model with sf_pvp's focus bias, focus byte 7,
channel stuns, chase guard and stall breaker, `recall_safe`, recall/heal on spawn, altar locks (reactive and
lock-side), wards, capture (stand on a free spawn tile), respawn waiting ring, never idling on spawn tiles,
alive-but-unseen -> respawning, bush goals, ranged attack rings, avoid zones of other awake camps, hit-and-run with
`escape_ok`, death memory, the stuck guard, island crossing (dash / TP crystal / recall), kit casting (shield,
damage/CC/AoE, heal, attack reset with re-target).

**Same shared-memory and draft-memory layouts as the Python bot** (claims 0-5, byte 6 free, focus byte 7;
draft memory `tb_splitfarm v1`), so mixed teams would interoperate.

### Python quirks reproduced on purpose (parity first)
- **`AbilityDash/AbilityAoeDamage.radius` is a float in Python**, so `dilate(bb, info.radius)` raises TypeError
  inside a try. Verified with the probe bot `bots/cpp_scratch_py` (prints `RANGE_ERR TypeError(...)`). Consequences in
  tb_merge_b: **HoR's landing dash (`cast_landing_dash`) never fires** and **`aim_area` always returns the
  target tile**. The port reproduces this; `params.h: KIT_RADIUS_FIX = true` enables the intended behaviour
  (implemented, untested) for a later A/B.
- `positions()` order is **engine chunk order** (8x8 chunks row-major, then row-major inside the chunk), not plain
  row-major (also verified with the probe). Every list the Python built from a board (enemies, allies, camps,
  neighbour candidates, ward/dash/retreat candidates) is in that order in the port, so first-minimum tie-breaks match.
- `read_claims` scans bytes 0..6; the farming `avoid` test compares a camp's current position with G's spawn
  tiles; `bank_now` gets `ad = BIG`; `Group.center` = first camp's spawn; `stun_channel`'s return value is used as
  `moved` (a stun cast suppresses the chase step); our own death counts as an ally death in `update_alerts`.

## How it differs from a line-by-line translation (fuel)
Native wasm code costs about 1 fuel per instruction; a trivial loop iteration is ~8 fuel and a `malloc` a few
hundred. Measured examples from this port: filling a 3,600-entry vector ~29k, an insertion `stable_sort` of 46
groups ~40k, parsing 46 camp groups into vectors ~70k. So:
- **No exceptions for control flow:** actions and queries use the raw status-returning imports
  (`cambc::detail::sdk_champion`, `sdk_cast`, `sdk_attack`, `sdk_move_to`, ...). A failed call is the Python
  `except: pass` path. Exceptions remain only in rare paths (`break_lock`) and in `main`.
- **One snapshot per turn** (`refresh_me`, one `sdk_champion` call), refreshed after every action; enemies/allies
  from cached sorted handles (one `sdk_champion` each) instead of `vision::champions`; camps from the awake/camp
  occupancy boards plus a spawn-tile index instead of `vision::camps()`.
- **Lazy per-epoch boards** (vision, occupancy, enemy locks, `blocked_now`), recomputed only after we act.
- **`choose_target`** returns exactly the Python arg-max (ties to the lower index) but selects lazily: candidates are
  ordered by a cheap valid upper bound `value * mult_max / (cheb + ttk + 6)` and the walking distance /
  reachability is only computed for groups that can still win (Python sorted by `value*1.95/(d+6)` after computing
  `d` for every group). Reachability and escape memos are per-group lists instead of dicts.
- **Per-turn field (`dist_field`) capped at 60** (`TURN_FIELD_MAXD`) and skipped below 40k fuel; it only exists until
  the static fields are built (Python computed it uncapped). Unbuilt groups beyond 60 use the Python cross-component
  estimate `cheb*1.5+12` if reachable.
- **`step_toward` is the exact Python algorithm** (field from the goals to us, avoid pass then no-avoid pass, first
  strictly better neighbour in engine order); its search depth is clamped only when fuel is short.
- Static fields are built after `play_turn` while `fuel > estimate + 10k` (estimate from the largest expansion count
  seen); all of them exist after about 1-7 rounds on 30x30-60x60 maps and about 65 rounds on 01big-world.

## Known gaps / approximations (all fuel-driven, all small)
1. Turn field capped at 60 during the first turns (above). Affects target choice only for far groups before their
   static field exists.
2. `choose_target` budgets first-time work per call: at most 4 new `can_reach` and 2 new `escape_ok` computations,
   each only with >= 60k fuel left; a group that needs one more is skipped for that turn (Python always computed
   them). Matters on island maps in the first turns and right after crossing to a new island.
3. `FUEL_SCORE_FLOOR` is 20k (C++) instead of 800k (Python): scoring stops early only when very short of fuel.
4. `KIT_RADIUS_FIX` (the intended landing dash / AoE aim) is off for parity.
5. **Platform risk:** the port calls `cambc::detail::sdk_*` imports directly (the same engine imports the public
   header wraps). If the platform compiles against a different SDK header version where these names change, the build
   fails; the fix would be swapping the wrappers in `core.cpp` back to the public API (they are thin).
6. Init on the first play turn is expensive (camp-group parsing ~40-100k because of allocations, home-component
   flood up to ~28k, altar rings ~13k, plus ~25k wasm start-up). If less than 85k remains after init, the first turn
   only shops (Python did the same with its 2M threshold). Cheaper init = more static fields and a real first move.

## Evaluations
- Smoke vs starter-cpp (debug build): 02crossing W 1000-358 (r853), 01big-world W, 00lanes W 1002-222 (r1290),
  01islands W 1017-0 (r1439). No crashes, no `bot error`.
- `python3 -I tools/eval.py cpp_port tb_merge_b --maps quick --jobs 4 --tag cpp-port-q1 --keep`
  `SUMMARY cpp_port vs tb_merge_b: 13W-11L (54%)  avg gems 668 vs 686  avg deaths 14.0 vs 14.3  botFaults(A) 0`
  Most maps are won by the same side in both games (mirror matches), as expected for a faithful port.
  Per team per game: deaths by champion 13.5 vs 13.7, by camp 0.5 vs 0.7; mean tribute 22.2 vs 22.6; wards 380 vs
  390; consumables 10.3 vs 10.4; **fuelExhausted 0 vs 87.4**.
- `python3 -I tools/eval.py cpp_port tb_merge_b --maps sprint --jobs 4 --tag cpp-port-s1 --keep`
  `SUMMARY cpp_port vs tb_merge_b: 20W-20L (50%)  avg gems 598 vs 634  avg deaths 11.6 vs 12.6  botFaults(A) 0`
  Per team per game: deaths by champion 11.2 vs 12.1, by camp 0.4 vs 0.5; mean tribute 21.7 vs 22.6; wards 432 vs 440;
  **fuelExhausted 0 vs 63.7**. Both sides lose 00crater, 01elk-arena, 00corners, 02harvest, 00quadrants and
  00monolith to the Python bot and win 01islands, 01gold-rush, gemcombat3, 01big-world, 01starvation and
  01concentrated-wealth from both sides; the rest go to whichever side the map favours. Matches are deterministic
  (re-runs reproduce the same scores) but fuel-dependent decisions (static-field timing, budgets) shift some games.
- After the final guard change (`FUEL_FIRST_TURN_MIN` 60k -> 85k, static-build estimate more conservative):
  `--tag cpp-port-q2` quick `SUMMARY cpp_port vs tb_merge_b: 13W-11L (54%)  avg gems 678 vs 678  avg deaths 13.5 vs 14.5  botFaults(A) 0`.
- Release mode (`--release`, platform mode), `./cli/cambc run cpp_port tb_merge_b --map 01big-world --release`:
  cpp_port wins 922-683 at the round limit, 0 crashes, empty stdout; p50 26.0k, p90 41.5k, p99 60.5k, max after the
  first turns 83.6k, exhausted 0.

## Fuel (budget 100k per turn, 200k first play turn)
From the eval replays (release-mode numbers: `eval.py` stdout is empty, so debug blocks did not run).
`python3 -I bots/cpp_port/tools/fuel_report.py matches/cpp-port-q2/<map>__A.repl26a --team a`:
| Map | p50 | p90 | p99 | max after first turns | exhausted |
|---|---:|---:|---:|---:|---:|
| 02arena / 02the-pond (30x30-ish) | 10-12k | 16-18k | 26k | 38-44k | 0 |
| 00anvil / 00gemfight / 00crater | 10-14k | 16-22k | 29-35k | 46-58k | 0 |
| 00monolith / 01elk-arena / 02famine | 14-18k | 23-26k | 35-38k | 82-86k | 0 |
| 00lanes | 23k | 33k | 45k | 87k | 0 |
| 01islands | 23-24k | 33k | 60-65k | 91-93k | 0 |
| 01big-world (sprint s1) | 26k | 42k | 61k | 84k | 0 |
| 02harvest / 01starvation / 00corners (sprint s1) | 17-25k | 28-37k | 43-63k | 84-86k | 0 |

First play turn (200k budget, includes ~25k of wasm start-up before `main`): 117-184k on the quick maps. On
02harvest it reached 196.9k with the old 60k guard (no exhaustion, but 3k from the limit); with the 85k guard the
first turn only shops and builds static fields there (171k). Per-turn fuel on the large maps stays around 60-80k for
the first rounds, while the per-turn field and the static builds run.
The heaviest turns are first-time work: static field builds (up to ~33k each on 100x100), the per-turn field
(~15k on 100x100 until the static fields exist), first-time reachability after reaching a new island, and long
`step_toward` searches (up to ~26k on 100x100).

## Profiling
`PROF("name")` marks (bot.h) record `fuel_remaining()` inside `debug_block` (free in debug builds, compiled out in
`--release` and on the platform). `main.cpp` prints `PROF r<round> used <n> mark=delta ...` for any turn above 60k,
in `team-X.stdout` of the replay. Scratch copy for experiments: `bots/cpp_scratch1`.

## Next steps (only after parity is accepted)
1. A/B `KIT_RADIUS_FIX = true` (HoR landing dash and Ryth AoE aim actually working).
2. Cheaper init (fewer allocations) so more static fields are built on turn 1; then raise `TURN_FIELD_MAXD`.
3. Spend the freed fuel (median turn uses 10-25% of the budget) on deeper fight evaluation.
