# Velvet Pathfinders (1500): ladder set f9a7ff0e, 1 Nov 2026, our v3, won 4-1

- **Opponent:** Velvet Pathfinders, rating 1500 (ours after the set: 1520).
- **Our version:** website v3 = `bots/q24_combo` (live 01:42-04:42 UTC). The set ran at 04:22 UTC. We were side B (team B) in all 5 games.
- **Record: 4-1.**
  - W 01starfish 1059-4 (r1931, gems).
  - **L 02crossing 519-1015** (r1139, gems).
  - W 00breadcrumbs 966-784 (r2000, tiebreak on gems).
  - W 00great_wall 1017-628 (r1740, gems).
  - W 00ribs 901-327 (r2000, tiebreak on gems).
- **Link:** https://2026a.battlecode.co.uk/game/match-groups/f9a7ff0e-259c-423a-a511-5938e5ef3caf
- **Sources:**
  - `matches/ladder/summary/<id>__B.json` for game ids 1376369e, 63a5ae4c, 82804d81, 508f91f7 and 4ad453ae.
  - `python3.12 -I tools/scout.py --group f9a7ff0e` gives every number marked "scout".
- **Method:** as in the e317decf report.
  - Positions come from ward trails (our `try_ward` places a ward within 2 tiles of the champion, and only after it moves more than 6 tiles from the last one) and from event tiles.
  - *Speculation* marks inference.

## Set summary (scout)
| Map (size, picks) | Result | Gems r250 | r500 | r1000 | End | Clears/100r us-them | K/D us | K/D them | Gems lost us/them | Mean tribute us/them |
|---|---|---|---|---|---|---|---|---|---|---|
| 01starfish (50x50, 5) | W | 44-0 | 62-4 | 268-4 | 1059-4 r1931 | 2.18-1.24 | 43/17 | 12/71 | 112/171 | 26.5/4 |
| 02crossing (51x51, 5) | **L** | 122-156 | 315-364 | 451-901 | 519-1015 r1139 | 2.81-7.99 | 8/16 | 13/11 | 222/0 | 27.3/13.4 |
| 00breadcrumbs (29x29, 3) | W (tiebreak) | 77-126 | 77-427 | 245-637 | 966-784 r2000 | 10.5-8.4 | 22/13 | 13/32 | 168/189 | 22.0/9.0 |
| 00great_wall (50x40, 5) | W | 34-0 | 141-0 | 428-247 | 1017-628 r1740 | 3.62-4.71 | 6/4 | 3/18 | 79/528 | 32.8/62.8 |
| 00ribs (51x85, 5) | W (tiebreak) | 0-57 | 43-157 | 315-178 | 901-327 r2000 | 2.45-0.70 | 33/9 | 9/43 | 43/29 | 23.7/21.8 |

Gems lost are carried gems lost on death, to champions and camps. Their camp deaths: 20 on starfish and 11 on great_wall.

## 1. Opponent profile

### Draft and roles
**Draft, identical everywhere:** Varg, Stellar, Cassi & Issac, Tavi, Ren on all four 5-pick maps (6 bodies). On 3-pick breadcrumbs: Cassi & Issac, Stellar, Ren (4 bodies against our 3).

| Champion | Role |
|---|---|
| **Stellar** | Ranged burst (2xF single target and 1.4xF AoE, range 4). **Their carrier hunter:**<br>• crossing: 5 kills, collected 124 of its 182 gems from kills;<br>• breadcrumbs: 6 kills, 98 gems from kills.<br>Its kills land on carriers in its own half. |
| **Cassi (+Issac)** | Ranged damage + stun; Issac is a melee extra body. Cassi was the second killer: crossing 3, breadcrumbs 6. |
| **Tavi / Ren** | Stun casters. On crossing Tavi was also their top clearer (25 clears); Ren made 20 tributes. |
| **Varg** | Splash farmer and tank (shield 17,000-26,000 a game). The usual camp-death victim while carrying: great_wall 158 gems lost, 3 camp deaths. |

