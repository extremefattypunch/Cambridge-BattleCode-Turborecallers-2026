# Continuous improvement loop (runs 24/7 on the dev PC)

**Standing instructions from the user (31 Oct 2026):**
- Keep improving all the time. Run our own simulated matches, monitor the leaderboard and our ladder matches, and submit to the site for every tournament and qualifier.
- **Every simulated match must test a new, meaningful, distinct strategy** with improvement potential, drawn from research on our ladder matches, our own bots, or postmortems. Never simulate for its own sake.
- **Our submission is always the strongest bot we have found.**

A session-scheduled job (`CronCreate`, about every 30 min) triggers one **tick**. CronCreate jobs are session-only and expire after 7 days, so re-create the job in each new session.

- State: `results/STATUS.md`
- Strategy backlog and verdicts: `results/STRATEGIES.md`
- Real ladder games: `results/ladder-games.jsonl` (plus `results/ladder-games-2026-10-31.json`)

## Each tick
1. **Clock and deadlines.**
   - Run `date`.
   - Read the next tournament lock from https://2026a.battlecode.co.uk/game/tournaments.
   - Record it in STATUS.md.
2. **Ladder research** (real games are analysed too).
   - In the logged-in Chrome tab, fetch `/api/v1/match-groups?scope=team`, then `/api/v1/match-groups/<id>` for any new groups.
   - Save the responses as a list via the localhost receiver to `matches/ladder/raw/<name>.json`.
   - Run `python3 -I tools/ladder_log.py matches/ladder/raw/<name>.json`. It appends the new games to `results/ladder-games.jsonl`, deduplicated by match id, and prints the record by version and team size plus the live version's losses.
   - Record the rating in STATUS.md.
   - Turn each **new** loss pattern into a strategy hypothesis in STRATEGIES.md (opponent comp, map type, how they won).
   - Format JS output with `|` separators (outputs that look like query strings are blocked).
   - Replay bundles (`/api/v1/matches/<id>/bundle`) are async: poll `pollUrl`. Download them only for losses we want to study.
3. **Strategy experiments: hypothesis → test → detailed analysis → new hypotheses.** This is the core learning process. If fewer than about 2 experiment workflows are running, take the top untested items from the STRATEGIES.md queue and launch a workflow in which every strategy goes through all four stages:
   - **(a) Implement** the strategy in its own candidate bot (`tools/newbot.py <champion> <cand>`; never edit the champion).
   - **(b) Test** it against the champion, and against imitation opponents of real ladder comps when the hypothesis targets them (e.g. `imit_test`, `lad_*`). Use `tools/eval.py ... --keep`.
   - **(c) Analysis session (mandatory, for every experiment).**
     - Run `python3 -I tools/analyze_match.py --summary matches/<tag> --games`, which contrasts wins and losses: gem race, opening tempo, K/D, damage, gold, fuel.
     - Read full per-game narratives (`tools/analyze_match.py matches/<tag>/<map>__A.json`) for every loss and any surprising win: deaths with killer and location, per-champion lines, tribute habits.
     - Read bot stdout from the kept replay zips (`team-a.stdout`) when decisions need explaining.
     - Answer: did the mechanism we targeted actually change, and why did the remaining losses happen?
   - **(d) Write** `results/experiments/<YYYY-MM-DD>-<cand>.md` from the template, covering:
     - the hypothesis and its source;
     - the setup;
     - the eval lines;
     - the analysis findings, with evidence;
     - the verdict (kept / rejected / inconclusive);
     - the **new hypotheses** the analysis suggests.

     Then add those hypotheses to the STRATEGIES.md queue, record the verdict there, and never re-run a rejected idea unchanged. Combine compatible winners in a follow-up merge experiment.

   **No match is run without a hypothesis, and no experiment ends without an analysis session and a written report.**
3b. **Candidate watch and the ready-to-submit bot** (user, 31 Oct).
   - Always keep the **strongest validated bot** ready to submit for any tournament at any time:
     - `results/CHAMPION` holds its name;
     - `submissions/READY.zip` holds its bundle;
     - `results/READY.md` holds its evidence and the watched candidates.
   - Look actively for improved candidates. The moment any experiment shows **≥ 55% vs the champion on sprint** (a screening threshold only), immediately launch a gate workflow for it (step 4) on a frozen snapshot copy (`tools/newbot.py <cand> <cand>_g1`), without waiting for its batch to finish.
   - Compatible near-winners (e.g. two candidates at 55% that change different subsystems) get a merge candidate that is gated too.
   - On promotion, rebuild READY.zip and **upload it as the live version right away** (step 5), so the live bot is always the best one we have, not only at deadlines.
4. **Promotion gate: the candidate must be *certain* to outperform the champion** (user, 31 Oct: "it must be certain to outperform the old bot"). All of these must hold:
   - **(a) Head-to-head, decisive:** `tools/eval.py <cand> <champion> --maps all` (70 maps × both sides = 140 games; local games are deterministic, so this is all the head-to-head evidence there is). The **95% Wilson lower bound of the win rate must be above 50%**, i.e. **≥ 82 of 140 (58.6%)**. Also **botFaults 0**.
   - **(b) Paired gauntlet:** `tools/gauntlet.py <cand> --pool <P> --maps sprint` and the same command for the champion, against the same pool `P` (currently sf_bank, tb_merge_a, tb_aggro, imit_test, lad_vcst). Total candidate wins must be **≥ the champion's**, and it must not lose more than 4 games' worth against any single opponent.
   - **(c) Robustness:** one `--release` game with 0 crashes, and `match_metrics` fuelExhausted not worse than the champion's.
   - **(d) Analysis session:** confirms the targeted mechanism changed and that the gain isn't an artefact (e.g. one map family).

   **Anything short of this stays a candidate, never a submission.** Near-misses (e.g. 55–58%) are combined or refined and re-gated, not shipped.
5. **Promote and submit.**
   - Write `results/CHAMPION`.
   - Run `./cli/cambc bundle <bot> --output submissions/<bot>.zip`.
   - Upload it at /game/submissions (file input, then a note, then Upload; retry on HTTP 503).
   - Confirm the version turns **Active / Verified** on our next match.
   - Update HANDOFF.md §3.
   - **Freeze window:** no uploads in the last 60 min before a tournament lock unless the candidate already passed the full gate.
6. **Commit and push** STATUS.md, STRATEGIES.md, `ladder-games.jsonl` and any promoted or tested bots to branch `ians-linux-bot`. Push needs the Bash sandbox disabled; retry, because GitHub was flaky.

`tools/soak.py` exists, but per the user's rule it is **not** run continuously. Use it only to test a specific hypothesis, for example "does candidate X fix our weak maps?".

## Parallel track: C++ port (STRATEGIES Q11)
The user asked to move to C++ after Sprint 3. Measurements on 31 Oct:
- The C++ starter uses about 19× less fuel than the Python starter, but its budget is 25× smaller. So C++ gives no compute headroom for code like ours.
- Python therefore stays the main line.
- The port (`bots/cpp_port`) goes through the same gate against the Python champion. Switch languages only if it wins.
