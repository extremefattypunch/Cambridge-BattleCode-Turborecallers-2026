# Experiment: h_shortcut (2026-11-01)

V3L-2, "the 01shortcut stuck champion". The root cause was found by trace and fixed generally (keyed on walk components). The fix is confirmed by flag-off controls.
**The gate fails head-to-head (72/140 vs c2_respawn)**, because the fix fires in about 1.4% of games. h_shortcut is a merge component, not a submission.

## Hypothesis
- **What.** A champion idles with 0 gems for 1,300-1,700 rounds on 01shortcut, which costs 25% of a 4-pick team.
  Find why, and fix it generally (no map names; qualifiers use unseen maps).
- **Source.**
  - `results/experiments/2026-11-01-v3-ladder-study.md` (V3L-2) and STRATEGIES V3L-2.
  - On the ladder, v3 went 0-3 on 01shortcut: 378-773, 476-531, 714-1015 vs Spawn Campers (v2 had won 1168-441 there). Since then v3 also won e701a61e, so it is 1-3.
  - Ladder stats (`tools/freeze_metric.py`):

| Ladder game | Our champion | Idle stretch |
|---|---|---|
| 2ec1835b (B) | Vendetta | r288-2001, with 0 gems |
| add2d07e (A) | Vendetta | r652-2001 |
| 71997673 (A) | Vendetta | r257-428 and r1072-1235 |

  - In 2ec1835b and add2d07e, every idle stretch starts right after a run of +20 monster damage taken per round, which is wolf hits.
  - `tools/lowhp_freeze.py` over all 9 ladder 01shortcut games (`results/ladder-games.jsonl`, `matches/ladder/summary`):
    - **3 games have a champion idle at low HP until the end:**
      - 2ec1835b (v3, L): Vendetta r288-2001;
      - add2d07e (v3, L): Vendetta r652-2001;
      - **dbe2c4a0 (v4 = c2_respawn, W 1006-463 vs Full Damage): Heart of Ruin r479-1999, carrying 11 gems.** The live champion has the bug on the real ladder.
    - **2 more have shorter low-HP idles:** 71997673 (Vendetta, 171 rounds, 21 gems) and db7dd19f (Marcella, 226 rounds).
- **Still present in the champion c2_respawn locally.**
  - `skc2-vs-tbm-all` 01shortcut__A: Vendetta r640-2001.
  - `skc2-lad-ns` 01shortcut__A: Vendetta r623-2001, carrying 9 gems.
  - Older reproductions: `gate-q24-all` 01shortcut__B, Vendetta r886-1596; `b1-tb_merge_b-mirror-all` 01shortcut__A, Vendetta r1059-2001.

## Root cause (traced)
`play_turn_main`, block "recall to heal / shop when safe". It runs when no camp is hitting us and we are not on spawn:

```python
low = hp < maxhp * 0.45
if (low or rich) and spawn_d > 6 and self.recall_safe(me, enemies):   # spawn_d = CHEBYSHEV distance
    me.recall() ...
elif low:
    self.step_toward(me, self.spawn)   # result ignored
    return
```

01shortcut has a hole-ringed island at x 10-19, y 31-34 for team A (mirrored at y 5-8 for B). It is walk component #2, 23 tiles.
It holds group 8: 2 wolves at (15,33) and (16,33), plus 2 gold clusters. Our spawn is 5-7 tiles away by Chebyshev distance.
1. Vendetta and HoR (Dash 2), and Marcella (TP crystal), cross onto the island and farm the wolves down to low HP.
2. A low champion takes the `elif low` branch.
3. `step_toward` cannot reach the spawn from another walk component, so it returns False and the turn ends.
4. With `spawn_d <= 6` the recall above never fires, and HP never regenerates off-spawn, so every later turn repeats.

**Trace evidence.**
- **The trace bot.** `bots/dbg_cut_trace` is c2_respawn plus a fuel-free `debug_block` trace.
  - **Run.** `tools/onslurm.sh -c 2 ... ./cli/cambc run dbg_cut_trace tb_merge_b --map 01shortcut -o matches/v3l2-trace-a`.
  - **Reproduced byte-for-byte:** 792-669, and the same freeze stretches as `skc2-vs-tbm-all` 01shortcut__A.