### Items: Power shards plus Durability, low spend
- **Order:** Power shards of the main stat first (Focus for Stellar, Tavi, Ren and Cassi; Strength for Varg and Issac), then Durability H, then more Power. No Jungle, Monster, Treasure or Bruiser.
- **First buys:** crossing Tavi PowF r69 and Varg PowS r116; starfish Ren r111 and Varg r120; ribs Cassi DurH r102.
- **Low spend.** Total gold earned: 2,440 (starfish), 2,750 (crossing), 1,300 (breadcrumbs), 3,220 (great_wall), 1,390 (ribs).
  - On breadcrumbs **all 1,300 gold came from kills**: they never capture gold clusters.
  - Emblems by r1000: 5, 10, 3, 7, 1. Ours: 20, 12, 11, 13, 10.
- **Wards and locks.** 21-174 wards a game, almost all in bushes (109/109 on crossing, 172/172 on breadcrumbs). Locks: crossing 9 bought / about 4 placed, first bought r116; 0-3 placed elsewhere.

### Farming: gem clusters only, at the altar and on our side
- **crossing: 91 clears to our 32.**
  - The four single clusters around the centre altar (25,25) were theirs 34 times: g18 (25,23), g19 (25,27), g20 (23,25), g21 (27,25), 2 tiles from it. Plus their own side (48 captures).
  - 8 clears per 100 rounds through r1000.
- **breadcrumbs: 15.3 clears per 100 rounds before r300**, to our 7.0.
  - The inner clusters on **our** side of the single altar (14,14) were theirs: g0, g2, g4, g10 and g12 were captured 11, 10, 9, 12 and 10 times by them, and 6, 3, 4, 2 and 2 by us.
  - Their first captures came at r33-43. 62 of their 115 captures (434 gems) were on our side.
- **great_wall:** their own half (60 of 83 captures) plus 23 on our side.
- **starfish (24 clears) and ribs (14): almost nothing.** Their champions kept dying.

### Tributes: tiny bags at very high cadence, when the altar is reachable
- **Altar reachable:**
  - crossing: 76 tributes, 13.4 mean, median 7, **first at r31**, median gap 9 rounds;
  - breadcrumbs: 87 tributes, 9.0 mean, first r35, median gap 7;
  - ribs: 15 tributes of 21.8, first r120.
- **Altar inside or next to camp ranges, the bot breaks down:**
  - **starfish:** the altars (23,17) and (26,17) sit inside g15's 6-elk ring. **1 tribute (4 gems) in 1,931 rounds**; 20 champion deaths to camps; 171 carried gems lost.
  - **great_wall:** the altars (17-32, 19-20) are flanked by the two 414-gem monolith groups g0 and g1. First tribute at r861 and only 10 tributes (62.8 mean). **303 gems lost to camps:**
    - Varg 56 at (21,8) r276;
    - Cassi 63 and Issac 37 at r410;
    - Cassi 52 and Issac 43 at (29-37,23) r835, inside monolith g1's range 5;
    - Tavi at (34,19) r864, right after its first tribute.

### Fight behaviour
- **They pick off our lone carriers in their own half, with ranged burst and stun.**
  - crossing: 7 of our 16 deaths were in our enemy half. Our big bags fell to Stellar: 49 gems (r655), 25 (r851) and 50 (r1065).
  - breadcrumbs: Vesper 21 at (10,23) r404 and Marcella 21 at (8,22) r414, both near their spawn.
- **They lose grouped fights badly.**
  - starfish: 17 kills, 71 deaths, 10 of them near their own spawn (spawn-camped).
  - ribs: 9 kills, 43 deaths; great_wall: 3 kills, 18 deaths.
  - Across the set we won 38 of the 42 fights that had 2 or more deaths.
- **No altar contesting.** No spawn camping. Locks are used only on crossing.

### Adaptation
**None.** Same draft, same Power/Durability build, same tiny-bag tributes on every map.
- Their altar pathing does not treat camp ranges as obstacles, so on guarded-altar maps they walk carriers into elks and monoliths.
- They are strong only where the altar is open and surrounded by single clusters: crossing, and breadcrumbs until r1000.

