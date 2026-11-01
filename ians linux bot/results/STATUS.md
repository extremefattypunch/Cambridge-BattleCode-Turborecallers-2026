# Loop status (updated every tick)

- **Last update:** 2026-11-01 00:15 EDT (tick, after a usage-limit pause from ~22:00 to 00:00 EDT; workflow agents hit HTTP 429 and resumed by themselves). The **cluster agent** (FASRC Cannon) has taken over from the dev PC. A session cron tick fires at :17 and :47 each hour while the session is alive.
- **Champion / live bot:** `q24_combo` (Python), uploaded as website **v3** at 01:24 UTC on 1 Nov after a full gate pass (87/140 vs tb_merge_b, gauntlet 174 vs 158; `results/READY.md`). Confirm v3 shows Active / Verified on the next ladder pull. The previous bot `tb_merge_b` (v2) was our Sprint 3 entry.
- **Ladder (pulled 1 Nov 04:10 UTC):** **v3 (q24_combo) went live at 01:42 UTC** (when v2 was deactivated; v3's own `statusAt` was refreshed later, so it misled).
  - **v3 is 24W-26L (48%), rating 1,526, flat**, against opponents rated ~1,520-1,575.
  - v2's comparable recent window was 21-9 (70%) against ~1,490-1,530. All of v2 is 87W-48L.
  - v3 still loses 02treasure_box (3 more times); its 0-0 gold play won 02the_pack but lost 01boss_battle to AI Coliseum.
  - **Workflow `battlecode-v3-ladder-study`** (launched 00:15 EDT) asks: is v3 really worse, and why?
  - By team size: 3-pick 13/19, 4-pick 23/28, 5-pick 38/63.
  - New loss patterns: **02gift_wrapping** (0 clears all game, lost 0-1028 and 16-1006: Q26); **02treasure_box** (0 tributes, lost 0-1002 and 163-1005: Q27); **7 close races** where the opponent hit ~1000 first (Q28); 0-0 gold tiebreaks on 01boss_battle and 02guardians (h_goldtie's target).
  - CLI login done 1 Nov ~01:00 UTC; it **expires ~7 Nov**. Ladder statistics are in `matches/ladder/summary/<id>__<our side>.json` (feed `tools/analyze_match.py` directly).
- **Upcoming locks:** International qualifiers 4 Nov, UK qualifiers 11 Nov, finals 18 Nov. Still not listed in `/api/v1/tournaments` at 01:02 UTC on 1 Nov (Sprint 3 is now `ready`). Recheck each tick.

## Cluster operating notes (31 Oct)
- Tools run with **`python3.12`**; the system `python3` is 3.6.
- `cli/cambc` → holylabs software tier; `matches/` and `replays/` → netscratch (`/n/netscratch/hekstra_lab/Lab/ian_poon/battlecode/`, 90-day purge).
- **All evals run on the free Slurm `test` partition** via `tools/onslurm.sh -c 24 -m 16G -t 00:20:00 -J <name> -- python3.12 tools/eval.py ... --jobs 16`. It runs from a node-local snapshot, because builds rewrite `bot.wasm` in place and parallel jobs would race. A 140-game `--maps all` run takes ~4 min. The user allows only free lanes (`test`, `gpu_test`).
- Determinism holds across machines: the cluster reproduced the dev-PC gauntlet numbers exactly.

## Session restart checklist (the agent runs on a login node from 1 Nov)
The session-only cron tick and any running workflows die whenever the Claude process ends: the OOD job ending, a login-node reboot, or FASRC killing a long process. Files on disk survive.
- **Restart** (user, in tmux on a login node; note `hostname` so you can `ssh` back and `tmux attach -t cambc`):
  `tmux new -s cambc`, then `cd /n/home05/ianpoon/Cambridge-BattleCode-Turborecallers-2026 && claude --resume 5245ba49-8b5b-4d9a-9345-708126bcbea8 --permission-mode auto`
  Only one process may hold the session, so start it after the old one has ended.
- **The resumed agent must:**
  1. Re-create the tick with CronCreate (`17,47 * * * *`, using the LOOP TICK prompt from the conversation; login-node rule: every game goes through `tools/onslurm.sh`).
  2. Check `squeue -u $USER -p test` and `results/experiments/` for the work the interrupted workflows finished.
  3. Relaunch what is missing.
- **Login-node rules:** run no games locally, not even a single debug game; send them through `tools/onslurm.sh -c 2 -m 2G -t 00:05:00 -J dbg -- ./cli/cambc run ...`. Long analysis scripts also go through onslurm.

## In progress
- **Workflow `battlecode-batch3`** (launched ~21:28 EDT):
  - **c2_respawn** = q24_combo + respawn fix: merge, review, gate vs q24_combo;
  - **placebo** noise-floor calibration;
  - **Q30**: q24's large-map regression (h_bigmap).
- **Workflow `battlecode-batch4`** (launched ~22:35 EDT):
  - **c3_teamclear** = q24_combo + Q26 team bootstrap: merge, review, gate vs q24_combo;
  - **Q27-refined** spawn-heal-aware fighting (h_spawnheal).
- After both: if c2 and c3 each pass, build **c4 = q24 + respawn fix + team clear** and gate it against the new champion.

## Done this session
- **Champion gauntlet baseline:** `tb_merge_b` **158/200** on sprint maps. In `results/gauntlet.jsonl`.
- **Batch 2 (workflow `battlecode-batch2`, finished 21:20 EDT).** Reports are in `results/experiments/2026-11-01-*.md`.
  - **q24_combo passed the full gate and is the new champion.**
  - **h_respawnfix (Q21): 92/140 vs tb_merge_b.** Next: merge it into q24_combo and gate.
  - Batch-1 analyses: h_earlyfight_all 84/140, h_antistun 79 (rejected), h_3pick 75, h_goldtie 74, h_fightfuel 72 (rejected alone).
- **Methodology flag:** the fuel-sensitive bots (h_goldtie, h_earlyfight_all, h_fightfuel) did not reproduce their dev-PC sprint records game for game, while h_3pick and h_antistun did. A null-change placebo run should calibrate the gate's noise.
- **Ladder-learning 1 (finished ~22:25 EDT):**
  - **Q26 h_teamclear kept: 91/140 vs tb_merge_b**, gauntlet 164/200. Root cause: no champion commits first to a group the solo check rejects; 73 such groups on 22 local maps.
  - Q27 h_treasure inconclusive (72/140): the mechanism was confirmed but regressions cancelled it.
  - Q28 h_tempo rejected (75/140).
  - Noise warning: identical logic under another bot name replayed only 26 of 40 games identically.
- **Agent relay** (`tools/agent_relay.sbatch`): built and tested, but **not used**. The user chose to run the agent on a login node instead (1 Nov).

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
