# c4_fallback: c2_respawn + the Q26 team bootstrap as an idle fallback, plus a first-turn fuel fix

**Status: built, smoke-checked and adversarially reviewed (two fixes, R1-R2, see "Review fixes" at the end); not gated.** Next is the LOOP.md §4 gate vs the champion `c2_respawn`. The smoke and fuel-probe numbers below predate R1-R2.

**Lineage.**
- `python3.12 tools/newbot.py c2_respawn c4_fallback` (champion, website v4).
- Then the team-clear hunks of `diff -u bots/q24_combo bots/c3_teamclear` (c3 = q24 + h_teamclear v2, already integrated with q24's caches and chip mode; see `bots/c3_teamclear/NOTES.md` T1-T6).
- Then the c4 changes below.
- For c2's own patch (RESPAWN_FIX, R1-R5) see `bots/c2_respawn/NOTES.md`. For q24's patches see `bots/q24_combo/NOTES.md`.

| File | Change |
|---|---|
| `src/bot.py` | c2_respawn + c3's team code + the c4 gate and fuel fixes, plus review fixes R1-R2: 3,354 lines (c2 2,776, c3 3,032). md5 `39196be3cbda2351cb45c5651e4a2442` (before the review: 3,325 lines, `37aed43b834b5f021d44a775e94f8a2e`). Every change is tagged `h_teamclear`, `c3_teamclear`, `c4_fallback` or `c4 review`. |
| `src/main.py`, `src/draft.py`, `src/randomness.py` | Byte-identical to c2_respawn (and to q24 / c3) |

## Hypothesis
The ladder blind spot on 02gift_wrapping (0 clears all game; lost 0-1028 and 16-1006) is the state "no champion has any solo-acceptable target, so all idle at spawn".
- c2 has the blind spot too. In the debug game below, c2 earned 0 gold and made 0 clears in 990 rounds.
- c3's team option fixed it (19 clears, 1000-0), but on every other map it competed with solo farming. The cost: 139 muster turns per game (241 on large maps), fewer team-only clears than q24 on the other targeted maps, and a gate of 80/140.
- **So in c4 the team option is used only when the champion's own solo/chip pass finds nothing.** The muster then never displaces a solo farming plan.

## Flags (top of `bot.py`)
| Flag | Value | What it does |
|---|---|---|
| **`TEAM_FALLBACK_ONLY`** | **True** | `choose_target` dispatches to `choose_target_fb`. Its loop is **c2's choose_target verbatim** (same tests, costs, multipliers, bound pruning and fuel break; AST-diffed), with three additions: it records the groups the loop rejects while nothing has passed yet, and best's `extra` and claim count `c`. Only if the loop finds nothing does `team_fallback` score c3's team option over the rejected groups: same `team_k` over [c+2, avail+c], team ttk, cost +`TEAM_MUSTER_COST`, /k, and c3's multipliers. False gives c3's `choose_target`, unchanged. |
| `TEAM_FALLBACK_TURNS` | 3 | The team pass runs only after this many consecutive `choose_target` calls with no solo/chip target (`self.nosolo`). A team pick does not reset the counter, so a fallback target is kept. |
| **`TEAM_MUSTER_IDLE_ONLY`** | **True** | **Muster gate.** A team pick musters as in c3. A *join* is a target the solo pass accepted only with c > 0 claimers' help. A join musters only if the champion's last pick that was not a join was "nothing solo" (`self.fb_idle`: set by a None or team pick; **since review R2** cleared only when some full-HP group (status 0 at full HP, or status 2) passed the loop with c = 0 in that call, even if a join outscored it, or by a join whose `muster_need` 0 came from its solo tests; captures, damaged groups and awake-group joins leave it unchanged). Otherwise the joiner fights as c2 does. Picks that passed with c = 0 skip `muster_need`, which provably returns 0 for them: its tests are the loop's at c = 0, and chip picks are excluded as in c3 T2. |
| `TEAM_BOSS_FUEL` | 300,000 | The lazy monolith API test in `group_boss` runs only above this fuel. Below it, the group counts as a boss for that turn and is retried. |
| `TEAM_CLEAR`, `TEAM_MUSTER`, `TEAM_TANK_CHECK`, `TEAM_WRAP_FIX` | True | c3 / h_teamclear, same values |
| `TEAM_NEAR_DANGER`, `TEAM_DEBUG` | False | c3 / h_teamclear, same values |
| `TEAM_MAX_STR` / `TEAM_MAX_HP` / `TEAM_MUSTER_COST` / `TEAM_COMMIT_WAIT` / `TEAM_MUSTER_WAIT` / `TEAM_BAN` / `DEAD_MARK` / `PRESENT_BYTE` | 250 / 15000 / 10.0 / 15 / 30 / 150 / 255 / 6 | c3 / h_teamclear, same values |
| `RESPAWN_FIX` | True | c2, unchanged |

- **Debug flags are all off:** `DEBUG`, `DIAG`, `VALIDATE`, `PROF`, `GOLD_LOG`, `TEAM_DEBUG` and `Bot.debug_tb`.
- c2's and q24's switches are unchanged. An AST check of the constants found only the four new c4 flags.

## WRAP fixes: decided with evidence; all three stay unconditional
- **(a) Hidden camps of an awake target count as threats: unconditional.**
  - It is the only part independent of Q21, and it is physically correct (a group wakes as a whole).
  - In the final smoke it added in-range hidden threats 930 times. **896 of those were on 02gift-wrapping** (wrapped groups); on the other 32 map-sides it fired about once per game.
  - Making it team-only would add code for no measurable effect. h_teamclear v0 died without it (Vendetta, 360 HP, an unseen elk).
  - It feeds `incoming`, so it also feeds c2's `turn_quiet`. That is coherent: a hidden awake camp in range really is hitting us, so the turn is not quiet.
- **(b) The "respawning" guess needs every believed-alive camp in view: unconditional.**
  - Under c2's RESPAWN_FIX (d), the guess already runs only when no spawn tile of the target is visible (`G.seen != rnd`). (b) then narrows it to "all camps believed dead". Without (b), walking around a wall or bush within 3 of the centre marks an alive target respawning and drops it for 10 rounds.
  - It still fires: **26.6 vetoes per game** in the final smoke, on 00great-wall, 00swirl, 02fields, 01corridors and 00road-of-riches, all non-gift maps.
  - It is a strict soundness refinement of a heuristic, and its cost is one `visible_tiles()` call only when the guess would fire.
- **(c) The target's own dead tiles may be stood on: kept, and a no-op under RESPAWN_FIX.** It only exempts tiles from the in-turn push-back, which RESPAWN_FIX (a) disables (`if not RESPAWN_FIX and ...`). The merged condition is the AND of c2's and c3's: `not RESPAWN_FIX and status != 1 and on a camp tile and not WRAP-exempt and blocks_respawn`. See C4-3.

## Shared memory: c3's 8-byte map, no collisions with c2
| Byte | Contents | Writers / readers |
|---|---|---|
| 0-5 | One byte per slot: 0 = idle, group idx+1 = claim, 255 = dead (`DEAD_MARK`) | `write_claim` (idx ≥ 254 maps to 0, so a claim is never 255), `write_dead` / `read_claims` (loops 0-5) |
| 6 | Presence bits: bit s = slot s stands within its claimed alive group's zone (range + 4) | `set_present` (read-modify-write of its own bit; cleared by `write_claim(None)` / `write_dead`) / `muster` |
| 7 | sf_pvp focus, `((enemy+1) << 5) \| (round & 31)` | `write_focus` / `read_focus` (c2, unchanged) |

- **Checked by grep:** c2 accesses only bytes 0-5 (claims via its own slot) and byte 7. c4's accessors are exactly c3's five, plus c2's focus pair.
- **Slot range:** at most 6 bodies, so slot ≤ 5, and nothing writes byte 6 except `set_present`.
- **c2's old `read_claims`** looped over bytes 0-6. Byte 6 was always 0 in c2, so the claims dict c4 reads is the same.

## Conflicts and resolutions
**Mechanical reference.** `git merge-file -p --diff3 c2 q24 c3` applies c3's team hunks to c2 with 5 conflicts, all resolved by `matches/c4fb-tools/resolve.py`:
1. The constants block: both kept.
2. The `Group` slots: c2's `seen`. c3's `boss`/`ring`/`zone` were later moved off `Group` (C4-4).
3. The `Group.__init__` tail: c2's `seen`. c3's boss gate became lazy (C4-4).
4. The `Bot` state: both kept.
5. The step-off condition: AND of all three (C4-3).

The merged file differs from c3 only by c2's hunks and from c2 only by c3's hunks (checked with `diff c3 merged`). c3's resolutions T1-T6 carry over unchanged. T1 is `wrap_hidden` in both threats paths; T2 is chip vs team (see C4-1); T4 is the `pbits` rename.

**C4-1. The fallback gate vs c3's T2 (chip vs team).**
- In c3, the team and chip options were compared per group.
- In c4 (flag on), a chip pick is a solo option of the loop, exactly c2's test: `cycles ≤ (30 if chip else 4) and escape_ok`, extra = 30·cycles. The team option exists only if the loop found nothing.
- A chip pick is identified as `best_x > 120` (cycles > 4) and never musters, as in c3.
- With the flag off, `choose_target` is c3's code byte for byte (except `group_boss`).

**C4-2. The muster for joins (TEAM_MUSTER_IDLE_ONLY).**
- c3 mustered any non-chip best that `muster_need` judged team-only, including joins by farmers.
- c4 musters joins only for champions whose last non-join pick was idle.
- **First version, replaced:** a scan for any solo alternative (`solo_alternative`). It cost 140-208k on turn 1 (profile below), so it was replaced by the O(1) `fb_idle` mode.
- In the final smoke, 297 join-turns per game would have mustered under c3's rule and fought instead (`supp`), while 25.5 per game mustered (`need_join`, nearly all on 02gift-wrapping).

**C4-3. WRAP (c) vs RESPAWN_FIX: coherent.**
- The in-turn push-back is dead code under RESPAWN_FIX, so (c)'s exemption does nothing there.
- c2's end-of-turn `leave_respawn_tile` reads the live engine state and steps off only Respawning groups. An alive target never is, so (c)'s intent (stand on the target's dead tiles while it is alive) holds automatically. If our belief is stale, the live state wins.
- `resp_mask` (farm goals) excludes only status-2 groups, never the alive target.
- The muster ring excludes all camp tiles, so a musterer never parks on a respawn tile.
- A muster turn either moves (`can_move` False) or stands on the ring (not a camp tile), so `leave_respawn_tile` never fires on it.

**C4-4. First-turn fuel (task item). Cause found by profiling; c3's "probable cause" was only part of it.**
- **Turn 1** has a 5M budget. `init_static` (~2.35M) plus the first decision runs within about 0.5M of it; then `build_static_fields` spends the rest down to its 1M floor. So any extra in turn 1 suspends it.
- **Profile (00dunes, `matches/c4fb-prof-dunes`, first c4 build).** The c3 code added three costs:
  - **`present`, 254-284k per champion:** the `group_zone` dilation in `set_present` for every alive target.
  - **`init_static`, +74k:** the boss gate's HP sum (the `is_monolith()` loop c3 blamed is only part of it).
  - **`choose`, +40-60k.**

  All 5 c4 champions then suspended at r1 (`susp=farm_goto`, 6.2M used), against 0 for c2.
- **Fixes:**
  - **Lazy boss gate.** `group_boss`: thresholds plus the monolith test on first use, behind `TEAM_BOSS_FUEL`. `team_k` runs first, so it is rarely reached. `muster_need`'s boss test moved to just before `team_k`, which gives the same result.
  - **Team caches off `Group`.** `boss`/`ring`/`zone` are now `Bot.g_boss` / `g_ring` / `g_zone` dicts, so `Group.__init__` is c2's byte for byte.
  - **`cheb_ball`.** The zone and the muster ring are drawn with one `draw_chebyshev` per spawn tile instead of `dilate` (8R bitboard ops). It is the same set: **0 mismatches in 988 checks** against `dilate` in the instrumented smoke.
  - **Presence only when it can be read.** The zone is tested only when I muster or an ally claims my group, and not in rounds 1-2. Presence bits are read only by musterers of the same group, and no team pick exists before round 3.
  - **The O(1) muster gate** (C4-2), in place of the scan.
  - **`wrap_hidden` guarded** to turns with an awake camp and a target.
  - **No team candidate when the tank budget is ≤ 0.** `team_k`'s cap is ≤ that budget, so it would return 0 anyway.
- **Profiles after the fixes** (both seats, `matches/c4fb-prof2`, `c4fb-prof3`):
  - The loop costs the same as c2's: `fb_loop` 369k vs 369k on 02famine, and 526k vs 526k on 01yellow-brick-road.
  - The residual per-turn overhead is about 30k (≈1.5%), measured over rounds 3-399 on 01big-world (`matches/c4fb-prof4`): the presence test on join turns, the muster bookkeeping, `wrap_hidden` on fighting turns and the c3 `read_claims`.
  - Suspended turns there are trajectory-dominated: c4 86 against c2 97 over both seats.

**C4-5. Behaviour changes inside c3 functions (all documented in the code).**
- `group_zone` and the `muster` ring now use `cheb_ball` (the same sets).
- `muster` reads the ring from `g_ring`.
- `set_present` is called only under the C4-4 condition. The worst case is that a claimer's bit lags by a turn when a musterer first claims, or until round 3.
- `threats_*` call `wrap_hidden` only when it can act.

**C4-6. Untouched c2 integration points.** These are byte-identical to c2 (except `play_turn`, which since review R1 also clears a stale presence bit after `leave_respawn_tile`):
- `G.seen = rnd` in both observes;
- the `play_turn` wrapper, `leave_respawn_tile` and `resp_mask`;
- `turn_quiet` right after `threats()`;
- the (d) gate on the guess;
- the farm-goal `resp_mask` filter.

## Checks
- **`py_compile`** passes on all 4 files, compiled to the scratchpad so no `__pycache__` is written into `src/`.
- **`attrcheck.py`:** no `self.` attribute is read without being assigned, and there are no undefined globals.
- **`funccmp.py` (AST, per function):**
  - Identical to c2: `Group.__init__`, `observe_fast`, `observe_slow`, `leave_respawn_tile`, `resp_mask` (`play_turn` was too, until review R1).
  - Identical to c3: `team_k`, `wrap_hidden`, `read_claims`, `write_claim`, `write_dead`, `set_present`, `nearest_incoming`, `init_static`.
  - The changed functions are listed in C4-1 to C4-5.
- **`choose_target_fb` vs c2's `choose_target`:** the unified diff shows only the three records, the `rejected` appends on the two rejection paths, and the post-loop block.
- **Static map.** `diff c2 c4` has 20 hunks. Every one is either a c3 team hunk or a C4-1 to C4-5 change.

## Validation (every game on the Slurm `test` partition via `tools/onslurm.sh`)
### Debug game: c4_fallback vs c2_respawn, 02gift-wrapping (final code, `matches/c4fb-dbg-gift-v3`)
- **W 1032-0 at r987.** 24 clears, all of team-only (census) groups 0/5/7/9; first clear r28; 44 tributes.
- 0 deaths, 0 camp deaths, **0 fuelExhausted** (r1-2: 0).
- botFaults 0; team stdout and debug logs 0 bytes.
- c2 made 0 clears and earned 0 gold.
- The earlier builds gave the same result: W 1008-0 r990 with 20 clears (`c4fb-dbg-gift`) and W 1032-0 r987 (`c4fb-dbg-gift-final`).
- For reference, c3 vs q24 won 1000-0 at r816 with 19 clears.

### Fuel probe, r1-2: c4_fallback itself vs c2_respawn, all 70 maps, both sides, `--rounds 3`
- **Method.** Counted from `team-*.fuel`: a turn at its budget (5M at r1, 2.5M after) was suspended. `matches/c4fb-tools/fuel12.py` reproduces the gate folders' event counts exactly.
- **Command:** `tools/onslurm.sh -c 24 -m 16G -t 00:20:00 -J c4fb-fuel3 -- python3.12 tools/eval.py c4_fallback c2_respawn --maps all --rounds 3 --jobs 16 --keep --tag c4fb-fuelprobe3`

| Build | Suspended r1 / r2 (r1-2 per game) | Opponent, same games | Maps with any |
|---|---|---|---|
| c3_teamclear (`gate-c3-all`, vs q24) | 160 / 148 (**2.20**) | q24 100 / 53 (1.09) | 35 vs 16 |
| c4 first build (`c4fb-fuelprobe`) | 102 / 85 (1.34) | c2 100 / 57 (1.12) | 20 vs 17 |
| c4 + O(1) muster gate, caches off Group (`c4fb-fuelprobe2`) | 98 / 66 (1.17) | c2 100 / 57 | 17 vs 17 |
| **c4 final (`c4fb-fuelprobe3`)** | **98 / 65 (1.16)** | **c2 100 / 57 (1.12)** | **17 vs 17** |

- **c3's excess over its opponent was +155 suspended turns at r1-2; c4's is +6.** Rounds 1-3: c4 181 vs c2 177.
- **r1 is now equal or better on every map.** The only map-sides worse at r1-2 are 01yellow-brick-road A and B: r2 5 vs 2 and 5 vs 1.
  - On that map both bots suspend all 5 r1 turns, and c2 runs its r2 and r3 at 2.45-2.50M.
  - c4 suspends at r2 where c2 suspends at r3: through r3 it is 10 vs 8 and 10 vs 7.
- One map-side is better: 00reverse-spiral B, 2 vs 3.

### Smoke: 17 maps, both sides (34 games), instrumented copy `dbg_c4fb` vs c2_respawn, with bot stdout
- **Maps:**
  - 02gift-wrapping and 01yellow-brick-road;
  - c3's 10 regressions on targeted maps (its report §3): 00swirl, 02crossing, 00great-wall, 00pilgrimage, 01islands, 00expanse, 00road-of-riches, 01corridors, 01fracture, 01the-farm;
  - 5 large maps where c3 mustered most: 00dunes, 02famine, 01big-world, 02fields, 01concentrated-wealth.
- **Command:** `tools/onslurm.sh -c 24 -m 16G -t 00:20:00 -J c4fb-smoke3 -- python3.12 matches/c4fb-tools/runlogs.py c4fb-smoke3 16 dbg_c4fb c2_respawn <17 maps>`. Parsed with `matches/c4fb-tools/c4parse.py ... matches/q26-tc/tools/census_out.txt --per-game`.
- **The instrumented copy.** `dbg_c4fb` is the final c4 plus C4DBG counters printed every 50 rounds, built by `matches/c4fb-tools/mkdbg2.py`. It also checks `cheb_ball` against `dilate` and calls `muster_need` for its `supp` counter.
- **Two earlier iterations** used the same maps: `c4fb-smoke` (first build, 19W) and `c4fb-smoke2` (O(1) gate not yet in, 19W). They found the fuel problems above. The table is the final code.

```
games 34  wins 20   (dbg_c4fb vs c2_respawn)
```

| Per game (34 games) | c4 final | c3 traced census on the same 34 map-sides (vs q24) |
|---|---|---|
| **Muster turns, 02gift-wrapping (2 games)** | 166.5 (team picks 89.5) | 187.0 (team picks 186) |
| **Muster turns, the other 32 map-sides** | **3.3** (team picks 0.6) | **308.3** (team picks 43.7) |
| Muster turns, large maps (> 2,500 tiles, 20 map-sides) | **3.6** | 330.5 |
| Muster bans | 0 in 34 games | |
| WRAP (a) hidden threats in range | 27.4 (896 of 930 on gift-wrapping) | |
| WRAP (b) vetoes | 26.6 | |
| Joins fought instead of mustered (`supp`) | 297 | |
| Joins mustered (`need_join`) | 25.5 | |

- **Muster outside gift-wrapping, per map-side:** 01concentrated-wealth A 71 (idle champions joining), 01corridors B 29 (its 20 team picks gave 2 team-pass clears), 01corridors A 4 and 01concentrated-wealth B 2. Every other map: 0.
- **Team-only (census) group clears in the same games, c4 / c2:**
  - 02gift-wrapping 44 / 4;
  - 01yellow-brick-road 38 / 8;
  - other maps 15 / 7;
  - **total 97 / 19.**
  - For reference, against q24 on these map-sides: c3 71, c2 27.
- **Results by family:**
  - 02gift-wrapping and 01yellow-brick-road: **4/4** (gift 1035-33 and 1004-32; YBR 851-49 and 863-511).
  - c3's 10 regression maps: 12/20 (c3 vs q24 there: 4/20).
  - 5 large maps: 4/10.
- **Other per-game numbers:** camp deaths 1.18 vs c2's 0.97; champion deaths 280 vs 293 in total; clears 51.6.
- **Fuel in the smoke is the instrumented copy's,** so it is not c4's:
  - **r1-2:** 78 vs c2's 67;
  - **all rounds:** 15.6 vs 11.9 per game;
  - **excluding print rounds:** 441 vs 333 turns at 2.5M, concentrated on 01big-world and 01islands.
  - The copy runs `dilate` checks (29 per game, about 280k each) and counters every turn. Use the probe above (r1-2) and the 01big-world profile (r3-399, uninstrumented) for c4's own fuel.

## Caveats / next steps
- **Gate.** Run the LOOP.md §4 gate vs `c2_respawn`:
  - `--maps all` ≥ 82/140;
  - a gauntlet ≥ c2's 177/200;
  - a `--release` game, checking fuelExhausted against c2 in the 140 gate games;
  - the analysis. Include the "targeted vs other maps" split and a muster census, as c3's report recommends.
- **The smoke is a mechanism check.** The maps were chosen because the mechanism acts or regressed there, and the W/L of a near-mirror re-rolls (placebo: null changes score 66-68/140).
- **Residual per-turn overhead.** About 30k per turn (≈1.5%) remains. If gate (c) fails on fuel, the next lever is a cheaper presence signal, for example evaluating it every 4 rounds when the bit is clear.
- **Diagnostic bots, never evaluate them:** `bots/dbg_c4fb` (counters), `bots/dbg_c4prof` and `bots/dbg_c2prof` (per-segment fuel profilers).
- **Tools and outputs** are in `matches/c4fb-tools/`: `runlogs.py`, `runshort.py`, `c4parse.py`, `fuel12.py`, `fuelmid.py`, `fueldist.py`, `baseline.py`, `mkdbg2.py`, `resolve.py`, `attrcheck.py`, `funccmp.py`.

## Review fixes (adversarial review, 1 Nov)
**Result: two real defects, both fixed in `src/bot.py` (tagged `c4 review R1` / `R2`); everything else checked out.** The review did not rely on the claims above. md5 before `37aed43b…`, after `39196be3cbda2351cb45c5651e4a2442` (3,354 lines). `main.py`, `draft.py` and `randomness.py` are still byte-identical to c2_respawn.

**What was checked and holds.**
- **Every c3 team hunk is present or deliberately gated.** Walked hunk by hunk through `diff -u q24_combo c3_teamclear` (530 lines) against c4:
  - constants, the `Bot` state, `n_bodies`, `read_claims`, `write_dead`, `set_present`, `write_claim`, `team_k` and `nearest_incoming` are present;
  - `wrap_hidden` is called from both threats paths, guarded by `awake and self.target is not None` (equivalent, because `wrap_hidden` acts only then and the else branch resets `hidden_hp`);
  - the dead branch, the `hidden_hp` fallback in the danger check, `TEAM_NEAR_DANGER` (off), the WRAP (b) veto and the muster call are present;
  - the step-off condition is the AND of both sides;
  - the `Group` boss/ring/zone slots became `Bot.g_*` (C4-4), and the team option in `choose_target` became `team_fallback` (gated by `TEAM_FALLBACK_ONLY`).
- **Nothing of c2 is lost.**
  - An AST diff per function (`fcmp.py`, scratchpad) finds no c2 function or constant missing or changed.
  - The 9 functions that differ do so only by c4/c3 additions: `__init__`, `choose_target`, `init_static`, `play_turn`, `play_turn_main`, `read_claims`, `threats_fast`, `threats_slow`, `write_claim`.
  - `read_claims` now reads bytes 0-5, where c2 read 0-6; byte 6 was always 0 in c2.
  - The c2 loop inside `choose_target_fb` still matches: `cycles > limit or not escape_ok` short-circuits like c2's two `continue`s, so `escape_ok` (and its cache) is called on exactly the same groups.
- **Team picks never displace a solo target.** `team_fallback` runs only when the loop set nothing. With best None there is no bound pruning and no fuel break, so every reachable, non-banned group was tested. At hp < 60% only the current target can be rejected, as in c3.
- **WRAP (c) and RESPAWN_FIX: confirmed a no-op**, as C4-3 says. The push-back block is `not RESPAWN_FIX and …`. `blocked_now` blocks only live camps. `leave_respawn_tile` checks the live Respawning state. Proximity never wakes camps (rules: damage wakes a group), so waiting at a respawning team group's 1-ring is safe.
- **WRAP (b) and RESPAWN_FIX (d):** the guess now fires only when every camp of the group is believed dead. Under (d), no tile of the group is visible when the guess runs, so any camp believed alive vetoes it. The champion then walks toward the believed-alive tiles, sees them, and `observe` corrects the status. No freeze is possible: the stuck guard bans after `STUCK_TURNS`.
- **Fuel guards.**
  - `group_boss` caches only a computed answer. Below `TEAM_BOSS_FUEL` it returns "boss" for that call, uncached.
  - A team pick always has a cached `g_boss`, because `team_fallback` computed it, so its `muster_need` never hits the fuel fallback.
  - The presence test and `wrap_hidden` are guarded as C4-4 says.
- **Shared memory.**
  - Bytes 0-5 hold claims: own slot only; slot ≤ 5 with at most 6 bodies.
  - Byte 6 holds the presence bits: read-modify-write of one's own bit, cleared by `write_claim(None)` and `write_dead`.
  - Byte 7 holds the focus, untouched.
  - No other accessor exists (grep).

**R1. Stale presence bits (c3 review item 6, still open in c4).**
- *Defect.* Byte 6 was re-evaluated only on farming turns. A claimer that left to fight an enemy (`handle_enemies`), fled (danger retreat), walked home on low HP or healed at spawn kept its "near" bit. A musterer counts that bit in `near_sh` and could wake a full-HP team group with fewer champions really near.
- *Fix.*
  - `play_turn` clears the bit after `play_turn_main` when the turn did not re-evaluate it (`self.pres_fresh`, set right after the farming block's `set_present`).
  - It costs O(1): there is no API call while the bit is clear, which is nearly always, and one write when it changes.
  - Clearing is the conservative direction. The musterer waits (≤ 30 rounds, then bans) instead of releasing on a champion that is busy elsewhere. Champions it can see in the zone still count through vision.

**R2. The join-muster gate (`fb_idle`) leaked, and was not a "no solo target" test.**
- *Defect 1, team members became "farmers".* `need <= 1 → fb_idle = False` fired on every `muster_need` 0, but `muster_need` also returns 0 for:
  - an awake or damaged group (every join of a team fight in progress);
  - a boss;
  - "no team".
  So after a team fight, its members' next full-HP join of a team-claimed group (often a 3rd champion whose check passes with c = 2, the case the muster exists for) walked in and woke the group alone. That contradicts the spec above: the last non-join pick was a team pick. Likewise `best_c == 0` cleared it on a lone *capture* (status 1), which says nothing about solo farming.
- *Defect 2, solo targets did not veto.* `fb_idle` only remembered the last non-join pick. A previously idle champion (for example a None turn at hp < 60%) whose best was a full-HP join mustered even when a full-HP group it could clear alone had passed in the same call (outscored by the join's ×1.2 ×1.3). That contradicts "the muster never displaces a solo farming plan".
- *Fix.*
  - The loop records `solo_full`: some status-0-at-full-HP or status-2 group passed with c = 0. This costs one `sum` per such pass until the first; the check `G.status != 1` comes first, so `hl` is always this iteration's.
  - `fb_idle` is set by a None or team pick and cleared iff `solo_full`, or by a join whose `muster_need` 0 came from its solo tests (`self.mn_solo`: s ≤ 0, direct or hit-and-run).
  - Captures, damaged groups and awake-group joins leave it unchanged.
- *Remaining gap, documented, not fixed.* A solo group pruned by the score bound (bound < the join's score) is not seen. Seeing it needs the full scan that C4-2 removed for fuel.
- *Direction of the change.* R2 adds join musters for team members on 02gift-wrapping-like maps and for once-idle champions with no full-HP solo pass. It removes them when a solo pass exists. It never changes team picks.
- **The gate's muster census should split join musters by map family.** The smoke numbers above (`supp` 297/game, `need_join` 25.5/game) predate R2. On 02gift-wrapping, `supp` was 143 and 185 per game. This review did not separate how much of that was the R2 leak and how much was champions able to solo groups late in the game.

**Not defects, or not fixed (noted for the gate analysis).**
- **Chip mode is starved while a team option exists.**
  - h_goldtie's chip mode needs 12 consecutive `G is None` turns in gold play.
  - A team pick after 3 idle turns resets that counter, so on no-tribute maps the team option replaces c2's chip bootstrap whenever both exist.
  - This is inherited from c3, whose gold totals were ≥ q24's on 01boss-battle and 02guardians.
  - Check 01boss-battle, 02guardians and 02the-pack in the gate.
- **Inherited from h_teamclear:**
  - A team pick on a damaged but sleeping group gets `muster_need` 0 (`hp_left < full`) and attacks alone.
  - A farmer (`fb_idle` False) that joins a team-picked group wakes it without waiting, which is c2 behaviour by design of `TEAM_MUSTER_IDLE_ONLY`.
  - Claim bytes stay stale on non-farming turns (c2's semantics: a retreating claimer still counts in c and `committed`).
- **`self.team_pick` is written, never read.** Harmless.

**Validation (each on the Slurm `test` partition via `tools/onslurm.sh`).**
- `py_compile` passes on all 4 files, compiled to the scratchpad. `attrcheck.py` finds no attribute read without being assigned and no undefined globals. All debug flags are off.
- **Debug game 1 (R1 + R2 code, before a comment-only edit):** `./cli/cambc run c4_fallback c2_respawn --map 02gift-wrapping -o matches/c4rev-dbg-gift` (job 56838204).
  - **W 1032-0 at r987, gold 5,603, 0 deaths, 0 crashes, stdout 0 bytes.**
  - `replay.repl26a` is **byte-identical** (md5 `4f455376…`) to `matches/c4fb-dbg-gift-v3`, the pre-review final. So neither fix changed a decision in that game.
  - Only `team-a.fuel` differs: 0 turns at budget in both; mean per-turn fuel 1,279k → 1,286k. That figure includes main.py's static-field spending, so it is not a clean overhead number.
- **Debug game 2 (final file, md5 `39196be3…`):** `./cli/cambc run c4_fallback c2_respawn --map 01corridors -o matches/c4rev-dbg-corridors` (job 56838590). This map was chosen because team picks, join musters and solo farming all occur on it.
  - **W 652-408 at r2000, K/D 6/11, gold 5,527, 0 crashes, stdout 0 bytes, 0 turns at budget** on either side.
  - `replay.repl26a` is **byte-identical** (md5 `b1600028…`) to the smoke game `matches/c4fb-smoke3/01corridors__A`, which was played by the pre-review instrumented copy. Its counters were `need_join` 4, `muster` 4, `supp` 917 and `none` 279. So on this map too R2 flipped no decision.
  - Read with the R2 logic, this means **those 917 `supp` join-turns were champions with a genuine full-HP solo pass**, not the leak.
- **Reading.** Both fixes are inert in the two games played. They close holes that the design claims are closed, at no measurable fuel cost. Their effect on the 140-game gate is expected to be small: their decisions differ only in rare states. The gate's muster census is still the check.
