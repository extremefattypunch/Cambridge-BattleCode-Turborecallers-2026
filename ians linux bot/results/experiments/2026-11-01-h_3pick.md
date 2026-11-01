# Experiment: h_3pick, lock-memory fix (2026-11-01, cluster)

Batch-1 finish for STRATEGIES **Q18 / T15**. The implement and test stages ran on the dev PC (31 Oct). The raw games were lost and the analysis session never ran. This report covers the all-maps evaluation, the analysis session, and traced debug games.

## Hypothesis
- **What:** `pick_altar` skips altars *remembered* as enemy-locked, not only those locked in sight now (`LOCK_MEMORY_FIX = True`; trio mode stays off).
  - **The bug in tb_merge_b:** a locked altar just outside vision is picked because it is near. The carrier steps toward it, sees the lock, picks the far altar, steps back, loses sight of the lock, and repeats.
  - The result is a 2-cycle that freezes gem carriers for hundreds of rounds, until enemies kill them and take the bags.
  - Removing it should raise banked gems, lower gems lost and win games where the opponent locks altars.
- **Source:** ladder loss on 01broken_curve (357-1011 vs "Blame the Altar"), plus dev-PC traces on 01broken-curve B vs imit_test and 02the-pond A (see `bots/h_3pick/NOTES.md`).

## Setup
- **Candidate:** `bots/h_3pick`, forked from the champion `tb_merge_b`.
  - It differs only in `bot.py`: `pick_altar` calls `self.locked_altars()` and skips those altars.
  - The trio-mode code is present but gated off (`TRIO_MODE = False`).
  - It also adds a one-time `len(cambc.champions(Team.ALLY))` call at init.
  - `draft.py` and `main.py` are identical to tb_merge_b's.
- **Gate head-to-head (LOOP.md §4a):** `tools/onslurm.sh -c 24 -m 16G -t 00:20:00 -J h_3pick -- python3.12 tools/eval.py h_3pick tb_merge_b --maps all --jobs 16 --keep --tag b1-h_3pick-all`.
  - Slurm `test` partition, job 56768276, exit 0. 70 maps × both sides = 140 games.
  - Raw stats are in `matches/b1-h_3pick-all/`.
- **Diagnostics:** these are single local `cambc run` games, not evaluations.
  - Two new trace-only bots were made with `tools/newbot.py`: `bots/dbg_tbm_trace` (a tb_merge_b copy) and `bots/dbg_h3_trace` (an h_3pick copy). They are not for submission and can be deleted.
  - Each adds a `cambc.debug_block` print of the tribute decision for carriers with ≥15 gems: round, champion, position, gems, altar distance, chosen altar and remembered locks. `dbg_h3_trace` also prints the `do_tribute` branch and the dynamic blockers.
  - Output is in `matches/b1-h_3pick-trace/` (`*_b.tr` trace files and stats JSONs).
