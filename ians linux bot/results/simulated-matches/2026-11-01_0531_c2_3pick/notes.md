# Experiment: c2_3pick, fixing c2_respawn's 3-pick regression against mirror-draft opponents (2026-11-01, cluster)

Workflow batch 5 item **c2_3pick** (STRATEGIES queue line "c2 3-pick mirror-draft regression"). Run on the cluster: Slurm `test` partition through `tools/onslurm.sh`, cambc 4.0.0 / engine 2.0.0. Candidate `bots/c2_3pick`; design notes in `bots/c2_3pick/NOTES.md`. Nothing was promoted, submitted or committed, and no tracked status file was edited.

**Bottom line.**
- **Cause.** Hunk (a) of `RESPAWN_FIX` alone causes the regression. That hunk removed q24's in-turn push-back off camp tiles.
  - The skeptic's H1 is **not** the cause. H1 was the step-off on quiet turns only, deadlocking or walking into fights.
- **Fix.** Restore the push-back, but only off the champion's *own target group's* tiles, and only for 3-champion teams. This recovers the 3-pick games against the tb_merge family:
  - **33/48 against c2's 20/48**, with 15 games won where c2 lost and 2 lost where c2 won (sign test p = 0.0023);
  - deaths per game vs tb_merge_b fall from 11.2 to 7.6.
  - It is neutral against c2_respawn and four ladder-draft imitation bots.
- **Final runs.**
  - **vs tb_merge_b: 106/140** (c2 98).
  - **vs c2_respawn: 70/140.** This fails the ≥ 82 gate by construction, because the change is inert on 116 of the 140 games.

## Hypothesis
- **What:** c2_respawn (website v4) lost 3-pick map-sides that every q24_combo run won.
  - Against tb_merge_b on 3-pick map-sides: 10/24 against q24's 19/24, Fisher p = 0.017.
  - Deaths per game 11.2 against 6.5.
  - Against tb_merge_a: 1/8 against 4/8 on the sprint 3-pick map-sides.
  - The c2 gate report's H1 suspected `leave_respawn_tile` (end-of-turn step-off, quiet turns only) of deadlocking or walking champions into fights when an enemy is near.
  - The skeptic proposed either "step-off only off-fight" or q24's behaviour for 3-pick drafts, keyed on team size and not on map names.
- **Source:** the c2 skeptic pass (`results/simulated-matches/2026-11-01_0437_c2_respawn/notes.md`, H1; STRATEGIES queue). Matches `matches/skc2-vs-tbm-all` (c2 vs tb_merge_b) and `matches/gate-q24-all`, `plc-b-vs-tbm` and `plc2-a-tbm` (q24 and two fuel placebos of it vs tb_merge_b).
  - All three q24-family runs give 19/24, game for game, on the 3-pick map-sides.

The 12 three-pick maps (`len(champions) == 6` in the stats JSON) are 00anvil, 00breadcrumbs, 00collision, 00fragment, 00packs, 01broken-curve, 01gold-rush, 01the-farm, 02arena, 02the-pack, 02the-pond and adgato-gemcombat1. Both tb_merge bots and we draft Vesper Vale, Vendetta and Marcella there (mirror draft).

## Setup
- **Candidate:** `bots/c2_3pick`, forked from the champion `c2_respawn` with `tools/newbot.py`. Only `src/bot.py` differs (md5 `c792936e54eed74028d2fed80c0794be`); main/draft/randomness are byte-identical.
- **Final diff (iteration 2):**
  - **New flag.** `PUSHBACK_3PICK = True`.
  - **Team-size switch.** `self.pb3 = PUSHBACK_3PICK and len(handles) == 3` is set once in `init_static`; `handles` comes from `cambc.champions(Team.ALLY)`.
  - **Push-back condition.** It becomes `((self.pb3 and G.tiles.is_set(pos)) or not RESPAWN_FIX) and G.status != 1 and all_camp_tiles(pos) and blocks_respawn(pos)`.
    - The body is q24's: step to the adjacent non-camp tile nearest `G.center` and end the turn.
    - Everything else in c2_respawn is untouched, at every team size.
  - **Iteration 1** restored the whole push-back (any camp tile) for 3-champion teams. That is `c2p3_noA` behaviour on 3-pick maps.
