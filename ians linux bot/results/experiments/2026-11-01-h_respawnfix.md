# Experiment: h_respawnfix (2026-11-01)

Q21, universal respawn-rule movement fix. Run on the cluster (Slurm `test` partition, cambc 4.0.0 / engine 2.0.0).

## Hypothesis
- **What:** tb_merge_b's "never block a camp's respawn" rule reacts wrongly in general, not only on 01yellow-brick-road. It pushes a champion off *any* camp tile toward its target's centre and ends the turn.
  - By the engine rules, an occupied spawn tile only matters while that group is **Respawning** (GameRules, Camps & capture: "The group respawns together after rewards are claimed ... Any occupied spawn tile delays the entire group").
  - A general fix should remove these freezes on any map with this geometry and turn frozen rounds into clears and tributes.
- **Source:** the h_goldtie analysis (`bots/h_goldtie/NOTES.md`; `results/experiments/2026-10-31-batch1-interim.md` finding 2). On 01yellow-brick-road all 5 champions froze from r~200 to r2000, with 1 clear per game.

## Setup
- Candidate: `bots/h_respawnfix`, forked from the champion `tb_merge_b` with `tools/newbot.py`. Only `src/bot.py` changed (79 diff lines, all switched by `RESPAWN_FIX`). Design and iterations are in `bots/h_respawnfix/NOTES.md`.

### Reproduction and diagnosis
- `cambc run tb_merge_b tb_merge_b --map 01yellow-brick-road` gave 38-11 at r2000. First clears came at r75 and r234; 2-3 clears per team.
- Per-turn traces (a temporary traced fork, since deleted) showed **two** freeze mechanisms. The map has two 30-tile rows of gold clusters, each one camp group, splitting the map. Each row's centre sits next to a spawn.
  1. **Respawn-rule 2-cycle.**
     - The planner's path crosses a dead tile of a half-cleared row, which is a group that is still *Alive*.
     - The rule pushes the champion back toward `G.center` (Chebyshev) and returns. The next turn the planner steps on again.
     - Trace: slot 4 alternates `(10,13) -> (11,12) -> (10,13)` every 2 rounds from r~360 to r2000. Four of five champions were in such cycles at r1000.
     - The push turn returns before `note_progress`, and the step-on turn counts as progress, so the stuck guard never fires.
  2. **Unseen-alive guess undone every turn.**
     - Within 3 of `G.center`, with no live camp of G in sight, the code guesses "respawning" and returns.
     - The next turn `observe()` re-reads the engine state (Alive, because the live members are 20+ tiles down the row) and resets the status. The guess fires again, and the champion never moves.
     - v1 (mechanism 1 fixed only) still froze all 5 side-B champions from r13 next to the row centre `(34,12)`. Every turn ended at this guess; trace lines show `T-FARM (1, 0, (34,12))` with no move.

### Fix (final = v3)
- **(a)** Remove the in-turn push-back.
- **(b)** `leave_respawn_tile` step-off. A turn that ends stationary (`can_move()`), quiet (no enemy in sight, no camp hitting us) and not channelling, on a tile of a group whose engine state is `CampGroupRespawning`, steps to an adjacent non-camp tile. It prefers a tile that keeps a live target camp in attack range.
- **(c)** Farming stand-off and bush goals exclude spawn tiles of groups believed respawning (`resp_mask`).
- **(d)** The unseen-alive guess runs only when `observe()` did not read the group's state this turn (`Group.seen`).

### Iterations (screen = sprint 20 maps + 01yellow-brick-road, both sides)
- **v1:** (a) + (b). On 01yellow-brick-road: 23-0 W on side A, 0-4 L on side B. Still ~90% frozen (mechanism 2).
- **v2:** + (d). Screen 25W-17L.
  - Traces showed a new 2-cycle caused by (b): a ranged Vesper parked on a respawning stand-off tile, stepped off, and walked back, 45 turns at `(20,13)<->(21,14)`.
- **v3:** + (c) and the in-range step-off preference. Screen 25W-17L. v3 was kept because it removes the cycle its own rule could create. The freeze metric on the screen was 7.5% vs 8.1% for v2.

### Opponents and maps
- The champion `tb_merge_b` on all 70 maps, both sides (the gate head-to-head).
- A trigger census: `bots/h_rfx_count` (tb_merge_b plus counters only) vs tb_merge_b on all 140 games, with stdout kept.
- One `--release` game.

