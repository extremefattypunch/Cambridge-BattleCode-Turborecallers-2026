# Ready-to-submit bot (always the best validated bot)

**Rule (user, 31 Oct):** always keep the strongest validated bot ready to submit for any tournament at any time. It is uploaded as our live version as soon as it is validated.

| Field | Value |
|---|---|
| Bot | `q24_combo` (Python) = `tb_merge_b` + lock-memory fix + gold-tiebreak play + group-balance fight rule + fuel caching (`bots/q24_combo/NOTES.md`) |
| Bundle | `submissions/READY.zip` (gitignored; rebuild with `./cli/cambc bundle q24_combo --output submissions/READY.zip`) |
| Live on site | uploaded as website **v3** at 01:24 UTC on 1 Nov (queued for verification at upload) |
| Gate (LOOP.md §4), all passed | (a) **87W-53L vs tb_merge_b** on all 70 maps × both sides, Wilson 95% LB 0.539, botFaults 0; A 43/70, B 44/70. (b) Gauntlet **174/200** vs the champion's 158: sf_bank 39-1, tb_merge_a 24-16, tb_aggro 39-1, imit_test 36-4, lad_vcst 36-4; worst per-opponent change −1. (c) release game clean; all 140 gate games re-run in release mode matched exactly; fuelExhausted 8.0 vs 67.9 per game. (d) Analysis: all four mechanisms changed (`results/experiments/2026-11-01-q24_combo.md`). A skeptic agent could not refute the claim |
| Known risks | Without the 5 tiebreak maps it is 77/130 (LB 0.506). Maps of ≥ 8,000 tiles went 2/12 vs the mirror's 6/12 (Q30). `no_tribute` is decided once at init, so an unseen map whose "guard" groups are clearable would never be tributed |
| Promoted | 1 Nov 2026, 01:24 UTC |

## Previous champion
`tb_merge_b` (website v2): 62W-33L on the ladder, rating ~1,500. Use `cambc submissions activate v2` to roll back.

## Candidates under watch
Any result ≥ 55% vs the champion goes to the full gate. The gate requires **certainty**: ≥ 82/140 on `--maps all`, a paired gauntlet and a clean release run.

| Candidate | Result | Status |
|---|---|---|
| h_respawnfix (Q21) | **92W-48L vs tb_merge_b** on all maps (not yet vs q24_combo) | next: merge into q24_combo and gate vs q24_combo |
| h_earlyfight_all, h_3pick, h_goldtie | 84/140, 75/140, 74/140 vs tb_merge_b | inside q24_combo |
| h_fightfuel | 72/140 alone (fuel −93% but no win gain) | inside q24_combo for the fuel headroom |
| h_antistun | 79/140 | rejected (rare events, gain not attributable) |
| cpp_port (C++) | 20W-20L vs tb_merge_b (sprint) | parity; 0 fuel exhaustions |
