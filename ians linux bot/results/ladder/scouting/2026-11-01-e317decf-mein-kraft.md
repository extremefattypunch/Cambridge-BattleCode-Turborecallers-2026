# Mein Kraft (1532): ladder set e317decf, 1 Nov 2026, our v3, lost 0-5

- **Opponent:** Mein Kraft, rating 1532 (ours after the set: 1520).
- **Our version:** website v3 = `bots/q24_combo` (live 01:42-04:42 UTC). The set ran at 04:12 UTC. We were side A (team A) in all 5 games.
- **Record: 0-5.**
  - L 00gem_fields 270-1006 (r688, gems).
  - L 02treasure_box 0-1002 (r740, gems).
  - L 00galaxy 969-1005 (r1689, gems). Lost by 36.
  - L 00rows 557-1002 (r1461, gems).
  - L 00contest 400-1000 (r1465, gems).
- **Link:** https://2026a.battlecode.co.uk/game/match-groups/e317decf-ab4b-4980-a1b4-9565a0f3ec38
- **Sources:**
  - `results/ladder-games.jsonl` rows, and `matches/ladder/summary/<id>__A.json` for game ids 4b1659a9, 5b51290c, 2b51939c, f99a3ec9 and d8736f52.
  - `python3.12 -I tools/scout.py --group e317decf` gives every number marked "scout".
- **Method.** The stats hold no positions. Champion positions come from:
  - **Wards.** Our `try_ward` places a ward within 2 tiles of the champion, and only when it is more than 6 tiles from its previous ward, so a gap in the ward trail means the champion stayed within about 6 tiles.
  - **Other events.** Captures, clears, tributes, kills, deaths and shop tiles.
  - The helper scripts (timeline, ward trails, metric runs, ASCII map) live in the session scratchpad, not the repo.
  - Anything marked *speculation* is not directly observed.

## Set summary (scout)
| Map (size, picks) | Result | Gems r250 | r500 | r1000 | End | Them ahead for good from | Clears/100r us-them | K/D us | Gems lost to kills us/them |
|---|---|---|---|---|---|---|---|---|---|
| 00gem_fields (50x40, 5) | L | 0-304 | 99-758 | — | 270-1006 r688 | r52 | 1.89-6.98 | 5/5 | 14/85 |
| 02treasure_box (35x35, 5) | L | 0-188 | 0-537 | — | 0-1002 r740 | r120 | 2.03-18.92 | 2/7 | 83/27 |
| 00galaxy (93x93, 5) | L | 46-179 | 145-319 | 531-534 | 969-1005 r1689 | r971 | 2.72-4.14 | 19/2 | 49/273 |
| 00rows (50x50, 4) | L | 0-69 | 42-214 | 277-636 | 557-1002 r1461 | r124 | 2.87-3.63 | 0/0 | 0/0 |
| 00contest (50x50, 5) | L | 0-0 | 0-0 | 400-0 | 400-1000 r1465 | r1287 | 6.42-5.80 | 5/18 | 0/400 |

**First tribute, them vs us:** r52 vs r292; r120 vs never; r104 vs r168; r124 vs r414; r1063 vs r665.

## 1. Opponent profile

### Draft and roles
**Draft:** Vesper Vale, Tavi, Varg, Willow, Cassi & Issac on all four 5-pick maps (6 bodies). On 4-pick rows: Vesper, Tavi, Varg, Willow. Our draft was Vesper, Vendetta, Marcella, HoR, Ryth (`draft.py` PRIORITY). Vesper is a mirror pick.

| Champion | Role (from per-champion lines) |
|---|---|
| **Tavi** | **Main farmer and main killer.** Buys shards anywhere (passive), so it starts upgrading at r37-79 while still in the field.<br>Farming: collected 387 gems on gem_fields, 468 on rows and 600 on contest (3 monolith tributes of 200).<br>Killing: contest 11 kills / 0 deaths; 4,321 gold earned there. |
| **Vesper Vale** | Second farmer and capturer. Its +33% gold makes it the top gold earner on rows (3,051) and contest (3,069). |
| **Varg** | Farms wolf groups with splash and tanks with its shield: 10,750-20,000 shielding per game. Carried the monolith bags on contest (2 x 200, both killed by us). |
| **Willow** | Healer. Healing done: 18,516 on contest, 9,801 on rows, 7,029 on gem_fields, 4,243 on galaxy.<br>It also finishes kills: treasure_box 3 kills, gem_fields 2. It almost never farms: 4-14 clears and 12-206 gems a game. |
| **Cassi & Issac** | Extra bodies that clear and capture small clusters. Cassi's ranged stun and damage join fights. |

