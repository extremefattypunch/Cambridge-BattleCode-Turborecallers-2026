# Turbo Altar Keepers (1537): ladder set 1649b879, 1 Nov 2026, our v3, lost 2-3

- **Opponent:** Turbo Altar Keepers, rating 1537 (ours after the set: 1529).
- **Our version:** website v3 = `bots/q24_combo` (live 01:42-04:42 UTC). The set ran at 03:02 UTC. We were side A (team A) in all 5 games.
- **Record: 2-3.**
  - **W 02crossing 1009-587** (r1118, gems).
  - **L 00great_wall 180-1003** (r1399, gems).
  - **L 02arena 95-1007** (r1748, gems).
  - **W 00the_line 1030-120** (r1941, gems).
  - **L 01yellow_brick_road 197-1011** (r1378, gems).
- **Link:** https://2026a.battlecode.co.uk/game/match-groups/1649b879-bd1e-46e4-bb36-0025ea745697
- **Sources:**
  - `results/ladder-games.jsonl` rows and `matches/ladder/summary/<id>__A.json`.
  - `python3.12 -I tools/scout.py --group 1649b879`, the fixed per-game profile; its definitions are in the module docstring.
  - Session scripts in the scratchpad, not the repo:
    - `ganks.py`: killer + assisters and carried gems per death;
    - `mirror.py`: captures on mirror-image groups;
    - `party.py`: champions per capture;
    - `tl.py`/`ts.py`: event and timeline dumps;
    - `mapart.py`: ASCII map from the .map26a decode.
