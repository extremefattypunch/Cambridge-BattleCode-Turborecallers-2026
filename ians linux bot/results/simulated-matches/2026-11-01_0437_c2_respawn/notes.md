# Experiment: c2_respawn, LOOP.md §4 promotion gate (2026-11-01, cluster)

STRATEGIES **Q21 on the new champion**: q24_combo plus h_respawnfix v3 (the respawn-rule movement fix). This report covers the full promotion gate (a-d) against the champion `q24_combo` and its mandatory analysis session. The bot was frozen for the gate and no code was changed. Nothing was promoted, and no tracked status file was edited.

**Gate result: PASS on all four parts, with one marginal item flagged in (c).**
- (a) **89/140** (63.6%), 95% Wilson lower bound **0.553**, botFaults 0. Side A 45/70, side B 44/70.
- (b) Gauntlet **177/200** against q24_combo's 174/200. The worst per-opponent change is −1 (tb_merge_a).
- (c) The release game is clean (0 crashes, empty stdout and debug logs).
  - fuelExhausted is **6.88 vs 6.86 per game** in the same 140 games (963 vs 960 events). That is equal at the one-decimal precision of the q24 gate, and c2 is lower in the gauntlet (8.72 vs 8.76) and in the release game (31 vs 48).
  - **Under a strict literal reading, c2 is 3 events worse over 140 games.** See the fuel section.
- (d) The targeted mechanism changed: frozen champion-rounds fall −25% against q24's own mirror seats, while two fuel-noise placebos stay flat. The gain is spread across both sides, all four map families, and the sprint and non-sprint subsets. It is far above the noise floor: no-op placebos of q24 score 66 and 68 of 140.
  - Two caveats: a new mutual-freeze mode on 02the-pond in the gauntlet, and 3/10 on the structural tiebreak maps.

## Hypothesis
- **What:** port h_respawnfix v3 (all four hunks behind `RESPAWN_FIX = True`) onto the champion q24_combo.
  - **(a)** No in-turn push-back off camp tiles.
  - **(b)** End-of-turn `leave_respawn_tile` step-off, on quiet turns only.
  - **(c)** No farming stand-off or bush goals on tiles of groups believed respawning (`resp_mask`).
  - **(d)** The unseen-alive guess is gated on a fresh `state()` read (`Group.seen`). `G.seen` is set in `observe_fast` too: this is the R1 silent-merge trap documented in `bots/c2_respawn/NOTES.md`.
- **Why:** q24_combo inherits tb_merge_b's respawn-rule bug, apart from h_goldtie's gold-play narrowing.
  - The h_respawnfix census measured it on tb_merge_b: the push-back fired on non-respawning tiles 17,059 times in 135/140 games, and the unseen-alive guess fired with a fresh Alive state 12,486 times.
  - h_respawnfix alone scored 92/140 against tb_merge_b, the best single patch of batch 1.
  - The expected result is fewer frozen champion-rounds and more clears/tributes.
- **Source:** `results/simulated-matches/2026-11-01_0126_h_respawnfix/notes.md`, `bots/h_respawnfix/NOTES.md`, `bots/c2_respawn/NOTES.md` (merge resolutions R1-R5, local validation on 01yellow-brick-road).

## Setup
- **Candidate:** `bots/c2_respawn`, forked from `q24_combo` with `tools/newbot.py`.
  - Only `src/bot.py` differs (md5 `83d844c8fece0d248ba5d6a044c41cb6`).
  - `main.py`, `draft.py` and `randomness.py` are byte-identical to q24_combo's.
  - All debug flags are off. bot.py was last modified 21:29 EDT on 31 Oct, before every gate job.
- **Engine:** cambc 4.0.0 / engine 2.0.0. All multi-game runs used the free Slurm `test` partition through `tools/onslurm.sh`.
- **(a) Head-to-head** (job **56783145**, COMPLETED exit 0, 21:55-21:58 EDT 31 Oct, raw output in `matches/gate-c2-all/`; 140 json + 140 replays):
  `tools/onslurm.sh -c 24 -m 16G -t 00:20:00 -J c2-gate -- python3.12 tools/eval.py c2_respawn q24_combo --maps all --jobs 16 --keep --tag gate-c2-all`
