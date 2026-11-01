# Electric Fog Walkers (1511): ladder set b8923d32, 1 Nov 2026, our v4, won 4-1

- **Opponent:** Electric Fog Walkers, rating 1511 (ours after the set: 1526).
- **Our version:** website v4 = `bots/c2_respawn` (live from 04:42 UTC, `results/ladder-versions.json`). The set ran at 05:42 UTC. We were team A in all five games.
- **Record:** **4-1.**

  | # | Map | Size, picks | Result | Tributed gems (us-them) | End |
  |---|---|---|---|---|---|
  | 1 | 01elk_arena | 50x50, 5 | W | 1008-72 | r1352, 1,000 gems |
  | 2 | 02harvest | 100x100, 5 | **L** | 460-1005 | r1421, 1,000 gems |
  | 3 | 02stalactites | 30x30, 4 | W | 1045-383 | r437, 1,000 gems |
  | 4 | 01starfish | 50x50, 5 | W | 987-618 | r2000, gem tiebreak |
  | 5 | 01the_farm | 50x40, 3 | W | 870-25 | r2000, gem tiebreak |
- **Link:** https://2026a.battlecode.co.uk/game/match-groups/b8923d32-049f-41cf-af18-cc528771a122
- **Data:** the five `results/ladder-games.jsonl` rows; `matches/ladder/summary/<id>__A.json`; replay zips `matches/ladder/replays/<id>.repl26a`; `python3.12 tools/scout.py --group b8923d32`; `tools/freeze_metric.py`, `tools/lowhp_freeze.py`.
  - Our `team-a.stdout` is empty in all five games. Ladder stdout is captured (v4 printed `submit failed` in set 5eca4952), so **no `bot error` happened here**: every odd behaviour below is the bot's own decision logic.
- **Method: what is measured and what is inferred.**
  - **HP** is reconstructed exactly from the timelines.
    - Max HP comes from Health shards plus +1 HP growth per Bruiser Str/Foc emblem.
    - Then subtract monster and champion damage taken and add `healingReceived`, which includes spawn healing. Check: Vendetta's +520 at r475 on harvest = 1,100 - 580.
    - It is not valid for Heart of Ruin and Varg, whose self-shields count as damage taken.
  - **Positions** are not in the stats.
    - Our bot places its ward only when the old one is more than 6 tiles away (`try_ward`). So a gap in our ward events bounds the champion to within Chebyshev 6 of its last ward.
    - Captures, kills and tributes give exact tiles.
  - **Per-turn fuel** comes from `team-a.fuel` in the replay zip.
    - Layout: 13 header bytes, 8 u64 budget constants, one u64 per draft pick, then one u64 per champion-turn in draft order. Index = 8 + picks + picks x (round - 1) + slot; checked against `fuelExhausted` at r2.
    - Over hundreds of turns, fuel that alternates with period 2 marks a two-state decision cycle. A walk shows a smooth trend instead.
  - Helper scripts are in the session scratchpad (`efw_b8923d32/`), not in the repo. Anything marked *inferred* or *speculation* is not directly observed.

## Game summary
Each team drafts 3-5 champions. Champions kill camps, capture them for gems and gold, and tribute gems at altars. The first team to 1,000 tributed gems wins; otherwise gems, then lifetime gold, decide at r2000. Healing happens only on your own spawn (no regeneration).

## 1. Opponent profile
### Draft and each champion's role
**Fixed list, truncated to the pick count:** Stellar, Ren, Marcella, Ryth, Varg. The 3-pick draft (the farm) is Stellar, Ren, Marcella; the 4-pick draft (stalactites) adds Ryth.
- We drafted Vesper, Vendetta, Marcella, HoR, Ryth (`draft.py` PRIORITY).
- Mirror picks: Marcella, plus Ryth on 5-pick maps.

| Champion | Role in these games | Evidence |
|---|---|---|
| Stellar | Ranged burst caster: 2xF single target and 1.4xF AoE, both range 4. Stacks Power-Focus. Their main killer, mostly late | 13 of their 36 champion kills (starfish 8, 6 of them after r1000). Estimated Focus on starfish: 130 at r500, 308 at r1000, 682 at r1500, 962 at the end |
| Ren | Melee farmer with Jungle-Health first, Power-Focus stunner late | Top collector on harvest (257 gems); 6 kills on starfish |
| Marcella | Cluster farmer: Prospector first, Monster-Focus late. Solo big-cluster captures | Stalactites: g8 alone for 210 (168 + 25%); 9 kills; Focus 984 by the end of starfish |
| Ryth | Solo farmer: Jungle-Health, then Power-Strength | 206 gems on harvest; 5 kills |
| Varg | Splash wolf farmer: Treasure first, then Power-Strength. Self-shield | Most clears: elk 32, harvest 18; 1 kill |

