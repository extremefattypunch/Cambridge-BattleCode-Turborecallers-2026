# sf_fuel: changes vs sf_base (INSIGHTS item 1 fuel exhaustion + item 12 stuck guard)

Patch: `matches/patches/sf_fuel.patch` (`diff -ruN bots/sf_base/src bots/sf_fuel/src`).
It touches only `src/bot.py` and one line of `src/main.py`.

## Where the fuel went (measured, 01big-world 100x100, sf_base)
Measured with `cambc.fuel_remaining()` checkpoints. The instrumenter lives outside the patch, in
the session scratchpad, and its output was read from `team-a.stdout` in the replay zip.
- Per-turn average was 1.7-1.8M, with a maximum of 4M. 149 of 214 turns used more than 2M.
  Marcella was suspended 598 times in one game, which means every other round from round 1.
- The biggest costs per turn:
  - `choose_target`: about 730k, or about 25-30k per camp group, because Python bytecode costs
    about 100 fuel and an API call about 3k.
  - The full-map `dist_field` BFS from our position: 600-780k.
  - `go_to`'s BFS: about 200-400k.
  - `observe` plus `threats`: about 200k, rising to 1.2M on camp-heavy maps like 01islands.
- `init_static` costs 3.4-4M on big maps, so turn 1 (5M budget) always ran out.

## Changes (each with its measured effect)

### 1. Static distance-field cache (exact; fuel only)
- **What it does.**
  - `build_static_fields()` builds one `DistanceField` per camp group centre, plus one rooted at
    the altar ring, over the static `walk_block`.
  - It runs from `main.py` after each `play_turn`, only while `fuel_remaining() > 1.0M`. Dead,
    recalling and healing turns build 2-3 fields each.
  - Walking distance is symmetric, so `field_G.get(pos)` equals the old per-turn
    field-from-pos value at `G.center`, and 65535 means unreached.
  - Once all fields are built, `play_turn` skips the per-turn field entirely
    (`field, visited = None, None`).
  - `group_dist()` and `altar_distance(..., pos)` read the cached fields.
- **Build-up phase.** The per-turn field becomes `compute_to(..., dests)`, where dests are the
  centres of the still-unbuilt groups (and the altar ring). It stops as soon as those are
  reached, so it stays exact for them. The build order is altar ring first, then the groups
  farthest from our spawn.
- **Verified exact.** A harness ran the original `choose_target`/`altar_distance` next to the
  new ones every turn, with `--fuel 60M`. It found **0 mismatches** in about 8,000 checks on
  01big-world (full game), 01islands and 02treasure-box (600 rounds each).

### 2. Pruned target scoring (exact; fuel only)
- `target_order()` computes for each group the distance `d` and an upper bound
  `G.value * SCORE_BOUND_MULT / (d + 6)`.
  - This bound is valid because cost >= d + 6, and 1.95 >= 1.5 (reward available) x 1.3
    (current target).
- The list is sorted best-bound-first, with the current target first.
- `choose_target` skips any group whose bound is below the best score so far. Ties go to the
  lowest `G.idx`, so the result is identical to the old idx-order loop.
- `can_reach` is memoised on (group, comp, crystal-or-10-gold). It is a pure function of these.

### 3. Fuel guards (approximate only under fuel pressure)
- `FUEL_SCORE_FLOOR = 800k`: once at least one group has been scored, `choose_target` stops
  scoring and keeps the best so far.
  - On 00lanes, scoring cost about 1.5M. Turns over 2.3M dropped from 185 to 19 in 700 rounds.
- `FUEL_FIRST_TURN_MIN = 2.0M`: if `init_static` leaves less than 2M on turn 1 (big maps), the
  champion only shops on turn 1, and `main.py` spends the rest on static fields.
  - Before, turn 1 always ran out and the champion acted in round 2 anyway. Now it does not
    run out.

### 4. Stuck guard (INSIGHTS item 12), which changes behaviour
- `note_progress()` runs at the end of the farming branch. After `STUCK_TURNS = 6` farming turns
  in a row with no move and no attack on the same group, that group is skipped for
  `STUCK_BAN = 30` rounds (`self.banned`, checked in `target_order`).
- **Cause, found in a replay.** On 01big-world, Vendetta's target camps sat behind walls. The
  static map said they were reachable, but a dynamic blocker cut the only route, so
  `step_toward` found no path. It idled for **1877 of 2000 rounds**.
  - sf_base has the same bug: one champion sat idle 374-977 turns in a profiled game.
- **Effect.** Idle "farm" turns per champion fell from hundreds to at most about 35 per game.

### Tried and reverted
- **Enemy-standoff idle timer.** After 4 enemy-handling turns with no move and no attack,
  `handle_enemies` was skipped for 10 rounds. It did remove the chase/retreat deadlocks
  (300-590 idle turns per champion on 01islands, in both bots). But in the quick A/B it went
  **10W-14L**, and deaths to champions doubled (28.7/game vs 13.5). 01elk-arena went from 2 wins
  to 2 losses with 64-69 deaths. It was removed.
  - **Open problem for whoever owns item 9.** In self-play both sides freeze. One "chases" an
    unreachable enemy (for example across a hole), while the other "retreats" but finds no
    tile with less danger.
