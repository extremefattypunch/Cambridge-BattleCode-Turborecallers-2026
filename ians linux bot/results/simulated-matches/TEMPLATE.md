# Simulated-match note template (the testing pipeline)

One folder per simulated match: one candidate bot tested against the champion, and against reference opponents where relevant.
- **Create it with** `python3.12 tools/new_sim_note.py <candidate> --vs <champion> --prev <parent folder>`. That makes `<YYYY-MM-DD>_<HHMM UTC when the test is launched>_<candidate>/notes.md` from the part below the line.
- **Write and commit sections 1-2 before any game runs.** Write sections 3-5 after the test, and never edit section 2 afterwards. This keeps the hypothesis and prediction honest.

**The previous simulated match** (also called the *parent*) is the finished simulated match this hypothesis builds on. It is usually the current champion's own gate match, or the experiment this one refines. Several experiments can share one parent. If another note in the same batch already analysed that parent in full, keep the same format but limit section 1 to what matters for this hypothesis (about 30 lines), and link that note for the rest.

---

# <candidate> vs <champion>: <W>-<L> of <N>, <date> <HH:MM> UTC, <verdict>

**Previous simulated match:** [`<folder>`](../<folder>/notes.md)
**Bots:** `bots/<candidate>` (forked from `bots/<champion>`)
**Games:** `matches/<tag>/`

## 1. The previous simulated match, analysed
Use the same format as a real-match note, applied to the parent match.
### 1.1 The games played
A summary table of its results (by map family, side and team size), and the key games described briefly.
### 1.2 Its strategy compared with its opponent's
### 1.3 Which strategy was superior, and what we learned
This is the learning that leads into the new hypothesis.

## 2. The new hypothesis
- **Change:** what the candidate does differently, behind which flag.
- **Why it should win:** the mechanism.
- **Evidence that it has promise:**
  - Real matches: [`<folder>`](../../real-matches/<folder>/notes.md), and what they showed.
  - Earlier simulated matches: [`<folder>`](../<folder>/notes.md), and what they showed.
- **Prediction (written before the test):** which metric should move, in which direction, by about how much, and the expected result vs the champion.

## 3. The test
- **Setup:** opponents, maps, sides, number of games, and the exact commands (all games run via `tools/onslurm.sh`).
- **Results:** the verbatim `SUMMARY` / `GAUNTLET` lines, including the check against `tb_merge_b` (gate step e).

## 4. This match, analysed
Use the same format as a real-match note.
### 4.1 The games played
### 4.2 The candidate's strategy compared with the champion's
### 4.3 Which strategy was superior, and what we learn
Did the predicted mechanism actually change? Why were the remaining games lost? Was the prediction right?

## 5. Verdict and next steps
- **Verdict:** promoted / kept as a component / inconclusive / rejected, with the gate numbers (LOOP.md step 4, checks a-f).
- **New hypotheses:** these go into the single ranked queue in `results/STRATEGIES.md`, and into the next simulated match.