### Items: build order and timing
The order is the same in every game. Only the timing moves with income.

| Champion | 1st emblem | 2nd | 3rd | 4th | Then |
|---|---|---|---|---|---|
| Stellar | Prospector F (done r50-401; 4-5 shards on the first visit, r37-79) | Jungle F | Bruiser F | Durability H | Power F x n |
| Ren | Jungle H (done r142-499; r1027 on the farm) | Bruiser H | Durability H | | Power F x n |
| Marcella | Prospector F (done r154-447) | Jungle F | Bruiser F | Durability H | Monster F x n |
| Ryth | Jungle H (done r264-410) | Bruiser H | Durability H | | Power S x n |
| Varg | Treasure S (done r173-524) | Jungle S | Bruiser S | Durability H | Power S x n |

- **Jungle:** on the three 5-pick maps every champion completed Jungle (-30% damage from camps) between r160 and r750.
- **No consumables:** they never bought an altar lock or a TP crystal.
- **Ours:** Bruiser shards only, plus an altar lock on most shop visits. `bruiser_item()` never returns None for our five champions (all are in `BRUISER_PLAN`), so `shop()`'s Jungle, Monster and Power fallbacks are unreachable.

### Farming: which camps, in what order, with how many, and tempo
**Strictly solo.** Captures made by a single champion:

| | elk | harvest | stalactites | starfish | the farm |
|---|---|---|---|---|---|
| Them | 95/95 | 77/77 | 25/26 | 130/132 | 10/11 |
| Us | 83/121 | 36/45 | 3/7 | 40/46 | 28/33 |

**Own-side circuit (harvest).**
- **Captures by side:** theirs own/mid/ours 59/17/1, for 857/194/12 gems. Ours own/mid/theirs 28/5/12, for 321/55/69 gems; 9 of our 12 on their side were the 0-gem gold cluster g11 next to their spawn.
- **Circuit:** g5 (94,68) Wolf+GemCl x17, g13 (69,70) Elk x13, g15 (64,60) x10, g17 (61,41) x9, g3 (94,26) x9, g7 (90,42) x8, and the mid group g16 (38,58) x8.
- **Mirror groups, their captures vs ours:**
  - g5 vs g4 (the safe wolf+gem group nearest each spawn): **17 vs 4**, and our first was at r772;
  - g13 vs g12: 13 vs 3;
  - g3 vs g2: 9 vs 0;
  - g7 vs g6: 8 vs 0;
  - g15 vs g14: 10 vs 8;
  - gold clusters g11 vs g10: 1 vs 13.

**Tempo rises as Power and Monster stacks land.** Clears per 100 rounds by phase (<300 / 300-1000 / >1000):

| Map | Them | Us |
|---|---|---|
| harvest | 4.0 / 5.1 / 7.1 | 3.0 / 3.3 / 3.1 |
| starfish | 3.0 / 7.9 / 8.3 | 1.0 / 1.7 / 1.9 |
| stalactites | 5.7 / 6.5 (game ended r437) | 2.0 / 0.7 |
| elk | 10.0 / 9.1 / 5.1 | 11.0 / 6.7 / 8.2 |

**Camp damage taken per 1,000 dealt:** harvest 219 vs our 521; starfish 211 vs our 572.

**Prospector on cluster fields.** On stalactites, g7 (77 gems) gave Stellar 96 and g8 (168) gave their solo Marcella 210.

### Tributes
**Bags of 30-55, banked at the nearest altar.** On harvest they used their home altar (51,80) 12 times for 452 gems and the mid altar (61,38) 12 times for 439. On starfish they held everything until r556, carrying 52 gems at r500.

| Map | Them: count x mean, first | Us: count x mean, first |
|---|---|---|
| elk | 1 x 72, r65 | 40 x 25.2, r252 |
| harvest | 30 x 33.5, r144 | 23 x 20, r122 |
| stalactites | 7 x 54.7, r91 | 13 x 80.4, r69 |
| starfish | 19 x 32.5, r556 | 32 x 30.8, r180 |
| the farm | 1 x 25, r94; then 136 gems frozen | 28 x 31.1, r119 |

### Fights
**Opportunistic and never grouped.**
- **No deliberate carrier hunting, spawn camping or altar locks seen.**
- **Where they killed us on harvest:** next to their own farming groups. 3 of our 4 deaths were in their half:
  - Ryth, r318 at (60,62), by Varg;
  - Vesper, r473 at (38,52), by Marcella;
  - Marcella, r924 at (52,58), carrying 11, by Marcella;
  - Ryth, r1117 at (53,60), by Stellar.
- **Carrier kills on us were incidental** (starfish):
  - our Marcella with 51 at (21,47), r1018, by Stellar (Varg was farming g4 there);
  - HoR with 55 at (20,20), r1063, by Ryth, by the altars.