## Results
```
SUMMARY h_respawnfix vs tb_merge_b: 92W-48L (66%)  avg gems 736 vs 606  avg deaths 12.8 vs 13.5  botFaults(A) 0      [--maps all, matches/q21-all, job 56773895]
SUMMARY h_respawnfix vs tb_merge_b: 25W-17L (60%)  avg gems 704 vs 599  avg deaths 12.7 vs 13.9  botFaults(A) 0      [v3 screen: sprint + 01yellow-brick-road, matches/q21-v3-sprint]
SUMMARY h_respawnfix vs tb_merge_b: 25W-17L (60%)  avg gems 717 vs 556  avg deaths 12.0 vs 13.2  botFaults(A) 0      [v2 screen, same maps, matches/q21-v2-sprint]
Q21 CENSUS over 140 games: respawn-rule firings on NON-respawning tiles 17059 (135 games), on respawning tiles 9050; unseen-alive guess with fresh Alive state 12486 (38 games), stale 1067   [matches/q21-count]
```
- **Gate head-to-head:** 92/140 ≥ 82, 95% Wilson lower bound **57.5%**, botFaults 0.
- **Sprint subset of the all-maps run:** **23W-17L** (57.5%). It is identical game for game (40/40) to the separate v3 screen job, so cluster runs reproduce exactly. This is a new bot, so there is no dev-PC number to compare.
- **Release:** `cambc run h_respawnfix tb_merge_b --map 01big-world --release` lost 802-944. That is the same score as the non-release game, as expected from determinism. 0 crashes, 0 `bot error` lines, botFaults 0.
- **Batch-1 candidates vs tb_merge_b on all maps** (same harness, for scale): h_earlyfight_v2 control 77, h_3pick 75, h_goldtie 74, h_fightfuel 72, h_earlyfight_all 84. h_respawnfix's 92 is the highest.

### Contrast on 140 games, `analyze_match --summary` (h_respawnfix / tb_merge_b, per game)
| Metric | h_respawnfix | tb_merge_b |
|---|---|---|
| Clears | 50.1 | 46.6 |
| Gold earned | 5,422 | 4,785 |
| Camp deaths (total) | 163 | 179 |
| Champion deaths (total) | 1,636 | 1,717 |
| fuelExhausted | 93.0 | 87.2 |

- `match_metrics`: deaths_by_camp 1.2/game, gemsLost_to_camp 8.8/game, fuelExhausted 93.0/game.
- **Wins vs losses:**
  - Wins: 861.9 vs 461.6 gems; we died 8.0 times to champions; lead at r500 +55.
  - Losses: 494.2 vs 881.6 gems; we died **18.7** times to champions and lost 131.6 gems (vs 73.2 in wins); lead at r500 −44.
  - Camp deaths are the same in both (1.3 vs 0.9).

## Analysis session
### Did the targeted mechanism change? Yes.
**Census (how general the bug is).** Measured on tb_merge_b's own play, using the counter copy:
- **Push-back on a non-respawning tile:**
  - fired 17,059 times in **135/140 games**;
  - 65% of all the rule's firings were on such tiles;
  - ≥100 times in 40 games, for example 01yellow-brick-road A 3,318, 00packs B 973, adgato-gemcombat5 A 833, 02geodes B 574, 00rows B 530, 00vault B 464, 01corridors B 447.
- **Unseen-alive guess with a fresh Alive state:**
  - fired 12,486 times in 38 games, ≥100 in 14;
  - for example 01yellow-brick-road B 6,562, 00quarry B 1,503, 00quarry A 1,046, 01fracture B 776, 02harvest B 774, adgato-gemcombat1 B 280.
- **37 maps** had at least one side with ≥100 buggy firings. So the bug is general, not one map.

**In h_respawnfix:**
- The push-back cannot fire.
- The guess fired only on stale state: 8-10 `T-UNSEEN` lines per traced game, against 1,000+ in the census games.
- The new step-off fired **0 times in 7 fully traced games** (00quadrants B, 02famine B, 01yellow-brick-road A, 02the-pond B, 00crater A, 01concentrated-wealth B, 00rows A / 02tangle A). It is a rarely used safety net, not a behaviour driver.

