# Experiment: h_bigmap, Q30 large-map regression fix (2026-11-01, cluster)

STRATEGIES **Q30**. This covers the claim 2-cycle fix plus a universal 2-cycle guard, forked from the champion `q24_combo`. All multi-game runs went to the free Slurm `test` partition through `tools/onslurm.sh` (cambc 4.0.0 / engine 2.0.0). Only single debug games ran locally.

**Result in one line.** The targeted mechanism is gone:
- two-target 2-cycle champion-rounds fell from **5,467 to 169** on big maps and from **1,982 to 328** on mid maps;
- big-map wins against tb_merge_b went from 2/12 to 7/12.

But the gate head-to-head against q24_combo is **80W-60L**, 2 short of 82. Wilson lower bound 0.489. **Not promotable. Kept as a merge component.**

## Hypothesis
- **What:** q24_combo's large-map regression (gate `matches/gate-q24-all`: 2/12 on the 6 maps of ≥ 8,000 tiles, clears 482 vs 579, frozen champion-rounds 16,068 vs 10,805) comes from a **target 2-cycle in `choose_target`'s claim rule**.
  - A solo-capable champion scores a teammate-claimed group ×0.3. A champion that cannot solo it scores it ×1.2 plus 55 dps of help.
  - A weak champion therefore joins a strong one's claim. The strong one sees that claim the next round and flees to the other group, and the weak one follows in the same round, because claims are visible within a round.
  - Both alternate targets every turn and step between two tiles for hundreds of rounds. The champion moves every turn, so the STUCK guard never fires. The ×1.3 current-target bonus cannot beat ×0.3.
  - This is base code inherited unchanged from tb_merge_b (tb_splitfarm); none of q24's four patches introduced it.
- **Fix:**
  1. **Claim semantics.** A claim carries a "joining, cannot solo" bit, and only a solo-capable claimant repels a solo-capable chooser.
  2. **Universal 2-cycle guard** (backstop). It covers no net displacement and A,B,A,B targets, in any branch.
- **Source:** the Q30 diagnosis. It covers:
  - the traced games `matches/q30-dbg-tangleB*` and `q30-dbg-tangleA2`;
  - 44 traced games (`matches/q30-trace`, Slurm 56782237);
  - the counterfactual `bots/dbg_q30cf` (`matches/q30-trace-cf`, Slurm 56782661), which cut two-target cycles by 92-97%.

## Setup
- **Candidate:** `bots/h_bigmap`, forked from `q24_combo` with `tools/newbot.py` by the earlier, interrupted attempt at this task (batch 3, 31 Oct ~21:58 EDT). This session reviewed that implementation line by line against the design and kept it. Only `src/bot.py` differs, and every change is behind a switch (see `bots/h_bigmap/NOTES.md`):
  - **`CLAIM_FIX`:**
    - `write_claim(idx, helper=not self.best_solo)` sets bit 7, and `read_claims` returns claim counts plus `self.claim_help` (helpers per group).
    - The split-farm `×0.3` applies only when `c > helpers`, i.e. some claimant can solo the group. Helpers still add 55 dps each, and non-solo choosers keep `×1.2`.
    - Maps with ≥ 127 groups keep the old byte. FOCUS_BYTE 7 is untouched.
  - **`CYCLE_GUARD`:**
    - `cycle_guard()` runs every turn after `threats()`. It keeps the last 4 (turn-start position, target) pairs.
    - The history resets on an attack, damage taken, a gem change, a gold gain, an enemy in view, or a skipped turn.
    - **Trigger:** 6 consecutive turns with pos[t] == pos[t-2] != pos[t-1], or an A,B,A,B target pattern over 4 turns.
    - **On trigger:** commit to the current target for 40 rounds. Claim multipliers are ignored, and the committed group gets ×1.5 instead of ×1.3, so another group must score ≥ 1.5× to win. A repeat trigger on the committed group bans it for 30 rounds.
  - No map names are special-cased.
- **Iterations** (each screened on the 19 maps over 3,000 tiles, both sides, 38 games):
  - **v1** = the design as specified, with "an awake camp in view" also counted as activity.
  - **v2 (final)** = v1 with `CYCLE_AWAKE_ACT = False`. The v1 traces showed that the residual cycles were same-target dances next to an awake camp that never hit anyone.
