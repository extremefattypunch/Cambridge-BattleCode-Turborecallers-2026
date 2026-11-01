# final_final_v3_really_final (1522): ladder set 910a58b9, 1 Nov 2026, our v3, won 3-2

- **Opponent:** final_final_v3_really_final, rating 1522 (ours after the set: 1529).
- **Our version:** website v3 = `bots/q24_combo` (live 01:42-04:42 UTC). The set ran at 01:42 UTC. We were **side B** (team B) in all 5 games.
- **Record: 3-2.**
  - **L 00lost_world 0-1008** (r379, gems).
  - W adgato_gemcombat2 1033-745 (r1125, gems).
  - W 00fragment 799-213 (r2000, tiebreak on gems).
  - **L 01shortcut 378-773** (r2000, tiebreak on gems).
  - W 02crossing 1033-953 (r1221, gems).
- **Link:** https://2026a.battlecode.co.uk/game/match-groups/910a58b9-6b92-41d5-a5cd-964eb7f91ce2
- **Sources:**
  - `matches/ladder/summary/<id>__B.json` for each game, and `python3.12 -I tools/scout.py --group 910a58b9`.
  - Map geometry decoded from `maps/*.map26a` (scout's loader). Scout's BFS treats holes as passable (dash); walking distances for champions **without** a dash (our Marcella and Ryth) were recomputed with holes blocked.
  - Replay `matches/ladder/replays/2ec1835b-...repl26a` (01shortcut): `team-b.stdout` is empty, so it adds nothing.
- **Method.** The stats file has no positions. Positions are inferred:
  - **Wards.** A ward lands within 2 tiles of its placer, and our bot re-wards only after moving more than 6 tiles (`try_ward`). So a long gap with no ward means the champion stayed inside a 6-tile box.
  - **Event tiles.** Deaths, captures, tributes and shop tiles.
  - **HP.** Estimated from the damage-taken and healing timelines.
  - Anything marked *inferred* or *speculation* is not directly observed.
- **Group ids** (gN) are the engine's camp-group ids, as `tools/scout.py` prints them.

## 1. Opponent profile
**Draft: fixed, truncated to the pick count.** The order is Stellar, Heart of Ruin, Ren, Cassi & Issac, Ryth.
- **3-pick** (fragment): Stellar, HoR, Ren.
- **4-pick:** adds Cassi & Issac, so **5 bodies against our 4**.
- **5-pick:** adds Ryth, so **6 bodies against our 5**.

The same core (Stellar, Ren, Cassi & Issac, Ryth) appears in the Us V Them set (a7ca9a58). It may be a shared public strategy.

| Champion | Role (evidence) | Item order (shop rounds) |
|---|---|---|
| Stellar | Ranged Focus burst and their main carrier. Range-4 2xF / 1.4xF spells. Its repeated 98 champion damage on us (lost_world) is the 1.4xF AoE. It carries big bags and dies with them: gemcombat2 collected 405 and **lost 314** (56 r38, 56 r327, 118 r1106). | **Power Focus first** (r76-328), then Home H, Durability H, then Power Focus stacking (fragment: 10 PowF emblems by r1781) |
| Heart of Ruin | Shield tank and farmer: 17 clears on lost_world and 21 on crossing; 3,000-22,050 shielding per game | Power S (r203-279), then Home H, Durability H, Power S. It never shopped on 4/5 pick maps before r200 |
| Ren | Melee skirmisher and their best killer: crossing 8/2, gemcombat2 4/0. It killed our 87-gem Vesper on shortcut | **Bruiser H first** (r82-364), then Durability H, then Power Focus stacking (crossing: 6 PowF emblems by r1183) |
| Cassi & Issac | Two farmers on one pick. Linked fate: 9 double deaths on gemcombat2, 8 on shortcut | Cassi: Power F, then Durability F. Issac: Power S, then Home H |
| Ryth | Farmer and tributer: crossing 17 clears, 298 tributed, the most of their team | Bruiser H (r338), then Durability H, then Power S |

- **Never bought:** Treasure, Jungle, altar locks (0 in 5 games) or TP crystals (0).
- **Wards:** 17-126 per game, **100% in bushes**. On fragment all 85 were at their own spawn.

**Farming: own half plus the middle, never our half.**
- **Enemy-side captures: 0 in all 5 games.**
  - lost_world: 67 of 70 captures mid.
  - crossing: 77 own, 20 mid.
  - shortcut: 34 own, 8 mid.
- **Tempo is high on open maps and low on small ones.** Clears per 100 rounds, theirs vs ours:
  - lost_world: 19.0 vs 0 (r0-379).
  - crossing: 10.3 vs 1.7 in r0-300, 8.0 vs 4.4 in r300-1000.
  - fragment: 1.55 vs 2.95.
- **They group on the main gem source.** On lost_world all 6 bodies cycled the 14 central gem-cluster groups (g2-g4, g7-g9, g11, g13-g17) every ~50 rounds, which is their respawn time.
  - First clear r24 (Issac, g17 at (14,15)).
  - By r60 they had cleared 11 groups.

**Tributes: big bags at the nearest central altar, early.**
- First tribute r92-176. Our first: r83 (gemcombat2) to r252 (shortcut).
- **lost_world:** 21 tributes averaging 48 (Cassi 91 at r191, Stellar 98 at r198), 19 of them at (18,15). That altar sits inside the gem field, so their farming route *is* their banking route.
- **Other maps, average bag:** gemcombat2 41.4 (HoR 105 at r937), shortcut 30.9, crossing 29.8 (29 of 32 at (25,2)), fragment 9.3 (starved).

**Fights: they fight where they farm.**
- **No hunting, spawn camping or locks.** On crossing, 6 of their 16 kills were in our half. Everywhere else their kills were in the mid or their own half.
- **Carrier kills are incidental, but expensive:**
  - Ren killed Vesper carrying 87 at (0,15), r358 (shortcut);
  - Stellar killed Marcella carrying 84 at (23,17), r819 (shortcut);
  - Stellar killed HoR carrying 41, then Vesper carrying 21, at (17-18,18), r1092-1105 (gemcombat2).
- **They lose grouped fights badly.** Fights with 2 or more deaths:
  - gemcombat2: we won 9, they won 0, 2 even;
  - fragment: 3-0-1;
  - shortcut: 3-0-0.
- **They feed camps:** 14 champions lost to camps on shortcut, around the altar-room monolith g5 at (29,15) and (26,13).

**Adaptation across the 5 maps: none.** Same draft, build and behaviour throughout. When behind on a small map they turtle: on fragment all 85 wards were at their spawn, and 11 of their 26 deaths were within 6 of it.

## 2. Per game
Gem race = tributed gems, us-them.

| Map (size, picks) | Result | r250 | r500 | r1000 | End | Clears us-them | K-D us | Gold us-them |
|---|---|---|---|---|---|---|---|---|
| 00lost_world (35x31, 5) | **L** | 0-347 | (ended r379) | — | 0-1008 r379 | 0-72 | 0-4 | 0-300 |
| adgato_gemcombat2 (51x31, 4) | W | 116-165 | 357-430 | 816-724 | 1033-745 r1125 | 35-44 | 20-9 | 2,884-900 |
| 00fragment (30x30, 3) | W | 42-38 | 76-54 | 322-88 | 799-213 r2000 | 59-31 | 26-10 | 9,783-3,070 |
| 01shortcut (40x40, 4) | **L** | 0-65 | 32-207 | 103-487 | 378-773 r2000 | 51-42 | 11-9 | 4,816-1,510 |
| 02crossing (51x51, 5) | W | 99-154 | 325-289 | 727-746 | 1033-953 r1221 | 43-99 | 15-17 | 3,539-3,380 |

### 00lost_world: L 0-1008 in 379 rounds (0 clears, 0 gold)
**Map.**
- **Spawns:** both on the west edge, 28 rows apart: A at (0-2,0-2), B (ours) at (0-2,28-30).
- **The gem field:** 14 small gem-cluster groups worth 175 gems per 50-round cycle. They sit around the central altar (18,15) at walking distance 19-25 from both spawns.
- **The monolith:** group g12 (GemClx4 + monolith, 228 gems, strength 200, range 5) at (1,15). It is on the west edge between the two spawn exits, and a dead-end corridor (rows 14-16, x3-12) runs from the field straight into it.

**Timeline.**
- **r12-22: we were on time.** Wards at r12 put 4 champions at (0-3,17-19). At r22 they were at (13,16), (11,18), (9,18) and (12,18), on the field's west edge. They cleared g17 at r24.
- **r25-50: skirmish and retreat.**
  - Marcella took 708 champion damage, retreated and healed at spawn by r56.
  - Ryth dealt 100 monster damage, exactly one 1xF AoE stun, while hitting enemies.
  - Then Ryth took 800 and Vesper 940 monster damage. Vesper died to camp 36, the monolith, at (0,18) at r47.
  - *Inferred:* Ryth's AoE caught a g12 tile and woke the monolith while we were retreating west past it.
- **r50-379: nothing.**
  - No champion of ours cleared or captured anything, earned any gold or shopped.
  - Ward trails oscillate between the field edge ((13,16), (17,19), (13,14)) and (3-9,16) or spawn: Marcella r76 (13,16), r98 (5,16), r114 (10,18), r156 (17,19), r171 (8,16).
  - Only HoR dealt monster damage (2,664 over r125-375 to the wolves g6 next to our spawn), and it never finished them.
  - Deaths: Vesper r144 (15,18) to Cassi, Vendetta r219 (9,16) to Ren, Vesper r363 (13,16) to Issac.
- **Their banking.** 1,008 gems in 21 tributes at (18,15) and (33,1), unopposed. They never needed to leave the field.

**Root (code).** The h_earlyfight group rule in `handle_enemies`:
- `group_balance()` compares (sum HP × sum dps) within 7 tiles. With 4-5 of ours against their 6 bodies it is at or below `GROUP_DISADV` 0.75 every time, so `dis` is True.
- `dis` forces `clearly_losing = True`, skips every target that is not a kill-now (`if dis and not kill_now: continue`), and retreats whenever `len(near) > n_allies + 1`.
- The stall breaker (`self.stall`, `holding`) only counts retreats when we are *not* clearly losing, so it never fires under `dis`.
- Meanwhile `choose_target` has no notion of contested ground. The gem clusters have 0 strength, so they are always `solo_ok` and pass at any HP. Every champion keeps re-picking the field, walks back in, sees 4-6 enemies, and retreats.
- The result is a 330-round approach-and-retreat cycle with 0 clears. 0 gold also meant no altar locks, so we could not even deny their altar.

### adgato_gemcombat2: W 1033-745
- **Map.** One altar (25,26) in the south middle and 9 gem-cluster groups.
- **They out-farmed the opening.** Clears 15 vs 6 before r300; gem race r250 116-165, r500 357-430.
- **We won the fights.**
  - Kills 20-9. Their Cassi & Issac died together 9 times (8 of them to Vendetta and Marcella).
  - We took **475 gems** in kills, 274 of them in r300-1000.
  - Marcella went 10/2 and earned 1,818 gold.
- **Decisive.**
  - r877: Marcella killed Stellar carrying 56 at (18,18).
  - r1092-1106: Stellar killed HoR (41 gems) and Vesper (21), then **Marcella killed Stellar carrying 118** at (18,19). She banked 118 at r1126 to end the game.
- **Root.** Grouped fights and carrier punishment: `focus_bias` tier 0 for channelling enemies, and ~8 lock uses against 0.

### 00fragment: W 799-213 (tiebreak)
- **Map.** 30x30 with 3 picks: our Vesper, Vendetta and Marcella against their Stellar, HoR and Ren.
- **Farming.** We cleared 59 vs 31 and captured 15 groups on their side (280 gems).
- **Fights.**
  - Vendetta went **16/1**, with 82k monster damage, 36 clears and 4,765 gold.
  - Stellar died 18 times.
  - 11 of our kills were within 6 of their spawn, where they had placed all 85 of their wards.
- **Their banking.** They tributed 9.3 gems per trip and stalled at 213.
- **Root.** Their 3-pick comp has one fragile carry and no answer to a Bruiser Vendetta.

### 01shortcut: L 378-773 (tiebreak), and one champion frozen for 1,713 rounds
**Map.**
- **Altars.** The two altars (32,12) and (32,27) each sit in a walled room beside a 235-gem monolith group (g5 / g6).
- **Distance to an altar from either spawn:**
  - walking with a dash (holes crossed): 44 steps;
  - without a dash (holes blocked): **109**;
  - with a TP crystal: a 19-step walk to a launch tile in the east corridor, then a 3-turn channel across the 2-wide wall.
- **Pockets.** The wolf groups g7 (14-17,6) and g8 (14-17,33) sit in pockets fenced by holes, **5 tiles (Chebyshev) from the spawns but with no walking path to them.** Only a dash or a crystal gets in or out.

**Vendetta, r235-2000 (decisive).**
- r235: shopped at spawn, bought a TP, full heal (780 healing at r230-240).
- r244: ward at (17,5), inside the g7 pocket.
- r250-290: hit g7's wolves for 2,100 and **took 920 monster damage, about 80 of 1,000 HP left.**
- r264: last ward of the game, at (14,7).
- **r287-2000: no metric changed** (scout quiet stretch 1,713 rounds; 20 gold all game, 0 gems).

**Root (code), traced from the stats.** In `play_turn` (q24; `play_turn_main` in c2_respawn, line ~2592), the heal branch reads:
```python
spawn_d = min(cheb(p, pos) for p in self.spawn.positions())   # Chebyshev, not walking
low = hp < maxhp * 0.45
if (low or rich) and spawn_d > 6 and self.recall_safe(me, enemies):
    me.recall() ...
elif low:
    self.step_toward(me, self.spawn)   # no path out of a hole pocket -> returns False
    return                             # ... every turn, forever
```
- In the pocket, `spawn_d` = 5, so the bot never recalls.
- `step_toward` finds no walking path, so it does nothing.
- The turn then returns before farming, crossing (`cross_toward` is never called) or using the held TP crystal.
- Nothing heals a champion off spawn, so the state is permanent until an enemy kills it.

**The same signature elsewhere:** a fight in the g7/g8 pocket, HP under 45%, then frozen to the end.
- Set 3 (add2d07e, v3, side A): Vendetta r651-2000.
- **v4 games:** dbe2c4a0 HoR r478-1997 (cleared g7 at r478 after taking 2,260 damage), and 6273ab29 Vendetta r867-1647 (game end, lost 436-1024).
- v2: c5919254 HoR r225-1880.
- **Local repro:** `matches/gate-q24-all/01shortcut__B.json` Vendetta cleared g7 at r885 and was idle r886-1596.
- This is the untraced "V3L-2 stuck champion" in STRATEGIES; **it is still live in c2_respawn (v4).**

**Carriers.**
- 270 gems lost to champions and 54 to camps:
  - Vesper killed Cassi & Issac at r347 (+43) and **died 11 rounds later at (0,15) with 87**, to Ren;
  - Marcella died at (23,17) with 84 at r819, to Stellar;
  - HoR died at (2,17) with 34 at r295.
- These are long walks to an altar 44 steps away (109 for a non-dasher) through the middle they farm.

**Gem race.** r250 0-65, r500 32-207, r1000 103-487. After r1000 it was nearly even (+275 vs +286).

**Root.** We played 3 against 5 bodies for 1,700 rounds and dropped 171 gems in two carrier deaths. Their 14 camp deaths and our 3.4x gold lead did not compensate.

### 02crossing: W 1033-953
- **They out-farmed us 2.3x on clears.**
  - Clears 99 vs 43; 31 vs 5 before r300. Their first clear was r7, ours r37.
  - They cycled their own-side groups g12, g10, g22 and g6, 13-16 captures each.
- **We won on kills.** They lost 241 gems to champions; we lost 54.
  - r417: Vesper killed Cassi & Issac (29).
  - r469: Vesper killed Ren carrying 50 at (21,31).
  - r811: Vesper killed Stellar (21).
  - r1155: Vendetta killed Issac carrying 43 at (20,35).
- **Lead.** Ahead for good from r1143. Vendetta's 50-gem tributes at (25,25) at r1169 and r1222 closed it.
- **Root.** Kill steals and locks (~7 used) made up for a farm deficit. The margin was thin (r1000: 727-746).

## 3. Their strategy vs ours
**Where theirs was superior.**
| Gap | Size | What in our code causes it |
|---|---|---|
| **A. Holding the main gem field with every body.** | lost_world: 1,008-0 in 379 rounds; 72-0 clears. | `handle_enemies`: `dis` (group_balance ≤ 0.75) → `clearly_losing = True`, no new fights, retreat whenever `len(near) > n_allies + 1`. The stall breaker never counts retreats under `dis`. `choose_target` has no contested-zone memory, so 0-strength gem clusters are re-picked forever. 6 enemy bodies beat 5 on hp×dps every time, so the rule can never say "advantage" here. |
| **B. No champion lost to geometry.** | shortcut: our 4-pick team played with 3 for 1,713 rounds. | The heal branch: Chebyshev `spawn_d ≤ 6` blocks the recall, and `step_toward(self.spawn)` silently fails from a hole pocket. See §2. |
| **C. Opening tempo on big open maps.** | crossing: 31 vs 5 clears before r300, first clear r7 vs r37. gemcombat2: 15 vs 6. | *Partly inferred.* Their first targets are the nearest small groups. Our first capture on crossing was g0 (Elk + GemClx5, 50 gems, 17-18 steps from our spawn) at r43: `choose_target` scores value/(d+ttk+6), so a 50-gem group 18 away beats a 7-11-gem group 6-9 away. Their circuit is short and own-side; ours mixes mid and enemy-side groups (18 own / 19 mid / 7 enemy captures). |
| **D. Banking geometry.** | shortcut: they banked 25 times at one altar and lost 180 to champions. We lost 270, including bags of 87 and 84. | `bank_now` uses `BANK_ANY` 30 / `BANK_NEAR` 15 regardless of altar distance. With a 44-step (dash) or 109-step (no dash) walk, a 30-gem threshold means carrying 40-90 gems across the middle. TP crystals are bought only for `need_crossing` (unreachable components) and used only by `cross_toward`, never as an altar shortcut (TP launch 19 vs walk 44). |

**Where ours was superior.**
- **Grouped fights and carrier punishment.**
  - Multi-death fights: gemcombat2 9-0, fragment 3-0, shortcut 3-0.
  - Gems taken in kills: gemcombat2 475 vs 107; crossing 241 vs 54.
  - Mechanisms: `focus_bias` tier 0 for channellers, `stun_channel`, the group rule's advantage branch, and Marcella's stun-immune Focus spells against 600-HP Cassi (linked death means 2 bodies per kill).
- **Altar locks:** 7-13 used per game vs 0.
- **Gold.** gemcombat2 2,884 vs 900; fragment 9,783 vs 3,070; shortcut 4,816 vs 1,510. The Bruiser build arrives earlier: 4 vs 1 emblems by r500 on gemcombat2. Their economy is kill-light and Treasure-free.
- **3-pick play:** fragment 799-213.

## 4. Our weaknesses exposed
| # | Weakness | Evidence | Games | Impact |
|---|---|---|---|---|
| W1 | **Hole-pocket freeze.** A low-HP champion within Chebyshev 6 of spawn but with no walking path to it never recalls and never moves. | shortcut Vendetta r287-2000 (1,713 rounds). Same signature in 4 more 01shortcut ladder games (2 of them v4) and the local gate. | 1 here (5 of 11 ladder 01shortcut games) | **decisive** (the 378-773 loss; v3 0-3 on shortcut) |
| W2 | **Dis-lock on a contested central field.** We never farm within 6 tiles of a larger enemy group and keep re-approaching. | lost_world: 0 clears, 0 gold in 379 rounds; ward oscillation (13,16) ↔ (5,16). | 1 | **decisive** (0-1008) |
| W3 | **Retreat and heal paths ignore sleeping boss camps.** We wake them with AoE and flee through their range. | lost_world r47: Vesper killed by the monolith at (0,18); Ryth took 800 from it. Repeated 12 times in set a7ca9a58. | 1 (3 across sets) | major |
| W4 | **Long carrier walks with big bags** to far altars. | shortcut: 270 gems lost to champions (87 at (0,15), 84 at (23,17)); first tribute r252 vs r139. | 1-2 | major |
| W5 | **Slow opening on open 5-pick maps.** | crossing: 5 vs 31 clears by r300; r250 99-154. gemcombat2 r250 116-165. | 2 | minor (won both through fights) |

## Testable hypotheses (structure-keyed; no map or team names in the fix)
1. **H-pocket (W1; highest priority, live in v4).**
   - **Change.** In the heal branch, replace the Chebyshev `spawn_d > 6` gate with "our spawn is in `comp_of(pos)` and within about 8 walking steps".
     - If the spawn is not in our walk component: `recall()` when `recall_safe`, else `go_to(self.spawn)`. `go_to` falls back to `cross_toward`, which uses the dash or the held crystal.
     - Add a guard: if `step_toward` returns False on k consecutive heal turns, recall.
   - **Check.** Both 01shortcut sides locally: `gate-q24-all 01shortcut__B` reproduces the freeze at r886. Also `--maps all` with `tools/freeze_metric.py`.
   - **Expected.** Quiet champion-rounds on 01shortcut drop from 1,400-1,700 per game to under 300.
   - **Metric.** Games with any champion quiet ≥ 500 rounds to the end.
2. **H-contest (W2).**
   - **Change.** Count `dis` retreats per target group. After k ≥ 4 within 60 rounds, stamp the group "contested" for ~100 rounds and multiply its score by 0.3, so champions farm elsewhere.
     - If the contested groups hold most of the map's gems (≥ 50% within 8 of one altar), muster instead: wait out of enemy sight until ≥ 3 allies are within `GROUP_ADV_R`, then let the advantage branch decide.
   - **Validate.** Against an imitation that groups 5-6 bodies on a central field (Stellar, HoR, Ren, Cassi & Issac, Ryth). Self-play never contests the field.
   - **Metrics.** Clears per 100 rounds while enemies hold the field; r250 gem gap.
3. **H-boss-avoid (W3).**
   - **Change.**
     - (a) `retreat_fast`: add the ranges of *sleeping* camps of strength ≥ 200 within 8 as a key between incoming damage and enemy distance.
     - (b) Pass the same mask as `avoid` to the low-HP `step_toward(spawn)` and to `do_tribute`'s `step_toward`.
     - (c) In `kit_units_fast`, weight sleeping camps of strength ≥ 200 at -20, so area spells never wake a boss.
   - **Metric.** Deaths to camps per game on maps with a boss within 6 of a spawn exit, target ≤ 2.
4. **H-bankdist (W4).**
   - **Change.** Scale the bank thresholds by altar walking distance, e.g. `BANK_ANY = clamp(10 + 0.4 × altar_walk, 15, 30)`, so a 44-step altar banks at about 28 and a 15-step altar at about 16. Combine with H-tpaltar (John Doe report).
   - **Metrics.** Gems lost on death per game; mean bag at death.
5. **H-near-open (W5, low priority).**
   - **Change.** For the first ~150 rounds, add a distance term to `choose_target` (score /(d + 6)^1.3) so the first clears are the nearest groups.
   - **Metrics.** First clear and gems at r250 on large open maps. Watch the r1000 race too: the 50-gem early group may be worth it later.

**Opponent-specific notes (expectations, not fixes).**
- This bot loses grouped fights and drops big bags. Kill its Stellar carrier, and Cassi & Issac (2 bodies per kill).
- It wins whenever we cannot field all our champions (freezes) or refuse to contest its field.