- **Late Focus burst.**
  - Starfish after r1000: the largest damage our champions took in one round was 1,772-1,925, against max HP of about 2,000-3,000. They won the late kills 17-10.
  - Harvest r1050-1200: our Marcella took 3,005 champion damage in four one-round chunks (650, 1,044, 752, 560) and dealt 0.
- **They lose grouped fights.**
  - Elk: K/D 6-25. 16 of our 25 kills were within 6 tiles of their spawn, as their champions came out one by one.
  - Stalactites: both of their 200+-gem carriers died at the altar.
- **Gems lost on death:** theirs 854 (0/32/419/268/135 by game), ours 169 (0/11/4/154/0).

### Map control
- **Wards:** 60-115 per champion, similar to ours. Stalactites is the exception: 16 in total, all at their spawn.
- **Locks and crystals:** none in any game. We bought 4-14 locks per game. Whether any of our locks blocked one of their tributes is not observable.

### Adaptation across the 5 maps
**None.** Same draft order, same build order and the same solo own-side circuit on every map. Their own failures:
- **The farm: carrier freeze.**
  - **Where:** all three froze at (23-26,15-17) from about r270 (Ren) or r450 (Stellar, Marcella) to the end. That is the south mouth of the gate in the wall y=19 (x 16-33). The never-cleared g16 (Wolfx2+GoldClx2, tiles (23-26,19)) fills that gate.
  - **Ward pairs alternate:** (25,16)/(25,17) and (24,16)/(23,16), which looks like an oscillation.
  - **Carried:** Ren 44, Marcella 40, Stellar 52. They tributed once all game (Ren, 25 at r94).
  - This is the same camp-gate shape as our own W1 bug.
- **Elk:** Stellar alternated wards (26,40)/(29,40) every 12 rounds from r316 to r712 (393 quiet rounds), also an oscillation.
- **Stalactites:** both big bags (205 and 210) were carried into our champions at the central altars.

## 2. Per game
Gem race = tributed gems, us-them.

| Map | Result | r100 | r250 | r500 | r1000 | End |
|---|---|---|---|---|---|---|
| 01elk_arena | **W** | 0-72 | 0-72 | 216-72 | 648-72 | 1008-72, r1352 |
| 02harvest | **L** | 0-0 | 50-78 | 178-145 | 380-596 | 460-1005, r1421 |
| 02stalactites | **W** | 161-12 | 399-188 | (ended r437) | | 1045-383 |
| 01starfish | **W** | 0-0 | 17-0 | 147-0 | 283-72 | 987-618, r2000 |
| 01the_farm | **W** | 0-25 | 21-25 | 54-25 | 231-25 | 870-25, r2000 |

### 01elk_arena: W 1008-72
**Map.** One gem source: g0 (24,24), Elkx2 + GemClx6, 72 gems, strength 120, 5,520 HP. Altars (22,22) on our side and (27,27) on theirs. The other 28 groups are gold-cluster pairs.

**Their opening.** Varg cleared g0 at r38, Stellar captured it at r44 for 72 and banked at (27,27) at r65. Marcella trades at r56/r66: ours killed theirs at (27,21), and Stellar killed ours at (22,21).

**Ours.** `choose_target` rejects g0 for every champion at base HP.
- For a 1,000-HP champion, budget = maxhp - 120x5 - 80 = 320, so cycles > 4.
- 24 of our 25 captures by r250 were 0-gem gold clusters.
- That bought the gold lead (1,745-1,232 at r250) and items: emblems by r500, 19 vs 12.

**Turn (r225-253).**
- r225: their Marcella cleared g0.
- r231-241: Vendetta killed Stellar and Marcella at (27,23); Ryth killed Ren and Ryth at (31,23-24).
- r248: Vesper, Marcella and HoR captured *their* clear at (24,23), banked at r252-253.

**Then.** We captured g0 14 times (r248-1344, every 75-100 rounds); they never captured it again.
- Kills 25-6. Vesper went 11/0, with 8 of the kills at x 27-33, next to their spawn.
- Their Stellar spent r316-712 oscillating.

**Root.**
- We won through grouped fights at the centre, then by holding the only gem group.
- The first 248 rounds went 0-72 because no champion will take g0 alone.

### 02harvest: L 460-1005 (the loss)
**Map.** 180-degree symmetric. Spawns: ours (10-12,12-14), theirs (87-89,85-87).
- **Gem groups:**
  - elk g12/g13 (15 gems), elk g14/g15 (29);
  - wolf+gem g4/g5, g6/g7, g16/g17 (11);
  - golem groups g8/g9 (57) and g18/g19 (43);
  - centre g20 (114, two golems).