- **Diagnostic bots** (trace only, fuel-free `cambc.debug_block`):
  - `dbg_hbig` = v1 + trace;
  - `dbg_hbig2` = v2 + trace;
  - `dbg_q30bank` = one-off goal and bank prints on 02tangle r60-130;
  - the opponent is `dbg_tb30` (tb_merge_b + trace), as in the diagnosis.
  - The traced runner is `matches/q30-hb-trace/run_trace.py` (`--log-limit 40000000`), and the cycle detector is the diagnosis's `cyc_all.py` method (runs ≥ 20 turns of pos[t] == pos[t-2] != pos[t-1], "two-target" when the target alternates).
- **(a) Smoke games (local):**
  - `matches/q30-hb-local` (earlier attempt): 02tangle A, W 1040-693, 0 crashes;
  - `matches/q30-hb-local2` (this session): `./cli/cambc run q24_combo h_bigmap --map adgato-gemcombat5`, W 1008-511 at r1800, 0 crashes, empty team-b.stdout.
- **(b) Screens and gate head-to-head:**

| Run | Tag | Slurm job |
|---|---|---|
| v1 vs q24_combo, 19 maps > 3,000 tiles | `q30-scr-q24` | 56814892 |
| v1 vs tb_merge_b, same maps | `q30-scr-tb` | 56813797 |
| v1 traced (`dbg_hbig` vs `dbg_tb30`), same maps | `q30-hb-trace` | 56814875 |
| v2 vs q24_combo, same maps | `q30-scr2-q24` | 56818195 |
| v2 vs tb_merge_b, same maps | `q30-scr2-tb` | 56818196 |
| v2 traced (`dbg_hbig2` vs `dbg_tb30`) | `q30-hb2-trace` | 56818197 |
| **Gate head-to-head**: `tools/onslurm.sh -c 24 -m 16G -t 00:20:00 -J h_bigmap -- python3.12 tools/eval.py h_bigmap q24_combo --maps all --jobs 16 --keep --tag q30-all` | `q30-all` | 56819251 |

- **Final bot:** `bot.py` md5 `a60ff1ec2c11a5960bedab88a5dfa0dc`.

## Results (verbatim)
```
SUMMARY h_bigmap vs tb_merge_b: 25W-13L (66%)  avg gems 806 vs 747  avg deaths 7.5 vs 9.7  botFaults(A) 0      [v1, 19 maps > 3000]
SUMMARY h_bigmap vs q24_combo: 23W-15L (61%)  avg gems 829 vs 743  avg deaths 7.6 vs 8.5  botFaults(A) 0       [v1, 19 maps > 3000]
SUMMARY h_bigmap vs q24_combo: 20W-18L (53%)  avg gems 798 vs 763  avg deaths 7.1 vs 8.2  botFaults(A) 0       [v2, 19 maps > 3000]
SUMMARY h_bigmap vs tb_merge_b: 26W-12L (68%)  avg gems 824 vs 728  avg deaths 7.8 vs 10.4  botFaults(A) 0     [v2, 19 maps > 3000]
SUMMARY h_bigmap vs q24_combo: 80W-60L (57%)  avg gems 758 vs 645  avg deaths 9.3 vs 11.6  botFaults(A) 0      [v2, all 70 maps = gate (a)]
```
Every job exited 0, with 0 missing games.

**Gate (a): FAIL.**
- 80/140 against the required 82. Wilson 95% interval [0.4886, 0.6504]. botFaults 0.
- Side split: A 40/70, B 40/70. Map pairs: WW 20, LL 10, WL 20, LW 20.
- For scale: the null-change placebos against q24_combo scored 66 and 68, and the mirror 70 (`results/simulated-matches/2026-11-01_0437_placebo/notes.md`; single-run SD ≈ 5). So 80 is about +2 SD over a null, but below the gate.

Gates (b) gauntlet and (c) release game were **not run**, because gate (a) already fails and LOOP.md forbids simulating for its own sake. The fuel part of (c) can be read from the gate games: fuelExhausted 7.7 per game against q24's 7.5 in the same 140 games.

