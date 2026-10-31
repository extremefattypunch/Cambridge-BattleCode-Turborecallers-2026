# Loop status (updated every tick)

- **Last tick:** 2026-10-31 19:16 EDT.
- **Champion:** `tb_merge_b` (Python), website v2, **Active / Verified**.
- **Ladder:** v2 is **36W-9L** (80%) over 9 sets. Rating 1,407 → **1,493**.
  - By team size: 3-pick **6/11**, 4-pick 12/14, 5-pick 18/20. 3-pick maps hold 5 of the 9 losses.
  - 02the_pack was lost **twice on the 0-0 gold tiebreak**.
  - Run `python3 -I tools/ladder_log.py` for the full list; the log is `results/ladder-games.jsonl` (110 games).
- **Next lock:** Sprint 3, 19:59 EDT. **Upload freeze is active (18:59–19:59).** After that: International qualifiers 4 Nov, UK qualifiers 11 Nov, finals 18 Nov.
- **Running:**
  - strategy batch 1 (`wt89dw4p0`): h_3pick (Q18), h_goldtie (Q2), h_earlyfight (Q12), h_antistun (Q15), h_fightfuel (Q13). Each gets a test plus an independent analysis and a report in `results/experiments/`.
  - C++ port track (Q11).
- **Blocked:** Q14 (the real replays of the losses to "test"). Bundle downloads fail under site load; retry after the lock, or use the CLI once `cambc login` is done.
