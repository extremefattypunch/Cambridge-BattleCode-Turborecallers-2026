# h_rfx_count: measurement-only copy of tb_merge_b (Q21 trigger census)

tb_merge_b plus counters; behaviour is unchanged apart from fuel. Every 100 rounds each champion prints
`Q21C <round> <slot> a b c d e` (cumulative): a = respawn-rule push-backs on a tile whose group is NOT
Respawning (the bug), b = push-backs on a Respawning group's tile (legitimate), c = "unseen alive" guesses
while observe() read the engine state this turn (the bug), d = guesses without a fresh read, e = a + b.
Runner: `bots/h_rfx_count/census_run.py` (run from the repo root, e.g. `tools/onslurm.sh -c 24 -m 16G -t 00:20:00 -J q21-cnt -- python3.12 bots/h_rfx_count/census_run.py 16`; it writes `matches/q21-count/`) (keeps stdout, sums the last Q21C line per slot). Used by
`results/simulated-matches/2026-11-01_0126_h_respawnfix/notes.md`. Not a candidate; never submit.
