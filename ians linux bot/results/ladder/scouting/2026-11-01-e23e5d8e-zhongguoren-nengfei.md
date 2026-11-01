# vs 中国人能飞 (1522): 3-2, 2026-11-01 03:42 UTC, our v3 (`q24_combo`)

**Site:** https://2026a.battlecode.co.uk/game/match-groups/e23e5d8e-43f2-4011-8a85-eeb51134223d
**Data:** `matches/ladder/summary/<matchId>__A.json` for each game (we were team A in all 5); `python3.12 -I tools/scout.py --group e23e5d8e`

- **Opponent:** 中国人能飞 ("Chinese people can fly"), rated 1522 before the set and 1519 after. Our rating after the set: 1526.
- **Our version:** v3 = `bots/q24_combo` (live 01:42-04:42 UTC). Everything below about our code also holds for v4 (`bots/c2_respawn`). v4 differs from v3 only in the respawn-tile step-off rule (`leave_respawn_tile`), and none of the weaknesses below involves that rule. Line numbers are given as v3 / v4.
- **Record: 3-2.**
  - **L 00contest 0-1000** (r1412, gems).
  - W 02the_pond 708-342 (r2000, tiebreak on gems; 3 picks).
  - W 02gift_wrapping 44-0 (r2000, tiebreak on gems).
  - **L adgato_gemcombat4 574-1004** (r600, gems).
  - W 01corridors 441-0 (r2000, tiebreak on gems).
- **Method:** the stats files hold no per-round positions. Positions come from death, kill, ward, clear and capture events (a ward lands within 2 tiles of whoever placed it). Map layouts come from the decoded `.map26a` files via `tools/scout.py`. Anything marked *speculation* was not directly observed. The helper scripts are in the session scratchpad, not the repo.

## 1. Opponent profile

**Draft: fixed.**
- 5 picks: Cassi & Issac, Varg, Vendetta, Ryth, Ren. That is 6 bodies against our 5.
- 3 picks (02the_pond): Varg, Cassi & Issac, Vendetta.
- Our draft: Vesper Vale, Vendetta, Marcella, Heart of Ruin, Ryth. Mirror picks: Vendetta and Ryth.

**Champion roles (from the per-champion lines):**
| Champion | Role | Evidence |
|---|---|---|
| Vendetta | Main killer and boss farmer | 00contest: 8 kills / 1 death, 16,087 champion damage, 400 boss gems tributed. 02the_pond: 7/1 |
| Ren | Second killer | 00contest: 7/1, 20,958 champion damage. Tributed two 200-gem boss bags |
| Varg | Splash farmer and tank | Shielded 5,750 on 00contest, 15,750 on 02the_pond. Took one 200-gem boss bag |
| Cassi & Issac | Extra bodies, farming support | They die to camps a lot: 00contest r575 (both, to the monolith), 02the_pond r307 and r646 |
| Ryth | Farmer | 4-12 clears per game |

**Items: Power on every champion plus one Durability Health emblem, nothing else.**
- No Jungle, Monster, Treasure or Bruiser, and no altar locks or TP crystals in any game.
- Early (00contest):
  - Vendetta's first shards at r43; Power Strength emblem by r143; Durability Health by r258.
  - Ren: Power Strength by r201, Durability Health by r303.
  - Issac: Power Strength at r115.
  - Totals: 15 emblems by r500 against our 5, and 28 by r1000 against our 18.
- Where they could not farm, they never shopped: 02gift_wrapping (no item at all), 01corridors (only Cassi, 3 shards at r106).

**Farming: strong where camps are weak, broken where camps are strong.**
- **Open cluster maps.**
  - adgato_gemcombat4: a 3-group circuit on their half, g5 (10,44) 28g, g7 (2,42) 35g and g3 (2,33) 42g, recaptured 7-8 rounds after each 50-round respawn. g5 was captured at r17, 74, 136, 197, 255, 316, 381, 437, 496 and 563.
  - 28 captures to our 19 in 600 rounds.
- **Boss maps.** On 00contest the whole team works the two 200-gem Monoliths.
  - g1 (32,18) clears: r752 (Ren), r973 (Vendetta), r1190 (Vendetta), r1368 (Varg). g0 (17,31) clear: r1077 (Vendetta).
  - **Each capture went to a single champion** (all 200 gems to one carrier).
  - It cost them deaths: Cassi and Issac at r575, Vendetta r723, Ren r969 and Ryth r1167, all killed by the Monolith ("camp#1").
