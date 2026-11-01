# vs Sneaky Bush Campers (1533): 2-3, 2026-11-01 04:04 UTC, our v3 (`q24_combo`)

**Site:** https://2026a.battlecode.co.uk/game/match-groups/b08d1f20-9663-497e-a333-0c602afcbe62
**Data:** `matches/ladder/summary/<matchId>__A.json` for each game (we were team A in all 5); `python3.12 -I tools/scout.py --group b08d1f20`

- **Opponent:** Sneaky Bush Campers, rated 1533. Our rating after the set: 1526.
- **Our version:** v3 = `bots/q24_combo`. Every code reference also holds for v4 (`bots/c2_respawn`), which only adds the respawn-tile step-off rule; line numbers are given as v3 / v4.
- **Record: 2-3.**
  - **L 01concentrated_wealth 305-1033** (r1262, gems).
  - W 00the_line 1046-269 (r1335, gems; 4 picks).
  - W 00galaxy 1017-648 (r1262, gems).
  - **L 00elkring 817-1012** (r1048, gems).
  - **L 02geodes 756-1014** (r1120, gems).
- **Method:** as in the other scouting notes. Positions come from death, ward, clear, capture and tribute events; *speculation* is marked. The helper scripts are in the session scratchpad.

## 1. Opponent profile

**Draft: fixed.**
- 5 picks: Varg, Heart of Ruin, Vesper Vale, Vendetta, Ryth.
- 4 picks (00the_line): the same without Ryth.
- Three of their picks mirror ours (Vesper, Vendetta, HoR, plus Ryth on 5-pick maps). The difference is **Varg instead of Marcella**.

**Champion roles.**
| Champion | Role | Evidence |
|---|---|---|
| Varg | Solo jungler of the biggest strong-camp group | concentrated_wealth: 370 gems, 6 tributes averaging 61.7. elkring: 374 gems. geodes: **643 gems**, 10 tributes averaging 64.3, all 6 Golem-field captures, 0 deaths to camps |
| Heart of Ruin | Cluster-field farmer (shield, plus a dash landing for 1.5×F in radius 1 that stuns) | concentrated_wealth: **541 gems**, 8 tributes averaging 58.8, 2,530 gold; 7 of the 12 captures of the central Elk + 20-cluster field |
| Vesper, Vendetta, Ryth | Small-group farmers, one group each | 15-22 gem groups, solo captures |

**Items: Power only, bought in bulk.**
- concentrated_wealth: HoR bought **Power Focus x11 (2 emblems) at r88**, x11 at r197, x11 at r466 and x18 at r878. Varg bought Power Strength x11 at r331 and Power Health x13 at r515.
- elkring: Varg Power Strength x10 at r176 (2 emblems); later Power Health x14 at r651 and Strength x15 at r896.
- geodes: Varg Power Strength x5 at r228 and r357, Power Health x14 at r825 and x19 at r1080.
- Never Jungle, Monster, Durability, Treasure or Bruiser.
- galaxy: they earned only 160 gold all game. They captured no gold group, so they had no emblems.
- **Wards: 0 in all 5 games.**
- **Altar locks:** 0, 11, 3, 14 and 0 bought. The first came at r29 on the_line and r117 on elkring.

**Farming: one champion per group, every capture solo, high-value groups first.**
- **Solo captures: 27/27, 36/36, 43/43, 50/50, 32/32.** That is 1.00 champions per capture in every game. Ours: 1.50, 1.09, 1.31, 1.64 and 1.25.
- **On elkring, the whole team cleared together in the opening, then one champion captured** while the other four moved on:
  - g1 clear r11 → capture r18 by Varg alone;
  - g3 clear r25 → r31;
  - g5 clear r43 → r49;
  - g8 clear r59 → r65.
- **They farm the single most valuable group on the map repeatedly, solo:**
  - concentrated_wealth: central g0, Elk + 8 GemCl + 12 GoldCl (71g + 330 gold, at (30,30), 5 tiles from both altars). **Captured 12 times** (HoR r76, r175, r387, r868, r953, r1152, r1247; Varg r295, r479, r636, r773, r1060), for **852 gems**.
  - geodes: g12, GemCl x8 + Golem (92g at (38,19), mid), captured by Varg at r325, r583, r729, r901 and r1075; g13 (50,51) at r992. That is **552 gems**.
  - elkring (every group is Elk + GemCl + GoldCl, 22g): 50 captures to our 36.
- **Gems per capture:** concentrated_wealth 40.9 vs our 12.5; geodes 33.5 vs our 15.1.

