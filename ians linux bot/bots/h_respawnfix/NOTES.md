# h_respawnfix: universal respawn-rule movement fix (STRATEGIES Q21)

Base: `bots/tb_merge_b` (champion), same draft. Only `src/bot.py` changed; every change is tagged
`h_respawnfix` and switched by `RESPAWN_FIX = True`. Report: `results/simulated-matches/2026-11-01_0126_h_respawnfix/notes.md`.

## The engine rule
"The group respawns together after rewards are claimed ... Any occupied spawn tile delays the entire
group" (GameRules, Camps & capture). So an occupied spawn tile matters **only while the group is
Respawning** (`CampGroupRespawning`). Dead members of a group that is still Alive never respawn on
their own, and standing on a RewardAvailable group's tile is a capture.

## Two freeze mechanisms in tb_merge_b (found with per-turn traces on 01yellow-brick-road)
The map has two 30-tile rows of gold clusters (one camp group each) splitting the map; every path
crosses dead tiles of a half-cleared row, and the rows' centres sit next to each spawn.
1. **Respawn-rule 2-cycle.** `if G.status != 1 and all_camp_tiles.is_set(pos)` pushed the champion off
   *any* camp tile (dead member of an Alive group, any group) toward `cheb(G.center)` and **returned**.
   The planner's path crossed that tile, so: step on, pushed back, step on ... The push turn returns
   before `note_progress`, and the step-on turn counts as progress, so the stuck guard never fires.
   Example (trace): slot 4 `(10,13) -> (11,12)` (dead tile of the y=12 row, target = the y=17 row)
   `-> pushed to (10,13)` every 2 rounds from r~360 to r2000.
2. **Unseen-alive guess undone every turn.** Within 3 of `G.center` with no live camp of G in sight,
   the farming code guessed "respawning" (`status = 2, ready = rnd + 10`) and returned. For a long
   group whose live members are out of sight, `observe()` re-reads the engine state (Alive) next turn
   and resets `status = 0`, so the guess fires again: the champion never moves (all 5 of side B froze
   at their spawn from r~13 next to the row's centre `(34,12)`).

## The fix (final = v3)
- **No in-turn push-back.** The old rule is disabled.
- **End-of-turn step-off (`leave_respawn_tile`, wrapper around `play_turn`).** Only if the turn ends
  stationary (`can_move()` still true), quiet (no enemy in sight, no camp hitting us), not channeling,
  and the tile under us belongs to a group whose engine state is `CampGroupRespawning`: step to an
  adjacent free non-camp tile, preferring one that keeps a live camp of the target in attack range,
  then the one closest to the target's centre.
- **Do not park on respawning tiles (v3).** Farming movement goals other than the live camps
  themselves (ranged stand-off tiles, bush tiles) exclude spawn tiles of groups we believe are
  respawning (`resp_mask`), when anything else is left.
- **Unseen-alive guess only without a fresh engine read.** `Group.seen` = round of the last
  `state()` read in `observe()`; the guess is skipped when the state was read this turn (it said Alive,
  so the live members are elsewhere and `alive_tiles` paths to them).

## Iterations
| Version | Change | 01yellow-brick-road (A / B) | sprint + ybr vs tb_merge_b |
|---|---|---|---|
| v1 | precise trigger (Respawning only) + end-of-turn step-off | 23-0 W / 0-4 L, both still frozen ~90% | not run |
| v2 | + fresh-read gate on the unseen-alive guess | 258-0 W / 464-600 L | 25W-17L (60%), `matches/q21-v2-sprint` |
| v3 (final) | + no parking on respawning tiles, in-range step-off | 696-206 W / 1020-209 W | 25W-17L (60%), `matches/q21-v3-sprint` |

v2 traces showed a new 2-cycle caused by the v1 step-off itself: a ranged Vesper parked on a
respawning tile that was a stand-off goal, stepped off at turn end, and the planner moved her back
(45 turns; the alternating move defeats the stuck guard). v3 removes respawning tiles from such goals.

## Tools
- `tools/freeze_metric.py` (new): idle stretches >= 150 rounds from the stats JSON.
- `bots/h_rfx_count`: tb_merge_b + counters only, for the trigger census (`matches/q21-count`).

## Results (final v3, md5 of src/bot.py 8e8fee7b...)
```
SUMMARY h_respawnfix vs tb_merge_b: 92W-48L (66%)  avg gems 736 vs 606  avg deaths 12.8 vs 13.5  botFaults(A) 0   [all 70 maps x 2, matches/q21-all]
SUMMARY h_respawnfix vs tb_merge_b: 25W-17L (60%)  avg gems 704 vs 599  avg deaths 12.7 vs 13.9  botFaults(A) 0   [sprint + 01yellow-brick-road, matches/q21-v3-sprint]
```
- 95% Wilson lower bound 57.5% (gate head-to-head threshold 82/140 met). Sprint subset 23W-17L.
- Release game (01big-world, `--release`): 0 crashes, 0 `bot error`, botFaults 0.
- Trigger census (`bots/h_rfx_count`, `matches/q21-count`): in tb_merge_b's play the push-back fired on a
  non-respawning tile 17,059 times in 135/140 games, and the fresh-Alive "unseen" guess 12,486 times in 38 games.
- Freeze metric (idle >= 150 rounds, excluding 4 structural 0-0 maps): 4.7% of champion-time vs 5.2% for
  tb_merge_b in the same games and 8.4-9.3% in the tb_merge_b mirror. 01yellow-brick-road: ~8,500 -> 286.
- Full analysis: `results/simulated-matches/2026-11-01_0126_h_respawnfix/notes.md`.