### Items: Jungle first, then every farming passive, then Power stacking
The shop order is the same on every map; only the timing moves with income.
1. **Jungle**, for the −30% camp damage: S shards for Tavi, Varg, Vesper and Issac; F for Willow and Cassi.
2. **Monster**, +15% to camps.
3. **Durability H** and **Treasure**.
4. **Capture** and **Prospector**.
5. **Power S, stacked:** 26 Power emblems on both rows and contest.

| Game | Their emblems by r500 / r1000 | Ours | Their first shard | First Jungle emblem |
|---|---|---|---|---|
| gem_fields | 7 / — | 1 / — | Tavi r39 (JunS x3, off spawn) | Tavi r148 |
| treasure_box | 5 / 8 | 5 / 9 | Cassi r63 | Vesper r100 |
| galaxy | 0 / 1 | 3 / 6 | Tavi r41 | Tavi r943 (no gold: gem-cluster map) |
| rows | 13 / 38 | 6 / 22 | Varg r42 (JunS x5 + MonS in one visit) | Varg r42 |
| contest | 20 / 38 | 6 / 21 | Tavi r37 | Vesper r40 |

**Altar locks: bought 4-8 a game, about 1-3 placed.** First buys came at r56 (Willow, gem_fields), r63 (treasure_box), r77 (contest), r419 (rows) and r1039 (galaxy). They never buy TP crystals.

### Farming: the whole team on the map's best objective
They go to the highest-value groups and keep them under constant rotation with 2-6 bodies nearby.
- **gem_fields: the two 71-gem Elk + 8-cluster groups.** g5 sits 5 dash-steps from *our* spawn, g4 5 from theirs.
  - Captured 12 times: g5 at r39, 148, 364, 442, 521 and 605; g4 at r83, 200, 310, 411, 489 and 657. That is about 852 of their 1,006 gems.
  - Tavi's wards sat at (27-33, 12-19), on our g5, from r35 to r264.
- **treasure_box: the 16 single gem clusters around the only altar (17,17).** 140 clears and 134 tributes of 7.5 gems. All 6 bodies were inside the inner box: 185 of their 239 wards were in the altar zone.
- **galaxy: the central cluster groups.** g6 (35 gems), g7 and g8 (14 each), right next to both altars.
  - Capture counts, theirs vs ours: g6 18 vs 4, g7 16 vs 5, g8 11 vs 8. 45 of their 63 captures were mid.
- **rows (no fights at all): their own three Wolf x3 groups**, g1, g3 and g5 (12-26 gems each), 53 captures. Varg (Jungle + Monster at r42) and Tavi (Jungle r79) did them solo from r37.
- **contest: the two 200-gem monoliths**, taken 7 times: r596, 756, 978, 1026, 1248, 1313 and 1426.
  - They took them as a team: Willow healing 18,516, Varg shield 15,250, Jungle on all 6 bodies.
  - It still cost them 8 champion deaths to camps.
- **Tempo, theirs vs ours.**
  - Clears per 100 rounds: 6.98 vs 1.89 (gem_fields), 18.92 vs 2.03 (treasure_box), 4.14 vs 2.72 (galaxy).
  - Camp damage taken per 1k dealt: 235 vs 723, 184 vs 485, 69 vs 108, 85 vs 211, and 327 vs 234 on contest, the one game where theirs was worse (monoliths).

### Tributes
**Bag size follows the objective.**
- Tiny on treasure_box: 7.5 mean, every 4 rounds.
- About 23-30 on gem_fields, galaxy and rows.
- 200 on contest (monolith).

**First tribute:** r52 (78 gems from the g5 capture at r39), r104, r120 and r124. On contest it waited until r1063, because nothing but monoliths gives gems there.

**Altars:** they bank at the altar nearest the objective, including ours. On gem_fields, 20 of their 34 tributes (631 gems) were at #2 (32,10), the altar on our side.

### Fight behaviour
- **They fight where they farm: zone control around their objective.** They do not hunt across the map.
  - treasure_box: all 7 of our deaths were at the inner-box entrance. 5 of them were at (13,21): Vendetta r278 carrying 17, Marcella r291 carrying 16, Ryth r354, HoR r667 carrying 21 and Ryth r689 carrying 20.
  - contest: Tavi's 11 kills were all at (19-37, 16-30), the ring between the gold-cluster field and the central altars.