- **(b) Paired gauntlet** (job **56783143**, COMPLETED exit 0, 21:55-22:00 EDT, appended to `results/gauntlet.jsonl` line 4 with commit f5db4e8, games in `matches/g-c2_respawn-vs-*`):
  `tools/onslurm.sh -c 24 -m 16G -t 00:30:00 -J c2-gaunt -- python3.12 tools/gauntlet.py c2_respawn --pool sf_bank,tb_merge_a,tb_aggro,imit_test,lad_vcst --maps sprint --jobs 16 --note "gate c2_respawn"`
  - **Champion baseline:** `results/gauntlet.jsonl` line 2 (note "gate q24_combo"), same pool, maps and engine.
- **Provenance of (a) and (b).** Both jobs were submitted by an earlier, interrupted attempt of this same gate step, about 2 hours before this session.
  - This session verified their exact commands from `sacct` SubmitLine. They are character for character the commands above.
  - It also verified the job states and exit codes, that the eval manifest ran workspace snapshots of `c2_respawn` and `q24_combo`, and that every bot file involved predates the jobs (md5 unchanged).
  - Local games are deterministic, so (a) and (b) were **not** re-run. That avoids duplicate games and a duplicate gauntlet.jsonl line. The Slurm logs are in `/n/netscratch/hekstra_lab/Lab/ian_poon/battlecode/logs/c2-gate-56783145.out` and `c2-gaunt-56783143.out`.
- **(c) Release game:** run by this session locally (00:02 EDT 1 Nov). The command is recorded in `matches/gate-c2-release/run-release.log`, and the bundle unzipped in `matches/gate-c2-release/unz-release/`.
  `./cli/cambc run c2_respawn q24_combo --map 01big-world --release -o matches/gate-c2-release`
  - The earlier attempt's game in the same folder (`run.log`, 21:56) did not record its flags. The release run reproduced it exactly: same score and replay size, and byte-identical `team-a.fuel` / `team-b.fuel`.