- **Strong-camp or walled maps: their farming collapses.**
  - 01corridors: **0 clears in 2,000 rounds, and 103 deaths to camps** (93 in their own half).
  - 02gift_wrapping: **0 clears**, and every champion was quiet from about r64-79 to r2000.
  - 02the_pond: 23 clears, and 2,148 quiet champion-rounds (Cassi 715).
  - Their bot also runs out of fuel in the opening of every game: 61, 1, 31, 27 and 26 `fuelExhausted` events, mostly in r1-7. That is a suspended opening, which matters most on maps where they must path through camps.

**Tributes.**
| Map | Tributes | Mean size | First | Notes |
|---|---|---|---|---|
| 00contest | 5 | 200 | r800 | All at altar (25,24): r800, r1028, r1192, r1240, r1413. Each is a 20-turn channel (ceil(200/10)) |
| adgato_gemcombat4 | 33 | 30.4 | r37 | Small and frequent |
| 02the_pond | 30 | 11.4 | r205 | Late first tribute |

**Fights: they invade and gank on open maps.**
- **00contest:**
  - 19 kills, 17 of them in our half or at our spawn. Fed champions: Vendetta 8/1, Ren 7/1.
  - Twelve of our deaths came in r193-605. Examples: Vesper (9,18) r224 and Marcella (11,19) r233 to Vendetta; Ryth (17,17) r267 and HoR (16,18) r290 to Ren; Vendetta (7,14) r298 to Vendetta.
  - Their wards show Vendetta roaming next to our spawn (3-5,3-5): (10,14) r251, (2,8) r302, (11,14) r349. Issac warded (9,11) at r300.
  - **Targets were our lone gold-cluster farmers, not carriers.** We never carried a gem on this map.
- **adgato_gemcombat4:** they held their mid group g3 (2,33).
  - Marcella r129 (3,28), Ryth r204 (3,28), Vendetta r210 (1,31) and Vesper r532 (1,33) all died there.
  - They killed two of our carriers: Marcella at (15,22) r255 with 28 gems (Vendetta), and Ryth at (25,29) r373 with 28 (Varg).
- **02the_pond:** their Vendetta guarded their own altar (3,7). Seven of our eight deaths were within 7 tiles of it, for example (5,13) r407, (4,13) r578, (5,12) r1083, (3,12) r1411 and (7,6) r1418.
- **Map control:** no altar locks and no crystals. Wards: 278, 56, 30, 113 and 131 per game, mostly their own half.

**Adaptation across the 5 maps: none.** Draft, build and play were the same every game. Results tracked map structure:
- they won both open maps (boss-only and cluster-only);
- they scored 0, 0 and 342 on the three maps whose gems sit behind strong camps or narrow walled paths.

## 2. Per game
Gem race = tributed gems, us-them.

| # | Map (size, picks) | Result | r250 | r500 | r1000 | End | Gold us-them | Clears us-them | Kills us-them |
|---|---|---|---|---|---|---|---|---|---|
| 1 | 00contest (50x50, 5) | **L** | 0-0 | 0-0 | 0-200 | 0-1000 r1412 | 5,555-6,960 | 88-49 | 3-19 |
| 2 | 02the_pond (30x30, 3) | **W** | 57-15 | 141-30 | 243-75 | 708-342 r2000 | 6,436-4,340 | 52-23 | 5-8 |
| 3 | 02gift_wrapping (45x45, 5) | **W** | 0-0 | 44-0 | 44-0 | 44-0 r2000 | 186-0 | 1-0 | 0-0 |
| 4 | adgato_gemcombat4 (41x61, 5) | **L** | 245-336 | 434-796 | — | 574-1004 r600 | 539-700 | 19-28 | 4-7 |
| 5 | 01corridors (51x40, 5) | **W** | 0-0 | 22-0 | 62-0 | 441-0 r2000 | 3,676-100 | 23-0 | 0-1 |