- **Vendetta, every turn from r650 to r2000:** `T r1000 2 @16,32 al1 hp220/1000 gems0 ... tgt[g8@16,33 st0 hpl120 alive[(14, 33)] d1] ... comp2/23 ... | start observe ward threats lock alerts danger he_none`.
  - The trail ends at `he_none`, so the turn returned inside the `low` branch, before `pm("recall")`.
  - Only the 120-HP gold cluster (14,33) is still alive. A healthy champion would kill it in 2 hits.
- **Perturbed build.** A second trace build that printed every turn (`matches/v3l2-trace-a2`) took a different trajectory.
  It stranded **two** champions on the same island from r615 to r2000: Marcella at 380/1400, and HoR at 380/1000 carrying 13 gems.

## Setup
- **Candidate:** `bots/h_shortcut`, forked from the champion `c2_respawn` (website v4). The final version is v2.
- **v1** (`SHORTCUT_FIX`): in the `elif low` branch, if `step_toward` fails, recall when `recall_safe`.
  - Source is at `/tmp/claude-69101/-n-home05-ianpoon-Cambridge-BattleCode-Turborecallers-2026/5245ba49-8b5b-4d9a-9345-708126bcbea8/scratchpad/h_shortcut_v1_bot.py` (scratch).
- **v2, final** (+ `SHORTCUT_FAIL_TURNS = 3`): recall only when it is structurally needed:
  - **at once** if our spawn is not in the champion's walk component, `(self.spawn & self.comp_of(pos)).is_empty()`;
  - **otherwise** after 3 failed steps home in a row (`home_fail`, `home_fail_rnd`, updated only on the failed-step path);
  - still only when `recall_safe`;
  - a one-turn block keeps c2's wait.
- **Size.** 2,776 → 2,808 lines. `main.py`, `draft.py` and `randomness.py` are byte-identical to c2_respawn's. See `bots/h_shortcut/NOTES.md`.
- **Controls (new method).** `bots/h_shortcut_off` (v1) and `bots/h_shortcut_off2` (v2) are byte-identical to the candidate except for `SHORTCUT_FIX = False`.
  - They have the same module size, so they spend the same fuel until the patched branch runs.
  - So *candidate vs control* differs **only** in games where the fix fired.
  - `tools/firstdiff.py` gives the first round where the games diverge.
- **Opponents.**
  - Champion `c2_respawn`, for the gate head-to-head.
  - `tb_merge_b`, the ladder hedge (c2 scored 98/140).
  - `lad_vcst`, a ladder-comp imitation (it showed the bug in `skc2-lad-ns`), used in the screen.
- **Screen maps (11).** 01shortcut, plus every map with a low-HP idle of 150+ rounds for us in any c2 all-maps run: 01yellow-brick-road, 02fields, 00split, 00great-wall, 00quadrants, 02crossing, 02harvest, 00gem-fields, 00the-line, 01broken-curve.
- **New analysis tools.**
  - `tools/lowhp_freeze.py`: frozen stretches that *start* at low HP. The HP deficit is damage taken − healing received − shielding since the last death; "low" means a deficit ≥ 50% of base HP. This is the V3L-2 signature.
  - `tools/firstdiff.py`.

## Results
Screen (v1), 11 maps × both sides (`matches/hsc-scr-*`):
```
SUMMARY h_shortcut vs c2_respawn: 10W-12L (45%)  avg gems 802 vs 874  avg deaths 12.5 vs 10.7  botFaults(A) 0
SUMMARY h_shortcut vs tb_merge_b: 15W-7L (68%)  avg gems 881 vs 703  avg deaths 11.4 vs 12.2  botFaults(A) 0
SUMMARY h_shortcut vs lad_vcst: 20W-2L (91%)  avg gems 951 vs 501  avg deaths 6.4 vs 24.5  botFaults(A) 0
```
On the same map-sides, c2_respawn scored 15/22 vs tb_merge_b (`skc2-vs-tbm-all`) and 16/18 vs lad_vcst (`skc2-lad-ns`, only 18 overlap).

