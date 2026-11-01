# h_goldtie: gold-tiebreak play (STRATEGIES Q2)

Base: `bots/tb_merge_b`, with the same draft. Only `src/bot.py` changed (about 130 diff lines, all tagged `h_goldtie`).

**Hypothesis (Q2).** At round 2000, equal tributed gems are decided by lifetime gold earned, then kills, then Team B.
- We lost 02the_pack 0-0 on gold on the ladder.
- 5 of the 15 losses in the 70-map local check were 0-0 tiebreaks.
- Plan: detect when no safe gems can be obtained, switch to maximising lifetime gold, and still take any safe gems.

## Why those maps are 0-0 (map dumps + analyze_match on `matches/final-mergeb-all`)
| Map | What blocks tributes | What tb_merge_b did |
|---|---|---|
| 02the-pack (1 altar) | The altar ring is free, but it sits inside one camp group of **48 wolves** (strength 960, 64,800 HP). | Champions carrying 30+ gems walked to the ring and stood there. A path through visible camps doesn't exist, and `do_tribute` never gives up. Vesper earned 79 gold in 2000 rounds. 10 clears per game. |
| 02guardians (1 altar) | The only walkable ring tiles are the spawn tiles of **2 monoliths**. The rest of the ring is walls and holes. | It banked toward an unreachable altar. Hundreds of gems were carried; gold was 2956 vs 3210. |
| 01boss-battle (1 altar) | The same, with a 2-monolith group (40,000 HP). The other ring tiles are holes or walls. | 4216 vs 4632 gold on side A. |
| 02gift-wrapping | Altars are open, but every group is 8 to 16 camps wrapped round a wall (strength 80 to 160). | No group passes the solo safety model (`cycles > 4`). **0 clears and 0 gold for both teams**, so Team B wins. |
| 01yellow-brick-road | Altars are open. | **Movement bug:** a champion steps onto a dead camp tile of a half-cleared group. The "never block a respawn" rule pushes it back toward `G.center`, and the cycle repeats. All 5 champions froze from about r200 to r2000; 1 clear per game. |

## What changed
1. **Static detection: `init_gold`, run at init.**
   - A group with total strength ≥ 200 or total HP ≥ 15,000 is a *guard* (monoliths, the 48-wolf ring).
   - An altar is *usable* when either:
     - one of its non-guard ring tiles is reachable from our spawn, walking around walls, holes and guard tiles; or
     - its ring is on another island (the existing dash/TP crossing logic decides).
   - **No usable altar means `no_tribute`.**
   - Over all 70 maps, it flags **exactly** 01boss-battle, 02guardians and 02the-pack. Every altar on the other 67 maps stays usable, so `pick_altar` is unchanged there. Check: `matches/h_goldtie-static`, slot-0 stdout line `GOLDTIE ...`.
   - `pick_altar` skips unusable altars.
2. **When `no_tribute` is set (gems are worthless):**
   - group value = gold, and gem-only groups are skipped;
   - **guard groups get value 0**, so we never open the gate. In v1, killing a monolith opened the altar and the enemy tributed the gems it took from us;
   - no banking: no `bank_now`/`do_tribute` trips, and no tribute when there is no target;
   - **a Treasure emblem of the main stat is bought first** (+10% gold; Vesper 33% → 43%). Spent gold still counts as earned;
   - the fight model ignores carried gems, ours and theirs: `rich` is always False and the enemy-gem bonus in `focus_bias` is 0;
   - the recall-to-shop rule treats carried gems as 0.
3. **Stalled state.** From round 300, while **both** teams have 0 tributed gems, `stalled` is set (`GOLD_STALL_ROUND`). It ends at the first tribute and is sticky after that.
4. **Gold play (`no_tribute` or `stalled`):**
   - `blocks_respawn`: we step off a camp tile only if that group is respawning (status 2). A dead camp in a still-alive group never respawns on its own. This fixes the 01yellow-brick-road freeze, but only in gold play.
   - **Chip mode:** after 12 healthy turns in a row with no target, allow up to 30 hit-and-run cycles per group instead of 4. Camps don't heal; the `cycles × 30` cost term keeps chip targets as the last resort.

## Iterations
- **v1:** steps 1-4, without the guard exclusion. On 02guardians, chip mode let a 2,000+ HP late-game champion farm the monolith (worth 300 gold). With the altar open, tb_merge_b tributed 11 and then 101 gems taken from us. Result: 0-2 there (`matches/h_goldtie-tie5`, 02guardians rows).
- **v2 (final):** adds the guard exclusion (value 0 for guards under `no_tribute`). That gives 6-0 on the three `no_tribute` maps.
  - 02gift-wrapping and 01yellow-brick-road don't use `no_tribute`, so their rows in `h_goldtie-tie5` are also valid for v2 (games are deterministic).

