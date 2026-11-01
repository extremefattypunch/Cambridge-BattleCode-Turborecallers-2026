# Sneaky Wardens (1512): ladder set 008a189a, 1 Nov 2026, our v3, won 5-0

- **Opponent:** Sneaky Wardens, rating 1512 (ours after the set: 1529).
- **Our version:** website v3 = `bots/q24_combo` (live 01:42-04:42 UTC). The set ran at 02:12 UTC. We were side A (team A) in all 5 games.
- **Record: 5-0.**
  - W 00dunes 1004-122 (r1242, gems).
  - W 00anvil 1183-21 (r1381, gems).
  - W 02cuts 1005-714 (r1659, gems).
  - W 02the_pond 939-417 (r2000, tiebreak on gems).
  - W 01starvation 860-8 (r2000, tiebreak on gems).
- **Link:** https://2026a.battlecode.co.uk/game/match-groups/008a189a-1502-49b5-84ac-ca25dc8bad18
- **Sources:**
  - `results/ladder-games.jsonl` rows and `matches/ladder/summary/<id>__A.json`;
  - `python3.12 -I tools/scout.py --group 008a189a` for every number in the tables;
  - `tools/freeze_metric.py` for idle stretches;
  - ward trails (one ward per 10 rounds after a move of more than 6 tiles, see `try_ward`) to infer positions. The stats file has no per-round positions.
  - Replays for these games are not downloaded. The inner `replay.repl26a` is a binary format with no decoder in the repo, so positions below are *inferred*.
- **Bottom line:**
  - This opponent is badly broken: 111-419 `fuelExhausted` events per game on 3 maps, and up to 6,524 idle champion-rounds. We won every game.
  - The set still exposes **our tempo problem**. Two games ran to r2000 against an opponent that scored 8 and 417.
  - On 01starvation, with no opposition at all, we collected only 952 camp gems in 2,000 rounds.

## Game summary
Gem race = tributed gems, us-them.

| Map (size, symmetry, picks) | Result | r250 | r500 | r1000 | End | Clears/100r us-them | K us-them |
|---|---|---|---|---|---|---|---|
| 00dunes (79x79, rot180, 5) | **W** | 174-18 | 244-61 | 659-122 | 1004-122 r1242 | 2.09-0.81 | 18-7 |
| 00anvil (37x31, horizontal, 3) | **W** | 63-21 | 217-21 | 504-21 | 1183-21 r1381 | 5.58-0.58 | 22-1 |
| 02cuts (60x60, rot180, 5) | **W** | 87-33 | 160-146 | 514-344 | 1005-714 r1659 | 2.83-1.63 | 5-2 |
| 02the_pond (30x30, rot180, 3) | **W** | 40-12 | 242-78 | 426-180 | 939-417 r2000 | 3.3-1.7 | 11-5 |
| 01starvation (80x80, horizontal, 5) | **W** | 46-0 | 188-0 | 404-4 | 860-8 r2000 | 5.3-0.75 | 6-3 |

## 1. Opponent profile
**Draft: fixed.** Heart of Ruin, Vesper Vale, Marcella, Ryth, Vendetta, truncated to the pick count (3-pick: HoR, Vesper, Marcella).
- It is the same five champions as ours in a different order, so every game was a near-mirror.
- No map adaptation.

**Roles (from per-champion lines).**
- **HoR is their only real fighter:**
  - dunes 6 kills, 3 deaths, 11,385 shielding;
  - pond 2/4 with 34,320 shielding.
- **Everyone else is a slow solo farmer.** Their Ryth went 0/7 on dunes and 0/4 on starvation.

**Items: Treasure emblem first, then Bruiser, then Power stacking where gold allows. Purchases are very late.**

| Champion | 1st emblem completed (round) | then |
|---|---|---|
| Heart of Ruin | Treasure F at r223 (dunes) and r330 (pond); never completed on anvil or cuts (Treasure shards from r68-220); Power F at r483 on starvation | Bruiser F, then Power F x n (pond: 8 Power emblems by r1712) |
| Vesper Vale | Treasure S at r294 (dunes, pond) and r951 (cuts); Power F at r549 on starvation; 2 shards only on anvil (r1305) | Bruiser S; Power S x n on pond |
| Marcella | Treasure H at r267 (pond), r601 (cuts), r824 (dunes) | **never shopped** on anvil and starvation |
| Ryth | Treasure H at r1164 (dunes) and r1606 (cuts); Power F at r1934 (starvation) | — |
| Vendetta | Treasure H at r344 (cuts); 1 shard at r880 (dunes); Power F at r783 (starvation) | Bruiser S, Power S (cuts) |

