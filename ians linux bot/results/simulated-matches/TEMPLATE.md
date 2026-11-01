# Simulated-match note template (the testing pipeline)

One folder per simulated match: one candidate bot tested against the champion, and against reference opponents where relevant. The folder is named `<YYYY-MM-DD>_<HHMM UTC>_<candidate>/` and holds a single `notes.md` laid out as follows. Copy everything below the line.

**"The previous simulated match"** is the most recent finished simulated match that this hypothesis builds on. It is usually the current champion's own gate match, or the experiment this one refines. Name it in the header.

---

# <candidate> vs <champion>: <W>-<L> of <N>, <date> <HH:MM> UTC, <verdict>

**Previous simulated match:** [`<folder>`](../<folder>/notes.md)
**Bots:** `bots/<candidate>` (forked from `bots/<champion>`)
**Games:** `matches/<tag>/`

## 1. The previous simulated match, analysed
Use the same format as a real-match note, applied to the previous simulated match.
### 1.1 The games played
A summary table of its results (by map family and side), and the key games described briefly.
### 1.2 Its strategy compared with its opponent's
### 1.3 Which strategy was superior, and what we learned
This is the learning that leads into the new hypothesis.

## 2. The new hypothesis
- **Change:** what the candidate does differently, behind which flag.
- **Why it should win:** the mechanism.
- **Evidence that it has promise:**
  - Real matches: [`<folder>`](../../real-matches/<folder>/notes.md), and what they showed.
  - Earlier simulated matches: [`<folder>`](../<folder>/notes.md), and what they showed.
- **Prediction:** which metric should move, in which direction, by about how much.

## 3. The test
- **Setup:** opponents, maps, sides, number of games, and the exact commands (all games run via `tools/onslurm.sh`).
- **Results:** the verbatim `SUMMARY` / `GAUNTLET` lines, including the check against `tb_merge_b`.

## 4. This match, analysed
Use the same format as a real-match note.
### 4.1 The games played
### 4.2 The candidate's strategy compared with the champion's
### 4.3 Which strategy was superior, and what we learn
Did the predicted mechanism actually change? Why were the remaining games lost?

## 5. Verdict and next steps
- **Verdict:** promoted / kept as a component / inconclusive / rejected, with the gate numbers (LOOP.md §4).
- **New hypotheses:** these feed `results/STRATEGIES.md` and the next simulated match.