### Their weaknesses (observed)
1. **Camp deaths with gems.** starfish: 20 camp deaths, 53 gems lost to camps. great_wall: 11 camp deaths, 303 gems.
2. **Almost no gold:** never captures gold clusters, about 1,300-3,200 earned per game. Their items fall behind from about r500, and from then on they lose every fight.
3. **Spawn-campable** (starfish: 10 deaths near their own spawn).
4. **Fuel:** 6-21 `fuelExhausted` per game after r1.

## 2. Per game

### 01starfish: W 1059-4 (r1931)
- **Their altar access failed.** The altars sit inside the 6-elk g15. Their carriers died to the ring: 8 deaths in the altar zone to camps, 12 more camp deaths in their own half. **1 tribute.**
- **We were steady.**
  - Early: 44-0 at r250 and 62-4 at r500.
  - Then the big groups as a team: g15 (118 gems) three times (r1030, r1758, r1896), and the Elk x2 + 3-cluster groups g2/g3 (51 each) six times from r794. That is 708 gems from 9 captures.
  - Fights: 14 of 16 multi-death fights won. Vesper went 16-4 and Vendetta 11-4.
  - We spawn-camped them at (7,7) at r1079 and (8,5) at r1569.
- **Our cost:** 5 camp deaths, 19 gems lost to camps. HoR was fed 6/1.
- **Root:** their bot cannot tribute at camp-guarded altars; our grouped fights and items (75 emblem completions vs 13) did the rest.

### 02crossing: L 519-1015 (r1139); the loss
**Map.** 51x51, rot180. Spawns: theirs (5-7, 23-25), ours (43-45, 25-27).
- **Altars:** (25,2), (25,25) and (25,48), all "mid".
- **Around the centre altar:** four single clusters g18-g21.
- **Elk + 5 clusters (50 gems):** g0 (26,16) and g1 (24,34).
- Diagonal wall lines split each half.

**Phase 1, r0-500: even.**
- **r43:** all five of ours captured g0 (50).
- **r66-69:** we killed Cassi & Issac and Stellar at (14-15, 27-30).
- **r87:** HoR died at (16,31) to Varg, carrying 10.
- We banked 9 times at (25,25) by r423: 206 gems. **315-364 at r500.**

**Phase 2, r424-804: the collapse.**
- **We made 0 tributes in 380 rounds.** They made 31 (455 gems), **27 of them at the centre altar (25,25)**.
- **Our carriers in that window:**
  - **Vesper:** carried 49 from r606 (g3 at (45,46), 43 gems). It did not bank at (25,48), about 8-20 tiles away.
    - Wards: (33,46) r616, (23,37) r626, (16,33) r636. Killed at (19,31) r655 by Stellar, deep in their half.
  - **HoR:** carried 25 from r720 (g0). Wards: (23,23) r743, (18,14) r753, (14,23) r796, (14,32) r806, (23,23) r838.
    - It was within about 2 tiles of (25,25) twice and never tributed. Killed at (29,21) r851 by Stellar.
  - **HoR and Vendetta** died to camps at (30,12) at r466 and r487, losing 7 and 11.
- **After r804:**
  - We banked only at (25,48): Ryth 25 at r805, Vesper 57 at r872, Marcella 54 at r986, Marcella 50 at r1107.
  - Ryth carried 50 from g1 (r1009) and died at (15,35) to Stellar at r1065.
- **Most likely cause** *(speculation, but every observation fits)*: from about r424 the centre altar was enemy-locked. They placed about 4 locks; first bought r116.
  - `pick_altar` and `locked_altars` then skip (25,25) for us.
  - `break_lock` only hits a lock from an adjacent tile, and only when no free altar is within 8.
  - `do_tribute` then sends carriers to the free outer altars along paths through contested ground.
  - The alternative, `handle_enemies` retreat loops near the busy altar, would also explain HoR's (23,23) visits.
- **Totals.**
  - Gems lost to champions: 192 (Stellar collected 124 of them), plus 30 to camps.
  - Clears: 32 to their 91. Captures on their side: 9 to their 11.