## Results (v2 unless noted)
```
SUMMARY h_goldtie vs tb_merge_b: 21W-19L (52%)  avg gems 606 vs 636  avg deaths 12.2 vs 12.9  botFaults(A) 0   [sprint, matches/h_goldtie-sprint]
SUMMARY h_goldtie vs tb_merge_b: 6W-0L (100%)  avg gems 0 vs 0  avg deaths 1.7 vs 8.2  botFaults(A) 0       [01boss-battle,02guardians,02the-pack; matches/h_goldtie-tie3-v2]
SUMMARY h_goldtie vs tb_merge_b: 7W-3L (70%)  avg gems 14 vs 13  avg deaths 2.1 vs 7.6  botFaults(A) 0      [5 tiebreak maps, v1; matches/h_goldtie-tie5]
SUMMARY h_goldtie vs tb_merge_b: 4W-4L (50%)  avg gems 533 vs 564  avg deaths 15.4 vs 15.8  botFaults(A) 0  [stall-prone maps 00contest,00the-line,00rows,01hooks; matches/h_goldtie-stallmaps]
SUMMARY h_goldtie vs imit_test: 8W-2L (80%)  avg gems 12 vs 2  avg deaths 1.0 vs 18.0  botFaults(A) 0       [5 tiebreak maps; matches/h_goldtie-tie5-imit]
SUMMARY tb_merge_b vs imit_test: 5W-5L (50%)  avg gems 0 vs 1  avg deaths 5.2 vs 15.8  botFaults(A) 0      [baseline, same maps; matches/h_goldtie-base-tie5-imit]
```
- **Release check:** `--release` on 01boss-battle won on gold, 27,655 vs 1,715, with 0 crashes and 0 `bot error` lines (`matches/h_goldtie-release`).
- **Combined v2 on the 5 tiebreak maps vs tb_merge_b: 9W-1L.** The only loss is 01yellow-brick-road B, which was decided before round 300.
- **Gold margins on the `no_tribute` maps:**

  | Map | Side A | Side B |
  |---|---|---|
  | 02the-pack | 15,491 vs 1,618 | 20,267 vs 539 (127/183 clears vs 16/10) |
  | 01boss-battle | 26,392 vs 1,918 | 29,929 vs 4,749 |
  | 02guardians | 17,031 vs 723 | 14,124 vs 696 |
- **02gift-wrapping:** chip mode clears 2 groups and tributes 60 gems on both sides. Against the idle tb_merge_b, that is a gem win, not a gold one.
- **Sprint:**
  - Stalled/gold logic fired only on 00stampede (1-1), 01elk-arena (1-1) and 02guardians (2-0).
  - The other 0-2 / 2-0 pairs cancel: 01islands, 00corners and 01concentrated-wealth went 0-2; 01starvation, 02famine and 00lanes went 2-0. No gold logic was active in any of them. This is divergence from turn-1 fuel (`init_gold` runs in the 2× first turn).
  - **Net sprint effect: +1 game (02guardians).**

## Known limits / follow-ups (proposed new hypotheses)
- **Teleport into a guard-enclosed altar ring (02the-pack, the real ladder loss).**
  - The 3×3 ring around the altar is free. From 3 tiles outside the wolf ring, a TP crystal (range 3, ignores terrain) lands inside it, and sleeping wolves never attack.
  - Example: from (22,17) to (22,20), next to the altar at (22,22). So real tributes should be possible there (untested). Our bot cannot do it today, because camps aren't in `walk_block`, so the crossing logic never fires.
- **Make the respawn-rule fix universal.**
  - In tb_merge_b, standing on a dead camp of an alive group triggers the "never block a respawn" push-back. That froze all 5 champions on 01yellow-brick-road for about 1,700 rounds.
  - Here it is gated to gold play. Once the enemy tributes (vs imit_test, B side) our team freezes again: 0 clears in 2000 rounds.
- **Open-gate rush.** On `no_tribute` maps each champion carries 200 to 1,300 gems. If anyone kills a guard, the altar opens until it respawns. A rush to tribute would turn the gold lead into gems. This is Q3-adjacent.
- **Chip mode is slow** (2 clears in 2000 rounds on 02gift-wrapping). A team assault (Q3) would clear the wrapped groups much faster.
- **Move `init_gold` into the draft.** The draft has 250M fuel; the result could go through draft memory. That keeps champion turn 1 fuel-identical to tb_merge_b and cuts the sprint divergence noise.