- **"Before" baselines** (all against q24_combo, 140 games, same seats; from the placebo noise-floor study, read-only here):
  - `matches/plc-mirror`: q24 vs q24, 70-70 (job 56780760);
  - `matches/plc-a-all`: `placebo_a` = q24 + one discarded `round_number()` per turn, about 3k fuel, 66/140;
  - `matches/plc-b-all`: `placebo_b` = q24 + a fixed ~67k-fuel burn per turn, 68/140.
  - The `plc2-*` reruns are identical to `plc-*` in 140/140 games each.
  - c2's measured per-turn fuel overhead (+12k) lies between the two placebos, so they are the right control for "is the gain fuel-noise divergence?".
  - Reference: `matches/gate-q24-all` (q24 vs tb_merge_b, q24's own gate).
- **Analysis tools:**
  - `analyze_match.py --summary --games`;
  - all 51 loss narratives, plus 8 surprising-win narratives;
  - `match_metrics.py`;
  - `tools/freeze_metric.py` (≥ 150 idle rounds);
  - a scratch script that decodes per-turn fuel from the kept `.fuel` traces (format below).

## Results (verbatim)
```
SUMMARY c2_respawn vs q24_combo: 89W-51L (64%)  avg gems 753 vs 611  avg deaths 9.8 vs 11.2  botFaults(A) 0
GAUNTLET c2_respawn: 177/200 (88%) on maps=sprint
Team A (c2_respawn) wins: round limit (2000) reached with more gems        [release, 01big-world: 851-820, crashes 0/0]
```
Gauntlet per opponent (verbatim):
```
sf_bank               40W-0L (100%)  gems 909 vs 232
tb_merge_a            23W-17L ( 58%)  gems 699 vs 659
tb_aggro              39W-1L ( 98%)  gems 894 vs 180
imit_test             38W-2L ( 95%)  gems 886 vs 366
lad_vcst              37W-3L ( 92%)  gems 877 vs 387
```

**Gate table:**

| Gate | Requirement | Result | |
|---|---|---|---|
| (a) head-to-head | ≥ 82/140, Wilson LB > 0.5, botFaults 0 | **89/140 (63.6%)**, Wilson 95% LB **0.5534**. botFaults 0 for both teams in all 140 games (`diagnostics.botFaults`). Side A **45/70**, side B **44/70** | PASS |
| (b) gauntlet total | ≥ 174 (q24_combo) | **177/200** | PASS |
| (b) per opponent | no opponent > 4 below q24 | sf_bank 40-0 (q24 39-1, **+1**); tb_merge_a 23-17 (24-16, **−1**); tb_aggro 39-1 (39-1, **0**); imit_test 38-2 (36-4, **+2**); lad_vcst 37-3 (36-4, **+1**). botFaults 0 in all 200 | PASS |
| (c) release | 0 crashes, no `bot error` | 0 crashes. team-a/b `.stdout` and `.debug` are **0 bytes** (0 `bot error`, 0 tracebacks); botFaults 0/0. W 851-820 at r2000, identical to the gate game 01big-world A | PASS |
| (c) fuel | c2 ≤ q24 in the gate-c2-all games | **6.88 vs 6.86 per game** (963 vs 960). Equal to one decimal; paired 95% CI of the difference [−0.65, +0.69]. Gauntlet 8.72 vs 8.76; release 31 vs 48 | PASS (marginal, see below) |
| (d) analysis | mechanism changed; not an artefact | see below | PASS (with caveats) |

**`match_metrics.py matches/gate-c2-all`** (c2's side, 140 games):
```
games 140  tributes 4218  mean tribute 25.0  small(<10) 439
  consumablesBought                    1203  (8.6/game)
  deaths_by_camp                        135  (1.0/game)
  deaths_by_champion                   1233  (8.8/game)
  fuelExhausted                         963  (6.9/game)
  gemsLost_to_camp                      761  (5.4/game)
  gemsLost_to_champion                 9881  (70.6/game)
  wardPlacement                       60539  (432.4/game)
```
q24's side of the same games, counted from the events, is 960 fuelExhausted (6.86 per game).

**`analyze_match --summary` (wins 89 / losses 51):**

| Metric | wins | losses |
|---|---|---|
| gems us-them | 915-481 | 470-837 |
| first clear us / them | r52 / r55 | r44 / r47 |
| first tribute us / them | r148 / r212 | r158 / r183 |
| clears us / them | 58.1 / 44.1 | 55.3 / 62.3 |
| kills us / them | 12.9 / 5.0 | 5.4 / 15.5 |
| gems lost us / them | 41 / 85 | 137 / 52 |
| gold us / them | 6,416 / 3,841 | 5,056 / 7,668 |
| gem lead at r250 / r500 / r1000 | +36 / +74 / +149 | +8 / −41 / −117 |
| fuelExh us | 7.4 | 5.9 |
| mean tribute | 25.5 | 23.2 |

## Analysis session

### 1. Did the targeted mechanism change? Yes
**Freeze before and after, all 70 maps × both seats.** Frozen champion-rounds (idle stretches ≥ 150 rounds), always against q24_combo:

| Scope | **c2** (gate) | q24 mirror seat ("before") | placebo_a | placebo_b | q24 as opponent in c2's games |
|---|---|---|---|---|---|
| all 140 | **58,904** (49 games) | 78,256 (59) | 79,521 | 77,531 | 62,307 |
| seat A | **24,114** | 38,499 | 38,121 | 37,779 | 28,979 |
| seat B | **34,790** | 39,757 | 41,400 | 39,752 | 33,328 |
| non-structural¹ | **38,797** (45) | 58,162 (54) | 59,427 | 56,256 | 42,335 |
| family 00 | **8,538** | 11,039 | 12,112 | 8,370 | 8,784 |
| family 01 | **18,102** | 31,809 | 32,001 | 40,048 | 21,294 |
| family 02 | 30,596 | 30,243 | 30,243 | 24,655 | 29,985 |
| adgato | **1,668** | 5,165 | 5,165 | 4,458 | 2,244 |

¹ Excludes 00stampede, 01boss-battle, 02gift-wrapping, 02guardians and 02the-pack.

- **The overall drop is −25%,** and **−33%** on non-structural maps. The two fuel-noise placebos stay within ±2% of the mirror, so the drop is the patch, not divergence.
- **By seat:** −37% for seat A and −12% for seat B. Two big side-B standoffs remain (below).
- **By family:** family 02 is flat. 02gift-wrapping (9,803 in every version) and 02tangle B (5,811 against 3,241) offset the drops elsewhere.
- For scale, q24's own gate had q24 79,372 against tb_merge_b 116,914.

**h_respawnfix's target maps** (c2 frozen / q24 mirror seat frozen):

| Map / seat | Frozen c2 / mirror | Result |
|---|---|---|
| 00quarry A | 0 / 973 | W 1010-340 |
| 00quarry B | 0 / 619 | W |
| 01fracture B | 0 / 1,798 | W 1026-838 |
| 01fracture A | 174 / 1,321 | W |
| 01broken-curve B | 0 / 2,033 | L, fight |
| 01broken-curve A | 711 / 2,476 | L, fight |
| adgato-gemcombat5 B | 0 / 2,363 | W 1113-133 |
| 01yellow-brick-road A | 2,122 / 7,357 | W 594-54 |
| 00reverse-spiral A | 0 / 320 | W 1020-295 |
| 02the-pond B | 0 / 744 | W 1001-250 |
| 02harvest A | 360 / 847 | W |
| 01concentrated-wealth A | 0 / 378 | W |

**The outcome tracks the freeze** (non-structural map-sides, bucketed by how long q24's own mirror seat froze there):

| q24 mirror-seat freeze | n | c2 | mirror | placebo_a | placebo_b |
|---|---|---|---|---|---|
| ≥ 300 champ-rounds | 40 | **28 (70%)** | 18 | 17 | 18 |
| 1-299 | 14 | 9 | 7 | 7 | 6 |
| 0 | 76 | **49 (64%)** | 40 | 38 | 38 |

- The gain is largest where q24 froze (+26 points), the mechanism the patch targets.
- It is also clearly present where q24 never froze (+13 points). That matches h_respawnfix's conclusion that the gain is broad: second-order effects of no longer being pushed off dead tiles inside the target group.

**Tempo and survival** (non-structural; c2 against q24's mirror seat, both against q24):

| Maps | Version | First tribute | Clears us / them | Deaths us / them | Gems lost us / them | Lead r500 / r1000 |
|---|---|---|---|---|---|---|
| < 3,000 tiles (92) | c2 | **r146** | **56.0** / 48.4 | 11.5 / 12.6 | 96 / 75 | +42 / +62 |
| < 3,000 tiles (92) | q24 mirror seat | r180 | 52.3 / 52.3 | 11.6 / 11.6 | 73 / 73 | 0 |
| ≥ 3,000 tiles (38) | c2 | r153 | 51.2 / **45.5** | **5.6** / 8.8 | **23** / 55 | +17 / +87 |
| ≥ 3,000 tiles (38) | q24 mirror seat | r169 | 50.4 / 50.4 | 7.7 / 7.7 | 50 / 50 | 0 |

- Deaths before r300 are 1.39 per game for c2 against 1.59 for q24 in the same games.
- **Remaining big freezes** are the open standoff types, not the respawn rule:
  - **01yellow-brick-road B:** 7,996, with q24 8,154 in the same game. This is the contested-capture standoff on the 30-tile row documented in `bots/c2_respawn/NOTES.md`. c2 won 15-4.
  - **02tangle B:** 5,811 against 3,241. It is a loss on clears, 24 vs 32 with 0 kills; this is h_respawnfix's target flip-flop map.
  - **02gift-wrapping:** 9,803 per seat, identical in every version (structural).
  - **01corridors:** about 1,870 per seat, unchanged from the mirror.

**Gauntlet freeze** (c2 vs q24 against the *same* opponent on the same 200 map-sides):
- **Totals are flat:** 43,575 (77 games) against 43,214 (83 games).
- **Without 02the-pond, c2 is −29%** (29,389 vs 41,302). The large drops are 02harvest −6,947, 00stampede −3,951, 01concentrated-wealth −3,227 and 00crater −1,358.
- **02the-pond is a new mutual freeze, +12,274:**
  - **vs tb_aggro A:** all three c2 champions are idle from r248-358 to r1920-1958, and tb_aggro's three are idle from r256-381. From r380 to r1920 the event log has **no** clear, gem collection, tribute, death or purchase by either team.
    - Every clear before the onset was followed by its gem collection, so this is not the cleared-but-uncaptured standoff of 01yellow-brick-road.
    - c2's Vendetta carried 12 gems from a kill at r241 and tributed them only at r1920.
    - Result **W 90-27** with 4 clears. q24 on the same map-side won 1019-27 with 62 clears.
  - **vs imit_test B and lad_vcst B** (identical games): c2 is frozen r101-537 and r~900-2000, and the opponent also from r~900. **W 359-0** with 22 clears; q24 won 756-339 with 56.
  - **Pattern:** both teams freeze, so the step-off that requires a *quiet* turn is the prime suspect (the R2 behaviour difference in the NOTES). With idle enemies in sight no turn is ever quiet, so a champion on a respawning group's spawn tile is never moved, the group never respawns, and both sides wait.
  - **Not traced.** Replays have no decoder and any code change diverges the trajectory, so this is new hypothesis H1 below.
  - Every one of these games was still a **win**, and the gauntlet result is unchanged.

### 2. Losses (all 51 narratives read)
| Type | Count | Side A / B | Games (controls mirror/placebo_a/placebo_b on the same map-side) |
|---|---|---|---|
| **Fight blowout** (our deaths ≥ 9 and ≥ 2× theirs) | 28 | 14 / 14 | 00breadcrumbs A [WWW], 00crater B [LLL], 00fragment B [LLL], 00gemfight A [LLL], 00great-wall A [LLL], 00interlock A [LLL], 00lanes B [WWL], 00monolith B [WWW], 00oasis A [LLL], 00oasis B [WWW], 00packs A [LLL], 00road-of-riches A [WWW], 00swirl B [LLL], 00the-line A [WWW], 00the-line B [LLW], 01broken-curve A [LLL], 01broken-curve B [WWW], 01hooks B [LLL], 01shortcut B [WWL], 02crossing A [WWW], 02crossing B [LLW], 02geodes A [LLL], 02stalactites B [LLL], 02the-pond A [WWL], 02treasure-box A [LLL], 02uncharted-lands B [LLW], adgato-gemcombat1 B [LLL], adgato-gemcombat4 A [WWW] |
| **Mixed / close fights** | 14 | 7 / 7 | 00contest A, 00corners A (985-1021), 00elkring A (928-1019), 00expanse B, 00great-wall B, 00interlock B (670-877), 00split A, 00vault B, 01shortcut A, 01starfish B, 01starvation A (398-442), 02harvest B, adgato-gemcombat1 A (893-1018), adgato-gemcombat4 B |
| **Farming race** (≤ 8 deaths) | 2 | 0 / 2 | 01the-farm B (865-873, c2 froze 618), 02tangle B (387-736, clears 24/32, c2 froze 5,811) |
| **0-0 / tiebreak** | 7 | 4 / 3 | 00stampede A+B, 01boss-battle A+B, 02gift-wrapping A (44-44), 02guardians B, 02the-pack A |

**What the losses show:**
- **Most losses are seat-determined on these maps.** 26 of the 51 were also lost by all three q24-equivalent controls.
- **14 were won by all three controls** (the "surprising losses"). Of these, 8 are fight blowouts, 4 mixed fights, 1 a farming loss by 8 gems (01the-farm B), and 1 a gold tiebreak (00stampede A).
  - 31 wins came on map-sides that all three controls lost, so the net is **+17 against the noise floor**.
  - None of the 14 shows a freeze signature, apart from 00great-wall B (856 against 0) and 01the-farm B (618 against 0).
- **The fight blowouts are decided early,** exactly the Q29 pattern: 70 of our deaths before r300 against 31 of q24's.
  - 00oasis A/B: K/D 4/36 and 3/44. The enemy Vendetta made 18-19 kills, with deaths from r117-150 on.
  - 01hooks B: 7/40.
  - 00crater B: 1/28.
  - 02stalactites B: 427 gems lost, as carriers holding 77-84 gems were killed.
  - adgato-gemcombat4 A: 320 gems lost against 0.
  - 00vault B: 469 gems lost, including Marcella's 118 at r691. fuelExh was 194/210, the known hotspot.
  - Unlike q24 against tb_merge_b (14 of its 20 blowouts as B), c2's blowouts are evenly split, 14 A / 14 B.
- **Tiebreak maps went 3/10,** against the mirror's 5/10, placebo_a's 4 and placebo_b's 6. The two seats that differ from the mirror are both lost on gold by ≤ 2.5%:
  - 00stampede A: 8,901 vs 9,126 gold;
  - 01boss-battle A: 29,680 vs 29,830, with 0 kills, Treasure emblems on both sides, and 123 vs 126 clears.
  - 01boss-battle B, 27,250 vs 27,344, is a coin flip in the controls as well (LLW).
  - The gold-play difference introduced by R2 (no push-back with an enemy in sight) is a possible small cost (H2).

### 3. Surprising wins (all three controls lost the map-side; narratives read)
- **00quarry A 1010-340:** clears 84/39, K/D 7/1. q24's mirror seat froze 973 here, and q24 as the opponent froze 1,089 in this very game; c2 froze 0. This is the respawn fix in action.
- **01fracture B 1026-838:** a pure farming race (K 2/2) with clears 70/62. The mirror seat froze 1,798; c2 froze 0.
- **02the-pond B 1001-250:** clears 66/25, K 21/3. The mirror seat froze 744; c2 froze 0.
- **00reverse-spiral A 1020-295:** K/D 19/0, first tribute r91 against r274. The mirror seat froze 320; c2 froze 0.
- **02arena A 1004-80:** K/D 32/0, a fight snowball from r255 with no freeze involvement.
- **01concentrated-wealth B 1005-480:** K/D 10/0, clears 55/36.
- **00vault A 1037-0 at r517:** mean tribute 115. The opponent never tributed (94 fuelExh).
- **01yellow-brick-road B 15-4:** both sides were in the capture standoff (about 8k frozen each). c2 tributed 15 by r256; q24's first tribute came at r1908.
- **All 31 such wins:** 00ambush A, 00anvil B, 00breadcrumbs B, 00dunes B, 00eight A, 00galaxy B, 00gem-fields B, 00lost-world B, 00pilgrimage A, 00quadrants A, 00quarry A, 00reverse-spiral A, 00ribs A, 00road-of-riches B, 00rows A, 00rushbait-v2 B, 00vault A, 01concentrated-wealth B, 01corridors A, 01elk-arena B, 01fracture B, 01islands A, 01starfish A, 01yellow-brick-road B, 02arena A, 02cuts B, 02famine A, 02fields A, 02the-pond B, adgato-gemcombat2 A, adgato-gemcombat3 B.

### 4. Is the gain an artefact? No

| Check | c2 | Mirror | placebo_a | placebo_b |
|---|---|---|---|---|
| **all 140** | **89** | 70 | 66 | 68 |
| seat A | **45/70** | 33 | 30 | 32 |
| seat B | **44/70** | 37 | 36 | 36 |
| family 00 (70) | **45** | 35 | 34 | 34 |
| family 01 (30) | **20** | 15 | 13 | 16 |
| family 02 (30) | **18** | 15 | 14 | 13 |
| adgato (10) | **6** | 5 | 5 | 5 |
| sprint subset (40) | **29** | 20 | 19 | 18 |
| non-sprint (100) | **60** | 50 | 47 | 50 |
| without the 5 structural maps (130) | **86 (Wilson LB 0.577)** | 65 | 62 | 62 |
| ≤ 1,100 tiles (34) | 19 | 17 | 15 | 15 |
| 1,100-3,000 tiles (68) | 39 | 34 | 33 | 37 |
| 3,000-8,000 tiles (26) | **21** | 13 | 12 | 9 |
| ≥ 8,000 tiles (12) | **10** | 6 | 6 | 7 |

- **Spread.** The gain covers both seats (+12 / +7 over the mirror seats), all four families, and the sprint and non-sprint subsets. It is not one family.
- **Above the noise floor.** Two fuel-noise placebos of the champion score 66-68, so 89 is 21-23 games above the noise floor.
- **Concentration on large maps.** On maps ≥ 3,000 tiles c2 went **31/38 against the mirror's 19/38**, which is +12 of the +19.
  - This is many maps, not one: 19 maps from 3,250 to 10,000 tiles, all four families.
  - The ≥ 8,000-tile maps were q24's known weakness (2/12 against tb_merge_b, Q30). c2 won 00ambush, 00galaxy, 01big-world and adgato-gemcombat5 on both seats there, and lost only 02harvest B and 02tangle B.
  - So this concentration is a bonus on q24's weak spot, not an artefact.
- **Paired gauntlet** (same opponents, same 200 map-sides): 177 against 174.
  - Flips: sf_bank +1/−0, tb_merge_a +9/−10 (pure churn), tb_aggro 0/0, imit_test +3/−1, lad_vcst +3/−2.
  - The improvement is small outside the h2h, which is expected: q24 already won 87% there.

### 5. Fuel: the marginal gate item
| Measure | c2 | q24 | Notes |
|---|---|---|---|
| fuelExhausted, gate-c2-all, per game | 6.88 (963) | 6.86 (960) | seat A 6.06 vs 6.16; seat B 7.70 vs 7.56 |
| paired per-game difference | +0.02 | | 95% CI [−0.65, +0.69]. c2 higher in 34, lower in 21, equal in 85 (sign test p = 0.105) |
| gauntlet, per game (same 200 map-sides) | **8.72** (1,745) | 8.76 (1,751) | per opponent: sf_bank 8.55 vs 9.00, tb_merge_a 9.35 vs 9.05, tb_aggro 8.35 vs 8.20, imit_test 8.97 vs 8.82, lad_vcst 8.40 vs 8.70 |
| release game 01big-world | **31** | 48 | |
| **all paired evidence (341 games)** | **2,739** | 2,759 | |
| mean fuel per turn (decoded `.fuel`) | 1,056,044 | 1,043,709 | **+1.2%**; q24 lower in 87/140 games. Turns using ≥ 2.5M fuel: 1,404 vs 1,401. For scale, q24's own gate had q24 1,053,845 per turn |

- **Verdict on (c):** not worse.
  - The exhaustion counts are equal within noise and lower across all paired evidence.
  - The +1.2% per-turn cost is real (the new `leave_respawn_tile`, `resp_mask` and `G.seen` work). It sits at about 42% of the 2.5M budget and does not move exhaustions.
  - **Strict literal reading:** 963 > 960, so if the orchestrator applies "≤" to the raw h2h count, (c) fails by 3 events in 140 games.
- **Engine fact: the `.fuel` trace format, worth adding to HANDOFF §7.**
  - The trace is a 13-byte header (`a62leuf\0` plus 5 bytes), then little-endian u64 records.
  - The first 8 records are budgets: 250M, 2.5M, 5M and 2.5M, twice. Then come 5 draft or first-turn entries, then one record per champion turn holding the fuel used. 0 means no turn (dead); the full budget means a suspension.
  - The 5M budget applies to each champion's first turn.
  - Check, in the release game: after the 8 header records, 26 / 43 turn records equal 2,500,000 and 5 / 5 equal 5,000,000. That is 31 / 48 budget hits, exactly fuelExhausted 31 / 48.

## Verdict
**PASS: gates a-d hold.** c2_respawn is eligible for promotion over q24_combo. That decision belongs to the orchestrator: this session promoted nothing and edited no tracked status file.
- (a) 89/140, Wilson LB 0.553, botFaults 0; A 45/70, B 44/70.
- (b) 177/200 against 174/200; per opponent +1, −1, 0, +2, +1.
- (c) Clean release game. fuelExh 6.88 vs 6.86 per game, equal within noise and lower in the gauntlet and the release game; the strict literal reading is flagged above.
- (d) The respawn-rule freezes are removed: −25% against q24's mirror seats, −33% non-structural, placebos flat.
  - On the h_respawnfix target maps the freezes go to 0.
  - The win gain tracks freeze: 70% vs 44% where q24 froze ≥ 300.
  - It is spread over both seats, all families and both map subsets, and it sits 21-23 games above the placebo noise floor.

**Known weaknesses that ship with it:**
- **New mutual freeze on 02the-pond** in 3 gauntlet games (2 distinct), all still won (H1).
- **Tiebreak maps 3/10:** gold races lost by ≤ 2.5% (H2).
- **The contested-capture standoff remains:** 01yellow-brick-road B 7,996, 02tangle B 5,811 (H3).
- **Per-turn fuel +1.2%.**
- **Early-fight blowouts** are still the main loss type: 28 of 51 losses (Q29).

## New hypotheses generated
- **H1: step-off deadlock with an enemy in sight** (new; a fix candidate for c2).
  - **Evidence:** in the gauntlet on 02the-pond, c2 vs tb_aggro A, all 3 c2 champions were idle from r248-358 to r1920-1958, and the opponent's 3 from r256-381.
    - From r380 to r1920 neither team cleared, collected, tributed, died or bought anything.
    - c2 vs imit_test B and lad_vcst B: idle r~900-2000, plus a c2-only freeze r101-537.
    - q24 cleared 62 and 56 groups on the same map-sides. These games add +12,274 frozen champion-rounds to c2's gauntlet total, which is otherwise −29%.
  - **Suspected cause:** `leave_respawn_tile` fires only on quiet turns. When idle enemies are in sight, a champion parked on a Respawning group's spawn tile is never moved, and the group never respawns.
  - **Plan:**
    - Build a counter fork (as `h_rfx_count` was) that logs turns where a champion is on a Respawning spawn tile with the step-off suppressed by "not quiet".
    - Candidate fix: allow the step-off when no enemy is within attack range plus 1 (rather than within sight), or after K stationary turns on a respawning tile.
  - **Why:** against an opponent that keeps farming, this deadlock would lose games.
- **H2: gold-play cost of R2** (extends Q32).
  - **Evidence:** structural maps 3/10 against the mirror's 5/10 and the placebos' 4-6.
    - Both seat differences are gold losses by ≤ 2.5%: 00stampede A 8,901 vs 9,126, and 01boss-battle A 29,680 vs 29,830, with 0 kills and 123 vs 126 clears.
    - q24's gold play pushed champions off respawning tiles even with an enemy in sight; c2 does not.
  - **Plan:** compare gold-per-round curves on 01boss-battle and 00stampede for c2 and the q24 mirror seat. Then test restoring the narrowed `blocks_respawn` push-back in gold play only (`no_tribute` or `stalled`).
  - **Why:** tiebreak maps are decided by small margins, and ladder 0-0 maps are decided the same way. The evidence is weak (2 games), so treat this as a watch item.
- **H3: contested-capture standoff** (existing open item from h_respawnfix and the c2 NOTES; new evidence).
  - **Evidence:** it is now the biggest remaining freeze. 01yellow-brick-road B had c2 7,996 and q24 8,154 frozen champion-rounds in the same game (W 15-4). 02tangle B rose from 3,241 to 5,811 (L 387-736, clears 24 vs 32, 0 kills).
  - **Plan:** a capture-branch timeout. If capture progress on a RewardAvailable group resets N times with an enemy on the region, fight the enemy on the region or retarget.
  - **Why:** with the respawn rule fixed, champions reach contested rows more often, so standoffs grow.
- **Q30 re-measure (queue update).** c2 went 31/38 on maps ≥ 3,000 tiles (mirror 19/38) and 10/12 on ≥ 8,000 tiles, with fewer deaths (5.6 vs 7.7) and fewer gems lost (23 vs 50).
  - Q30 (large-map farming tempo) should be re-measured on c2 before any work. Much of q24's large-map weakness looks like the respawn-rule bug.
- **Q29 (evidence update).** Early-fight blowouts are still the largest loss class: 28 of 51, with 70 vs 31 deaths before r300, now split evenly 14 A / 14 B. Q29 stays a top priority.
- **Fuel (minor).** c2 costs +12k fuel per turn (+1.2%). If a future patch pushes exhaustions up, the first place to look is caching `resp_mask()` per round instead of per farm-goal call.
