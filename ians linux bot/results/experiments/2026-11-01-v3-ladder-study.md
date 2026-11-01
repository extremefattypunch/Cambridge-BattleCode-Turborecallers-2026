# Ladder study: is v3 (q24_combo) worse than v2 (tb_merge_b)? (2026-11-01, cluster)

Decision memo for workflow `battlecode-v3-ladder-study`. It merges three independent analyses of the same ladder data:
- **Statistics**: rating model, rating-controlled comparisons, subgroups.
- **Mechanisms**: did each q24 patch work on real games, and what decided the losses.
- **Skeptic**: what the comparison really rests on.

The synthesis pass also checked the key facts again (see "Checked in this pass"). No game was simulated for this memo, no repo file was edited apart from this report, and no account action was taken.

**Verdict: KEEP v3 LIVE.**
- The data does not show v3 to be worse than v2. Most whole-sample estimates lean 40-100 Elo against v3, but no rating-controlled comparison is significant, and against matched opposition the two versions are indistinguishable.
- No q24 patch is implicated by the data, so there is no "fixed v3" to build.
- A rollback would change the team account and would itself fail the standing "certain to outperform" rule.
- **Confidence: medium.**

## Hypothesis
- **What:** v3 (`bots/q24_combo`, live from 01:42:13 UTC) plays worse on the real ladder than v2 (`bots/tb_merge_b`, live 21:53-01:42 UTC), even though the local gate went the other way (87/140 against tb_merge_b, gauntlet 174 vs 158; `2026-11-01-q24_combo.md`). If so, which of the four q24 patches is responsible?
  1. Lock-memory fix.
  2. Gold-tiebreak play.
  3. The all-game group-balance fight rule.
  4. Fuel caching.
- **Source:** STATUS tick at 04:10 UTC: "v3 is 24W-26L (48%), rating 1,526, flat … v2's comparable recent window was 21-9 (70%)".

## Data
- **Ladder log.** `results/ladder-games.jsonl` has 250 rows up to the 04:04 set. Engine statistics for every v2 and v3 game are in `matches/ladder/summary/`; the mechanisms analysis fetched the 58 missing v2 summaries read-only.
- **Version split, corrected.** Analysis copies are `matches/mb-ladder-v2` (110 games) and `matches/mb-ladder-v3` (75 games).
- **Rating fields.** `opp_rating` is the opponent's rating at pull time. `our_rating_after` is our rating at pull time, which is stale for every row except the newest set.
- **Two sets after the analyses**, not in the log (read-only `cambc matches list` at 04:28 UTC):
  - 04:10 vs **Mein Kraft**: **0/5**, side a. Losses on 00gem_fields, 00contest, 00galaxy, 02treasure_box and 00rows. Their draft was Vesper, Tavi, Varg, Willow, Cassi&Issac.
  - 04:20 vs **Velvet Pathfinders**: **4/5**, side b.
    - 02crossing: L.
    - 00breadcrumbs and 00ribs: W, on tiebreak_gems.
    - 01starfish and 00great_wall: W.
    - Their draft was Varg, Stellar, Cassi&Issac, Tavi, Ren.
- **Live ladder at 04:28 UTC** (read-only `cambc ladder`): Turbo Recallers **1519.8, rank 385 of 815**. Mein Kraft is 1532.5 and Velvet Pathfinders 1499.9.

## Key numbers (verbatim from the analyses unless marked)

### 1. The comparison was mislabelled (all three analyses, found independently)
**25 rows logged `v=2` were played by v3.** They are the five sets created 01:40:08, 01:50:08, 02:00:14, 02:10:07 and 02:20:08 UTC:

| Set (created) | Opponent | Result |
|---|---|---|
| 01:40:08 | final_final_v3_really_final | 3-2 |
| 01:50:08 | Us V Them | 1-4 |
| 02:00:14 | John Doe | 1-4 |
| 02:10:07 | Sneaky Wardens | 5-0 |
| 02:20:08 | Spawn Campers | 3-2 |
| **Total** | | **13W-12L** |

