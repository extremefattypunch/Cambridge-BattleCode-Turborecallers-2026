# tb_merge_a: Sprint 3 merge of sf_bank + sf_pvp + sf_draft + sf_fuel

Base: `bots/sf_base` (the frozen tb_splitfarm). sf_maps is **excluded**.
The patches went in this order: sf_bank, then sf_pvp, then sf_draft, then sf_fuel. After them comes one merge-only fuel guard.
Each step was A/B-tested against sf_bank (`--maps quick --jobs 3`), and each step's source is snapshotted in
`matches/tb_merge_a-good-s{1..5}/src`. The shipped source is identical to `good-s5`.

The base strategy (farming, claims, crossing, camp safety) is unchanged; see the tb_splitfarm notes at the end.
For details of each patch, read `bots/<patch>/CHANGES.md`.

## Patches included
| step | patch | how it applied | quick A/B vs sf_bank (24 games) |
|---|---|---|---|
| s1 | sf_bank | `patch -p2` clean; identical to bots/sf_bank | (is sf_bank) |
| s2 | + sf_pvp | 7/11 hunks clean, 4 merged by hand (see below) | `19W-5L (79%)  avg gems 889 vs 287  avg deaths 8.3 vs 18.2  botFaults(A) 0` |
| s3 | + sf_draft | clean (draft.py PRIORITY, Bruiser items in shop, kit hooks) | `20W-4L (83%)  avg gems 845 vs 265  avg deaths 8.4 vs 18.9  botFaults(A) 0` |
| s4 | + sf_fuel | 8/12 hunks clean, 4 merged by hand + banking made cache-aware | `23W-1L (96%)  avg gems 1015 vs 217  avg deaths 6.7 vs 20.5  botFaults(A) 0` |
| s5 | + merge fuel guard (`FUEL_KEEP_TARGET`) | new | `24W-0L (100%)  avg gems 1014 vs 222  avg deaths 6.5 vs 21.4  botFaults(A) 0` |

fuelExhausted per game on the quick set: s2 502, s3 542, s4 119.5, s5 93.5.

## How conflicts were resolved
### sf_bank + sf_pvp: `handle_enemies` (the decision model is sf_bank's, the targeting layer is sf_pvp's)
- **Engage/retreat.** The decision is still sf_bank's kill-time ratio: `FIGHT_ENGAGE` 0.85, 0.7 when rich, the
  `FIGHT_FLEE` clearly-losing test, the adjacent-melee stand, the stall breaker, the chase guard and `recall_safe`.
- **sf_pvp's bias, layered on top.** `focus_bias()` returns sf_pvp's ratio, and the engage limit becomes
  `sf_bank limit + (pvp ratio - 0.8)`. That adds +0.4 for a tribute or teleport channel, +0.2 for a recall,
  +0.2 for the team focus, and up to +0.3 for the gems the target carries. sf_bank's +0.15 carrier bonus stays as a
  floor. When we carry 30 gems or more, sf_pvp's cap leaves non-channellers with only sf_bank's own limit.
- **Target ordering.** Targets are sorted by sf_pvp's key `(tier, my_ttk / (1 + gems/20), d)`: channellers first,
  then the team focus, then carriers.
- **Wider candidate list.** The team-focus enemy is a candidate out to 8 tiles. It does not add to sf_bank's
  `fight_dps`, and it does not count toward the outnumbered check, which now uses `n_close` (enemies within 6).
- **Channel weighting.** `CHAN_THREAT` scales both sf_bank's `fight_dps` and `threat`: tribute 0.5, teleport 0.
- **Engage branch.** It starts with `write_focus(best)`, which writes shared byte 7, then
  `moved = stun_channel(...)`, then sf_bank's dash/step/attack and chase-guard code.
- **Shared memory.** Bytes 0-5 hold the claims and byte 7 the focus. Byte 6 is free. `read_claims` loops
  `range(FOCUS_BYTE)`.