**Tributes: every bag is banked right after its capture.**
- Mean tribute equals one capture: concentrated_wealth 39.7 (26 tributes), geodes 35.0 (29), elkring 23.0 (44).
- **First tribute earlier than ours in all 5 games:** r128, r45, r70, r70 and r75, against our r320, r162, r171, r93 and r113.
- They used both altars, picking the nearest each time.

**Fights: they hardly fight.**
- **Kills per game: 1, 4, 1, 0, 1.** Their deaths: 4, 18, 20, 9 and 4.
- **Their kills were at the altar or on our carriers:**
  - the_line: Vendetta killed 4 times around the only altar (3,16): Marcella (10,17) r385, Vesper (5,18) r684, Vendetta (1,17) r716 with 8g, Vendetta (4,17) r1054 with 4g.
  - galaxy: Vendetta killed our Vendetta at (41,63) at r373 with **35g**.
  - concentrated_wealth: Ryth killed our HoR at (35,27) at r703.
  - geodes: Varg killed our Ryth at (52,17) at r858.
- **No hunting, no spawn camping, no wards.** They use altar locks on some maps (elkring: about 10 used).
- **Their big carriers walk unescorted.** We killed their 161-gem Vesper on the_line, their 71-gem HoR on concentrated_wealth, and took 154 gems in 8 kills on galaxy.

**Adaptation across the 5 maps: none.** Same draft, same Power builds, same one-champion-per-group circuit. They won every map whose gems sit in **strong-camp groups** (an Elk + cluster field, Elk groups, Golem + cluster fields). They lost the two maps whose gems sit in **0-Strength cluster fields** next to the altar, where fights decide.

## 2. Per game
Gem race = tributed gems, us-them. We were side A in every game.

| # | Map (size, picks) | Result | r250 | r500 | r1000 | End | Gold us-them | Clears us-them | Captures (champions per capture) us / them | Kills us-them |
|---|---|---|---|---|---|---|---|---|---|---|
| 1 | 01concentrated_wealth (61x61, 5) | **L** | 0-168 | 74-355 | 281-754 | 305-1033 r1262 | 2,734-5,505 | 24-27 | 24 (1.50) / 27 (1.00) | 4-1 |
| 2 | 00the_line (33x33, 4) | **W** | 165-16 | 334-32 | 692-237 | 1046-269 r1335 | 3,393-2,657 | 25-34 | 23 (1.09) / 36 (1.00) | 18-4 |
| 3 | 00galaxy (93x93, 5) | **W** | 60-193 | 292-298 | 683-585 | 1017-648 r1262 | 3,296-160 | 50-42 | 49 (1.31) / 43 (1.00) | 20-1 |
| 4 | 00elkring (30x30, 5) | **L** | 129-176 | 220-462 | 777-968 | 817-1012 r1048 | 5,460-5,790 | 34-54 | 36 (1.64) / 50 (1.00) | 8-0 |
| 5 | 02geodes (89x71, 5) | **L** | 105-138 | 254-321 | 655-801 | 756-1014 r1120 | 2,983-2,862 | 49-34 | 48 (1.25) / 32 (1.00) | 4-1 |

### Game 1: 01concentrated_wealth, L 305-1033
**Map.** Two altars, (23,24) on our side and (37,36) on theirs.
- Central g0: Elk + 8 GemCl + 12 GoldCl (71g, 330 gold).
- Corner groups: g1 at (1,1) and g2 at (59,59), each Elk + GemCl + GoldCl (22g).
- Wolf groups worth 4-15g.

**Decisive moments.**
- **r76: their HoR captures g0 alone** (+71 gems, +330 gold). It tributed 71 at r128 and bought Power Focus x11 at r88. By r250 HoR had earned 660 gold.
- **They repeated it 11 more times:**
  - HoR: r175 (tributed 71 at r192 at our-side altar (23,24)), r387, r868, r953, r1152, r1247.
  - Varg: r295, r479, r636, r773, r1060.
- **We never cleared g0.**
  - Our income was g1 (1,1), 10 captures, three champions at a time early: Marcella + HoR + Ryth at r45 and r135, Vendetta + Marcella + HoR at r228.
  - Our first tribute came at r320, by three champions at the enemy-side altar (37,36). The race stood 0-168 at r250 and 74-355 at r500.
- **Our one swing:** at r405 our Ryth killed their HoR at (30,28) carrying **71 gems** and tributed them at r542.
- **Our HoR earned 254 gold all game.** It bought one Bruiser Health emblem at r326 and was quiet r326-478.

**Root reason:**
- 852 of their 1,033 gems came from one group our safety model never lets a champion start.
- Their HoR snowballed on its gold (330 per capture) into 2 Power Focus emblems by r88.