- **Gold clusters (0 gems, 20 gold):** g10 (26,8) by our spawn, g11 (73,91) by theirs.
- **Altars:** (48,19) ours, (51,80) theirs, and mid (38,61), (61,38), (12,92), (87,7).

**Race.**
- Gap change by window, us-them: r0-250 -28; r250-500 +61; r500-750 -98; r750-1000 -151; r1000-1421 -292. They led for good from r630.
- **Camp gems collected after r1000: 80 to 383.**
- Totals, us vs them: gems collected 477 vs 1,074; gold 2,867 vs 7,046; clears 45 vs 78; monster damage 52k vs 161k.
- Kills 1-4, so fights did not decide it.

**Where our five champions' rounds went (decisive):**
- **Vendetta (79 gems): HP-band trap, 1,029 rounds at 45-60% HP.**
  - r29-38: Vendetta, Marcella and Ryth cleared elk g12; Vendetta took 7x60 and dropped to 580/1000.
  - r64-470: it captured the gold cluster g10 (26,8) eight times, every 57 rounds, for 20 gold and 0 gems each.
  - Between captures its ward trail ran (22,19) → (32,29) → (28,24) → (20,14) and back to g10 as it respawned.
  - The `rich` recall at 160 gold freed it at r470.
  - Repeats: r589-812 at 520/1100 (g10 x3), and r1034-1401 at 894/1800 (**g11 (73,91), beside their spawn, x5**).
  - In total 16 of the team's 22 zero-gem captures (13 at g10, 9 at g11) were Vendetta's.
- **Vesper (90 gems, 58 of them from camps): no monster damage at all until r593.**
  - r0-340: three walks into their half towards (50-61,44-59), around their g15/g17. Skirmishes at r114-146 and r194-242 ended in low-HP recalls (r150, r244).
  - r337: it killed Stellar, who carried 32, at (66,54), and banked at r389.
  - r473: it died at (38,52) to their Marcella.
  - r534-966: it farmed 58 gems.
  - r790-845: it hovered near (25,23) holding 11 gems.
  - **r966-1421: frozen.**
    - Last ward (21,19) at r966. Then no ward, damage, gold or gem change for 455 rounds, at full HP (1,700), holding 6 gems that it never banked.
    - Its fuel alternates 1,837k / 1,777k every turn, in exact anti-phase with HoR's for r975-1045 (70 of 70 turns).
    - Mechanism: §3 gap F (*inferred*: claim 2-cycle).
- **Ryth (74 gems):** 0 gems after r1000.
  - Died at r318 at (60,62) in their half.
  - In the HP band r958-1114, it took g11 twice (0 gems), then died at r1117 at (53,60).
- **Marcella (105 gems):**
  - Died at r924 at (52,58) carrying 11.
  - r1060-1188: two walks towards (46,44) and (56,54), each ended by a recall after taking 3,005 champion damage in total and dealing 0.
- **HoR (129 gems):** solid on g14 (5 captures), but it also went to g7 (90,41) at r240, deep in their side, and to g11 twice (r526, r585; 0 gems).

**Root: farming throughput.**
- One champion was trapped on 0-gem targets for about 1,000 rounds, and one was frozen for the last 455.
- The others were repeatedly drawn into their half, where 3 of our 4 deaths happened.
- Meanwhile the wolf and elk groups on our own half idled (g4 4 captures, g2/g6 0).

### 02stalactites: W 1045-383 (r437)
**Map.** 30x30. Altars (14,14) and (15,14) in the centre.
- Gem-cluster fields: g6 (8,23) 77, g8 (14,21) 168, g7 (21,23) 77, g0/g1 28, g13/g14 21.
- Wolf+gold flanks: 4 gems and 120 gold each.

**Timeline.**
- **r56-58:** we took g6 (Vesper, 77) and g8 (Vendetta + HoR, 168). 161-12 at r100.
- **r150-160:** they killed our Marcella at (17,8) (Ryth) and Vesper at (12,18) (Stellar).
- **r190-197:** they took g7 (Stellar, 96) and g8 (Stellar + Ryth, 189); Stellar carried 205.
- **r207:** HoR killed Stellar at (14,15), next to the altar, and took the 205.
  - HoR then *recalled* (ward at spawn, r222) while their Ryth (84) and Marcella (64) banked at (15,14) at r224 and r231.
  - HoR walked back and banked the 205 at r256.
- **r335-362:** their Marcella captured g8 alone for 210, killed our Vesper at (12,12) at r356, and was killed by HoR at (13,13) at r362.
- **r362-438:** HoR backed off towards (9,6) (ward, r392) while Ren and Ryth banked 77 each at (14,14) at r398. HoR banked the 210 at r438: 1045, game over.

**Root.**
- 415 of our 1,045 gems came from two carrier kills at the altar.
  - `focus_bias` puts channelling enemies in tier 0, and HoR's landing-dash stun does the rest.
