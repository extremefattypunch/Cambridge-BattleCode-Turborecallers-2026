# Experiment batch: learning from real ladder matches (2026-10-31)

## Hypotheses
1. Mid-ladder drafts (Varg / Cassi&Issac / Stellar / Tavi / Ren) are stronger than our census meta draft.
2. v2's only two ladder losses (to team "test" on adgato_gemcombat4 and 02arena) can be reproduced locally and fixed with fight-model tweaks:
   - (a) count an enemy's shield as HP;
   - (b) weight caster burst higher.

## Setup
- **Ladder data:** 80 real games, in `results/ladder-games-2026-10-31.json`. The statistics script is `postmortems/ladder_stats.py`, and the report is `results/real-matches/studies/2026-10-31_2340_ladder-analysis/notes.md`.
- **Imitation opponents:** copies of tb_merge_b with only the draft changed: `lad_vcst`, `lad_svrc`, `lad_hyb`, `lad_varg4`, `imit_test`.
- **Fix candidates:** `tb_v3_cand` (shield as HP) and `tb_v3_burst` (caster burst weighting).

## Results
```
SUMMARY tb_merge_b vs lad_vcst:  27W-13L (68%)  [sprint]     tb_merge_b vs lad_vcst 11W-1L on the ladder-loss maps
SUMMARY tb_merge_b vs lad_svrc:  32W-8L  (80%)  [sprint]
SUMMARY tb_merge_b vs lad_hyb:   24W-16L (60%)  [sprint]
SUMMARY tb_merge_b vs lad_varg4: 39W-41L (49%)  [80 games: sprint + ladder-loss maps + 16 extra maps]
SUMMARY tb_merge_b vs imit_test: 34W-6L  (85%)  [sprint]
SUMMARY tb_v3_cand vs tb_merge_b: 20W-20L (50%) [sprint];  tb_v3_cand vs imit_test 32W-8L (80%)
SUMMARY tb_v3_burst vs imit_test: 33W-7L (82%)  [sprint]
Ladder: v1 18W-47L (opponents avg 1447); v2 13W-2L (opponents avg 1419)
```

## Analysis session
- **Draft is not the cause.** With our logic, every ladder-common comp loses to our draft. That includes 2-0 on both maps we lost to "test", by wide margins (adgato-gemcombat4 1066-138, 02arena 1001-248). "Test" won through play quality.
- **Determinism.** Repeating a game (same map, same bots) gives byte-identical stats. Evidence has to come from more maps, not reruns.
- **Kill-driven gem swings.** In our local adgato-gemcombat4 win, 551 of our 1066 gems came from champion kills. Test hit 1018 by round 577 while we banked 361. They almost certainly won the fights and took our carried gems. This is unconfirmed until we have the real replay.
- **Who kills us in the imitation games:** Varg is our top killer and gem-taker (451 gems over 40 games), then Ryth, Ren and Issac. Marcella is our most-killed champion. Stellar drew first blood on Marcella in both repro maps (rounds 61 and 68).
- **Champion farming value:** Varg is the best imitation farmer every run (about 120-130 gems and 20k monster damage per game, up to 70k on 01big-world). HoR is our weakest farmer (about 115 gems, 7-9k monster damage), but swapping it for Varg was neutral, so HoR's fight value seems to compensate.
- **Linked-fate weakness:** the imitations' Cassi&Issac died about 7 times per game with our logic, which has no linked-fate handling.
- **Ladder economics:** rating moves about ±16 for a 5-0 and ±3 for a 3-2, so avoiding blowout set losses matters most. v1's losses were mostly blowouts (34 of 47 with us under 40% of their gems).
- **Self-play predictiveness:** it predicted the *relative* v1→v2 gain (about +600 Elo locally vs +465 on the ladder) but not absolute strength, and not which maps we lose on the ladder.

## Verdicts
- T11 rejected; T12 neutral; T13 and T14 rejected. tb_merge_b stays the Sprint 3 entry.

## New hypotheses
Q14 (study "test"'s real replays), Q15 (anti-stun channel rule), Q16 (Varg with a Bruiser plan), Q17 (C&I linked fate), Q18 (3-pick stun anchor). All are in STRATEGIES.md.
