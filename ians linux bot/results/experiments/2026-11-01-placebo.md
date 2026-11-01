# Experiment: placebo (null-change) controls, calibrating the promotion gate's noise floor (2026-11-01, cluster)

Methodology experiment, not a candidate. It follows h_antistun's new hypothesis 1 ("noise-calibrated evaluation").

**Verdict in one line.** A change with no strategic effect does not score far from 70/140. The two placebos scored **66** and **68** (the mirror scores 70). The measured trajectory noise is **below** the binomial noise the Wilson bound assumes, so **keep the ≥ 82/140 gate**. The one real leak is the screen-then-gate selection (about 3% false passes for a screened null candidate). A cheap placebo replicate (rule R3 below) closes it.

## Hypothesis
- **What:** our bots read `fuel_remaining()`, so a change that only alters fuel use can still change decisions and re-roll game outcomes.
  - If such a null change can land far from 70/140, the gate (≥ 82/140, 95% Wilson lower bound > 50%) is noisier than its binomial assumption. Candidates could then pass on trajectory luck.
- **Source:**
  - Three batch-1 bots whose code differs from tb_merge_b mainly in fuel use did not reproduce their dev-PC records. These were h_goldtie (sprint 18-22 here vs 21-19 there), h_fightfuel (21-19 vs 22-18) and h_earlyfight_all.
  - h_antistun's logging-only control changed 100/140 games and flipped 44/140 outcomes against the tb_merge_b mirror. That report quoted "SD ≈ ±6.6 wins over 140", which is above the binomial 5.92.

## Setup
- **Placebo bots.** Both were made with `python3.12 tools/newbot.py q24_combo placebo_{a,b}`. Only `src/main.py` differs from q24_combo; `bot.py`, `draft.py` and `randomness.py` are byte-identical.
  - **placebo_a:** `cambc.round_number()` once at the start of every play turn, result discarded.
  - **placebo_b:** `_burn(100)`, a 100-iteration pure-Python summation loop at the start of every play turn, result discarded.
    - The task suggested "a few thousand iterations". At the measured ~700 fuel per iteration, that would cost 55-85% of the 2.5M turn budget, a real handicap rather than a placebo. 100 iterations was used instead.
- **Code check: decisions can depend on the change only through fuel.**
  - Neither placebo touches bot state.
  - The RNG (`randomness.py`) is seeded from spawn and start positions, not from time or fuel.
  - The only `id()`-keyed memos (`reach_memo`, `cross_cache`, `escape_cache`) key on the walk components in `self.comps`, which live all game. So memory layout cannot leak into decisions.
  - The `set`s hold plain values.
  - The fuel-dependent branches are:
    - `build_static_fields` (`while todo and fuel_remaining() > FUEL_BUILD_FLOOR`);
    - `FUEL_SCORE_FLOOR` (target scoring);
    - `FUEL_FIRST_TURN_MIN`;
    - `FUEL_RETREAT_DASH` and `FUEL_KIT_AIM`;
    - fuel-exhaustion suspensions.
- **Measured fuel overhead.** I decoded the replay `team-?.fuel` streams: a 13-byte header ("fuel26a" byte-reversed), 8 budget u64s, then one u64 per unit-turn. I compared each placebo with the mirror's same seat before the games diverge. Script: `matches/plc-tools/fuel_delta.py`.
  - **placebo_b:** about **69-77k fuel per turn** (about 3% of the budget). Its second play turn costs about 141-171k.
  - **placebo_a:** typically **+0.3k to +5k per turn** (about 0.1%). Some turns go down to −2k, because `build_static_fields` spends whatever is left above its floor, so the rest of the turn's fuel use shifts too.
  - First-draft-turn fuel differs by −0.4k (placebo_a) and +2.7k (placebo_b), because a different `main.py` costs a different amount to import. The draft picks were identical in all 140 games.
- **Runs.** All on the free Slurm `test` partition via `tools/onslurm.sh -c 24 -m 16G -t 00:20:00`, `eval.py ... --maps all --jobs 16 --keep`, cambc 4.0.0 / engine 2.0.0:

  | Job | Pairing | Tag | Role |
  |---|---|---|---|
  | 56813486 | q24_combo vs q24_combo | `plc2-mirror` | baseline mirror (the reference per map/side) |
  | 56813488 | placebo_a vs q24_combo | `plc2-a-all` | null change 1 |
  | 56813489 | placebo_b vs q24_combo | `plc2-b-all` | null change 2 |
  | 56813490 | placebo_a vs tb_merge_b | `plc2-a-tbm` | placebo re-run of the actual q24_combo promotion gate (`gate-q24-all`, 87/140) |
  | 56783427 | placebo_b vs tb_merge_b | `plc-b-vs-tbm` | the same, from the earlier attempt (see below) |

