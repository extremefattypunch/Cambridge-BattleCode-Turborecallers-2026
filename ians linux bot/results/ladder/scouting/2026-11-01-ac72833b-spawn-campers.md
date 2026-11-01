# Spawn Campers (1507): ladder set ac72833b, 1 Nov 2026, our v3, won 3-2

- **Opponent:** Spawn Campers, rating 1507 (ours after the set: 1529).
- **Our version:** website v3 = `bots/q24_combo` (live 01:42-04:42 UTC). The set ran at 02:22 UTC. We were side A (team A) in all 5 games.
  - v4 (`bots/c2_respawn`) differs from v3 **only** in the respawn-tile hunks (`RESPAWN_FIX`; `diff` shows nothing else). Every mechanism below except the v3 push-back freeze is also live in v4.
- **Record: 3-2.**
  - W 00anvil 1082-129 (r1847).
  - W 01the_farm 1026-846 (r1645).
  - **L 00split 476-1013** (r1144).
  - **L 01shortcut 714-1015** (r1789).
  - W 02fields 872-611 (r2000, tiebreak on gems).
- **Link:** https://2026a.battlecode.co.uk/game/match-groups/ac72833b-d6c3-4d47-9dcf-5e50c0d5dbe7
- **Sources:**
  - `results/ladder-games.jsonl` and `matches/ladder/summary/<id>__A.json`;
  - `python3.12 -I tools/scout.py --group ac72833b` and `tools/freeze_metric.py`;
  - ward trails to infer positions (a ward every 10 rounds after a move of more than 6 tiles);
  - map BFS from `tools/scout.py`'s decoder. Walking distances below treat holes as **blocked**, as `walk_block` does; scout's own BFS lets holes through.
  - Replays are not downloaded, and there is no decoder for the binary replay. Positions are inferred, and inferences are marked.
- **Bottom line.** This opponent out-farms us 3-4x on 5-pick maps by:
  - solo farming everywhere;
  - taking **2.3-5.6x less camp damage per 1,000 dealt** (Jungle + Durability emblems);
  - getting an extra body from Cassi & Issac.

  We win the fights: 100-50 in kills over the set.
  - **The two losses come from walking, not fighting:**
    - **00split:** each of our champions made 10-13 spawn round trips of 25-30+ steps each way.
    - **01shortcut:** our carriers took the 109-step walking route to the altar instead of the hole-crossing shortcut, and one died on it carrying 158 gems.

## Game summary
| Map (size, symmetry, picks) | Result | r250 | r500 | r1000 | End | Clears/100r us-them | K us-them | Camp dmg taken per 1k dealt us/them |
|---|---|---|---|---|---|---|---|---|
| 00anvil (37x31, horizontal, 3) | **W** | 96-46 | 157-54 | 305-129 | 1082-129 r1847 | 3.79-2.76 | 29-9 | 628 / 483 |
| 01the_farm (50x40, horizontal, 3) | **W** | 55-0 | 144-159 | 300-312 | 1026-846 r1645 | 2.55-3.71 | 6-0 | 405 / 222 |
| 00split (45x35, horizontal, 5) | **L** | 180-39 | 213-308 | 402-858 | 476-1013 r1144 | 1.84-6.03 | 8-10 | **772 / 278** |
| 01shortcut (40x40, vertical, 4) | **L** | 28-0 | 186-141 | 387-333 | 714-1015 r1789 | 2.63-4.19 | 18-10 | 480 / 304 |
| 02fields (51x51, rot180, 5) | **W** | 65-14 | 123-126 | 414-230 | 872-611 r2000 | 2.2-7.35 | 39-21 | **627 / 112** |

## 1. Opponent profile
**Draft: fixed, truncated by pick count.** Ryth, Cassi & Issac, Stellar, Varg, Tavi.
- 3-pick: Ryth, Stellar, Varg.
- 4-pick: + Cassi & Issac.
- 5-pick: + C&I + Tavi.
- **Cassi & Issac is one pick and two bodies.** That gave them 5 bodies to our 4 on shortcut and 6 to our 5 on split and fields. A C&I death costs them both bags.

**Roles (per-champion lines).**
- **Ryth:** top farmer and biggest banker:
  - farm 511 gems, 9 tributes x 46.9;
  - shortcut tributes of 78, 101 and 78.