### Primary metric: 2-cycle champion-rounds (traced, vs dbg_tb30, 19 maps > 3,000 tiles)
| Bot (trace folder) | two-target cycles, big / mid | all position 2-cycles, big / mid | traced wins, big / mid |
|---|---|---|---|
| q24_combo (`q30-trace`, baseline) | **5,467 / 1,982** | 6,879 / 6,600 | 3/12, 16/26 |
| counterfactual dbg_q30cf (`q30-trace-cf`) | 154 / 159 | 2,288 / 4,736 | 7/12, 21/26 |
| h_bigmap v1 (`q30-hb-trace`) | 205 / 241 | 2,799 / 5,170 | 8/12, 19/26 |
| **h_bigmap v2 (`q30-hb2-trace`)** | **169 / 328** | **947 / 1,450** | 6/12, 22/26 |
| tb opponent in the v2 games | 2,807 / 2,668 | 6,051 / 13,982 | |

- **Two-target cycles:** −97% on big maps and −83% on mid maps, on par with the counterfactual.
- **All position 2-cycles:** v2's guard also removes most same-target cycles (−86% big, −78% mid against q24). Those are cycles the claim fix alone does not touch; the counterfactual had 2,288 / 4,736.

**Cycle turns by guard state** (candidate side, runs ≥ 20):

| | 2-target quiet | 1-target quiet | 1-target with an awake camp in view | 1-target with an enemy in view |
|---|---|---|---|---|
| q24 | 7,080 | 3,840 | 1,801 | 365 |
| v1 | 96 | 113 | **5,242** | 2,175 |
| v2 | 180 | 136 | **932** | 839 |

**Guard activity** in 38 traced games:
- v1: 201 triggers, about 72 of them bans;
- v2: 273 triggers, about 93 bans.

Helper claims (bit 7 set) were 25% of champion-turns.

### Secondary metrics
| Folder (opponent) | maps ≥ 8,000 tiles: wins / clears / frozen (`tools/freeze_metric.py`) | maps 3,000-8,000 tiles: wins / clears / frozen | wins > 3,000 tiles |
|---|---|---|---|
| gate-q24-all (q24 vs tb, baseline) | 2/12, 482:579, **16,068:10,805** | 15/26, 1,363:1,268, 6,376:13,336 | **17/38** |
| q30-scr-tb (v1 vs tb) | 7/12, 508:560, 9,400:9,799 | 18/26, 1,328:1,307, 7,247:16,106 | 25/38 |
| **q30-scr2-tb (v2 vs tb)** | **7/12, 529:536, 7,824:8,018** | 19/26, 1,332:1,294, 4,611:15,560 | **26/38** |
| q30-scr-q24 (v1 vs q24) | 6/12, 568:529, 10,493:10,227 | 17/26, 1,349:1,285, 2,304:4,563 | 23/38 |
| q30-scr2-q24 = big and mid part of q30-all (v2 vs q24) | 7/12, 564:493, 9,906:11,088 | 13/26, 1,322:1,292, 2,482:4,387 | 20/38 |

### Gate run `q30-all` (v2 vs q24_combo, 140 games)
**By map size:**

| Maps | Wins | Clears | Gems | fuelExh |
|---|---|---|---|---|
| ≥ 8,000 tiles | 7/12 | 564:493 | 10,548:9,646 | 191:189 |
| 3,000-8,000 tiles | 13/26 | 1,322:1,292 | 19,768:19,355 | 226:222 |
| ≤ 3,000 tiles | **60/102** | 5,971:5,546 | 75,776:61,254 | 656:636 |

**Paired means per game (h_bigmap : q24):**
- gems 758 : 645;
- clears 56.1 : 52.4;
- kills 10.7 : 8.5;
- deaths 9.3 : 11.6;
- gems lost 62 : 77;
- lifetime gold 6,091 : 5,313;
- tributes 30.4 : 25.8;
- fuelExhausted 7.7 : 7.5.

**Frozen champion-rounds:** 53,081 against 62,082 (big 9,906 : 11,088; mid 2,482 : 4,387; small 40,693 : 46,607).

**`match_metrics.py` (h_bigmap side):**
```
games 140  tributes 4262  mean tribute 24.9  small(<10) 423
  deaths_by_camp 117 (0.8/game)  deaths_by_champion 1186 (8.5/game)  fuelExhausted 1073 (7.7/game)
  gemsLost_to_camp 413 (3.0/game)  gemsLost_to_champion 8309 (59.4/game)  wardPlacement 61705 (440.8/game)
```

