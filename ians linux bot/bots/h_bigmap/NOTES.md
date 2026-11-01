# h_bigmap: STRATEGIES Q30 (claim 2-cycle fix + universal 2-cycle guard)

**Lineage.** `tools/newbot.py q24_combo h_bigmap`; only `src/bot.py` changed (every change is behind
`CLAIM_FIX` / `CYCLE_GUARD`; no map names). Report: `results/simulated-matches/2026-11-01_0437_h_bigmap/notes.md`.
Diagnostic twins (trace-only, fuel-free `cambc.debug_block` dumps): `bots/dbg_hbig` (v1),
`bots/dbg_hbig2` (v2 = this bot + trace), `bots/dbg_q30bank` (one-off goal/bank prints, 02tangle r60-130).

| Switch | Value | What it does |
|---|---|---|
| `CLAIM_FIX` | True | Claim byte at the champion's slot: low 7 bits = group idx + 1, bit 7 = "joining, I cannot solo this group" (`write_claim(..., helper=not self.best_solo)`). `read_claims` returns the claim count and fills `self.claim_help` (helper count per group). In `choose_target` the split-farm `x0.3` for a solo-capable chooser applies only when `c > helpers` (some claimant can solo it). Helpers still add 55 dps each; non-solo choosers keep `x1.2`. Maps with >= 127 groups keep the old byte. FOCUS_BYTE 7 untouched. |
| `CYCLE_GUARD` | True | `cycle_guard()` runs every turn after `threats()` in every branch. History of the last 4 (turn-start position, target idx); a turn with an attack (`cg_act`), damage taken, gem change, gold gain or an enemy in view resets it, as does a skipped turn. Trigger: `CYCLE_POS_TURNS`=6 consecutive pos[t]==pos[t-2]!=pos[t-1], or target A,B,A,B for `CYCLE_ALT_TURNS`=4 turns. On trigger: commit to the current target for `CYCLE_COMMIT`=40 rounds (claim multipliers ignored, committed group x`CYCLE_SWITCH`=1.5 instead of the x1.3 current-target bonus, exempt from bound pruning; commit dropped if another group still wins or the group becomes invalid). A second trigger on the committed group bans it for `CYCLE_BAN`=30 rounds. |
| `CYCLE_AWAKE_ACT` | False | v2. v1 (True) also treated "an awake camp in view" as activity; its traces showed the residual cycles were same-target dances next to an awake camp that hit nobody (02cuts A: 4 champions x 626 rounds), so v2 dropped it. |

**Iterations (screens on the 19 maps > 3,000 tiles, both sides, 38 games each).**
- v1: vs q24_combo 23W-15L, vs tb_merge_b 25W-13L; traced vs dbg_tb30: two-target cycles big 205 / mid 241 (q24 5,467 / 1,982), all position 2-cycles 2,799 / 5,170.
- v2 (final): vs q24_combo 20W-18L, vs tb_merge_b 26W-12L; traced: two-target 169 / 328, all position 2-cycles 947 / 1,450.

---

(Inherited q24_combo notes follow.)

# q24_combo: STRATEGIES Q24 combined candidate

**Lineage.** `tools/newbot.py tb_merge_b q24_combo`, then four batch-1 patches ported in this order:
1. h_3pick (lock-memory fix only)
2. h_goldtie v2
3. h_earlyfight_all (v3)
4. h_fightfuel

Each patch scored 52-58% alone vs tb_merge_b on 40 sprint games. Each one keeps its original switch names and values, and no diagnostic output is on.

| File | Change |
|---|---|
| `src/bot.py` | All four patches plus the integration below (2,697 lines; tb_merge_b has 1,935) |
| `src/main.py` | Identical to h_fightfuel's: profiler hooks are no-ops with `PROF = False`, and the traceback runs only with `Bot.debug_tb` (False) |
| `src/draft.py`, `src/randomness.py` | Identical to tb_merge_b. No source changed them |

**How the merge was checked.**
- **Function by function.** Every function in `bot.py` is byte-identical to the one source that changed it, except the functions two or more patches touch: `Bot.__init__`, `init_static`, `pick_altar`, `retreat`, `retreat_fast`, `handle_enemies` and `play_turn`. Each of those was diffed against tb_merge_b and contains every hunk of every patch.
  - `init_gold` and `do_tribute`/`break_lock` differ only by the switches listed below.