**Evidence that these sets were v3:**
- **Timestamps.** v2's `statusAt` (deactivation) is **2026-11-01T01:42:13.317Z**. All four sets created from 01:50 onward fall after it. The 01:40 set *finished* at 01:42:23-01:42:26, after it as well.
- **Fuel fingerprint** (our team's `fuelExhausted` events per game):

| Group | Games | Median | Mean | Games at ≤ 1 | Source |
|---|---|---|---|---|---|
| True v2 | 52 with stats | 24.5 | 95.0 | 7/52 | Statistics |
| True v2 | 110 | 13 | 109.7 | 16/110 (50/110 at ≥ 20) | Mechanisms |
| The 25 mislabelled games | 25 | 0 | 3.7 | 23/25 | Skeptic |
| Logged v3 | 50 | 0 | 3.1 | 37/50 | |
| 01:40 set alone | 5 | | | [0,1,0,0,0] | P about 4e-5 to 6e-5 under v2's rate |

- **Not an engine change.** Opponents in those sets still exhausted fuel (mean 161; the John Doe set had 309, 329 and 1679). The engine hash `85aa7167b4` is identical in all 127 summaries checked.

**Cause.** `tools/ladder_pull.py` assigns `v` once, when it writes a row. These rows were written before `results/ladder-versions.json` had a `"3"` entry, and the puller never relabels old rows.

**Corrected records** (checked in this pass by recounting `ladder-games.jsonl`):

| | As logged | Corrected |
|---|---|---|
| v2 (tb_merge_b) | 87W-48L (135) | **74W-36L (67.3%, 110 games, 22 sets, opponents avg 1479, range 1402-1525)** |
| v3 (q24_combo), to 04:04 | 24W-26L (50) | **37W-38L (49.3%, 75 games, 15 sets, opponents avg 1534, range 1507-1574)** |
| v3, with the 04:10 and 04:20 sets | - | **41W-44L (48.2%, 85 games, 17 sets)** (this pass) |

### 2. "21-9" was v2's hottest window
v2 had three phases (Skeptic):

| Phase | Sets | Record | Opponents avg | Performance |
|---|---|---|---|---|
| Climb | 9 | 36-9 | 1449 | 1691 |
| Plateau, 23:22-00:54 UTC (rating flat at 1491-1502) | 10 | 26-24 | 1499 | 1513 |
| Burst, 01:02-01:28 UTC | 3 | 12-3 | | 1740 |

The quoted "21-9" is the end of the plateau plus the burst: v2's last 30 games, 00:33-01:28. Against opponents rated 1485 or lower, v2 went 39-11; v3 has never met that band.

### 3. Rating model and trajectory
**The site rating is exactly Elo with K=32 per 5-game set (score = wins/5, so 6.4 points per game).**
- **Checks.** It matches all 25 exact-rating sets within ±1 point. Reconstructed ratings match the later pull snapshots within 2.3 points: 1497/1499.3, 1501/1502.5, 1530/1530.8, 1529/1530.1, 1526/1526.3 (Statistics).
- **v2's path:** 1407 at 21:53, 1493 by 23:14, flat at 1491-1502 from 23:22 to 00:54, and 1530 after the 01:28 set.
- **v3's path:** 1532 at 01:42, 1513 at 02:02 after two 1-4 sets, a peak of 1557 at 02:42, 1533 at 03:21 after AI Coliseum 0-5, and 1526 at 04:04. Then **1510.3** after Mein Kraft 0-5 and **1519.8** after Velvet Pathfinders 4-1 (this pass).
- **What follows.** v3 has held the rating v2 handed over, to within about 10 points over 17 sets. A bot of v2's full-sample strength (performance 1605) starting at 1530 "would be expected near 1570 after 16 sets". The 1510 low was "about 1.8 SD" below that (Skeptic).

### 4. Rating-controlled comparisons
Expected score per game is 1/(1+10^((R_opp − R_us)/400)). Standard errors are clustered by set, and intervals come from a set-level bootstrap.

**S-E against our own rating** (Statistics: corrected labels, `our_rating_after` against `opp_rating`):

| Window | n | S-E |
|---|---|---|
| v2, all | 110 | +0.162 ± 0.038 |
| v2, our rating ≥ 1480 | 80 | +0.116 ± 0.041 |
| v3 | 75 | +0.002 ± 0.073 |

- v3 − v2 (≥ 1480): **−0.115, 95% [−0.272, +0.044], p 0.16**. As a logit, −82 ± 57 Elo.
- v3 − v2 (all): **−0.161, 95% [−0.315, +0.001], p 0.04-0.05**. This is the only nominally significant cut, and it is biased, as explained below.
- Mechanisms gets the same picture: v2 74 wins against 56.2 expected; v3 37 against 36.9 expected.
- **Why S-E misleads here.** S-E against our own rating measures *rating lag*, not strength. v2 inherited v1's depressed 1407 and was climbing for most of its life, while v3 inherited a converged 1530. Any bot that merely holds its rating scores 0 on this measure.

**Strength against opponent ratings only, θ** (the bias-free measure):

| Source | Comparison | v2 | v3 | Difference [95%] | p or P |
|---|---|---|---|---|---|
| Statistics | v2 all | 1605 ± 29 | 1530 ± 51 | −75 [−189, +37] | p 0.18 |
| Statistics | v2 at ≥ 1480 | 1584 ± 32 | 1530 ± 51 | **−54 [−166, +65]** | **p 0.36** |
| Statistics | v2 with pre-set rating ≥ 1480 | 1567 ± 28 | 1530 ± 51 | −38 [−153, +73] | p 0.48 |
| Skeptic, Elo-offset logistic | 75 games | - | - | −75 ± 57 | z −1.31, p 0.19 |
| Skeptic, Elo-offset logistic | 80 games (with 04:10) | - | - | −96 ± 59 | z −1.64, p 0.10 |
| Skeptic, matched band (opponents 1486-1534) | | 35-25, perf 1559 | 27-23, perf 1553 | **+9 [−139, +132]** | P(v3 ≥ v2) 0.45 |
| Skeptic, v2 after its climb (23:22-01:28) | 38-27 vs 1499 avg | 1558 | | +31 [−88, +144] | P(v3 ≥ v2) 0.30 |
| Mechanisms, OLS on win (free slope) | | - | - | v3 **+0.05 ± 0.10** | opponent rating −0.21 ± 0.07 per +50 |

- **This pass (85 games):** v3 θ is **1520** (game-level SE 38), against v2's 1584 (≥ 1480) and 1605 (all). That is −64 and −85 Elo, still under 2 SE. The quick recomputation used logged-style opponent ratings; it reproduced the Statistics values of 1605, 1584 and 1530 exactly.
- **The OLS number is model-dependent.** Its free opponent slope comes out at 3.8× Elo's, driven by v2's convergence climb. Fixing the slope at Elo's flips the sign to −75 (Skeptic's fragility check). The honest reading is the Elo-slope family: **v3 leans 40-100 Elo weaker on whole samples and about 0 against matched opposition, and nothing is significant.**
- **Controls that change nothing.** Map, side and team-size mix each move the estimate by 4 Elo or less (Skeptic).