**Freeze metric** (new `tools/freeze_metric.py`). A champion's frozen time is the length of its stretches of ≥150 alive rounds in which none of its activity counters change (damage, healing, gems, gold, kills, deaths).

| Freeze (% of champion-time) | All maps | Excl. 4 structural 0-0 maps (gift-wrapping, guardians, the-pack, boss-battle) | Stretches ≥300 |
|---|---|---|---|
| h_respawnfix in q21-all (140 games) | 90,764 champ-rounds = **8.6%** (62 games) | **4.7%** | 6.1% (27 games) |
| tb_merge_b, same games | 96,933 = 9.2% (76 games) | 5.2% | 6.8% (39 games) |
| tb_merge_b mirror (`matches/b1-tb_merge_b-mirror-all`, 70 games) | 12.9% / 12.1% | 9.3% / 8.4% | 10.3% / 9.9% |

**01yellow-brick-road:**

| | tb_merge_b mirror | h_respawnfix side A | h_respawnfix side B |
|---|---|---|---|
| Frozen champ-rounds per team | 8,002 / 9,065 | 571 | 0 |
| Score | 38-11 (A wins) | **696-206 W** | **1,020-209 W** |
| Clears | 2-3 | 30 | 38 |
| First clear | — | r314 | r82 |

- Our side-A clears went to 30 (Vesper 294 gems tributed). The opponent, still running tb_merge_b, stayed frozen for 2,714 / 1,894 champ-rounds.

**Largest per-map freeze drops** (tb_merge_b mirror average per team → h_respawnfix average):
- 01islands 1,990 → 0;
- 01broken-curve 1,586 → 0;
- 02geodes 1,525 → 0;
- 00quarry 1,032 → 0;
- 00packs 1,897 → 233;
- 02harvest 1,740 → 278;
- 00expanse 1,299 → 104;
- 00reverse-spiral 980 → 82;
- 00corners 4,691 → 1,964;
- 00rushbait-v2 4,001 → 1,706.

**Increases:**
- 02tangle 463 → 2,071;
- 00elkring 0 → 1,620;
- 00rows 0 → 934;
- 00pilgrimage 83 → 738;
- 01the-farm 262 → 799;
- 00quadrants 995 → 1,666;
- 01corridors 2,169 → 2,712.

Traced forks of those games show the long idle stretches are **pre-existing cycle types that this diff does not touch**:
- **Target flip-flop:** in 02tangle A (traced), slot 3 alternated targets G25 ↔ G27 between `(8,57)` and `(8,56)` for **467 turns**, and slot 4 for 288 turns. `choose_target`'s ×1.3 hysteresis is not enough.
- **Tribute altar alternation:** carriers bouncing between two altar goals (the lock-memory 2-cycle that h_3pick fixed).
  - 02famine B (traced): Vesper carrying 36 gems for 128 + 336 turns.
  - 00rows A (traced): 105 turns.
- **Capture standoff:** in 01yellow-brick-road A (traced), HoR waited 609 turns (`T-CAPWAIT`) on a tile of the 30-tile row. The group was RewardAvailable, but capture never completed because an enemy stood elsewhere on the same region.

### Losses (48)
Every loss is in the appendix table (`analyze_match` facts, freeze and census for each loss). The patterns:
- **Fight-decided (most losses):** our champion deaths far exceed the enemy's.

  | Map/side | Score | Our deaths / enemy deaths |
  |---|---|---|
  | 01hooks B | 154-1,001 | 49 / 8 |
  | 01elk-arena A | 252-972 | 44 / 13 |
  | 01elk-arena B | 288-918 | 50 / 15 |
  | 01starfish A | 262-873 | 43 / 18 |
  | 01starfish B | 381-663 | 41 / 23 |
  | 02arena B | 198-885 | 34 / 6 |
  | 00contest A | 0-1,000 | 34 / 4 |
  | 00ribs B | 213-1,023 | 36 / 9 |
  | 00eight A | 295-847 | 41 / 15 |
  | 00breadcrumbs A | 147-1,001 | 13 / 2 |
  | 00breadcrumbs B | 259-1,008 | 16 / 4 |
  | 00gemfight A | 301-1,016 | 20 / 6 |
  | 00gemfight B | 665-1,031 | 19 / 9 |
  | 00anvil A | 119-1,089 | 22 / 6 |

  These are the existing early-fight / burst problems (Q12, Q1), not movement.
  - The 00anvil A loss is chaotic divergence: v2 won the same map-side 1,006-82; v3 trailed 0-21 by r100 after an early fight.