### Game 2: 00the_line, W 1046-269 (4 picks)
**Map.** A 33x33 vertical map.
- Central g2, GemCl x23 (161g, 0 Strength), sits 3 tiles from the only altar (3,16).
- Everything else is Wolf + GoldCl groups worth 4g.

**Decisive moments.**
- **r119:** our HoR captured g2 alone (+161) and tributed at r162. It stood 165-16 at r250.
- **r393:** their Vesper captured g2 (+161). Our Vendetta killed it at (11,25) next to their spawn at r463 (161 gems lost) and tributed 169 at r499.
- **We captured g2 again** at r559 (Vesper + HoR), r914 (HoR) and r1035 (Marcella): 5 captures to their 2. Varg's r685 capture was tributed at r743.
- Our Vendetta went 16/2, with streaks of 2, 2 and 3. They lost 201 gems to us.
- Their other income was 26 tributes, median 4: Wolf + GoldCl bags.

**Root reason:**
- On a 0-Strength field, the race is decided by who holds the field and kills the carrier.
- Our solo model takes such fields immediately and our fights win them. Theirs gave 161 gems away.

### Game 3: 00galaxy, W 1017-648
**Map.** A 93x93 map. All gem groups are 0-Strength clusters around the two altars, (38,46) ours and (54,46) theirs: g6 35g (46,46), g1 21g, g0 21g, g7 14g and g8 14g.

**Decisive moments.**
- **r0-250: behind 60-193.** Their first tribute came at r70 against our r171.
- **From r500: we hunted their carriers at the mid fields.** Twenty kills to 1. They lost 154 gems: Ryth 21g r516, HoR 21g r571, Vendetta 21g r589, Varg 21g r715, Ryth 14g r834, Ryth 21g r1115, Vendetta 21g r1183, Varg 14g r1191.
- Ahead for good from r624. The gap grew +246 in r1000-1262.
- They earned 160 gold all game: no gold groups and no kills, so no items.

**Root reason:**
- Our fights won a cluster-field race we were losing on tempo.
- Our only loss was Vendetta with 35g at r373.

### Game 4: 00elkring, L 817-1012
**Map.** A 30x30 map with 10 identical groups, Elk + GemCl + GoldCl (22g each, 5 per side), and two altars at (3,26) and (26,3).

**Decisive moments.**
- **r0-80: an even opening.** Both teams team-cleared:
  - their clears r11, r25, r43, r59;
  - ours r13, r31, r55, r78.
  - But they **captured solo**, while our captures took 3 champions: Marcella + HoR + Ryth at r19 and r38; Vendetta + Marcella + HoR at r61.
- **r80-110: all five of ours did 0 monster damage**, banking 21-23 gem bags at (3,26) at r93, r96 and r109. Theirs only paused in r60-70.
  - Their g1 was recaptured at r117, ours g0 at r135.
- **r250-500: −195.**
  - In r300-1000 they cleared 5.71 groups per 100 rounds to our 3.43; captures were 50 to 36 overall.
  - At r500 we were carrying 88 unbanked gems (Vesper 30, Vendetta 33, Marcella 7, Ryth 18); they were carrying 22.
- Kills went 8-0 to us, taking 66 gems (their HoR 22g three times), and the race was 777-968 at r1000. Not enough.

**Root reason:**
- Same map value, but they converted it faster: 14 more captures (about 300 gems).
- Causes: no split captures, prompt banking, and no idle team-wide banking trips. *Speculation:* their spawn is only 4-9 steps from their groups, so it heals them between elk pulls; ours is equally close, but our hit-and-run budget does not model it.

### Game 5: 02geodes, L 756-1014
**Map.** An 89x71 map.
- Two mid Golem + 8 GemCl fields: g12 (38,19) and g13 (50,51), 92g each.
- Elk + cluster and Wolf + cluster groups on each side.
- Five altars.

**Decisive moments.**
- **r325 and onward: Varg's solo Golem farm.**
  - g12 captures: r325 (tributed 92 at r347 at (28,13)), r583 (r605), r729 (r751), r901 (r923), r1075 (r1121).
  - g13: r992 (tributed r1013).
  - That is 552 gems, with 0 Varg deaths to camps.
- **We out-cleared them 49 to 34** and took 10 enemy-side captures (78g); we led 336-332 at r600.
- **r750-1000: −109,** as Varg's 92-gem bags kept landing.
- Kills 4-1 (Vendetta 4, including their HoR with 29g at r587). It was not enough.

**Root reason:**
- 552 Golem-field gems against our 0.
- Our solo model rejects the Golem field: s = 120, hl = 5,960, so cycles of about 8-9 are above the cap of 4.