### 5. The one v3-specific signals (all marginal)
- **Lopsided sets.** v3 now has **5 of 17 sets with ≤ 1 win**: AI Coliseum 0-5, Mein Kraft 0-5, Us V Them 1-4, John Doe 1-4 and Warwick Wuants 1-4. v2 had **0 of 22**.
  - Variance of wins per set: v3 2.12-2.36 against v2 0.78-0.91. One-sided permutation p 0.03.
  - v3's design effect of 1.7-1.9 means its 75 games carry the information of about 40-44.
- **01xx maps** (Statistics): v3 8/21 against v2 13/17. Δ S-E −0.37 ± 0.14, **p 0.006 uncorrected**, which is borderline once about 13 subgroups are corrected for.
- **4-pick maps:** v3 6/14 against v2 13/17, p 0.04. They overlap the 01xx maps:
  - **01shortcut** went 0-3 for v3 (378-773, 476-531, 714-1015) and 3-1 for v2.
  - The same map, side and opponent: Spawn Campers on side a, which v2 won 1168-441 and v3 lost 714-1015.
- **Same-map pairs.** On the 39 maps both versions played, v3 was better on 14 and worse on 25 (sign test p 0.108).
- **Not reproduced in self-play** (this pass, from `matches/gate-q24-all`):