### Game 1: 00contest, L 0-1000
**Map.** The only gem sources are two Monoliths (200 gems, 20,000 HP, Strength 200, range 5): g0 at (17,31) and g1 at (32,18), both 30 BFS steps from each spawn. Twelve gold-cluster groups (0 gems) fill the rest. There are two central altars, (24,25) and (25,24).

**Decisive moments.**
- **r193-605: the gank phase.**
  - Twelve of our deaths, all in our half or at the altar, to Vendetta (8 in the game) and Ren (7).
  - Gold at r250 was 726-1,480 and at r500 1,338-2,960. Emblems by r500: 5 to 15.
  - Our five champions were spread over gold clusters on our half and in the middle, g12 (6,18), g6 (19,4), g8 (5,34), g4 (18,27) and g3 (27,18); 88% of our captures were solo. Our only kill before r671 was Ryth's at r73.
- **r575-723: they open the boss.** Cassi and Issac died to the Monolith at r575 and their Vendetta at r723. We killed Cassi and Issac at r671 at (33,17)/(37,19) while they hit the Monolith, but our Vendetta then died to the Monolith at (37,19) at r679.
- **r752-1413: five boss bags.** The captures were r759 (Ren), r980 (Vendetta), r1083 (Ren, g0), r1197 (Varg) and r1374 (Vendetta). All five were tributed at (25,24) in 20-turn channels.
  - During three of the channels one of our champions was within 2-4 tiles of that altar: HoR warded (24,28) at r773, Ryth (27,22) at r1216, and Marcella (22,24) at r1397.
  - We held altar locks: 15 bought, about 11 used. No 200-gem channel was cancelled.

**Root reason.**
- `choose_target` never targets a Monolith, so we scored 0 gems in 1,412 rounds.
- The opponent took 5 x 200 with team clears and single-champion captures.
- The early ganks (gold 1,480 vs 726 at r250) also let them out-item us.

### Game 2: 02the_pond, W 708-342 (3 picks)
- **Our lead from the start.** We tributed first by 139 rounds: Marcella 15 at r66, then 42 at r232, r298 and r364 at our altar (26,22).
- **Their opening was passive:** first clear r169, first tribute r205, 2,148 quiet champion-rounds. Cassi and Issac also died to camps at r307, r646 (and Varg at r739).
- **Our losses there:** seven of our eight deaths were within 7 tiles of their altar (3,7), six of them to their Vendetta (7/1 in the game) and one to Varg (r1897). We tributed 8 times there (135 gems) when it was the nearest altar on our path, and lost Vendetta r407, Vesper r578, Marcella r1083, Vesper r1411 and Marcella r1418 nearby. No gems were lost in those deaths.
- **Root reason:** we out-farmed a passive opponent (52-23 clears, 6,436-4,340 gold). The deaths at their altar only cost tempo.

### Game 3: 02gift_wrapping, W 44-0
- **The opponent did nothing.** 0 clears; all six champions were quiet from about r64-79 to r2000, and they had 31 `fuelExhausted` events in r1-7.
- **Our single capture.** Our only capture was g7 (Wolf x4 + GemCl x4, 44g at (5,24)) at r359, with all five champions. That bag split into 12/8/8/8/8, banked at (12,20) in r365-388.
- **Then we stopped.** From r365 to r2000 all five of our champions were quiet: 9,808 champion-rounds with no metric change.
  - The capture happened in chip mode, which `play_turn` enables while both teams are on 0 tributed gems after r300.
  - Our own first tribute switched it off (`self.chip = False`, q24 l.2457 / c2 l.2522).
  - After that every group fails the solo safety model again. That includes g0 (Elk x2 + GemCl, 128g), which nobody ever touched.
- **Root reason:** we won only because the opponent's bot never started. Against any opponent that farms, this map is a loss; v1/v2 lost it 0-1028 and 16-1006 (STRATEGIES T23).

### Game 4: adgato_gemcombat4, L 574-1004 (r600)
**Map.** Every group is gem clusters (0 Strength), around one central altar (20,30).
- Each side has a 105-gem circuit: ours g4 28g, g6 35g, g2 42g; theirs g5, g7, g3.
- Two 21g pockets, g0 (17,18) and g1 (23,42), are ringed by holes. Neither team took them; g0 is 8 BFS steps from our spawn.

