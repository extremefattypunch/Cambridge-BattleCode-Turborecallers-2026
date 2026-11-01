# Ready-to-submit bot (always the best validated bot)

**Rule (user, 31 Oct):** always keep the strongest validated bot ready to submit for any tournament at any time. It is uploaded as our live version as soon as it is validated.

| Field | Value |
|---|---|
| Bot | `tb_merge_b` (Python) |
| Bundle | `submissions/READY.zip` (gitignored; rebuild with `./cli/cambc bundle tb_merge_b --output submissions/READY.zip`) |
| Live on site | yes, website **v2**, Active / Verified since 31 Oct 22:13 UTC |
| Local validation | 37W-3L vs sf_bank (sprint); **125W-15L vs sf_bank on all 70 maps**; 24W-0L vs tb_aggro; 0 crashes; release mode clean |
| Real ladder | **43W-17L** (72%); rating 1,407 → about 1,491 (plateau). Weak on 3-pick maps (6/12) and in mirror-meta matchups at ~1,500 |
| Promoted | 31 Oct 2026 ~17:40 EDT |

## Candidates under watch
Experiments against the champion; any result ≥ 55% on sprint goes to the full gate. The gate requires **certainty**: ≥ 82/140 on `--maps all`, a paired gauntlet and a clean release run.

| Candidate | vs champion (sprint, 40 games) | Status |
|---|---|---|
| h_earlyfight_all (v3) | 23W-17L (58%) | in the Q24 combo; not gated |
| h_earlyfight (v2) | 22W-18L (55%) | superseded by v3 |
| h_fightfuel | 22W-18L (55%) | in the Q24 combo; not gated |
| h_3pick (lock-memory fix) | 22W-18L (55%); 13-11 on 3-pick maps | **bug fix**; in the Q24 combo |
| h_goldtie (v2) | 21W-19L (52.5%); 9-1 on tiebreak maps | in the Q24 combo |
| h_antistun | 20W-20L (50%) | likely reject |
| cpp_port (C++) | 20W-20L (50%) | parity; 0 fuel exhaustions |

**Next:** build the **Q24 combined candidate** and gate it (see `results/STATUS.md`, "Resume here").