**Root.** Losing access to the central altar. Our carriers then made long trips through Stellar's half, and their cluster farming at 8 clears per 100 rounds ran away: 901-451 at r1000.

### 00breadcrumbs: W 966-784 (r2000 tiebreak, on gems)
**Map.** 29x29, 3 picks: our 3 bodies against their 4. One altar, (14,14). 22 single gem clusters across the middle, plus a column of 6 gold clusters next to each spawn: ours g23-g33 at x=26, theirs at x=2.

**r0-1000: they led** (126-77 at r250, 427-77 at r500, 637-245 at r1000).
- **Our captures, r0-1000:**
  - 54 of 98 were 0-gem gold clusters (g23-g31, each taken 18-22 times all game);
  - we made **0 tributes in r250-500**, while they made 32;
  - our early carrier deaths: r331 Vendetta 14 (at our spawn edge), r404 Vesper 21 at (10,23) and r414 Marcella 21 at (8,22), both near their spawn, by Stellar and Cassi.
- **Their side of it:** their bot farmed the inner clusters on both sides of the altar from r33 and tributed 9-gem bags every 7 rounds.

**r1000-2000: we won 721-147 on tributes.**
- The gold went into items: 11 emblems vs 3 at r1000, 36 Bruiser emblems by the end.
- Fights flipped: we killed 16 and lost 6 after r1000. Marcella went 10-0, killing 4 enemy bodies in each of two fights, r1089-1102 and r1181-1196.
- Their clears fell to 5.0 per 100 rounds, and ours rose to 12.5.

**Root.**
- Early: their gem-only cluster farming beat our gold-weighted target choice (`value = gems + 0.25*gold` makes a gold cluster next to spawn outscore a gem cluster 8-13 away).
- Late: the same gold bought the item lead that won every fight.
- A narrow tiebreak win (966 vs 784) against a 4-body team with no gold income.

### 00great_wall: W 1017-628 (r1740)
- **We banked steadily** at (17,19): 29 tributes of about 33, first r194. 141-0 at r500, 428-247 at r1000.
- **They self-destructed on camps.**
  - 303 gems lost to camps; 11 camp deaths, mostly at their own Elk x3 group g5 (21,8) and around monolith g1 (30,20).
  - First tribute r861.
- **Our losses:** our 4 deaths cost 79 gems. Vendetta died at (9,27) to a camp with 29 at r1380.
- **Carrier kills, ours:** Vendetta took Ren's 60 at r557; Ryth took Varg's 80 at r1141 and banked it at r1166; HoR took Issac's 55 at r1556.
- **Root:** their altar route goes through camp ranges. We were steady and safe.

### 00ribs: W 901-327 (r2000 tiebreak)
**Map.** 51x85. Spawns at the bottom corners, (3-5, 3-5) and (45-47, 3-5). All gems are at the top, 64-72 tiles away: the altars (22,71) and (28,71) with three groups next to them, g0 (GemCl x2), g1 and g2 (Elk + 4 clusters, 43 gems each). The rest is single gold clusters.

**r0-386: no clears for 309 rounds.**
- Every champion made 2-3 round trips spawn → (18-29, 58-74) → spawn. Vesper's trail:
  - r1 (45,1) → r72 (23,64), then died r74 (Cassi);
  - r135 (45,1) → r219 (22,69) → r263 (45,1);
  - r335 (18,62) → r350 (45,1).
- Our champions died one at a time at the top: Vesper r74 at (24,64), Ryth r148 at (23,63), HoR r210 at (18,74). The others recalled.
- Meanwhile Varg and Tavi took g2 at r115 (43) and tributed at r120. **0-57 at r250, 43-157 at r500.**

**From r387: we farmed the altar groups.** g0 7 times, g1 9 times, g2 10 times, and we won fights 33-9 (HoR 12-1). **315-178 at r1000.**

**Root.** We won through fights and items once we were established. But the opening cost about 300 rounds: one-by-one arrival into their group at the far objective, then recall-heal round trips of about 130 rounds each.

## 3. Their strategy vs ours

