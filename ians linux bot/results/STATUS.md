# Loop status (updated every tick)

- **Last update:** 2026-10-31 ~20:15 EDT, the **handoff from the dev PC to the cluster agent**. No loop is running anywhere right now: the dev-PC session ended, and its scheduled tick and background workflows stopped with it.
- **Champion / live bot:** `tb_merge_b` (Python), website **v2**, Active / Verified. It was our **Sprint 3 entry** (locked 31 Oct 23:59 GMT).
- **Ladder:** v2 is **43W-17L** (72%) over 12 sets. Rating ~**1,491**, a plateau around 1,490-1,497 as of 23:40 UTC.
  - By team size: 3-pick 6/12, 4-pick 14/16, 5-pick 23/32.
  - Set losses at ~1,500 came against the **mirror meta comp** (Q19).
  - 02the_pack was lost twice on the 0-0 gold tiebreak.
  - Log: `results/ladder-games.jsonl` (125 games); summarise with `python3 -I tools/ladder_log.py`.
- **Upcoming locks:** International qualifiers 4 Nov, UK qualifiers 11 Nov, finals 18 Nov. Check https://2026a.battlecode.co.uk/game/tournaments for exact times.

## Resume here (in order)
1. **Q24 combined candidate.** Build tb_merge_b + LOCK_MEMORY_FIX (h_3pick) + gold play (h_goldtie) + early-fight rule (h_earlyfight_all) + fuel caching (h_fightfuel). Then run the analysis session and the full gate (LOOP.md §4: ≥ 82/140 on all maps, plus a paired gauntlet). Inputs: `results/experiments/2026-10-31-batch1-interim.md`.
2. **Gauntlet baseline for the champion.** `python3 -I tools/gauntlet.py tb_merge_b --pool sf_bank,tb_merge_a,tb_aggro,imit_test,lad_vcst --maps sprint --note "baseline tb_merge_b"`. It was started but never written; `results/gauntlet.jsonl` doesn't exist yet.
3. **Finish batch 1's analysis sessions** (reports for h_3pick, h_goldtie, h_earlyfight, h_fightfuel, h_antistun). The raw stats were in the dev PC's gitignored `matches/`. Re-run the evals with `--keep` on the cluster if you need the games.
4. **Ladder monitoring.** After `cambc login` (a human runs it once), use `cambc matches` and `cambc ladder` (see `docs/CLI_ONLY.md`) to pull new games into `results/ladder-games.jsonl`.
5. **Q14 / Q19, real replays.** Download our losses to "test" and to the mirror-meta teams, and study how they beat us.
6. **C++ track.** `bots/cpp_port` is at parity (sprint 20-20, 0 fuel exhaustions). The verify/fix phases never ran. It's the platform for compute-heavy ideas (Q25 etc.).

## Leftover bot dirs from interrupted work
- `g_earlyfight`, `g_fightfuel`: gate snapshots, never evaluated.
- `g_ef_ff`: merge attempt with a stale NOTES.md and unverified state. Rebuild it rather than trust it.
- `cpp_bench`, `cpp_scratch*`: C++ fuel micro-benchmarks and scratch work.
- `h_earlyfight_diag`: diagnostic build only; never evaluate it.