- They out-farmed us: 26 clears vs 7, gold 2,708 vs 530. Vesper and Vendetta bought nothing.
- We held two big bags for 49 and 76 rounds next to a usable altar (W8).

### 01starfish: W 987-618 (r2000)
**Map.**
- Both altars, (23,17) and (26,17), sit inside g15 (24,17): Elkx6 + GemClx4 + GoldClx4, 118 gems.
- The centre is a column of single wolves g7-g14 (4 gems each).
- g2/g3 (Elkx2 + GemClx3, 51) at (20,38)/(29,38); g4 (Wolfx2 + GemClx4, 36) at (24,46).

**Race.** 17-0 at r250, 147-0 at r500, 283-72 at r1000, 441-315 at r1500. They held their gems until r556.

**Their play.** They farmed the wolf column: 147 clears vs our 34, monster damage 282k vs 112k, gold 10,448 vs 9,362.

**Our gems.**
- **g15, three late captures:**
  - r1394: Vesper + Ryth, 59 each;
  - r1628: Vendetta 118, banked as 126 at r1727;
  - r1882: Vesper 118, banked at r1915.

  That is 354 gems, 36% of our total. They never took g15.
- **Carrier kills, Vesper 15/2:** Marcella with 32 at r567, Stellar with 20 at r893, and Marcella with 68 at r1550 (a triple with Stellar and Ren at r1545-1556).

**Late fights went their way as their Focus stacked.**
- After r1000: kills 17-10, our deaths 19 vs 13.
- Single-round hits on us reached 1,772-1,925, and r1000-1500 went -85.
- Camp deaths 7 vs 8, to the elks in the altar ring.

**Root.**
- We won on the big objective plus Vesper's carrier kills, while losing the farming race 4.3 to 1 on clears.
- We needed until r1394 to take g15 (W7).

### 01the_farm: W 870-25 (r2000)
**Map.**
- Our spawn is (1-4,1-3), theirs (45-48,1-3).
- Altars: (2,37), (17,35), (23,22), (26,22), (32,35), (47,37).
- The central altars (23,22)/(26,22) lie north of the wall y=19 (x 16-33). Its gate (23-26,19) is filled by g16, which nobody cleared.
- The wall can be walked around at x ≤ 15 or x ≥ 34.

**Them.** 11 captures and one tribute; then all three froze at the gate mouth with 136 gems (§1). We killed them only late:
- Vesper killed Ren (44 gems) at r1603;
- Vendetta killed Ren (51) at r1874 and Marcella (40) at r1882.

**Us.** 33 captures and 870 gems; we never reached 1,000.
- **1,998 of our 6,000 champion-rounds (33%) were frozen**, and 1,993 of those were spent **carrying gems (average 30)**.
- Our frozen stretches:

  | Champion | Frozen rounds (gems carried) |
  |---|---|
  | Vesper | r177-465 (34); r1748-1865 (34) |
  | Vendetta | r233-463 (15, at 50% HP); r1604-1802 (33) |
  | Marcella | r286-500 (33); r589-870 (29-33); r1024-1181 (29); r1254-1652 (31); r1894-2000 (37) |
- Wards bound all of these to the chamber south of the gate (x about 11-24, y about 4-16).
- Most stretches show period-2 fuel: Marcella r690-870, r1024-1181, r1254-1652; Vendetta r1604-1802; Vesper r1748-1865. The early r233-463 stretch froze three carriers at once with irregular or period-4 traces.