| Subset | q24 vs tb_merge_b, local gate |
|---|---|
| 01xx maps | 19/30 (63%) |
| 00xx maps | 39/70 |
| 02xx maps | 24/30 |
| 3-pick | 19/24 |
| 4-pick | 20/32 (63%) |
| 5-pick | 48/84 |
| 01shortcut | 1/2 |
| 00interlock | 2/2 |
| 01hooks | 1/2 |
| 00reverse-spiral | 1/2 |

  If these ladder signals are real, they depend on the opponent, which fits "every local opponent shares our logic".

## Mechanism check on the ladder (Mechanisms)
All comparisons below are v2 against v3, rating-controlled where stated.

### (1) Group-balance rule (all game): unresolved, and it does not explain the record by itself
- **Deaths and kills.** v3 dies more: deaths **+3.4 ± 2.3** and K-D **−6.0 ± 3.3** per game, mostly after r1000 (−3.3 ± 1.6). Raw deaths in losses were 12.6 against 18.3.
- **One opponent accounts for it.** All of the excess comes from **Us V Them**: 10 games, 3-7, **292 champion deaths, 29 per game**. Their Stellar and Ren carried 13-33 Power Focus emblems; on 00packs (0-1020) Stellar had 28 kills and 22 of our 45 deaths were within 8 tiles of our spawn.
  - Without Us V Them, the death excess is **+0.2 ± 2.0** and the win effect is +0.09 ± 0.11.
  - v2 never met this opponent.
- **Outnumbered deaths fell slightly, as the rule intends.** Enemies involved per death: 3.01 against 2.79. Deaths with 3 or more enemies: 64% against 56%. Solo deaths after r1000 rose: 13% against 21%.
- **Tempo:** no cost found.
  - Gem lead: r250 +3.9 ± 21.7; r1000 +6.4 ± 66.8.
  - Clears per 100 rounds: OLS 0.00 ± 0.48.
- **Code fact.** `enemy_dps = strength + 0.15 × focus` in both `group_balance` and v2's threat model. A 25-emblem Power Focus Stellar (about 2,700 burst at r4) scores about 230. v3's advantage branch also sets `clearly_losing = False`, which overrides v2's headcount flee (`len(near) > n_allies + 1`).
- **Targeted Slurm run** (jobs 56820278/79/80): 12 crushed maps, both sides, against `bots/mb_imit_uvt` (the Us V Them draft with Power Focus builds).

| Bot | Record | Deaths per game | Deaths to casters per game |
|---|---|---|---|
| q24_combo | 23W-1L | 5.83 | 1.25 |
| `mb_q24_nogroup` (EARLY_ROUNDS=0) | 23W-1L | 6.00 | 1.58 |
| tb_merge_b | 21W-3L | 6.83 | 1.42 |

  **Inconclusive.** The imitation fights with our logic and died 40.6 times per game, so it does not reproduce the ladder opponent.

### (2) Gold-tiebreak play: works
- 0-0 games: v3 2W-1L, v2 2W-4L.
- Structural maps: v3 3W-2L, v2 3W-6L.
- The one loss was 01boss_battle to AI Coliseum (1574), out-farmed on gold 25,319 to 38,840.

### (3) Lock memory: works, partly through map mix
- Carrier-frozen champion-rounds per game: 427 → 224. Rating-controlled −382 ± 196.
- It does not cover the pre-existing **stuck champion**. On 01shortcut, Vendetta sat idle with 0 gems from r288 and from r652 to r2001.
  - v2 shows it too: Heart of Ruin r226-1882.
  - The local gate shows it in both bots: gate-q24-all 01shortcut__B Vendetta r886-1596; b1-tb_merge_b-mirror-all 01shortcut__A Vendetta r1059-2001.

### (4) Fuel caching: fully effective
- `fuelExhausted` per game: 109.7 → 3.3 (rating-controlled −118 ± 43).

### What decided the worst v3 losses
No single patch appears in these.
- **Economy and items:**
  - 00swirl 128-1032: clears 31 vs 63; gold 3,673 vs 12,746.
  - 02arena 95-1007: gold 1,129 vs 13,112.
  - 01yellow_brick_road 197-1011: first clear r242 vs r40.
  - 01concentrated_wealth 305-1033: first tribute r320 vs r128.
  - In v3 losses overall, opponent gold averaged 7,815 against our 4,143, and opponents cleared 4.9 camps per 100 rounds against our 2.4.