- Team gold at r500: 626 / 100 / 469 / 1,150 / 346, against our 1,445 / 1,608 / 1,633 / 1,210 / 932.
- **No altar locks or TP crystals in any game.** Wards: 21-275 per game, almost all on their own half. The name notwithstanding, they don't ward our side.

**Farming: strictly solo, own side only, slow.**
- 100% solo captures: 10/10, 4/4, 27/27, 36/36, 14/14.
- Enemy-side (our-side) captures: 0, 1, 0, 1 and 1 per game.
- Clear rate 0.58-1.7 per 100 rounds, against our 2.1-5.6.
- **Opening:** one champion takes the nearest gem group:
  - dunes: HoR solo on g4 Elk+GemClx4 at r54;
  - cuts: HoR on g5 Wolf at r19;
  - pond: HoR on g6 Wolfx3 at r67.
- **Big objectives:** they never take them.
- **The bot is visibly starved of compute:**
  - `fuelExhausted` after r1: 111 (dunes), 6 (anvil), 222 (cuts), 2 (pond), 419 (starvation);
  - idle (quiet) champion-rounds: 594, 257, 1,955, 137 and 6,524.
  - On starvation their 5 champions made 14 captures in 2,000 rounds, 13 of them 0-gem gold clusters. Their first tribute was at r923.

**Tributes: few and mid-size, at their nearest altar.**
- Count x mean: dunes 4 x 30.5, anvil 1 x 21, cuts 26 x 27.5 (every bag 24-29), pond 32 x 13.0, starvation 2 x 4.
- First tribute: r198, r166, r72, r88 and r923.
- **On 02cuts they banked 14 times (392 gems) at altar #1 (25,25), on OUR side of the map.** Nobody contested or locked it. Our lock usage there was about 1.

**Fights: rare and defensive.**
- Kills per 100 rounds: 0.06-0.48.
- Their kills on us are mostly HoR on our half (dunes, 50% in our half). Otherwise our champions die to their champions defending their own groups.
- No hunting, no spawn camping, no carrier focus.
- They lost 165 gems to our champions on dunes, 78 on pond and 25 on anvil.

**Adaptation across the 5 maps: none.** Their strength tracks their fuel:
- cuts (222 exhaustions, but 27 captures) was their best game, 714;
- starvation (419) was their worst, 8.

## 2. Per game
### 00dunes: W 1004-122
**Map.** Altars #0 (39,35) and #1 (39,43) sit beside the centre group g0, GemClx8+Golem (92 gems, 3 tiles from the altars).
- Each side has an Elk+GemClx4 group (43 gems, 9 from the altar) and a Wolf+GemClx2 group (18).
- Six Wolf+GoldCl groups lie far away.

**Opening.**
- Our 4-champion clear of our g3 Elk+GemClx4 (Vendetta, Marcella, HoR, Ryth) at r58; first tribute r88.
- Their HoR soloed their g4 at r54 but didn't tribute until r198. Score 174-18 at r250.

**Fights.** All 3 multi-death fights were ours:
- r329-335 at (46,27);
- r470-471 at (52,26), where Vendetta killed Vendetta and Ryth;
- r968-978 at (40,46), by the altar.

Vendetta went 8/1. 104 of their gems died to us after r1000.

**Missed.** The 92-gem centre g0, 3 tiles from both altars, was first captured at **r891** (Marcella + Ryth, 46 each), and only twice all game.

**Root.** The opponent barely played. We farmed our two near-altar groups g1/g3 19 times (10 + 9) and won every fight.

### 00anvil: W 1183-21
**Map.** One altar (18,8) in the middle. The g10 Monolith (200 gems, 3 tiles from the altar) sits beside it, with gold clusters around the spawns.

**Their game.** 4 captures, 1 tribute (21 at r166) and 179 earned gold. Their Marcella never shopped. 25 deaths (Vendetta 13/0, Marcella 6/1).

