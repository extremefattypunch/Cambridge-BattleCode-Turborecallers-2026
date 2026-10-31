# Continuous improvement loop (runs 24/7 on the dev PC)

Standing instruction from the user (31 Oct 2026), to be followed at all times:
- run our own simulated matches;
- monitor the leaderboard and our ladder matches;
- submit improved bots for every tournament and qualifier.

A session-scheduled job (`CronCreate`, about every 30 min) triggers one **tick**. CronCreate jobs are session-only and expire after 7 days, so re-create the job in each new session. The live state of the loop is in `results/STATUS.md`.

## Each tick
1. **Clock and deadlines.**
   - Run `date`.
   - Read the next tournament lock from https://2026a.battlecode.co.uk/game/tournaments (or `/api/v1/tournaments/...`).
   - Record it in `results/STATUS.md`.
2. **Ladder monitor.**
   - In the logged-in Chrome tab, fetch `/api/v1/match-groups?scope=team`, then `/api/v1/match-groups/<id>` for any new groups.
   - Append the new games to `results/ladder-games.jsonl`, deduplicated by match id. Each line holds: version, opponent, opponent rating, map, side, result, scores, rounds, end reason, both drafts.
   - Note the current rating and the live version's record in STATUS.md.
   - Flag fresh losses, along with the opponent's draft and the map, for the improvement queue.
   - Format JS output with `|` separators, since outputs that look like query strings get blocked.
3. **Local simulation health.**
   - Make sure `tools/soak.py` is running. If not, restart it with `nice -n 10 python3 -I tools/soak.py --jobs 3 >> matches/soak.log 2>&1` in the background.
   - Read `python3 -I tools/soak.py --report --last 400`. It lists the weakest maps and match-ups.
4. **Improvement pipeline.** If no improvement workflow is running (check STATUS.md and the background tasks), launch one, targeting the top item from:
   - (a) fresh ladder losses;
   - (b) the soak report's weakest maps and opponents;
   - (c) HANDOFF.md §5.

   Rules for the workflow:
   - Candidates live in their own `bots/<cand>` (`tools/newbot.py`).
   - Never edit the champion in place.
   - Use imitation opponents (our bot with a ladder-common draft, e.g. `imit_test`, `lad_*`) to reproduce real losses.
5. **Promotion gate.** A candidate replaces the champion only if all of these hold:
   - `tools/eval.py <cand> <champion> --maps sprint`: **≥ 55%** and **botFaults 0**;
   - `tools/gauntlet.py <cand> --maps sprint`: no regression against the rest of the pool;
   - one `--release` game: 0 crashes;
   - for movement or draft changes, also `--maps all`: ≥ 55%.
6. **Promote and submit.**
   - Write `results/CHAMPION`.
   - Run `./cli/cambc bundle <bot> --output submissions/<bot>.zip`.
   - Upload it at /game/submissions (file input, then a note, then Upload; retry on HTTP 503).
   - Confirm the version turns **Active / Verified** on the next match.
   - Update HANDOFF.md §3.
   - Commit and push.
   - **Freeze window:** no new uploads in the last 60 min before a tournament lock unless the candidate already passed the full gate.
7. **Commit and push.** Commit STATUS.md, `ladder-games.jsonl` and any promoted bot to branch `ians-linux-bot`. Push needs the Bash sandbox disabled; retry, because GitHub was flaky.

## Parallel track: C++ port
The user asked to move to C++ after Sprint 3. Measurements on 31 Oct:
- The C++ starter uses about 19× less fuel than the Python starter, but its budget is 25× smaller. So C++ gives no compute headroom for code like ours.
- Python therefore stays the main line.
- A faithful port (`bots/cpp_*`) is developed alongside it and goes through the same promotion gate against the Python champion. Switch languages only if it wins.