- **Close races** (gem gap < 100 at the end):
  - 00galaxy A 993-1,018;
  - 02geodes B 997-1,005;
  - 00great-wall A 978-1,035;
  - adgato-gemcombat1 B 970-1,004;
  - 02uncharted-lands B 942-1,009;
  - 00split B 934-1,013;
  - 02harvest A 821-834.
- **Structural 0-0:**
  - 02guardians A/B and 02gift-wrapping A, lost on the tiebreak. Freeze there is 5,900-10,000 for both teams; this is Q2/Q3/Q26 territory.
  - The 0-0 wins on 01boss-battle A/B, 02the-pack A/B and 02gift-wrapping B are tiebreaks too.
- **Freeze-heavy losses:**
  - 01corridors A (4,100 frozen, 218-728; census 370 push-backs);
  - 00corners A (3,700);
  - 02tangle A (2,955);
  - 00quadrants B (2,459);
  - 00rows A (1,867);
  - 01big-world A (1,588);
  - adgato-gemcombat5 B (1,727, enemy 2,868).

  The traced forks attribute these to the remaining cycle types above, not to the new code.

### Regressions: did respawn blocking help anywhere?
- **Camp safety did not get worse.** Camp deaths were 163 for us vs 179 for tb_merge_b in the same games, and 168-171 for the other batch-1 forks.
  - 02geodes B lost 997-1,005 with **6 camp deaths**, 5 of them to camp#15 at `(63,9)` (r163, 167, 351, 353, 1,643).
  - The same camp kills 2-4 champions per game in **every** tb_merge_b fork (control, h_3pick, h_goldtie, h_fightfuel). It is a pre-existing trap, slightly worse here.
- **Against the other batch-1 forks on the same map-sides:**
  - 14 losses where ≥4/5 other forks won: 00gemfight B, 00great-wall A, 01hooks B, 02arena B, 02geodes B (5/5); 00anvil A, 00breadcrumbs B, 00galaxy A, 00lost-world B, 00quadrants B, 00rows A, 01the-farm A, 02famine B, 02tangle A (4/5).
  - 16 wins where ≥4/5 other forks lost, for example 00expanse B, 00reverse-spiral A, 00crater A (0/5 others), 00vault B, 01corridors B, 00rushbait-v2 B, 01big-world B.
  - Map-side flips are dominated by chaotic divergence. No loss shows a camp-death or freeze pattern caused by the new code.
- **Fuel:** fuelExhausted was 93.0/game vs 87.2 for tb_merge_b in the same games (+6.7%).
  - The other forks show the same us > them gap (control 87.1 vs 79.2, h_3pick 77.4 vs 72.0). Active champions on dense camp maps cost more `observe()` fuel; 01yellow-brick-road went to 1,034 / 877 exhaustions now that champions see the rows.
  - **Watch item for gate (c):** compare fuelExhausted with the paired gauntlet.
- **Where the gains come from:**
  - Wins do not concentrate on the high-census maps: 47/74 games on maps with ≥100 buggy firings vs 45/66 on the others; terciles by census count win 30/46, 31/47 and 31/47.
  - So the +22 over parity is broad. Plausibly it comes from the second-order effects of no longer being pushed off dead tiles inside the target group (closer engagement, standing on a tile when the last member dies), plus divergence noise.
  - The direct freeze removal is decisive on the maps where it fires heavily, 01yellow-brick-road above all.

### Surprising wins
- 00expanse B, 00reverse-spiral A and 00crater A were won although 0 of 5 other forks won them.
- 01yellow-brick-road 2-0 vs 1-1 in the mirror (decided by side).
- 01islands, 01broken-curve and 02geodes A dropped from ~1,500-2,000 frozen champ-rounds to 0.

## Verdict
**Kept.** Head-to-head gate passed:
- 92/140 (66%), Wilson lower bound 57.5% > 50%;
- botFaults 0;
- clean release game;
- mechanism confirmed by the census, traces and freeze metric.

Still needed before promotion (orchestrator): the paired gauntlet vs the champion's 158/200 baseline, and a fuelExhausted comparison on that pool. The fix is orthogonal to Q24's pieces (lock memory, gold play, early fights, fuel caching) and should be merged into Q24.

