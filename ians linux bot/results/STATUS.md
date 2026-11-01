# Loop status (updated every tick)

- **Last update:** 2026-10-31 21:30 EDT: **q24_combo promoted and uploaded (website v3)**. The **cluster agent** (FASRC Cannon) has taken over from the dev PC. A session cron tick fires at :17 and :47 each hour while the session is alive.
- **Champion / live bot:** `q24_combo` (Python), uploaded as website **v3** at 01:24 UTC on 1 Nov after a full gate pass (87/140 vs tb_merge_b, gauntlet 174 vs 158; `results/READY.md`). Confirm v3 shows Active / Verified on the next ladder pull. The previous bot `tb_merge_b` (v2) was our Sprint 3 entry.
- **Ladder (pulled 1 Nov ~01:10 UTC via `python3.12 tools/ladder_pull.py`):** v2 is **62W-33L** (65%), rating **1,501** after the 01:00 UTC set. The latest 35 games went 19-16. 02treasure_box was lost a **third** time (138-1005 vs EXP'D), and 00quadrants again by 26 gems (Q27, Q28).
  - By team size: 3-pick 11/17, 4-pick 17/21, 5-pick 31/52.
  - New loss patterns: **02gift_wrapping** (0 clears all game, lost 0-1028 and 16-1006: Q26); **02treasure_box** (0 tributes, lost 0-1002 and 163-1005: Q27); **7 close races** where the opponent hit ~1000 first (Q28); 0-0 gold tiebreaks on 01boss_battle and 02guardians (h_goldtie's target).
  - CLI login done 1 Nov ~01:00 UTC; it **expires ~7 Nov**. Ladder statistics are in `matches/ladder/summary/<id>__<our side>.json` (feed `tools/analyze_match.py` directly).
- **Upcoming locks:** International qualifiers 4 Nov, UK qualifiers 11 Nov, finals 18 Nov. Still not listed in `/api/v1/tournaments` at 01:02 UTC on 1 Nov (Sprint 3 is now `ready`). Recheck each tick.

## Cluster operating notes (31 Oct)
- Tools run with **`python3.12`**; the system `python3` is 3.6.
- `cli/cambc` → holylabs software tier; `matches/` and `replays/` → netscratch (`/n/netscratch/hekstra_lab/Lab/ian_poon/battlecode/`, 90-day purge).
- **All evals run on the free Slurm `test` partition** via `tools/onslurm.sh -c 24 -m 16G -t 00:20:00 -J <name> -- python3.12 tools/eval.py ... --jobs 16`. It runs from a node-local snapshot, because builds rewrite `bot.wasm` in place and parallel jobs would race. A 140-game `--maps all` run takes ~4 min. The user allows only free lanes (`test`, `gpu_test`).
- Determinism holds across machines: the cluster reproduced the dev-PC gauntlet numbers exactly.

## In progress
- **Workflow `battlecode-ladder-learning-1`** (launched ~21:00 EDT): Q26 (02gift_wrapping zero clears), Q27 (02treasure_box zero tributes), Q28 (race tempo). Each is a diagnosis followed by one fix experiment. NB: its candidates fork **tb_merge_b**, so any keeper must be ported onto q24_combo and gated against it.

## Done this session
- **Champion gauntlet baseline:** `tb_merge_b` **158/200** on sprint maps. In `results/gauntlet.jsonl`.
- **Batch 2 (workflow `battlecode-batch2`, finished 21:20 EDT).** Reports are in `results/experiments/2026-11-01-*.md`.
  - **q24_combo passed the full gate and is the new champion.**
  - **h_respawnfix (Q21): 92/140 vs tb_merge_b.** Next: merge it into q24_combo and gate.
  - Batch-1 analyses: h_earlyfight_all 84/140, h_antistun 79 (rejected), h_3pick 75, h_goldtie 74, h_fightfuel 72 (rejected alone).
- **Methodology flag:** the fuel-sensitive bots (h_goldtie, h_earlyfight_all, h_fightfuel) did not reproduce their dev-PC sprint records game for game, while h_3pick and h_antistun did. A null-change placebo run should calibrate the gate's noise.
- **Agent relay** (`tools/agent_relay.sbatch`, `tools/agent_attach.sh`): it keeps this session alive past the 12 h job cap on the free test partition. Dry runs and a live `claude --resume` test passed. **Not armed**; waiting for the user's go-ahead.

## Resume here (in order)
1. **c2 = q24_combo + h_respawnfix:** merge, review and gate vs q24_combo; also the placebo calibration and Q30 (q24's large-map regression).
2. Collect `battlecode-ladder-learning-1`, port any keepers onto q24_combo and gate them.
3. Ladder: confirm v3 is Active / Verified, then track v3's record separately (`tools/ladder_pull.py`).
4. Queue: Q29-Q32 and the batch-2 hypotheses in STRATEGIES.md; Q20 and Q22 (structural no-tribute maps); C++ track.

## Leftover bot dirs from interrupted work
- `g_earlyfight`, `g_fightfuel`: gate snapshots, never evaluated. Superseded by the batch-2 all-maps runs.
- `g_ef_ff`: merge attempt with a stale NOTES.md and unverified state. Superseded by `q24_combo`.
- `cpp_bench`, `cpp_scratch*`: C++ fuel micro-benchmarks and scratch work.
- `h_earlyfight_diag`: diagnostic build only; never evaluate it.
