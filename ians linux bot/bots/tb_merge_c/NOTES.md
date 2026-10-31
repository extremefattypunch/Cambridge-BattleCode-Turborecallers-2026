# tb_merge_c: Sprint 3 merge (sf_bank, then sf_draft, then sf_fuel)

Base: `bots/sf_base` (frozen tb_splitfarm). Created with `tools/newbot.py sf_base tb_merge_c`.
Merge order (conservative): **sf_bank -> sf_draft -> sf_fuel**. **sf_pvp is not included**, to avoid
its `handle_enemies` conflict with sf_bank, and sf_maps was neutral, so it is not included either.
One merge-specific change was added at the end: the draft order (step 4 below).
Snapshots of each validated step: `matches/tb_merge_c-good-s1` (sf_bank), `-good-s2` (+sf_draft),
`-good-s3` (+sf_fuel), `-good-x1` (+draft order, the **shipped** version, identical to `src/`).

## What is in
| step | content | how it went in |
|---|---|---|
| s1 | **sf_bank** (whole patch): kill-time fight/flee model, detour-aware banking, camp safety and death memory, stall breaker, chase guard | `patch -p2`, clean. The result is byte-identical to `bots/sf_bank/src`. |
| s2 | **sf_draft** (whole patch): meta draft in `draft.py`, Bruiser items (`bruiser_item()` in `shop()`), HoR landing dash, AoE aim, attack-reset retarget | `patch -p2`, clean (hunk 1 with fuzz, checked by hand). One small merge edit, listed below. |
| s3 | **sf_fuel** (whole patch): static distance-field cache, pruned target scoring, `can_reach` memo, fuel floors, first-turn guard, stuck guard, `main.py` `build_static_fields()` | `patch -p2`, 3 hunks rejected and resolved by hand, listed below |
| x1 | **draft order**: `VESPER, VENDETTA, MARCELLA, RYTH, VARG, HoR, TAVI, ...` | a new `PRIORITY` assignment in `draft.py`, after sf_draft's list |

## Conflict resolution and merge edits
- **sf_draft with sf_bank.** The two don't conflict textually. sf_bank's `strike()` (stand and hit) calls
  `cast_combat`, so the sf_draft kit hooks also run in the enemy branch.
  - The merge edit: sf_bank's `champ_dps()` (our damage against champions in the kill-time model) now
    also counts the landing-dash damage / 8, behind `KIT_LANDING_DASH`. This mirrors sf_draft's
    change to `dps()`.
- **sf_fuel with sf_bank: the main conflict.** Once all static fields are built, `field` and `visited`
  are `None`. sf_bank's banking reads both directly: `pick_altar` takes the path distance per altar,
  and `detour` takes the path distance to the next target.
  - Static fields are now keyed per altar (`-2 - i` for `altar_goals[i]`, built first) instead of
    sf_fuel's single whole-ring field `-1`. sf_bank no longer uses `altar_distance`, and
    `pick_altar` needs the distance to each altar separately because of locks and the danger penalty.
    `build_static_fields` and `sf_dests` root those fields at `altar_goals[i]`.
  - A new `altar_goal_dist(i, goals, pos, field, visited)` reads the static field once it is built.
    Before that it reads the per-turn field, which is still exact because the unbuilt altars' goal
    tiles are in `sf_dests`. It returns BIG when neither field is available.
  - `pick_altar(..., pos)` uses `altar_goal_dist`. `detour(..., pos)` uses `self.group_dist(G, pos, field, visited)`.
    `altar_distance` (unused) now takes the minimum over the per-altar fields.
  - `group_dist` returns None, instead of raising, if `visited` is None.
- **The `choose_target` loop.** It uses sf_fuel's `target_order` header, bound skip, fuel floor and
  lowest-idx tie-break. sf_bank's death-memory multiplier (x0.3) is <= 1, so `SCORE_BOUND_MULT = 1.95`
  is still a valid bound.
- **Rejected hunks of sf_fuel:**
  - `__init__` state: added after sf_bank's state.
  - The tie-break line: placed after sf_bank's death penalty.
  - `altar_distance` in `play_turn`: obsolete, because sf_bank replaced it with `pick_altar`.
- **sf_fuel's `note_progress`** (stuck guard) is still the last line of the farming branch. The
  first-turn guard sits before sf_bank's dead-champion bookkeeping.
- **Shared memory:** unchanged. Bytes 0-5 hold the claims. Nothing uses bytes 6 or 7, because sf_pvp is not merged.

## Draft order (x1): why HoR was demoted
- In the s3 quick A/B, the losses clustered on 5-pick maps: 02famine and 00crater were lost on both
  sides, against sf_bank's Varg roster.
