# Continuous improvement loop (runs 24/7; moved from the dev PC to the cluster agent on 31 Oct)

**Standing instructions from the user (31 Oct 2026):**
- Keep improving all the time. Run our own simulated matches, monitor the leaderboard and our ladder matches, and submit to the site for every tournament and qualifier.
- **Every simulated match must test a new, meaningful, distinct strategy** with improvement potential, drawn from research on our ladder matches, our own bots, or postmortems. Never simulate for its own sake.
- **Our submission is always the strongest bot we have found.**

Something must trigger one **tick** about every 30 min. On the dev PC this was a session-scheduled `CronCreate` job (session-only, expires after 7 days). On the cluster, use whatever keeps the agent running there: `/loop`, CronCreate, or an external scheduler. **Start with `results/STATUS.md` → "Resume here".**

**Work that was running on the dev PC when it stopped** (all must be restarted by the cluster agent; nothing runs by itself):
- the scheduled tick (this file);
- strategy experiments with analysis sessions (batch 1 interrupted; see `results/simulated-matches/2026-11-01_0017_batch1-interim/notes.md`);
- the promotion gate for the best candidates (gate round 1 interrupted; nothing gated);
- ladder tracking (needs `cambc login` on a CLI-only machine);
- postmortem and ladder research (`postmortems/INSIGHTS.md`; Q14/Q19 replay studies pending);
- the C++ port track (`bots/cpp_port`, at parity).

- State: `results/STATUS.md`
- Strategy backlog and verdicts: `results/STRATEGIES.md`
- Real ladder games: `results/ladder-games.jsonl` (plus `results/ladder-games-2026-10-31.json`)

## Each tick
1. **Clock and deadlines.**
   - Run `date`.
   - Read the next tournament lock from https://2026a.battlecode.co.uk/game/tournaments.
   - Record it in STATUS.md.
2. **Ladder research** (real games are analysed too).
   - **Without a browser (cluster):** after a one-time `cambc login` by a human, use:
     - `./cli/cambc matches list --team me --kind ranked --json --limit 50` lists our games (map, teams, drafts);
     - `./cli/cambc matches summary <id> --json -o matches/ladder/<id>.json` gets a game's statistics, which should feed `tools/analyze_match.py`. Verify the format on the first one;
     - `./cli/cambc matches download <id> -o ...` gets the replay;
     - `./cli/cambc ladder --json` gets the standings.

     See `docs/CLI_ONLY.md`. The site API JSON that `tools/ladder_log.py` expects is the `/api/v1/match-groups/<id>` response (`group` + `matches` with per-side `draft`, `score`, `result`). If `cambc matches` returns a different shape, adapt `tools/ladder_log.py` or write a small converter.
   - **With a browser (dev PC):**
     - in the logged-in Chrome tab, fetch `/api/v1/match-groups?scope=team`, then `/api/v1/match-groups/<id>` for any new groups;
     - post the list to a localhost receiver, saving it to `matches/ladder/raw/<name>.json`;
     - format JS output with `|` separators, because outputs that look like query strings are blocked;
     - replay bundles (`/api/v1/matches/<id>/bundle`) are async: poll `pollUrl`.
   - Then run `python3.12 -I tools/ladder_log.py matches/ladder/raw/<name>.json`. It appends the new games to `results/ladder-games.jsonl`, deduplicated by match id, and prints the record by version and team size plus the live version's losses.
   - Record the rating in STATUS.md.
   - Turn each **new** loss pattern into a strategy hypothesis in STRATEGIES.md (opponent comp, map type, how they won). Download replays only for losses we want to study, and run `tools/analyze_match.py` on their statistics.
