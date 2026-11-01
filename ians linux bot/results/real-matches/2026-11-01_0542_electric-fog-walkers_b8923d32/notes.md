# Electric Fog Walkers (1511): ladder set b8923d32, 1 Nov 2026, our v4, won 4-1

- **Opponent:** Electric Fog Walkers, rating 1511 (ours after the set: 1526).
- **Our version:** website v4 = `bots/c2_respawn` (activated 04:42 UTC). The set ran at 05:42 UTC. We were side A (team A) in all 5 games.
- **Record:** **4-1.**
  - W 01elk_arena 1008-72 (r1352, gems).
  - **L 02harvest 460-1005** (r1421, gems).
  - W 02stalactites 1045-383 (r437, gems).
  - W 01starfish 987-618 (r2000, tiebreak on gems).
  - W 01the_farm 870-25 (r2000, tiebreak on gems).
- **Link:** https://2026a.battlecode.co.uk/game/match-groups/b8923d32-049f-41cf-af18-cc528771a122
- **Sources:** `results/ladder-games.jsonl` rows, `matches/ladder/summary/<id>__A.json`, and replay zips in `matches/ladder/replays/<id>.repl26a`.
  - Our `team-a.stdout` is empty in all 5 games: the live bot prints nothing.
  - Map layouts and our solo-model verdict per group come from the census dumps `matches/q26-census/<map>.stdout.txt` (MAPDUMP / GROUP / MODEL lines).
- **Method:** the summaries hold no per-round positions, so champion positions are inferred:
  - **Wards:** a ward lands within 2 tiles of its placer. Our bot places one every 10 rounds when it has moved more than 6 tiles, so ward positions give a rough route.
  - **Other events:** camp clears, captures, tribute tiles, shop tiles and kill or death positions.
  - **HP:** estimated as damage taken minus healing, reset at death. Anything below marked *speculation* is not directly observed.
  - Scripts are in the session scratchpad, not the repo.

## Game summary
Each team drafts 3-5 champions. Champions kill camps, capture them for gems and gold, and tribute gems at altars; first to 1,000 tributed gems wins, otherwise gems and then gold decide at r2000. Map sizes in this set: 30x30 (stalactites), 50x40 (the farm), 50x50 (elk arena, starfish) and 100x100 (harvest).

## 1. Opponent profile
**Draft: fixed, identical on every map.** Stellar, Ren, Marcella, Ryth, Varg, truncated to the pick count:
- 3-pick (the farm): Stellar, Ren, Marcella.
- 4-pick (stalactites): adds Ryth.
- 5-pick: adds Varg.

We drafted Vesper, Vendetta, Marcella, HoR, Ryth (`draft.py` PRIORITY). Mirror picks: Marcella, and Ryth on 5-pick maps.

**Champion roles (from per-champion lines):**
- **Stellar:** ranged burst caster. Spells are 2xF single target and 1.4xF AoE, both range 4.
  - Its Focus stacks to Power Focus x15 (starfish, harvest), which makes it their main killer late.
  - Kills on us: harvest 1/1, starfish 8 (0 of them before r650), stalactites 2.
- **Ren:** the most active farmer, monster damage on 24-48% of rounds (the highest on either team). It is also their main skirmisher (starfish 6 kills).
- **Marcella and Ryth:** solo farmers.
- **Varg:** splash farmer for wolves and clusters. Varg and Stellar burst the elk-arena centre in the opening.

**Items: one passive emblem first, then Jungle, Bruiser, Durability, and Power (or Monster) stacking.** The order is the same in every game; only the timing moves with income.

| Champion | 1st emblem | 2nd | 3rd | 4th | then |
|---|---|---|---|---|---|
| Stellar | Prospector F (r37-79; 4-5 shards in one visit) | Jungle F (r58-518) | Bruiser F | Durability H | Power F x n |
| Ren | Jungle H (r90-1027) | Bruiser H | Durability H | — | Power F x n |
| Marcella | Prospector F (r154-447) | Jungle F | Bruiser F | Durability H | Monster F x n |
| Ryth | Jungle H (r264-410) | Bruiser H | Durability H | — | Power S x n |
| Varg | Treasure S (r173-524) | Jungle S | Bruiser S | Durability H | Power S x n |