- **Diagnosis bots** (throwaway, made with `tools/newbot.py`):
  - **Hunk ablation:** `c2p3_noA` / `noB` / `noC` / `noD` / `off` are c2_respawn with hunk (a) push-back removal / (b) step-off / (c) farm-goal mask / (d) fresh-read gate turned off, or all four. They use the per-hunk flags `RF_A`-`RF_D`.
  - **Push-back categories:** `c2p3_pbT` pushes back only off tiles of the target group. `c2p3_pbO` pushes back only off tiles of *other* groups. `c2p3_pbK` pushes back off any camp tile but does not end the turn: it keeps farming and casting after the move.
  - **Trace bots:** `dbg_c2p3_tr` and `dbg_q24p3_tr` are c2_respawn and q24_combo with per-turn `cambc.debug_block` trace lines (`T round champ x y hp gems e<n>/<dist>/<incoming> quiet+canmove target on-tile tags`).
    - The tags are: `SO` step-off executed; `STAYn`/`STAYq` turn ends stationary on a Respawning tile, not quiet/quiet; `PB` push-back (q24) or `PBc` push-back q24 *would* do (c2); `GS`/`GSc` unseen-alive guess fired / suppressed by the fresh-read gate; `FM` farm-goal mask changed goals; `WR` ring wait; `CAP` capture; `HE` fight branch; `DR` danger retreat; `TB` tribute.
    - They ran through `cambc run-batch --log-limit 6000000`: runner `matches/c2p3-tools/trace_batch.py` extracts `<map>__<side>.<a|b>.stdout`.
- **Jobs** (all `tools/onslurm.sh`, both sides, the 24 three-pick map-sides unless "all"):

| Job | Command (abridged) | Tag(s) |
|---|---|---|
| 56824687 | trace_batch dbg_c2p3_tr / dbg_q24p3_tr vs tb_merge_b | `c2p3-tr-c2`, `c2p3-tr-q24` |
| 56824288 | eval c2p3_{noA,noB,noC,noD,off} tb_merge_b | `c2p3-abl-*` |
| 56825294 | eval c2p3_{pbT,pbO,pbK} tb_merge_b | `c2p3-abl-pb*` |
| 56825295 | eval c2p3_noA tb_merge_b --maps all | `c2p3-noA-tbm-all` |
| 56826004 / 56825834 / 56825991 | iteration 1 vs tb_merge_b, tb_merge_a, c2_respawn, tb_aggro, imit_test; q24 and c2 baselines vs tb_merge_a, tb_aggro, imit_test | `c2_3pick-scr-*`, `c2p3-base-*` |
| 56826681 / 56826797 | pbT vs c2_respawn and tb_merge_a; noA vs c2_respawn; iteration 1 and c2 vs h3_csv, h3_tvv | `c2p3-pbT-*`, `c2p3-noA-c2_respawn`, `c2p3-h3-*` |
| 56828142 / 56828138 | final version vs tb_merge_b, tb_merge_a, c2_respawn, h3_csv, h3_tvv; final and c2 vs lad_vcst, lad_hyb | `c2_3pick-v2-*`, `c2p3-lad-*` |
| **56828146** | `python3.12 tools/eval.py c2_3pick c2_respawn --maps all --jobs 16 --keep --tag c2_3pick-all` | `c2_3pick-all` |
| **56828140** | `python3.12 tools/eval.py c2_3pick tb_merge_b --maps all --jobs 16 --keep --tag c2_3pick-tbm-all` | `c2_3pick-tbm-all` |
| 56829015 | `./cli/cambc run c2_3pick c2_respawn --map 02arena --release -o matches/c2_3pick-release` | release check |

Two jobs (56825832/3) died in rsync with "Stale file handle", because another workflow deleted a bot directory mid-copy. They were resubmitted unchanged.