- **Varg:** splash farmer of wolf and cluster groups (fields 34 clears, the most on either side).
- **Stellar:** ranged burst. Farms (fields 29 clears) and kills carriers (shortcut: our Marcella's 158-gem bag).
- **Tavi:** ranged stun plus damage, the **altar guard**. On split, 5 of their 10 kills, every one at or next to the shared altar (22,32).
- **Cassi/Issac:** farmer pair. Cassi is the second killer on shortcut (5 kills).

**Items: an altar lock at the first shop, then a camp-damage build. Never Bruiser.**

| Champion | 1st emblem | then |
|---|---|---|
| Ryth | Jungle S (r60-r409) | Durability H, then Power S x n (fields: 12 Power emblems) |
| Stellar | Monster F (r302-r738) | Durability H, Jungle F, Power F x n |
| Varg | Monster S (r129-r1468) | Durability H, Jungle S, Power S x n |
| Cassi / Issac | Monster F / Monster S (r84-r565) | Durability H, Jungle, Power |
| Tavi | Monster S (r215-r259; buys shards in the field) | Durability H, Jungle S, Power S x n |

- **Nearly every champion completes Durability H (-10% all damage) and Jungle (-30% camp damage) by r300-1350.** The one exception is split's Varg, which bought Monster only. We never buy either: `BRUISER_PLAN`, `JUNGLE_FIRST = False`.
- **Locks:** 7-18 bought per game; about 11, 7, 1, 3 and 14 used (bought minus held). Placements aren't in the stats, so their effect on our tributes is unknown.
- **Wards: zero in every game.** They play blind and rely on bushes. The bush ring around split's shared altar is where Tavi sits.

**Farming: strictly solo, everywhere, high tempo.**
- 100% solo captures: 48/48, 60/60, 65/65, 74/76, 142/142.
- Clear rate 2.8-7.6 per 100 rounds, highest on 5-pick maps: split 6.03, fields 7.35.
- They farm our side freely: split 11 captures on our side, fields 32.
- **Camp efficiency is their edge.** Camp damage taken per 1,000 dealt, theirs vs ours: split 278 vs 772, fields 112 vs 627, farm 222 vs 405, shortcut 304 vs 480.
  - Camp damage dealt per clear is also lower (split 1,637 vs 2,253; fields 1,037 vs 2,724). We spend damage on camps we don't finish.
- **Their weak point:** a weak camp-safety model. Champions lost to camps: 7 (anvil), 4 (farm), 6 (split), 4 (shortcut).
  - On the farm, camps destroyed **158** of their gems:
    - Ryth 51 at r119, Stellar 55 at r738 and 22 at r850, all to the same camp (id 19) at (36,13-16);
    - Ryth 30 at r580 at (29,0).

**Tributes: the size follows the walk to the altar.**
- Count x mean:
  - fields 68 x 9.0 (three central altars, so they bank almost every capture);
  - split 48 x 21.1;
  - farm 22 x 38.5;
  - anvil 10 x 12.9;
  - shortcut 15 x 67.7 (altars far behind walls: bags of 179, 109, 101, 85 and 78).
- They use whichever altar is nearest the farming, including ours:
  - fields: 39 of 68 tributes at **our-side** altar #0 (17,25);
  - split: 44 of 48 at the shared (22,32).

**Fights: altar-centred, unwarded, no spawn camping.**
- Despite the name, they don't camp our spawn. Our deaths near *their* spawn are our own dives:
  - shortcut 3: Vendetta at (16,18) and (19,17), Vesper at (15,14);
  - we killed them beside their own spawn 3 times on anvil and 6 on shortcut.
- Their kills cluster on altars: split 7 of our 12 deaths, fields 6 of 25.
- They lose grouped fights to our group rule: anvil 6 of 6 multi-death fights ours, fields 7 of 10, shortcut 4 of 5.

**Adaptation across the 5 maps.** Draft and build are fixed. Only tribute cadence changes, driven by altar distance. On the 3-pick maps (anvil, farm), without C&I and Tavi, they were close to harmless in fights (anvil K 9-29, farm 0-6).

## 2. Per game
### 00anvil: W 1082-129
- **Their start.** First tribute r46 (ours r142), but their early gems died with them: 7 champions lost to camps, and 78 gems to our champions.
- **Fights:**
  - Vendetta 15/3, Marcella 10/2.
  - Kills in their half: 20 of 29.
  - Six multi-death fights, all ours: r348, r469, r728 (3-for-0), r1120, r1445 and r1714 (3-for-0).
- **Swing.** The g10 Monolith (200 gems, 3 tiles from the only altar):
  - Vendetta soloed it at **r1557** and banked 211 at r1586;
  - Marcella soloed it at **r1824** and banked 214 at r1848, which ended the game.
  - The monolith made up 400 of our 1,082 gems. Before r1557 the race was only 305-129 at r1000.
- **Root.** We won the fights, then the late big objective.

### 01the_farm: W 1026-846 (lead for good only from r1297)
- **No PvP until r1001.** They made 0 kills all game; we made 6, all after r1001.
- **Our tempo hole, r312-500.**
  - Vesper's ward trail stops at r321 (11,3) and resumes at r522 (20,0).
  - Marcella's stops at r319 (12,3) and resumes at r498 (spawn).
  - Both had about 180 rounds with **no metric change** (scout quiet: Vesper r312-479, Marcella r323-479), right beside our home group g7, Elkx2+GemCl+GoldClx2 (37 gems, 5 steps from spawn). We first captured g7 only at **r1012**.
  - *Inference:* this fits v3's respawn push-back 2-cycle. `play_turn` pushes a champion off **any** camp tile (`blocks_respawn` returns True outside gold play) and `return`s **before** `note_progress`, so the STUCK ban never fires. v4's `RESPAWN_FIX` removes that branch.
- **Race.** 144-159 at r500, 300-312 at r1000.
- **How we got ahead.** Bigger bags late (66 at r1061, 74 at r1362) and their 158 gems lost to camps. We still trailed on clears, 42 to 61.
- **Root.** Their camp deaths and our late fights offset our ~360 idle champion-rounds and slower farming.

### 00split: L 476-1013 (the clearer loss)
**Map.** Two halves split by a wall plus hole column at x=21-23, joined only at the bottom around the **single shared altar (22,32)**, which is ringed by bushes.
- Each team's spawn (ours (10-12,1-3)) sits in a walled room with private altars (18,2)/(26,2).
- The camp field (y=12-33) is reached only through **two chokepoints**: the west gap (0-2,5), then (16-20,11).
- The nearest camp is 24 steps from spawn (g30 at (14,12)); our gem groups are 29-42 steps away (g12 29, g10 36, g14 42).

**Decisive mechanism 1: the commute (r150-1144).**
- Every one of our champions shows the same ward trail, repeated: spawn (12,0) → (5,4) → (15,6) → (12-14,14-17) → (11-12,20-22), then **back on spawn within 10-30 rounds**. That is too fast to walk, so it is a recall.
- Spawn visits per champion after the start: Vesper 12, Vendetta 11, Marcella 12, Ryth 9, HoR 8. Most did not follow a death (Vesper 11 of 12).
- That is one round trip about every 90 rounds, each costing about 55 rounds of walking plus the recall.
- **Vesper earned 0 gold until r500**, bought nothing until r727 and made 2 clears all game. Each trip cost it about 850 damage (camp 4,960 plus champion 5,234 over 12 trips) on 1,000 HP, so every trip ended in the `low` recall (`hp < 0.45*maxhp`).
- The turnaround point (11-12,20-22) is inside the range of the g12 golem (11,19), 64 gems, and of the g10 elk (13,25). We first cleared g12 at **r843**.
  - *Inference:* the champions were chipping g12/g10 with recall-length cycles.
- **Result:** our clears were 7 / 11 / 3 per phase against their 14 / 44 / 11. Monster damage dealt was 47k against 113k. Camp damage taken was 36.5k against 31.4k for 21 clears against 69.

**Decisive mechanism 2: the shared altar.**
- We banked at (22,32) 7 times, the last at **r143**. Then:
  - r200: Vesper died at (20,29) to Issac;
  - **r239-247: HoR at (22,31) and Vendetta at (18,29), both to Tavi;**
  - r369: Marcella at (21,30) to Stellar;
  - r548: Vendetta at (22,30) to Stellar;
  - r559: Marcella at (21,30) to Tavi;
  - r609: Ryth at (19,28) to Tavi, carrying 29;
  - r618: HoR at (20,29) to Tavi.
- Our champions arrived **one at a time**: no multi-kill fight of theirs had more than 2 of ours in it.
- After r143 all our banking went to the top altar (18,2), 14 times, through the chokepoints. They banked at (22,32) 44 times.

**Race.** +141 at r250, then -236 (r250-500) and -269 (r500-750), which was the widest swing.

**Root.** They farm 3x faster from a front-line altar. We spend about half of each champion's time walking to spawn and back, and we lost the one altar near the field to their bush-hidden ranged guard.

### 01shortcut: L 714-1015 (lost after leading 563-333 at r1300)
**Map.** Vertical symmetry. Spawns: ours (18-21,25-27), theirs (18-21,12-14).
- The mid row y=19-20 (the "shortcut") runs 5 steps from both spawns and holds:
  - g0 GemClx4 (28 gems);
  - g1 Elkx2+GoldClx2 (30 gems);
  - g2 Wolfx2+GoldClx2.
- **Both altars, (32,12) and (32,27), sit in walled boxes.**
  - With holes treated as walls, the walking distance from our spawn to either altar is **109 steps**, around the far west lane and the enemy half.
  - Crossing hole strips (dash, or TP crystal range 3) cuts it to about 45.

**The mid.** They captured g0 (28 gems, 5 steps from both spawns) 10 times, we 2. Camp gems: theirs 1,250, ours 716 (clears 75 vs 47).

**Our compensation: kills.**
- Vesper went 12/1 and took 293 gems from kills; Marcella took 208.
- **We took 501 gems from their carriers.** Examples: C&I with 51+22 at r258, Issac 64 at r829, Varg 42 at r858, C&I 66+49 at r1055, Stellar 64 at r1645.

**Decisive moment: r1070-1192.**
- After killing C&I (r1055) and Varg (r1068), **Marcella carried 158 gems.**
- Her ward trail with walking distance from our spawn: (16,24) r1108 [2] → (19,32) r1118 → (11,34) r1128 → (1,33) r1138 [29] → (7,24) r1153 [44] → (3,19) r1164 [51] → (4,9) r1174 [67].
  - That is the 109-step walking route to the altar.
  - She dealt and took **no damage** from r1070 to r1160, so she was walking, not fighting.
- **Stellar killed her at (0,6), step 75 of 109, at r1192.** Stellar banked **179** at r1304.
- Marcella still held an unused TP crystal at game end (`consumables`: TP 1).
- Then:
  - Cassi took bags from Vesper (22, at r1442) and Vendetta (29, at r1505);
  - Cassi banked 109 and Issac 85 at r1578-1579, the moment they took the lead for good.
  - We ended with **155 unbanked gems**: Vesper 133, from carrier kills at r1645-1740.

**Gem flow.**
- Ours: we collected 716 + 501 = 1,217; tributed 714; lost 323 to champions and 25 to camps; carried 155 at the end.
- Theirs: they collected 1,250 + 323; tributed 1,015; lost 501 and 57.

**Root.**
- They out-farmed us 1,250 to 716 camp gems.
- We kept pace through kills, but threw it back by walking stolen bags along 109-step routes through their half, instead of crossing holes. 158 of our gems became their 179.
- Our 1,304 idle champion-rounds (Marcella 602, r911-1053) did not help.

### 02fields: W 872-611 (r2000)
**Map.** Three central altars, (17,25) ours, (25,25) mid and (33,25) theirs, inside a bush grid.

**Their farming.** 147 clears to our 44. After r1000: **76 clears to our 10.**
- 39 of their 68 tributes (9 gems each) were at our-side altar #0.

**Ours: altar killers.** 39 kills to 21, 19 of them at altars:
- Marcella 17/4, with 8 kills after r1000;
- Vendetta 12/6, with 9 after r1000.
- `focus_bias` puts tributing enemies in tier 0 and adds ratio 1.2, and their 9-gem bags kept coming. Their gems lost to our champions: 235.

**Vesper idle r479-1768 (1,289 rounds).**
- The trail stops at r473 (35,38), a bush 2 tiles from g9 GemClx8+Monolith (256 gems, never touched), and resumes at r1771.
- *Cause not identifiable* from the stats. The v3 push-back needs a dead camp tile, and g9 was never damaged, so it is unlikely.

**Gold.** Earned gold ended 8,966 to 9,040 (they led). Gems won it.

**Root.** We won on kills at the altars while losing the farm 3:1. With 1 of 5 champions frozen for 65% of the game, the margin (261) was thin.

## 3. Their strategy vs ours
**Where theirs was superior.**

| Gap | Size | Our code responsible |
|---|---|---|
| **A. Camp efficiency.** Jungle + Durability on every champion; ranged and splash farmers. | Camp damage per 1k dealt: 278 vs 772 (split), 112 vs 627 (fields). Damage dealt per clear: 1,037-1,637 vs 2,253-2,724. | `shop()` → `bruiser_item()` with `BRUISER_PLAN` (Bruiser S/H/F only). `JUNGLE_FIRST = False`; Durability is never bought. Plus the chip model below, which deals damage to camps we then abandon. |
| **B. No commute.** They bank at the front altar and keep farming. We recall to heal about every 90 rounds on split. | Split: 10-13 spawn trips per champion; Vesper 0 gold for 500 rounds; clears 21 vs 69. | `play_turn`: `low = hp < maxhp * 0.45` → `me.recall()`; `handle_enemies`: `hp < 0.5*maxhp` → recall. `choose_target`'s chip model (`cycles <= 4`, `extra = cycles * 30.0`) prices a hit-and-run cycle at 30 rounds. With a 25-30-step spawn path a cycle actually costs ~60 (recall 5 + walk back), and nothing in the cost uses the spawn distance. The claim term `tdps = dps + c * 55.0` lets several champions each accept a group none can solo, but they don't arrive together. |
| **C. Front altar held.** Tavi/Stellar in the bush ring of the only shared altar. | Split: 7 of our 12 deaths at (18-22,28-31); our last tribute there at r143; theirs 44x. | `pick_altar` adds `ALTAR_DANGER_PEN = 12` after a sighting, then sends carriers to the far private altar. Nothing makes us contest the altar *as a group*. `group_balance` only counts allies within `GROUP_R = 7`, so lone arrivals get the `dis` retreat or die. |
| **D. Shortcut use.** | Shortcut: Marcella's 158-gem bag lost at walking step 75 of 109; 155 unbanked at the end. | `go_to` / `do_tribute` → `step_toward` over the **walk-only** field. `cross_toward` (dash / TP crystal) fires only when the goal is in a **different walk component** (`(goals & comp).is_empty()`). When the same component reaches the goal by a 109-step detour, we never cross, even holding a TP crystal. |
| **E. Bodies per pick.** | +1 champion on 4-5-pick maps. | `draft.py` PRIORITY never takes C&I. A draft question, not tested here. |

**Where ours was superior.**
- **Grouped fights.**
  - Kills 100-50 over the set. Multi-death fights: 20 won, 4 lost, 2 even (anvil 6-0, split 3-2, shortcut 4-0-1, fields 7-2-1).
  - `group_balance` (`GROUP_ADV` 1.4 commit, `GROUP_DISADV` 0.75) beats their unwarded solo farmers when they walk into 2-3 of ours.
- **Carrier kills:**
  - shortcut 501 gems taken; fields 235; anvil 78.
  - `focus_bias` puts channelling enemies in tier 0, and the carried-gem term adds up to +0.3.
- **Big objectives once our items allow:** the anvil Monolith twice (400 gems).
- **Early tributes:** we were first on split (r80), shortcut (r226) and farm (r105).

## 4. Our weaknesses exposed
| # | Weakness | Evidence | Games | Impact |
|---|---|---|---|---|
| W1 | **Spawn commute / recall cycles.** Heal recalls every ~90 rounds when the spawn is 25-30+ steps from the field; the chip model doesn't price the trip. | Split: 10-13 spawn visits per champion; Vesper 0 gold to r500; clears 21-69; monster damage dealt 47k vs 113k. | 1 (decisive) | decisive |
| W2 | **Walk-only routing inside one component.** Hole crossings are never used as shortcuts. | Shortcut: altars 109 walking steps vs ~45 with crossings; Marcella killed at walking step 75 with 158 gems while holding a TP crystal; 155 unbanked at the end. | 1 (decisive) | decisive |
| W3 | **Camp damage efficiency** (no Jungle / Durability) | Camp damage per 1k dealt 1.6-5.6x theirs in all 5 games; damage per clear 1.4-2.6x. | 5 | major |
| W4 | **Front altar abandoned to a hidden ranged guard; champions arrive one at a time** | Split: 7 deaths at the altar ring, our last tribute there r143 vs their 44 tributes; Tavi 5 kills. | 1-2 | major |
| W5 | **Long freezes** | Fields: Vesper idle 1,289 rounds (r479-1768). Farm: Vesper/Marcella about 180 rounds each by g7 (v3 push-back likely; fixed in v4). Shortcut: 1,304 idle champion-rounds (Marcella 602). | 3 | major |
| W6 | **Mid groups between the spawns conceded** | Shortcut: g0 (5 steps from both spawns) 10 vs 2; fields: 32 of their captures on our side. | 2 | minor |

## Testable hypotheses (structure-keyed; no map or team names)
1. **H-cross-shortcut (W2, highest value: cheap and decisive).**
   - **Change.** In `go_to` and `do_tribute`, compare the walk-only distance with a crossing-aware estimate: BFS where a hole strip of width ≤ 2 (dashers) or ≤ 3 (crystal holders) costs 1 step. If walking > 1.5x crossing + 8, route to the crossing staging tile via `cross_toward` even inside the same component.
   - **Also.** Non-dashers keep a TP crystal (already bought by `need_crossing`).
   - **Metrics.** Walking steps per tribute; carrier deaths en route; gems lost to champions per game.
   - **Mechanism check.** Local 01shortcut A/B. Its altars are 109 vs 45, so the bug reproduces deterministically.
2. **H-commute-cost (W1).**
   - **Change.** In `choose_target`, when a target is not solo-safe (`dmg > hp - 150`), price each extra cycle at `5 + 2 * spawn_path(G)` rounds instead of a flat 30 (`spawn_path` is a static BFS from our spawn). Drop the `c * 55` claim credit unless the claimer is within 6 tiles.
   - **Alternative.** When the spawn is ≥ 25 path steps from the field, replace the `low` recall with a step out of camp range and a wait for allies. Camps don't regenerate, so a chipped group keeps its damage.
   - **Metrics.**
     - spawn visits per 1,000 rounds (ward-inferred, or a debug counter in a local run);
     - clears per 100 rounds on maps where the nearest gem group is ≥ 25 steps from spawn;
     - camp damage dealt per clear.
3. **H-jungle-durability (W3; a variant of the queued Q28 items).**
   - **Change.** Make the 2nd emblem Jungle for any champion whose own camp damage taken per 1k dealt is above 400 by its second shop visit, and the 3rd Durability. This is keyed on the champion's own stats, not the map.
   - **Metrics.** Camp damage per 1k dealt (target < 400); heal-recall trips; fight K/D must hold (T25 Jungle-first was rejected for fight blowouts, so keep the 1st emblem Bruiser).
4. **H-altar-escort (W4).**
   - **Change.** If an ally died within 4 of an altar in the last 150 rounds, a carrier banks there only with another ally within 4 (wait at 8 tiles otherwise). Champions near that altar treat a bush tile next to it as a `rally` point.
   - **Metrics.** Deaths within 3 of an altar; front-altar tributes per game.
5. **H-idle-watchdog (W5, shared with the 008a189a report).**
   - **Change.** 80 rounds with no activity-counter change, alive and off spawn → ban the current target for 150 rounds and recall if HP < 70%.
   - **Metric.** `tools/freeze_metric.py`.
6. **H-C&I draft (E).**
   - **Change.** On 4-5-pick maps, try Cassi & Issac as our last pick (an extra body).
   - **Test.** A pure draft A/B through `tools/eval.py` on 4-5-pick maps only. *Speculative:* their linked death gives killers both bags.

**Opponent notes (for ladder expectations, not for fixes).**
- Expect wins on 3-pick maps.
- On 5-pick maps with far-from-field spawns, a single shared front altar, or hole-separated altars, this bot out-farms us 3:1. It wins unless our fights take its bags.
- It never wards and loses champions to camps, so carrier hunts near its farming lanes pay off.