**Decisive moments.**
- **r0-250: the recapture gap.** We fell behind 91. Respawn is 50 rounds after a capture. The lateness of the second capture after respawn was:
  - theirs: g5 7 rounds, g7 8;
  - ours: g4 35, g6 15, g2 69.
- **r200-400: they gained 413 to our 77.**
  - Our deaths: Ryth r204 (3,28) to Ren, and Vendetta r210 (1,31) to Issac, both at their mid group g3. Then Marcella r255 at (15,22) with **28 gems** to Vendetta, and Ryth r373 at (25,29) by the altar with **28 gems** to Varg.
  - Two to three of our champions were dead at any moment from r204 to about r270. At r400 we were carrying 70 unbanked gems.
  - Captures in the window: theirs 11, ours 6.
- **r500-600:** they closed it out with 33 tributes (median 28).

**Root reason.** On a symmetric cluster map they ran a tighter circuit (28 vs 19 captures) and won the fights at the contested mid group g3 and at the altar. They killed 4 of our champions there before r400, two of them carrying 28 gems each.
- Three different champions of ours died at the same mid group, (1-3, 28-33), within 81 rounds. Our death memory (`died_at`) is per champion, so the others kept going there.

### Game 5: 01corridors, W 441-0
- **The opponent destroyed itself on the camps:** 103 deaths to camps (Cassi 22, Issac 22, Varg 18) and 0 clears.
- **We were slow too.** We needed 2,000 rounds for 441: 23 clears (1.15 per 100 rounds), 1,000 gems lost to nothing but time.
  - **Our Vesper Vale earned 0 gold and 0 gems all game.** It was quiet r0-961, with 1,437 quiet rounds in total.
  - Its ward trail loops every ~150 rounds between the corridor x=8-10 near g5 (8,20): (10,15) r21, (10,10) r33, (12,17) r43. Then it goes to corridors x=36-42 near g9 and g10: (38,8) r103, (40,18) r113, (38,13) r124, and back via (16,2) r154 and (10,11) r164. The same loop repeats at r199-r311 and r323-r466.
  - That is a target 2-cycle between two far groups, and it never attacks.
- **Gems destroyed:** Ryth and HoR died to the Elk pair g1 at (21,19)/(20,18) at r1752-1755, losing **58 gems** (camp kills destroy the bag).
- **Root reason:** the opponent was broken. Our own throughput was limited by the solo model and by Vesper's freeze. The elk groups g8 (Elk x4, 60g) and g10 (30g) and the Monolith field g0 (428g) were never touched.

## 3. Their strategy vs ours

**Overall (3-2).** Each side won on the map structures that suit it.
- Theirs was superior on **open maps with big or quick gem sources**: a boss map and a cluster circuit.
  - They team up on giant camps and send a single carrier with the whole bag.
  - They run a tight recapture circuit.
  - Power-built Vendetta and Ren hunt our lone farmers.
- Ours was superior on **maps with strong camps or walled paths**: their bot does not farm there at all.
- **Two of our three wins were against a bot that did not function:** 0 clears on 02gift_wrapping and on 01corridors. They are not evidence that our strategy is better.

**Where theirs was superior, and by how much.**
| Aspect | Them | Us | Gap |
|---|---|---|---|
| Boss gems (00contest) | 1,000 from 5 Monolith captures | 0, never attempted | Decided the game |
| Early fights (00contest) | 19 kills; 1,480 gold by r250 | 3 kills, 23 deaths; 726 gold by r250 | 2.0x gold at r250 and r500; 15 vs 5 emblems at r500 |
| Cluster-circuit tempo (gemcombat4) | 28 captures, first tribute r37, recaptures 7-8 rounds after respawn | 19 captures, first tribute r67, recaptures 15-69 rounds late | +9 captures (about 300 gems) in 600 rounds |
| Fights at a contested group (gemcombat4) | Killed 4 of ours at g3 and the altar by r373, two carrying 28 each | 2 kills before r415 | 56 gems lost; about 250 dead champion-rounds in r204-433 |

**Where ours was superior.**
- **Farming through strong-camp and walled maps:**
  - 01corridors: 23 clears to 0, and 10 deaths to their 104.
  - 02the_pond: 52 clears to 23, 6,436-4,340 gold, first tribute r66 to r205.
  - 02gift_wrapping: 1 capture to 0.
