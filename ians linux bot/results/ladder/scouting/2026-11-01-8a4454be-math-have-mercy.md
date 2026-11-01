# Math Have Mercy (1515): ladder set 8a4454be, 1 Nov 2026, our v3, won 4-1

- **Opponent:** Math Have Mercy, rating 1515 (ours after the set: 1530).
- **Our version:** website v3 = `bots/q24_combo` (live 01:42-04:42 UTC). The set ran at 04:32 UTC. We were side B (team B) in all 5 games.
- **Record: 4-1.**
  - W 00anvil 1170-46 (r1398, gems).
  - **L 00vault 10-1029** (r520, gems).
  - W 00reverse_spiral 726-437 (r2000, tiebreak on gems).
  - W 01shortcut 639-85 (r2000, tiebreak on gems).
  - W 00dunes 917-259 (r2000, tiebreak on gems).
- **Link:** https://2026a.battlecode.co.uk/game/match-groups/8a4454be-57ba-498f-90a5-57a3d509e3a4
- **Sources:**
  - `matches/ladder/summary/<id>__B.json` for game ids 241b6a54, f9572a77, 59eca85f, e701a61e and 7e388f6e.
  - `python3.12 -I tools/scout.py --group 8a4454be` gives every number marked "scout".
- **Method:** as in the e317decf report. Positions come from ward trails (our ward lands within 2 of the champion, and only after a move of more than 6 tiles) and from event tiles. *Speculation* marks inference.

## Set summary (scout)
| Map (size, picks) | Result | Gems r250 | r500 | r1000 | End | Clears/100r us-them | K/D us | K/D them | fuelExhausted us/them |
|---|---|---|---|---|---|---|---|---|---|
| 00anvil (37x31, 3) | W | 56-25 | 217-46 | 534-46 | 1170-46 r1398 | 4.79-0.50 | 26/4 | 2/26 | 0/0 |
| 00vault (31x31, 4) | **L** | 0-343 | 4-686 | — | 10-1029 r520 | 1.73-0.58 | 2/8 | 8/2 | **186**/12 |
| 00reverse_spiral (30x30, 4) | W (tiebreak) | 58-21 | 108-76 | 327-156 | 726-437 r2000 | 3.05-1.70 | 7/9 | 6/7 | 0/0 |
| 01shortcut (40x40, 4) | W (tiebreak) | 0-40 | 144-40 | 194-85 | 639-85 r2000 | 2.40-0.50 | 13/8 | 5/14 | 0/5 |
| 00dunes (79x79, 5) | W (tiebreak) | 73-0 | 182-22 | 341-117 | 917-259 r2000 | 1.05-0.50 | 23/14 | 12/29 | 1/185 |

## 1. Opponent profile

### Draft and roles
**Draft:** Varg, Tavi, Vesper Vale, then Marcella (4-pick), then Stellar (5-pick). On 3-pick anvil: Varg, Tavi, Vesper. Mirror picks: Vesper, and Marcella from 4 picks.

| Champion | Role |
|---|---|
| **Tavi** | **Their killer.** Ranged stun (1.6xF, range 4) plus shards bought anywhere.<br>vault: 4-0, including 3 of our 4 deaths in r77-96, with 3,414 champion damage dealt and **0 taken**. Also shortcut 2 kills, dunes 3, reverse_spiral 2. |
| **Marcella** | Bruiser-Health brawler and their best carrier. vault: carried 85 + 85 and tributed 170 at r365; dunes: 5 kills. |
| **Varg** | Tank (shield 4,000-25,800) and splash farmer. Often the victim: 10 deaths on anvil. |
| **Vesper Vale** | Farmer/capturer. vault: 114-gem tributes. |
| **Stellar** (5-pick only) | Ranged burst. dunes: 3 kills. |

### Items: Bruiser Health on everyone, then Durability; low spend
- **Order:** Bruiser Health shards first, then Durability H, then Bruiser Strength late. No Jungle, Monster or Power.
- **First buys:**
  - Tavi: BruH at r23-88 (anywhere). On vault it bought **mid-fight**: BruH x3 r78, BruH x2 + DurH r86, DurH x4 r97.
  - Marcella: r34 and r136.
  - Varg: r119-623.