- **About the `plc-*` folders.** An earlier, interrupted attempt at this task (jobs 56780760-2, about 21:31 EDT on 31 Oct) left `matches/plc-mirror`, `plc-a-all`, `plc-b-all` and `plc-b-vs-tbm`, but no report.
  - I re-ran under fresh `plc2-*` tags, because placebo_a's `main.py` was last modified in the same minute those games were stamped.
  - **Every re-run is game-for-game identical to the earlier run:** 140/140 each for the mirror, placebo_a and placebo_b, so 420/420 games.
  - So the code was the same, and the engine is deterministic across jobs and nodes. On that basis `plc-b-vs-tbm` (job 56783427, run after placebo_b's last edit) is reused rather than re-run.
- **Analysis scripts** (in `matches/plc-tools/`, gitignored):
  - `compare.py`: per map/side identical or diverged, the first divergence round from events and per-round timelines, and outcome flips against a reference run.
  - `placebo.py`: mirror self-check, pooled flip rates, variance estimators.
  - `gate_null.py`: exact null distribution, screen-conditional.
  - `gate_rules.py`: game-level Monte Carlo of gate rules.
  - `fuel_delta.py`: fuel overhead.

## Results
Verbatim:
```
SUMMARY q24_combo vs q24_combo: 70W-70L (50%)  avg gems 685 vs 685  avg deaths 10.4 vs 10.4  botFaults(A) 0
SUMMARY placebo_a vs q24_combo: 66W-74L (47%)  avg gems 675 vs 694  avg deaths 10.6 vs 10.3  botFaults(A) 0
SUMMARY placebo_b vs q24_combo: 68W-72L (49%)  avg gems 675 vs 685  avg deaths 10.4 vs 10.0  botFaults(A) 0
SUMMARY placebo_a vs tb_merge_b: 85W-55L (61%)  avg gems 719 vs 584  avg deaths 9.4 vs 14.0  botFaults(A) 0
SUMMARY placebo_b vs tb_merge_b: 90W-50L (64%)  avg gems 717 vs 604  avg deaths 10.2 vs 13.2  botFaults(A) 0
```
For reference, the gate run (`gate-q24-all`): `SUMMARY q24_combo vs tb_merge_b: 87W-53L (62%)  avg gems 718 vs 586  avg deaths 9.4 vs 14.0  botFaults(A) 0`.

**Mirror self-check.** In the mirror, every map's A and B games are identical (70/70), so it scores exactly 70-70. Team A wins 33 of 70 maps. In this mirror the seat bias is small, unlike the ~75% team-B figure from older bots.

**Game-by-game comparison against the reference's same map and seat:**

| Run | Reference | W | A / B | Identical games | Diverged | Outcome flips (+/−) | Median first-divergence round | Sprint W (flips) | fuelExh/game (this bot) |
|---|---|---|---|---|---|---|---|---|---|
| plc2-mirror | — | 70 | 33 / 37 | 140 vs earlier `plc-mirror` | 0 | 0 | — | 20/40 | 7.2 |
| plc2-a-all | mirror | **66** | 30 / 36 | 126 | 14 (10 maps) | **4** (+0 / −4) | 53 | 19/40 (1) | 7.9 |
| plc2-b-all | mirror | **68** | 32 / 36 | 63 | 77 (46 maps) | **28** (+13 / −15) | 37 | 18/40 (10) | 7.0 |
| plc2-a-tbm | gate-q24-all (87) | **85** | 42 / 43 | 126 | 14 | 4 (+1 / −3) | 50 | 23/40 (1) | 7.8 |
| plc-b-vs-tbm | gate-q24-all (87) | **90** | 46 / 44 | 66 | 74 | 27 (+15 / −12) | 31 | 28/40 (10) | 8.9 |

The original gate run scored 24/40 on the sprint subset.

- **placebo_a vs placebo_b agreement:** against q24_combo, 63 identical games and 30 outcome disagreements. Against tb_merge_b, 66 identical and 27 disagreements.
- **Map scores** (placebo_b vs q24_combo; every mirror map is 1-1): 48 maps 1-1, 10 maps 2-0, 12 maps 0-2.
- **Flipped games:**
  - **placebo_a vs mirror:** 00vault B (r12), 01boss-battle A (r30), 01concentrated-wealth A (r658), 02stalactites A (r21). All four are losses; under a symmetric null that happens with probability 1/16 (two-sided 1/8), so it is not significant.
  - **placebo_b vs mirror:** 28 flips on 25 different maps, with no map family. Examples: 00lanes A+ / B− (both diverged at r2), 00split A+ / B− (r58), 01big-world A+ / B− (r11-12), 02harvest A− (r2), 01fracture A− (r2), 02tangle B+ (r535).

**Flip rate of a diverged game, by when it diverged** (placebo.py; both q24 runs pooled):

| First divergence | Games | Flipped |
|---|---|---|
| r0-50 | 52 | 19 (37%) |
| r51-200 | 19 | 7 (37%) |
| r201-500 | 12 | 4 (33%) |
| r501-1000 | 6 | 2 (33%) |
| r1001+ | 2 | 0 |

- **All four runs pooled:** 179 diverged games, **63 flipped (35.2%, 95% Wilson 28.6-42.4%)**.
- **By the reference game's final gem margin:**

  | Margin | Flipped |
  |---|---|
  | 0-99 | 14/38 (37%) |
  | 100-249 | 12/34 (35%) |
  | 250-499 | 20/47 (43%) |
  | ≥ 500 | 17/60 (28%) |

- **By game length:** games that ended early flipped 34%, games that went to r2000 flipped 38%.

**`match_metrics.py`** (candidate seat; mirror / placebo_a / placebo_b):

| Metric | Mirror | placebo_a | placebo_b |
|---|---|---|---|
| fuelExhausted | 7.2 | 7.9 | 7.0 |
| deaths_by_champion | 9.4 | 9.5 | 9.5 |
| deaths_by_camp | 1.0 | 1.0 | 1.0 |
| gemsLost_to_champion | 61.0 | 62.5 | 58.8 |
| gemsLost_to_camp | 6.3 | 7.0 | 4.9 |
| mean tribute | 24.3 | 24.2 | 24.4 |
| wards | 427.4 | 427.3 | 423.8 |

**`analyze_match.py --summary matches/plc2-b-all`** (68 wins vs 72 losses, wins / losses):
- **Opening tempo is the same:** first clear (us) 53.6 / 48.1; first tribute (us) 182.1 / 185.5.
- **Kills / deaths:** 12.6/5.3 vs 5.4/13.4.
- **Gem lead:** r250 +7 / −16, r500 +49 / −57, r1000 +123 / −122.

## Analysis session
### 1. Did the perturbation behave as a placebo?
- **Yes.** The overhead is fuel only, and the drafts are identical in 140/140 games.
- Aggregate play is unchanged within noise: deaths, tribute size, wards and consumables match the mirror to within about 4%.
- The perturbation reaches as far as its fuel cost:
  - placebo_a (about 0.1% of the budget) changed **14/140** games, on 10 maps (e.g. 00vault, 01boss-battle, 02stalactites, 01concentrated-wealth).
  - placebo_b (about 3%) changed **74-77/140** games, in both pairings.
- Divergence is usually early: median r31-53, often r2-r12. That is consistent with `build_static_fields` and the score floor changing what the first turns compute.

### 2. A diverged game is re-rolled, not nudged
- About **35%** of diverged games flip, whether the divergence happens at r2 or at r800 (table above). Even games the reference won by ≥ 500 gems flip 28% of the time.
- Example, 00lanes A, diverged at r2:
  - **mirror:** LOSS 883-1015, K/D 10/11, first kill (us/them) r164/r67;
  - **placebo_b:** WIN 1002-834, K/D 16/4, first kill r171/r297.
  - The fight sequence is entirely different, and the winner was not ahead until r1500 in either game.
- The win/loss summary shows why: the opening is identical in wins and losses, and games are decided by mid-game fights. K/D flips from 12.6/5.3 to 5.4/13.4, and the gem gap only opens after r250.
- Fights are where tiny timing differences compound.

### 3. The noise floor
- **Model.** For one bot pair, each game g has a win probability q_g over trajectory perturbations, and W = Σ X_g.
  - A null change has q_{m,A} + q_{m,B} = 1 per map, so **E[W] = 70**.
  - Var(W) = Σ q_g(1−q_g). That is **at most 35**, the binomial(140, ½) variance (SD 5.92) the Wilson bound assumes.
  - Two independent realizations of a game disagree with probability 2q(1−q). So, with outcomes independent across games, the flips on diverged games estimate Var.
- **Measured per-game variance of a re-rolled game:** v = 0.352/2 = **0.176** (range 0.143-0.212).
  - A real candidate changes decisions directly, so it re-rolls essentially every game. h_antistun's logging-only control already diverged 100/140.
  - **For such a run, SD(W) ≈ 4.96 (4.47-5.45), below the binomial 5.92.**
  - As actually run, placebo_b's SD is 3.74 and placebo_a's 1.41, because many of their games never diverge.
- **The observed null scores are 70, 66 and 68.** The largest deviation is 4 games, about 0.8 SD. None comes near +12.
- **The promoted candidate under re-perturbation scored 87, 85 and 90** (gate, placebo_a, placebo_b). The spread is 5 games, consistent with the SD above, and all three are ≥ 82.
  - The q24_combo promotion is therefore robust to trajectory noise.
  - But one of three realizations sat only 3 games above the line. A real candidate at q24_combo's level (+17) fails a single 140-game gate about 13% of the time (Monte Carlo below).
- **False-pass probability of gate (a) for a zero-effect candidate:**
  - **1.0% (0.5-1.7%)** using the measured v, against 2.6% under the binomial.
  - Candidates reach the gate through the ≥ 55% sprint screen, and the screen's 40 games are inside the 140. Conditional on passing the screen it is **3.0% (1.6-4.7%)**, against 6.6% binomial.
  - So the screen-then-gate pipeline, not the gate itself, is the part that exceeds the nominal 2.5% one-sided level.
- **The sprint screen is mostly noise.** A null change passes ≥ 22/40 **28.5%** of the time. placebo_b flipped 10/40 sprint outcomes in both pairings. The null sprint scores were 20, 19 and 18; the real +17 candidate's realizations scored 24, 23 and 28.
- **Reconciling h_antistun's "±6.6".**
  - That figure is √44 flips: the SD of the *difference between two 140-game realizations*, which is √(2·Var).
  - It is the right number for comparing two runs with each other: a candidate vs its control, or two candidates. Re-rolled pairs have SD(diff) ≈ 7.0.
  - It overstates the noise of one run against the fixed 82. From its own data (44 flips on 100 diverged games), the single-run SD for a fully re-rolled tb_merge_b run is about 5.5, still below 5.92.
  - q24_combo's diverged games flip a little less often than tb_merge_b's did (35% vs 44%). q24_combo also has far fewer fuel exhaustions (7 per game vs ~77). Whether that is the cause was not tested.

### 4. Batch-1 non-reproduction, explained
- Cluster runs are bit-identical across jobs and nodes: 420/420 games matched the earlier attempt's runs.
- A ~3% fuel change flips 10/40 sprint outcomes. So any bytecode difference between the dev-PC iteration and the committed code explains the 1-3 game sprint discrepancies of h_goldtie, h_fightfuel and h_earlyfight_all.
- No engine nondeterminism is needed. This supports the explanation in the h_goldtie report.

### 5. Side finding for gate (c)
- Across null changes, fuelExhausted moves from 7.0 to 7.9 per game (mirror 7.2).
- "Not worse than the champion's" needs a tolerance of about 1 per game, or it will fail null-equivalent candidates at random.

## Verdict
**Hypothesis rejected: the 82/140 gate is not noisier than the Wilson bound assumes.**
- A null change scores 66-70.
- The measured trajectory noise (SD ≈ 5.0 for a fully re-rolled run) is below the binomial 5.92.
- The false-pass rate for a zero-effect candidate is about 1%.
- **Residual risk:** about 3% for a candidate that reached the gate through the sprint screen, because the screen's games are reused, plus the multiplicity of gating many candidates over time.
- The promoted q24_combo is confirmed: its placebo re-runs scored 85 and 90 against tb_merge_b.

## Recommendation
**Keep the ≥ 82/140 threshold.** Add one cheap requirement, (a′):
- **The placebo replicate.**
  - Fork the candidate with `tools/newbot.py CAND CAND_plc`, and add placebo_b's `_burn(100)` line to its `main.py`, at the top of the play branch (the template is `bots/placebo_b/src/main.py`).
  - Run `tools/eval.py CAND_plc CHAMPION --maps all` on Slurm (about 5 min).
  - **The replicate must score ≥ 78/140.**

Monte Carlo of the rules (`gate_rules.py`). The model:
- per-game v = 0.18;
- the replicate re-draws 55% of games, as placebo_b did;
- the sprint screen is the first 40 games;
- 100k simulations;
- δ is the candidate's true advantage in games per 140.

Pass probabilities, unconditional (and conditional on having passed the ≥ 22/40 screen):

| Rule | δ = 0 (null) | δ = +6 | δ = +12 | δ = +17 (≈ q24_combo) |
|---|---|---|---|---|
| R0 current: W1 ≥ 82 | 1.04% (3.13%) | 13.5% | 54.1% | 87.3% |
| **R3: W1 ≥ 82 and replicate ≥ 78** | **0.38% (1.13%)** | 9.2% | 49.3% | 86.0% |
| R2: W1 ≥ 82 and W1+W2 ≥ 164 | 0.19% (0.58%) | 6.7% | 44.5% | 84.4% |
| R1: both ≥ 82 | 0.13% (0.38%) | 4.6% | 36.5% | 78.9% |
| R4: raise to W1 ≥ 85 | 0.16% (0.53%) | 4.5% | 30.6% | 69.7% |

- **R3 cuts the false-pass rate for a screened null candidate about 3×**, from 3.1% to 1.1%, back under the nominal 2.5%. It costs about 1 point of power on a +17 candidate and 5 on a +12. q24_combo would have passed it (85 and 90).
- **Raising the threshold (R4) is dominated.** R2 gives the same null control with far more power, and R4 would have put q24_combo's own placebo_a realization (85) on the line.
  - With the binomial v = 0.25 as a pessimistic check, R0 gives 2.7% (6.9% given the screen) and R3 gives 1.0% (2.7%). The ranking of the rules is the same.
- **Also:**
  - (i) Treat a 55% sprint screen as a coin flip that earns a gate run, never as evidence in a report.
  - (ii) When two 140-game runs are compared with each other (a candidate vs its control, or two candidates), differences under about 14 games (2 SD of a difference) are noise.
  - (iii) Give gate (c)'s fuelExhausted comparison a tolerance of about 1 per game.

## New hypotheses generated
1. **Replicated evaluation for small components (methodology; h_antistun 1b, now quantified).**
   - **Evidence:**
     - one 140-game run has SD ≈ 5 under re-rolling;
     - a single placebo replicate re-draws only 55% of games;
     - gains of +3 to +6 games (like h_goldtie's deterministic +4) are invisible in one run (pass rate 4.6-13.5%).
   - **Test:**
     - make 3-4 placebo variants with different burn sizes (e.g. 60, 100, 140 iterations), each re-drawing a different ~55% of games;
     - pool them for 420-560 games per comparison;
     - check the pairwise identical-game counts first, to confirm the variants are close to independent.
2. **Fuel-independent decisions (supporting evidence for h_goldtie's proposal to replace fuel floors with fixed work quotas).**
   - **Evidence:** a 0.1% fuel change diverged 10% of games, and a 3% change diverged 55%.
   - With fixed quotas, a patch would change only the games where its behaviour fires. Paired candidate-vs-control comparisons would then be exact on the rest, and dev-PC and cluster numbers would stop drifting.
   - It does not reduce the game-level chaos once behaviour differs.
3. **Leads are not safe: a lead-protection mode.**
   - **Evidence:** diverged games that the reference won by ≥ 500 gems still flipped 28% of the time, and in 00lanes neither game's winner led before r1500. Wins vs losses differ in mid-game K/D (12.6/5.3 vs 5.4/13.4), not in opening tempo.
   - **Proposal:** first check, in the flipped ≥ 500-margin games, when the eventual loser lost the lead. If late fights decide them, test a rule that stops taking even fights once ahead by ≥ X tributed gems after r1000, and banks or tributes instead.