- **Constants.** Every module constant a patch adds or changes has the source's value. h_3pick's 17 trio constants are deliberately not ported.
- **Static checks.** `py_compile` passes on all four files. There are no undefined globals (symtable), and no `self.` attribute is read without being assigned.

## Patches and switches
| # | Source | Switches (value) | What it does |
|---|---|---|---|
| 1 | h_3pick ("L") | `LOCK_MEMORY_FIX = True` | `pick_altar` refreshes `locked_altars()` and skips altars remembered as enemy-locked, not only locks in vision. This fixes the 2-cycle that froze carriers (01broken-curve, 02the-pond). Trio mode (`TRIO_MODE`, alerts, assist, commitment) is **not** ported: it was rejected and inert with `TRIO_MODE = False`. |
| 2 | h_goldtie v2 | `GOLD_GUARD_STR = 200`, `GOLD_GUARD_HP = 15000`, `GOLD_STALL_ROUND = 300`, `GOLD_IDLE_TURNS = 12`, `GOLD_CHIP_CYCLES = 30`, `TREASURE_ITEMS` | `init_gold` detects `no_tribute` statically (guard groups) and sets `altar_ok`. Under `no_tribute`: gold value, guard value 0, no banking, Treasure first, and gems are ignored in the fight and recall models. `stalled` (r300+, 0-0) turns on gold play: the respawn-rule fix and chip mode. |
| 2a | (new, diagnostic) | `GOLD_LOG = False` | h_goldtie printed `GOLDTIE no_tribute ...` on slot 0 at init in every game. That print is now behind this switch and off. |
| 3 | h_earlyfight_all (v3) | `EARLY_ROUNDS = 2000` (the rule runs all game), `GROUP_R = 7`, `GROUP_ADV = 1.4`, `GROUP_DISADV = 0.75`, `GROUP_ENGAGE_BONUS = 0.4`, `GROUP_REGROUP_D = 4`, `GROUP_ADV_R = 4`, `GROUP_BONUS_D = 2`; `DIAG = False`, `DIAG_UNTIL = 320` | `group_balance()` scores the local fight as (sum hp × sum dps) ours / theirs. **Advantage:** commit (engage bonus, stand and trade). **Disadvantage:** no new fights; regroup with `retreat(..., rally)` toward visible allies; `hit_while_leaving`. |
| 4 | h_fightfuel | `OBSERVE_FAST`, `THREATS_FAST`, `RETREAT_FAST`, `KIT_FAST` = True; `FUEL_RETREAT_DASH = 350000`, `FUEL_KIT_AIM = 400000`; `VALIDATE = False`, `PROF = False`, `PROF_MIN = 1500000`; `Bot.debug_tb = False` | Bitboard `observe`, awake-only `threats` with a per-turn enemy cache (`self.esrc`), `retreat_fast` (cached sources, memoised scoring, no dash search under 350k fuel), `kit_units_fast` and `reset_target_fast`. `pm()` profiler checkpoints are no-ops. |
| I | (new, integration of 1+2) | `TRIBUTE_USABLE_ONLY = True` | See conflict C1. |

`DEBUG = False` (unchanged).

## Overlaps and how they were resolved
**C1. `pick_altar` / `do_tribute` (patches 1 and 2).**
- *Changes to `pick_altar`.* Both patches add a `continue` to its loop: h_3pick skips remembered-locked altars, and h_goldtie skips `i not in altar_ok`. Both are kept, so an altar is a candidate only if it is usable, not remembered-locked and not locked in vision. The order doesn't change the result.
- *The gap.* When every usable altar is locked, `pick_altar` returns `(BIG, None)` and `do_tribute(me, None)` falls back to `self.altar_ring`. Its `free` ring and `break_lock`'s "free altar within 8" test scan **all** altars, so on a map with some guard-only altars the fallback could send a carrier into a guard ring. That is the 02the-pack stall that h_goldtie removed from `pick_altar`.
- *Fix.* `init_gold` sets `tribute_altars` / `tribute_ring` to the usable altars only when **some but not all** altars are guard-only. Otherwise they are `self.altars` / `self.altar_ring`, so the code is byte-for-byte equivalent to the sources.
  - On all 70 local maps it is a no-op: h_goldtie's static check marks every altar usable on 67 maps and none on 3, and with `no_tribute` `do_tribute` is never called.
  - The submit-if-adjacent loop at the top of `do_tribute` still checks every altar, since standing next to one means it is reachable.