- **Focus-caster spawn camp:** 00packs, 0-1020 and 85-1005, against Us V Them.
- **Boss camp:** 00contest 0-1000. They took the 200-gem bags 5 times from r800; we took none, despite 88 clears against their 49.
- **Carrier ganks:** 00great_wall 180-1003, 378 gems lost over 16 deaths.
- **Mid-map fight lock:** 02treasure_box 19-1015 against AI Coliseum.

## Analysis
1. **The headline gap was mostly an artefact.** 24-26 against 21-9 compared the wrong rows (25 of them mislabelled) against v2's hottest 30 games. Corrected, the records are 37-38 against 74-36, and about 40% of that raw gap is schedule: v3's opponents averaged 1534 against v2's 1479.
2. **What is left is model-dependent and not significant.**
   - Elo-slope models put v3 40-100 Elo below v2's *whole* sample (p 0.10-0.36).
   - That whole sample includes a 39-11 record against teams rated ≤ 1485, which v3 never met.
   - Against matched opposition the gap is +9 Elo [−139, +132].
   - Against v2's post-climb form it is +31 [−88, +144].
   - v3's θ of about 1520-1530 is *above* v2's 10-set plateau performance of 1513, and below v2's late burst (1740 over 3 sets).
3. **More v3 games alone cannot settle a 50-Elo question.** v2's θ is frozen at ±29-32 (set-clustered), so the difference can never reach z = 2 for a ~55-Elo gap. About 100 more v3 games would let a 75-100 Elo gap show at one-sided 95% (Skeptic).
4. **No patch is implicated.**
   - Mechanisms 2-4 demonstrably work on real games.
   - The group rule's ladder cost is confined to one opponent (Us V Them). It comes from a threat formula that v2 shares and an opponent that v2 never met.
   - The only ablation run showed no effect, but it is inconclusive.
   - Removing the group rule would discard the largest local gain in q24 (h_earlyfight_all: 84/140 alone vs tb_merge_b) on no ladder evidence. That is the opposite of the "certain to outperform" standard.
5. **The v3-specific pattern worth chasing is the lopsided sets.** Five whole-set collapses in 17 sets: AI Coliseum, Mein Kraft, Us V Them, John Doe and Warwick, against none in v2's 22. Each collapse is a comp-specific failure (focus-caster nukes, economy snowballs, boss timing). These are improvement targets for the normal pipeline, not reasons to roll back.
6. **Weighing the options:**
   - **(1) Keep v3:** supported. No significant deficit, local evidence in its favour, and mechanisms confirmed.
   - **(2) Re-activate v2:** not supported. P(v3 ≥ v2) is 0.05-0.09 on whole samples but 0.2-0.5 on matched opposition, so a switch would not be "certain to outperform". It also changes the team account and so would need the user's approval.
   - **(3) Fixed v3 variant:** no patch is identified to disable or change, so a variant now would be a guess.
   - **(4) Wait:** passive monitoring continues anyway (below), but it is not a decision, because the evidence can't converge from v3 data alone.

## Verdict
**Keep v3 (q24_combo) live. Do not recommend re-activating v2, and do not build a patch-removal variant.**
- The claim "v3 is worse than v2" is **not supported** at any conventional level.
- The best summary is: **"v3 is about equal to v2 within noise, leaning 40-80 Elo weaker on whole-sample comparisons, about equal against matched opposition."**
- **Confidence: medium.** The point estimates mostly lean against v3, and v3's sets are unusually lopsided, so a real 50-100 Elo regression cannot be ruled out.

## Recommendations
These are for the orchestrator and user. I made no repo edits other than this report.