### Where theirs was superior
| Gap | Size | What in our code causes it (`bots/q24_combo/src/bot.py`) |
|---|---|---|
| **A. Holding the central altar, and our response to losing it.** | crossing: 0 tributes from us in r424-804 against their 31; 3 carriers (49, 25, 50 gems) killed on detours. | **`pick_altar` skips altars in `locked_altars()`** (`LOCK_MEMORY_FIX`).<br>**`do_tribute` does not break the lock.** It calls `break_lock(me, locked, not reach_free)`, which returns False when a free altar is within 8 or when no lock is in `me.attack_tiles()`. It never walks to the lock. Then `ring = free` sends the carrier to the outer altars.<br>**Routes ignore danger.** Path cost has no enemy-half or danger term except `ALTAR_DANGER_PEN` at the destination. *(The lock is inferred, not observed: see §2.)* |
| **B. Cluster tempo and tiny-bag banking on open single-altar maps.** | breadcrumbs: 0 vs 32 tributes in r250-500; 427-77 at r500. crossing: 8 vs 2.8 clears per 100 rounds. | **Gold weight.** `Group.value = gems + 0.25*gold` makes a 20-gold cluster at distance 1-5 (value 5, cost about 9) outscore a 7-gem cluster at 8-13 (cost about 16-21).<br>**Banking thresholds.** `BANK_CLOSE = 5` within `BANK_CLOSE_D = 4`, `BANK_NEAR = 15` within 15. Our banks are 2-3 times their bag size, which is fine, but combined with the gold detour our gems come in later. |
| **C. Ranged carrier picks in their half.** | crossing: Stellar 5 kills, 124 gems. breadcrumbs: r404 and r414, 42 gems. | **Nothing in the farm or bank routing avoids enemy-half tiles.** `choose_target` scores value/time only; `DEATH_PENALTY` applies only after we died at that same group.<br>**No memory of where carriers die.** `handle_enemies` reacts only to enemies visible this turn (`near` ≤ 6, `threat` within `attack_range + 2`), and `threatened()` only halves the bank thresholds. A carrier whose route crosses a zone where a ranged burster killed an ally 30 rounds earlier walks the same route again. |
| **D. Opening on far-objective maps.** | ribs: first clear r309; 0-57, then 43-157. | **`play_turn` recalls to heal at `low = hp < 0.45*maxhp`** (or walks home), then waits on spawn to 92%. With spawn 64-72 tiles from every gem group, each heal trip costs about 130 rounds.<br>**Champions arrive and fight one by one.** `group_balance` only counts allies within 7. |

### Where ours was superior
- **Grouped fighting and items.** In 3 of 5 games we won 14/16, 11/12 and 11/12 of the multi-death fights.
  - Bruiser emblems by the end: 75, 36, 34 and 37, against their 6-17.
  - The q24 `group_balance` commit rule plus `focus_bias` channel and carrier targeting (Vesper 16 kills on starfish; Marcella 19 on breadcrumbs; HoR 12 on ribs).
- **Camp safety.** We lost 19 / 30 / 0 / 29 / 0 gems to camps, against their 53 / 0 / 0 / 303 / 0.
  - The `choose_target` chip and escape model, plus the "never die to camps" danger retreat, keep us alive near guarded altars, where their carriers die.
- **Gold economy:** 12,100 vs 2,440 (starfish), 5,780 vs 1,300 (breadcrumbs). It is what turned breadcrumbs.

