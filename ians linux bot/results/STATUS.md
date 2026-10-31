# Loop status (updated every tick)

- **Last tick:** 2026-10-31 18:50 EDT.
- **Champion:** `tb_merge_b` (Python), website v2, **Active / Verified**.
- **Ladder:** v2 is **24W-6L** over 6 sets (5-0, 5-0, 3-2, 4-1, 4-1, 3-2). Rating 1,407 → **1,465**.
  - By team size: 3-pick 3/6, 4-pick 10/11, 5-pick 11/13. **3-pick is the weak spot.**
  - Losses:
    - 02arena and adgato_gemcombat4 vs "test";
    - 00galaxy and 00swirl vs C-- (Vesper, Tavi, Marcella, Willow, Vendetta);
    - 01broken_curve vs Blame the Altar (3-pick);
    - 02the_pack 0-0, lost on the gold tiebreak (3-pick).
  - Log: `results/ladder-games.jsonl` (95 games).
- **Next lock:** Sprint 3, 19:59 EDT. **Upload freeze is active (18:59–19:59).** After that: International qualifiers 4 Nov, UK qualifiers 11 Nov, finals 18 Nov.
- **Running:**
  - strategy batch 1 (`wt89dw4p0`): h_3pick (Q18), h_goldtie (Q2), h_earlyfight (Q12), h_antistun (Q15), h_fightfuel (Q13). Each gets a test plus an independent analysis and a report in `results/experiments/`.
  - C++ port track (Q11).
- **Blocked:** Q14 (the real replays of the losses to "test"). Bundle downloads fail under site load; retry after the lock, or use the CLI once `cambc login` is done.
