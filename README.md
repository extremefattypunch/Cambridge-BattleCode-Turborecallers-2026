# Cambridge-BattleCode-Turborecallers-2026

Created at: 2026-10-31T18:01:01.099Z
Active markdown file: Cambridge BattleCode Turborecallers 2026.md
Obsidian vault: Obsidian Md Notes

---

Team **Turbo Recallers** in [Cambridge Battlecode 2026a](https://2026a.battlecode.co.uk). An AI agent improves our bot around the clock with two sources of learning:

- **Real matches.** Our live bot plays ranked ladder games against other teams. These are the most valuable evidence.
- **Simulated matches.** Our own bots play each other on free cluster nodes. This is the **testing pipeline**: every idea is tested here before it can go live.

Everything lives in [`ians linux bot/`](ians%20linux%20bot). The rest of this page explains the workflow and where to read the results.

## 1. The improvement loop

```mermaid
flowchart TB
    subgraph REAL["REAL MATCHES (ladder, against other teams)"]
        LIVE["Our live bot plays<br/>ranked ladder matches"] --> PULL["tools/ladder_pull.py<br/>downloads every game's statistics"]
        PULL --> RNOTE["One folder + notes.md per real match<br/>(results/real-matches/, format in §4.1)"]
        RNOTE --> INS["INSIGHTS.md and WEAKNESSES.md<br/>what real opponents do better than us"]
    end
    PM["postmortems/INSIGHTS.md<br/>(other teams' published lessons)"]
    QUEUE[("STRATEGIES.md queue<br/>ranked hypotheses")]
    subgraph SIM["SIMULATED MATCHES (the testing pipeline)"]
        HYP{{"New hypothesis<br/>(one change, with evidence)"}} --> CAND["Candidate bot =<br/>champion + that change"]
        CAND --> TEST["Test vs the champion: 70 maps x both sides = 140 games<br/>plus reference/imitation opponents (free Slurm nodes)"]
        TEST --> SNOTE["One folder + notes.md per simulated match<br/>(results/simulated-matches/, format in §4.2)"]
    end
    INS -- "learning points from real matches" --> QUEUE
    SNOTE -- "learning points from simulated matches" --> QUEUE
    PM -.-> QUEUE
    QUEUE -- "top item (real-match evidence first)" --> HYP
    SNOTE --> GATE{"Promotion gate:<br/>certain to beat<br/>the champion?"}
    GATE -- "no: refine, combine or reject" --> QUEUE
    GATE -- "yes" --> UP["Upload: the candidate becomes<br/>the new champion and live bot"]
    UP --> LIVE
```

In words:
1. Every real match gets a careful note. The notes add up to a ranked list of our weaknesses.
2. Weaknesses from real matches, lessons from earlier simulated matches and other teams' postmortems feed one ranked queue of **hypotheses** in `STRATEGIES.md`. Hypotheses with real-match evidence come first.
3. Each hypothesis is built into a **candidate** bot (the champion plus one change) and tested in simulated matches.
4. A candidate that is **certain** to beat the champion (see §3) is uploaded and becomes the bot playing the ladder. Its real matches then feed step 1 again.

## 2. What happens every 30 minutes (one "tick")

```mermaid
flowchart TD
    T0(["Tick every 30 min (:17 and :47)"]) --> T1["Step 1: clock and the next tournament lock<br/>Confirm which bot is live"]
    T1 --> T2["Step 2: pull new ladder games"]
    T2 --> Q1{"New real matches<br/>without a note?"}
    Q1 -- yes --> T2b["Step 2b: one notes.md per match, in its own folder<br/>Then rewrite INSIGHTS.md and WEAKNESSES.md"]
    Q1 -- no --> T3
    T2b --> T3{"Step 3: fewer than 2 experiments<br/>running?"}
    T3 -- yes --> T3b["Launch the top hypotheses from the queue<br/>Each gets a simulated-match note:<br/>sections 1-2 before the test, 3-5 after"]
    T3 -- no --> T4
    T3b --> T4{"Step 3b: a candidate at 55% or more<br/>vs the champion on its test run?"}
    T4 -- yes --> T4b["Step 4: run the full promotion gate (§3)"]
    T4 -- no --> T6
    T4b --> G{"Passed?"}
    G -- yes --> T5["Step 5: promote and upload<br/>(it becomes champion and live bot)"]
    G -- no --> T6
    T5 --> T6["Step 6: update STATUS.md, then commit and push"]
```

Step numbers match `LOOP.md`. Real-match analysis (step 2b) comes first each tick; simulated experiments keep running alongside.

## 3. The promotion gate (LOOP.md step 4): when does a new bot go live?

```mermaid
flowchart TD
    C["Candidate bot"] --> A{"(a) 140 games vs the champion:<br/>at least 82 wins, 0 bot faults?"}
    A -- no --> X["Stays a candidate:<br/>refine it, or combine it with other fixes"]
    A -- yes --> B{"(b) Gauntlet vs 5 reference bots:<br/>total wins at least the champion's,<br/>no opponent more than 4 wins worse?"}
    B -- no --> X
    B -- yes --> R{"(c) Clean release-mode run,<br/>fuel use no worse?"}
    R -- no --> X
    R -- yes --> D{"(d) Analysis: did the intended<br/>mechanism actually change?"}
    D -- no --> X
    D -- yes --> H{"(e) Also beats the old v2 bot tb_merge_b:<br/>at least 82 of 140, and no more than<br/>8 below the champion's score there?"}
    H -- no --> X
    H -- yes --> S{"(f) Does the result survive<br/>an independent skeptic agent?"}
    S -- no --> X
    S -- yes --> P["Promote: results/CHAMPION, submissions/READY.zip<br/>Upload as the new live version<br/>(never in the 60 min before a tournament lock)"]
```

(a) uses all 70 maps from both sides; 82/140 is the smallest score whose 95% Wilson lower bound is above 50%. (e) guards against gains that exist only when our bots play each other. The gate's noise was calibrated with "placebo" bots that change nothing. They score 66-68 wins out of 140 against an even 70. So passing at 82 isn't luck. Even so, local wins don't guarantee ladder wins, so the live bot's real record is monitored after every promotion.

## 4. How each note is written

### 4.1 Real-match note: one folder per match (the 5 games against one team)
`ians linux bot/results/real-matches/<YYYY-MM-DD>_<HHMM UTC>_<opponent-slug>_<group8>/notes.md`, where group8 is the first 8 characters of the match-group id ([template](ians%20linux%20bot/results/real-matches/TEMPLATE.md))

```mermaid
flowchart TB
    A["Part 1: the games played<br/>(brief, against this exact team)"] --> B["Part 2: their strategy<br/>compared with ours"]
    B --> C["Part 3: which strategy was superior<br/>(given the results), and what we learn"]
    C --> D["Part 4: weaknesses exposed,<br/>with code and hypotheses"]
    D --> E[("INSIGHTS.md<br/>WEAKNESSES.md")]
```

### 4.2 Simulated-match note: one folder per test
`ians linux bot/results/simulated-matches/<YYYY-MM-DD>_<HHMM UTC>_<candidate>/notes.md`, created by `tools/new_sim_note.py` when the test is launched ([template](ians%20linux%20bot/results/simulated-matches/TEMPLATE.md))

```mermaid
flowchart TB
    P["Part 1: the previous (parent) simulated match,<br/>analysed in the real-match format"] --> H["Part 2: the new hypothesis, the evidence<br/>(real and simulated) that it has promise,<br/>and a prediction"]
    H -- "parts 1-2 are committed before any game runs" --> T["Part 3: the test<br/>(setup, commands, results)"]
    T --> A["Part 4: this match, analysed<br/>in the same format"]
    A --> V["Part 5: verdict and<br/>next hypotheses"]
```

The notes chain together. Each simulated note starts by analysing its **parent**: the finished simulated match it builds on, usually the current champion's gate match or the experiment it refines. Several experiments can share a parent. Each note also cites the real-match notes behind its hypothesis, and `simulated-matches/INDEX.md` shows every note's parent.

```mermaid
flowchart LR
    R1["Real match:<br/>we lose to X"] -- "weakness, cited in part 2" --> S2
    S1["Parent simulated match<br/>(e.g. the champion's gate match)"] -- "analysed in part 1" --> S2["Simulated match:<br/>hypothesis fixing X"]
    S2 -- "verdict + new hypotheses" --> S3["Next simulated match"]
    S2 -- "if it passes the gate" --> LIVE["New live bot"]
    LIVE -- "plays" --> R2["Real match:<br/>did X get better?"]
```

## 5. Where to read things

| What | Where |
|---|---|
| **Insights from real matches** (start here) | [`results/real-matches/INSIGHTS.md`](ians%20linux%20bot/results/real-matches/INSIGHTS.md) |
| Ranked list of our weaknesses | [`results/real-matches/WEAKNESSES.md`](ians%20linux%20bot/results/real-matches/WEAKNESSES.md) |
| Every real match, newest first, with links to the site | [`results/real-matches/INDEX.md`](ians%20linux%20bot/results/real-matches/INDEX.md) |
| Every simulated match (the testing pipeline), in order | [`results/simulated-matches/INDEX.md`](ians%20linux%20bot/results/simulated-matches/INDEX.md) |
| Live bot, its evidence, and the candidates being watched | [`results/READY.md`](ians%20linux%20bot/results/READY.md) |
| What the agent is doing right now | [`results/STATUS.md`](ians%20linux%20bot/results/STATUS.md) |
| Hypothesis queue and every verdict so far | [`results/STRATEGIES.md`](ians%20linux%20bot/results/STRATEGIES.md) |
| Lessons from other teams' published postmortems | [`postmortems/INSIGHTS.md`](ians%20linux%20bot/postmortems/INSIGHTS.md) |
| The detailed operating protocol | [`LOOP.md`](ians%20linux%20bot/LOOP.md) |
| History, lineage and engine facts | [`HANDOFF.md`](ians%20linux%20bot/HANDOFF.md) |

```text
ians linux bot/
├── bots/<name>/src/bot.py        every bot; the champion is named in results/CHAMPION
├── results/
│   ├── real-matches/
│   │   ├── INSIGHTS.md           the readable synthesis (kept short, rewritten each update)
│   │   ├── WEAKNESSES.md         ranked weakness ledger
│   │   ├── INDEX.md              all real matches, with site links
│   │   ├── TEMPLATE.md
│   │   ├── 2026-11-01_0532_team-name_5eca4952/notes.md     one folder per real match
│   │   └── studies/…/notes.md    analyses across many real matches
│   ├── simulated-matches/
│   │   ├── INDEX.md              all simulated matches, oldest first
│   │   ├── TEMPLATE.md
│   │   └── 2026-11-01_0437_c2_respawn/notes.md             one folder per simulated match
│   ├── STATUS.md  READY.md  STRATEGIES.md  CHAMPION
│   └── ladder-games.jsonl        every real ladder game (one line each)
├── tools/                        harness: eval, gauntlet, ladder_pull, scout, organize_notes, onslurm
├── LOOP.md                       the operating protocol
└── HANDOFF.md                    history and engine facts
```

## 6. Glossary

| Term | Meaning |
|---|---|
| Match (real) | The 5 games our live bot plays against one team in one ladder "match group". It gets one folder and one note |
| Match (simulated) | One test of a candidate, usually 140 games against the champion. It gets one folder and one note |
| Champion | Our best validated bot (`results/CHAMPION`). It is also the bot playing the ladder |
| Candidate | The champion plus one change that tests a hypothesis |
| Gate | The checks in §3 that a candidate must pass to become champion |
| Tick | One pass of the loop in §2, every 30 minutes |
| Version (v2, v3, v4, ...) | Our uploads on the site, in order. `results/ladder-versions.json` records when each went live |

## 7. Running it

- The agent runs on the Harvard FASRC cluster. All games run on the free Slurm `test` partition through `tools/onslurm.sh`.
- Setup and the rules for agents are in [`CLAUDE.md`](CLAUDE.md). The step-by-step protocol is in [`LOOP.md`](ians%20linux%20bot/LOOP.md).
- Useful commands, from `ians linux bot/`:
  - `python3.12 tools/ladder_pull.py`: fetch new ladder games and print the record per version.
  - `python3.12 tools/scout.py --group <id>`: profile both teams in a real match.
  - `python3.12 tools/unscouted.py --claim`: list and claim the real matches that still need a note.
  - `python3.12 tools/new_sim_note.py CAND --vs CHAMP --prev PARENT`: start a simulated-match note before its test.
  - `python3.12 tools/organize_notes.py`: tidy the note folders and rebuild both indexes.
  - `tools/onslurm.sh -c 24 -m 16G -t 00:20:00 -J gate -- python3.12 tools/eval.py CAND CHAMP --maps all --jobs 16`: a 140-game head-to-head.