**`analyze_match --summary` (80 wins / 60 losses):**

| Metric | wins | losses |
|---|---|---|
| gems us-them | 898-473 | 572-874 |
| kills us/them | 14.8/5.6 | 5.2/12.3 |
| clears us/them | 58.7/44.9 | 52.6/62.4 |
| first tribute us/them | r181/r189 | r191/r189 |
| gem lead at r250/r500/r1000 | +12/+38/+143 | −16/−39/−90 |
| fuelExh us | 4.1 | 12.4 |

## Analysis session

### 1. Did the targeted mechanism change? Yes
- **Claim 2-cycle.** Two-target cycles fell from 5,467 to 169 on big maps and from 1,982 to 328 on mid maps. The champions that used to alternate g8/g9 for 748 rounds on 02tangle B now hold one target. In the v1 and v2 traces of 02tangle B there are 0 cycle turns, and both won 1018-860 against tb (the gate game was L 600-1006).
- **Big-map recovery, which was the stated target.**
  - Against tb_merge_b (the opponent of the original gate): 7/12 on ≥ 8,000 tiles in both v1 and v2, against q24's 2/12. Clears are now even (529:536, against 482:579). Frozen champion-rounds fell from 16,068 to 7,824, below the opponent's 8,018.
  - Over all 19 maps above 3,000 tiles, 26/38 against q24's 17/38.
- **Against q24 itself:** 7/12 on big maps with 564:493 clears.
- **02tangle**, the map family behind most of the deficit: won on both sides in all four untraced screens. q24 lost both sides in the gate.

### 2. Why v2 (iteration 1)
- **What the v1 traces showed.** The remaining cycles were same-target dances that the guard ignored, because an awake camp was in view.
  - The largest: 02cuts A, slots 1-4, all on g8 for **626 rounds** (r1093-1718). The trace shows `aw1`, no enemy, full HP, no damage, `CG0` (never triggered).
  - In q24's own trace the same spot shows shorter g8 cycles (r1415-1522).
- **The v2 change.** v2 stops counting an awake camp as activity. Attacks, damage taken, gem or gold changes and enemies in view still reset the guard.
- **Effect on cycle turns:** all position 2-cycles went from 2,799 to 947 (big) and from 5,170 to 1,450 (mid). Turns with an awake camp in view went from 5,242 to 932.
- **Effect on wins:** v1 and v2 are equal within noise over the three 38-game samples, 75/114 and 74/114.
  - v2 is +1 against tb, +1 traced, and −3 against q24.
  - The v1→v2 flips against q24 were 2 for and 5 against, all chaotic trajectory changes. The placebo report puts differences under about 14 games between two 140-game runs at noise.
  - v2 was chosen on the mechanism metric. I did not iterate a second time, to avoid tuning against the gate sample.

### 3. What the guard is backstopping
I traced the same-target cycle on 02tangle B r62-77 with `dbg_q30bank` (`matches/q30-bank-dbg`, `q30-bank-dbg2`).
- **Setup.** Slots 1 and 3 had just captured g26, standing on its spawn tiles (85,14) and (85,13). They then target g24 at distance 5 or 6.
- **Odd rounds** (at (86,13), d5): the farming code runs `go_to` toward g24's live tiles, and the path leads back over g26's tiles.
- **Even rounds:** play_turn returns before the farming goals. This is consistent with the "never block a camp's respawn" push-off toward `G.center` by Chebyshev distance.
- **The bank decision** was `go=False` with det = 24 throughout, so banking is ruled out.
- **Duration.** In q24 this cycle ran from r63 to r122 (60 rounds, two champions). The guard committed at r69 and banned g24 at r77.
- **Root cause.** This is h_respawnfix's mechanism 1 (`results/simulated-matches/2026-11-01_0126_h_respawnfix/notes.md`), which `c2_respawn` fixes at the root. h_bigmap only bans the target.
- **The 00galaxy A residual.** The 169 two-target turns there in v1 and v2 are a target-independent movement cycle: slot 4 at (28,15)/(29,14), r975-1024. The guard committed to g6, banned it, and then the same two tiles repeated with g7 and then g8. Banning targets does not break a cycle that is not caused by the target.
- **Residual fight standoffs** ("1-target, enemy in view"), for example v1's adgato-gemcombat5 A slot 1:
  - Vendetta at full HP dances (77,79)/(76,79) for 633 rounds against a lone enemy at distance 3-5 with 1,200 HP;
  - `group_balance` is 1.31: below the 1.4 commit threshold and above the 0.75 retreat threshold;
  - nobody attacks;
  - this lives in `handle_enemies`, which the guard's target commitment cannot reach.