## Results (verbatim)
Final runs:
```
SUMMARY c2_3pick vs c2_respawn: 70W-70L (50%)  avg gems 686 vs 696  avg deaths 10.3 vs 10.4  botFaults(A) 0
SUMMARY c2_3pick vs tb_merge_b: 106W-34L (76%)  avg gems 788 vs 533  avg deaths 9.0 vs 14.3  botFaults(A) 0
Team B (c2_respawn) wins: round limit (2000) reached with more gems     [release, 02arena: 339-656, crashes 0/0]
```
Diagnosis and screens (24 three-pick map-sides each):
```
SUMMARY c2p3_noA vs tb_merge_b: 19W-5L (79%)  avg gems 744 vs 440  avg deaths 7.3 vs 13.0  botFaults(A) 0
SUMMARY c2p3_noB vs tb_merge_b: 10W-14L (42%)  avg gems 609 vs 674  avg deaths 11.0 vs 9.3  botFaults(A) 0
SUMMARY c2p3_noC vs tb_merge_b: 13W-11L (54%)  avg gems 664 vs 626  avg deaths 9.7 vs 11.6  botFaults(A) 0
SUMMARY c2p3_noD vs tb_merge_b: 11W-13L (46%)  avg gems 615 vs 694  avg deaths 10.9 vs 9.9  botFaults(A) 0
SUMMARY c2p3_off vs tb_merge_b: 19W-5L (79%)  avg gems 753 vs 441  avg deaths 6.5 vs 13.3  botFaults(A) 0
SUMMARY c2p3_pbT vs tb_merge_b: 18W-6L (75%)  avg gems 731 vs 529  avg deaths 7.6 vs 12.8  botFaults(A) 0
SUMMARY c2p3_pbO vs tb_merge_b: 15W-9L (62%)  avg gems 665 vs 540  avg deaths 9.1 vs 10.8  botFaults(A) 0
SUMMARY c2p3_pbK vs tb_merge_b: 14W-10L (58%)  avg gems 675 vs 558  avg deaths 8.6 vs 11.6  botFaults(A) 0
SUMMARY c2p3_noA vs tb_merge_b: 93W-47L (66%)  avg gems 747 vs 548  avg deaths 9.1 vs 14.6  botFaults(A) 0     [all maps]
SUMMARY c2p3_pbT vs c2_respawn: 12W-12L (50%)  avg gems 589 vs 655  avg deaths 8.7 vs 7.2  botFaults(A) 0
SUMMARY c2p3_pbT vs tb_merge_a: 16W-8L (67%)  avg gems 634 vs 581  avg deaths 8.6 vs 13.8  botFaults(A) 0
SUMMARY c2p3_noA vs c2_respawn: 9W-15L (38%)  avg gems 535 vs 710  avg deaths 10.4 vs 7.4  botFaults(A) 0
```
Iteration 1 (whole push-back for 3-champion teams):
```
SUMMARY c2_3pick vs tb_merge_b: 19W-5L (79%)  avg gems 744 vs 440  avg deaths 7.3 vs 13.0  botFaults(A) 0
SUMMARY c2_3pick vs tb_merge_a: 17W-7L (71%)  avg gems 668 vs 536  avg deaths 8.5 vs 13.2  botFaults(A) 0
SUMMARY c2_3pick vs c2_respawn: 9W-15L (38%)  avg gems 535 vs 710  avg deaths 10.4 vs 7.4  botFaults(A) 0
SUMMARY c2_3pick vs tb_aggro: 24W-0L (100%)  avg gems 910 vs 122  avg deaths 1.6 vs 24.2  botFaults(A) 0
SUMMARY c2_3pick vs imit_test: 24W-0L (100%)  avg gems 920 vs 249  avg deaths 1.7 vs 33.8  botFaults(A) 0
SUMMARY c2_3pick vs h3_csv: 21W-3L (88%)  avg gems 832 vs 385  avg deaths 3.8 vs 33.0  botFaults(A) 0
SUMMARY c2_3pick vs h3_tvv: 17W-7L (71%)  avg gems 766 vs 457  avg deaths 5.1 vs 16.2  botFaults(A) 0
```
Final version (iteration 2) and baselines:
```
SUMMARY c2_3pick vs tb_merge_b: 18W-6L (75%)  avg gems 731 vs 529  avg deaths 7.6 vs 12.8  botFaults(A) 0
SUMMARY c2_3pick vs tb_merge_a: 15W-9L (62%)  avg gems 616 vs 589  avg deaths 9.1 vs 13.3  botFaults(A) 0
SUMMARY c2_3pick vs c2_respawn: 12W-12L (50%)  avg gems 589 vs 655  avg deaths 8.7 vs 7.2  botFaults(A) 0
SUMMARY c2_3pick vs h3_csv: 23W-1L (96%)  avg gems 860 vs 350  avg deaths 3.4 vs 29.6  botFaults(A) 0
SUMMARY c2_3pick vs h3_tvv: 22W-2L (92%)  avg gems 808 vs 420  avg deaths 5.7 vs 16.4  botFaults(A) 0
SUMMARY c2_3pick vs lad_vcst: 23W-1L (96%)  avg gems 914 vs 266  avg deaths 1.7 vs 32.2  botFaults(A) 0
SUMMARY c2_3pick vs lad_hyb: 21W-3L (88%)  avg gems 850 vs 368  avg deaths 3.3 vs 27.7  botFaults(A) 0
SUMMARY c2_respawn vs tb_merge_a: 10W-14L (42%)  avg gems 559 vs 719  avg deaths 12.3 vs 8.3  botFaults(A) 0
SUMMARY c2_respawn vs tb_aggro: 24W-0L (100%)  avg gems 843 vs 89  avg deaths 1.3 vs 22.0  botFaults(A) 0
SUMMARY c2_respawn vs imit_test: 24W-0L (100%)  avg gems 900 vs 187  avg deaths 1.2 vs 32.2  botFaults(A) 0
SUMMARY c2_respawn vs h3_csv: 23W-1L (96%)  avg gems 844 vs 347  avg deaths 3.1 vs 30.1  botFaults(A) 0
SUMMARY c2_respawn vs h3_tvv: 21W-3L (88%)  avg gems 872 vs 360  avg deaths 3.6 vs 18.2  botFaults(A) 0
SUMMARY c2_respawn vs lad_vcst: 24W-0L (100%)  avg gems 899 vs 192  avg deaths 1.2 vs 31.2  botFaults(A) 0
SUMMARY c2_respawn vs lad_hyb: 20W-4L (83%)  avg gems 810 vs 415  avg deaths 5.6 vs 25.6  botFaults(A) 0
SUMMARY q24_combo vs tb_merge_a: 18W-6L (75%)  avg gems 688 vs 536  avg deaths 8.4 vs 13.7  botFaults(A) 0
```