## New hypotheses generated
- **Universal oscillation guard:**
  - Detect `pos[t] == pos[t-2]` (or stationary with no attack) for ≥ 8 turns in **any** branch: farming, tribute travel, capture wait or ring wait. Then commit to one goal or ban the target for 30 rounds.
  - Today's stuck guard only sees farming turns that neither move nor attack. Any alternating move defeats it.
  - Evidence: traced forks show a 467-turn target flip-flop (02tangle A), 128 + 336-turn and 105-turn tribute 2-cycles (02famine B, 00rows A) and a 45-turn stand-off cycle. Idle time is still 4.7% of champion-time outside the structural maps.
- **Contested-capture standoff:**
  - On a RewardAvailable group, capture resets while any enemy is in the region. On long groups (30-tile rows) an idle or frozen enemy anywhere on the row blocks the capture forever.
  - Abandon after ~10 rounds of waiting with an enemy on the region, or go and contest/kill the blocker.
  - Evidence: 01yellow-brick-road A (traced), HoR stood in `T-CAPWAIT` for 609 turns at `(5,12)`.
- **Target-choice hysteresis:**
  - Score distance from the current target's committed goal, or require a ≥20% better score for N turns before switching.
  - Evidence: 02tangle A, slot 3 alternated G25 ↔ G27 each turn for 467 turns (`(8,57)` ↔ `(8,56)`). The ×1.3 current-target bonus does not cover a wall-induced distance jump of one tile.
- **Per-camp death trap memory:**
  - After 2 deaths to the same camp, hard-ban its group, or require full HP plus an ally.
  - Evidence: 02geodes B, camp#15 at `(63,9)` killed us 5 times (r163-1,643). Every tb_merge_b fork dies there 2-4 times per game. DEATH_PENALTY 0.3 for 250 rounds is not enough.
- **Respawn denial as a tool (speculative):**
  - Standing on a Respawning group's spawn tile blocks it indefinitely. A champion with no target could park on a high-value group near the enemy side instead of idling.
  - Evidence: the engine rule, plus 9,050 legitimate rule firings in the census (our champions often stand on respawning tiles).
  - Test only after the oscillation guard.
- **Add the freeze metric to the gate analysis:** `tools/freeze_metric.py matches/<tag>` costs nothing and flags new stalls, such as v2's step-off cycle, before they cost games.

## Appendix: every loss in `matches/q21-all`
Columns:
- final score and rounds;
- the round from which the winner stayed ahead;
- the gem race at r250, r500 and r1000;
- clears (us/them);
- our kills / our deaths (camp deaths in brackets);
- gems lost (us/them);
- frozen champ-rounds (us/them);
- fuelExhausted (us/them);
- census firings for tb_merge_b on that map-side (push-back on non-respawning tiles / fresh unseen guess);
- how many of the 5 other batch-1 forks won that map-side.