- **Kills come from Tavi's stun plus focus fire**, with Willow healing their side. Tavi took only 100 champion damage in 740 rounds on treasure_box and 1,981 on contest while dealing 21,279.
- **Spread out, they lose fights.**
  - galaxy, a 93x93 map where they farmed in 1-2s: 2 kills vs 24 deaths, and we stole 273 gems.
  - contest: 2 x 200-gem monolith carriers walked into our HoR and Vesper (r644, r765).

### Adaptation across maps
It is a value model, not a fixed script.
- They identify the map's richest objective (elk groups, an altar-ring cluster field, the central clusters, monoliths) and commit the team to it.
- On rows, with no rich objective (the 470-gem Monolith + 10-cluster centre g6 was never touched by either side), they simply out-farm their own half.
- Draft and build never change.

### Their weaknesses (observed)
1. **Carriers die when the team spreads out.** galaxy: 24 deaths, 273 gems lost to us. contest: 400 gems lost (2 monolith carriers).
2. **Stuck champions.** galaxy: Cassi quiet r64-210, Issac quiet r152-335 standing at our g1 (see §2), Varg parked at g0 (30-32, 70-72) from r269 to r539.
3. **Fuel exhaustion:** 21 on gem_fields, 37 on treasure_box, 7 on galaxy.
4. **Camp deaths at monoliths:** 8 on contest.

## 2. Per game

### 00gem_fields: L 270-1006 (r688)
**Map.** 50x40, rot180. Spawns: ours (20-22, 14-16), theirs (27-29, 23-25), only 7 tiles apart. Walking routes are long: hole lines separate each spawn from the elk group 5 dash-steps away.
- **Centre:** g5 (28,15) and g4 (21,24), each Elk + 8 gem clusters, 71 gems.
- **Altars:** #2 (32,10) on our side, #1 (17,29) on theirs, plus #3 (45,4) and #0 (4,35) in the corners.

**Decisive moments.**
- **r32-52:** Cassi cleared g5 (r32), Tavi captured it alone for 71 (r39), bought Jungle shards on the spot (r39) and tributed 78 at #2 (r52).
- **r11-36:** our five went west and north-west instead.
  - Wards: (13,19), (14,17), (15,24), (16,24) at r11; (21,23), (22,22) at r21-22; (24,20), (25,20) at r30-36.
  - Targets: single 7-gem clusters (g14, g0, g8) and the other elk group, g4.
  - Vesper cleared g4 at r56, but Varg captured it at r83.
