# Ready-to-submit bot (always the best validated bot)

**Rule (user, 31 Oct):** always keep the strongest validated bot ready to submit for any tournament at any time. It is uploaded as our live version as soon as it is validated.

| Field | Value |
|---|---|
| Bot | `c2_respawn` (Python) = `q24_combo` + the Q21 respawn-rule freeze fix (`bots/c2_respawn/NOTES.md`) |
| Bundle | `submissions/READY.zip` (gitignored; rebuild with `./cli/cambc bundle c2_respawn --output submissions/READY.zip`) |
| Live on site | uploaded as website **v4** at 04:36 UTC on 1 Nov (queued for verification at upload) |
| Gate (LOOP.md §4), all passed | (a) **89W-51L vs q24_combo** on all 70 maps × both sides, Wilson LB 0.553, botFaults 0; A 45/70, B 44/70. (b) Gauntlet **177/200** vs q24's 174 (worst per-opponent change −1). (c) all 140 gate games re-run in release mode identical, 0 `bot error`; fuelExhausted 6.88 vs 6.86 per game. (d) frozen champion-rounds −25% (`results/experiments/2026-11-01-c2_respawn.md`). The skeptic did not refute it. Extra checks: placebo-perturbed c2 scored 83/140 vs q24; **98/140 vs tb_merge_b** (q24: 87); 92/100 vs imit_test and lad_vcst on the 50 non-sprint maps (q24: 83 and 85) |
| Known risks | **3-pick maps vs mirror-draft (tb_merge-family) opponents: 11/32 vs q24's 23/32 (p=0.004)**; fix queued (H1, step-off with an enemy in sight). The gain is mostly on large and 5-pick maps. The local gate does not reliably predict the ladder (q24: 87/140 locally, but ≈ v2 on the ladder) |
| Promoted | 1 Nov 2026, 04:36 UTC |

## Previous champions
- `q24_combo` (website v3, live 01:42-~04:40 UTC on 1 Nov): 45W-45L on the ladder at ~1,530. The v3 ladder study found it not significantly different from v2 (−54 Elo, p 0.36; `results/experiments/2026-11-01-v3-ladder-study.md`).
- `tb_merge_b` (website v2): 74W-36L on the ladder (corrected labels).
- Roll back with `cambc submissions activate v3` (or v2); that changes the team account, so ask the user.

## Candidates under watch
Any result ≥ 55% vs the champion goes to the full gate. The gate requires **certainty**: ≥ 82/140 on `--maps all`, a paired gauntlet and a clean release run.

| Candidate | Result | Status |
|---|---|---|
| h_teamclear (Q26) | 91/140 vs tb_merge_b | c3_teamclear (q24 + team clear) is being gated; next is c4 = c2 + team clear |
| h_bigmap (Q30) | 80/140 vs q24_combo | fails the gate by 2; kept as a merge component |
| h_earlyfight_all, h_3pick, h_goldtie | 84/140, 75/140, 74/140 vs tb_merge_b | inside q24_combo |
| h_fightfuel | 72/140 alone (fuel −93% but no win gain) | inside q24_combo for the fuel headroom |
| h_antistun | 79/140 | rejected (rare events, gain not attributable) |
| cpp_port (C++) | 20W-20L vs tb_merge_b (sprint) | parity; 0 fuel exhaustions |