```
00ambush__B                   827-1011 r1865 lead-from r1500  r250 14-14 r500 56-108 r1000 323-316  clr 57/42  K/D 2/4(camp 0)  gemloss 14/51  freeze 660/165  fuelExh 10/8  census nonresp/unseen 100/0  other-cands won 1/5
00anvil__A                    119-1089 r1806 lead-from r100  r250 0-88 r500 36-173 r1000 57-498  clr 54/75  K/D 6/22(camp 1)  gemloss 98/27  freeze 0/0  fuelExh 6/2  census nonresp/unseen 3/0  other-cands won 4/5
00breadcrumbs__A              147-1001 r1066 lead-from r100  r250 21-133 r500 63-364 r1000 147-896  clr 99/170  K/D 2/13(camp 0)  gemloss 182/0  freeze 0/0  fuelExh 6/2  census nonresp/unseen 0/0  other-cands won 3/5
00breadcrumbs__B              259-1008 r1140 lead-from r250  r250 70-175 r500 126-399 r1000 210-868  clr 122/184  K/D 4/16(camp 0)  gemloss 189/56  freeze 0/0  fuelExh 1/0  census nonresp/unseen 0/0  other-cands won 4/5
00contest__A                    0-1000 r1800 lead-from r1500  r250 0-0 r500 0-0 r1000 0-0  clr 85/95  K/D 4/34(camp 0)  gemloss 0/200  freeze 0/187  fuelExh 12/4  census nonresp/unseen 37/0  other-cands won 0/5
00corners__A                  369-645  r2000 lead-from r1000  r250 34-15 r500 128-15 r1000 262-296  clr 40/59  K/D 21/3(camp 0)  gemloss 55/94  freeze 3700/2200  fuelExh 23/38  census nonresp/unseen 7/0  other-cands won 3/5
00dunes__A                    775-917  r2000 lead-from r100  r250 60-94 r500 78-173 r1000 273-321  clr 20/30  K/D 23/22(camp 2)  gemloss 108/206  freeze 154/0  fuelExh 64/77  census nonresp/unseen 62/0  other-cands won 2/5
00dunes__B                    616-1006 r1867 lead-from r250  r250 0-73 r500 84-143 r1000 206-484  clr 25/23  K/D 8/25(camp 0)  gemloss 217/82  freeze 0/0  fuelExh 66/67  census nonresp/unseen 102/0  other-cands won 2/5
00eight__A                    295-847  r2000 lead-from r1500  r250 0-27 r500 41-42 r1000 184-78  clr 29/36  K/D 15/41(camp 2)  gemloss 236/89  freeze 0/0  fuelExh 69/62  census nonresp/unseen 86/0  other-cands won 1/5
00galaxy__A                   993-1018 r1744 lead-from r1500  r250 137-21 r500 284-212 r1000 576-491  clr 59/60  K/D 10/14(camp 0)  gemloss 160/55  freeze 515/350  fuelExh 3/10  census nonresp/unseen 16/0  other-cands won 4/5
00gemfight__A                 301-1016 r1210 lead-from r500  r250 144-29 r500 209-249 r1000 285-778  clr 41/40  K/D 6/20(camp 1)  gemloss 173/21  freeze 0/0  fuelExh 38/58  census nonresp/unseen 66/0  other-cands won 0/5
00gemfight__B                 665-1031 r1583 lead-from r750  r250 177-18 r500 345-75 r1000 381-629  clr 59/57  K/D 9/19(camp 2)  gemloss 155/41  freeze 0/0  fuelExh 80/45  census nonresp/unseen 138/0  other-cands won 5/5
00great-wall__A               978-1035 r1858 lead-from r750  r250 19-74 r500 166-147 r1000 345-422  clr 73/61  K/D 11/16(camp 3)  gemloss 291/207  freeze 0/413  fuelExh 1/18  census nonresp/unseen 76/153  other-cands won 5/5
00lost-world__B               828-1017 r1236 lead-from r250  r250 173-232 r500 215-601 r1000 663-877  clr 62/61  K/D 5/27(camp 5)  gemloss 161/60  freeze 0/166  fuelExh 69/70  census nonresp/unseen 39/130  other-cands won 4/5
00monolith__B                 586-1059 r1652 lead-from r500  r250 54-27 r500 101-111 r1000 318-355  clr 59/74  K/D 3/20(camp 0)  gemloss 89/46  freeze 0/0  fuelExh 20/17  census nonresp/unseen 129/0  other-cands won 1/5
00quadrants__B                843-1030 r1416 lead-from r1500  r250 125-54 r500 348-245 r1000 750-682  clr 29/35  K/D 6/4(camp 0)  gemloss 76/56  freeze 2459/937  fuelExh 166/39  census nonresp/unseen 39/0  other-cands won 4/5
00ribs__A                     543-756  r2000 lead-from r500  r250 43-0 r500 100-157 r1000 208-328  clr 30/34  K/D 16/29(camp 0)  gemloss 134/106  freeze 0/0  fuelExh 28/24  census nonresp/unseen 37/20  other-cands won 3/5
00ribs__B                     213-1023 r1688 lead-from r250  r250 15-128 r500 15-306 r1000 86-514  clr 13/31  K/D 9/36(camp 2)  gemloss 85/41  freeze 339/0  fuelExh 16/9  census nonresp/unseen 9/0  other-cands won 0/5
00rows__A                     257-768  r2000 lead-from r500  r250 0-0 r500 12-83 r1000 106-222  clr 33/47  K/D 3/11(camp 2)  gemloss 22/19  freeze 1867/0  fuelExh 21/28  census nonresp/unseen 101/0  other-cands won 4/5
00split__B                    934-1013 r1858 lead-from r1000  r250 103-129 r500 224-233 r1000 411-463  clr 45/57  K/D 13/13(camp 1)  gemloss 138/102  freeze 169/174  fuelExh 226/353  census nonresp/unseen 141/0  other-cands won 3/5
00the-line__B                 203-1040 r1689 lead-from r250  r250 0-169 r500 0-260 r1000 203-521  clr 16/30  K/D 6/18(camp 0)  gemloss 219/54  freeze 409/631  fuelExh 78/53  census nonresp/unseen 14/14  other-cands won 0/5
00vault__A                      4-1045 r554  lead-from r250  r250 4-343 r500 4-698 r1000 4-1045  clr 8/12  K/D 3/8(camp 0)  gemloss 4/0  freeze 0/0  fuelExh 226/276  census nonresp/unseen 124/0  other-cands won 3/5
01big-world__A                802-944  r2000 lead-from r500  r250 22-0 r500 94-154 r1000 208-343  clr 52/59  K/D 4/2(camp 1)  gemloss 68/52  freeze 1588/215  fuelExh 33/38  census nonresp/unseen 80/0  other-cands won 1/5
01broken-curve__A             707-1105 r1642 lead-from r750  r250 48-72 r500 164-147 r1000 330-459  clr 43/59  K/D 6/12(camp 3)  gemloss 80/18  freeze 0/0  fuelExh 1/0  census nonresp/unseen 48/0  other-cands won 3/5
01corridors__A                218-728  r2000 lead-from r1000  r250 0-0 r500 20-4 r1000 76-144  clr 16/25  K/D 6/7(camp 2)  gemloss 38/26  freeze 4100/2008  fuelExh 0/0  census nonresp/unseen 370/0  other-cands won 3/5
01elk-arena__A                252-972  r2000 lead-from r1500  r250 0-0 r500 72-72 r1000 252-252  clr 113/128  K/D 13/44(camp 0)  gemloss 72/36  freeze 0/0  fuelExh 146/109  census nonresp/unseen 179/0  other-cands won 3/5
01elk-arena__B                288-918  r2000 lead-from r1000  r250 0-0 r500 72-72 r1000 192-240  clr 92/122  K/D 15/50(camp 0)  gemloss 60/60  freeze 0/150  fuelExh 138/101  census nonresp/unseen 148/0  other-cands won 2/5
01gold-rush__B                286-1018 r1708 lead-from r500  r250 44-33 r500 77-121 r1000 154-319  clr 57/75  K/D 0/23(camp 0)  gemloss 44/0  freeze 0/348  fuelExh 77/34  census nonresp/unseen 16/0  other-cands won 3/5
01hooks__B                    154-1001 r1912 lead-from r1000  r250 0-22 r500 66-22 r1000 154-209  clr 37/107  K/D 8/49(camp 0)  gemloss 66/55  freeze 0/362  fuelExh 51/29  census nonresp/unseen 43/138  other-cands won 5/5
01shortcut__B                 458-613  r2000 lead-from r1000  r250 32-0 r500 68-66 r1000 218-267  clr 50/36  K/D 6/20(camp 1)  gemloss 397/166  freeze 1180/1738  fuelExh 1/2  census nonresp/unseen 38/0  other-cands won 3/5
01starfish__A                 262-873  r2000 lead-from r750  r250 0-18 r500 42-36 r1000 153-191  clr 24/39  K/D 18/43(camp 0)  gemloss 281/154  freeze 0/187  fuelExh 84/110  census nonresp/unseen 99/0  other-cands won 3/5
01starfish__B                 381-663  r2000 lead-from r250  r250 4-36 r500 19-90 r1000 120-186  clr 26/30  K/D 23/41(camp 1)  gemloss 248/221  freeze 0/0  fuelExh 75/66  census nonresp/unseen 155/0  other-cands won 1/5
01the-farm__A                 609-1015 r1725 lead-from r500  r250 80-58 r500 139-163 r1000 325-411  clr 27/38  K/D 2/9(camp 0)  gemloss 76/48  freeze 646/158  fuelExh 37/22  census nonresp/unseen 20/0  other-cands won 4/5
02arena__B                    198-885  r2000 lead-from r750  r250 84-52 r500 122-74 r1000 190-252  clr 37/75  K/D 6/34(camp 0)  gemloss 98/54  freeze 0/0  fuelExh 2/0  census nonresp/unseen 12/0  other-cands won 5/5
02famine__B                   671-958  r2000 lead-from r500  r250 90-76 r500 151-198 r1000 355-364  clr 37/52  K/D 10/16(camp 0)  gemloss 120/35  freeze 908/263  fuelExh 1/4  census nonresp/unseen 52/2  other-cands won 4/5
02fields__A                   555-1044 r1653 lead-from r500  r250 44-37 r500 63-186 r1000 296-499  clr 66/57  K/D 11/27(camp 0)  gemloss 210/87  freeze 0/0  fuelExh 12/15  census nonresp/unseen 28/153  other-cands won 0/5
02geodes__B                   997-1005 r1755 lead-from r500  r250 87-69 r500 152-224 r1000 394-503  clr 51/62  K/D 8/14(camp 6)  gemloss 139/95  freeze 0/0  fuelExh 3/3  census nonresp/unseen 574/0  other-cands won 5/5
02gift-wrapping__A              0-0    r2000 lead-from rNone  r250 0-0 r500 0-0 r1000 0-0  clr 0/0  K/D 0/0(camp 0)  gemloss 0/0  freeze 10000/10000  fuelExh 0/0  census nonresp/unseen 0/0  other-cands won 1/5
02guardians__A                  0-0    r2000 lead-from rNone  r250 0-0 r500 0-0 r1000 0-0  clr 8/12  K/D 5/5(camp 1)  gemloss 31/8  freeze 6127/5917  fuelExh 0/0  census nonresp/unseen 1/0  other-cands won 3/5
02guardians__B                  0-0    r2000 lead-from rNone  r250 0-0 r500 0-0 r1000 0-0  clr 12/9  K/D 4/5(camp 0)  gemloss 37/37  freeze 5860/6124  fuelExh 0/0  census nonresp/unseen 0/0  other-cands won 3/5
02harvest__A                  821-834  r2000 lead-from r750  r250 47-36 r500 139-84 r1000 234-280  clr 57/54  K/D 8/16(camp 1)  gemloss 34/50  freeze 154/753  fuelExh 4/3  census nonresp/unseen 13/18  other-cands won 2/5
02tangle__A                   731-1017 r1759 lead-from r1000  r250 73-73 r500 189-195 r1000 365-444  clr 32/50  K/D 0/4(camp 3)  gemloss 11/0  freeze 2955/1152  fuelExh 19/20  census nonresp/unseen 39/0  other-cands won 4/5
02the-pond__A                 499-606  r2000 lead-from r1000  r250 30-15 r500 100-65 r1000 202-207  clr 36/41  K/D 6/19(camp 0)  gemloss 129/63  freeze 191/170  fuelExh 7/11  census nonresp/unseen 14/9  other-cands won 2/5
02the-pond__B                 528-622  r2000 lead-from r500  r250 50-36 r500 79-100 r1000 262-318  clr 41/38  K/D 9/11(camp 0)  gemloss 73/30  freeze 296/411  fuelExh 15/13  census nonresp/unseen 19/113  other-cands won 2/5
02uncharted-lands__B          942-1009 r1442 lead-from r500  r250 185-161 r500 343-391 r1000 609-708  clr 59/60  K/D 6/13(camp 1)  gemloss 98/47  freeze 207/0  fuelExh 8/6  census nonresp/unseen 148/0  other-cands won 3/5
adgato-gemcombat1__B          970-1004 r1624 lead-from r1500  r250 98-143 r500 308-259 r1000 665-595  clr 50/45  K/D 10/11(camp 0)  gemloss 153/115  freeze 0/0  fuelExh 2/0  census nonresp/unseen 19/280  other-cands won 1/5
adgato-gemcombat2__B          797-1044 r1341 lead-from r500  r250 161-126 r500 308-336 r1000 531-788  clr 39/43  K/D 7/21(camp 0)  gemloss 253/91  freeze 0/0  fuelExh 9/7  census nonresp/unseen 20/39  other-cands won 0/5
adgato-gemcombat5__B          840-1064 r1706 lead-from r1500  r250 56-0 r500 420-84 r1000 567-539  clr 26/20  K/D 9/26(camp 0)  gemloss 693/294  freeze 1727/2868  fuelExh 78/60  census nonresp/unseen 521/0  other-cands won 1/5
```