### sf_bank + sf_pvp: `do_tribute` / `pick_altar`
- `do_tribute` runs sf_pvp's lock code first: `locked_altars`, the free ring, and `break_lock`.
- sf_bank's preferred altar (`pref`) is then used only when that altar is not in the enemy-locked set.
- `pick_altar` now also skips altars remembered as enemy-locked (it calls `locked_altars()`, which costs
  O(altars)).
- sf_pvp's `ENEMY_SIGHT` filter in `threats()` puts ward-only sightings in `self.far_enemies`. To keep
  sf_bank's census and altar-danger memory as they were measured, `update_alerts` receives
  `enemies + self.far_enemies`.

### sf_draft + sf_pvp: `shop()`
- No textual conflict. `buy_lock` runs before the item loop, and the item loop then calls `bruiser_item()`
  first.
- sf_bank's `strike()` calls `cast_combat`, so it gets sf_draft's landing dash, AoE aim and reset-retarget too.

### sf_fuel vs sf_bank's banking (field/visited are None once the static fields are built)
- The static-field keys are extended. `-2-i` is a field rooted at altar i's ring (`self.altar_goals[i]`).
  `sf_roots(key)` gives the roots for every key kind, and both `build_static_fields` and `sf_dests` use it.
  `sf_todo` builds the altar keys first, then the groups. sf_fuel's whole-ring key `-1` is no longer built,
  because nothing uses it.
- `altar_goal_dist(i, goals, pos, field, visited)` reads the static field when it is built. Otherwise it reads
  the per-turn field, which is exact for the unbuilt keys because `sf_dests` includes their rings.
  `pick_altar(..., pos)` uses this function, so it gives the same answer as sf_bank's per-altar path distance.
- `detour(..., pos)` uses `self.group_dist(G, pos, field, visited)` in place of `field.get(G.center)`.
- `altar_distance` falls back to the per-altar fields when `visited is None`. It is unused, as it was in sf_bank.
- `choose_target`:
  - sf_fuel's `target_order` loop header, bound skip, score fuel floor and tie-break are in.
  - sf_bank's death-memory multiplier (x0.3) and `escape_ok` skip keep the bound valid: multiplier <= 1.
  - The stuck guard (`note_progress`, `banned`) is in.
- `main.py` calls `bot.build_static_fields()` after `play_turn()`.
- `FUEL_FIRST_TURN_MIN` sits before sf_bank's dead branch in `play_turn`.

### Merge-only addition: `FUEL_KEEP_TARGET` (1.0M)
- **What it does.** If fuel is under 1.0M when `choose_target` starts and the current target is still valid
  (not banned, and not respawning for more than 30 more rounds), the current target is kept for that turn.
- **Why.** Profiling 400 rounds of 00lanes showed `target_order` alone costs about 355k per call and
  `choose_target` about 755k. With sf_bank's fight code, sf_pvp's ward and lock code and `update_alerts` added,
  heavy turns overran the budget.
- **Effect.** Turns over 2.4M fell from 87 to 29 in that 400-round sample, and the quick set went from 119.5 to
  93.5 fuelExhausted per game. W-L went from 23-1 to 24-0.

## Final validation (shipped = good-s5)
- (a) **Sprint vs sf_bank (40 games):** `SUMMARY tb_merge_a vs sf_bank: 37W-3L (92%)  avg gems 881 vs 248  avg deaths 5.5 vs 18.4  botFaults(A) 0`
  - The losses were 02guardians A (0-0, gold tie-break; sf_bank also lost it) and 01concentrated-wealth on
    both sides (497-877 and 726-854).
- (b) **Quick vs tb_aggro (24 games):** `SUMMARY tb_merge_a vs tb_aggro: 24W-0L (100%)  avg gems 1014 vs 222  avg deaths 4.9 vs 30.9  botFaults(A) 0`
  - For comparison: sf_bank 19W-5L, sf_pvp v2 22W-2L, sf_base 9W-15L.