**Our weak start.**
- Our first four captures were 0-gem gold clusters by Marcella: g4 at r16, g11 at r30, then Wolf+GoldCl g0 at r66 and g4 again at r81.
- The first gem capture came at r95 (g9 GemClx3). Score only 63-21 at r250.

**Swing.** The Monolith was taken **solo by Vendetta at r1179** (+200). Window r1000-1381: +479.

**Root.** We won on volume: 77 clears to 8.

### 02cuts: W 1005-714 (their best game)
**Map.** Four altars on the diagonal: #0 (14,14) and #1 (25,25) ours, #2 (34,34) and #3 (45,45) theirs.
- Mid group g22 GemClx4 (30,30), 27 steps from both spawns.
- Golem groups g16/g17 (78 gems).
- Monolith groups g23/g24 (228 gems each) at (27,32)/(32,27).

**Race.** 87-33 at r250, then **160-146 at r500 (+14 only)**. The game was decided r750-1000 (+148).

**Their plan.** Solo farming of their side plus the mid g22, which they captured 15 times to our 4. Then 28-gem bags into our altar #1 (25,25), 14 times.

**Our problems.**
- **Vendetta collected 42 gems all game.** It was idle r1060-1659 (599 rounds).
  - Last ward at (26,52), 3-4 tiles from g8 Wolfx2+Elk+GoldClx6 (30,55), which was never touched.
  - Our solo model rejects g8 for Vendetta: about 8 chip cycles, over the limit of 4.
  - The idle cause is *not identifiable from the stats*. The v3 respawn push-back needs a dead camp tile on the path, and g8 was never touched, so it is unlikely here.
- 13 groups were never touched, including both 228-gem monolith groups and the 78-gem g16 on our side, which we first took at r956.

**Root.** Our bigger groups won it: 1,077 camp gems to 743. Two champions' worth of time was lost: Vendetta idle, and Ryth 126 rounds idle at r340-466.

### 02the_pond: W 939-417 (r2000)
**Map.** 30x30. The central gem island (g0-g3 GemCl, 70 gems in total) is ringed by holes, so reaching it needs a dash or a TP crystal. Altars #0 (3,7) theirs and #1 (26,22) ours.

**Our play.**
- 15 TP crystals and 13 altar locks bought.
- **Vesper did nothing for r0-140.** Its ward trail runs (25,1) → (16,2) → (6,10) → (0,19) → (0,14) → (5,5) → spawn at r159, where it bought a crystal. There are no damage or gold changes in that time.
- 3.3 clears per 100 rounds, but the bags were small (20 per tribute).

**Their play.** Power stacking (Power:Str 28 at the end), 32 tributes of 13 gems.

**Fights.** 11-5 for us, 6 of the kills at the altars (their 78 gems lost).

**Root.** We out-farmed them 2:1 and still didn't reach 1,000 in 2,000 rounds. The gap is tempo, not opposition.

### 01starvation: W 860-8 (r2000)
**Map.** 80x80. Two altars at (35,15) and (44,15), mid.
- g5 GemClx4 (40,10), 4 tiles from them.
- **g2 Elkx4+GemClx4+GoldClx4 (88 gems) at (40,16), 3 tiles from both altars.**
- Two Monoliths g10/g11 (200 each).
- Gold-cluster pairs elsewhere.

**Their game.** 419 fuel exhaustions, 6,524 idle champion-rounds, 4 camp deaths.

**Ours, effectively unopposed.**
- 107 captures, but **40 of them 0-gem**.
- 36 captures on their side for 76 gems in total: gold clusters g4, and the wolf g7 at 4 gems each.
- About 700 of our 952 camp gems came from one group, g5 (25 captures x 28).
- g2 (88) was captured **once, at r1964**. The monoliths were never touched.
- Idle 2,152 champion-rounds: Vendetta 631, Vesper 560, HoR 529.

**Root.** Our target model has no way to commit the team to a group that fails the solo safety check, even when there is no opposition at all.

## 3. Their strategy vs ours
**Where theirs was "superior" (minor; their bot is broken):**