### 4. Losses (all 60 classified; the large-map ones read in full)
Classified by digest (kills deficit ≥ 5 or deaths excess ≥ 5 = fight; frozen excess ≥ 600 = freeze; first tribute ≥ 150 rounds later = slow bank; otherwise margin ≤ 150 = close race, else farm race):

| Class | Losses |
|---|---|
| fight | 32 |
| close race | 16 |
| farm race | 8 |
| slow bank | 3 |
| freeze | **1** |

- **Freeze.** The only freeze loss is 01yellow-brick-road B (60-65, frozen 6,510 : 5,834). Both teams froze there. This is the known respawn-rule freeze (Q21), not the claim cycle.
- **Fights dominate.** Losses average 5.2 kills against 12.3. For example 02guardians B was 0-0 with 61 deaths to 1: a gold-tiebreak snowball where seat A wins in both directions. h_bigmap won the A side with 39 kills.
- **Big-map losses against q24** (5 of 12 games):
  - **00ambush A** (fight, 700-1013): first tribute r646 against r187. Seat A of 00ambush banks late in every run of every bot (tb mirror r362, q24 gate r437, here r346-646). This is map geometry, not Q30.
  - **00ambush B** (farm race, 813-1015): led 678-593 at r1500, then lost 153 gems on deaths.
  - **adgato-gemcombat5 A** (455-1022): first clear r209 against r75. A fight map; the v1 game on the same seat was a win (1015-700).
  - **01big-world A** (close race, 891-1003): early 10-gem tributes from r80. Seat A of 01big-world also lost in the q24 gate and against tb in both screens. This is a seat effect, not Q30.
  - **02harvest B** (fight, 906-984): led 355-283 at r1000, then went 0 kills against 8 and lost the late race.
- **Mid-map losses against q24** (13 of 26): close races (02cuts A led 518-418 at r1000; 01islands B; 01concentrated-wealth B) and fights (00ribs A 5:25 kills; 00dunes B; 00expanse B; 02geodes A; 02famine A). None is freeze-class.

### 5. Regressions elsewhere?
- **No size class got worse.** Small maps 60/102, mid 13/26 (even), big 7/12.
  - The economy metrics are better or equal on every class: small maps have clears 58.5 : 54.4, kills 11.9 : 9.3, deaths 10.1 : 12.9. Mid maps are level (gems 760 : 744, clears 50.8 : 49.7).
  - Frozen rounds are lower on every class.