- *Other altar uses* (`try_lock`, wards, alerts, static fields) are unchanged.

**C2. `retreat` signature (patches 3 and 4).**
- *The clash.* h_earlyfight added `rally=None`: the last tie-break is the distance to the nearest visible ally instead of our spawn. h_fightfuel added `dry=False` (its VALIDATE harness) and routes every call to `retreat_fast`, which scores the spawn distance from a static per-tile memo (`self.spawn_cd`).
- *A textual merge would be wrong.* It would have silently dropped the rally in the fast path, because `retreat_fast` always used spawn distances.
- *Resolution.* The signatures are now `retreat(me, awake, enemies, rally=None, dry=False)` and `retreat_fast(me, awake, enemies, rally=None, dry=False)`.
  - With `rally`, `retreat_fast`'s 4th key is `min(cheb(p, t) for p in rally)`. This is exactly the slow `retreat`'s `spawn_pts = rally if rally else self.spawn_pts`.
  - The rally distance is memoised only per call (`memo`), **never** written into the static `spawn_cd`, because the rally points change every turn.
  - The VALIDATE harness passes `rally` to both versions, by keyword.
  - The play_turn danger-retreat passes no rally, so it uses the spawn memo as in h_fightfuel.

**C3. Caches vs later readers (patch 4 vs 2 and 3).** h_fightfuel's only per-turn cache is `self.esrc`: enemy position, range and strength, filled by `threats_fast`. Its readers:
- **`retreat_fast` (the only reader).** Every call site, play_turn's danger retreat and `handle_enemies`, runs after `threats()` in the same turn.
- **Static caches.** `camp_rng` (camp range per spawn tile) and `spawn_cd` are built in `init_static` and are valid all game. `retreat_fast`'s `memo` and `kit_units_fast` are per call.
- **Defensive invariant.** `play_turn` now clears `self.esrc = None` at the start of every turn, so no future path can read last turn's positions. With `esrc` None, `retreat_fast` reads live data, so this changes nothing today.
- **h_earlyfight's `group_balance()` and `hit_while_leaving()`** read live API data (ally and enemy position, health, strength, focus, channel state), not the cache, so they always see the current turn. The `near` list they get is built from live reads in `handle_enemies`. h_fightfuel did not change that part.
- **h_goldtie's code** reads only `G.status` from `observe()` (`blocks_respawn`). `observe_fast` sets the same statuses: VALIDATE in h_fightfuel showed 0 mismatches. It also reads live gem and gold counts.

**C4. `handle_enemies` (patches 2, 3 and 4).** These merged without conflict:
- h_goldtie: `gems = 0` under `no_tribute`, so `rich` is False;
- h_earlyfight's adv/dis logic then overrides `clearly_losing`;
- h_goldtie's `focus_bias` zeroes enemy gems, so the target key's gem term is 0 under `no_tribute`;
- h_fightfuel only adds `pm()` checkpoints, including around the regroup `retreat` call.

**C5. `play_turn` (patches 2, 3 and 4).** The order is:
1. `observe`, then `pm("observe")`;
2. h_goldtie's stall check (as in h_goldtie, before the channel early return);
3. `threats`, then the profiler tag;
4. h_earlyfight's `DIAG` hook (off).

The remaining changes (h_goldtie `carried`, `no_tribute` banking, chip mode, `blocks_respawn`, and h_fightfuel `pm`) don't overlap.

**C6. Turn 1.** `init_static` now runs h_fightfuel's `camp_rng` loop, then h_goldtie's `init_gold`. That is one `reachable_tiles` call plus a loop over the altars.

## Smoke results (merge check only, not evidence of strength)
The smoke games check the merge, not strength. The q24 games diverge from each source's games from turn 1, so a per-game comparison shows each mechanism's *signature*, not its effect size. Strength needs the LOOP.md §4 gate.