- **r87-203:** Vendetta won skirmishes in the gap between the spawns: Cassi & Issac r87, Vesper r94, Varg r203. Its totals for the game were 0 clears and 7 gems.
- **r250: 0-304.**
  - Our first gem tribute came at r292: Ryth 35 and Vesper 36 at r300, both from the single g5 capture at r260 (Vesper + Ryth, taken 35 rounds after Cassi's clear).
  - Both carriers walked from g5 past altar #2 to #3 (45,4): Vesper's wards (28,3), (39,2), (44,3); Ryth's (30,9), (34,4), (44,3). That is about 15 extra tiles each.
  - *Speculation:* #2 was enemy-locked (they placed about 2 locks; Willow bought one at r56). `pick_altar` skips locked altars, and `break_lock` only hits a lock from an adjacent tile.
- **r395-398:** HoR and Ryth died to Willow and Vesper at (20-22, 20-23).
- **r500: 99-758.** Mein Kraft reached 1,006 at r688.

**Root.** They owned both 71-gem elk groups from r39, with Jungle shards in hand: 852 gems from those two groups. Our solo farm model never committed a group to either (see §3 gap A). We farmed 7-gem clusters at 1.89 clears per 100 rounds.

### 02treasure_box: L 0-1002 (r740)
**Map.** 35x35. Spawns side by side: ours (12-15, 30-33), theirs (19-22, 30-33). One altar, (17,17), sits inside an inner walled box (12-22, 12-22) whose entrances are at (16-18, 22) and (16-18, 12). It is surrounded by 16 single gem clusters, g0-g15, 1-3 tiles away. Wolf + gold flanks are outside.

**Their play.** All bodies inside the box from about r100. 140 clears, 134 tributes of 7.5 gems, 185 wards in the altar zone.

**Ours.**
- We farmed the outer Wolf + 2 Gold groups (4 gems, 80 gold) and the Wolf x4 g16.
  - We were ahead on gold: 2,338 vs 1,724.
  - We captured 136 gems and lost 83 of them to champion kills.
  - **We never tributed: 0 tributes in 740 rounds.** We ended carrying 64 gems.
- Our carriers entered the box one at a time and died at the entrance: Vendetta r278 (17 gems), Marcella r291 (16), Ryth r354, HoR r667 (21) and Ryth r689 (20), all at (13,21).
- The 16 altar clusters (7 gems, 120 HP, strength 0) were never touched by us: 0 clears out of 140.

**Root.**
- A contested single altar: banking is a solo decision (`bank_now`/`do_tribute`), so carriers arrived alone into 3-6 enemies.
- `Group.value = gems + 0.25*gold` made the 80-gold wolf flanks (value 24) outrank the 7-gem altar clusters (value 7, at path distance about 30).

### 00galaxy: L 969-1005 (r1689); lost by 36
**Map.** 93x93. Spawns are corner to corner, (3-5, 3-5) and (87-89, 87-89). Altars at (38,46) and (54,46).
- **Gem groups:** central g6 (5 clusters, 35 gems), g7 and g8 (14 each), and our-side g1 (60,20) and their-side g0 (32,72) with 21 each.

**Decisive moments.**
1. **r0-500: they held the centre.** 179-46 at r250 and 319-145 at r500. g6 was theirs 18 times, ours 4 (first at r814).
2. **Two capture standoffs cost us about 460 champion-rounds.**
   - **Vesper.** Issac cleared g1 at r152 and then stood next to it (wards at (58-59, 23-26) every 10 rounds) until Ryth killed Cassi at r335, which took Issac down via the linked death.
     - Vesper's ward trail stops at (54,21), r156, and resumes at r347. Scout lists it as quiet (no metric changes) from r74 to r339.
     - So Vesper stood within 6 tiles of g1 for about 190 rounds without hitting anything, and captured g1 at r339, 4 rounds after Issac died.
   - **HoR.** HoR cleared g0 (their side, 32,72) at r269. Its trail stops at (31,72), r275, and resumes at (26,63), r542; it is quiet r269-578.
     - Varg's wards sat at (30-32, 70-72) from r269 on.
     - Nobody captured g0 until Varg did at r539, right after HoR left.
   - **Mechanism, read from the code:** see §3, gap D.
3. **r746-1300: we won the fights 24-2** (Vendetta 7-0, Ryth 5-0): 273 gems stolen, and the race reached 531-534 at r1000.
4. **r1018: the swing that decided the game.** Vesper captured g1 for 42 at r957, then spent 61 rounds between (54,28), (59,37) and (59,29) without banking. Willow was at (58,37) and (54,38) at r999-1009.
   - Cassi killed Vesper at (62,34) with 42 at r1018 and tributed 42 at r1034: an 84-gem swing in a 36-gem loss.
5. **End.** HoR carried 35-70 gems from r1569 to r1646 before banking 70. At r1689 we were at 969 tributed + 36 carried, against their 1,005.

**Root.**
- They owned the centre early.
- We gave away about 460 champion-rounds in capture standoffs, and 84 gems in one carrier death.
- Our superior fighting nearly rescued it.

### 00rows: L 557-1002 (r1461)
**Map.** 50x50, rot180. Spawns at (2-5, 2-5) and (44-47, 44-47). Each side has three Wolf x3 groups along its edge: ours g0 (18,4), g2 (32,4) and g4 (42,4). There are two 0-gem GoldCl x4 groups, g7 (48,15) and g8 (1,32), and the centre g6 (Monolith + 10 clusters, 470 gems) was never touched. **0 kills either side.**

**Decisive: our r0-289 opening.**
- Our four champions orbited the two 0-gem gold groups, 50 tiles apart. Vesper's trail: (14,14) → (30,14) → (45,16) [g7] → (36,18) → (27,24) → (20,20) → (12,20) → (3,29) [g8] → (22,22) → (38,17) → (45,16) [g7] → ...
- Captures in that window: g7/g8 at r56 (3 champions sharing 80 gold), r72, r136 (3 champions), r152, r213 (3) and r229. **0 gems in 289 rounds.**
- Our first gem capture was g0 at r289, 55 rounds after our first emblem (Vendetta, Bruiser S, r234). The first tribute came at r414.
- Meanwhile Varg (Jungle + Monster bought at r42) and Tavi (Jungle at r79) farmed their Wolf x3 groups from r37: 100 gems tributed by r250.

**Then.** An even-ish farming race with Bruiser items against Jungle → Monster → Treasure → Capture → Prospector → Power:
- they made 53 captures to our 42, and earned 9,896 gold to our 6,720;
- their camp damage taken per 1k dealt was 85, ours 211.

**Root.**
- Our value model (gold-only groups valued at any distance; Wolf x3 groups rejected solo) wasted the first 289 rounds.
- Their economy build compounded the gap.

### 00contest: L 400-1000 (r1465)
**Map.** 50x50. Only gold clusters (GoldCl x2/x4, 0 gems) plus two 200-gem monoliths, g0 (17,31) and g1 (32,18). The central altars are at (24,25) and (25,24).

**Decisive moments.**
- **r0-596: 0-0 on gems.** They out-farmed the gold clusters: 3,505 vs 1,358 gold at r500. Tavi went 4-0 in r180-309 at (19-26, 18-25).
- **r596 and r756:** Varg captured the monoliths. We killed both carriers:
  - HoR killed Varg (200) at (26,26), next to the altar, at r644, and tributed 200 at r665;
  - Vesper killed Varg (200) at (26,13) at r765 and tributed 200 at r807.
- **From r978 they kept capturing monoliths:** r978, 1026, 1248, 1313, 1426.
  - None of these 5 carriers died. Our champions that came near were killed: Tavi killed Vendetta at (37,19) r1021 and Vesper at (27,16) r1162; their Vesper killed Ryth (22,30) r1069 and Ryth, Marcella and HoR at (22-31, 22-31) r1417-1434.
  - *Speculation:* the carriers moved with escorts. No positions show this directly.
  - They tributed 5 x 200 between r1063 and r1466.
- We never attacked a monolith.

**Root.**
- A map whose gems are almost all behind monoliths. They have a team-clear capability (healer + shield + Jungle); we have none.
- Our only answer was intercepting carriers. It worked twice and then failed against escorted carriers and Tavi (11-0).

## 3. Their strategy vs ours

### Where theirs was superior
| Gap | Size | What in our code causes it (`bots/q24_combo/src/bot.py`) |
|---|---|---|
| **A. Committing to rich, defended camp groups.** | gem_fields: they took the two 71-gem elk groups 12 times, we took one once. rows: no Wolf x3 group taken by us before r289. contest: monoliths 7-0. | **The `choose_target` chip model.**<br>At base stats the hit-and-run check (`cycles = hl / per_cycle`, `continue` when `cycles > 4`) rejects:<br>• Elk + 8 clusters for Vesper (6.4 cycles), HoR (6.7) and Vendetta (4.1);<br>• Wolf x3 + 3 gold for all four champions on rows (4.6-8.0).<br>Marcella and Ryth pass, but with `extra = cycles*30` ≈ 112-117 rounds of cost. That makes the 71-gem group score about 0.53, the same as a 7-gem cluster at about 7 tiles (0.47).<br>**Claims cannot start a team clear.** The claim help (`tdps = dps + c*55`, `dmg /(1+c)`, ×1.2 if not `solo_ok`) only applies once some ally already targets the group.<br>**Monoliths:** `budget = maxhp - 200*dmg_mult*(5+1) - 80` < 0 for every champion, so they are rejected outright. |
| **B. Killing the camp that hurts first.** | Camp damage taken per 1k dealt: gem_fields 723 vs 235, treasure_box 485 vs 184, rows 211 vs 85. | **`pick_camp_in_range` hits the lowest-HP camp in range.** In Elk/Wolf + cluster groups that means the harmless 120-HP clusters first, while the elk or wolf keeps hitting.<br>**`hl` counts cluster HP.** The chip model's `hl` includes that cluster HP as "exposure", which makes the rejection in A worse. |
| **C. Economy build.** | Emblems by r500: 13 vs 6 (rows), 20 vs 6 (contest), 7 vs 1 (gem_fields). Gold: 9,896 vs 6,720 (rows), 10,872 vs 6,042 (contest). | **`shop()` calls `bruiser_item()` first, and it never returns None for our five champions:** `BRUISER_PLAN` covers all of them, and `JUNGLE_FIRST = False`. So the Jungle → Monster → Power fallback is dead code for our draft.<br>No Treasure, Prospector or Capture is bought outside `no_tribute`. (T25 Jungle-first was rejected for fight blowouts; Q28 variants are queued.) |
| **D. Capture standoffs.** | galaxy: Vesper about 190 and HoR about 270 quiet rounds next to cleared groups with one enemy parked on them. | **The capture branch is `if G.status == 1: if G.tiles.is_set(pos): return`.** It waits forever: there is no timeout and no ban.<br>**`handle_enemies` never resolves the standoff.**<br>• Engage: a lone Issac or Varg gives ratio ≈ 1.0-1.1, above `FIGHT_ENGAGE` 0.85, so we don't engage.<br>• "Clearly losing": `best_ratio` is not above 1.6 and the enemy count is not above `n_allies + 1`, so we are not clearly losing either.<br>• Stall breaker: after 25 retreat-turns `self.holding` makes `handle_enemies` return False, so the champion walks back onto the tile and waits.<br>Their bot waits too. Neither side's capture completes until one leaves. *(The champion was quiet; whether it oscillated between retreat and hold is not observable. Either way no capture completes.)* |
| **E. Contested single altar: solo banking.** | treasure_box: 0 tributes, 5 deaths at (13,21) carrying 16-21. galaxy: Vesper carried 42 for 61 rounds near Willow and Cassi, then died. | **Banking is per champion.** `bank_now` / `bank_detour` thresholds, then `do_tribute`.<br>**The only altar-danger signal is `ALTAR_DANGER_PEN = 12`**, from the champion's own sightings, and it doesn't help when there is only one altar.<br>**`handle_enemies` runs before the tribute decision.** A carrier facing 2+ enemies regroups (`group_balance` → `dis` → `retreat`) and comes back next turn, alone again. Nothing makes carriers wait for or travel with allies. |
| **F. Value of zero-gem gold groups.** | rows: 6 captures of 0-gem groups in r0-289 (3 of them split three ways), 0 gems. | **`Group.value = gems + 0.25*gold`** gives GoldCl x4 (80 gold) a value of 20 with no distance cap. Zero strength means `solo_ok`, so the Wolf x3 rejection in A leaves these the best eligible targets.<br>The ×0.3 claim discount did not stop three champions sharing one capture: status 1 gets ×1.5×0.6 = ×0.9. |

### Where ours was superior
- **Fighting a spread-out opponent.** galaxy 24-2 (Vendetta 7-0, Ryth 5-0; 273 gems stolen). gem_fields: Vendetta's 4 early kills.
  - This comes from the q24 `group_balance` commit rule and `focus_bias`: carriers and channellers are tier 0 targets, with an engage bonus of carried gems/100.
- **Carrier interception at the altar.** contest: two 200-gem monolith carriers killed at (26,26) and (26,13), giving our only 400 gems.
- **Gold on gem-light maps** (treasure_box +614, galaxy +2,385). Vesper's 33% and the gold weight in `Group.value` help here, but it was irrelevant to the result in all five games.

## 4. Our weaknesses exposed
| # | Weakness | Evidence | Games | Impact |
|---|---|---|---|---|
| W1 | **No team commitment to rich defended groups** (elk + clusters, Wolf x3, monoliths). The solo chip model rejects them and claims cannot bootstrap. | gem_fields: 71-gem groups captured 12 times by them, once by us. rows: first gem capture r289. contest: monoliths 0 vs 7 (1,400 gems). | 3 | decisive |
| W2 | **Lowest-HP-first kill order in mixed groups.** It wastes exposure on 0-strength clusters, and the chip model counts cluster HP as exposure. | Camp damage per 1k dealt 723/485/211 vs 235/184/85 (gem_fields, treasure_box, rows). | 3 | major |
| W3 | **Solo banking into an enemy-held altar.** | treasure_box 0 tributes, 5 carrier deaths at (13,21). galaxy r1018: Vesper's 42 became their 42. | 2 | decisive (treasure_box, galaxy) |
| W4 | **Capture standoff with a single enemy on a cleared group.** No timeout, no fight. | galaxy: about 190 (Vesper, g1) plus about 270 (HoR, g0) idle champion-rounds, in a game lost by 36. | 1 | major (probably decisive in galaxy with W3) |
| W5 | **Zero-gem gold groups with no distance cap**, chosen over (rejected) gem groups. | rows: 4 champions orbited g7 (48,15) and g8 (1,32) for 289 rounds, 0 gems. | 1 | major |
| W6 | **Bruiser-only build:** no camp-efficiency passives. | Emblems by r500: 6 vs 13 and 6 vs 20; gold -32% / -44% (rows, contest). | 3 | major |
| W7 | **Carriers bypass the nearest (probably locked) altar** and walk 15+ extra tiles. | gem_fields r260-300: Vesper and Ryth passed within about 4 of #2 (32,10) and banked at #3 (45,4). | 1 | minor |

## Testable hypotheses (structure-keyed; no map or team names)
1. **H-killorder (W2; cheap, local, high value).**
   - **Change.** In `pick_camp_in_range`, choose the camp with the highest `strength / health` among those in range. 0-strength clusters come last, with lowest HP as the tie-break.
   - **Chip model.** In `choose_target`, compute exposure from the HP of strength > 0 camps only: `hl_dmg / dps` for the damage term, while total time still uses all HP.
   - **Metrics.** Camp damage taken per 1k dealt (target: -25% on elk/wolf + cluster groups), clears per 100 rounds, and first capture of mixed groups.
   - **Gate.** `--maps all` (both sides).
2. **H-lead (W1; distinct from the team-clear bootstrap T23/T30).**
   - **Change.** If a group's `cycles` is at most 6 for a champion and at least one ally is within 8 tiles with no strength > 0 target, that champion claims the group with the cycles check relaxed to 6. The ×1.2 not-`solo_ok` claim bonus and `tdps + c*55` then pull the ally in.
   - **Metrics.** Captures of multi-elk and Wolf x3 groups before r300; rounds to first gem capture; champion deaths to camps (must not rise).
3. **H-standoff (W4).**
   - **Change.** Count rounds standing on a status-1 group whose capture has not completed while an enemy champion is within 2 of the group's tiles.
     - After 12 such rounds: if `group_balance` near ratio ≥ 1.0, engage that enemy with `FIGHT_ENGAGE` + 0.3;
     - otherwise `banned[G.idx] = rnd + 60` and retarget.
   - **Metrics.** Champion-rounds with no metric change for 100 or more rounds (scout `idle`); captures per game.
4. **H-escort (W3).**
   - **Change.** If at least 2 enemies were seen within 8 of the chosen altar in the last 40 rounds (`altar_seen`, kept per enemy count) and we carry 15 or more, wait at a tile 9-12 path steps from the altar until an ally is within 4, then go together.
     - Alternative 1: re-pick an altar with no sightings if it is at most 20 path steps farther.
     - Alternative 2: with a single altar, bank only when `group_balance` near ≥ 1.0.
   - **Metrics.** Gems lost to champion kills; tributes per game on maps with one altar; carrier deaths within 6 of an altar.
5. **H-goldcap (W5; same family as EFW's H-goldcap, now with a second map of evidence).**
   - **Change.** A group with `gems == 0` is valued only within about 12 path tiles of the champion (or of its next gem target), unless in `gold_play()`.
     - Also: no second champion joins a 0-gem capture. Apply a ×0.3 claim factor at status 1 when `G.gems == 0`.
   - **Metrics.** 0-gem captures before r300; gems at r300.
6. **H-ecopassive (W6; a Q28 variant keyed on own observations).**
   - **Change.** If no enemy champion has been seen for 250 rounds (a pure farming race), the next emblem is Jungle (then Monster) instead of the next Bruiser.
   - **Metrics.** Gold at r1000 and camp damage per 1k on no-contact games; the fight K/D on contact games must not fall.
7. **H-intercept (strengthen what worked).**
   - **Change.** When an enemy carrying 100 or more gems is seen (`e.gem_count()`), write it as team focus with a long TTL (about 40 rounds) and send up to 2 allies within 25 tiles to the altar it is nearest to. Today `FOCUS_TTL = 3`, and only champions already within 8 react.
   - **Metrics.** Gems we steal per game on monolith or jackpot maps.

**Opponent-specific notes (for ladder expectations, not for fixes).**
- Mein Kraft is a complete team bot: objective selection, Jungle-first economy, healer and shield sustain, zone control.
- Expect to lose to it until W1-W3 are fixed.
- Our real edge is killing its carriers when it spreads out, on big maps.