- **Every champion owns a Jungle emblem (-30% damage from camps) by r300-750.**
- **They never buy altar locks or TP crystals.** Ward counts are like ours (60-115 per champion), except on stalactites (16 in total).

**Farming pattern: strictly solo, on their own half, rotating a fixed circuit.**
- **Solo captures:** 95/95 on elk, 77/77 on harvest, 25/26 on stalactites, 130/132 on starfish, 10/11 on the farm. Ours: 83/121, 36/45, 3/7, 40/46, 28/33.
- **Harvest:** 68 of their 77 captures were on their half, for 959 gems. Ours: 30 of 45 on our half, for 343 gems, and 13 of those 30 were 0-gem gold clusters.
- **Their per-champion circuits (harvest):**
  - g5 (94,69) x17; g13 (70,70) x13; g15 (65,60) x10;
  - g17 (62,41) x9; g3 (95,26) x9; g7 (91,42) x8;
  - our-side g16 (37,58) x8.
- **Tempo accelerates as Power and Monster stacks land.** Clears per phase, theirs vs ours:
  - harvest 10/11/27/30 vs 8/8/16/13;
  - starfish 6/18/40/83 vs 3/4/8/19.
- **Gem clusters with Prospector:** +25% of their own share.
  - Stalactites: g8 (168 gems) gave their solo Marcella 210, and g7 (77) gave Stellar 96.
  - Harvest: their wolf+cluster groups give 12 gems against our 11.

**Tributes: big bags, delayed, at the nearest altar.**
- Mean tribute size, theirs vs ours:
  - elk 72 vs 25;
  - harvest 33.5 vs 20;
  - stalactites 54.7 vs 80;
  - starfish 32.5 vs 31.
- Starfish: no tribute at all until r556; at r500 they carried 52.
- Stalactites: bags of 205 and 210 were carried to the single central altar. Both carriers were killed beside it (see §2).
- Harvest: they used their home altar (51,80) x12 and the central (61,38) x12.

**Fights: opportunistic and ungrouped.**
- **No hunting, spawn-camping or altar locks observed.** Their kills on us come from:
  - champions defending their own farming zone: harvest kills at (60,62), (38,52), (52,58), (53,60);
  - Stellar's range-4 burst once it is Focus-stacked.
- **They lose grouped fights badly.** Elk: K/D 6/25, with their champions arriving one at a time and dying at their spawn exit (27-33, 21-25).
- **Carrier kills on us are incidental:** starfish Marcella 51 at (21,47) by Stellar, HoR 55 at (20,20) by Ryth.
- **They do not contest altars and do not break our locks.** (Whether they could is unobserved; none of our locks is logged.)

**Adaptation across the 5 maps: none.** Same draft, same build order, same solo circuit. Two map-specific failures:
- **The farm: their 3 champions froze for about 1,500 rounds.** Positions (24-26, 16-17); sources: ward placements every ~10 rounds from r280 (Ren), r470 (Marcella) and r520 (Stellar) to the end, with zero activity. They carried 44 + 40 + 52 = 136 gems.
  - The spot is just south of the wall row y=19, whose only gap (23-26, 19) is the wolf + gold group g16.
  - The gap leads to the two central altars (23,22) and (26,22). Nobody ever cleared g16.
  - *Speculation:* their tribute pathing does not treat live camps as obstacles.
- **Stalactites:** 205- and 210-gem bags walked into our champions at the central altar.

## 2. Per game
Gem race = tributed gems, us-them.

