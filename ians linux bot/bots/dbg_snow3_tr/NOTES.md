# c2_3pick: c2_respawn + q24's push-back off the target group's own camp tiles, 3-champion teams only

**Lineage.** `python3.12 tools/newbot.py c2_respawn c2_3pick` (champion, website v4). Only `src/bot.py` differs;
`main.py`, `draft.py` and `randomness.py` are byte-identical to c2_respawn. The full study (diagnosis, ablations,
screens, final runs) is `results/simulated-matches/2026-11-01_0531_c2_3pick/notes.md`. For c2_respawn's own patch see
`bots/c2_respawn/NOTES.md`.

| File | Change |
|---|---|
| `src/bot.py` | c2_respawn + the patch below (2,776 -> 2,793 lines). md5 `c792936e54eed74028d2fed80c0794be` |

## The patch (flag `PUSHBACK_3PICK = True`)
- `self.pb3 = PUSHBACK_3PICK and len(handles) == 3`, set once in `init_static` from `cambc.champions(Team.ALLY)`
  (team size, never map names). Default False in `__init__`.
- The in-turn push-back that c2_respawn turned off (`RESPAWN_FIX` hunk (a)) runs again when `self.pb3` and the
  champion stands on a tile of **its own target group** `G`:
  `if ((self.pb3 and G.tiles.is_set(pos)) or not RESPAWN_FIX) and G.status != 1 and all_camp_tiles(pos) and blocks_respawn(pos)`.
  The body is q24_combo's: move to the adjacent non-camp tile nearest `G.center` and end the turn.
  `blocks_respawn` keeps h_goldtie's gold-play narrowing, as in q24.
- Everything else is c2_respawn: the end-of-turn step-off, the farm-goal mask and the fresh-read gate stay on
  for every team size. On 4- and 5-champion teams the code path is c2_respawn's apart from one attribute read.

## Why (summary of the experiment)
- c2_respawn regressed on 3-pick maps against the mirror-draft tb_merge family: 10/24 vs tb_merge_b and 10/24
  vs tb_merge_a, where q24_combo won 19/24 and 18/24.
- Hunk ablation (24 three-pick map-sides vs tb_merge_b): push-back restored 19/24; step-off off 10/24;
  farm mask off 13/24; fresh-read gate off 11/24; all four off 19/24 (game-for-game = q24_combo).
  Trace games: the step-off with an enemy in sight (H1) is rare (46 turns in 24 games) and not the cause.
- Push-back categories: target-group tiles only 18/24, other groups' tiles only 15/24, push-back that keeps
  acting after the move 14/24. Whole restore vs c2_respawn on 3-pick: 9/24; target-only: 12/24.
- The whole restore on all maps costs 13 of 84 five-pick games vs tb_merge_b (64 -> 51), hence the team-size key.
- The whole restore (iteration 1) lost 6 of 48 against tb_merge-logic bots with ladder 3-pick drafts
  (h3_csv/h3_tvv); the target-only rule (this version) is neutral there (45 vs 44 of 48).

## Validation
- `c2_3pick vs tb_merge_b --maps all`: **106W-34L** (c2_respawn 98). 3-pick 18/24 (c2 10); 114 of 116
  four/five-pick results identical to c2_respawn's.
- `c2_3pick vs c2_respawn --maps all`: **70W-70L**; 56 of 58 four/five-pick maps split 1-1 (mirror), 3-pick 12/24.
  The LOOP.md §4 head-to-head (>= 82/140) cannot be met by a change scoped to 24 of 140 games.
- Release game (02arena vs c2_respawn): 0 crashes, empty stdout/debug, botFaults 0, fuelExhausted 0.
- fuelExhausted in the 140 games vs c2_respawn: 837 vs 857.

## Throwaway bots from this study (not for submission; can be deleted)
`c2p3_noA/noB/noC/noD/off` (one RESPAWN_FIX hunk off each, or all), `c2p3_pbT/pbO/pbK` (push-back categories),
`dbg_c2p3_tr` / `dbg_q24p3_tr` (debug_block per-turn traces of c2_respawn / q24_combo).