2b. **Scout every new match set** (user, 1 Nov: analyse what exactly we were weak at, what the opponent's strategy was, and how it was superior or inferior to ours, not just who we played).
   - Pull each new set with `python3.12 tools/ladder_pull.py`.
   - **This is the top priority each tick.** `python3.12 tools/unscouted.py --claim` lists *and claims* the matches without a note, newest first, each with its folder name. A claim hides a match from other runs for 3 hours. Run them through `tools/workflows/ladder_scout.js` (`Workflow({scriptPath: ".../ians linux bot/tools/workflows/ladder_scout.js", args: <that JSON>})`).
   - Self-play experiments (step 3) keep running alongside at lower priority; the user wants both.
   - **One folder per real match:** `results/real-matches/<YYYY-MM-DD>_<HHMM UTC>_<opponent>_<group8>/notes.md`. That is the 5 games against one team in one match group. Use `results/real-matches/TEMPLATE.md`, in the user's order:
     1. the games played, briefly, against this exact team;
     2. their strategy compared with ours;
     3. which strategy was superior given the results, and what we learn;
     4. the weaknesses exposed, with the responsible code and testable hypotheses.

     Tools: `tools/scout.py` profiles both teams; `tools/analyze_match.py` narrates a game.
   - With each batch of notes, rewrite (do not append to) the short, readable synthesis `results/real-matches/INSIGHTS.md` (laid out like `postmortems/INSIGHTS.md`; at most 150 lines) and the ranked ledger `results/real-matches/WEAKNESSES.md` (at most 25 open rows). Start from the current versions plus the new notes; never re-read every note. Feed the top items into the STRATEGIES.md queue.
   - `python3.12 tools/organize_notes.py` rebuilds `results/real-matches/INDEX.md` and `results/simulated-matches/INDEX.md`, and moves any note left in an old location.
   - The full replay zip (`cambc matches download <id>`) adds our bot's stdout and per-turn fuel trace when decisions need explaining.
3. **Strategy experiments: hypothesis → test → detailed analysis → new hypotheses.** This is the core learning process. If fewer than about 2 experiment workflows are running, take the top untested items from the STRATEGIES.md queue and launch a workflow in which every strategy goes through all four stages:
   - **(a0) Write the first half of the note before anything runs.** Run `python3.12 tools/new_sim_note.py <cand> --vs <champion> --prev <parent folder>`. It creates `results/simulated-matches/<date>_<HHMM UTC>_<cand>/notes.md` from TEMPLATE.md. Fill in and commit:
     - §1, the parent simulated match analysed in the real-match format;
     - §2, the hypothesis, the evidence links (real and simulated notes) and a numeric prediction.

     §2 is never edited after the test.
   - **(a) Implement** the strategy in its own candidate bot (`tools/newbot.py <champion> <cand>`; never edit the champion).
   - **(b) Test** it against the champion, and against imitation opponents of real ladder comps when the hypothesis targets them (e.g. `imit_test`, `lad_*`). Use `tools/eval.py ... --keep`.
   - **(c) Analysis session (mandatory, for every experiment).**
     - Run `python3.12 -I tools/analyze_match.py --summary matches/<tag> --games`, which contrasts wins and losses: gem race, opening tempo, K/D, damage, gold, fuel.
     - Read full per-game narratives (`tools/analyze_match.py matches/<tag>/<map>__A.json`) for every loss and any surprising win: deaths with killer and location, per-champion lines, tribute habits.
     - Read bot stdout from the kept replay zips (`team-a.stdout`) when decisions need explaining.
     - Answer: did the mechanism we targeted actually change, and why did the remaining losses happen?
   - **(d) Complete the note** created in (a0). It is one folder per simulated match: `results/simulated-matches/<YYYY-MM-DD>_<HHMM UTC>_<cand>/notes.md`. Use `results/simulated-matches/TEMPLATE.md`, in the user's order:
     1. **The previous simulated match, analysed**, in the same format as a real-match note. This is the most recent finished simulated match this hypothesis builds on, usually the champion's own gate match or the experiment being refined.
     2. **The new hypothesis**: the change; why it should win; the evidence that it has promise, linking the real-match notes and earlier simulated-match notes that motivated it; the prediction.
     3. **The test**: setup, commands, verbatim SUMMARY/GAUNTLET lines.
     4. **This match, analysed**, in the same format: games, strategies compared, which was superior, whether the targeted mechanism changed, and why the remaining games were lost.
     5. **Verdict and new hypotheses** (kept / rejected / inconclusive / promoted, with gate numbers).

     Then run `python3.12 tools/organize_notes.py`, which rebuilds the indexes.
   - **Keep STRATEGIES.md bounded.**
     - Merge each new hypothesis into the single ranked `## Queue` table: one one-line row, linking the note for detail. Never add a separate "New hypotheses from …" section.
     - Record each verdict as one row in `## Tested`, linking the note.
     - Once the file passes ~300 lines, move closed Tested rows from before the current champion's lineage to `results/strategies-archive.md`.
     - Never re-run a rejected idea unchanged. Combine compatible winners in a follow-up merge experiment.

   **No match is run without a hypothesis, and no experiment ends without an analysis session and a written report.**
3b. **Candidate watch and the ready-to-submit bot** (user, 31 Oct).
   - Always keep the **strongest validated bot** ready to submit for any tournament at any time:
     - `results/CHAMPION` holds its name;
     - `submissions/READY.zip` holds its bundle;
     - `results/READY.md` holds its evidence and the watched candidates.
   - Look actively for improved candidates. The moment any experiment shows **≥ 55% vs the champion on its test run** (usually all 70 maps; a screening threshold only), immediately launch a gate workflow for it (step 4) on a frozen snapshot copy (`tools/newbot.py <cand> <cand>_g1`), without waiting for its batch to finish.
   - Compatible near-winners (e.g. two candidates at 55% that change different subsystems) get a merge candidate that is gated too.
   - On promotion, rebuild READY.zip and **upload it as the live version right away** (step 5), so the live bot is always the best one we have, not only at deadlines.
4. **Promotion gate: the candidate must be *certain* to outperform the champion** (user, 31 Oct: "it must be certain to outperform the old bot"). All of these must hold:
   - **(a) Head-to-head, decisive:** `tools/eval.py <cand> <champion> --maps all` (70 maps × both sides = 140 games; local games are deterministic, so this is all the head-to-head evidence there is). The **95% Wilson lower bound of the win rate must be above 50%**, i.e. **≥ 82 of 140 (58.6%)**. Also **botFaults 0**.
   - **(b) Paired gauntlet:** `tools/gauntlet.py <cand> --pool <P> --maps sprint` and the same command for the champion, against the same pool `P` (currently sf_bank, tb_merge_a, tb_aggro, imit_test, lad_vcst). Total candidate wins must be **≥ the champion's**, and it must not lose more than 4 games' worth against any single opponent.
   - **(c) Robustness:** one `--release` game with 0 crashes, and `match_metrics` fuelExhausted not worse than the champion's.
   - **(d) Analysis session:** confirms the targeted mechanism changed and that the gain isn't an artefact (e.g. one map family).
   - **(e) Old-bot hedge** (from 1 Nov, after the v3 ladder study): `tools/eval.py <cand> tb_merge_b --maps all` must score **≥ 82/140** and **no more than 8 below the champion's own score** against tb_merge_b (c2_respawn: 98/140). This guards against gains that exist only in self-play. Placebo runs vary by about ±3 here.
   - **(f) Skeptic:** an independent agent tries to refute (a)-(e) from the kept games, including a release-mode rerun with logs on and a placebo-perturbed replicate. Promote only if the claim survives.

   **Anything short of this stays a candidate, never a submission.** Near-misses (e.g. 55–58%) are combined or refined and re-gated, not shipped.
5. **Promote and submit.**
   - Write `results/CHAMPION`.
   - Run `./cli/cambc bundle <bot> --output submissions/<bot>.zip`.
   - Upload it: on the CLI, `cambc submit <bot> -n "<note>"` (needs `cambc login`); in a browser, /game/submissions (file input, then a note, then Upload; retry on HTTP 503). The user **pre-authorised** uploads of bots that pass the full gate.
   - Confirm the version turns **Active / Verified** on our next match.
   - Update HANDOFF.md §3.
   - **Freeze window:** no uploads in the last 60 min before a tournament lock (CLAUDE.md standing instruction), even for a candidate that passed the full gate. Upload right after the lock instead.
6. **Commit and push** to branch `ians-linux-bot`, so teammates can follow:
   - STATUS.md, STRATEGIES.md and `ladder-games.jsonl`;
   - `results/real-matches/` and `results/simulated-matches/`, after `python3.12 tools/organize_notes.py`;
   - `tools/` changes;
   - any promoted or tested bots.

   Raw `matches/` output is gitignored, so copy the key numbers into the notes. On the dev PC, push needed the Bash sandbox disabled, and GitHub was intermittently flaky, so retry.

`tools/soak.py` exists, but per the user's rule it is **not** run continuously. Use it only to test a specific hypothesis, for example "does candidate X fix our weak maps?".

## Parallel track: C++ port (STRATEGIES Q11)
The user asked to move to C++ after Sprint 3. Measurements on 31 Oct:
- The C++ starter uses about 19× less fuel than the Python starter, but its budget is 25× smaller. So C++ gives no compute headroom for code like ours.
- Python therefore stays the main line.
- **Status:** `bots/cpp_port` is a complete faithful port (~3,200 lines; `DESIGN.md` has the fuel benchmarks and design, `NOTES.md` the status). It plays at parity with the Python champion (sprint 20W-20L), with **0 fuel exhaustions** against Python's ~87/game. The independent verify/fix review never ran.
- It goes through the same gate against the Python champion; switch languages only if it wins. Its fuel headroom makes it the natural home for compute-heavy ideas (e.g. Q25 cheaper sensing, deeper fight simulation).
