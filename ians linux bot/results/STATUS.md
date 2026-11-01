# Loop status (updated every tick)

- **Last update:** 2026-11-01 01:50 EDT (tick). The **cluster agent** (FASRC Cannon) has taken over from the dev PC. A session cron tick fires at :17 and :47 each hour while the session is alive.
- **Champion / live bot:** `c2_respawn` (q24_combo + respawn fix), website **v4**, **live since ~04:40 UTC on 1 Nov** after a full gate pass plus a skeptic pass (`results/READY.md`).
- **Ladder (pulled 1 Nov 04:35 UTC):** corrected labels give **v3 45W-45L** (~1,530) and **v2 74W-36L**. The v3 ladder study (`results/real-matches/studies/2026-11-01_0437_v3-ladder-study/notes.md`) found:
  - 25 games had been mislabelled; `tools/ladder_pull.py` now re-derives versions by finish time.
  - Rating-controlled, v3 vs v2 is −54 Elo [−166, +65], p 0.36, so not significant. v3 held v2's rating.
  - Fuel caching, gold play and lock memory are confirmed working on real games.
  - Decision: keep v3, and require successors to also beat tb_merge_b locally (c2: 98/140).
  - **v4 (c2_respawn) has been live since 04:42:47 UTC: 17W-18L so far** (rating 1,530 → 1,507 → 1,526; 13-8 since its 4-10 start).
    - Us V Them (Power Focus casters): 1-4. They also beat v3 3-7, so this is the V3L-1 focus-burst matchup.
    - Lie groups lie (near-mirror draft): 0-4, consistent with c2's mirror-draft weakness; c2_3pick is in progress.
    - Full Damage: 3-2.
    - 14 games is not significant (p ≈ 0.09); v3 also opened 5/15 and ended 45-45. Keep monitoring.
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
  1. Re-create the tick with CronCreate (`17,47 * * * *`). Its prompt follows LOOP.md; first priority is real-match scouting (`tools/unscouted.py` → `tools/workflows/ladder_scout.js`), then self-play experiments. Login-node rule: every game goes through `tools/onslurm.sh`.
  2. Check `squeue -u $USER -p test` and `results/experiments/` for the work the interrupted workflows finished.
  3. Relaunch what is missing.
- **Login-node rules:** run no games locally, not even a single debug game; send them through `tools/onslurm.sh -c 2 -m 2G -t 00:05:00 -J dbg -- ./cli/cambc run ...`. Long analysis scripts also go through onslurm.

## Note layout (user, 1 Nov ~06:00 UTC)
- **One folder per match, each with its own `notes.md`.**
  - Real matches: `results/real-matches/<date>_<HHMM>_<opponent>_<group8>/`.
  - Simulated matches: `results/simulated-matches/<date>_<HHMM>_<candidate>/`.
- The formats are in each folder's `TEMPLATE.md`; the workflow, with flowcharts, is in the repo `README.md`.
- `tools/organize_notes.py` moves notes left in old places (`results/experiments/`, `results/ladder/scouting/`) and rebuilds both `INDEX.md` files. Run it after any workflow finishes.
- Untracked compatibility symlinks in `results/experiments/` (and `TEMPLATE.md` there) exist only for workflows started before the move. Delete them once batch 6, batch 7 and both scouting workflows have finished.

## In progress
- **Workflow `battlecode-ladder-scouting`** (launched ~01:40 EDT): deep scouting of all 24 v3/v4 ladder sets. It builds `tools/scout.py`, writes per-set notes in `results/ladder/scouting/` and a ranked `results/ladder/WEAKNESSES.md`. From now on every new set is scouted each tick into `results/ladder/INSIGHTS.md` (user, 1 Nov: real-match insights first, self-play continues).
- **Workflow `ladder-scout`** (01:48 EDT): the Electric Fog Walkers set (05:42 UTC, 4-1). After the big scouting run finishes, refresh INSIGHTS.md from all notes.
- **Batch 4 (finished 00:50 EDT):**
  - **c3_teamclear failed the gate** (80/140 vs q24, LB 0.489). It fixes 02gift-wrapping, but muster idling cancels the gain elsewhere.
  - **h_spawnheal** was inconclusive (74/140).
  - **Workflow `battlecode-batch6`** (launched 00:55 EDT): **c4_fallback** = c2 + team clear as a *fallback only* (when no champion has a solo target), plus a first-turn fuel fix. It gets a build, a review, the gate vs c2, the tb_merge_b hedge and a skeptic.
- **Batch 5 (finished ~01:10 EDT):**
  - **c2_3pick kept** (3-pick vs the mirror-draft family 33/48 vs 20/48; 106/140 vs tb_merge_b).
  - **h_shortcut kept** (a stuck-champion bug fix).
  - **h_bosscommit rejected.**
  - Both kept fixes are scoped, so they go into the next combo: **c5 = (c4 if it passes, else c2) + c2_3pick patch + h_shortcut fix**.

- **Workflow `battlecode-batch7`** (launched ~01:15 EDT), on c2_respawn: **h_antifocus** (V3L-1, the counter to the Us V Them focus casters; it first builds an imitation that reproduces the ladder loss) and **h_snowball** (Q29, a runaway enemy carry).

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