- **Not walking into camps.** We had 4, 0, 0, 0 and 9 camp deaths per game, against their 5, 5, 0, 0 and 103.

**What in our code causes the gaps.** All references are `bots/q24_combo/src/bot.py` line / `bots/c2_respawn/src/bot.py` line.
1. **No boss farming.** In `choose_target` (l.1371 / 1390), a group that fails `dmg <= hp - 150` goes to hit-and-run with `budget = maxhp - s*dmg_mult*(G.rng+1) - 80` (l.1406 / 1425), and `if budget <= 0: continue`.
   - A Monolith has s = 200 and rng = 5, so the budget is `maxhp - 1280`. That is negative for every one of our champions until it has about 1,300 max HP. Even with 2,000 HP the cycle count (20,000 HP / per-cycle damage) is far above the cap of 4 (l.1411 / 1430).
   - There is no team commit: a claim only adds 55 dps per ally that already targets the group, and nobody ever targets it first.
   - Result: we never cleared or captured a Monolith on 00contest.
2. **Lone farmers on an open map.** Each champion picks its own target, and claims discount groups that are already taken (×0.3 when solo-safe, l.1422-1428 / 1441-1447). So the team spreads one per gold group.
   - `handle_enemies` (l.1960 / 1979) only reacts once an enemy is within 6 (`near`). `group_balance` (l.1917 / 1936) then counts allies within 7, and with none there `dis` makes us retreat toward the spawn, which a dashing Vendetta catches.
   - Nothing makes farmers pair up after an ally is ganked.
3. **Lock use is opportunistic.** `try_lock` (l.2279 / 2298) places a lock only if *this* champion is already within 2 of an altar where it sees a channel, or proactively at `lock_side` altars it passes.
   - Nothing sends a champion to an altar where a 20-turn, 200-gem channel is running. Champions that see it only through their ward (`far_enemies`, beyond `ENEMY_SIGHT` = 8, l.47) ignore it.