v1, all maps (`matches/h_shortcut-v1-all`, `h_shortcut-v1-tbm-all`), with the v1 controls:
```
SUMMARY h_shortcut vs c2_respawn: 70W-70L (50%)  avg gems 688 vs 712  avg deaths 10.7 vs 10.0  botFaults(A) 0
SUMMARY h_shortcut vs tb_merge_b: 99W-41L (71%)  avg gems 784 vs 557  avg deaths 9.7 vs 13.9  botFaults(A) 0
SUMMARY h_shortcut_off vs tb_merge_b: 100W-40L (71%)  avg gems 787 vs 550  avg deaths 9.4 vs 13.9  botFaults(A) 0
SUMMARY h_shortcut_off vs c2_respawn: 70W-70L (50%)  avg gems 694 vs 699  avg deaths 10.3 vs 10.4  botFaults(A) 0
```

**v2 (final), all maps.** Gate head-to-head `--tag h_shortcut-all`, ladder hedge `--tag h_shortcut-tbm-all`, and the v2 controls:
```
SUMMARY h_shortcut vs c2_respawn: 72W-68L (51%)  avg gems 704 vs 694  avg deaths 10.3 vs 10.5  botFaults(A) 0
SUMMARY h_shortcut vs tb_merge_b: 98W-42L (70%)  avg gems 764 vs 566  avg deaths 9.7 vs 13.6  botFaults(A) 0
SUMMARY h_shortcut_off2 vs tb_merge_b: 98W-42L (70%)  avg gems 763 vs 567  avg deaths 9.7 vs 13.5  botFaults(A) 0
SUMMARY h_shortcut_off2 vs c2_respawn: 71W-69L (51%)  avg gems 704 vs 695  avg deaths 10.2 vs 10.5  botFaults(A) 0
```
- **Head-to-head vs c2.** 72/140, A 34 + B 38, Wilson lower bound 0.432. **Gate (a) fails** (it needs ≥ 82). botFaults 0.
- **Ladder hedge.** 98/140 vs tb_merge_b, equal to c2's 98.
- **Release mode** (`matches/h_shortcut-release`, 01shortcut, h_shortcut as A vs tb_merge_b):
  - W 1020-515, identical to the debug-mode game;
  - 0 crashes;
  - team stdout and debug log 0 bytes.
- **Gauntlet.** Not run, because (a) fails.

## Analysis session

### 1. Where the fix fires: control-isolated (v2)
Candidate vs flag-off control, same opponent: games that differ at all.

| Opponent | Game | Control (c2 logic) | h_shortcut v2 | First divergence | Our frozen champion-rounds, control → fix |
|---|---|---|---|---|---|
| tb_merge_b | 01shortcut A | W 792-669 | **W 1020-515** | r645 Vendetta healingReceived (recalled, healed) | 1,787 → 601 |
| tb_merge_b | 01shortcut B | L 881-934 | L 813-920 | r517 Vendetta spentGold (recalled, shopped) | 490 → 332 |
| c2_respawn | 01shortcut B | L 768-1019 | **W 821-686** | r619 HoR spentGold | 1,644 → 1,193 |
| c2_respawn | 02the-pond A | L 455-761 | L 406-912 | r673 Vendetta healingReceived | 0 → 0 |

- **How often it fires.** The fix fires in **4 of 280 games**, 3 of them on 01shortcut. Results go from 1W-3L to 2W-2L: +1 vs c2 (72 vs 71), 0 vs tb_merge_b (98 vs 98).
- **01shortcut A vs tb_merge_b.**
  - Vendetta collects 258 gems instead of 51; she was stuck r640-2001 in the control.
  - Clears rise from 47 to 68 and gold from 4,343 to 7,253.
- **01shortcut B vs c2.**
  - HoR's idle r614-1569 (955 rounds, carrying 11 gems) disappears.
  - HoR collects 181 gems instead of 88 and tributes 156 instead of 34.
  - c2's own HoR is now the one stuck (r1159-2001).
- **The other two games** (01shortcut B vs tb_merge_b, 02the-pond A vs c2) are fight-decided losses either way.
  - 01shortcut B: K/D 5/9, Vendetta 2/5.
  - 02the-pond A: 15 → 22 deaths to champions, at 0 camp deaths.

### 2. Signature search over all 70 maps, before vs after
`tools/lowhp_freeze.py --min 300`: idle ≥ 300 rounds that start at low HP, for our side.

