# placebo_a: noise-floor control (not a candidate)

Made with `tools/newbot.py q24_combo placebo_a` for the gate-calibration experiment `results/experiments/2026-11-01-placebo.md`. Never submit it.

- **Change:** `src/main.py` calls `cambc.round_number()` once at the start of every play turn and discards the result. That is one extra behaviour-free API read.
- **Fuel cost:** about 0.3k to 5k per turn, varying by turn (about 0.1% of the 2.5M budget). This was measured from the replay `.fuel` streams against the q24_combo mirror, before the games diverge.
- **Unchanged:** `src/bot.py`, `draft.py` and `randomness.py` are byte-identical to q24_combo's.
  - The RNG is position-seeded.
  - The only `id()`-keyed memos use the long-lived `self.comps` components.
  - So decisions can differ from q24_combo's only through fuel-dependent branches: `FUEL_*` floors, the `build_static_fields` loop, `FUEL_FIRST_TURN_MIN`, and suspensions.
- **Result:** vs q24_combo on all maps, 66W-74L. 126/140 games were identical to the mirror and 4 outcomes flipped. vs tb_merge_b, 85W-55L, against the gate's 87.