4. **Chip mode ends at our first tribute** (l.2450-2457 / 2515-2522). After it ends, champions that no group satisfies idle for the rest of the game (02gift_wrapping, r365-2000).
5. **Death memory is per champion.** `self.died_at[self.target.idx] = rnd` in `play_turn` (l.2437-2438 / v4's `play_turn_main`) gives `DEATH_PENALTY` 0.3 for 250 rounds only to the champion that died.
   - Allies have no memory of a deadly contested group and walk into it one after another (gemcombat4 g3: Marcella r129, Ryth r204, Vendetta r210).
6. **Target 2-cycle on a corridor map** (Vesper, 01corridors r0-961). This is the claim-rule cycle already filed as Q30 / h_bigmap (claim fix plus cycle guard).

**Lessons.**
- Map structures where this opponent scores 1,000 and we score 0 (boss-only maps) are guaranteed losses until we have some form of boss or bag contest.
- On open cluster maps, small differences decide the race: recapture timing and losing a contested group's fights 4-0.

## 4. Our weaknesses exposed and testable hypotheses
| # | Weakness | Evidence | Impact | Code responsible (v3 / v4 lines) | Testable hypothesis (structure-keyed) |
|---|---|---|---|---|---|
| W1 | We never farm or contest a boss camp (Monolith: s=200, rng 5) | 00contest: 0 gems in 1,412 rounds; theirs 5 x 200 (g1 4x, g0 1x) | **decisive** (1 game) | `choose_target` hit-and-run budget `maxhp - s*(rng+1) - 80 <= 0` (l.1406 / 1425), cycle cap 4 (l.1411 / 1430); no team commit | **H1 "contest the delivery":** an enemy boss capture is visible (the boss group reads Respawning while an enemy carries 100+ gems), or an enemy channel of 50+ gems is seen at an altar, including through our own ward. Every ally whose path to that altar fits within the remaining channel turns goes there to lock (a lock cancels the channel), stun, or kill the carrier. Complements V3L-3b (big-bag hunt) without a boss commit. **Test:** on boss maps vs a boss-farming imitation, count enemy 50+ gem tributes completed vs interrupted, and gems stolen. |
| W2 | Lone farmers ganked in our own half by Power-built melee | 00contest r193-605: 12 deaths in our half (Vendetta 8/1, Ren 7/1); gold 726-1,480 at r250 | **major** (snowballed items: 5 vs 15 emblems at r500) | Claims spread the team one per group (l.1422-1428 / 1441-1447); `handle_enemies` only reacts at d ≤ 6 (l.1976 / 1995); `dis` retreats toward the spawn | **H2 "buddy after a gank":** after an ally is killed by an enemy champion in our half, champions farming within 12 of that spot pair up for 150 rounds (choose a group within 4 of an ally, or follow the nearest ally's claim). Alternatively, retreat at d ≤ 8 when a single visible enemy has a higher hp×dps product than ours. **Test:** own-half deaths to champions per game and r500 gold vs an invader imitation (Vendetta + Ren Power builds). |
| W3 | Allies repeat a death at the same contested group | gemcombat4: Marcella r129 (3,28), Ryth r204 (3,28), Vendetta r210 (1,31), Vesper r532 (1,33), all at their mid g3 (2,33) | **major** in gemcombat4 | `died_at` is per champion (`play_turn`, l.2437 / v4 `play_turn_main`); `DEATH_PENALTY` applies only to the champion that died (l.1431 / 1450) | **H3 "team danger memory":** publish (group id, round) in a free shared-memory byte when a champion is killed by an enemy *champion* while targeting a group. Every ally applies `DEATH_PENALTY` to that group for N rounds. **Test:** repeat deaths per group per 250 rounds, and the gem race at r500 on cluster maps with a contested mid group. |
| W4 | The solo safety model leaves strong-camp groups untouched even against an empty opponent | 01corridors: 23 clears in 2,000 rounds vs a team that cleared 0. Elk x4 g8 (60g), Elk x2 g10 and the Monolith field g0 were never touched. 58 gems destroyed by the Elk pair g1 at r1752-1755 | major (it cost us nothing here, but the same groups decide other sets) | `choose_target` solo model (l.1394-1415 / 1413-1434) | Covered by H5 in the Team Torsk and Sneaky Bush Campers notes (value-scaled cycle cap; strong-camp-first exposure). |
| W5 | Chip mode ends at our first tribute, so we idle for 1,600 rounds | 02gift_wrapping: one capture at r359, then 9,808 quiet champion-rounds | major vs any opponent that farms (v1/v2 lost this map 0-1028 and 16-1006) | `play_turn` stall check sets `self.chip = False` at the first tribute (l.2455-2457 / 2520-2522) | Existing queue item "universal idle chip mode", and c4's idle-fallback team clear. **New evidence:** 9,808 idle champion-rounds after one capture. **Test:** clears per game on maps where no group passes the solo model. |
| W6 | Long target 2-cycle (no attack for 961 rounds) | 01corridors: Vesper 0 gold, 0 gems, ward loop (10,10-17) ↔ (36-40,3-18) every ~150 rounds | minor here (won), major in principle | claim-rule cycle in `choose_target` (Q30) | Existing h_bigmap claim fix and cycle guard (c4). Add this game as a regression case: it is a corridor map with 12 groups in one row. |
| W7 | Recaptures of 0-Strength cluster groups are late | gemcombat4: our 2nd captures came 35, 15 and 69 rounds after respawn; theirs 7-8 | major (−91 by r250) | Bank and walk-away pattern; *speculation:* champions bank or retarget instead of being back at `G.ready` | **H4 "respawn timing":** for 0-Strength groups with status 2, plan the bank trip so the champion is back at `G.ready`. Bank immediately if the round trip to the altar is shorter than the respawn timer left; otherwise wait at the group. **Test:** mean lateness of recaptures after respawn on cluster maps. |

**Their weaknesses to exploit.**
- **They do not function on maps whose paths run through strong camps:** 103 camp deaths and 0 clears on 01corridors, 0 clears on 02gift_wrapping. On such maps, any steady farming beats them; our job is to not idle (W5).
- **No locks, ever.** Our banking at their altar is never blocked.
- **Their Cassi and Issac die cheaply, to camps and to our burst** (two double kills on 00contest at r671 and r1170). A linked death is 2 bodies for one kill.
- **Opening fuel suspensions in every game** (r1-7): they lose the first rounds of the opening.
- **Bosses are delivered in 200-gem, 20-turn channels at a central altar.** That is the softest target in the game, if we route to it (H1).