**Runs.**
- One onslurm job on the test partition, 56769983, exit 0: 30 games, folders `matches/q24-smoke-*`.
- Source numbers on the vs-tb_merge_b maps come from the existing `matches/b1-<source>-all` runs.
- Three local debug games came from a throwaway instrumented copy (counters plus `GOLD_LOG`). It has since been deleted; the replays are in `matches/q24-dbg-{dunes,curve,pack}`.

**Local check.** `cambc run q24_combo tb_merge_b --map 00anvil` (`matches/q24-local`) won 996-400. It had 0 crashes, empty stdout (no `bot error` lines) and no stderr file. fuelExhausted was 0 for q24_combo and 5 for tb_merge_b.

**Exact SUMMARY lines:**
```
SUMMARY q24_combo vs imit_test: 4W-0L (100%)  avg gems 986 vs 334  avg deaths 2.8 vs 16.5  botFaults(A) 0      [01broken-curve,02the-pond; q24-smoke-lock]
SUMMARY h_3pick vs imit_test: 3W-1L (75%)  avg gems 790 vs 342  avg deaths 2.2 vs 17.0  botFaults(A) 0        [same maps; q24-smoke-lock-src]
SUMMARY tb_merge_b vs imit_test: 1W-1L (50%)  avg gems 756 vs 672  avg deaths 4.5 vs 22.0  botFaults(A) 0     [01broken-curve; q24-smoke-lock-base]
SUMMARY q24_combo vs tb_merge_b: 8W-0L (100%)  avg gems 3 vs 0  avg deaths 1.2 vs 11.0  botFaults(A) 0        [01boss-battle,02guardians,02the-pack,01yellow-brick-road; q24-smoke-goldfuel]
SUMMARY q24_combo vs sf_bank: 4W-0L (100%)  avg gems 1002 vs 204  avg deaths 9.5 vs 30.8  botFaults(A) 0     [00dunes,01starfish; q24-smoke-early]
SUMMARY h_earlyfight_all vs sf_bank: 4W-0L (100%)  avg gems 927 vs 144  avg deaths 16.8 vs 32.8  botFaults(A) 0 [same maps; q24-smoke-early-src]
SUMMARY tb_merge_b vs sf_bank: 3W-1L (75%)  avg gems 836 vs 345  avg deaths 16.0 vs 25.8  botFaults(A) 0      [same maps; q24-smoke-early-base]
```

### Patch 1: lock-memory fix (vs imit_test)
"Frozen" is h_3pick's metric: champion-rounds with 15 or more carried gems unchanged for 150+ rounds, taken from the `gems` timeline.

| Game | tb_merge_b | h_3pick | q24_combo |
|---|---|---|---|
| 01broken-curve B (the traced bug) | L 381-1013, frozen 1638 | W 1183-525, frozen 0 | **W 1168-488, frozen 0** |
| 02the-pond A (the traced bug) | L 15-77, frozen 3162 (`g-tb_merge_b-vs-imit_test`) | W 262-91, frozen 1147 | **W 1007-0, frozen 0** |
| 01broken-curve A | W 1130-331, frozen 0 | L 702-738, frozen 202 | W 1012-510, frozen 0 |
| 02the-pond B | W 1014-15 | W 1014-15 | W 756-339 |

- **Reproducibility.** h_3pick reproduced its NOTES numbers exactly on the cluster (1183-525 and 262-91), so determinism holds across machines.
- **Debug game** (01broken-curve, q24 as B). By r1000 the counters show 35, 94 and 74 `pick_altar` skips per champion of an altar remembered as locked but **out of vision**. Those are exactly the skips tb_merge_b lacked. The game reproduced the smoke game: 1168-488.

### Patch 2: gold play (vs tb_merge_b; the h_goldtie column is from `b1-h_goldtie-all`)
Gold earned, us/them. Every game ended 0-0 on gems and was won on gold.

| Map | Side | h_goldtie | q24_combo | Treasure buys (both bots) |
|---|---|---|---|---|
| 01boss-battle | A | 27,655 / 1,715 | 24,108 / 2,578 | 25 |
| 01boss-battle | B | 29,929 / 4,749 | 25,916 / 4,505 | 25 |
| 02guardians | A | 17,031 / 723 | 14,222 / 443 | 20 |
| 02guardians | B | 14,124 / 696 | 19,827 / 872 | 20 |
| 02the-pack | A | 15,491 / 1,618 | 19,475 / 1,352 | 15 |
| 02the-pack | B | 20,267 / 539 | 21,586 / 1,139 | 15 |