- **Gold:** 549 to 2,970 earned per game. Emblems by r1000: 2, 7, 6, 6, 5. Ours: 19, 2, 5, 15, 9.
- **Map control:** **0 wards in all 5 games.** Locks: 1-3 bought a game, 0-1 placed. No crystals.

### Farming: one jackpot, as a pack; otherwise almost idle
- **vault: the 343-gem centre g0, GemCl x49** (5,880 HP, strength 0) inside a walled box. Captured 3 times, with 3-4 champions present at each completion: r109 (Tavi, Vesper, Marcella), r283 (Varg, Tavi, Vesper, Marcella) and r481 (Varg, Tavi, Vesper).
  - 1,029 gems from those 3 captures and nothing else. Their total clears: 3.
- **Everywhere else: 0.5-1.7 clears per 100 rounds** (anvil 7 captures in 1,398 rounds; shortcut 10; dunes 9).
- **Huge idle stretches** (champion-rounds with no metric change for 100 or more rounds):
  - shortcut 2,953 (Tavi 998, longest r761-1148);
  - reverse_spiral 1,096 (Vesper 424, Tavi 423).
- **Fuel:** dunes 185 `fuelExhausted`, every champion from r59 on.

### Tributes
**Bag size follows the jackpot.**
- vault: 9 tributes, mean 114, first r130.
- Elsewhere: 3-19 tributes of 15-28 gems, first at r97 (anvil), r173 (shortcut), r187 (reverse_spiral) and r451 (dunes).

### Fight behaviour
- **They fight at their objective, with Tavi's ranged stun.**
  - vault r67-97: they lost Varg and killed 4 of ours at the box's west mouth and towards their altar (5,25). Positions: (11,15), (5,21), (9,24), (18,17).
  - The kill that decided their second jackpot was their Marcella killing our Vendetta with 85 gems at (17,30) at r332.
- **They are weak elsewhere.** anvil: 2 kills, 26 deaths, **10 of them near their own spawn** (spawn-camped by our Marcella, 19-1). dunes: 12 kills, 29 deaths.
- No carrier hunting away from their objective. No wards, so no vision of our approach.

### Adaptation
- They recognise a jackpot group and send the pack to it.
- Otherwise they drift: low clears and long idle stretches. Draft and build are fixed.

### Their weaknesses (observed)
1. **Passive and idle when there is no jackpot:** 1,096-2,953 quiet champion-rounds; 0.5 clears per 100 rounds.
2. **No wards at all.**
3. **Low gold, few emblems.** They lose every fight once our items lead: anvil 26-2, dunes 29-12.
4. **Spawn-campable** (anvil).
5. **Fuel collapse on a large map** (dunes 185).

## 2. Per game

### 00vault: L 10-1029 (r520); the loss
**Map.** 31x31, rot180. Spawns: theirs (2-4, 2-4), ours (26-28, 26-28). Altars at (5,25) and (25,5), 21 path steps from each spawn.
- **g0:** GemCl x49 (343 gems, 0 strength) in the walled box (11-19, 11-19). It opens west at x=10-11, y=14-16, and east at x=19-20, y=14-15, with hole gaps north and south.
- **Everything else:** Wolf/Gold groups worth 0-4 gems.

**Decisive moments.**
1. **r11-50: we went to the jackpot but our turns were suspended.**
   - All four of ours were at the box by r11: wards (18,16), (20,16), (18,15), and Vesper (18,17) at r34.
   - **Vendetta, Marcella and HoR each logged 13 `fuelExhausted` in r0-50**, about one suspended turn in every 3-4.
   - Vesper logged its first 4 (r43-50) exactly while it stood at the box.
   - Over the game: Vendetta 54, Marcella 50, HoR 76, Vesper 6. **186 suspended turns in 520 rounds.**
   - The bins line up with the jackpot cycles: r150-250 (22-28 each) and r350-450 (8-30).
2. **r67-97: the brawl.**
   - r67: our Marcella killed Varg at (11,15).
   - Tavi, upgrading Bruiser H and Durability in the field at r78, r86 and r97, killed Marcella at (11,15) r77, HoR at (5,21) r85 and Vendetta at (9,24) r96. Their Marcella killed Vesper at (18,17) r97.
   - Our champions had followed the fight west past the box towards their altar: wards (9,14), (4,24) and (3,23) at r78-88. **All four of ours were dead by r97.**
