# Cambridge Battlecode 2026a — team Turbo Recallers

Team repo for Cambridge Battlecode 2026a ("cambc", https://2026a.battlecode.co.uk). Our bots are Python. Everything lives in `ians linux bot/`. The folder name has spaces, so always quote it.

**Read first:**
1. `ians linux bot/HANDOFF.md`: current state, submitted versions, results, prioritised next steps, and the overnight improvement protocol.
2. `ians linux bot/.claude/skills/`: the `cambc-game-rules` and `cambc-bot-api-python` skills.
   - Claude Code discovers them automatically when you work inside that folder.
   - They hold verified rules and API facts plus the full official docs.
3. `ians linux bot/postmortems/INSIGHTS.md`: a census of ~1,040 ranked games played by the top-20 ladder teams, plus lessons from past winners.

## Layout (`ians linux bot/`)
| Path | What |
|---|---|
| `bots/<name>/src/*.py` | Bots. `main.py` dispatches draft vs play; `bot.py` holds the logic. The current champion is named in `results/CHAMPION` |
| `tools/eval.py A B` | Head-to-head on a map set, both sides. Prints per-game rows and a `SUMMARY` line |
| `tools/tournament.py A B C ...` | Round-robin matrix |
| `tools/gauntlet.py CAND` | Candidate vs the reference pool. Appends to `results/gauntlet.jsonl`, which is git-tracked |
| `postmortems/match_metrics.py matches/<tag>` | Tribute sizes, deaths and gem loss by killer, fuel exhaustion, wards |
| `docs/` | Official GameRules.md, BotAPI*.md and handbook guides |
| `maps/` | Local map pool (70 maps). Sprints use **unseen** maps, so never special-case map names |
| `cli/cambc` | CLI binary, **gitignored** (99 MB). On a new machine see Setup |
| `docs/CLI_ONLY.md` | CLI equivalents of site tasks (login, submit, match-groups) for agents without a browser |
| `matches/`, `replays/`, `.cambc/` | Generated output, gitignored |

## Setup on a new machine
```bash
cd "ians linux bot"
curl -L -o cli/cambc https://2026a.battlecode.co.uk/api/v1/distribution/linux-x64/download && chmod +x cli/cambc
# or: python -m pip install --upgrade cambc  (tools/eval.py falls back to `cambc` on PATH or $CAMBC)
./cli/cambc init --yes .      # refreshes sdk/ and maps/ and keeps bots/; check `git diff` afterwards
./cli/cambc maps pull         # refresh the published map pool
python3 tools/eval.py sf_base starter-python --maps quick --jobs 4   # smoke test (~1 min on 16 cores)
```
The CLI version must match the platform engine (it was 4.0.0 / engine 2.0.0 on 31 Oct 2026). If `/game/download` lists a newer version, update before evaluating.

## Rules of the road
- **Run-batch manifests are whitespace-separated and resolve paths relative to the manifest file.** `tools/eval.py` handles this; reuse it rather than writing new runners.
- **Measure every change** with `tools/eval.py NEW CHAMPION --maps sprint` (40 games). 2–3 games of difference is noise. Require `botFaults(A) 0`.
- **Python fuel is 2.5M per turn.** `fuelExhausted` events, counted by match_metrics, mean a turn was suspended. Keep them near 0.
- **Commit and push milestones** to branch `ians-linux-bot` so teammates can follow.
  - Never commit `cli/cambc` or `postmortems/raw/` (both gitignored).
  - On the original dev machine, `git push` needed the Bash sandbox disabled.
- **Submitting** means uploading the zip from `./cli/cambc bundle <bot> --output submissions/<bot>.zip` at https://2026a.battlecode.co.uk/game/submissions.
  - A new upload becomes the selected live version. Older versions keep "Make Live".
  - At each tournament deadline the live version is snapshotted, then submissions lock for about an hour.
  - The upload API sometimes returns 503; retrying worked.
  - **Get the user's OK before uploading** unless they have pre-authorised it.
- **Ask the user before** anything that changes the team account (submissions, eligibility, team settings).
