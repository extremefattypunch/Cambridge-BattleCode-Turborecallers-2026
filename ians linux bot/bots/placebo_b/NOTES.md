# placebo_b: noise-floor control (not a candidate)

Made with `tools/newbot.py q24_combo placebo_b` for the gate-calibration experiment `results/experiments/2026-11-01-placebo.md`. Never submit it.

- **Change:** `src/main.py` runs `_burn(PLACEBO_BURN)` at the start of every play turn. That is a pure-Python summation loop of 100 iterations, with the result discarded.
- **Fuel cost:** about 69-76k per turn (about 3% of the 2.5M budget). This was measured from the replay `.fuel` streams against the q24_combo mirror, before the games diverge.
  - The task asked for "a few thousand iterations". At the measured ~700 fuel per iteration, 2,000-3,000 iterations would cost about 1.4-2.1M, i.e. 55-85% of the turn budget. That would be a real handicap, not a placebo, so 100 was used.
  - The main.py comment, from the earlier attempt, records 0.98M for 1,000 iterations and 2.07M for 2,000. Those two figures were not re-measured.
- **Unchanged:** `src/bot.py`, `draft.py` and `randomness.py` are byte-identical to q24_combo's. Decisions can differ only through fuel-dependent branches (see placebo_a's NOTES).
- **Result:** vs q24_combo on all maps, 68W-72L. 77/140 games diverged from the mirror and 28 outcomes flipped (+13/-15). vs tb_merge_b, 90W-50L, against the gate's 87.
- **Template:** this is the template for a "placebo replicate" of a candidate. Fork the candidate, add the same burn to its main.py, and re-run it vs the champion (see the experiment report's recommendation).