1. **Keep v3 live; no rollback; no patch removal.** Report the ladder state as "v3 41W-44L over 85 games (corrected) at θ about 1520-1530, holding the 1530 rating it inherited (1519.8 at 04:28, rank 385/815). v2 74W-36L over 110 games, θ 1584 ± 32 post-convergence. Difference not significant." Drop the "24-26 vs 21-9" framing from STATUS.
2. **Fix the ladder attribution** (owner: whoever maintains `tools/ladder_pull.py`).
   - **Relabel the rows.** The 25 rows in groups created 01:40:08-02:20:08 UTC become `v=3`.
   - **Change the puller:**
     - store `createdAt` in each row;
     - re-derive `v` for *every* row on each run;
     - use the rule **version = newest version whose predecessor's `statusAt` ≤ the set's `finishedAt`**. This fits both observed switches: v1 `statusAt` 21:53:18.963 with the set finishing at 21:53:35 already on v2's draft, and v2 `statusAt` 01:42:13.317 with the set finishing at 01:42:23 already v3 by fuel.
   - **Correct the version file.** `results/ladder-versions.json` stores `"2": "2026-10-31T21:42:13.848Z"`, which is v2's *upload* time. v1's `statusAt`, 21:53:18.963, is the real switch: the set finishing at 21:43 still used v1's draft with Varg.
   - **Sanity check.** Use `fuelExhausted` ≤ 1 per game as the v3 fingerprint.
3. **Measurement standard for version comparisons:**
   - compare θ (strength against opponent ratings only) with set-clustered SEs, plus a matched-opponent-band comparison;
   - never use S-E against our own rating, which only measures inherited rating lag;
   - never compare against a hand-picked last-N window;
   - reconstruct pre-set ratings by chaining Elo with K=32 per set.
4. **Monitoring trigger** (passive; no simulation needed). When v3 reaches **≥ 150 corrected games** (about 13 more sets), rerun θ, the Elo-offset model and the matched band.
   - **Raise it with the user** if v3's θ is below 1500 *and* the Elo-offset gap against v2's post-climb window is one-sided p < 0.05.
   - **Otherwise keep v3.** A θ of 1530 or more is consistent with v2's post-climb level.
   - This trigger becomes moot if a successor (c2, c3 or c4) is promoted first.
5. **Optional paired test, which needs the user's approval because it uses the team's shared quota.** This is the only cheap way to remove the opponent confound without re-activating v2.
   - **Method:** with v3 live, replay v2's ladder sets against the *same opponent bot versions*: `cambc match-groups create <opp team id> --source-group <v2 ladder groupId> --maps <the 5 maps> --sides <the 5 sides>`. Then compare v3 with v2 game by game (McNemar on the discordant pairs).
   - **Priority:** v2's 13 post-climb sets (65 games).
   - **Quota at 04:28:** limit 50, used 0. The CLI does not say whether the units are groups or matches.
   - **Caveats:** it is unverified whether `--source-group` accepts a *ranked* group id; and fuel-sensitive bots don't replay bit-identically across machines.
   - **The alternative** is a v2/v3 ladder A/B: about 370 games per version for 75 Elo, about 830 for 50. That is a live-version change and also needs the user.
6. **Promotion hedge.** For successors built on q24 (c2, c3, c4), also run the 140-game screen against `tb_merge_b` and require at least q24's 87/140. Self-play can't settle the ladder doubt, but this keeps a successor from drifting below v2 locally while that doubt stands.
7. **Pull and analyse the two new sets.** Run `tools/ladder_pull.py` on the next tick, then `analyze_match.py` on the 04:10 Mein Kraft 0-5 and the 04:20 Velvet Pathfinders 4-1. 02treasure_box is now 0-3 for v3 (STATUS: Q27). 00contest and 00galaxy were lost again.
8. **Clean-up of analysis artefacts** (untracked):
   - bots: `bots/mb_q24_nogroup` and `bots/mb_imit_uvt`;
   - match folders: `matches/mb-q24-vs-uvt`, `matches/mb-nogrp-vs-uvt`, `matches/mb-tbm-vs-uvt`, `matches/mb-ladder-v2` and `matches/mb-ladder-v3`;
   - scratch scripts (`skeptic.py`, `band.py`, `fe.py`, `ladder_mech.py`, `agg.py`, `ctrl.py`, `localfight.py`, `extra_rows.json`, `memo_*.json`) in `/tmp/claude-69101/-n-home05-ianpoon-Cambridge-BattleCode-Turborecallers-2026/5245ba49-8b5b-4d9a-9345-708126bcbea8/scratchpad`.