**Mechanism (*inferred*).** It matches the traced 01the-farm B game in `results/simulated-matches/2026-11-01_0126_h_3pick/notes.md`.
- `pick_altar` reads static fields in which camp tiles are walkable. From (19,14), the altar (23,22) is 7 steps away through g16.
- `blocked_now`, used by `step_toward`, blocks only *visible* camp tiles. With g16 seen, the real walk is 14 steps, west around the wall; the next altar, (17,35), is 20.
- Each step that hides or reveals g16 behind the bush row y=15 flips the route, so the carrier dances.
- *Speculation:* the enemy trio parked at the gate mouth (inside `handle_enemies`' 6-tile range, 1 vs 3) may add a second flip.

**Never touched:** the monoliths g24/g25 (207 gems each), g9 (74) and g22/g23 (44). We took the elk pair g7 (37) next to our spawn only from r1565.

**Root.** An opponent bug won the game. Our own carrier freezes cost a third of it; against a working bot on this map that is the difference between a win and a coin flip.

## 3. Their strategy vs ours
### Where theirs was superior
| Gap | Size | Rule or threshold responsible (live bot `bots/c2_respawn/src/bot.py`) |
|---|---|---|
| **A. Farming continuity: no HP-band dead time** | 45-60% HP band, champion-rounds per game (excluding shield champions): ours 286 / 1,399 / 46 / 586 / 1,115 vs theirs 53 / 233 / 170 / 345 / 478. Harvest: Vendetta alone 1,029 rounds, with 16 of our 22 zero-gem captures | In `choose_target`, `if not (self.target is G) and hp < maxhp * 0.6: continue` sits inside `if s > 0`, so between 45% and 60% HP only 0-strength groups (gold and gem clusters) and the current target stay eligible. `play_turn_main` heals only at `low = hp < maxhp * 0.45` or when `rich` (gold ≥ 150 with < 8 gems carried, or gold ≥ 400). The `G is None` recall (gold ≥ 60 or hp < 0.7) never fires while any gold cluster on the map is eligible |
| **B. No 0-gem detours** | Harvest: 9 captures of g11 next to their spawn (about 80 steps from ours) for 20 gold each; their 0-gem captures numbered 1 | `Group.__init__`: `value = gems + 0.25 * gold`, so a lone gold cluster is worth 5 at any distance. `choose_target`'s status-2 rule (`G.ready > rnd + d` → skip, else `wait`) makes g10 ineligible right after a capture. The champion walks towards g11 until g10 is eligible again, then turns back: the g10/g11 oscillation |
| **C. Own-side circuit vs claim-pulled expeditions** | Harvest: captures by side 59/17/1 vs our 28/5/12; mirror g5 vs g4 17-4; Vesper 0 monster damage in r0-593; 3 of 4 deaths in their half | `choose_target`: claimants add `tdps = dps + c * 55.0`, and a non-solo chooser gets `score *= 1.2`, both regardless of where the claimant is. Model estimate for Vesper (dps 50.6, *inferred*): a claimed elk group about 55 steps away (g15) scores about 0.8 with one or two claimants, against about 0.4 for the solo wolf g4 17 steps from spawn. Nothing prefers uncontested or home groups. `DEATH_PENALTY` only applies after a death at that group |
| **D. Camp-damage efficiency** | Damage taken per 1k dealt: 219 vs 521 (harvest), 211 vs 572 (starfish). Clears 78-45 and 147-34 | `shop()` → `bruiser_item()`: `BRUISER_PLAN` covers all five drafted champions, so Jungle, Monster and Power are never bought (`JUNGLE_FIRST = False`). Part of the gap is their ranged/AoE kits and more champion-rounds spent farming |
| **E. Opening on the dominant group** | Elk: 0-72 until r248 | `choose_target` chip model: `budget = maxhp - s*(rng+1) - 80`; `budget <= 0` or `cycles > 4` → `continue`. That rejects g0 for every 1,000-HP champion. The team path (c3/c4) is not live |
| **F. No frozen time (their 4,558 frozen rounds were their own farm/elk bugs)** | Ours frozen: harvest 806 (Vesper 455 at the end), the farm 1,998 (all carrying). Theirs on harvest, stalactites and starfish: 0 | (1) **Camp-gate vision flicker:** static `sfields` in `pick_altar` vs `blocked_now` (visible camps only) in `step_toward`. (2) **Claim 2-cycle** (harvest, *inferred* from the Vesper-HoR anti-phase): a solo-capable chooser scores a claimed group x0.3 and a non-solo chooser x1.2, via `read_claims`/`write_claim`; HoR acts after Vesper within the round. (3) `note_progress` (the stuck guard) counts only farming turns with no move, so alternating moves and the tribute branch are never caught |
| **G. Late Focus burst** | Starfish after r1000: kills 17-10; single-round hits of 1.8-1.9k. Harvest: Marcella took 3,005 and dealt 0 (r1050-1200) | `enemy_dps(e) = strength + 0.15 * focus` (Stellar at Focus 962: about 190 per round, while one 2xF cast is about 1,900). `handle_enemies` sums `threat += e.strength()` (no Focus), so `their_ttk` is overestimated and we engage or stay in spell range |

### Where ours was superior
- **Grouped fighting** (`group_balance`, `GROUP_ADV` 1.4): elk 25-6 with Vesper 11/0; starfish Vesper 15/2; elk fights with 2+ deaths won 7-0.
- **Punishing carriers and channellers** (`focus_bias` tier 0 for tributing enemies; HoR's dash stun via `stun_channel`): stalactites 415 gems from two kills; starfish 32/20/68-gem carriers; the farm 135 gems. Gems lost on death: their 854 vs our 169.
- **Small, frequent banking** (`bank_now` / `bank_detour`: BANK_ANY 30, NEAR 15, CLOSE 5): our mean tribute was 20-31 on the 5-pick maps, so a death rarely cost a bag. Only starfish lost 154.
- **Taking cleared or abandoned objectives:** 13 capture steals on elk and 13 on starfish (status-1 groups score x1.5). g0 was held for 1,100 rounds; g15 was taken three times late.
- **Early gold on gold-cluster maps:** elk 1,745 vs 1,232 at r250. The Bruiser items it bought won the centre fights. The gold value itself is fine; gaps A and B are about *when* and *how far*.

## 4. Our weaknesses exposed
| # | Weakness | Evidence | Games | Impact |
|---|---|---|---|---|
| W1 | **Carrier and target 2-cycle freezes** (camp-gate vision flicker; claim 2-cycle) | **The farm:** 1,993 carrier-frozen champion-rounds (33% of our time, average 30 gems), period-2 fuel, wards bounded to the gate chamber. **Harvest:** Vesper frozen r966-1421 (6 gems, full HP; anti-phase with HoR for 70/70 turns) and r790-845 (11 gems). Same mechanism class as the traced 01the-farm B game and h_bigmap's 5,467 two-target cycle rounds on big maps (q24) | 2 | major (decisive in combination on harvest; a third of the farm) |
| W2 | **45-60% HP band trap** | Harvest: Vendetta 1,029 band rounds and 16 zero-gem captures; Ryth 157. The farm: Vendetta 552, Marcella 383. **Local census, recomputed** (`matches/gate-c2-all`, 140 games, shield champions excluded): 624 band champion-rounds per game for c2, 123/140 games ≥ 200, **02harvest A 1,700** (B 1,231), 27% of c2's captures 0-gem | 2 | decisive (harvest) |
| W3 | **Claim-pulled expeditions into the enemy farming zone; home groups idle** | Harvest: captures by side 28/5/12 vs their 59/17/1; g4 first captured r772 (theirs: g5 x17); Vesper 0 monster damage r0-593; 3 of 4 deaths in their half; Marcella 3,005 taken / 0 dealt r1050-1200 | 1 | decisive (harvest) |
| W4 | **0-gem gold trips at any distance** | Harvest: 22 zero-gem captures, 9 at g11 next to their spawn | 1 | major |
| W5 | **Focus-burst blind spot** in the fight model | Starfish: late kills 10-17, deaths 19 vs 13, single-round hits up to 1,925; harvest Marcella 3,005/0 | 2 | major |
| W6 | **Slow farm tempo, high camp damage (Bruiser-only build)** | Starfish: 34 vs 147 clears (572 vs 211 per 1k); harvest 45 vs 78 (521 vs 219); the farm 870 gems in 2,000 rounds against no opposition | 3 | major |
| W7 | **No early commitment to solo-rejected big groups** | Elk 0-72 until r248 (24 of 25 early captures 0-gem); starfish g15 first at r1394; harvest g20 and the golem groups never taken; the farm's monoliths and g9 never touched | 4 | major |
| W8 | **Big bags not banked under contest** | Stalactites: HoR recalled with 205 (r217-222) and backed off with 210 (r362-392), next to a usable altar, while enemies banked 148 and 154 at the same altars | 1 | minor (won) |
| W9 | **Idle enemy carriers left alone** | The farm: 136 gems parked at (23-26,15-17) from about r450; first kill r1603 | 1 | minor (won) |

### Testable hypotheses (structure-keyed; no map or team names in any fix)
1. **H-cycle (W1, top priority): kill both 2-cycle classes.**
   - **(a) Claim 2-cycle.** Port h_bigmap's `CLAIM_FIX` (helper bit; x0.3 only against a solo-capable claimant) and its v2 `CYCLE_GUARD` into c2. `bots/c4_fallback` has neither.
   - **(b) Camp-gate flicker.** h_bigmap's guard commits to a *target*, which does not fix a `do_tribute` route flip. In `blocked_now`, also block the tiles of groups believed alive (`G.status == 0` with live `G.hp` entries), which are static and remembered. Or add route hysteresis: after an A,B,A,B position pattern with unchanged gems, keep the last route for about 10 turns.
   - **Metrics:**
     - `freeze_metric` champion-rounds, split into carrying and not carrying;
     - period-2 fuel stretches (this note's method);
     - turns from capture to bank.
   - **Predict:** carrier-frozen rounds near 0 on gate maps, and the 100x100 two-target cycles gone.
   - **Gate:** full `--maps all`, plus traces of 01the-farm A/B and 02harvest A/B as mechanism checks.
2. **H-band (W2): heal instead of 0-gem farming in the band.**
   - **Change:** when `hp < 0.6*maxhp` and the best target has strength 0 and gems 0, treat it as no target, so the existing `G is None` → recall-if-`hp < 0.7` path heals (only when `recall_safe`). Alternative: raise `low` to 0.6 while no strength > 0 group is eligible.
   - **Metrics:** band champion-rounds per game (now 624 locally); 0-gem captures with more than 20 steps of travel; gems per alive champion-round.
   - **Mechanism check:** 02harvest A (1,700 band rounds locally).
3. **H-goldcap (W4): bound travel for gold-only groups.**
   - **Change:** a group with 0 gems is eligible only within about 12 path steps of the champion, of its next gem target, or of our spawn, unless `gold_play()`. This keeps the early gold-cluster income near spawn (the elk strength).
   - **Metrics:** 0-gem captures per game; gold at r250 (must not fall).
4. **H-claimreach (W3; different from the rejected T8 enemy-half x0.4): count help only from allies who are actually there.**
   - **Change:** the +55 dps per claimant and the x1.2 non-solo bonus apply only if a claiming ally is visible within 8 tiles of us or of the group's centre. Otherwise the non-solo chooser keeps the solo test with c = 0.
   - **Add a contested-zone stamp:** for about 150 rounds after we retreat from, or take champion damage near, a group (within 8), multiply its score by about 0.5 unless `group_balance` near ratio ≥ `GROUP_ADV`.
   - **Metrics:** share of captures on our side; champion damage taken with 0 dealt; first-capture round of the nearest wolf+gem group.
   - **Validate** against a solo own-side farmer imitation (see the methodology note below), not only self-play.
5. **H-burst (W5): a Focus-aware threat model.**
   - **Change:** for an enemy whose kit has a damage spell (`is_damage`, `is_cc` or `is_aoe_damage` with `damage_amount() > 0`) and that is within its cast range + 1, add that spell's damage to `threat` and `fight_dps`. That is the burst available this turn, not /8.
   - Use the same term in `recall_safe` and in the engage ratio.
   - **Metrics:** late (r > 1000) K/D; deaths with ≥ 15 gems carried; largest single-round damage taken before a retreat.
   - **Test** against a Focus-stacking imitation.
6. **H-jungle2 (W6; a Q28 variant keyed on the champion's own stats):** after the first Bruiser emblem, buy Jungle next if the champion's own camp damage taken per 1k dealt is above about 400.
   - **Metrics:** camp damage per 1k; heal trips per 1,000 rounds; fight K/D must hold.
7. **H-commit (W7): open on a dominant group when it is close.**
   - **Change:** if one group holds ≥ 40% of the map's gems, is within about 15 path steps of our spawn, and every champion rejects it solo, muster the team on it from r1 (h_teamclear bootstrap); otherwise use the c4 team fallback.
   - **Metrics:** first-capture round of the top group; gems at r250.
8. **H-bigbag (W8, low priority).** A champion carrying ≥ 60 gems within 1 tile of a usable altar, with no enemy stunner within cast range + 1, starts the tribute before `handle_enemies` (damage does not interrupt a tribute). If enemies are channelling at that altar, they are tier-0 targets first.
9. **H-idlecarrier (W9, low priority).** An enemy seen stationary for ≥ 50 rounds with ≥ 30 gems becomes a team focus; muster 2-3 before engaging.

**Methodology note.** Build an imitation of this opponent for tests of H-claimreach, H-burst and H-jungle2:
- fixed draft Stellar, Ren, Marcella, Ryth, Varg;
- first emblem Prospector / Jungle / Treasure, then Jungle, Bruiser, Durability, then Power or Monster Focus stacking;
- a strictly solo own-side circuit, nearest altar, no locks.

Self-play cannot show the own-side farming race that decided harvest.

**Ladder expectation (not a fix).** This bot farms 2-3 times our rate on large symmetric maps when left alone (harvest). It loses to grouping at chokepoints, to carrier kills at altars, and to objectives it ignores (multi-elk groups). Expect losses to it, and to bots like it, on 100x100 maps until W1-W4 are fixed.

## Changes from the first draft of this note
A draft of this note was written at 06:12 UTC; `tools/organize_notes.py` has since moved it to `results/real-matches/2026-11-01_0542_electric-fog-walkers_b8923d32/notes.md`. This version re-derives every number.
- **New:**
  - W1: the farm's 33% carrier freeze, and harvest Vesper's 455-round 2-cycle in anti-phase with HoR (fuel-trace evidence);
  - W5: late Focus-burst damage and the threat-model code;
  - W8: big bags held next to the altar on stalactites;
  - the opponent's own freezes (farm trio, elk Stellar).
- **Corrected:**
  - Elk: 24 of 25 early captures were 0-gem (not 29).
  - Harvest: Marcella's r1050-1200 champion damage taken was 3,005 (not 4,400).
  - Vesper's early harvest walks included two skirmishes (585 and 870 damage taken), not "0 damage".
  - The farm's y=19 wall can be walked around at x ≤ 15 or x ≥ 34, so g16 is not the "only gap": the issue is route flicker, not a blocked map.
  - The local band census recomputed to 624 per game, 123/140, 1,700 on 02harvest A, and 27% 0-gem captures (was 564, 113/140, 1,720, 24%).