3. **r103-132: the uncontested jackpot.** Their Marcella cleared g0 at r103. Tavi, Vesper and Marcella captured 343 at r109 while our whole team was dead (our respawn wards appear only at r137-158), and tributed 115 + 114 + 114 at r130-132.
4. **r271-283: second cycle.** Tavi killed HoR at (20,15) r271. They cleared at r277 and captured with 4 at r283 (85-88 each).
5. **r296-365: the 170-gem swing.**
   - Vendetta killed their Vesper at (8,14) and took 85.
   - Vendetta's trail: (4,24) at r305, next to altar (5,25), **but no tribute**; then (9,23) r319 and (14,28) r329. It took 538 champion damage at r310-312.
   - Their Marcella killed it at (17,30) at r332 and tributed 85 + 85 = 170 at r365.
   - *Speculation:* (5,25) carried their lock (MHM placed about 1; Marcella bought locks at r136 and r370), or the 9-turn channel for 85 gems was stunned. Either way, the 85-gem bag sat next to an altar for about 25 rounds and never banked.
6. **r462-521: third cycle.** Their Marcella killed ours at (18,18) r462. They captured g0 at r481 and tributed 114 + 114 + 115 at r503-521. Game over at r520.

**Root.** A pure jackpot map.
- Our champions reached it first but lost about a quarter of their turns to fuel suspensions near the 49-camp group.
- They then chased west into Tavi's stun range and were wiped (1 for 4) just before the first capture.
- Our only counter-swing (Vendetta's 85) never banked.

### 00anvil: W 1170-46 (r1398)
- **Map:** 37x31, 3 picks. One altar, (18,8). Spawns at (2-4, 14-16) and (32-34, 14-16).
- **Fights:** Marcella went 19-1 (12 kills in r300-1000), with streaks at (13,1)-(13,7) and **at their spawn**, (2-4, 12-14): r587-596, r880-896 and r1258-1269. They died 10 times near their own spawn.
- **Farming:** we made 67 captures, 26 of them on their side (347 gems). They made 7.
- **The monolith:** we even captured monolith g10 (18,5) twice from r1159, with Marcella's 3,612 gold of items. Tribute max 202.
- **Root:** our items and the group commit rule against a passive, ward-less, Bruiser-Health team.

### 00reverse_spiral: W 726-437 (r2000 tiebreak)
- **Map:** 30x30. Spawns overlap the centre: theirs (12-14, 13-15), ours (15-17, 14-16). Altars are in opposite corners, (2,2) and (27,27), 30 or more path steps away.
- **Their gold lead early:** 744 vs 353 at r500, from wolf/gold groups such as g7 (2,22).
- **Our gems:** the single cluster g13 (19,18), 2 tiles from our spawn, 17 times, plus g3 and g4. We led from r358.
- **Fight:** Vendetta took 33 gems at r606-618, killing Tavi and Varg at (15-21, 25).
- **Them:** 1,096 quiet champion-rounds.
- **Our losses:** 3 camp deaths, 7 locks used. We finished 726, never near 1,000.

### 01shortcut: W 639-85 (r2000 tiebreak)
- **Map:** 40x40. Spawns at (18-21, 12-14) and (18-21, 25-27). Both altars, (32,12) and (32,27), sit inside walled enclosures next to a 235-gem Monolith + 5-cluster group (g5/g6), 45 path steps from each spawn.
  - The corridor into our altar enclosure passes Elk + 2-cluster group g15 (27,6).
- **Them:** 3 tributes all game, 2,953 quiet champion-rounds.
- **Us:**
  - 2,203 quiet champion-rounds (Vesper 813), 9 TP crystals bought;
  - 213 gems lost on death, **139 of them to camps**;
  - **Marcella carried 95-121 gems from r1734 to r1874.** Trail: (17,15) → (21,7) → (10,2) → (0,4) → (4,11) → (9,19) → (25,19) → (34,19) → (32,8). It killed their Marcella (+26) at (26,14) r1861, then **died to a camp at (26,8) at r1874, destroying 121 gems**.
- **Root:** both bots struggle with the long, camp-flanked altar route. We won on farming volume.

### 00dunes: W 917-259 (r2000 tiebreak)
- **Map:** 79x79. Spawns at the corners, (3-5, 3-5) and (73-75, 73-75). Every gem group is in the centre, 36-45 path steps away. Altars at (39,35) and (39,43).
- **Opening:** we led from r73. g4 (49,40), Elk + 4 clusters (43 gems), was ours 11 times; the centre Golem + 8 clusters g0 (92 gems) 3 times.
- **Them:** first tribute r451, 185 `fuelExhausted`.
- **Fights:** won 23-14 (Ryth 10-2).
- **Our tempo:** only 21 clears in 2,000 rounds (1.05 per 100 rounds). Vendetta collected 66 gems in 2,000 rounds.
- **Root:** an easy opponent, but with our tempo on a sparse big map we did not reach 1,000.

## 3. Their strategy vs ours

### Where theirs was superior (only on the jackpot map)
| Gap | Size | What in our code causes it (`bots/q24_combo/src/bot.py`) |
|---|---|---|
| **A. Compute near a 49-camp group.** | vault: 186 suspended turns (54/50/76 for the three champions that stayed at the box), 13 per champion in r0-50. | **Several per-turn loops run over every camp of a group or every awake camp:**<br>• `observe_fast`: per camp, `gv.is_set`, `ct.is_set`, `c.health()`;<br>• `threats_fast`: per awake tile, `camp_at`, `spawn_position`, `strength` (damage wakes all 49);<br>• `pick_camp_in_range`: per camp, `is_visible`, `state`, `position`, `health`;<br>• the `play_turn` danger block and the `avoid` loop over `awake`.<br>At about 3k fuel per API call, 49 camps × 3-4 calls × 3-4 loops is plausibly over 1.5M on top of the rest of the turn.<br>*(Likely cause, not yet profiled: confirm with `PROF = True` on a 49-cluster local map.)* |
| **B. Winning the jackpot brawl.** | vault r67-97: 1 kill for 4 deaths. | **`handle_enemies` engages per champion.** `ratio <= limit`, plus `focus_bias` and the team focus byte, let a champion chase a retreating enemy (Marcella's r67 kill on Varg at the box mouth). Followers then walked into Tavi's range 4 near (5,21)-(9,24).<br>**Nothing ties combat to the objective.** There is no "hold the jackpot" rule: chasing is allowed anywhere. `group_balance` counts allies within 7 only. |
| **C. Banking a big bag.** | vault r296-332: 85 gems next to (5,25) for about 25 rounds, never banked, lost to their Marcella (+170 for them). | **A tribute of 85 gems is a 9-turn channel** (`ceil(gems/10)`), broken by stun or a new lock.<br>**`do_tribute` / `bank_now` have no bag-size or enemy-stun awareness.** `handle_enemies` runs first every turn, and `stun_channel` is our tool only. If the altar was locked, `break_lock` only hits from an adjacent tile. |

### Where ours was superior (4 games)
- **Fighting with items.**
  - anvil 26-2: Marcella 19-1 with 3,612 gold of Bruiser items, spawn-camping at (2-4, 12-14).
  - dunes 23-12, shortcut 13-5.
  - The source is the q24 `group_balance` commit rule and Bruiser stacking (`BRUISER_PLAN`) against their low-gold Bruiser-Health builds.
- **Farming volume** against a passive opponent: clears per 100 rounds 4.79 vs 0.50, 3.05 vs 1.70, 2.40 vs 0.50 and 1.05 vs 0.50.
- **Wards and vision:** 232-703 per game against their 0.
- **A solo monolith late** (anvil, twice, from r1159) once our items were big enough. The `choose_target` chip model passes it when `budget > 0`.

## 4. Our weaknesses exposed
| # | Weakness | Evidence | Games | Impact |
|---|---|---|---|---|
| W1 | **Fuel blow-up near groups with many camps.** | vault: 186 `fuelExhausted` (Vendetta 54, Marcella 50, HoR 76) against 0-1 on the other four maps. The time bins match the time spent at the 49-cluster box. | 1 | decisive (with W2) |
| W2 | **Jackpot fights: we chase away from the objective and get wiped before the capture.** | vault r67-97: deaths at (11,15), (5,21), (9,24) and (18,17). They captured 343 at r109 with all of ours dead. | 1 | decisive |
| W3 | **Big-bag tribute failure** (long channel, possible lock, no escort). | vault r305-332: 85 gems next to (5,25), no tribute; died at (17,30); +170 for them. shortcut r1874: 121 gems destroyed by a camp at (26,8) after 140 rounds of carrying 95 or more. | 2 | major |
| W4 | **Slow tempo against passive opponents:** 3 tiebreak wins at 639-917. | dunes 1.05 clears per 100 rounds; shortcut 2,203 quiet champion-rounds; reverse_spiral 726 at r2000. | 3 | minor (all won; rating risk vs better farmers) |
| W5 | **Camp deaths with gems on altar approach routes.** | shortcut: 139 gems lost to camps. reverse_spiral: 3 camp deaths. | 2 | minor |

## Testable hypotheses (structure-keyed; no map or team names)
1. **H-fuelgroup (W1; cheap, high value on any many-camp map).**
   - **Profile first.** Run `PROF = True` in a debug copy on a local map with a group of 20 or more camps (onslurm, test partition).
   - **Then make every per-camp loop proportional to what matters:**
     - `observe_fast` reads `c.health()` only for camps inside `me.attack_tiles()` dilated by 1, and marks the rest from `camp_tiles` presence alone;
     - `threats_fast` skips 0-strength awake camps (clusters deal no damage);
     - `pick_camp_in_range` iterates `G.tiles & attack_tiles & camp_tiles` positions instead of all of `G.camps`;
     - the danger and `avoid` loops skip `s == 0` camps.
   - **Metrics.** `fuelExhausted` per game on maps whose largest group has 20 or more camps (target near 0); jackpot first-clear round.
2. **H-jackpot-hold (W2; extends INSIGHTS item 11, the map-archetype profile).**
   - **Change.** When a 0-strength group holds 35% or more of the map's gems and we are within 8 of it, `handle_enemies` may only engage targets within 6 of the group, and the regroup point is the group itself.
     - No chasing out of the box.
     - If outnumbered at the group, all champions retreat together toward the group's far side, not toward their spawn.
   - **Draft memory.** Mark the archetype in the draft so all champions go to the jackpot from r1 and stand together.
   - **Metrics.** Jackpot captures ours vs theirs; deaths more than 8 from the jackpot in its contest windows.
3. **H-bigbag (W3).**
   - **Change.** With 50 or more gems, a channel of at least 5 turns:
     - start a tribute only if no enemy champion with a stun or CC has been seen within 8 of that altar in the last 10 rounds and no enemy is visible within 6;
     - otherwise pick the other altar, or wait 1 tile out of sight until an ally is within 4.
   - **Lock.** If the altar is locked and we are within 3, step adjacent and break it (shared with H-lockbreak in the f9a7ff0e report).
   - **Metrics.** Gems lost by carriers with 50 or more gems; big-bag tribute success rate.
4. **H-carrycamp (W5).**
   - **Change.** While carrying 30 or more gems, `step_toward` / `go_to` for banking add every awake camp's range plus 1 to `avoid`. Sleeping elk and golem ranges get a soft penalty.
   - **Danger threshold.** Use `hp <= incoming*(steps+2)+120` instead of `+60` when carrying 30 or more, so a weakened carrier leaves camp range earlier.
   - **Metrics.** Gems lost to camps per game.
5. **H-closeout (W4; shared with f9a7ff0e H-closeout).**
   - **Change.** After r1200, with a lead of 150 or more, lower the bank thresholds.
   - **Also.** Let idle champions (no target for 20 or more turns) take any positive-value group, up to 1.5 times the current travel limit.
   - **Metric.** Share of wins ending by tiebreak (3 of 4 here).

**Opponent-specific notes (for ladder expectations).**
- Math Have Mercy is beatable everywhere except a contested jackpot.
- Against such a map our current bot loses the first jackpot brawl and the compute budget near the group.
- Expect wins elsewhere, by tiebreak.
