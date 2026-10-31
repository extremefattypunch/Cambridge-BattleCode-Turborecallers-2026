# Experiment: <candidate bot> (<date>)

## Hypothesis
- **What:** what we change, and why it should raise performance.
- **Source:** ladder game(s) / postmortem / own analysis (link the evidence).

## Setup
- Candidate: `bots/<cand>`, forked from the champion `<champion>`.
- Diff summary: the exact behaviours changed.
- Opponents and maps: champion (sprint/quick), imitation opponents, targeted maps.

## Results
Paste the verbatim `SUMMARY ...` lines, plus any `match_metrics.py` and `analyze_match.py --summary` key rows.

## Analysis session
- **Did the targeted mechanism actually change?** Give metrics before and after.
- **Losses:** why were they lost? Gem race, the tempo of the first clear and tribute, deaths (killer, location, round), fights, fuel.
- **Surprising wins:** what happened in them?
- **Evidence:** cite the games by map/side.

## Verdict
kept / rejected / inconclusive, with the reason.

## New hypotheses generated
Each gets a one-line rationale and is added to `results/STRATEGIES.md`.
- ...