| Run (140 games unless noted) | Before (c2 logic) | After (h_shortcut v2) |
|---|---|---|
| vs tb_merge_b (`h_shortcut_off2-tbm-all` → `h_shortcut-tbm-all`) | 1,773 in 2 games: **01shortcut A Vendetta r640-2001**; 00great-wall B Marcella r1555-1967 | 412 in 1 game: 00great-wall B Marcella (unchanged) |
| vs c2_respawn (`h_shortcut_off2-c2-all` → `h_shortcut-all`) | 955 in 1 game: **01shortcut B HoR r614-1569** | **0** (c2, as "them": 955, 01shortcut A HoR) |
| vs lad_vcst (`skc2-lad-ns`, 100 games → v1 screen, 22) | **01shortcut A Vendetta r623-2001**; 00split B Vesper r312-779 | 0 |

**V3L-2 stalls of 900+ rounds on 01shortcut** (bold above): 3 → **0**.

**The others are not V3L-2.** In each of these the patched branch never runs: the fix-on and flag-off games are identical, so the bot's own `low` flag plus a failed step never happened.
- **00great-wall B Marcella** (vs tb_merge_b).
- **02fields B HoR r559-1465** (from `gate-c2-all`): re-run vs q24_combo with and without the fix (`matches/v3l2-q24-on`, `v3l2-q24-off2`), 356-1000 both ways, identical games.
- **Traced false positives.** Health shards raise max HP, so these champions were never below 45% by the bot's own measure (traced with `bots/dbg_cut_trace2`, `matches/v3l2-trace-gw|line|bc`, each a byte-identical reproduction):
  - 00great-wall A Ryth;
  - 00the-line B Vendetta;
  - 01broken-curve B Vesper.
- **Unclassified.** `gate-c2-all` 01yellow-brick-road B Ryth r535-1976 (vs q24) did not reproduce. The re-run diverged by module size, and neither re-run shows a low-HP idle.

Total frozen champion-rounds (`freeze_metric`, ≥ 150 / ≥ 300 rounds, ours):

| Opponent | Before | After |
|---|---|---|
| tb_merge_b | 60,134 / 44,049 | 58,790 / 42,688 |
| c2 | 48,628 / 34,511 | 48,177 / 33,556 |

The whole difference is in the 4 games where the fix fired.

### 3. v1 → v2 (why the refinement)
- **What v1 did.** v1 recalled on *any* failed step home. The v1 controls show it fired in 5/140 games vs tb_merge_b and 10/140 vs c2. Most of those were one-turn blocks by a unit, not islands.
- **01elk-arena B vs tb_merge_b.** The control walked home next turn and healed at r242; v1's recall healed at r246.
- **02the-pack A and 00corners A vs c2** (traced with `bots/dbg_cut_trace3`, reproduced exactly):
  - v1 fired once on a single failed step while walking home, at r162 and r544 respectively, with an enemy at distance 6. That is a risky moment to start a 5-turn channel.
  - The large control freezes there (Marcella r1240-1973; HoR and Ryth r990-1563) involve no low-HP turn at all.
  - So v1's bigger freeze reduction (−5,538 vs c2, −4,055 vs tb_merge_b) is downstream trajectory change, not mechanism.
- **Result.** v2 fires only in the structural case. Its 4 firings are all the island or a persistent block.

### 4. Why raw comparisons with c2 mislead here (module-size chaos)
- **Against tb_merge_b**, 125 of 140 h_shortcut-v1 games are byte-identical to c2's (`skc2-vs-tbm-all`). Of the 15 that differ, only 5 are fix firings.
- **The 01shortcut and 01yellow-brick-road games diverge at r2-4,** before any champion can be low (`tools/firstdiff.py`). The bigger module changes turn-1 fuel there.
  - This is how v1's 01shortcut A went "W 792-669 → L 676-925" in the screen; that game was chaos, not the fix.
  - The v2 control happens not to diverge on 01shortcut, so its games equal c2's.
- **Against c2, 64 of 70 maps are mirror-identical in v2,** so side bias decides them: exactly 1 win per map.
  - Of the 6 maps that changed, 4 also change in the control (00lanes, 01big-world, 01yellow-brick-road, adgato-gemcombat5), so they are chaos.
  - That leaves 2 fix games.
- **Consequence for the gate.** A fix that fires in 1-2% of games cannot reach 82/140 on its own. The placebo floor (66-68/140) dwarfs it.

### 5. Losses
- **The v2 head-to-head is a near-mirror.**
  - 68 losses: 64 are side-bias halves of mirror-identical maps.
  - The rest are 01big-world, 01yellow-brick-road, 00lanes and adgato-gemcombat5 (chaos, see §4), plus 02the-pond A (fight).