**3-pick record before and after** (24 map-sides each; deaths per game us / them):

| Opponent | c2_respawn | **c2_3pick (final)** | iteration 1 (whole push-back) | q24_combo |
|---|---|---|---|---|
| tb_merge_b (mirror draft) | 10/24, 11.2 / 9.3 | **18/24, 7.6 / 12.8** | 19/24, 7.3 / 13.0 | 19/24, 6.5 / 13.3 |
| tb_merge_a (mirror draft) | 10/24, 12.3 / 8.3 | **15/24, 9.1 / 13.3** | 17/24, 8.5 / 13.2 | 18/24, 8.4 / 13.7 |
| **tb_merge family, pooled** | **20/48** | **33/48** | 36/48 | 37/48 |
| c2_respawn | (12/24 mirror) | **12/24**, 8.7 / 7.2 | 9/24, 10.4 / 7.4 | 10/24 (gate-c2-all) |
| h3_csv (tbm logic, C&I/Stellar/Vesper) | 23/24 | **23/24** | 21/24 | |
| h3_tvv (tbm logic, Tavi/Varg/Vendetta) | 21/24 | **22/24** | 17/24 | |
| lad_vcst | 24/24 | **23/24** | | |
| lad_hyb | 20/24 | **21/24** | | |
| **non-mirror drafts, pooled** | **88/96** | **89/96** | (h3 only: 38/48 vs c2's 44/48) | |
| tb_aggro / imit_test | 24/24, 24/24 | (iteration 1: 24/24, 24/24) | | 8/8, 8/8 (sprint) |

- **Paired flips vs c2_respawn**, same map-sides:
  - tb_merge_b: +9 / −1 on 3-pick;
  - tb_merge_a: +6 / −1.
  - **Pooled +15 / −2, sign test p = 0.0023.**
  - The non-mirror drafts are +6 / −5.
  - Iteration 1 against h3_csv and h3_tvv was +1 / −7.

**Final all-maps runs by team size:**

| Run | 3-pick (24) | 4-pick (32) | 5-pick (84) | Total | Sides A / B |
|---|---|---|---|---|---|
| **c2_3pick vs tb_merge_b** | **18**, d7.6 | 25, d10.7 | 63, d8.7 | **106** | 53 / 53 |
| c2_respawn vs tb_merge_b (`skc2-vs-tbm-all`) | 10, d11.2 | 24, d10.5 | 64, d8.5 | 98 | 50 / 48 |
| q24_combo vs tb_merge_b (`gate-q24-all`) | 19, d6.5 | 20, d11.2 | 48, d9.6 | 87 | 43 / 44 |
| c2p3_noA (whole push-back, every team size) vs tb_merge_b | 19, d7.3 | 23, d10.3 | 51, d9.1 | 93 | |
| **c2_3pick vs c2_respawn** | **12**, d8.7 | 15, d11.7 | 43, d10.2 | **70** | 34 / 36 |
| q24 vs q24 mirror (`plc-mirror`), for scale | 12 | 16 | 42 | 70 | 33 / 37 |

- **vs tb_merge_b:** 114 of the 116 four/five-pick results equal c2_respawn's. The two exceptions are 01shortcut B (+1) and 01big-world B (−1), which is fuel-trajectory noise. All the gain is the 3-pick change: +10 / −2.
- **vs c2_respawn:** 56 of 58 four/five-pick maps split 1-1, decided by side as in a mirror; 01boss-battle went 2-0 and 01shortcut 0-2. On 3-pick, 00collision and 01broken-curve went 2-0, 00anvil and 02arena 0-2, and the other 8 maps split.
- **botFaults** 0/0 in all 280 games.
- **fuelExhausted:** c2_3pick 837 against c2_respawn 857 in the same 140 games, and 919 against c2's 947 against tb_merge_b.
- **Release game:** 0 crashes, `team-a/b.stdout` and `.debug` 0 bytes, botFaults 0/0, fuelExhausted 0. It reproduces the debug-build result: 02arena A is lost in `c2_3pick-all` too.

**`match_metrics.py matches/c2_3pick-all`:** 140 games; 3,821 tributes, mean tribute 25.1; deaths 1.0 per game to camps and 9.3 to champions; fuelExhausted 6.0 per game.

**`analyze_match.py --summary --games` on the 24 three-pick games vs tb_merge_b (18 W / 6 L):**

| metric | wins | losses |
|---|---|---|
| gems us-them | 864-393 | 333-937 |
| clears us / them | 73.5 / 39.2 | 74.2 / 101.8 |
| kills us / them | 15.0 / 4.4 | 5.5 / 15.7 |
| gold us / them | 9,134 / 3,646 | 3,682 / 7,378 |
| gem lead r250 / r500 / r1000 | +5 / +51 / +127 | −6 / −79 / −249 |

## Analysis session

### 1. Debug traces: H1 (step-off with an enemy in sight) is not the cause
- **The traces reproduce the real games.** `dbg_c2p3_tr` vs tb_merge_b went 10/24 with the same W/L and death counts as `skc2-vs-tbm-all` in all 24 games. `dbg_q24p3_tr` went 19/24, identical to `gate-q24-all` except the death counts on 01the-farm A/B.
- **Totals over the 24 map-sides:**

| Event | c2 trace | q24 trace |
|---|---|---|
| step-off executed (`SO`) | **7** | (not in q24) |
| stationary on a Respawning tile, step-off blocked by "not quiet" (`STAYn`) | **46** | 56 |
| stationary on a Respawning tile, quiet (`STAYq`) | 0 | 0 |
| in-turn push-back: done (`PB`) / would be done (`PBc`) | 2,584 would-be | **2,752 done** |
| unseen-alive guess: fired fresh / stale (`GS` / `GSs`) | 62 suppressed (`GSc`) | 1,040 / 156 |
| farm-goal mask changed goals (`FM`) | 746 | n/a |
| ring waits / captures / fight branch / danger retreats | 3,692 / 19,954 / 24,747 / 1,032 | 4,024 / 19,644 / 24,118 / 905 |

- The step-off machinery barely acts on 3-pick maps: 7 step-offs and 46 blocked turns in 24 games, against about 108 push-backs per game.
- **Classifying the 2,584 would-be push-backs** in c2 by where the turn ended:
  - **868 (34%)** stayed on a tile of the alive target group, with a camp hitting it or an enemy in sight, without moving. This is a melee champion farming from a dead member's tile.
  - 771 had already walked onto a non-camp tile.
  - 256 ended the move on a Respawning tile.
  - 195 were on RewardAvailable tiles.
  - The rest were mixed.
- **First divergence between c2 and q24 on the same map-side** is always a push-back:
  - **01broken-curve B, r24:** Vendetta on (8,24), a dead tile of target group 3, with a camp hitting for 40.
    - c2 stays and farms: Vendetta goes 840 → 400 HP by r41 while Marcella takes 0 damage.
    - q24 steps to (7,23) and loses that turn. The camp damage then splits between Vendetta (480) and Marcella (920).
    - c2's Vendetta walks home at r47 and the games diverge. c2 lost that map-side 3-12 in kills; q24 won it.
  - The same pattern is the first divergence on 02arena A at r45 (group 12) and on 00packs B at r19 (group 3).

### 2. Which hunk: ablation on the 24 map-sides vs tb_merge_b
- **Push-back removal (a) is the only hunk that matters.**
  - Restoring it alone (noA) gives 19/24, with deaths 7.3 vs 13.0.
  - Turning off the step-off (noB, 10/24), the farm mask (noC, 13/24) or the fresh-read gate (noD, 11/24) leaves c2's record.
  - All four off (`c2p3_off`) reproduces q24_combo **game for game** (19/24, identical deaths), so the regression is the patch, not fuel noise.
- **Which push-backs:**
  - Off the target group's own tiles only (pbT): 18/24, deaths 7.6 vs 12.8.
  - Off other groups' tiles only (pbO): 15/24.
  - The relocation that keeps farming and casting in the same turn (pbK): 14/24.
  - So most of the effect comes from the 868-type events, and from the push-back *ending the turn*, not only from where the champion stands.
- **Restoring it everywhere is wrong.** noA on all 140 maps scores 93: 3-pick 19, 4-pick 23, 5-pick **51/84** against c2's 64. The 5-pick gain of the respawn fix is the removal of this same push-back, which confirms the h_respawnfix freeze analysis. The rule therefore has to be scoped.
- **Team size, not map size, separates the two regimes.** c2 minus q24 vs tb_merge_b:

| Team size | < 1,100 tiles | 1,100-2,000 | 2,000-3,000 | ≥ 3,000 |
|---|---|---|---|---|
| 3-pick | −4 (14) | −4 (6) | −1 (4) | none |
| 4-pick | +1 (16) | +2 (10) | +1 (6) | none |
| 5-pick | +2 (4) | −1 (10) | +4 (30) | +11 (40) |

  Small 4- and 5-pick maps show no regression.

### 3. Mechanism: what the push-back changes on 3-pick maps vs tb_merge_b
- **Economy is even through r300 and splits by r600.** By r600, with c2 vs tb_merge_b, then q24 vs tb_merge_b, then c2_3pick vs tb_merge_b:
  - **clears (us/them):** 23/22 for c2, 23/18 for q24, 24/21 for c2_3pick;
  - **earned gold:** 1,595/1,489, then 1,718/1,203, then 1,848/1,238;
  - **kills/deaths:** 3/3, then 3/2 and 2/4, then 4/2 and 2/4.
  - By r150 c2 is even slightly ahead (gold 348 vs 308).
- **The difference is the opponent's farming and the early fights.**
  - tb_merge_b clears 20.7 groups by r600 against c2 and 17.0 against q24.
  - Capture steals are not the channel: about 1 per side per game either way, and the clear-to-capture delay is the same 10-11 rounds.
- **Deaths by r300 / r600 / r1000 (us / them, per game):**
  - c2: 1.58/1.58, 3.12/2.83, 6.04/5.21;
  - q24: 1.00/1.50, 2.42/3.54, 3.50/6.46;
  - c2_3pick: 1.12/1.67, 2.42/3.92, 4.17/6.83.
- **Context of early deaths** (trace, r ≤ 600; c2 75 deaths, q24 58):
  - 75-76% followed a turn with both a camp hitting and an enemy in sight, in both bots.
  - HP at the first sight of an enemy is identical (median 1,000; 9% below 600 HP in both).
  - c2 lost more carriers: 26 deaths carrying ≥ 10 gems, against 13.
  - So c2 does not enter fights weaker. It loses more of the same contested-camp fights.
- **The effect is opponent-specific (non-transitive):**
  - The whole push-back beats the stay-and-farm style against the push-back bots tb_merge_a and tb_merge_b, which draft the same three champions.
  - It *loses* to the stay style of c2_respawn (9/24).
  - It also loses to tb_merge logic with other drafts (h3_csv/h3_tvv 38/48 vs c2's 44/48).
  - Small 3-pick maps are decided by the first contested fights around shared camp groups. Which side the push-back's skipped turn favours depends on the opposing draft.
  - The target-only rule keeps 33 of the 36 mirror-draft wins and removes the cost elsewhere: 12/24 vs c2, and 89/96 vs 88/96 against the four non-mirror drafts.
  - The exact micro-mechanism is open. It is probably camp aggro being shared, or ability timing, because the pushed turn skips `cast_combat`. See H-A below.

### 4. Losses of the final version (3-pick vs tb_merge_b, 6 of 24)
- **Also lost by q24:** 00breadcrumbs A, 00fragment B, 00packs A, 01gold-rush B.
- **Won by q24:** 00breadcrumbs B and 02the-pond B.
- **00fragment B is won by c2** (10/25) and lost by c2_3pick and q24 (26/8 and 28/7).
- **All six are fight snowballs** (our K/D 2-8 against 11-26). In four of them the enemy Vesper Vale ran away with the game:
  - 00breadcrumbs B: Vesper 10/0. We led 133-0 at r250, but lost carriers holding 21 gems at r201, r778, r794 and r833, and 14 at r395.
  - 02the-pond B: Vesper 7/0. We were down 15-85 at r250 after two deaths at r101/r110.
  - 00fragment B: Vesper 21/0, with Strength ×25.
  - 00packs A: Vesper 13/0, with Strength ×27.
- **The other two:**
  - 00breadcrumbs A: their Vendetta went 10/2 and we lost 238 gems.
  - 01gold-rush B: kills 2 vs 14, spread over their three champions.
- This is the known early-fight class (Q29), not the push-back.

### 5. Surprising results
- **The 02arena / 00anvil flip with the opponent:**
  - vs tb_merge_b: c2 0-2 (5/32 and 20/23 kills), c2_3pick 2-0 (34/3 and 26/13).
  - vs c2_respawn: c2_3pick 0-2 (7/27 and 0/31 in iteration 1).
  - vs h3_* and lad_* both bots win nearly everything there.
  - These are the maps that make the effect non-transitive.
- **Iteration 1 lost 6 net map-sides to h3_csv/h3_tvv,** among them 00breadcrumbs A/B, 00packs A and 00fragment B. So "restore q24's behaviour on 3-pick drafts" as first proposed would most likely have hurt on the real ladder, where 3-pick opponents almost never use our draft. In `results/ladder-games.jsonl`, 1 of 265 games was a 3-pick mirror draft.

### 6. The gate
- **(a) fails:** 70/140, and it cannot pass. c2_3pick plays exactly like c2_respawn on 4- and 5-pick maps: 56 of 58 maps split 1-1, so 116 games give about 58. Even 24/24 on 3-pick could not reach 82.
- **(b) gauntlet:** not run, because (a) fails.
  - On the 8 three-pick sprint map-sides, c2's gauntlet record is 8/8 against sf_bank, tb_aggro, imit_test and lad_vcst, with nothing left to gain.
  - Against tb_merge_a it is 1/8; the 24-map-side tb_merge_a screen above covers that.
- **(c):** clean release game; fuelExhausted 837 vs 857.
- **(d):** the mechanism is confirmed (sections 1-3).
- **Ladder hedge:** 106/140 vs tb_merge_b against c2's 98. That is the 3-pick gain with nothing lost elsewhere.

## Verdict
**kept, as a component, not promotable on its own.**
- **The regression's cause is identified and fixed.** It was the removed push-back, restored only off the target group's tiles and only for 3-champion teams.
  - 3-pick vs the tb_merge family goes 20/48 → 33/48 (p = 0.0023).
  - Deaths vs tb_merge_b fall 11.2 → 7.6 and vs tb_merge_a 12.3 → 9.1.
  - The ladder-hedge line rises 98 → 106/140.
  - It is neutral against c2_respawn (12/24 on 3-pick, 70/140 overall) and against four ladder-draft bots (89 vs 88 of 96).
- **It fails the LOOP.md §4 head-to-head by construction** (70/140), so it must not be shipped alone.
  - It belongs in the next merge candidate (STATUS: "c4 = c2_respawn + team clear + a fix for c2's 3-pick mirror-draft regression"), gated as a whole.
  - Its patch is three lines and touches nothing on 4/5-pick maps.
- **H1 is refuted as the cause.** The step-off acted 7 times in 24 games, and turning it off changes nothing (10/24). H1 may still matter for the 02the-pond gauntlet freeze it was raised for. That is a different symptom and was not tested here.

## New hypotheses generated
- **H-A: why skipping a farming turn wins mirror-draft 3-pick fights.**
  - **Evidence:** pbT 18/24 vs pbK 14/24. The relocation alone is not enough; the skipped turn matters, and it skips `cast_combat`.
  - c2's Vendetta tanks all camp aggro from a dead member's tile (01broken-curve B r24-41: Marcella took 0 damage).
  - The differences in early deaths are in contested camp+enemy fights.
  - **Plan:** trace ability cooldowns and camp-aggro targets at each first enemy sighting, c2_3pick vs c2. If cooldowns explain it, the rule is "keep burst abilities when a 3-pick enemy can arrive within N turns", which would generalise beyond this push-back hack.
- **H-B: draft-aware small-map play.**
  - **Evidence:** the same rule is +9 against mirror drafts and −6 of 48 against Tavi/Varg/C&I drafts (iteration 1). 02arena and 00anvil flip 2-0 ↔ 0-2 with the opponent.
  - **Plan:** log 3-pick ladder games of v4 by opponent draft (a draft-split view in `ladder_log.py`) before building any draft-keyed rule.
  - Low priority, because mirror drafts are under 1% of ladder 3-pick games.
- **H-C: methodology, a scoped gate for scoped fixes.**
  - **Evidence:** a change that is inert on 116 of 140 games scores about 70 against the champion, whatever it does on its 24.
  - **Plan:** for a change keyed on a structural game feature (team size, `no_tribute`), the gate could be:
    - a paired test on the affected subset against a diverse pool (here +15/−2 vs the tb_merge family, +6/−5 vs the rest);
    - plus a proof of no change elsewhere (here 114/116 identical results vs tb_merge_b).
  - Otherwise such fixes ride in merges only. Decide in LOOP.md.
- **H-D: Q29 evidence (early fights).** All 6 remaining 3-pick losses vs tb_merge_b are fight snowballs. Four were led by the enemy Vesper Vale (10/0, 7/0, 21/0, 13/0), with carriers of 21 gems killed. Q29 stays the top 3-pick lever.
- **H-E: H1 status.** Its 3-pick evidence is gone: 46 blocked step-offs in 24 games. Its 02the-pond gauntlet evidence (mutual freeze vs tb_aggro and imit_test) remains open and needs its own trace.