- Per champion in s3's 4/5-pick games, HoR collected 155 gems and did 9.0k monster damage per game.
  The others collected 190-225 gems and did 21-26k.
- In x1's games, Varg (on the old Jungle -> Monster -> Power build) collected **281 gems per game**
  and did 27.4k monster damage, the most of any of our champions.
- On the ten 4/5-pick maps (20 games): **s3 went 8W-12L and x1 went 14W-6L**.
- 3-pick maps are unchanged (Vesper, Vendetta, Marcella). 4-pick maps now take Ryth instead of HoR.
  HoR is 6th and still gets the kit code if it is ever drafted.

## Eval lines (all `--jobs 3`)
- s2 (sf_bank + sf_draft), quick: `SUMMARY tb_merge_c vs sf_bank: 14W-10L (58%)  avg gems 810 vs 522  avg deaths 7.7 vs 19.4  botFaults(A) 0` (fuelExhausted 524.0/game)
- s3 (+ sf_fuel), quick: `SUMMARY tb_merge_c vs sf_bank: 16W-8L (67%)  avg gems 868 vs 571  avg deaths 7.5 vs 19.2  botFaults(A) 0` (fuelExhausted 63.3/game)
- s3, sprint: `SUMMARY tb_merge_c vs sf_bank: 25W-15L (62%)  avg gems 754 vs 556  avg deaths 7.5 vs 16.3  botFaults(A) 0` (fuelExhausted 45.0/game)
- x1, 4/5-pick subset (10 maps): `SUMMARY tb_merge_c vs sf_bank: 14W-6L (70%)  avg gems 878 vs 619  avg deaths 9.8 vs 15.8  botFaults(A) 0`
- **FINAL (x1), sprint, vs sf_bank** (`matches/tb_merge_c-final-vs-bank`):
  `SUMMARY tb_merge_c vs sf_bank: 30W-10L (75%)  avg gems 801 vs 486  avg deaths 7.0 vs 16.1  botFaults(A) 0`
  - match_metrics: mean tribute 22.7, deaths_by_camp 0.7/game, deaths_by_champion 6.3/game,
    gemsLost_to_champion 28.6/game, **fuelExhausted 27.2/game**, no botFault events.
- **FINAL, quick, vs tb_aggro** (`matches/tb_merge_c-final-xag`):
  `SUMMARY tb_merge_c vs tb_aggro: 22W-2L (92%)  avg gems 977 vs 360  avg deaths 5.5 vs 32.2  botFaults(A) 0`
  - For comparison, sf_bank alone went 19W-5L and sf_base 9W-15L.
- **Platform mode:** `./cli/cambc run tb_merge_c sf_base --map 02crossing --release` was won 1012-248
  in round 1016, with **0 crashes**, botFaults 0 and 3 fuelExhausted.
- **Cross-check, quick, vs tb_economy** (`matches/tb_merge_c-final-xeco`):
  `SUMMARY tb_merge_c vs tb_economy: 22W-2L (92%)  avg gems 960 vs 324  avg deaths 2.0 vs 45.3  botFaults(A) 0`
  - For comparison, sf_bank and sf_draft each went 21W-3L. fuelExhausted was 30.8/game.
  - The losses were 01islands B (905-1007) and 00crater B (92-154, a stand-off).

## Known risks
- Every A/B is self-play against our own family, mostly sf_bank, and that pairing is close to
  deterministic. The draft change (x1) was chosen on games against sf_bank and was then confirmed on
  the full sprint and against tb_aggro, but no other opponent was tested.
  - The meta draft argument (top-20 teams all draft HoR) is overridden here because our HoR plays poorly.
- Still lost on both sides or near-even, against sf_bank on the sprint set:
  - 02guardians A: 0-0, lost on the gold tie-break. sf_bank had the same problem.
  - 01concentrated-wealth, on both sides.
  - 02the-pond B: a 36-45 stand-off, also lost by sf_bank and sf_draft.
  - 00gemfight A, 00quadrants A, 02harvest A, 01starvation A, 00monolith B, 00crater B.
- fuelExhausted is about 27 per game, mostly on 00lanes and 01islands: about 500 per game on
  00lanes in the s3 quick run, and 100 on 01islands. It is far below sf_bank's 384 per game but not zero.
- sf_fuel's stuck guard and sf_bank's chase guard and stall breaker all run, and their combination
  was only measured as a whole.
- The sf_pvp features are absent: focus byte 7, stun channels, altar locks and wards. This bot does
  not place wards or use altar locks, so an opponent that locks altars is handled only by sf_bank's
  `pick_altar` skipping enemy-locked altars.