| Map (size, picks) | Result | r250 | r500 | r1000 | End |
|---|---|---|---|---|---|
| 01elk_arena (50x50, 5) | **W** | 0-72 | 216-72 | 648-72 | 1008-72 r1352 |
| 02harvest (100x100, 5) | **L** | 50-78 | 178-145 | 380-596 | 460-1005 r1421 |
| 02stalactites (30x30, 4) | **W** | 399-188 | — (ended r437) | — | 1045-383 |
| 01starfish (50x50, 5) | **W** | 17-0 | 147-0 | 283-72 | 987-618 r2000 |
| 01the_farm (50x40, 3) | **W** | 21-25 | 54-25 | 231-25 | 870-25 r2000 |

### 01elk_arena: W 1008-72
**Map.** One gem source, g0 (24,24): 2 elks + 6 gem clusters, 72 gems, str 120. Altars at (22,22) and (27,27), spawns at (12-15, 23-26) and (34-37, 23-26). Everything else is gold clusters.

**Their opening.** Stellar went straight to the centre (monster damage 1,624 in r0-40). Varg cleared g0 at r38, Stellar captured it at r44 for **72** and tributed at (27,27) at r65.

**Ours.** Our solo model rejects g0 for every champion (census: REJECT, cycles 19-42). Our 5 champions farmed gold clusters g3, g5, g19, g23, g25, g27 and g18 instead: **29 zero-gem captures in r0-245.** They did win the gold race: 626 to 550 at r100, 1,745 to 1,232 at r250.

**Turn.**
- r225: their Marcella cleared g0.
- r231-241: Vendetta killed Stellar and Marcella at (27,23); Ryth killed Ren and Ryth at (31,23).
- r248: we captured *their* clear (Vesper + Marcella + HoR, 24 gems each) and banked at r252-253.

**Then.** 13 more g0 captures, every 75-100 rounds, by 1-5 champions. They never retook it.
- Kills 25-6. Vesper went 11/0, mostly at (27-33, 21-25), at their spawn exit.

**Root.**
- Won by grouped fights at the centre, after a stolen capture.
- Lost the opening tempo (0-72 for 250 rounds) because nobody will commit to a group the solo model rejects.

### 02harvest: L 460-1005 (the loss)
**Map.** 180-degree symmetric. Spawns: ours (10-12, 12-14), theirs (87-89, 85-87).
- **Elk groups:** g12/g13 15 gems; g14/g15 29 gems.
- **Wolf groups (11 gems):** g4, g5, g6, g7, g16, g17. g2/g3 are wolf + 2 gold for 4 gems.
- **Golem groups (43-57 gems):** g8, g9, g18, g19.
- **Centre g20:** 114 gems, 2 golems.
- **Gold clusters (0 gems, 20 gold):** g10 (26,8) next to us, g11 (73,91) next to them.
- **Our solo model:** Vesper (dps 50.6) and HoR (48.8) reject every elk group (cycles 5.0-5.5 > 4). Nobody can take golems or g20.

**Decisive mechanism 1: Vendetta's HP-band loop (r38-474).**
- **r29-38:** Vendetta, Marcella and Ryth killed the elk group g12 (29,29). Vendetta took 7 x 60 = 420 camp damage, leaving it at about **580/1000 HP (58%)**. It received no healing until r475.
- **r64-470:** it captured the gold cluster **g10 (26,8) every 57 rounds** (r71, 128, 185, ... 470) for 20 gold and 0 gems each, idle in between.
- **Ward trail, each cycle:**
  1. (24,10), then (22,19) and (32,29), heading north-east;
  2. back via (28,24) and (20,14) to g10 just as it respawns.
- **Mechanism, read from the code:** see §3, gap A. The g11-then-g10 alternation matches the ward trail and the 57-round cadence (50 respawn + 2 to kill + 5 to capture).
- **Exit:** at 160 gold the `rich` recall fired (r470). Vendetta shopped at r475, healed to full, and only then farmed gems (g14, g16).
- **Recurrences:**
  - Vendetta was back in the band r589-812, capturing g10 again (r634, 691, 748);
  - r1034-1401, capturing **g11 (73,91), beside the enemy spawn, 5 times** (r1143-1374; wards at (62,72)-(75,89));
  - Ryth (band r958-1114) took g11 at r1029 and r1086; HoR at r526 and r585.