| Gap | Size | Our code responsible |
|---|---|---|
| **Uncontested banking on our side** (02cuts: 14 x 28 = 392 gems at our altar #1) | 39% of their gems on that map | `try_lock`'s proactive branch only locks `self.lock_side`, altars no farther from the enemy spawn than ours + `LOCK_SIDE_MARGIN`, i.e. *their* side. The reactive branch needs a visible tributing enemy within 2 of us. There is no memory of "enemy banks at altar X". |
| **Mid group contested** (cuts g22: 15 to our 4) | 420 gems to them | `choose_target` scores by `G.value / cost` with no notion that a group is contested. Claims (`c` x0.3 when `solo_ok`) spread our champions to other groups. |

**Where ours was superior (by a lot).**
- **Clears:** 1.7-10x theirs (2.09-0.81, 5.58-0.58, 2.83-1.63, 3.3-1.7, 5.3-0.75).
- **Gold at r1000:** ahead in all five: 3,035-1,106, 4,232-100, 3,365-1,041, 2,862-2,714 and 2,039-699.
- **Fights:** K 62-18 over the set; all 5 multi-death fights won (3 on dunes, 2 on anvil).
- **Early tributes:** our first tribute came at r66-129, theirs at r72-923. They were first only on cuts (r72 vs r86).
- **Grouped openings** on near-spawn elk groups: 3-4 champions on dunes g3 at r58 and cuts g14 at r81.

## 4. Our weaknesses exposed
| # | Weakness | Evidence | Games | Impact |
|---|---|---|---|---|
| W1 | **Can't close games against a passive opponent.** The value and solo-safety model leaves the big groups to the end. | Starvation 860 at r2000: 88-gem g2 (3 tiles from the altars) once at r1964, monoliths untouched. Pond 939 at r2000. Dunes 92-gem centre first at r891. Anvil monolith first at r1179. Cuts 78-gem g16 first at r956, both 228-gem groups untouched. | 5 | major (no loss here; the same mechanism costs games against real opponents) |
| W2 | **Long idle stretches** (freeze ≥ 100 rounds while alive) | Cuts: Vendetta 599 rounds (r1060-1659, by (26,52)). Starvation: 2,152 idle champion-rounds. Pond: Vesper r0-140. `freeze_metric` (≥150): cuts 600. | 3 | major |
| W3 | **0-gem and far captures** | Starvation: 40 of 107 captures 0-gem; 36 on their side for 76 gems. Anvil: 4 of the first 4 captures 0-gem (gem race 63-21 at r250). | 2 | minor |
| W4 | **Own-side altar left to the enemy** | Cuts: 14 enemy tributes (392 gems) at our altar #1; we used about 1 lock. | 1 | minor |

## Testable hypotheses (structure-keyed; no map or team names)
1. **H-commit-uncontested (W1).**
   - **Change.** If no enemy champion has been seen within 10 tiles of a group for 150+ rounds, at least 3 of our champions are healthy (≥ 80% HP), and the group holds ≥ 15% of the map's gems within 6 tiles of an altar, the team musters on it.
     - Reuse the existing claims byte; extra claims already raise `tdps = dps + c*55` in `choose_target`.
     - Ignore the solo safety check while ≥ 3 claimers are within 4 tiles.
   - **Metrics.** Rounds to 1,000 against passive imitations (starter-python, `imit_test`); first-capture round of the largest group; gems per alive champion-round. The cuts/starvation-style maps in the local pool are the mechanism check.
2. **H-idle-watchdog (W2).** If a champion has gone 80 rounds with no change in any activity counter (damage, gold, gems, kills; the `freeze_metric` definition) while alive and off spawn, ban its current target for 150 rounds and drop all status-2 waits. Recall if HP < 70%.
   - **Metric:** `tools/freeze_metric.py` idle champion-rounds, which must not rise in fight-heavy games.
3. **H-goldcap (W3, shared with the b8923d32 report).** A 0-gem group is valued only within about 12 path tiles of the champion or of its next gem target, unless `gold_play()` is on.
   - **Metrics:** 0-gem captures per game; gold at r250, which must not fall.
4. **H-lock-memory-own (W4).** Remember altars where an enemy completed or started a tribute (seen in vision) in the last 300 rounds. Lock such an altar on the next pass within 2, even on our side.
   - **Metric:** enemy tributes at our-side altars per game.

**Opponent notes (for ladder expectations, not for fixes).**
- This is a near-mirror draft run by a fuel-starved bot.
- Expect wins. The only risk is a map where its 28-gem steady banking runs uncontested at an altar we don't visit.
