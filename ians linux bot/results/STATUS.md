# Loop status (updated every tick)

- **Last update:** 2026-10-31 ~20:50 EDT. The **cluster agent** (FASRC Cannon) has taken over from the dev PC. A session cron tick fires at :17 and :47 each hour while the session is alive.
- **Champion / live bot:** `tb_merge_b` (Python), website **v2**, Active / Verified. It was our **Sprint 3 entry** (snapshot 31 Oct 23:59 UTC; Sprint 3 was seeding as of 00:30 UTC on 1 Nov).
- **Ladder:** v2 is **43W-17L** (72%) over 12 sets. Rating ~**1,491**, a plateau around 1,490-1,497 as of 31 Oct 23:40 UTC. No new pull yet: the CLI on the cluster is **not logged in** (`cambc login` needs a human).
  - By team size: 3-pick 6/12, 4-pick 14/16, 5-pick 23/32.
  - Set losses at ~1,500 came against the **mirror meta comp** (Q19).
  - Log: `results/ladder-games.jsonl` (125 games); summarise with `python3.12 -I tools/ladder_log.py`.
- **Upcoming locks:** International qualifiers 4 Nov, UK qualifiers 11 Nov, finals 18 Nov. Not yet listed in `/api/v1/tournaments` (only Sprints 1-3 were, at 00:30 UTC on 1 Nov). Recheck each tick.

## Cluster operating notes (31 Oct)
- Tools run with **`python3.12`**; the system `python3` is 3.6.
- `cli/cambc` → holylabs software tier; `matches/` and `replays/` → netscratch (`/n/netscratch/hekstra_lab/Lab/ian_poon/battlecode/`, 90-day purge).
- **All evals run on the free Slurm `test` partition** via `tools/onslurm.sh -c 24 -m 16G -t 00:20:00 -J <name> -- python3.12 tools/eval.py ... --jobs 16`. It runs from a node-local snapshot, because builds rewrite `bot.wasm` in place and parallel jobs would race. A 140-game `--maps all` run takes ~4 min. The user allows only free lanes (`test`, `gpu_test`).
- Determinism holds across machines: the cluster reproduced the dev-PC gauntlet numbers exactly.

## In progress
- **Workflow `battlecode-batch2`** (launched ~20:45 EDT):
  - **Track A:** build **Q24** `q24_combo` (lock-memory fix + gold play + early-fight v3 + fuel caching), adversarial merge review, then the full LOOP.md §4 gate and a skeptic pass.
  - **Track B:** batch-1 analysis sessions (h_3pick, h_goldtie, h_earlyfight_all, h_fightfuel, h_antistun), each on all 70 maps with reports in `results/experiments/2026-11-01-*.md`.
  - **Track C:** **Q21** respawn-rule freeze fix (`h_respawnfix`).

## Done this session
- **Champion gauntlet baseline:** `tb_merge_b` **158/200** on sprint maps. sf_bank 37-3, tb_merge_a 20-20, tb_aggro 40-0, imit_test 34-6, lad_vcst 27-13. In `results/gauntlet.jsonl`.

## Resume here (in order)
1. Collect `battlecode-batch2`: promote q24_combo only on a full gate pass and a skeptic pass. Record verdicts and new hypotheses in STRATEGIES.md.
2. **Ladder monitoring** needs `cambc login` once (ask the user). Then pull games with `cambc matches list` (see `docs/CLI_ONLY.md`).
3. **Q14 / Q19, real replays** (needs login): study the losses to "test" and the mirror-meta teams.
4. Next queue items: Q20 (TP into wolf-ringed altar), Q22 (open-gate rush), Q25 (cheaper sensing), Q1 (burst comp counter).
5. **C++ track:** `bots/cpp_port` is at parity; the verify/fix phases never ran.

## Leftover bot dirs from interrupted work
- `g_earlyfight`, `g_fightfuel`: gate snapshots, never evaluated. Superseded by the batch-2 all-maps runs.
- `g_ef_ff`: merge attempt with a stale NOTES.md and unverified state. Superseded by `q24_combo`.
- `cpp_bench`, `cpp_scratch*`: C++ fuel micro-benchmarks and scratch work.
- `h_earlyfight_diag`: diagnostic build only; never evaluate it.