## 4. Our weaknesses exposed
| # | Weakness | Evidence | Games | Impact |
|---|---|---|---|---|
| W1 | **No answer to losing the nearest altar** (likely enemy-locked). `break_lock` never approaches a lock, and carriers detour to far altars through enemy ground. | crossing: 0 tributes r424-804 (31 by them); HoR 25 gems within about 2 of (25,25) at r743 and r838 with no tribute; Vesper 49, HoR 25, Ryth 50 killed by Stellar on the detours. | 1 (gem_fields in e317decf shows the same bypass) | decisive |
| W2 | **Carriers path through the enemy half, with no memory of where carriers were killed.** | crossing: 7 of 16 deaths in our enemy half, 192 gems lost to champions. breadcrumbs: r404 and r414, 42 gems at their spawn. | 2 | major |
| W3 | **Early gold-cluster farming while the enemy farms the gem clusters on our side.** | breadcrumbs: our inner clusters g0, g2, g4, g10 and g12 were captured 52 times by them, 17 by us. 54 of our 98 captures by r1000 were 0-gem; 0 tributes in r250-500. | 1 | major (nearly lost; tiebreak win) |
| W4 | **Recall-heal round trips and one-by-one arrival on maps where the objective is far from spawn.** | ribs: first clear r309; 3 solo deaths at (18-24, 63-74), r74-210; trips of about 130 rounds. | 1 | major (early deficit; won late) |
| W5 | **Not reaching 1,000 against a weak opponent.** | breadcrumbs 966, ribs 901 at r2000. Both wins went to the tiebreak. | 2 | minor (rating risk) |

## Testable hypotheses (structure-keyed; no map or team names)
1. **H-lockbreak (W1).**
   - **Change.** If the nearest usable altar by path is in `locked_altars()` and the nearest free one is at least 10 path steps farther, walk to a tile adjacent to the locked altar and attack the lock. `ALTAR_LOCK_HITS = 5`; a melee champion with an attack reset needs about 3 turns.
     - Only if `group_balance` near ≥ 1.0 or no enemy is within 8.
     - Otherwise wait at the staging ring (8-10 from the altar) for an ally.
   - **Implementation.** `do_tribute`: replace the `free_d <= 8` early-out with the path-difference test, and add `step_toward(adjacent-to-lock)` when not adjacent.
   - **Metrics.**
     - Rounds between our last and next tribute at a contested altar (crossing-like gaps of 380 should vanish).
     - Gems lost to champions on detours.
   - **Validate** against a lock-placing imitation (`imit_*` with proactive locks) as well as self-play.
2. **H-saferoute (W2).**
   - **Change.** For carriers with ≥ 15 gems, add a per-tile penalty for enemy-half tiles (scout's side margin: nearer the enemy spawn by `max(3, 10%)`) when choosing the altar, i.e. `pick_altar` distance + 0.5 × enemy-half path length.
   - **Memory.** Keep a per-tile-region "carrier killed here" stamp for 150 rounds (our own deaths with ≥ 15 gems, read in `play_turn` when `was_dead` flips) and add it to the same route penalty.
   - **Metrics.** Gems lost to champion kills per game; deaths in the enemy half.
3. **H-gemfirst (W3; complements EFW/e317decf H-goldcap).**
   - **Change.** If a gem cluster group on our side (nearer our spawn) was observed respawning without our capture (status → 2 while no ally claim) twice within 200 rounds, the enemy is farming it. Multiply its score by 1.5 and the score of 0-gem groups within 15 of our spawn by 0.5, for 300 rounds.
   - **Metrics.** Own-side gem captures, ours vs theirs; tributes before r500; gold at r1000 (must not collapse, because the late item lead won the game).
4. **H-farheal (W4).**
   - **Change.** If the path from the current tile to spawn is above 40 steps:
     - lower the recall-heal threshold from 0.45 to 0.30;
     - restrict targets to zero-strength groups and those with `dmg_solo <= hp - 150` while below 0.6;
     - leave spawn as a group: wait on spawn until 2 or more allies are healed (only at game start and after a team wipe).
   - **Metrics.** Round of first clear and first tribute on maps with spawn-to-altar ≥ 50; deaths before r300.
5. **H-closeout (W5).**
   - **Change.** After r1200, if our tributed + carried ≥ 800 and the enemy is ≥ 150 behind, lower `BANK_ANY` to 15. More frequent banks convert carried gems to the 1,000 finish instead of r2000.
   - **Metric.** Share of wins ending by tiebreak (currently 2/4 here).

**Opponent-specific notes (for ladder expectations).**
- Velvet Pathfinders beats us only on open, single-cluster-ring altar maps, by out-tempoing us early.
- It collapses on maps with guarded altars.
- Expect wins unless the central altar is lost (W1).