## New hypotheses (for STRATEGIES.md; number them when they are added)
- **V3L-1 Focus-burst threat model.**
  - *Problem:* `enemy_dps = strength + 0.15 × focus` underrates Power Focus Stellar and Ren nukes (2×F, and 1.1×F plus stun, at range 4).
  - *Evidence:* Us V Them went 3-7 against us with 29 deaths per game; we were spawn-camped on 00packs.
  - *Change:* score spell burst (multiplier × focus when the spell is off cooldown, plus a one-shot check against our HP) in `threats`, `group_balance` and `recall_safe`. Keep v2's headcount flee active even when the group rule says "advantage".
  - *Precondition:* build a focus-caster imitation that farms and kites competently, and verify it takes games off tb_merge_b; `mb_imit_uvt` died 40.6 times per game.
- **V3L-2 01shortcut stuck champion.**
  - *Problem:* a champion idles with 0 gems for 1,300-1,700 rounds. v3 went 0-3 on 01shortcut, v2 has the same behaviour, and it is reproducible locally (gate-q24-all 01shortcut__B Vendetta r886-1596).
  - *Fix path:* trace one deterministic game through `tools/onslurm.sh -c 2`, then fix the navigation or target loop. It costs 25% of a 4-pick team.
- **V3L-3 Boss-camp commit timing.**
  - *Problem:* on 00contest the ladder opponent took the 200-gem bags 5 times from r800; we took none despite out-clearing them 88 to 49. Local q24 takes the boss at r1440-1700.
  - *Change:* commit to the boss camp earlier when gems come from one giant camp.
- **V3L-4 Economy gap against teams rated 1530+.**
  - *Problem:* in v3 losses opponent gold averaged 7,815 against our 4,143, and their clears 4.9 against our 2.4 per 100 rounds.
  - *Builds to study:* Treasure ×20-28 and Bruiser Strength ×27 snowballs; on 02arena our Marcella earned 70 gold.
  - *Approach:* farming tempo and item builds measured against imitations of real 1530+ comps. This links to Q26 (c3_teamclear) and Q27.
- **V3L-5 Whole-set collapses against specific comps.**
  - *Problem:* 5 of 17 v3 sets had ≤ 1 win, against 0 of 22 for v2. Our draft is the same in both versions.
  - *Comps to imitate:*
    - AI Coliseum: Vendetta, Cassi&Issac, Ryth, Stellar;
    - Mein Kraft: Vesper, Tavi, Varg, Willow, Cassi&Issac;
    - Us V Them: Ren, Stellar, Cassi&Issac, Ryth;
    - John Doe: HoR, Vesper, Prism, Ryth, Marcella;
    - Warwick: HoR, Vesper, Marcella, Ryth.
  - *Test:* compare q24_combo with tb_merge_b against them through `tools/onslurm.sh`. A consistent gap there would be the first real evidence against the all-game group rule.
- **V3L-6 01xx and 4-pick weakness (marginal).**
  - *Signal:* on the ladder, v3 was 8/21 on 01xx maps against v2's 13/17, and 6/14 on 4-pick maps against 13/17.
  - *Self-play doesn't show it:* locally q24 went 19/30 on 01xx and 20/32 on 4-pick.
  - *Next step:* test only together with V3L-1 or V3L-5 opponents, never as a self-play rerun.

## Checked in this pass
| Check | How | Result |
|---|---|---|
| Corrected records | Recount of `ladder-games.jsonl` | v2 74-36 and v3 37-38 |
| θ values | Quick recomputation | Matches Statistics: 1605, 1584, 1530 |
| Submission timestamps | `cambc submissions list` | v1 `statusAt` 21:53:18.963; v2 created 21:42:13.848, `statusAt` 01:42:13.317; v3 created 01:24:35.093 |
| Finish times of the 01:40 set | Ladder log | 01:42:23-01:42:26 |
| Local-gate subgroup records | `matches/gate-q24-all` | As in section 5 |
| Two newest sets and current rating | Read-only `cambc matches list` and `cambc ladder` | As in "Data" |