- **Total: 22 zero-gem captures (13 at g10, 9 at g11).** Vendetta collected 79 gems in 1,421 rounds (their worst champion: 173).

**Decisive mechanism 2: incursions into their half, while our own half went unfarmed.**
- **Vesper:** 0 monster damage in r0-500 and only 4 clears all game.
  - Wards (19,17), (26,24), (33,34), (41,44), (50,51), (57,56): it walked to the enemy half, fought there, recalled at r140-160 and r240-260, and repeated.
  - Its one kill was Stellar carrying 32 at (66,54) at r337, banked at (48,19) at r389.
  - It died at r473 at (38,52) to Marcella.
- **Marcella:** r1050-1200, three trips toward (46,44)-(56,54), taking **4,400 champion damage while dealing 0**. Each trip ended in a recall.
- **Mirror-group capture counts, theirs vs ours:**

  | Their group | Ours | Theirs | Ours |
  |---|---|---|---|
  | g5 | g4 | 17 | 4 (first r772) |
  | g13 | g12 | 13 | 4 (none in r44-703) |
  | g3 | g2 | 9 | 0 |
  | g7 | g6 | 8 | 0 |
  | g17 | g16 | 9 | 2 |

  They also took our-side g16 eight times.

**Totals, theirs vs ours.**
- Collected gems 1,074 vs 477; gold 7,046 vs 2,867.
- Clears 78 vs 45; monster damage 161k vs 52k.
- **Camp damage taken per 1k dealt: 219 vs 521.**
- Kills only 1-4, so the game was not decided by fights. Their lead began between r500 (178-145 us) and r750 (244-309).

**Root.** Farming throughput:
- one of our five champions was trapped on 0-gem targets for about 1,000 rounds;
- two more spent their time walking into the enemy farming zone and being driven off;
- our home groups idled.

### 02stalactites: W 1045-383 (r437)
**Map.** 30x30. Two altars at (14,14) and (15,14). Gem-cluster fields: g6 (9,25) 77 gems, g8 (14,24) 168, g7 (20,25) 77, g0/g1 28, g13/g14 21. Wolf + gold flanks give 4 gems and 120 gold each. Hole columns at x=5 and x=24.

**Opening.** We took g6 (r56, Vesper solo, 77) and g8 (r58, Vendetta + HoR, 168), and banked 77/84/84 by r115. The score was 161-12 at r100.

**Their side.** They farmed the wolf flanks for gold (2,708 vs our 530) and the small cluster groups. Vesper and Vendetta bought **nothing** all game.

**Carrier kills (decisive).**
- **r207:** HoR killed Stellar at (14,15), beside the altar, carrying **205** (Stellar collected 241 and submitted 12). HoR banked 205 at r256.
- **r335:** their Marcella captured g8 alone for 210 (Prospector), walked to the altar, and was killed by HoR at (13,13) at r362. HoR banked 210 at r438, which ended the game at 1045.
- **415 of our 1,045 gems came from these two kills.**

