# Loop status (updated every tick)

- **Last tick:** 2026-10-31 19:46 EDT.
- **Champion:** `tb_merge_b` (Python), website v2, **Active / Verified**.
- **Ladder:** v2 is **43W-17L** (72%) over 12 sets. Rating is about **1,491**, a plateau around 1,490-1,497.
  - By team size: 3-pick 6/12, 4-pick 14/16, 5-pick 23/32.
  - Recent set losses (2-3) were to the **mirror meta comp** (Halma _und _Oleck, The Dreamyard), now hypothesis Q19.
  - 02the_pack has been lost twice on the 0-0 gold tiebreak.
  - Run `python3 -I tools/ladder_log.py` for the full list (125 games logged).
- **Next lock:** Sprint 3, 19:59 EDT. **Upload freeze is active (18:59–19:59).** After that: International qualifiers 4 Nov, UK qualifiers 11 Nov, finals 18 Nov.
- **Running:**
  - strategy batch 1 (`wt89dw4p0`): h_3pick (Q18), h_goldtie (Q2), h_earlyfight (Q12), h_antistun (Q15), h_fightfuel (Q13). Each gets a test plus an independent analysis and a report in `results/experiments/`.
  - C++ port track (Q11).
- **Blocked:** Q14 (the real replays of the losses to "test"). Bundle downloads fail under site load; retry after the lock, or use the CLI once `cambc login` is done.