- **Lost both sides** against q24: 00ambush, 00gem-fields, 00lanes, 00monolith, 00pilgrimage, 00rows, 00vault, 01concentrated-wealth, 02cuts, 02uncharted-lands. Mostly fights or close races, with no common mechanism. 00pilgrimage was also lost on both sides in q24's own gate against tb.
- **Possible side effect: more grouping.** On mid maps, allies within distance 6 per champion-turn rose from 0.763 to 0.813 (q24 trace against v2 trace); big maps are unchanged (0.562 and 0.556). The claim fix keeps a weak helper with its strong partner instead of chasing the partner away. This plausibly explains part of the small-map fight gain, but it was not traced on small maps.
- **Unchanged:**
  - **Fuel:** 7.7 against 7.5 fuelExhausted per game.
  - **Turn 1:** the second turn-1 suspension (Q31, `init_gold`'s flood) was not addressed.

### 6. Is the gain an artefact?
- **The mechanism gain is robust.** Two-target cycles fell more than 80% in two independent traced replicates (v1 and v2), matching the counterfactual.
- **Big-map wins against tb** reproduce across replicates:
  - 7/12 in both untraced screens (v1 and v2);
  - 8/12 (v1) and 6/12 (v2) in the traced runs against dbg_tb30, against traced q24's 3/12;
  - 7/12 for the traced counterfactual.
- **The head-to-head result is not certain.**
  - 80/140 is 2 games under the gate, and the 95% Wilson lower bound is 0.489.
  - Most of the margin comes from small maps (60/102), where the targeted cycle was rarer. The mechanism there is plausible but less directly tied to Q30.

## Verdict
**Kept as a component; not promotable on its own.**
- Gate (a) fails: 80W-60L, Wilson lower bound 0.489, botFaults 0. Gates (b) and (c) were not run.
- The mechanism is confirmed and the stated target (the large-map deficit) is fixed:
  - big-map wins against tb went from 2/12 to 7/12;
  - clears went from 482:579 to 529:536;
  - frozen rounds went from 16,068 to 7,824;
  - two-target cycles fell 97% (big) and 83% (mid).
- The paired economy is better than q24 in every size class.
- **Next:** merge `CLAIM_FIX` + `CYCLE_GUARD` (v2) into the next combo, with c2's respawn fix and c3's team clear, and gate that combo.

**Merge notes for c3_teamclear** (shared-memory layout):
- c3 uses `PRESENT_BYTE = 6` as a presence bitmask and writes `DEAD_MARK = 255` into a dead champion's claim byte. Its team-clear count compares `buf[s] == G.idx + 1`.
- In a merge:
  - (i) loop claims over `range(PRESENT_BYTE)`, not `range(FOCUS_BYTE)`, so byte 6 is never read as a claim;
  - (ii) test `DEAD_MARK` before decoding the helper bit (255 would otherwise decode as a helper on group 126);
  - (iii) mask with `& 0x7F` in every other claim comparison, including c3's `near_sh` count;
  - (iv) keep the ≥ 127-group fallback.

## New hypotheses generated
1. **c4 = q24 + respawn fix (c2) + team clear (c3) + claim fix and cycle guard (h_bigmap v2).**
   - *Evidence:* the cycles that h_bigmap's guard has to break are respawn-rule push-offs (02tangle B r62-77 traced; 02cuts A, 4 champions × 626 rounds in v1), which c2 fixes at the source. The guard only bans the target for 30 rounds.
   - *Why:* the three fixes are complementary freeze removals in different code paths. h_bigmap is +10 over the null on its own.
2. **Fight-standoff breaker.**
   - *Evidence:* adgato-gemcombat5 A (v1 trace) has a 633-round standoff between our full-HP Vendetta and a lone 1,200-HP enemy at distance 3-5. `group_balance` 1.31 sits between the 0.75 and 1.4 thresholds; there are no attacks and no damage. "1-target, enemy in view" cycle turns are 839 in v2 and 2,175 in v1.
   - *Proposal:* after N quiet turns in that band, commit if the ratio is above 1, otherwise disengage and farm.
   - *Why:* it is the largest remaining class of 2-cycle turns, and the fight branch returns before any target logic.
3. **The cycle guard should perturb movement when a ban does not help.**
   - *Evidence:* 00galaxy A (v2 trace), slot 4 at (28,15)/(29,14). Banning g6, then g7, then g8 left the same two-tile cycle running for 50 rounds.
   - *Proposal:* when the position pair repeats after a ban, mark the pair as no-enter for pathing for about 20 rounds instead of banning more groups.
   - *Why:* target-independent movement cycles exist, and bans cost good targets.
4. **Late-race protection on big maps.**
   - *Evidence:* 00ambush B led 678-593 at r1500 and lost after 153 gems died with carriers. 02harvest B led 355-283 at r1000 and lost the late race with 0 kills against 8. 32/60 gate losses are fight-class.
   - *Proposal:* bank before engaging when carrying 15 or more gems after r1000.
   - *Why:* leads built by the farming fix are being given back in late fights.
5. **Seat-specific big-map losses** (01big-world A, 00ambush A).
   - *Evidence:*
     - 01big-world seat A lost in the q24 gate (749-1004), in both h_bigmap screens against tb (816-1013, 859-1005) and against q24 (849-929, 891-1003), with first tributes of 10 gems at r80;
     - 00ambush seat A banks first at r281-646 in every run of every bot.
   - *Why:* a consistent seat effect across bots suggests a geometry problem: altar choice or a guarded path. One traced study per seat would identify it.
6. **Q31 (unchanged) is still open:** move `init_gold`'s `reachable_tiles` flood out of turn 1. h_bigmap still has the second turn-1 suspension on the 100×100 maps.