- **Frozen-carrier detector** (definition from NOTES.md; script in this session's scratchpad, re-implemented from that definition):
  - a champion holding **≥15 gems, unchanged, for ≥150 consecutive rounds while alive**;
  - counted in champion-rounds, for both teams of the same stats JSON.
  - It also counts genuine waiting, so it measures stalls in general, not only the lock bug.

## Results
```
SUMMARY h_3pick vs tb_merge_b: 75W-65L (54%)  avg gems 684 vs 636  avg deaths 12.4 vs 12.8  botFaults(A) 0
```
| Subset | Record | Note |
|---|---|---|
| all 70 maps | **75W-65L (53.6%)**, as A 40/70, as B 35/70 | Wilson 95% [45.3%, 61.6%]. **Gate (a) needs ≥82/140: FAIL** (botFaults 0) |
| 20 sprint maps | **22W-18L** (A 12/20, B 10/20) | **Reproduces the dev-PC sprint record exactly** (22W-18L) |
| 12 three-pick maps | **13W-11L** (A 8/12, B 5/12) | **Reproduces the dev-PC 3-pick record exactly** (13W-11L) |
| 58 other maps | 62W-54L | |

Per-map pattern (when the bots are identical, each map is exactly 1W-1L, decided by side):
- **Won both sides (19):** 00collision, 00corners, 00galaxy, 00gem-fields, 00great-wall, 00lanes, 00oasis, 00quadrants, 00rows, 00split, 01fracture, 01hooks, 01shortcut, 02arena, 02crossing, 02famine, 02geodes, 02harvest, 02treasure-box.
- **Lost both sides (14):** 00contest, 00eight, 00packs, 00reverse-spiral, 00ribs, 01big-world, 01boss-battle, 01concentrated-wealth, 01islands, 01starfish, 01starvation, 02cuts, 02uncharted-lands, adgato-gemcombat5.
- **Split (37), including 6 byte-identical to a mirror:** 02gift-wrapping, 02guardians, 02the-pack, adgato-gemcombat1/3/4.
- Net: 19 − 14 = +5 over the 70/140 a no-op change would score.

`analyze_match.py --summary --games` key rows (mean, our wins vs our losses):

| metric | wins | losses |
|---|---|---|
| gems us / them | 906 / 479 | 427 / 817 |
| first tribute us / them | r164 / r151 | r228 / r217 |
| champion deaths us / them | 6.7 / 15.9 | 16.4 / 6.7 |
| gems lost us / them | 58 / 124 | 110 / 63 |
| gold earned us / them | 6471 / 3839 | 3791 / 6101 |
| gem lead at r250 / r500 / r1000 | +20 / +54 / +132 | −28 / −65 / −148 |
| fuelExhausted us | 77.4 | 77.5 |

`match_metrics.py` (h_3pick):
- 140 games, 3856 tributes, mean tribute 24.8, small (<10) 409;
- deaths by champion 11.2/game, by camp 1.2/game;
- gems lost to champions 75.3/game, to camps 6.6/game;
- fuelExhausted 77.4/game, consumables 8.6/game, botFault 0.

Paired totals in the same 140 games (each bot plays every map from both sides):

| per game | h_3pick | tb_merge_b |
|---|---|---|
| gems banked | **683.5** | 635.8 (+7.5%) |
| gems lost on death | **81.9** | 95.6 (−14%) |
| lifetime gold | **5227** | 4889 (+7%) |
| champion deaths | 12.4 | 12.8 |
| fuelExhausted | 77.4 | **72.0** (h_3pick +7.5%) |

## Analysis session

### 1. Did the targeted mechanism change? Yes, and the traces confirm the cause
Frozen carriers, h_3pick vs tb_merge_b in the same games:

| Scope | h_3pick champion-rounds | tb_merge_b | Change | Games affected (h3 / tb) |
|---|---|---|---|---|
| all 140 games | 47,524 | 70,866 | **−33%** | 42 / 64 |
| excluding the 6 structural no-tribute maps¹ | 17,719 | 43,913 | **−60%** | 36 / 58 of 128 |
| 12 three-pick maps | 10,729 | 14,098 | −24% | 7 / 10 of 24 |
| three-pick maps excluding 02the-pack | 3,549 | 6,918 | **−49%** | 5 / 8 of 22 |

¹ 02guardians, 01boss-battle, 02the-pack, 02gift-wrapping, 00stampede, 01yellow-brick-road. Nobody can tribute on these, so carriers hold gems by necessity. 02guardians (10,608 each) and 02the-pack (7,180 each) are byte-identical in both bots.

**Traced proof.** `dbg_tbm_trace` plays tb_merge_b's side, with h_3pick as team A:
- **00quadrants:** the traced game matches the eval game until r286 and ends the same way (A wins at r1125, 1005-503 vs eval 1048-427).
  - From r381, all five tb_merge_b carriers (18-49 gems, 173 gems in total) step between x=34 and x=35 every turn until the game ends.
  - At x=34 `pick_altar` picks the remembered-locked altar (43,22) at distance 8; at x=35 it picks (22,43) or (22,1) at distance 16-19.
  - 1,363 of 3,048 carrier-turns (45%) chose a remembered-locked altar.
  - This is the exact 2-cycle in NOTES.md, here triggered by h_3pick's locks (h_3pick bought 9 locks).
- **02crossing:** the traced game is identical to the eval game (1018-460).
  - tb_merge_b chose a remembered-locked altar on **1,082 of 1,583 carrier-turns (68%)**, across all 5 champions, from r227.
- **00split:** the traced game diverged from the eval game (1030-971 instead of 1002-391) and shows only 7 lock picks (1%). The eval's tb freeze on 00split is **not confirmed** as the lock bug.
- **h_3pick never repeats it:** 0 remembered-locked picks in 2,790 traced carrier-turns on 01the-farm.

**Outcome association** (game buckets by frozen-round difference, structural maps excluded):

| Bucket | Record |
|---|---|
| tb_merge_b froze ≥300 rounds more than h_3pick | **21W-8L (72%)**, Wilson [54%, 85%] |
| neither froze | 32W-26L (55%) |
| similar (<300 difference) | 14W-21L (40%) |
| h_3pick froze ≥300 more | 3W-3L |
| structural 0-0 maps | 5W-7L |

The maps where the opponent's freeze is largest are mostly double wins:
- 00quadrants: tb 4,518 vs h3 0 frozen rounds;
- 02crossing: 1,851 vs 0;
- 00corners: 3,298 vs 679;
- 00split: 2,532 vs 508;
- 02famine: 1,267 vs 0;
- 00great-wall: 1,791 vs 848;
- 01shortcut: 4,013 vs 3,379.

Seven of the 19 double wins are of this kind; only 3 of the 14 double losses are (00reverse-spiral, 00packs, 00ribs).

### 2. Why is the head-to-head only 54%? Chaotic divergence swamps the signal
- With identical bots both games of a map are the same game, so `<map>__A` vs `<map>__B` gives the first round h_3pick acted differently.
  - **64 of 70 maps diverge.** The median divergence round is r198; 21 maps diverge by r100 and 8 by r30 (00reverse-spiral at r1, 00great-wall at r7, 01big-world at r12). That is long before any lock can be bought (first items come around r80-120).
- **Cause: tb_merge_b is fuel-adaptive.**
  - `build_static_fields` builds cached fields while `fuel_remaining() > 1,000,000`.
  - Target scoring stops below 800,000 (`FUEL_SCORE_FLOOR`).
  - Turn 1 waits unless 2,000,000 fuel is left.
  - So any change in per-turn fuel shifts decisions: h_3pick's extra `locked_altars()` API calls in `pick_altar`, the `champions(ALLY)` call at init, and a larger module.
  - fuelExhausted events differ between the two files from r1-r28 on 00reverse-spiral, 00anvil, 00packs and 00swirl. 00great-wall diverges at r7 with no exhaustion at all.
- **Live demonstration:** adding a single `debug_block` call (fuel-free inside, but the call itself costs fuel) to h_3pick flipped 01the-farm B from the eval's 820-832 **loss** to an 843-283 **win**. Later variants reproduced the loss exactly, and one gave 907.
- **Implication:** most of the 140-game result is a re-roll of fight snowballs (see §3). Only a minority of games are decided by the lock mechanism. The +5 net is in line with the bucket evidence, but it cannot be told apart from 50% (95% Wilson [45%, 62%]).

### 3. Why were the losses lost?
I read the narratives of all 65 losses (`analyze_match.py` per game). The causes, roughly by frequency:
- **Fight snowballs (most losses).** Champion deaths average 16.4 in losses vs 6.7 in wins. The gem lead is already −28 at r250 and the first tribute comes ~65 rounds later.
  - The losing side falls behind on kills early, earns ~40% less gold, and never catches up on items.
  - Blowouts:
    - 00eight A 4/45 K/D (gold 1,728 vs 11,642);
    - 00crater A 10/39 (the enemy Vendetta went 25/0);
    - 00swirl B 13/45;
    - 01elk-arena B 19/49;
    - 00fragment B 5/34;
    - 01starfish A 14/45;
    - 01starvation A/B 5/31 and 5/30;
    - 02fields A 12/35;
    - 00dunes A 2/26.
  - Killers are spread evenly over the enemy roster (Vendetta and Vesper most often). This is the same mirror behaviour on both sides, so the direction is set by the early divergence, not by the lock fix.
- **Big carrier deaths:**
  - 00the-line B: Marcella lost 84 gems at r411 and Vesper 81 at r440, then 0 tributes all game (0-881);
  - 00vault B: carriers with 114-171 gems died at r229, r477 and r515 (tributes average 85 on that map);
  - 00gemfight A: Vendetta lost 82 at r426;
  - adgato-gemcombat4 A: 8 deaths carrying 28-56 gems each in r238-r630.
- **Spawn pin (new):**
  - 00packs A (4-578): our Vesper Vale took **205,491** champion damage across the game but died only 4 times. The enemy Vesper dealt 204,335. The team made 1 tribute (4 gems) in 2,000 rounds.
  - 00the-line B (0-881): our Heart of Ruin took 142,219.
  - These are the only champion-games in all 140 with ≥60k damage taken by one champion, and both are heavy h_3pick losses. The logic is identical in tb_merge_b, so this is a shared weakness.
- **Gold tiebreak on 0-0 maps:** 01boss-battle was lost on both sides, 0-0, on lifetime gold (3,642 vs 4,668 and 4,298 vs 5,083). It is chaotic (diverges at r66, ~600 fuelExhausted per game) and is h_goldtie's (Q2) territory. The other 0-0 maps split 1-1.
- **Narrow end-game races:** 00ambush B 783-974, 00expanse B 971-1014, 01islands A 860-920, 01the-farm B 820-832, 02cuts B 938-1024, 02uncharted-lands 922-1005 / 942-1007, 00pilgrimage B 333-348. Kills are close and tribute counts decide these.
- **Residual h_3pick freezes (not the lock bug):**
  - On 01the-farm B (traced; identical to the eval game until r1391), h_3pick carriers with 15-66 gems spend **1,082 turns in 2-tile oscillations**:
    - r365-403 at (19,17)↔(18,18) with 55 gems;
    - r440-493 at (18,14)↔(19,13) with 22;
    - r1228-1308 at (19,14)↔(20,15) with 66.
  - In each, the preferred altar is free and in the same walk component, and `go` is true every turn.
  - `do_tribute` → `step_toward` alternates direction because `blocked_now` counts **only visible** camp tiles as walls.
    - From (19,17), the camps at (24,19)/(25,19) guarding the altar entrance are visible, so the path goes round via (18,18).
    - From (18,18) they are out of sight, so the short path looks open and the carrier steps back.
  - This is the **same 2-cycle shape with camps instead of locks**. tb_merge_b has identical code. The game was lost 820-832.
- **Fuel:** h_3pick has +7.5% fuelExhausted (77.4 vs 72.0 per game). The gap is broad but modest; the largest are 00lanes +227, 00split +125 and 00quadrants +118 over both sides. Part of it is activity (unfrozen carriers keep acting), and part is `locked_altars()` running twice per carrier-turn (pick_altar and do_tribute, ~3k fuel per API call per altar). It does not separate wins from losses (77.4 vs 77.5).

### 4. Surprising wins
- **00quadrants (1048-427 and 1019-539, games over by r1125 and r965):** a lock-mechanism win. The traced game shows every tb_merge_b carrier stuck in the 2-cycle with 173 gems from r381.
- **02crossing (1018-460, 1001-761):** a lock-mechanism win (68% of tb carrier-turns picked a remembered lock).
- **02arena (954-283 and 821-262, both sides on a 3-pick map):** **not** lock-related (0 frozen rounds for either bot). It was a kill snowball, 33-6 and 35-11 (Vendetta 17/1 and 21/4, Vesper Strength ×22-23). It shows how small 3-pick maps amplify early fight outcomes.

## Verdict
**kept, as a component of the Q24 combo; not promotable on its own.**
- **The mechanism is confirmed:**
  - the lock 2-cycle is real in tb_merge_b, traced on 00quadrants and 02crossing, and absent in h_3pick;
  - frozen carriers fall 33% overall and 60% off the structural maps;
  - in the same games h_3pick banks 7.5% more gems and loses 14% fewer;
  - games where the opponent froze ≥300 rounds more went 21W-8L.
- **The head-to-head fails gate (a):** 75/140 < 82, Wilson lower bound 45%.
  - Most games are decided by chaotic fight snowballs that any fuel change re-rolls.
  - It also costs +7.5% fuelExhausted, so (c) would need checking.
- Gates (b) to (d) were not run, and no promotion or upload is warranted.

## New hypotheses generated
The orchestrator assigns Q numbers when adding these to STRATEGIES.md.
1. **(new) Camp-gate vision-flicker 2-cycle (01the-farm trace).**
   - **What:** `blocked_now` should also treat camp tiles *remembered* as occupied (camps are static) as walls, or add path hysteresis. If a carrier alternates A,B,A,B with unchanged gems for 6 turns, it commits to its current route for ~10 turns.
   - **Why:** the same freeze shape as the lock bug, still present in both bots: 1,082 oscillating carrier-turns in one game lost 820-832, and residual freezes on 01shortcut, 00road-of-riches and 01fracture.
2. **(new) Lock-and-hunt.**
   - **What:** after we lock an altar, send a hunter to the lock's vision edge (~8 tiles out, toward the enemy side), where enemy carriers with full bags oscillate.
   - **Why:** our locks froze all five tb_merge_b carriers with 173 gems from r381 to r1125 on 00quadrants. The real ladder team "Blame the Altar" killed our frozen carriers on 01broken_curve (110 gems in 13 rounds). Ladder bots with the same memory gap are free gems.
3. **(new) Spawn-pin escape.**
   - **What:** detect a champion repeatedly healing at spawn while an enemy keeps hitting it (≥X champion damage taken in N rounds with no kill). Then sortie as a group, or stop re-entering the enemy's range one at a time.
   - **Why:** 00packs A (Vesper took 205k damage, 1 tribute all game, 4-578) and 00the-line B (HoR took 142k, 0-881) are our two worst non-structural losses.
4. **(new) Cheaper lock memory.**
   - **What:** refresh `locked_altars()` once per turn (cache it on `self`) instead of in both `pick_altar` and `do_tribute`.
   - **Why:** it keeps the fix but removes per-call API overhead behind part of the +7.5% fuelExhausted. Needed if the fix ships alone or in Q24, since gate (c) requires fuelExhausted not worse than the champion's.
5. **(new, methodology) Null-change calibration of the gate.**
   - **What:** run tb_merge_b plus one dead API call per turn vs tb_merge_b on all maps, once.
   - **Why:** 64/70 maps diverge from tiny fuel changes, so a no-op variant shows the real spread of the 140-game head-to-head. That tells us whether 82/140 is reachable by noise or too strict for single-mechanism fixes, which should then be judged on paired mechanism metrics plus the gauntlet.
6. **Supports Q2 / Q24:** 01boss-battle was lost on both sides 0-0 on gold. The h_goldtie gold play belongs in the Q24 combo next to this fix.
