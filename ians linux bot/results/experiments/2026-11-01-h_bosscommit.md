# Experiment: h_bosscommit, boss-camp commit timing (2026-11-01)

STRATEGIES V3L-3. Run on the cluster (Slurm `test` partition through `tools/onslurm.sh`, cambc 4.0.0 / engine 2.0.0).
Candidate `bots/h_bosscommit` (design and flags in `bots/h_bosscommit/NOTES.md`). Variants: `bots/h_bosscommit_nj` (no Jungle-first)
and `bots/h_bosscommit_v4` (enemy gate + commit time cap). Debug copy with fuel-free `debug_block` traces: `bots/dbg_bc_trace`.
**Verdict: rejected.** The commit moved our boss clears earlier, but it halved our farming on the boss maps and lost 12 of 16 games there against c2.

## Hypothesis
- **What:** when most of a map's gems sit in one giant camp group (a monolith, a golem stack), commit the team to it much earlier than c2 does. That means:
  - judging the boss by team kill time against team HP;
  - mustering near it;
  - recapturing it when it respawns, instead of farming small camps.
- **Source: real ladder games** (`matches/ladder/summary`, measured with `bossmetrics.py`, below).

  | match | map | opponent | result | boss clears us / them | their first boss clear | notes |
  |---|---|---|---|---|---|---|
  | c706decb | 00contest | 中国人能飞 | L 0-1000 (r1412) | 0 / 5 | r752 | We made 88 clears to their 49, but they had 4x our monster damage (122k vs 33k). Kills 3 vs 19, gold 5,555 vs 6,960. |
  | d8736f52 | 00contest | Mein Kraft | L 400-1000 (r1465) | 0 / 7 | **r589** | Our 400 came from killing their Varg twice while he carried a 200-gem bag (r644, r765). Their build was Jungle + Monster + Durability, with Willow. |
  | 103657e7 | 00contest | Halma (v2) | W 1000-0 | 5 / 0 | - | Our first boss clear was r1538. |

  - **On all 81 ladder games on maps with boss groups** (all versions): we cleared bosses 28 times in 12 games, median first clear **r1338**. Opponents cleared 22 times in 6 games, median **r1033**.
  - **Other boss-decided ladder losses:** 01broken-curve (opponent's first boss clear r1033), 01shortcut (r1219) and 01starfish (r982).
- **Local timing (before):** c2_respawn's median first boss clear on the 8 boss maps below was **r1804** against tb_merge_b and **r1671** against q24_combo. On 00contest it was r1156/r1322 against tb_merge_b and r1671/r1807 against q24.

## Setup
### Census: share of gems in boss groups
- **Source:** `matches/q26-census/*.stdout.txt` (group dumps for all 70 maps).
- **Boss group:** a monolith, total HP ≥ 15,000, or strength ≥ 250.
- **Share:** static share of gems, and share of gem *rate* (gems / max respawn timer).
- 26 maps have boss groups. On these 8 the boss groups hold at least 50% of the gem rate:

| Map | Rate share | Static share | Boss groups |
|---|---|---|---|
| 00contest | 1.00 | 1.00 | 2 monoliths (200 g each). Every other group is gold clusters (0 gems). |
| 00stampede | 1.00 | 1.00 | 1 group: 6 wolves + 10 elks + 4 golems (160 g, 16,080 HP, strength 360) |
| 00great-wall | 0.61 | 0.77 | 2× (2 monoliths + 2 clusters; 414 g, 40,240 HP, s400) + (4 golems + 16 clusters; 256 g, s480) |
| 00rows | 0.58 | 0.80 | 2 monoliths + 10 clusters (470 g, 41,200 HP, s400) |
| 00anvil | 0.53 | 0.78 | 1 monolith (3-pick) |
| 00monolith | 0.53 | 0.76 | 2× (monolith + 8 clusters, 256 g) |
| 01starvation | 0.53 | 0.75 | 2 monoliths, 80×80 |
| 01gold-rush | 0.50 | 0.75 | monolith + 4 gold clusters (3-pick) |

02the-pack (0.55) is a no_tribute guard ring (strength 960) and is excluded.

### How c2 values and gates bosses (`choose_target`, danger check)
- **Solo safety model.** A monolith gives `dmg = 200*ttk/(1+c) > hp-150`. Hit-and-run then needs a positive budget `maxhp - 200*(5+1) - 80`, i.e. maxhp > 1,280, and at most 4 cycles. Claims add only 55 dps per ally.
- **Danger check.** Every awake camp in range counts as hitting us, and the exit cost is the free-field `s*(r-d+2)+60`: 1,260 HP for a melee champion next to a monolith. So base melee champions cannot stand next to a monolith at all.

### Engine fact measured here
**A camp hits the Chebyshev-nearest champion of either team, and ties go to the lowest unit id.**
- Method: `BT` end-of-turn traces in 4 games (`matches/bc-trace2/A`, `bc-trace2/D`, `bc-trace3/A`, `bc-trace4/A`), with targets inferred from 140/200 HP drops between consecutive turns (`targeting2.py`).
- Chebyshev nearest explains **665/665** inferred boss hits. Euclidean explains 629/665 and Manhattan 606/665.
- **78/78 Chebyshev ties** went to the lowest unit id (lowest Euclidean distance would explain only 43).

### Candidate (final = v3), forked from c2_respawn with `tools/newbot.py`
Only `src/bot.py` changed. Every change is gated by `boss_on`, so on the other 62 maps the bot plays c2's logic.
1. **Boss map test:** `init_boss` uses the rate share ≥ 0.5 (structure only, no map names).
2. **Team commit** (`boss_check`):
   - The team is estimated as n_team copies of me.
   - `usable = maxhp - (s_eff*4+60)` and `waves = s_eff*ttk_team / (k*usable)`. Commit when waves ≤ 1.25.
   - Cost = travel + team kill time; claims raise the score.
3. **Rally byte** (shared byte 6 = boss idx + 1):
   - Champions able to hold the aggro join.
   - While a rally is active, only the rallied boss gets the commit.
   - The byte is cleared on capture or respawn.
4. **Nearest-champion danger** (`boss_danger`, using the measured rule):
   - A boss camp is ignored while a healthy other champion is nearer (or tied with a lower id).
   - Otherwise the exit cost stops where a healthy other champion would take the aggro.
5. **Escape field** per boss group: the walking distance out of its range.
   - Used for the solo exit cost, for the retreat (`boss_escape`, dash if it saves a step) and to filter stand tiles (no dead ends).
6. **Jungle emblem first** on boss maps (-30% camp damage).
7. **Muster** (v2) is off in v3. `BOSS_LOG` (debug) is off.

### Iterations (each screened on the 8 boss maps, both sides, 16 games)
- **v0:** waves ≤ 3, tie = 1 step, muster with a timeout that ends in a solo attack.
- **v1:** + healthy-cover danger model, Jungle-first, 3-hit reserve.
- **v2:** + escape field, lowest-id ties, waves ≤ 1.25 with a 4-hit reserve, rally byte, muster that bans instead of attacking solo, death penalty kept.
- **v3 (final):** muster off; rally exclusive to one boss; no rally clear on death.
- **Ablations of v3:** `h_bosscommit_nj` (no Jungle-first); `h_bosscommit_v4` (commit only if no enemy was seen within 10 of the boss for 30 rounds, plus a 120-round commit cap followed by a 200-round ban).
- **Opponents:** c2_respawn, and tb_deathball (a different-logic team that moves as one group and takes bosses). Then the final version on all maps against c2_respawn and tb_merge_b.

## Results
```
SUMMARY h_bosscommit vs c2_respawn: 69W-71L (49%)  avg gems 700 vs 698  avg deaths 10.4 vs 10.6  botFaults(A) 0     [FINAL v3, --maps all, matches/h_bosscommit-all, job 56828840]
SUMMARY h_bosscommit vs tb_merge_b: 94W-46L (67%)  avg gems 761 vs 581  avg deaths 10.1 vs 13.1  botFaults(A) 0     [FINAL v3, --maps all, matches/h_bosscommit-tbm-all, job 56828836]
SUMMARY h_bosscommit vs c2_respawn: 4W-12L (25%)  avg gems 491 vs 806  avg deaths 14.6 vs 8.9  botFaults(A) 0      [v3 screen, 8 boss maps, matches/bc-scr4-c2]
SUMMARY h_bosscommit_nj vs c2_respawn: 3W-13L (19%)  avg gems 433 vs 784  avg deaths 13.5 vs 7.8  botFaults(A) 0   [v3 without Jungle-first, matches/bc-scr4nj-c2]
SUMMARY h_bosscommit_v4 vs c2_respawn: 3W-13L (19%)  avg gems 482 vs 763  avg deaths 13.5 vs 9.9  botFaults(A) 0   [v4 enemy gate + commit cap, matches/bc-scr5v4-c2]
SUMMARY h_bosscommit vs c2_respawn: 5W-11L (31%)  avg gems 442 vs 774  avg deaths 13.5 vs 8.4  botFaults(A) 0      [v2 screen, matches/bc-scr3-c2]
SUMMARY h_bosscommit vs c2_respawn: 3W-13L (19%)  avg gems 364 vs 841  avg deaths 18.1 vs 5.9  botFaults(A) 0      [v1 screen, matches/bc-scr2-c2]
SUMMARY h_bosscommit vs c2_respawn: 2W-14L (12%)  avg gems 275 vs 871  avg deaths 21.4 vs 5.6  botFaults(A) 0      [v0 screen, matches/bc-scr1-c2]
SUMMARY h_bosscommit vs tb_deathball: 13W-3L (81%)  avg gems 709 vs 179  avg deaths 7.6 vs 30.4  botFaults(A) 0    [v2, matches/bc-scr3-db]
SUMMARY h_bosscommit vs tb_deathball: 12W-4L (75%)  avg gems 746 vs 239  avg deaths 12.6 vs 25.6  botFaults(A) 0   [v1, matches/bc-scr2-db]
SUMMARY h_bosscommit vs tb_deathball: 10W-6L (62%)  avg gems 613 vs 320  avg deaths 14.0 vs 23.5  botFaults(A) 0   [v0b, matches/bc-scr1-db]
SUMMARY c2_respawn vs tb_deathball: 15W-1L (94%)  avg gems 803 vs 198  avg deaths 5.2 vs 36.6  botFaults(A) 0      [baseline, matches/bc-base-c2-db]
```

### Gate (LOOP.md §4)
- **Head-to-head:** 69/140 < 82 (95% Wilson interval 0.41-0.57). It fails. botFaults 0.
- **Split by map group:**

  | Run | 8 boss maps | Other 62 maps |
  |---|---|---|
  | vs c2_respawn | **4/16** | 65/124 (noise) |
  | vs tb_merge_b | **5/16** | 89/124 |
  | c2's own vs tb_merge_b run (`skc2-vs-tbm-all`) | 9/16 | 89/124 |

  - Against tb_merge_b, 60 of the 124 non-boss games are byte-identical to c2's. The other 64 diverge by fuel chaos, with 24 result flips that net to 0.
  - **The whole −4 against c2's 98/140 comes from the boss maps.**
- **The v3 screen and the final run agree:** the 16 boss-map games of the final run are identical to the v3 screen. Local games are deterministic.
- Not run, since the head-to-head fails: the gauntlet and the release game.

### Economy and deaths on the 8 boss maps (`econ.py`, per game, us / them)
| Run | W/16 | Clears | Gold earned | Camp deaths us | Champion deaths us | Boss clears us / them | Median first boss clear us / them |
|---|---|---|---|---|---|---|---|
| c2 vs tb_merge_b (before) | 9 | 79.6 / 76.2 | 7,463 / 6,973 | 0.7 | 11.3 | 18 / 5 | r1804 / r1525 |
| c2 vs q24_combo (before) | 9 | 86.7 / 76.7 | 7,686 / 6,548 | 0.8 | 7.9 | 10 / 8 | r1671 / r1341 |
| v0 vs c2 | 2 | 29.4 / 97.8 | 2,693 / 8,473 | **11.6** | 9.8 | 11 / 20 | r1484 / r1273 |
| v1 vs c2 | 3 | 31.6 / 91.6 | 3,022 / 8,665 | 5.2 | 12.9 | 14 / 21 | r1217 / r1184 |
| v2 vs c2 | 5 | 48.1 / 86.2 | 4,546 / 8,019 | **1.4** | 12.1 | 13 / 21 | r1254 / r1277 |
| **v3 (final) vs c2** | **4** | **39.4 / 90.2** | **4,002 / 8,190** | 3.9 | 10.8 | **21 / 19** | **r1184 / r1359** |
| v3 no-Jungle vs c2 | 3 | 45.4 / 93.1 | 4,253 / 7,980 | 3.2 | 10.2 | 16 / 14 | r1350 / r1582 |
| v4 vs c2 | 3 | 60.4 / 80.3 | 5,096 / 7,862 | 2.0 | 11.5 | 5 / 22 | r1445 / r1438 |
| v3 vs tb_merge_b (final) | 5 | 40.0 / 87.2 | 4,115 / 7,842 | 3.8 | 12.3 | - | - |
| c2 vs tb_deathball | 15 | 77.2 / 44.2 | 9,235 / 3,878 | 1.0 | 4.2 | 24 / 0 | r1068 |
| v2 vs tb_deathball | 13 | 52.8 / 57.9 | 6,874 / 4,730 | 1.7 | 5.9 | 18 / 2 | r1035 |

## Analysis session
### Did the targeted mechanism change? Yes: we clear bosses earlier, but the games are lost
- **Timing.** Our median first boss clear moved from r1804 (c2 vs tb_merge_b) to **r1184** (final vs c2).
  - We cleared 21 bosses to c2's 19 in the same games.
  - Against tb_deathball the v0/v1 versions reached r976/r928 (c2: r1068).
  - On 00contest the earliest local boss clears were r795 (no-Jungle variant) and r873/r939 (v0, v3). The best ladder opponent's was r589.
- **Cost.** Our gold on the boss maps fell from 7,463 to 4,002 per game, and our clears from 79.6 to 39.4. c2 (8,190 gold) then outfights us: champion deaths 10.8 vs 5.5.
- **The boss captures do not convert:**
  - In the final 00contest A game (`matches/h_bosscommit-all/00contest__A.json`), Vesper killed monolith g0 at **r939**.
  - The capture was contested until **r985**, when Marcella got 200 gems.
  - c2's Ryth killed Marcella at (14,29) at **r996** and took the bag; c2 tributed it at r1032.
  - We finished with 200-1000, gold 2,105 vs 11,868, and K/D 4/25.
- **We fed c2's boss timing.** Camps do not heal, so our chip damage counted for whoever finished the boss.
  - On 00contest side B, c2's first boss clear against us was r997, against r1322 in its own game against tb_merge_b. Side A was about the same (r1166 vs r1156).
  - Over the 8 maps, c2's median first boss clear as our opponent was r1359. As tb_merge_b's opponent its own was r1804.

### Why each version lost (traces, `bots/dbg_bc_trace`; `debug_block` lines are fuel-free)
**v0/v1: camp deaths (11.6 and 5.2 per game).**
- Trace `matches/bc-trace2/A` (00contest): Marcella attacked monolith (17,31) alone (r293, 1,200 HP) and retreated at r296.
- c2's `retreat` breaks ties among the in-range tiles by **distance to our spawn**. Our spawn lies behind the pocket's north wall, so the retreat walked into the dead-end corner **(14,29)**: every neighbour is a wall or closer to the boss.
- She stood there at d=3 losing 140 per round, from 640 to dead at r301 (BD lines r293-301).
- In that v1 game 10 of our 13 camp deaths were at (14,29) or (12,30). In the v0 trace (`bc-trace1/A`), 10 of 27 were at (14,29). Causes: the dead-end corner, the free-field exit cost, and (in v0) muster timeouts ending in solo attacks.
- **v2's escape field fixed this:** camp deaths fell to 1.4 per game (0.8 in wins).

**v2: idle mustering and a split team.**
- Trace `matches/bc-trace3/A`: slot 0 committed at r409 (waves 0.97) and the rally pulled in slots 1, 3 and 4.
- **685 muster turns** followed, mostly with 2 of the 3 needed champions in sight.
- The 30-round bans cleared the rally, and champions flipped between g0 and g1 (on the enemy's side).

**v3 (final): commit equals starvation.**
- Trace `matches/bc-trace4/A`: first commit at r409, then **5,950 champion-rounds** targeting a boss. That is about 93% of the team's time after r409.
- Max HP stayed at 1,200-1,600 through r1100, because there was no farming.
- c2's roaming champions kept forcing retreats and recalls. The kill that "should" take 40 rounds took 500.
- On 00great-wall (`bc-trace4/G`) the team committed at r938 to group 2 (4 golems + 16 clusters, 21,920 HP, s480) and spent **3,228 champion-rounds with 0 clears**.

**Ablations: the commit itself is the cause.**
- Without Jungle-first: 3/16, and gold barely changed (4,253).
- With an enemy-presence gate and a 120-round commit cap (v4): 3/16, gold 5,096, and boss clears fell to 5 against c2's 22. With the gate, c2 roams near the bosses, so we rarely commit, yet we still farm less than c2.

### Losses: decided by the fight and the gold race, not by camps
- **Final vs c2, 71 losses** (`analyze_match --summary`): kills 5.0 vs 13.4; gold 4,059 vs 6,987; clears 44 vs 62.
- **On the boss maps:**

  | Map | Result | Losing pattern |
  |---|---|---|
  | 00contest | 0-2 | both lost 1000-0 / 1000-200; c2 took 5-6 bosses from r997-1166 |
  | 00monolith | 0-2 | c2's first boss r1359 / r1584 |
  | 01gold-rush | 0-2 (B 280-1002) | c2's bosses from r994 |
  | 01starvation | 0-2 | slow gem race, we 302 / 150 |
  | 00anvil | 0-2 | we killed the boss first (r1184 / r1204), but the bags went to c2 (221 / 421 boss gems to c2, 0 to us) |
  | 00great-wall | 0-2 | B 711-996 |

### Surprising wins
- **00stampede, 2/2 vs c2** (400-80, 720-80): the boss is the map's only gem source (1.00).
  - We cleared it 3 and 6 times (first r1119 / r959). c2 never cleared it.
  - Strength 360 spread over 20 camps is tankable once Jungle is in.
- **00rows, 2/2 vs c2:** one late boss clear each (r1641 / r1675).
- **Ladder relevance of 00stampede:** it has no ladder games in our log, so this edge is untested where it counts.

### Fuel (defect, not the cause)
- On the boss maps we had **75.8 fuelExhausted per game** (c2: 0.6). They were concentrated on 00stampede (517 / 447) and 00rows (109 / 78).
- Cause: the stand-tile filter loops `goals × alive camps` in Python for 20-camp groups, and `boss_danger` reads `vision.champions()` every turn.
- 00stampede was won anyway. 00contest, 00monolith and 00anvil had ≤ 2 exhaustions and were still lost.
- Other maps: 8.2 vs 7.6.

### Ladder reading
- The two 00contest ladder losses were **fight** losses as much as timing: kills 3 vs 19, and they had 4x our monster damage with Power, Durability and Jungle builds.
- Our own v3 shows what an early commit costs a weak team. A rule that makes us take the boss early without first winning the area hands the bag to whoever controls the area.

## Verdict
**Rejected.**
- **Head-to-head:** 69/140 vs c2 (4/16 on the targeted maps, 65/124 noise elsewhere).
- **Ladder hedge:** 94/140 vs tb_merge_b, below c2's 98. The whole deficit is on the boss maps (5/16 vs c2's 9/16).
- **Consistency:** five implementations (v0-v4) all scored 2-5/16 on the boss maps against c2's 9/16 baseline. The negative result does not depend on one parameter choice.
- **The mechanism was confirmed and is net negative:**
  - earlier boss clears (r1184 vs r1804) and more of them (21 vs c2's 19);
  - but half the gold (4.0k vs 7.5k), contested captures, and dead carriers.
- **Keep from this experiment:** the measured targeting rule and the escape-field retreat (new hypotheses below). Do not ship the commit.

## New hypotheses generated
- **V3L-3b Boss kill-steal / contest, no commit.**
  - Camps don't heal, so watch the HP of visible bosses. When an enemy has chipped one below ~30%, or is fighting it, converge to finish it and contest the capture: capture needs uncontested occupancy.
  - Also hunt big-bag carriers: give an enemy carrying ≥ 100 gems team focus and a longer chase.
  - Evidence: Mein Kraft 00contest, where we got 400 gems from killing Varg twice. In our screens c2 profited from our chip damage: its median first boss clear on the 8 maps was r1359 against us, against its own r1804 versus tb_merge_b, and on 00contest B it came at r997 instead of r1322. It also killed our 200-gem carrier 11 rounds after the capture.
- **Escape-field retreat for every camp.**
  - c2's `retreat` breaks danger ties by spawn distance, which can lead into walled dead ends. Retreat along a BFS "distance out of range" field instead.
  - Evidence: bc-trace2 A, death at (14,29) after 9 hits. Camp deaths on the boss maps fell from 11.6 (v0) to 1.4 per game (v2) once the field was in.
  - Measure deaths_by_camp per game over all maps (c2: about 1.0).
- **Exact aggro rule in team clears.** A camp hits the Chebyshev-nearest champion (either team), ties to the lowest unit id (665/665 hits, 78/78 ties).
  - h_teamclear's TEAM_NEAR_DANGER screened worse without the exact rule and without an escape path.
  - Retest it on c3_teamclear with this rule plus the escape field. Non-targeted champions keep hitting instead of fleeing.
- **00contest-type maps are fight races.**
  - Where all gems sit in bosses and the rest is gold, the winners had Durability, Power and Jungle builds and won the area (kills 19-3).
  - Test a fight-first item and positioning plan near the boss region on boss-only maps (share 1.0) against a ladder imitation (Mein Kraft: Vesper, Tavi, Varg, Willow, C&I), not against c2.
- **Boss code must be fuel-flat.**
  - Precompute stand tiles per boss group, and read `vision.champions()` once per turn.
  - Evidence: 500 fuelExhausted per game on 00stampede from per-turn `goals × camps` loops.

## Reproduce
- **Census and metrics:** `matches/bc-tools/` (gitignored, like `matches/q26-tc/tools`). The numbers above are copied here.
  - `bosscensus.py matches/q26-census out.json`: boss groups and gem-rate share per map.
  - `bossmetrics.py bosscensus.json [--games] [--maps ..] DIR|files`: boss clears, first clear, captured boss gems, camp deaths near bosses. Ladder files are mapped through `results/ladder-games.jsonl`.
  - `econ.py [--maps ..] DIR...`: clears, gold and deaths per game.
  - `split.py`: boss maps vs other maps.
  - `targeting2.py team-a.stdout`: the nearest-champion inference.
  - `commit_time.py`: champion-rounds committed.
  - `getlog.sh DIR`: unzips the team stdout from a replay.
- **Traces:** `matches/bc-trace{1,2,3,4}/` with `run.sh`. Each `.repl26a` holds `team-a.stdout` with the BOSS / BD / BT lines.