- **Result.** q24 is 6-0, the same as h_goldtie.
- **Debug game** (02the-pack, q24 as A). It printed `GOLDTIE no_tribute True altars 1 usable [] guard_tiles 48`, and chip mode was on for one champion by r1999. It won 0-0 on gold, 18,565 vs 2,232.
- **Other maps.** On 00dunes it printed `no_tribute False ... usable [0, 1]`, and on 01broken-curve `usable [0, 1, 2, 3]`. So `TRIBUTE_USABLE_ONLY` is a no-op there, as designed.
- **01yellow-brick-road** (the stall map): q24 won A 26-0 and B 0-0 on gold (100 vs 0). h_goldtie went W 21-2 and L 0-15 there.

### Patch 4: fuel (fuelExhausted for our side, same games vs tb_merge_b)
| Map | Side | tb_merge_b (opponent in the q24 game) | h_goldtie | h_fightfuel | q24_combo |
|---|---|---|---|---|---|
| 01boss-battle | A | 231 | 402 | 5 | 6 |
| 01boss-battle | B | 270 | 259 | 5 | 6 |
| 01yellow-brick-road | A | 151 | 1,352 | 15 | 22 |
| 01yellow-brick-road | B | 847 | 205 | 51 | 73 |
| 02guardians | A | 0 | 2 | 0 | 0 |
| 02guardians | B | 0 | 0 | 0 | 0 |
| 02the-pack | A | 849 | 97 | 0 | 3 |
| 02the-pack | B | 124 | 196 | 0 | 3 |
| **Total (per game)** | | **2,472 (309)** | **2,513 (314)** | **76 (9.5)** | **113 (14.1)** |

- **Result.** q24 keeps h_fightfuel's fuel profile. Gold play alone (h_goldtie) had 1,352 exhaustions on 01yellow-brick-road A; the combo has 22.
- **The other 22 smoke games.** q24 had 0 exhaustions vs imit_test (4 games) and 3 vs sf_bank (4 games). On those same sf_bank games h_earlyfight_all had 393 and tb_merge_b 257.

### Patch 3: group fight rule all game (vs sf_bank)
Format: result, score, early deaths before r300 (us/them), total deaths (us/them).

| Game | tb_merge_b | h_earlyfight_all | q24_combo |
|---|---|---|---|
| 00dunes A | W 1092-136; 1/2; 7/18 | W 1002-34; 3/6; 7/26 | W 1001-103; 0/4; 2/15 |
| 00dunes B (the traced early-fight loss) | **L 196-1036; 7/1; 20/3** | W 1002-306; 1/1; 13/20 | **W 1002-608; 3/1; 5/17** |
| 01starfish A | W 1041-28; 5/6; 14/39 | W 653-124; 7/3; 32/40 | W 1001-7; 7/5; 17/42 |
| 01starfish B | W 1017-181; 6/2; 23/43 | W 1052-114; 7/4; 15/45 | W 1002-96; 2/6; 14/49 |
| **Sum** | early 19/11, deaths 64/103 | early 18/14, deaths 67/131 | **early 12/16, deaths 38/123** |

**Debug game** (00dunes, q24 as B). It reproduced the smoke game: 1002-608, 16 kills and 5 deaths. By r1000, each of the 5 champions recorded:
- 103-236 advantage turns and 52-116 disadvantage turns;
- 35-107 regroup retreats, with 2 `hit_while_leaving` hits in total;
- 236-760 `retreat_fast` candidates scored by rally distance. That is the C2 integration path working.

No `bot error` or traceback line appeared in any debug log.

## Caveats
- `TRIBUTE_USABLE_ONLY` is untested on a real mixed map: none of the 70 local maps has some but not all altars guard-only. It only matters on unseen maps.
- The group rule reads live API data in `group_balance()`. It does not use h_fightfuel's enemy cache, so it costs the same fuel as in h_earlyfight_all.
- **Next step: the LOOP.md §4 gate.** That means `--maps all` vs tb_merge_b (≥ 82/140), a paired gauntlet, a release run and an analysis session. None of these has been run for q24_combo.

