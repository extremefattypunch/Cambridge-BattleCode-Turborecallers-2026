# c2_respawn: q24_combo + the Q21 respawn-rule movement fix (h_respawnfix v3)

**Lineage.** `python3.12 tools/newbot.py q24_combo c2_respawn` (champion, website v3), then every hunk of
`diff -u bots/tb_merge_b/src/bot.py bots/h_respawnfix/src/bot.py` ported. h_respawnfix forks tb_merge_b and
changed only `src/bot.py`. Its design, its two freeze mechanisms and its 92W-48L vs tb_merge_b are in
`bots/h_respawnfix/NOTES.md` and `results/simulated-matches/2026-11-01_0126_h_respawnfix/notes.md`. For q24_combo's own
patches see `bots/q24_combo/NOTES.md`.

| File | Change |
|---|---|
| `src/bot.py` | q24_combo + patch 5 below (2,697 -> 2,776 lines). md5 `83d844c8...` |
| `src/main.py`, `src/draft.py`, `src/randomness.py` | Byte-identical to q24_combo |

## Flags
- **New:** `RESPAWN_FIX = True`. This is h_respawnfix's only switch, with its name and value unchanged.
- **Debug:** off (`DEBUG`, `DIAG`, `VALIDATE`, `PROF`, `GOLD_LOG`, `Bot.debug_tb` all False).
- **q24_combo switches:** unchanged (`LOCK_MEMORY_FIX`, gold play, group rule, `OBSERVE_FAST`/`THREATS_FAST`/`RETREAT_FAST`/`KIT_FAST`, `TRIBUTE_USABLE_ONLY`).
- **With `RESPAWN_FIX = False`:** the logic is q24_combo's, including h_goldtie's `blocks_respawn` push-back. A few extra bytecodes per turn remain (`G.seen`, `turn_quiet`), so the fuel is not identical, and games can diverge chaotically.