## 3. Their strategy vs ours

**Overall (2-3).** Theirs was the better *farming* strategy: one champion per group, every capture solo, the most valuable strong-camp group farmed repeatedly by a sustain champion, and every bag banked at once. Ours was the better *fighting* strategy: kills 54-7 over the set.
- They won the three maps whose gems need a strong camp killed (an Elk + cluster field, Elk groups, Golem fields).
- We won the two maps whose gems sit in 0-Strength fields, where our fights decide who keeps the bag.
- The result came from strategy, not from bugs: no long freezes, and 0-3 fuel exhaustions per game.

**Where theirs was superior, and by how much.**
| Aspect | Them | Us | Gap |
|---|---|---|---|
| Strong-camp group gems | concentrated_wealth 1,006 elk-group gems; geodes 552 Golem-field gems; elkring 1,100 | 220; 0; 792 | **decisive** in all 3 losses |
| Champions per capture | 1.00 in all 5 games | 1.09-1.64 (elkring 59 capture slots for 36 captures) | about 23 wasted capture slots on elkring |
| Gems per capture | concentrated_wealth 40.9; geodes 33.5 | 12.5; 15.1 | 2.2-3.3x |
| First tribute | r45-128 | r93-320 | 23-192 rounds earlier |
| Gold on strong-camp maps | concentrated_wealth 5,505 by end; HoR 660 by r250 | 2,734 by end; our HoR 254 in the whole game | 2.0x |

**Where ours was superior.**
- **Fights: kills 4-1, 18-4, 20-1, 8-0 and 4-1.** Our Vendetta (16/2 on the_line, 7/1 on galaxy) and Marcella (6/0 on galaxy) won every trade.
- **Taking 0-Strength fields:** the_line g2 5 captures to 2; galaxy 868 cluster gems to 784.
- **Stealing bags:** 161 (the_line r463), 71 (concentrated_wealth r405), 154 (galaxy), 66 (elkring) and 29 (geodes).
- **Clear count on the big map** (geodes 49-34), though at low value per clear.

**What in our code causes the gap.** All references are `bots/q24_combo/src/bot.py` line / `bots/c2_respawn/src/bot.py` line.
1. **Split captures.** In `choose_target` (l.1371 / 1390), a group whose reward is available scores ×1.5 (l.1420-1421 / 1439-1440). The claim discount for it is only ×0.6 (l.1423-1424 / 1442-1443), and the champion's current target gets ×1.3 (l.1429-1430 / 1448-1449).
   - So after a team clear every participant that had the group as its target stays to capture.
   - The reward is split 3 ways (22 → 7/7/8 on elkring), each extra capturer loses about 5-10 rounds, and the small bags then sit below `BANK_ANY = 30` / `BANK_NEAR = 15` (l.52-54 / 54-56). The result: late tributes and 88 carried gems at r500.
2. **The safety model charges the strong camp for the whole group's HP.**
   - `hl = G.hp_left()` sums every member, so 20 clusters add 2,400 HP to the elk's 2,400 on concentrated_wealth g0. `dmg_solo = s*(hl/dps)*...` (l.1394-1400 / 1413-1419).
   - Our attack order matches that pessimism: `pick_camp_in_range` (l.1349 / 1368) hits the lowest-HP camp in range, so clusters die first while the elk keeps hitting.
   - With s = 60, hl = 4,800, dps ≈ 55 and a 1,000 HP champion: budget 620, per cycle 568, cycles 8.4 > 4. Rejected.
3. **Shields and AoE are not in the model.**
   - `dps()` (l.1001 / 1020) adds the landing dash's single-target damage / 8, not its radius-1 hits on up to 9 clusters.
   - `choose_target` ignores HoR's 1.5×F and Varg's 2.5×F self-shields, which `cast_combat` (l.1027) does cast whenever a camp hits us.
   - Their HoR farms exactly this field solo; ours never targets it.
4. **HoR's build is split.** `BRUISER_PLAN` for HoR is Health 1.0 / Focus 1.0 (l.121). Focus scales both the shield and the landing (1.5×F each); their HoR stacked 11 Focus shards by r88.
5. **Draft.** Our `PRIORITY` (`draft.py`) has no sustain jungler. Varg was in our older priority list (2nd) and was replaced by the "top-20 meta core". The draft phase sees the whole map, but we pick the same five regardless.

**Lessons.**
- Against farming-first opponents, our fights win only where the gems are 0-Strength.
- Where gems sit behind one strong camp, an opponent with a sustain jungler takes 500-850 gems from a single group we never touch, and our kill advantage cannot make it up.