**Root.** Their big-bag tribute walks into our altar presence. Our channel-focus logic (`focus_bias` tier 0 for tributing enemies; HoR's stun dash in `stun_channel`) punished them. They out-farmed us (26 clears vs 7).

### 01starfish: W 987-618 (r2000 tiebreak)
**Map.** The two altars (23,17) and (26,17) sit **inside** g15 (24,18): 6 elks + 4 gems + 4 gold, 118 gems, solo-rejected by everyone. The centre is a column of 8 single wolves (g7-g14, 4 gems each).

**Their play.**
- They farmed the wolf column 100+ times: **147 clears vs our 34**, monster damage 282k vs 112k, gold 10,448 vs 9,362.
- They held their gems: first tribute at r556.

**Our gems came from two sources.**
1. **g15 captured 3 times late:** r1394 (Vesper + Ryth, 59 each), r1628 (Vendetta 118, banked as 126 at r1727) and r1882 (Vesper 118, banked at r1915). That is **354 gems, 36% of our total.** They never took g15.
2. **Carrier kills:** Vesper killed Marcella at r567 (32), Stellar at r893 (20) and Marcella at r1550 (68). They killed our Marcella at r1018 at (21,47) carrying 51, and HoR at r1063 at (20,20) carrying 55.

**Deaths.** Even: 22 vs 21 by champions; camp deaths 7 vs 8. Ours died to the altar-ring elks at (22-29, 12-21), including Vesper at r794 carrying 15.

**Root.** We won through the big objective and carrier kills, while losing the farming race 4.3x on clears. Our champions spend most of their time on single-clear round trips: clear, walk to an altar 20-35 tiles away, recall to heal or shop, walk back.

### 01the_farm: W 870-25 (r2000 tiebreak)
**Their collapse.** Their 3 champions froze south of the g16 gap (§1) while carrying 136 gems. We killed them only late: Vesper killed Ren at r1603 (44), Vendetta killed Ren at r1874 (51) and Marcella at r1882 (40).

**Our play, unopposed.**
- We farmed slowly: 33 captures, **870 gems in 2,000 rounds**, never reaching 1,000.
- Vendetta spent 471 rounds in the 45-60% HP band and was idle r233-462 carrying 15 gems.
  - No wards were placed, so it stayed within 6 tiles of (22,9).
  - Why is *unexplained*; no positions.
- Marcella spent 347 rounds in the band.
- The monolith pairs g24/g25 (207 gems each) and the 74-gem g9 were never touched.

**Root.** Opponent bug; our tempo even without opposition is the real lesson.

## 3. Their strategy vs ours
**Where theirs was superior.**
| Gap | Size | Our code responsible |
|---|---|---|
| **A. Farming continuity: no long dead stretches.** Their champions spend ~0 rounds in the 45-60% HP band; ours spend 1,029 (Vendetta, harvest) and 471 + 347 (the farm). | Harvest: 22 zero-gem captures; Vendetta 79 gems in 1,421 rounds. | `choose_target`: `if not (self.target is G) and hp < maxhp * 0.6: continue` sits inside `if s > 0`, so between 45% and 60% HP only the current target and zero-strength groups (gold and gem clusters) are eligible. `play_turn_main` heals only at `low = hp < maxhp * 0.45`, or at `rich` (gold >= 150 with carried < 8, or gold >= 400). The `G is None -> recall if hp < 0.7*maxhp` escape never fires while a gold cluster anywhere on the map stays eligible. |
| **B. No value on pointless trips.** They never travel for 0-gem gold; we went to g11 beside their spawn 9 times. | About 150 tiles of walking per 20 gold. | `Group.__init__`: `value = gems + 0.25 * gold` gives a lone gold cluster value 5 with no distance cap. `choose_target`'s status-2 rule (`G.ready > rnd + d`) re-admits g10 as soon as we walk away, producing the g11-to-g10 oscillation. |
| **C. Own-half circuit.** Harvest: 68 of 77 captures on their half; mirror groups 17 v 4, 13 v 4, 9 v 0, 8 v 0. | Collected 1,074 vs 477. | Nothing in `choose_target` prefers near-home or uncontested groups. The claim weighting (`c` -> x0.3 if `solo_ok`, **x1.2 if not**) pulls extra champions across the map to an ally's elk fight; Vesper's r0-140 trek ended at (57,56) with 0 damage. `DEATH_PENALTY` only acts after a death at that group. `update_alerts` / `threatened()` feed banking, not targeting. (The blanket enemy-half x0.4, T8, was already rejected.) |
| **D. Camp-damage efficiency.** Jungle emblem on all 5 champions by r300-750; Prospector on cluster maps. | Camp damage taken per 1k dealt: harvest 219 vs 521, starfish 211 vs 572. Clears: starfish 147 vs 34, harvest 78 vs 45. | `shop()` / `bruiser_item()` with `BRUISER_PLAN`, `JUNGLE_FIRST = False`. T25 (Jungle-first) was rejected for fight blowouts; Q28b/c/d are queued. Some of the gap is also composition and time: their ranged Focus casters, and more of their champion-rounds spent farming. |
| **E. Opening on a dominant central group.** Varg + Stellar took the elk-arena centre at r38-44. | 72-0 for 250 rounds. | The `choose_target` chip model (`cycles > 4` / `budget <= 0` -> `continue`) rejects any multi-elk group for every champion, and c2 has no team-clear path (T23/T30 not merged). The harvest centre g20 (114) and four golem groups (43-57) were never taken by us; the starfish g15 (118) only from r1394. |
| **F. Not feeding in their zone.** Their kills on us are on their half. | Harvest: Marcella took 4,400 champion damage while dealing 0, in r1050-1200. | `handle_enemies` -> `group_balance` `dis` -> `retreat`. Retreating is right once there, but nothing remembers that the target sits in a defended zone, so the next `choose_target` sends the champion back. |

**Where ours was superior.**
- **Grouped fighting.**
  - Elk K/D 25-6; Vesper 11-0 on elk, 15-2 on starfish.
  - The q24 group rule (`group_balance`, `GROUP_ADV`) wins when solo enemies walk into 2-3 of ours.
- **Punishing channelling carriers.**
  - `focus_bias` puts tribute-channelling enemies in tier 0 with engage ratio 1.2 (+ carried gems/100); HoR's landing-dash stun is used by `stun_channel`.
  - Stalactites: 415 gems from two altar kills. Starfish: 68- and 32-gem carriers killed.
  - Their gems lost to kills: 0 / 32 / 419 / 268 / 135. Ours: 0 / 11 / 4 / 154 / 0.
- **Small, frequent banking.** `bank_now` / `bank_detour` (BANK_ANY 30, NEAR 15, CLOSE 5) mean we rarely carry big bags into danger.
- **Capturing the big objective once it is open.**
  - Elk: we stole their clear at r248, then held g0 (14 x 72).
  - Starfish: g15 (3 x 118) late, as a group.
- **The early gold race on gold-cluster maps** (elk 1,745 vs 1,232 at r250), which bought the Bruiser items that won the centre fights. Gold-cluster value is not useless; gaps A and B are about *when* and *how far*.

## 4. Our weaknesses exposed
| # | Weakness | Evidence | Games | Impact |
|---|---|---|---|---|
| W1 | **45-60% HP band trap.** Only zero-strength targets are eligible and there is no heal. | Harvest: Vendetta 1,029 band rounds, 22 zero-gem captures (r38-474 g10 loop, then g11 at the enemy spawn x5), plus Ryth 157 and HoR 91. The farm: Vendetta 471, Marcella 347. **Local census** (`matches/gate-c2-all`, c2 vs q24_combo, 140 games): 564 band champion-rounds per game, 113/140 games >= 200, and **02harvest A reproduces it locally (1,720)**. 24% of all c2 captures are 0-gem. | 2 (decisive in 1) | decisive |
| W2 | **Home groups left unfarmed while champions walk into the enemy half** and are driven off. | Harvest: own-half gem captures 17 vs their 68 on theirs; mirror groups 4-17, 4-13, 0-9, 0-8; Vesper 0 monster damage in r0-500; Marcella's r1050-1200 damage taken with none dealt. | 1-2 | decisive |
| W3 | **Unlimited travel for 0-gem gold** (value 5 at any distance). | Harvest: 9 g11 trips at (73,91), about 75 tiles from our spawn. | 1 | major |
| W4 | **No commitment to solo-rejected big groups** in the opening, and late on maps where they hold most of the gems. | Elk 0-72 until r248 (29 zero-gem captures while waiting); harvest g20 and golems never taken; starfish g15 first at r1394; the farm's monoliths and 74-gem g9 never taken. | 4 | major |
| W5 | **Slow farm tempo and high camp damage per clear.** | Starfish: 34 clears vs 147, 572 vs 211 camp damage per 1k. Harvest: 521 vs 219. The farm, unopposed: 870 gems at r2000. | 3-4 | major |
| W6 | **Few items on gem-cluster maps.** | Stalactites: 530 gold vs 2,708; Vesper and Vendetta 0 items. | 1 | minor (won) |
| W7 | **Idle enemy carriers left alone.** | The farm: 136 gems parked at (24-26,16) from r~500, first killed at r1603. Our group rule rejects 1-vs-3. | 1 | minor (won) |

## Testable hypotheses (structure-keyed; no map or team names)
1. **H-band (W1, highest priority): heal instead of farming clusters in the band.**
   - **Change.** When `hp < 0.6*maxhp` and the best target from `choose_target` has strength 0 and no gems (or value below that of a gem target), treat it as no target. The existing `G is None -> recall if hp < 0.7` path then heals; recall only when `recall_safe`.
   - **Alternative.** Raise `low` to 0.6 whenever no strength > 0 target is eligible.
   - **Metrics.**
     - Band champion-rounds (re-run the HP-band census, which the scripts in this session do), target near 0.
     - 0-gem captures with more than 20 tiles of travel.
     - Gems collected per alive champion-round.
   - **Mechanism check.** The local 02harvest A game (1,720 band rounds now).
   - **Gate.** Full `--maps all`, plus the off-screen split (Q30 addendum).
2. **H-goldcap (W3): limit travel for gold-only groups.**
   - **Change.** A gold-only group (gems 0) is valued only within ~12 path tiles of the champion or of its next gem target, or in `gold_play()` mode.
   - **Keep:** the early gold-cluster income near spawn (the elk strength).
   - **Metrics.** 0-gem captures per game; gold at r250 (must not fall).
3. **H-zone (W2, distinct from the rejected T8 enemy-half x0.4): decay targets where we were driven off.**
   - **Change.** Keep a per-group "contested" stamp: an enemy champion seen within 8 of the group, or we retreated or took champion damage there, in the last ~150 rounds. Multiply that group's score by ~0.5 unless `group_balance` near-ratio >= `GROUP_ADV`.
   - **Also.** Cap claim-attraction (the x1.2 branch) to claims within ~20 path tiles of us.
   - **Validate.** Against solo-farmer imitations (`lad_*` style), not self-play only.
   - **Metrics.**
     - share of captures on our half;
     - champion damage taken with 0 dealt per game;
     - Vesper and HoR monster-damage rounds.
4. **H-commit (W4): open on the dominant group when it is close.**
   - **Change.** If one group holds >= 40% of all map gems, lies within ~15 path tiles of our spawn, and every champion rejects it solo, the whole team musters on it from r1 (the h_teamclear bootstrap, used only for this opening case).
   - **Fallback.** Otherwise the team option fires only when no solo target exists (c4 idea).
   - **Metrics.** First-capture round of the top group; gems at r250.
5. **H-pair (W2/W4): pair weak solo champions on elk groups.**
   - **Change.** Champions with solo cycles in 4-6 (dps ~50 vs elk groups) may commit when an ally is within 6 tiles and claims the same group, instead of being attracted from anywhere.
   - **Metrics.** Vesper and HoR clears per game; travel per clear.
6. **H-jungle2 (W5, a Q28 variant): Jungle as the second emblem.**
   - **Change.** Buy Jungle as the second emblem (after the first Bruiser) only for a champion whose own camp damage taken per 1k dealt exceeds ~400 by its second shop visit. This is keyed on its own stats, not the map.
   - **Metrics.** Camp damage per 1k dealt; heal trips per 1,000 rounds; fight K/D must hold.
7. **H-idlecarrier (W7, low priority): muster on idle enemy carriers.**
   - **Change.** An enemy seen stationary for >= 50 rounds with >= 30 gems (`e.gem_count()`) becomes a team focus target. Muster 2-3 before engaging, overriding `dis` once the local ratio reaches >= 1.0.

**Opponent-specific notes (for ladder expectations, not for fixes).**
- This bot farms 2-3x our rate on large symmetric maps when left alone (harvest).
- It is beaten by grouping at chokepoints, by killing its big-bag carriers at altars, and by taking objectives it ignores (multi-elk groups).
- Expect losses to it, and to bots like it, on 100x100 maps until W1-W3 are fixed.