- **01shortcut still has a non-V3L-2 stall:** 01shortcut A vs tb_merge_b, Vendetta r184-410.
  - She carried 23 gems for about 225 rounds. Her route was (12,36) → (2,34) → (7,18) → (32,19) → (26,12) → (36,12) → (29,31), and she tributed at our altar (32,27) at about r425.
  - The enemy-side altar (32,12) is locked by tb_merge_b, which we only learn on sight.
  - Our own altar carried the +12 `ALTAR_DANGER_PEN` because an enemy had been seen near it at r246.
  - See V3L-2b below.

## Verdict
**kept, as a merge component; not promotable alone.**
- **Mechanism confirmed.** The root cause was traced, and the fix is keyed on walk components, not map names.
- **Effect.** It removes every V3L-2 stall in the all-maps runs (3 → 0) and turns one control loss into a win (01shortcut B vs c2).
- **No measured cost.** 98 = 98 vs tb_merge_b, 72 vs 71 vs c2, release clean, botFaults 0.
- **Gate (a) fails:** 72/140, LB 0.432. The fix fires in about 1.4% of local games, so it should ride along in the next merged candidate (and in `bots/cpp_port`) rather than be uploaded alone.
- **Ladder relevance.** v3 went 1-3 on 01shortcut on the ladder, and two of its three losses had a champion stuck at low HP to the end.
  The live v4 still stalls a champion for 1,520 rounds there (dbe2c4a0).
  5 of 9 ladder 01shortcut games carry the low-HP idle signature.

## New hypotheses generated
- **V3L-2b: altar-lock trip.** Carriers walk 100-200 rounds to an enemy-side altar that turns out to be locked.
  - *Evidence:* 01shortcut A vs tb_merge_b, Vendetta carrying 23 gems r184-410 (`matches/v3l2-trace-a`). The lock is only learned on sight, and the danger penalty pushed her off our own altar.
  - *Change:* treat altars on the enemy's side (`lock_side`) as probably locked once any enemy lock has been seen, or share seen locks via a spare shared-memory bit.
- **V3L-2c: low-HP carrier flip-flop near an altar.** The `low` branch needs `incoming == 0`. On a camp's range edge, incoming toggles each turn, so the champion alternates between "walk home" and "walk to the altar".
  - *Evidence:* `matches/v3l2-trace-b`, Vendetta r836-861 at (26,10)/(26,11), HP 400 → 160, carrying 18 gems.
  - *Change:* a low carrier next to a usable altar tributes first (tribute isn't interrupted by damage), and the `low` decision becomes sticky for a few turns.
- **V3L-2d: island farming safety.** On a hole-ringed island the only escape from a bad fight is a 5-turn recall, but `choose_target`'s safety model assumes walk-away retreats.
  - *Change:* add the recall time to the safety budget for groups outside our spawn's walk component, and finish 0-strength clusters (the 120-HP gold cluster left at (14,33)) before recalling.
- **Q23 support (turn-1 fuel chaos).** A 30-line change made 01shortcut and 01yellow-brick-road diverge at r2-4. That is more evidence that keeping turn 1 fuel-identical (map analysis in the draft) would make local A/B tests far less noisy.
- **Method: flag-off control builds for rare-trigger fixes.** Compare the candidate with a byte-identical build that has the flag off. This isolates the causal games: 4 of 280 here, against 16-20 changed games vs the old champion. Worth adding to LOOP.md §3 as the standard analysis for bug fixes.

Artifacts:
- **Match directories:** `matches/v3l2-trace-*`, `hsc-scr-{c2,tbm,lad}`, `h_shortcut-v1-all`, `h_shortcut-v1-tbm-all`, `h_shortcut_off-tbm-all`, `h_shortcut_off-c2-all`, `h_shortcut-all`, `h_shortcut-tbm-all`, `h_shortcut_off2-tbm-all`, `h_shortcut_off2-c2-all`, `v3l2-q24-on`, `v3l2-q24-off2` and `h_shortcut-release`.
- **Debug bots:**
  - `bots/dbg_cut_trace`: c2 plus a full trace;
  - `bots/dbg_cut_trace2`: v1 plus a low-HP trace;
  - `bots/dbg_cut_trace3`: the v1 control plus a low-HP trace.