## Patch 5 (h_respawnfix v3, every hunk)
| h_respawnfix fix | Hunk in c2_respawn |
|---|---|
| (a) No in-turn push-back | `if not RESPAWN_FIX and G.status != 1 and ... and self.blocks_respawn(pos):` |
| (b) End-of-turn step-off | `play_turn` is now a wrapper: `turn_quiet = False`, then `play_turn_main()` (q24_combo's old `play_turn` body), then `leave_respawn_tile()` if `RESPAWN_FIX and turn_quiet`. `turn_quiet = incoming == 0 and not enemies` is set right after `threats()`. `leave_respawn_tile` and `resp_mask` are copied verbatim. |
| (c) No parking on respawning tiles | Farming stand-off and bush goals minus `resp_mask()` (if anything is left), before `pm("farm_goals")` |
| (d) Fresh-read gate on the unseen-alive guess | `Group.seen` (new slot, init -1), set to `rnd` after every successful `G.g.state()` read. The guess runs only if `not (RESPAWN_FIX and G.seen == rnd)`. |

## Conflicts and resolutions
A reference `git merge-file --diff3 q24_combo tb_merge_b h_respawnfix` gives 6 textual conflicts: Bot state, the `play_turn` head, the `threats` line, the push-back condition, the farm goals, and the constant block. Five of them are pure adjacency and keep both sides. The two below are semantic, and one more problem merged *silently*.

**R1. `G.seen` and the fuel cache (`observe_fast`). Silent-merge trap.**
- **The trap.** The textual merge put `G.seen = rnd` only in `observe_slow`, which is dead code under `OBSERVE_FAST = True`. `G.seen` would then stay -1, the fresh-read gate (d) would never fire, and **freeze mechanism 2 would survive**. That is the "unseen-alive guess undone every turn" that froze all 5 side-B champions next to (34,12) on 01yellow-brick-road.
- **Fix.** `G.seen = rnd` is set in both `observe_fast` (live) and `observe_slow` (flag-off / VALIDATE), right after the `state()` read.
- **Why it is current.** `observe_fast` reads `G.g.state()` fresh every turn under the same condition as the slow path (centre within 10, some spawn tile visible). So `G.seen == rnd` means "the engine said this group is Alive this turn", exactly as in h_respawnfix.
- **VALIDATE.** VALIDATE (off) runs both observes, and both write the same `rnd`.

**R2. h_goldtie's `blocks_respawn` (gold play) vs (a).**
- **q24_combo's rule.** It narrowed the push-back to tiles of groups believed respawning (`status == 2`), and only in gold play (`no_tribute` or `stalled`). Outside gold play it pushed off *any* camp tile, which is tb_merge_b's bug.
- **Resolution.** `RESPAWN_FIX` removes the in-turn push-back in all modes. This is what h_goldtie's own NOTES asks for ("Make the respawn-rule fix universal").
  - A partial narrowing would keep the 2-cycle for paths that cross a believed-respawning tile: step on, pushed back, step on again, with the stuck guard blind to it.
  - `blocks_respawn` is kept, unchanged, for the flag-off path.
- **Known behaviour difference.** In gold play, h_goldtie's push-back also fired with an enemy in sight. The step-off requires a quiet turn: no enemy within `ENEMY_SIGHT` and no awake camp hitting us. This is h_respawnfix's design, and it was not changed.

**R3. Chip mode, `no_tribute` and `stalled`.**
- **Chip mode** only raises `choose_target`'s cycle limit (`GOLD_CHIP_CYCLES`). A hit-and-run turn either moved (`can_move()` False) or is not quiet (an awake camp is hitting us). So `leave_respawn_tile` never fires mid-chip.
- **`no_tribute` and `stalled`** don't touch the status-2 ring wait, the capture branch or the unseen-alive guess, so (c) and (d) apply unchanged in gold play.
- **`resp_mask`** reads `G.status`. That is set by this turn's `observe_fast` (or by the guess), and `observe_fast` and `observe_slow` set it identically.

**R4. h_fightfuel caches and q24's `play_turn` prologue.**
- **Prologue.** The wrapper is outermost. `pm("start")`, `self.esrc = None` and PROF tagging stay at the top of `play_turn_main`, so the esrc invariant (cleared before `threats()` refills it) holds.
- **No cache reads.** `leave_respawn_tile` reads no cache: it calls `state()` and `blocked_now()` live, plus the target's `G.hp` from this turn's observe.
- **`turn_quiet` vs `threats_fast`.** `threats_fast` has the same semantics as tb_merge_b's `threats()` here: `incoming` counts awake camps in range plus enemies in range, and `enemies` is the list of enemies within `ENEMY_SIGHT`.
- **Order in `main.py`.** It is unchanged: `play_turn` (now including the step-off), `pm_end`, `build_static_fields`, `prof`. This is the same position relative to `build_static_fields` as in h_respawnfix.

**R5. Group-balance rule (h_earlyfight).** It does not touch movement on camp tiles. Its regroup `retreat(..., rally)` runs only with enemies in sight, so the turn is not quiet and the step-off never fires.

## Merge check
- **Token comparison.** I resolved the reference merge as above (and added the `observe_fast` line), then compared tokens ignoring comments and blank lines. The only differences from `src/bot.py` are:
  - docstrings;
  - where the `RESPAWN_FIX` constant sits;
  - the `turn_quiet` line placed before `pm("threats")`/DIAG, both no-ops for it.
- **Static checks.**
  - `py_compile` passes on all 4 files.
  - No `self.` attribute is read without being set.
  - All debug flags are off.
  - `RESPAWN_FIX` appears in all 4 places.
  - `src/__pycache__` was removed after compiling.

## Validation
### Local games, 01yellow-brick-road (the h_respawnfix trace map)
- **Required game.** `./cli/cambc run c2_respawn q24_combo --map 01yellow-brick-road -o matches/c2-local`, stats in `matches/c2-local/01yellow-brick-road__A.json`:
  - **W 594-54** at r2000;
  - 30 clears, 40 tributes, first tribute at r220 (q24_combo: r1174);
  - K/D 16/11, gold 7,001 vs 1,658, fuelExh 34;
  - 0 crashes; team stdout and debug logs 0 bytes (no `bot error`, no traceback); botFault 0.
- **Extra game, sides swapped.** `q24_combo c2_respawn`, `matches/c2-local-b`: **W 15-4**, 0 crashes, empty logs. This game re-ran byte-identically (`matches/c2-local-b-rep`), and the cluster smoke reproduced both games exactly.

**Freeze** (`tools/freeze_metric.py`, idle stretches ≥ 150 rounds, champion-rounds us / them):

| Game | c2_respawn | Opponent | Reference |
|---|---|---|---|
| A: c2 vs q24_combo | **2,122** | 4,749 | q24_combo vs tb_merge_b, same side (`gate-q24-all`): **8,648** / 9,411 |
| B: q24_combo vs c2 | **7,996** | 8,154 | q24_combo vs tb_merge_b (B): 9,335 / 9,135 |
| B: q24_combo vs **h_respawnfix** (`matches/c2-hrf-b`) | h_respawnfix 0 (W 1,018-140) | 836 | |
| B: c2 logic, 3 code-perturbed trace builds (`matches/c2-dbg-b*`) | 0, 0, 174 (W 861-375, 920-192, 1,002-32) | | |

**The B game's freeze is a capture standoff, not a respawn-rule freeze.**
- **The event log.** Team A's Heart of Ruin cleared **group 1, the 30-tile y=12 row** (centre (34,12)), at r349. **No `gemCollection` for that group ever follows.** After r534 neither team logs a single clear, death or tribute until r1908.
- **In other games.** I scanned the other 01yellow-brick-road games (`gate-q24-all` A/B, `q21-all` A/B, `c2-local` A, `c2-hrf-b`). None of them has a clear left uncaptured for more than 150 rounds, so q24_combo's 8,600-9,300 frozen rounds per side there were the respawn-rule freeze that this patch removes.
- **Mechanism (from the rules).** "Leaving the region empty or admitting an enemy resets progress." Both bots wait on any free tile of a RewardAvailable target (`capture` branch: `if G.tiles.is_set(pos): return`), and the row is 30 tiles long. So champions of both teams on one row reset each other's capture forever.
  - This is the **contested-capture standoff** that the h_respawnfix report lists as an open hypothesis (HoR waited 609 turns in its traced game).
  - The port does not create it. The capture branch is unchanged, and q24_combo waits the same way.
  - It shows up here because c2's champions no longer freeze elsewhere and reach the rows.
- **Not directly traced.** The standoff could not be traced in the 15-4 game itself. Any code change, even a single fuel-free `debug_block` call at the end of the turn, changes turn-1/turn fuel and the trajectory diverges: the 3 traced builds won big with ≤ 174 frozen rounds.
  - A traced build did log 30 turns of capture attempts with an enemy seen on the target's region (`matches/c2-dbg-b3`, groups 16/1/12/10). They resolved there.

### Smoke job (onslurm job 56781042, exit 0, `matches/c2-smoke-resp`, `--keep`)
- **Maps (15, both sides = 30 games).** These are the maps where h_respawnfix changed most:
  - the largest freeze drops: 01yellow-brick-road, 01islands, 01broken-curve, 02geodes, 00quarry, 00packs, 02harvest, 00expanse, 00reverse-spiral, 00corners, 00rushbait-v2;
  - the heaviest census maps: adgato-gemcombat5, 00rows, 01corridors;
  - the largest freeze increase: 02tangle.
- **Command.** `tools/onslurm.sh -c 24 -m 16G -t 00:20:00 -J c2smoke -- python3.12 tools/eval.py c2_respawn q24_combo --maps <15 maps> --jobs 16 --keep --tag c2-smoke-resp`
```
SUMMARY c2_respawn vs q24_combo: 22W-8L (73%)  avg gems 823 vs 623  avg deaths 5.9 vs 7.9  botFaults(A) 0
```
- **Same 30 map-sides in the earlier runs:**
  - h_respawnfix vs tb_merge_b (`q21-all`): 22W;
  - q24_combo vs tb_merge_b (`gate-q24-all`): 17W.
  - The opponents differ, so this is a mechanism check, not a strength estimate.
- **Per game (means; us / them in the same games):**

| Run | Clears | Camp deaths | Deaths | fuelExhausted |
|---|---|---|---|---|
| c2_respawn vs q24_combo | 46.9 / 40.8 | 1.4 / 1.2 | 5.9 / 7.9 | **13.3** / 11.6 |
| h_respawnfix vs tb_merge_b | 47.5 / 42.6 | 2.0 / 1.3 | 9.8 / 11.1 | 92.6 / 69.3 |
| q24_combo vs tb_merge_b | 43.2 / 43.4 | 1.0 / 1.1 | 6.7 / 8.1 | 13.5 / 61.4 |

  - **Fuel.** The h_respawnfix report's fuel watch item (+6.7%) is absorbed by q24's fuel caches: 13.3/game vs q24_combo's own 13.5 vs tb_merge_b.
- **Freeze.**
  - **≥ 150 rounds:** c2 26,268 champion-rounds (11.6%) vs q24_combo 27,721 (12.2%) in the same games.
  - **≥ 300 rounds:** 19,574 vs 21,297.
  - **Reference, same 30 map-sides:** q24_combo had 42,797 in `gate-q24-all`; h_respawnfix had 22,776 in `q21-all`.
  - **Concentration.** 7,996 of c2's total is the standoff game above. Without it c2 has 18,272.
- **Analysis.** `tools/analyze_match.py --summary matches/c2-smoke-resp --games` gives wins at 907 vs 491 gems and losses at 594 vs 987.
  - **Losses 01broken-curve A/B, 02geodes A, 00packs A and 00expanse B are fight-decided:** K/D 2/14, 5/12, 1/9, 4/20 and 1/8 respectively, with 0-711 frozen rounds.
  - **Close races:** 00corners A 985-1,021 and 02harvest B 775-1,013.
  - **02tangle B (387-736) is the only freeze-heavy loss: 5,811 / 3,493.** 02tangle is the map where the h_respawnfix traces found the pre-existing target flip-flop (G25 <-> G27, 467 turns). q24_combo also froze 2,984 there vs tb_merge_b.

| Map | Side | c2_respawn vs q24_combo | h_respawnfix vs tb_merge_b | q24_combo vs tb_merge_b |
|---|---|---|---|---|
| 01yellow-brick-road | A | W 594-54, 2122 / 4749 | W 696-206, 571 / 2714 | W 26-0, 8648 / 9411 |
| 01yellow-brick-road | B | W 15-4, 7996 / 8154 | W 1020-209, 0 / 1894 | W 0-0, 9335 / 9135 |
| 01islands | A | W 1057-583, 0 / 171 | W 1050-887, 0 / 0 | L 940-1008, 1085 / 0 |
| 01islands | B | W 1052-511, 152 / 161 | W 1006-561, 0 / 154 | W 1012-905, 0 / 310 |
| 01broken-curve | A | L 339-1086, 711 / 0 | L 707-1105, 0 / 0 | W 1013-549, 0 / 167 |
| 01broken-curve | B | L 659-1002, 0 / 0 | W 1013-496, 0 / 0 | W 1063-217, 0 / 1787 |
| 02geodes | A | L 610-1022, 0 / 167 | W 1100-532, 0 / 0 | W 1002-921, 183 / 0 |
| 02geodes | B | W 1007-864, 0 / 1063 | L 997-1005, 0 / 0 | W 1000-656, 498 / 2648 |
| 00quarry | A | W 1010-340, 0 / 1089 | W 1027-573, 0 / 680 | L 362-1000, 216 / 290 |
| 00quarry | B | W 1000-240, 0 / 0 | W 1012-142, 0 / 596 | W 1019-763, 1115 / 981 |
| 00packs | A | L 328-976, 0 / 0 | W 710-606, 466 / 543 | L 559-921, 0 / 0 |
| 00packs | B | W 1036-122, 0 / 201 | W 1004-188, 0 / 0 | W 804-102, 307 / 430 |
| 02harvest | A | W 1009-581, 360 / 0 | L 821-834, 154 / 753 | L 706-860, 554 / 526 |
| 02harvest | B | L 775-1013, 355 / 335 | W 1052-778, 402 / 1202 | L 691-981, 589 / 1022 |
| 00expanse | A | W 1038-676, 672 / 572 | W 979-877, 207 / 328 | W 1011-581, 0 / 771 |
| 00expanse | B | L 665-1038, 464 / 0 | W 1005-785, 0 / 649 | L 726-1036, 158 / 218 |
| 00reverse-spiral | A | W 1020-295, 0 / 0 | W 642-433, 0 / 244 | L 301-769, 344 / 0 |
| 00reverse-spiral | B | W 853-624, 0 / 202 | W 799-393, 163 / 180 | W 1013-471, 155 / 379 |
| 00corners | A | L 985-1021, 0 / 0 | L 369-645, 3700 / 2200 | W 1029-395, 190 / 548 |
| 00corners | B | W 1013-948, 211 / 0 | W 1028-372, 228 / 571 | W 1021-231, 177 / 1600 |
| 00rushbait-v2 | A | W 1003-805, 305 / 0 | W 260-197, 2907 / 2764 | W 808-371, 1007 / 1415 |
| 00rushbait-v2 | B | W 867-568, 376 / 177 | W 1001-805, 505 / 725 | L 425-751, 677 / 1638 |
| adgato-gemcombat5 | A | W 1001-497, 1668 / 1544 | W 1001-609, 313 / 416 | W 1078-469, 2441 / 2273 |
| adgato-gemcombat5 | B | W 1113-133, 0 / 151 | L 840-1064, 1727 / 2868 | L 385-1008, 6569 / 5034 |
| 00rows | A | W 868-860, 155 / 201 | L 257-768, 1867 / 0 | L 582-874, 0 / 0 |
| 00rows | B | W 1017-864, 0 / 160 | W 912-853, 0 / 190 | W 807-466, 0 / 1980 |
| 01corridors | A | W 620-348, 1864 / 1748 | L 218-728, 4100 / 2008 | L 455-627, 2736 / 2000 |
| 01corridors | B | W 752-180, 1875 / 1778 | W 732-351, 1324 / 1516 | W 433-356, 1556 / 2504 |
| 02tangle | A | W 1008-713, 1171 / 1605 | L 731-1017, 2955 / 1152 | L 793-1001, 1273 / 0 |
| 02tangle | B | L 387-736, 5811 / 3493 | W 1025-745, 1187 / 819 | L 600-1006, 2984 / 158 |

Cells: result and tributed gems (us-them), then frozen champion-rounds us / them.

## Caveats and next steps
- **Not gated.** This is a merge check plus a 30-game smoke on maps chosen *because* the fix acts there, so 22W-8L overstates the general effect. Next is the LOOP.md §4 gate vs q24_combo:
  - `--maps all` with ≥ 82/140;
  - a paired gauntlet ≥ q24_combo's 174/200;
  - a `--release` game;
  - an analysis that includes `tools/freeze_metric.py`.
- **Open hypothesis: contested-capture standoff.** On a long RewardAvailable group with an enemy on the region, the capture never completes and both teams idle (the 15-4 game: 1,650 rounds). Fixing it means abandoning the capture after N rounds with an enemy on the region, or contesting the blocker. It is not ported or changed here. The fix should stay behind its own flag, separate from `RESPAWN_FIX`.
- **Remaining stalls the patch does not touch:** the 02tangle target flip-flop and 01corridors (about 1,870 frozen rounds per side for both bots). These match the h_respawnfix report's "universal oscillation guard" and "target-choice hysteresis" hypotheses.
- **Debug traces.** The throwaway trace fork used for the B-game investigation (`bots/c2dbg_trace`) was deleted. Its games are kept in `matches/c2-dbg-b`, `c2-dbg-b2` and `c2-dbg-b3` (`team-b.stdout` is NUL-padded; strip `\x00` before parsing).

## Review fixes (adversarial merge review, 31 Oct)
**No code defects found; `src/` is unchanged** (bot.py md5 still `83d844c8fece0d248ba5d6a044c41cb6`; main/draft/randomness byte-identical to q24_combo).

How it was checked (independent of the sections above):
- **Hunk-by-hunk.** `diff -u tb_merge_b h_respawnfix` has 8 code hunks (constant, `Group.seen` slot + init, `turn_quiet` init, `G.seen = rnd` in observe, `play_turn` wrapper + `resp_mask` + `leave_respawn_tile`, `turn_quiet` after `threats()`, push-back gate, guess gate, farm-goal mask). All are in `diff -u q24_combo c2_respawn`.
- **AST, per function, docstrings stripped** (tb_merge_b / h_respawnfix / q24_combo / c2_respawn). Every function h_respawnfix did not touch is identical to q24_combo. `leave_respawn_tile`, `resp_mask`, `play_turn` and `Group.__init__` are identical to h_respawnfix. `observe_slow` is identical to h_respawnfix's `observe`. `observe_fast` = q24_combo + the one `G.seen = rnd` line, at the same point (after a successful `state()` read). `play_turn_main` = q24_combo's old `play_turn` + exactly h_respawnfix's 4 hunks.
- **Integration points.**
  - `G.seen` is written in both observes (R1 is correct; without it gate (d) would be dead under `OBSERVE_FAST`).
  - `turn_quiet` uses `threats_fast`'s `incoming` / `enemies`, which have tb_merge_b's semantics.
  - The `not RESPAWN_FIX` short-circuit makes `blocks_respawn` dead code only when the flag is on.
  - Every early return before `threats()` leaves `turn_quiet` False: first turn, dead, channelling.
  - `group_balance` / regroup `retreat` run only inside `handle_enemies`, i.e. with enemies in sight, so those turns are never quiet.
  - `leave_respawn_tile` reads no h_fightfuel cache. After it, main.py runs only `build_static_fields`, which is position-independent.
- **Static checks.** All 4 files compile (`py_compile` to a scratch dir, no `__pycache__` written into `src/`). No `self.` attribute is read without being set. Debug flags are all off.

Corrections to the text above (wording only):
- **R3 "never fires mid-chip" is overstated.** A chip turn whose first hit lands on a sleeping camp without moving is quiet, and `can_move()` is still True, so `leave_respawn_tile` is evaluated. It can only act if that tile belongs to a *different*, Respawning group (the chip target is Alive). It then steps to a tile that keeps the target in range. Harmless.
- **R4.** `self.target` (step-off direction) is last turn's target when the turn returned before `choose_target`: a tribute walk, a recall, or a low-HP walk home. It only orders the candidate tiles. This is the same as in h_respawnfix.

Gold-play check (`no_tribute` map, not covered by the smoke). Local `cambc run`, 0 crashes, empty stdout:

| Game (A vs B), 02guardians | Result (gold) | Kills A/B | Folder |
|---|---|---|---|
| c2_respawn vs q24_combo | c2 W 13,401-3,367 | 37/5 | `matches/c2rev-guard-A` |
| q24_combo vs c2_respawn | c2 L 1,979-18,101 | 42/2 | `matches/c2rev-guard-B`, re-run identically with stats in `matches/c2rev-guard-B2` (c2 frozen 313 champion-rounds) |
| q24_combo vs q24_combo (control) | B L 1,430-18,479 | 51/0 | `matches/c2rev-guard-mirror` |

- **The map is side-A-dominant for the q24 family.** In the mirror, B dies 53 times.
- **c2's B-side loss is fight-decided** (42 champion deaths), and it is smaller than the mirror's. No sign that dropping h_goldtie's in-turn push-back hurts gold play.
- These are 3 games, a mechanism check only, not strength evidence. The §4 gate's `--maps all` covers all 3 `no_tribute` maps.