## Review fixes (adversarial merge review, 31 Oct)
**Result: no merge defect found. `src/` was not changed.** The checks below were run independently of the claims above.

**1. Mechanical reference merge.**
- *Method.* tb_merge_b plus h_3pick's two lock-memory hunks (`LOCK_MEMORY_FIX` and the `mem` skip in `pick_altar`), then `git merge-file` with h_goldtie, h_earlyfight_all and h_fightfuel, in that order.
- *Conflicts.* h_goldtie and h_earlyfight_all merged with no conflict. h_fightfuel gave 5 conflicts:
  - the `__init__` state;
  - the `retreat` signature and VALIDATE harness;
  - the regroup `retreat` call in `handle_enemies`;
  - `pm("observe")` vs the stall check;
  - `pm("threats")` vs the DIAG hook.
- *Comparison.* `src/bot.py` differs from this reference only in those 5 regions and in the documented additions:
  - C1 `TRIBUTE_USABLE_ONLY`;
  - C2 `rally` in `retreat_fast` and VALIDATE;
  - C3 `esrc = None`;
  - `GOLD_LOG`;
  - comments.
- *Conflict regions.* Each of the 5 regions holds both sides. This was checked against the diff3 base, so no base-line edit was lost.
- *Conclusion.* Every hunk of every patch is present, and no tb_merge_b code was dropped or duplicated.

**2. AST, function by function.**
- **Single-source functions.** Every function only one source changed is identical to that source's version.
- **No duplicates.** There are no duplicate definitions or constants.
- **Constants.** Every module constant equals its source's value: h_goldtie v2, h_earlyfight_all v3 (`EARLY_ROUNDS = 2000`) and h_fightfuel.
- **Switches.** `DEBUG`, `DIAG`, `VALIDATE`, `PROF`, `GOLD_LOG` and `debug_tb` are off.
- **h_3pick's omitted hunks** in `retreat`, `handle_enemies`, `play_turn`, `read_claims` and `init_static` are all gated by `self.trio`, which is False under `TRIO_MODE = False`. The one exception is the `n_bodies` API call at init, and only trio reads it.

**3. Static checks.**
- py_compile passes.
- There are no undefined globals.
- No `self.` attribute is read without being set.
- Every `self.method(...)` call matches its signature, both positional count and keywords. This matters because most of this code swallows exceptions, so a bad call would fail silently.

**4. Interactions, reviewed by hand.**
- **`retreat_fast` with `rally`.**
  - It orders tiles by the same 4 keys as h_earlyfight's slow `retreat`, where `spawn_pts = rally if rally else self.spawn_pts`.
  - In both versions, an empty rally list falls back to the spawn distance.
  - The rally key is never written into `spawn_cd`.
  - The camp pre-filter (`lim`) depends only on keys 1-2, so it stays exact.
- **`esrc`.**
  - Its only reader is `retreat_fast`, and both call sites run after `threats()` in the same turn.
  - `group_balance()`, `hit_while_leaving()` and the `near` list read live API data.
- **Gold code.** It reads only `G.status`, which `observe_fast` and `observe_slow` set identically, plus its own state.
- **Static memos.** h_fightfuel's `camp_rng` and `spawn_cd` are static, and neither h_goldtie nor h_earlyfight changes their inputs. `G.value` (h_goldtie) is not cached anywhere.
- **Aliasing.** In the default branch, `tribute_ring` is the same object as `altar_ring`. Nothing mutates either in place: `build_static_fields` and `sf_dests` OR them into fresh bitboards.
- **`TRIBUTE_USABLE_ONLY` on a mixed map.** If every usable altar is locked, `free` is empty, so `break_lock` is forced and the carrier walks to a locked usable altar to break the lock. The sources would walk into the guard-only ring instead, which is the intended fix.

**5. Local game.** `./cli/cambc run q24_combo tb_merge_b --map 02arena -o matches/q24-review`:
- W 1002-177 at r1946, with 0 crashes;
- `team-a.stdout` and `team-b.stdout` empty, so no `bot error` line;
- fuelExhausted 0 (tb_merge_b: 1);
- kills/deaths 37/3.