- (c) **match_metrics on (a):**

  | metric | per game |
  |---|---|
  | mean tribute | 24.2 |
  | fuelExhausted | 66.7 (sf_bank in the same games: 354.1) |
  | botFaults | 0 |
  | deaths_by_camp | 0.6 |
  | deaths_by_champion | 4.9 |
  | gemsLost_to_champion | 35.8 |
  | wards | 449 |

  - Of the remaining fuelExhausted, 1293 of 2667 come from the two 00lanes games. 01islands accounts for 317.
- (d) **Release game:** `./cli/cambc run tb_merge_a sf_base --map 02crossing --release` was won 1006-110 in round
  1074, with **0 crashes** and empty stdout (no `bot error` lines).

## Known risks
- **Self-play only.** Every number above comes from our own bot family plus tb_aggro. sf_pvp's proactive
  locks make bots that stall at locked altars look worse than they are.
- **Fuel.** 00lanes still has about 650 exhaustions per game, and 01islands about 160.
  - The remaining cost is `observe` + `threats` (base code, up to 1.1M + 0.9M) and sf_bank's
    `retreat`/`handle_enemies` in fights (up to 1.2M).
  - `FUEL_KEEP_TARGET` is the only approximation the merge added. It applies only under fuel pressure.
- **01concentrated-wealth** was lost on both sides in the sprint run. It is a farming race with few deaths, and
  sf_bank lost it on side B as well. Not investigated.
- **Aggression.** The bias stacks on the engage limit. A channelling carrier on the team focus can reach a limit
  of about 1.75, against sf_bank's 0.85. This could backfire against bots that cancel a tribute to fight back.
  Lower the ratios in `focus_bias` if it does.
- **HoR** (5th pick on 4-5 pick maps) is still the weakest farmer, as sf_draft notes.
- **Static fields.** One full-map field is built per altar and per camp group, in spare fuel only (above 1M).
  Memory grows with the map's altar count.

---

# Base strategy (tb_splitfarm / sf_base notes, unchanged)

## Strategy
- Draft: fixed priority list of strong solo farmers, dash champions early:
  Vendetta, Varg, Ryth, Vesper Vale, Marcella, Heart of Ruin, Tavi, Ren, ...
- Every champion scores every camp group as value / time
  (value = gems + 0.25*gold; time = path distance + kill time + capture + respawn wait
  + an attrition penalty when the fight needs several recall cycles).
- Spreading: each champion writes its current target group (idx+1) into its own byte of
  the 8-byte team shared memory (slot = rank of its handle among ally handles).
  Groups claimed by an ally are discounted (x0.3) when soloable, and *boosted* (x1.2)
  when they are too heavy to solo (so allies regroup on elks/golem packs); team kill time
  and tank damage assume +55 dps and shared tanking per joining ally.
- Never die to camps: before engaging, estimated damage taken (sum strength * kill time,
  x0.7 for multi-camp groups, x0.7 with Jungle emblem) must fit in HP-150, or the fight
  must be finishable within <=4 hit-and-run cycles. While fighting, if HP <= incoming *
  (steps needed to leave range + 1) + 60 and we cannot finish the camps first, step to the
  adjacent tile with the least incoming damage (dash if available). Recall when out of
  range and HP < 45%; heal to 92% on spawn before leaving.
- Enemy champions: chase/kill when our time-to-kill < 0.8 * their time-to-kill-us
  (dash to close), otherwise step away / recall (and always step away carrying >=15 gems).
- Tribute when gems >= 35, altar within 4 tiles, HP low with >=12 gems, enemies near with
  >=10 gems, team total would reach 1000, no target left, or the round limit is close.
- Shop on spawn/while dead: Jungle shards of strength (emblem: -30% camp damage), then
  Monster shards of strength (+15% camp damage), then alternating Power strength / health.
  Recall to shop when rich (>=150 gold, few gems).