## 4. Our weaknesses exposed and testable hypotheses
| # | Weakness | Evidence | Impact | Code responsible (v3 / v4 lines) | Testable hypothesis (structure-keyed) |
|---|---|---|---|---|---|
| W1 | Several champions capture the same group | elkring 59 capture slots for 36 captures (1.64); concentrated_wealth 1.50; galaxy 1.31; theirs 1.00 everywhere. elkring r19, r38, r61: 3 champions per 22g capture. 88 unbanked gems at r500 | **major** (elkring, about 14 captures short) | `choose_target` status-1 scoring ×1.5, claim ×0.6, current ×1.3 (l.1420-1430 / 1439-1449) | **H9 "one capturer":** when `G.status == 1` and an ally claims G and is no farther from its spawn tiles, score G as 0 for this champion. When several are equally close, the lowest slot captures, the others retarget at once. Keep the ×1.5 only for the capturer. **Test:** champions per capture and clears per 100 rounds on all maps (gate); captured gems on maps with many identical Elk groups. |
| W2 | Elk + cluster fields rejected because the model counts every cluster's HP against the elk's damage | concentrated_wealth central g0 (Elk + 20 clusters, 71g): their 12 captures (852 gems) to our 0 | **decisive** (concentrated_wealth) | `hl = G.hp_left()` in `choose_target` (l.1394 / 1413); `pick_camp_in_range` lowest HP first (l.1349-1361 / 1368-1380) | **H11 "strong-camp-first":** order attacks by camp Strength (highest first, then lowest HP). In `choose_target`, compute exposure as Σ over strong camps of their HP/dps × Strength, plus the clusters that must die to reach them. Clusters cost time but no damage. **Test:** captures of groups made of 1-2 strong camps plus ≥ 4 clusters, and camp deaths, vs c2 on all maps. |
| W3 | Golem and big fields: shield and AoE kits are not credited | geodes: Varg's 6 Golem-field captures, 552 gems (0 camp deaths); ours 0. concentrated_wealth: their HoR 541 gems from the cluster field | **decisive** (geodes) | `dps()` (l.1001 / 1020) and `choose_target` ignore self-shield and AoE hits | **H12 "kit-aware safety model":** subtract the self-shield per turn (1.5×F for HoR, 2.5×F for Varg, every 8 turns) from the camp damage. Credit the landing AoE as k cluster kills when a group has ≥ 3 clusters within radius 1 of a landing tile. Pair with **H13**: on maps where ≥ 30% of gem value is in 0-Strength clusters packed next to a strong camp, HoR buys Focus Bruiser first. **Test:** HoR's gems per game and its deaths to camps. |
| W4 | No sustain jungler in the draft for strong-camp maps | Varg was their top gem earner in 3 of 5 games (370, 374, 643); Torsk's Varg did the same (517 on 02fields) | major | `draft.py` fixed `PRIORITY` (Vesper, Vendetta, Marcella, HoR, Ryth) | **H14 "structure-keyed draft":** at draft time (the whole map is visible, with 100x fuel), if ≥ 40% of the map's gem value sits in groups with Strength ≥ 60, pick Varg in place of our 5th pick (Ryth) or 3rd (Marcella). Write the decision to draft memory so play logic can give Varg the strong groups. **Test:** win rate and strong-group gems on those maps vs c2; never key on map names. |
| W5 | Late first tribute, and bags carried over several captures | First tribute r320 (concentrated_wealth), r171 (galaxy), r162 (the_line), r113 (geodes), r93 (elkring), all later than theirs. elkring: 88 carried at r500 | major (it cost r250 leads in 4 games) | `BANK_ANY = 30` / `BANK_NEAR = 15` (l.52-54 / 54-56) with split bags (W1) | Mostly a consequence of W1. If W1 alone does not fix it, test **H15:** bank at once when a capture gave ≥ 15 gems and the altar detour is under 12. Measure the first tribute round and the r250 race. |

**Their weaknesses to exploit.**
- **They do not fight back.** Kills 1, 4, 1, 0 and 1 per game, and **no wards at all**: our champions are never seen coming.
- Their carriers walk 71-161 gem bags across the map unescorted (the_line r463, concentrated_wealth r405). Focusing big carriers near their delivery altar would turn even their winning maps. Their HoR and Varg carried 71 and 92 gems in 8-10 turn channels at the same altars every time: (37,36) and (23,24) on concentrated_wealth, (28,13) on geodes. That is the "contest the delivery" idea (H1 in the 中国人能飞 note, V3L-3b).
- **On 0-Strength maps they are beatable 2-0 by our current bot,** so the fixes above only need to close the strong-camp gap.
