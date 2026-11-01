# h_earlyfight: opening-phase group fight rule (STRATEGIES Q12)

Base: `bots/tb_merge_b` (copied with `tools/newbot.py`). Only `src/bot.py` changed; the draft is unchanged.

## Evidence that motivated it
- `matches/final-mergeb-all` (tb_merge_b vs sf_bank, 70 maps x 2): the clearest early-fight loss is
  00dunes B (196-1036): 7 of our champion deaths before r300 against their 1, their Vendetta 9-0.
- Early deaths alone do not predict losses vs sf_bank (wins 1.26 early deaths/game, losses 1.13), but
  the *enemy's* early deaths do (wins 1.82, losses 0.60). Against imit_test it is the same picture:
  their early deaths 3.74/game in our wins vs 1.00 in our losses. So "winning the early fights" means
  converting fights, not just avoiding them.
- Diag games (per-turn log of position / hp / allies / enemies for r<320; `DIAG` flag, off in tests),
  `matches/h_earlyfight-diag/` (00dunes B, 01starfish B, 00lost-world B, 02stalactites A vs sf_bank).
  Every early champion death had the same shape:
  - a lone, mostly **non-dash melee** (Ryth, Marcella, HoR) stands **adjacent to an enemy melee and
    trades for 5-11 turns** (`adjacent_melee` stand-and-trade: it only lets a champion with a dash
    or next to spawn walk away) while **2-5 enemies are within 6** and 0-1 allies within 8;
  - or a champion **chases a low-hp target into 3-4 enemies** (the kill-time ratio is small because
    the target is nearly dead; the numbers check `len(near) > n_allies + 1` is applied only after the
    engage decision);
  - or 3-4 of our champions are within 2-6 tiles of a 2v4 / 3v4 fight but **nobody commits**:
    each ally's own ratio `my_ttk / their_ttk` is ~1.0 > 0.85 because their_ttk assumes all enemy
    damage lands on that one ally, and allies only count within 4 tiles at 0.7 strength.

## What changed (only for `round < EARLY_ROUNDS` = 300)
In `handle_enemies` the local fight is scored by `group_balance()`:
`(sum hp x sum dps)` of me + allies within `GROUP_R` (7) that are not recalling/teleporting, divided by
the same for the enemies within the engage radius (6; dps x CHAN_THREAT). dps = strength + 0.15 focus
for every unit (the same `enemy_dps` estimate on both sides).
- **Advantage** (>= `GROUP_ADV` 1.4): engage limit `+ GROUP_ENGAGE_BONUS` (0.4) on every target,
  `clearly_losing` forced False, always stand and trade with an adjacent melee. Every ally sees
  roughly the same local picture, so the group collapses on the fight together.
- **Disadvantage** (<= `GROUP_DISADV` 0.75): no new engagement unless the target dies to the next hit;
  `clearly_losing` forced True; an adjacent melee is only traded with when it dies in 2 hits;
  otherwise, when an enemy is within `GROUP_REGROUP_D` (4) or threatens us, step away with
  `retreat(..., rally)` whose last tie-break is distance to the nearest visible ally instead of our
  spawn (spawn when no ally is visible).
- In between: unchanged tb_merge_b behaviour.

After round 300 the bot is byte-for-byte tb_merge_b's logic.

## Results
See the eval lines below (filled in after the runs).