- Unreachable areas: walk components (walls|holes|altars|enemy spawn blocked) computed
  with native reachable_tiles; staging tiles = my component & dilate(target component, r)
  (r=2 dash, r=3 TP crystal). Buys a TP crystal (10g) whenever the map has such areas.
  If the altar is not reachable from an island we recall.

## Engine / API behaviour learned (verified in games)
- Camps do NOT regenerate HP while asleep (monolith stayed at 19145 -> 17015 for 500+
  rounds; a 5-hp gold cluster stayed at 5). So hit-and-run attrition with recalls works.
- Standing on a camp's spawn tile blocks the whole group's respawn forever: a bot that
  "waits" on the tile deadlocks the camp (and its own target loop). Never idle on spawn
  tiles unless capturing.
- Camps standing on bush tiles are invisible from outside the bush cluster. Moving onto a
  hidden occupant returns False (no exception) every turn -> infinite loop if not handled.
  Fix: treat assumed-alive camp tiles as non-enterable, and walk into an adjacent bush tile
  of the same cluster to see them.
- vision.camps()/Camp.is_visible() never report dead camps; detect a dead camp as
  "tile visible and vision.has_camp(tile) is False".
- Replay bundles (.repl26a) are zip files containing team-a.stdout / team-b.stdout - the
  only place bot prints go (`cambc run -o DIR` keeps them).
- --statistics JSON: events of kind "death" have owner = the dying champion and
  entries[].target = the killer (None = killed by a camp).
- Starter Vesper Vale snowballs: +33% gold -> 100+ Power strength shards; it kills
  champions that ignore it. Melee champions must chase ranged attackers (they stand still).
- DistanceField.compute(walls, roots, visited) fills the whole component (no max needed);
  use the visited board to test reachability.

## Eval numbers (tools/eval.py vs starter-python)
- v1 (no enemy handling): quick 15W-9L (62%), gems 457 vs 331, deaths 5.1 vs 38.7.
- v2 (+attrition model, respawn-tile deadlock fix, bush-hidden camps, crossing fixes):
  quick 23W-1L (96%), gems 935 vs 285, deaths 7.5 vs 38.8.
- v3 (+always step away from unfavourable enemies, ally dps in fight check, recall to shop
  when rich): quick 24W-0L, gems 960 vs 173, deaths 4.2 vs 36.2.
- FINAL sprint (20 maps x 2 sides):
  SUMMARY tb_splitfarm vs starter-python: 40W-0L (100%)  avg gems 878 vs 152  avg deaths 3.3 vs 39.7  botFaults(A) 0
- Tried and reverted: (a) attacking huge groups (00stampede 20-camp elk herd) with a
  "local strength" model and 12-cycle cap - never finished the herd and lost the gold
  tiebreak; (b) caching the whole-map DistanceField for 8 turns + re-scoring targets every
  4 turns - cut fuel a lot but movement/targeting regressed badly on 01big-world (15 gems);
  saved in matches/tb_splitfarm_scratch/bot_cache_attempt.py.

## Fuel
- Measured with cambc.fuel_remaining() on 01big-world (100x100-ish): one full-map
  DistanceField.compute costs ~575k fuel; scoring 24 groups in Python costs ~900k
  (~37k fuel per group!); observe ~100k; threats ~50-80k. A turn can exceed the 2.5M
  budget on big maps (the bot gets suspended and resumes next round). Python per-group
  loops are the expensive part, not the native ops. Only safe fix shipped: the target
  is scored once per turn (the tribute check reuses it).

## Known weaknesses
- No multi-hop island crossing; TP landing only within 3 tiles of the staging tile.
- Monolith is never attempted (too much damage per cycle).
- Maps whose only gems sit behind a monolith or a 20-camp elk herd (02guardians,
  00stampede) score 0 gems; we only win those on the gold tiebreak.
- Fuel heavy on 100x100 maps (see Fuel) - occasional mid-turn suspension.
- Enemy fight model is simple (ttk comparison); a focused champion-hunting opponent
  could still pick off lone farmers.