- **Method:** the stats file has no per-round positions. Positions come from events (kills/deaths are the victim's tile, captures, tributes at the altar tile, shop tiles) and from ward placements, which land within 2 of the placer. Anything not directly observed is marked *speculation*. Our live bot prints nothing, so replays add nothing beyond the stats.

## Game summary
Team A spawns are west/north in every game. Map sizes: 30x30 (arena), 33x33 (the line), 40x30 (yellow brick road), 50x40 (great wall), 51x51 (crossing). Gem race = tributed gems, us-them.

| Map (size, picks) | Result | r250 | r500 | r1000 | End | Clears /100r us-them | K/D us | Gold end us-them |
|---|---|---|---|---|---|---|---|---|
| 02crossing (51x51, 5) | **W** | 80-121 | 247-249 | 841-566 | 1009-587 r1118 | 2.86-5.72 | 29/7 | 5,751-1,717 |
| 00great_wall (50x40, 5) | **L** | 0-150 | 37-315 | 73-651 | 180-1003 r1399 | 3.0-4.0 | 4/17 | 3,206-5,412 |
| 02arena (30x30, 3) | **L** | 65-78 | 80-199 | 80-564 | 95-1007 r1748 | 1.37-5.66 | 3/35 | 1,129-13,112 |
| 00the_line (33x33, 4) | **W** | 0-16 | 0-28 | 169-64 | 1030-120 r1941 | 1.55-1.18 | 32/18 | 5,505-3,793 |
| 01yellow_brick_road (40x30, 5) | **L** | 0-106 | 45-212 | 124-592 | 197-1011 r1378 | 0.8-5.52 | 12/22 | 4,432-16,569 |

## 1. Opponent profile

### Draft and roles
**Draft: fixed order, truncated by the pick count.**
- 5 picks: Vesper Vale, then Varg or Tavi, Marcella, Tavi or Varg, Ryth.
- 4 picks: Vesper, Tavi, Marcella, Ryth.
- 3 picks: Vesper, Tavi, Marcella.

Mirror picks with us: Vesper, Marcella and Ryth. We drafted Vesper, Vendetta, Marcella, HoR, Ryth (`draft.py`).

**Roles (from per-champion lines):**
- **Tavi: the pick-off tool.** Its stun (1.6xF + 1-round stun, r4) sets up kills: 30 kills in 5 games, 14 of them on arena. It is also a solid farmer (arena 260 gems).
- **Vesper: their main farmer and second killer.** Monster damage 93,849 on yellow brick road, the most of any champion in the set. 20 kills in the set; 6/1 on yellow brick road.
- **Marcella: their duellist.** 13/0 on arena, 24 kills in the set.
- **Varg: splash farmer and roamer.** Kills on great wall: HoR at (13,12) r388, Ryth at (13,12) r640, HoR at (5,7) r803, all deep in our half.
- **Ryth: weakest.** 8 kills, 12 deaths.

### Items: Treasure first, a lock with the first purchases, then a fixed loop
| Champion | 1st emblem | Then | Later |
|---|---|---|---|
| Vesper | **Treasure S** (r175 YBR, r235 great wall, r294 the line, r325 arena) | Jungle S, Monster S | Power S, Bruiser S, Durability H, then Treasure again (arena: 39 Treasure shards in total) |
| Tavi | **Treasure S** (r97 YBR, r143 the line, r154 great wall, r289 arena) | Jungle S, Monster S | Power S, Bruiser S, Durability H, Treasure ... |
| Marcella | Treasure S (arena r194, the line r211, crossing r208); Jungle S on great wall and YBR | Monster S | Durability H, Bruiser S, Power S |
| Varg | Jungle S (r166 YBR, r267 great wall); Treasure S on crossing | Monster S, Treasure S | Durability H, Bruiser S, Power S |
| Ryth | Treasure H or Jungle H | Monster S | Durability H, Power H |

- **Altar locks are bought with the first purchases on every champion:** 6-11 bought per game, ~1-7 used. Vesper bought **only a lock** in all of crossing.
- **Emblems by r1000, theirs vs ours:** YBR 67 vs 18; arena 40 vs 4; great wall 17 vs 8. Crossing 9 vs 27 and the line comparable (both wins for us).
- **The Treasure-first plan pays only where groups carry gold.**
  - Crossing is mostly gem clusters (0 gold). Their Vesper earned **26 gold in 1,118 rounds**, and their team gold was 1,717 vs our 5,751.

### Farming pattern
- **Own-half circuit, with 2-4 champions per capture in the opening on lane maps.**
  - YBR <r300: 11 captures, mean party size 2.55, solo only 18%. The groups were g3, g5, g9 and g27, all next to their spawn.
  - From r300, their captures are 70-90% solo.
- **Tempo vs ours.**
  - Clears per 100 rounds: YBR 5.52 vs 0.8; arena 5.66 vs 1.37; crossing 5.72 vs 2.86; great wall 4.0 vs 3.0.
  - **Camp damage taken per 1k dealt:** YBR 163 vs 695; arena 126 vs 424; great wall 205 vs 384; crossing 351 vs 621.
  - Monster damage dealt per 100 rounds: YBR 18,084 vs 2,675; arena 7,131 vs 1,669.
- **They invade our half once ahead.**
  - YBR: 19 captures of our-side groups (340 gems). g12 (18,9) alone was taken 6 times from r708.
  - Arena: 38 enemy-side captures (390 gems).
  - Both cases are after r300.
- **They skip the big zero-strength jackpots.**
  - The line: the 23-cluster, 161-gem row g2 (17,16) was **never** captured by them. We took it 6 times.
  - YBR: the 30-cluster gold "roads" g0/g1 were taken only opportunistically, on clears we had paid for (see §2).

### Tribute behaviour: tiny, constant banking at the nearest altar
- Tributes per game and mean size:
  - arena **94 x 10.7**;
  - YBR **95 x 10.6**;
  - crossing 54 x 10.9;
  - the line **31 x 3.9**;
  - great wall 46 x 21.8.
- First tribute: r24 (arena), r32 (crossing), r52 (the line), r60 (YBR), r112 (great wall).
- They also tribute the bags they steal at once: great wall r153 Tavi killed Ryth carrying 36 at (1,17) and tributed 36 at (17,19) at r172.

### Fight behaviour: altar keeping, carrier hunting, edge ganks
- **Wards concentrate on altars:**
  - the line 119 of 299 at the single altar (3,16);
  - YBR 194 of 450.
- **The line, r540-700.** Ward trail around (0-6, 12-17), the ring of altar (3,16):
  - their Ryth, Tavi, Marcella and Vesper placed 14 wards there;
  - meanwhile they tributed 4 gems every ~60 rounds;
  - our two carriers (HoR 80, Vendetta 89 gems) could not bank for 172 rounds.
- **Great wall: they kill our carriers on the altar route** (detail in §2). 8 carrier kills, 232 gems taken, at the edge corridors (1,17), (47,16) and (48,17), and at the bush gap (13,12).
- **Arena: duels and small ganks at our corners and edges.**
  - 19 of our 34 champion deaths were 1-vs-1 kills (killer, no assist) and 12 were 2-vs-1.
  - Death tiles: (0,0), (0,7), (0,11), (12-15,0), (27-29,0-7).
- **They do not dive spawns recklessly, but they chase low-HP champions into them.**
  - The line r667/r676: their Marcella and Vesper died at (14,1) and (14,3), on our spawn edge, chasing our carriers. Those two deaths are what let us bank 169 gems at r706-707.
- **Crossing: they lost the fights.**
  - K/D 7/29. 16 of their deaths were in their own half around (28-35,12-23), 10 of them 1-vs-1.
  - They had 1,618 gold at r1000 (ours 4,689), so they were item-poor.

### Adaptation across maps
None visible: same draft order, same Treasure-first and lock-first shopping, same tiny-bag banking. The outcomes track the map instead:
- **Gold-rich maps** (YBR, arena: wolves/elks with gold clusters): Treasure snowballs. Gold at r500 3,135 vs 1,647 (YBR) and 1,979 vs 696 (arena).
- **Gem-cluster maps** (crossing, the line): they fall behind on items and lose fights.

## 2. Per game

### 02crossing (W 1009-587, r1118)
- **Opening, r0-250 (80-121).**
  - They tributed first (r32) and cleared 14 groups vs our 7.
  - Two early fights: r50/r62, we killed Tavi and Varg at (29,22)/(32,19), Ryth with assists. r112/r134, we lost Marcella (7 gems) and Vendetta (11) at (25,21)/(19,21).
- **Turn: r400-r1105.** Our grouped fights in their half:
  - r400-408 at (31,12)/(25,14): Varg and Marcella;
  - r457-460 at (31-32,12-13): Tavi (11 gems) and Vesper;
  - r478-488: Ryth and Varg;
  - r1015-1035 at (28-37,14-19): 4 kills, 0 losses.
- **Kills in 300-1000: 19 to 1.** Our kill gold reached 3,197 by the end, which bought 27 Bruiser emblems by r1000 against their 9.
- **Root.**
  - Won by fights: K/D 29/7, with 10 solo kills and 10 2-vs-1.
  - Their Treasure-first build earned nothing on a gem-cluster map, so their champions were item-poor.
  - Our captures came from the mirrored 50-gem elk groups:
    - g1 (24,34): 6 captures, first at r38;
    - g0 (26,16): 3;
    - g2/g3, 43 gems at the corners: 4 and 2.
  - **We lost the farming race 2:1 on clears** and still won.

### 00great_wall (L 180-1003, r1399), decided by carrier kills
**Map (decoded).** Our half is y<13; theirs is y>26.
- The four altars (17,19), (17,20), (32,19), (32,20) sit in a sealed central band.
- The band is entered only through 2-wide edge corridors at x=0-1 and x=48-49 (rows 17/22 are holes at x=2-14 and 35-47) or by dashing holes.
- From our farms g3 (10,8), g13 (30,10), g15 (19,0) and g9 (40,1), the walk to an altar is about 35-50 tiles.

**Our carrier deaths (victim tile, carried gems, killer + assists):**

| Round | Champion | Tile | Gems | Killed by |
|---|---|---|---|---|
| r153 | Ryth | (1,17) west corridor | 36 | Tavi (Tavi tributed 36 at r172) |
| r216 | Vendetta | (47,16) east corridor | 28 | Vesper |
| r317 | Vesper | (39,14) | 28 | Tavi |
| r350 | Ryth | (22,8) | 22 | Ryth |
| r388 | HoR | (13,12) bush gap | 29 | Varg |
| r574 | Vendetta | (41,19) | 19 | Vesper |
| r640 | Ryth | (13,12) bush gap | 43 | Varg |
| r686 | Vesper | (48,17) east corridor | 27 | Vesper |

- **Totals.** We lost 378 gems on death (363 to champions); they lost 29.
- **Collected camp gems were close:** 566 vs 697. The race was lost by gems that never reached an altar: only **9 tributes all game**, first at **r253** (theirs: 46, first at r112).
- **Kills:** K/D 4/17. Our deaths by gank size: 4 solo, 7 2-vs-1, 3 3-vs-1, 2 4-vs-1. They move in pairs; our carriers walk alone.
- **Root:** long solo banking trips with 19-43 gems through two predictable chokepoints that the enemy patrols (ward/kill tiles above).

### 02arena (L 95-1007, r1748), 3 picks, a 3-vs-3 duel map
- **Even start.** r250 65-78. We tributed at r64, r71, r122 and r159; their Vesper tributed at r24.
- **r173-288: three 3-vs-1 ganks start the snowball.**
  - r173: their Marcella captured g2 (4,18), the elk group our Vendetta cleared at r157 (a steal).
  - r177: Marcella died at (8,15) to Marcella + Vesper + Tavi.
  - r222: Vesper died at (2,23), carrying 8, to Tavi + Vesper + Marcella.
  - r288: Vendetta died at (1,11), carrying 8, to Tavi + Vesper + Marcella.
- **Gold.** Kill gold plus Treasure: gold at r500 was 1,979 vs 696. By r1000 they had **40 emblems vs our 4**.
- **r300-1748: repeated 1-vs-1 losses at the map edges.**
  - Our champions kept leaving spawn alone to farm the corner clusters: g10 (28,1), g0 (13,2), g11 (2,28) and the gold singles at (1-2,1-2).
  - Deaths at (12-15,0) x6, (27-29,0-7) x7, (0,0-15) x6.
  - **Our Marcella earned 70 gold in 1,748 rounds**, collected 56 gems and died 12 times.
  - Our clears in 300-1000: **4** (0.57/100r) vs their 43.
- **Root.**
  - We lost the first three fights, all outnumbered 3-to-1, while farming alone.
  - Then each champion kept making the same solo corner trips against item-superior duellists: K/D 3/35.
  - They spawn-camped us (9 deaths within 6 of our spawn).

### 00the_line (W 1030-120, r1941)
- **0-28 until r500.**
  - Both teams fought over the four 4-gem wolf groups; their tributes were 4 gems each.
  - We had 5 deaths before r300, including Marcella at (3,7) at r30.
- **r422-534.**
  - Vendetta cleared the 161-gem row g2 at r422 (last hit at (28,16)).
  - The capture completed only at **r534**: Vendetta 81, HoR 80. *Speculation:* enemies near the long row kept resetting it, the same contested-capture standoff as YBR.
- **r534-707: carriers held off the only altar.**
  - Their 3-4 champions warded and held altar (3,16).
  - Our Vendetta reached (4,12) at r600, retreated to spawn (15,1) and shopped at r677.
  - Their Marcella and Vesper chased and died at (14,1) and (14,3) (r667, r676).
  - HoR and Vendetta then banked 80 + 89 at r706-707.
- **Then:** 5 more captures of g2 (857 camp gems after r1000). Kills 21-8 after r1000.
- **Root.** They never contest or take the 161-gem row; we won it 6-0. Their altar-keeping only delayed us, and their chase onto our spawn cost them the guard.

### 01yellow_brick_road (L 197-1011, r1378), decided in the opening by our targeting
**Map (decoded).**
- Spawns: ours (2-5,13-16), theirs (34-37,13-16).
- The lane between them (y 13-16) holds g2/g3 (Wolfx2+GoldClx2, 8 gems) and g4/g5 (Elkx2+GoldClx2, 30 gems).
- The lane is bounded by two 30-tile rows of gold clusters: **g0 (y=17, x=5-34) and g1 (y=12, x=5-34)**. Each is **one group: 600 gold, 0 gems, 0 strength**, and each touches both spawns.

**Opening r0-250 (0-106).**
- **Theirs:** 11 gem captures with 2-4 champions each: g3 (30,14) r47, g9 r68, g27 r97, g3 r142, g5 r168, g9 r191, g3 r240, g5 r263. Small tributes from r60. Gold 1,870 by r250.
- **Ours:** zero gem captures until r307.
  - Team monster damage by r250 was **5,599**; theirs was **38,095**.
  - More than half of ours was Ryth: 2,840 by r150, the HP of about 24 clusters at 120 HP. *Likely road clusters:* Ryth's wards at r53 (13,13) and r63 (17,16) sit next to the rows.
  - **r184:** their Marcella landed the last hit on road g0 at (21,17).
  - **r238:** our Vesper, Marcella, HoR and Ryth finally captured g0 at (5-8,17), 54 rounds later, for 600 gold split 4 ways.
  - **r242:** our Vesper landed the last hit on road g1 at (6,12). **r248:** their Varg, Marcella and Ryth captured it at (27-29,12).
- Our own lane group g2 (8,14), 3 tiles from our spawn, was **never cleared by us**: 2 steal-captures, the first at r891. g4 (12,14) was first captured at r410.

**Mid/late.**
- Our clears per 100 rounds stayed below 0.9 all game.
- Ward trails show champions stalling beside the dead road tiles:
  - Vendetta quiet r455-679, last wards (15,11) r480 and **(10,12)** r558, a g1 tile;
  - Marcella quiet r711-908, ward (7,12);
  - Ryth wards (7,12) r1087 and (12,11) r1300.
- They invaded our north: 19 captures of our-side groups, and tributes at our altars (6,5) 6x and (16,4) 15x.
- Fights there went against us:
  - r596-610 at (18,6): we lost Marcella, Vesper and HoR to their Vesper;
  - r1143-1147 at (15,7): we lost Ryth, Vendetta and Marcella.
- Final gold 4,432 vs 16,569; monster damage 36k vs 249k.

**Root.**
1. The 30-tile gold rows out-score every gem group in `choose_target` (§3 gap A), so 4 champions spent about 240 rounds on 600 gold.
2. Their captures stall on contested long regions, and stepping on dead row tiles triggers the respawn push-back 2-cycle (Q21; **fixed in v4** `c2_respawn`).
3. The enemy took our lane and north groups once ahead.

## 3. Their strategy vs ours

### Where theirs was superior
| Gap | Size | Our code responsible |
|---|---|---|
| **A. We over-value huge zero-strength gold groups** and commit the whole team to them. | YBR: 4 champions, r0-238, for 600 gold. Gem race 0-106 at r250; gold 649 vs 1,870. | `Group.__init__`: `self.value = self.gems + 0.25 * self.gold` (q24 l.246, c2 l.260). A 30-cluster row is worth **150**, more than any gem group on the map (max 45 gems + 75 = 120). `choose_target` scores strength-0 groups as `solo_ok` with `ttk = hl / (dps + c*55)`. Worked from the formula (approximate, d about 10): for Marcella with 2 allies claiming, the row scores about 150/39 x 0.3 = **1.15**. The next-best g2 (8,14), not solo-ok (cycles 2.4, `extra` 73), scores about **0.27**; the 30-gem elk g4 fails the cycle test (cycles about 23 > 4). The claim discount (x0.3 for `solo_ok`, l.1425-1426) cannot overcome a 4x margin, and nothing values capture contestability (a region touching the enemy spawn). |
| **B. Capture standoffs on long regions.** | YBR g0: last hit r184, captured r238 (54 rounds). The line g2: cleared r422, captured r534 (112 rounds). YBR g1: we cleared at r242, they captured at r248. | `play_turn` capture branch `if G.status == 1: if G.tiles.is_set(pos): return` (q24 l.2647-2655, c2 l.2718+) waits indefinitely, while any enemy on the region resets the 5-round timer. There is no abandon or contest rule ("c2 H3 contested-capture standoff", open). |
| **C. Solo carriers on long altar routes.** | Great wall: 8 carrier kills, 232 gems. Gems lost on death 378 vs 29. 9 tributes vs 46. | `bank_now`/`bank_detour` thresholds (BANK_ANY 30; BANK_NEAR 15 within 15 path; halved when `threatened`) mean a 35-50-tile route is walked alone with 19-43 gems. `pick_altar` only adds ALTAR_DANGER_PEN = 12 for enemies seen **within 8 of the altar** in 40 rounds (l.1565-1566). It knows nothing about the route or where allies died. `update_alerts` records only *that* an ally died (`last_ally_death`), not where. The only reaction is halving thresholds, which means *more* trips through the same corridor. |
| **D. Kill snowball from early outnumbered fights**, then 1-vs-1 losses forever. | Arena: deaths 3-vs-1 at r177, r222, r288; then 19 of 34 deaths were 1-vs-1; K/D 3/35; emblems by r1000 4 vs 40. | `handle_enemies` + `group_balance` only react to enemies **in sight** (GROUP_R 7). `choose_target` has no enemy-presence term, and DEATH_PENALTY (x0.3 for 250 rounds) applies only to the *target group* at death. Deaths cluster around the corner groups g10 (28,1) and g0 (13,2), 6-7 each: champions kept returning there, either a different champion or the same one after its 250-round penalty. No rule says "we are out-itemed: farm near spawn or move in pairs". |
| **E. Camp-damage efficiency and item count.** | Camp damage per 1k dealt: YBR 695 vs 163, arena 424 vs 126, great wall 384 vs 205. Emblems by r1000: 18 vs 67 (YBR). | `shop()` -> `bruiser_item()` (BRUISER_PLAN, `JUNGLE_FIRST = False`, l.126). No Jungle or Durability passive ever (T25 rejected; Q28b-d queued). Their Treasure-first + Jungle + Monster gives economy and camp tankiness. |
| **F. They bank tiny bags constantly; locks and wards hold the altar.** | The line: our 80- and 89-gem carriers waited 172 rounds while 3-4 of them warded altar (3,16). | We have no "altar held by >= 2 enemies" plan. `handle_enemies` with >= 30 gems uses FIGHT_ENGAGE_RICH 0.7 and flees at ratio > 1.0 (correct), and `break_lock` exists. But nothing musters allies to escort a big bag. (Here their over-chase rescued us; that is not a plan.) |

### Where ours was superior
- **Grouped fights when we are not item-starved.**
  - Crossing: K/D 29/7; 19 kills to 1 in r300-1000, in their half.
  - The line after r1000: 21-8.
  - `group_balance` (GROUP_ADV 1.4) wins when 2-3 of ours meet 1-2 of theirs.
- **Taking a jackpot they ignore.** The line: the 161-gem row 6 times (first capture r534, then 857 gems after r1000). They never touched it.
- **Spawn defence.** The line r667/r676: chasers died on our spawn edge (spawn healing).
- **Gold on gem-cluster maps.** Crossing gold 5,751 vs 1,717, mostly from kills (3,197).

## 4. Our weaknesses exposed
| # | Weakness | Evidence | Games | Impact |
|---|---|---|---|---|
| W1 | **Huge gold-only groups dominate targeting**: value 0.25 x gold with no cap and no contestability term. | YBR: 4 champions r0-238 on 30-cluster rows (600 gold); first gem capture r307; 0-106 at r250; home group g2 never cleared by us. | 1 | decisive |
| W2 | **Contested-capture standoff on long regions** (waits forever on a tile). | YBR g0 54 rounds (r184-238); g1 cleared by us and captured by them 6 rounds later; the line g2 112 rounds (r422-534). | 2 | major |
| W3 | **Solo banking through chokepoints with 19-43 gems**; no route or death-site memory. | Great wall: 8 carrier kills at (1,17), (47,16), (48,17), (13,12) x2, (39,14), (41,19), (22,8); 378 gems lost vs 29; first tribute r253 vs r112. | 1 (+ the line delay) | decisive |
| W4 | **No adaptation after losing early fights**: lone farmers keep visiting corner/edge groups. | Arena: 3 early 3-vs-1 deaths, then 19 1-vs-1 deaths at (0-2,0-15), (12-15,0), (27-29,0-7); Marcella 70 gold all game; clears 0.57/100r in r300-1000. | 1 (+ great wall) | decisive |
| W5 | **Camp-damage efficiency / item count** (Bruiser only, no Jungle/Durability). | Camp damage taken per 1k dealt 2-4x theirs in all three losses; emblems by r1000 18 vs 67 (YBR), 4 vs 40 (arena). | 3 | major |
| W6 | **Push-back freeze on dead camp tiles** (Q21). | YBR: quiet stretches next to row tiles, e.g. Vendetta (10,12) r558-679 and Marcella (7,12) r718-908. | 1 | major (**fixed in v4**) |
| W7 | **Big-bag carriers have no escort/standoff plan at a held altar.** | The line: 169 gems carried r534-707 while 3-4 enemies held the only altar. | 1 | minor (won) |

## Testable hypotheses (structure-keyed; no map or team names)
1. **H-rowvalue (W1): value large gold-only groups per champion-time and per contestability.**
   - **Change.** For a group with gems 0 and n >= 10 tiles, `value = 0.25 * gold / max(1, claimants)`, and do not apply the x1.2/x0.3 claim multipliers to it.
   - **Exclusion.** Skip it entirely while any of its tiles is within ~6 path steps of the enemy spawn and an enemy has been seen within 8 of the region in the last 40 rounds (they can contest the capture for free).
   - **Mechanism check.** First gem capture round and gems at r250 on maps with long gold rows; champion-rounds on 0-gem targets in r0-300.
   - **Gate.** Full `--maps all` (the rule is inert on most maps, so bundle per H-C).
2. **H-capabandon (W2, sharpens "c2 H3").**
   - **Rule.** If a RewardAvailable capture has not completed after 15 rounds on the tile *and* an enemy was visible within the region's bounding box during that time, either:
     - (a) engage that enemy if `group_balance` >= 1.0 (the capture needs it gone anyway), or
     - (b) abandon and ban the group for 60 rounds.
   - **Metric.** Rounds from last clear to our capture on groups with n >= 10; captures of our clears by the enemy ("steals" in scout).
3. **H-deathsite (W3/W4; concrete version of "death-site and fed-carry avoidance via shared memory").**
   - **Publish.** Store the champion's position every turn. On the first dead turn (the `not me.is_alive()` branch of `play_turn`), write that tile (x, y) and the round into free shared bytes 5-6 (with <= 5 champions, bytes 0-4 hold claims and byte 7 the focus).
   - **Banking.** Add a penalty to `pick_altar` routes passing within 3 of a recent (< 150 rounds) death tile, and bank only with >= 1 ally within 4, or at a lower threshold (<= 15) when the route crosses one.
   - **Targeting.** `choose_target` multiplies groups within 5 of a recent death tile by DEATH_PENALTY *for every champion*, not only the one who died.
   - **Metrics.** Gems lost to champions per game; carrier deaths with >= 15 gems; repeated deaths within 5 tiles of an earlier one within 300 rounds (arena: 18 of 34).
4. **H-outclassed (W4): a team pressure mode keyed on observed strength, not map.**
   - **Trigger.** When our team has lost >= 3 more champions than it killed in the last 300 rounds, *or* a visible enemy's strength+HP exceeds our best champion's by >= 25%.
   - **Effect.** Restrict targets to groups whose path distance to our spawn is <= that of the nearest enemy-seen tile, or require an ally within GROUP_ADV_R for groups farther than 15 from spawn. Leave spawn only in pairs (wait up to 15 rounds on spawn for a second healthy ally).
   - **Validate.** Against an imitation of a 3-pick duellist comp (Vesper/Tavi/Marcella with Treasure-first items), not self-play.
   - **Metrics.** Deaths per game when behind; solo-kill share of our deaths; gold per alive champion-round.
5. **H-jungle-adaptive (W5; ladder evidence for Q28b).**
   - **Rule.** Buy Jungle first when no ally has died to a champion and none has seen an enemy within 8 of our farms by the first 150 gold; else keep Bruiser.
   - **Evidence for.** The losses here show 2-4x worse camp-damage efficiency against Jungle/Treasure builds.
   - **Evidence against.** Arena was fight-decided, where Bruiser should stay.
   - **Metrics.** Camp damage per 1k dealt; clears per 100 rounds; fight K/D must not fall.
6. **H-escort (W7, low priority).**
   - **Rule.** A carrier with >= 50 gems whose chosen altar has >= 2 enemies within 6 holds within ~10 of it until `group_balance` >= GROUP_ADV with allies present, writing the altar into the focus byte so allies muster.
   - **Metric.** Rounds carrying >= 50 gems; gems lost by carriers with >= 50.

**Opponent-specific notes (for ladder expectations, not for fixes).**
- This bot is strong on gold-rich maps (Treasure snowball, then duels) and on maps with long altar routes, where it hunts carriers.
- It is weak on gem-cluster maps (item-poor; it lost fights 7-29 on crossing) and ignores big zero-strength gem rows.
- Against it, bank in pairs, avoid corners when behind on kills, and take the jackpots.