- **Not attempted.** Greedy steps on the static fields for long `go_to` trips (worth about
  200-400k per turn). It would change movement, and the original author warned about this.

## Results
- Quick A/B, after changes 1, 2 and 4 (with the old 350k score floor):
  `SUMMARY sf_fuel vs sf_base: 13W-11L (54%)  avg gems 531 vs 419  avg deaths 14.3 vs 16.0  botFaults(A) 0`
  - fuelExhausted/game: **12.3 for sf_fuel vs 188.5 for sf_base** in the same games. The rest
    is on 00lanes and 01islands.
- Single games (one sample each, profiled copies):
  - 01big-world: team exhaustions 60 vs 2560, gems 1064 vs 282.
  - 01islands: exhaustions 72 vs 2717, gems 1024 vs 312.
- **Final sprint A/B** (final code, 40 games):
  `SUMMARY sf_fuel vs sf_base: 24W-16L (60%)  avg gems 556 vs 390  avg deaths 11.9 vs 14.8  botFaults(A) 0`
  - fuelExhausted/game: **6.5 for sf_fuel vs 180.5 for sf_base** in the same games, a 96% cut.
    | Map | sf_fuel | sf_base |
    |---|---|---|
    | 01islands | 97 | 4504 |
    | 01big-world | 36 | 2198 |
    | 00lanes | 106 | 418 |
    | 01concentrated-wealth | 9 | 45 |
    | 02harvest | 0 | 24 |
  - Our other metrics from match_metrics.py:
    - mean tribute 21.1 (base vs starter: 18.9);
    - deaths_by_camp 0.8/game (1.4);
    - gemsLost_to_camp 2.6/game;
    - gemsLost_to_champion 49/game. That is self-play, so it is not comparable to the
      13/game baseline against starter.
  - Won both sides on 01big-world, 01islands, 00lanes, 00quadrants, 00corners and 01elk-arena.
- **Cross-check vs tb_economy** (quick):
  `SUMMARY sf_fuel vs tb_economy: 20W-4L (83%)  avg gems 930 vs 397  avg deaths 6.7 vs 49.1  botFaults(A) 0`
  - sf_base got 18W-6L, avg gems 885 vs 413, with the same command (folder
    `matches/sf_draft-xeco-base`). fuelExhausted/game: 9.1 for sf_fuel vs 148.2 for tb_economy.
- **Big maps not in the sprint set** (02treasure-box and 00expanse, both sides): **1W-3L**, and
  fuelExhausted was 0 for sf_fuel.
  - 02treasure-box was lost on both sides (268 vs 713, and 0 vs 1002 with 40 deaths).
  - The same map with the stuck guard disabled went 1W-1L (657 vs 77, 98 vs 801).
  - These are 2-game samples in chaotic self-play.
- **Stuck guard on its own** (quick A/B with `STUCK_TURNS` disabled, everything else equal):
  `14W-10L (58%)  avg gems 537 vs 416`.
  - That is the same W-L as the final build's 24 quick-map games (14W-10L), so the guard is
    W-L neutral in self-play.
  - It is kept because it removes a documented pathology: one champion idle for up to 1877 of
    2000 rounds. It is optional for the merge (piece (f)).

## Merge notes (important)
- **Never read `field` or `visited` directly in `play_turn` after this patch.** Once the static
  fields exist, both are `None`. During the build-up, the field is exact only for the unbuilt
  group centres and the altar ring.
  - Use `self.group_dist(G, pos, field, visited)` or `self.altar_distance(field, visited, pos)`.
    Or add another static field: append a key to `sf_todo` and roots in `build_static_fields`
    and `sf_dests`.
  - This matters for the banking (item 2) patch if it wants path distance to an altar.
- **`choose_target`.** Only the loop header (it now iterates `target_order(...)`, with the bound
  skip and the fuel floor) and the final `if score > best_score` tie-break changed. The scoring
  body is untouched. If another patch changes the scoring, keep the bound valid:
  - multipliers <= 1 (item 13's x0.4/x0.6/x0.5) are fine;
  - any new multiplier > 1 must be folded into `SCORE_BOUND_MULT`;
  - cost terms must stay >= 0;
  - if value weights gold above 0.25, compute the bound from that value instead.
  - When in doubt, raise `SCORE_BOUND_MULT`, which only costs fuel.
- **Independent pieces.** Each could be dropped alone:
  - (a) the static cache plus the partial field;
  - (b) pruning (needs `group_dist`, which falls back to the per-turn field if (a) is dropped);
  - (c) the `can_reach` memo;
  - (d) the score fuel floor;
  - (e) the first-turn guard;
  - (f) the stuck guard (`note_progress`, `banned`, and the last line of `play_turn`).
- `main.py` gains one line: `bot.build_static_fields()` after `bot.play_turn()`.
