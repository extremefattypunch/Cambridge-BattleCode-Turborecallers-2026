# Cambridge Battlecode 2026a — team Turbo Recallers

Team repo for Cambridge Battlecode 2026a ("cambc", https://2026a.battlecode.co.uk). Our bots are Python, and a C++ port is at parity. Everything lives in `ians linux bot/`. The folder name has spaces, so always quote it.

## Start here (agent taking over, e.g. on the cluster)
1. **`ians linux bot/results/STATUS.md` → "Resume here"**: what was in progress when the dev-PC session stopped, and what to do next, in order.
2. **`ians linux bot/LOOP.md`**: the operating protocol the user wants run continuously. It covers:
   - strategy experiments with analysis sessions;
   - ladder tracking;
   - the promotion gate;
   - submissions;
   - the C++ track.
3. `ians linux bot/results/STRATEGIES.md`: every strategy tested (with verdicts) and the hypothesis queue.
4. `ians linux bot/results/READY.md`: the current best bot (always ready to submit) and the candidates being watched.
5. `ians linux bot/HANDOFF.md`: lineage, results history and engine facts that bit us.
6. `ians linux bot/.claude/skills/`: the `cambc-game-rules` and `cambc-bot-api-python` skills, auto-discovered inside that folder. They hold verified rules and API facts plus the full official docs.
7. `ians linux bot/postmortems/INSIGHTS.md`: a census of ~1,040 ranked games by the top-20 teams, plus lessons from past winners' postmortems. `postmortems/notes/` has per-source notes.

## Standing instructions from the user (31 Oct 2026; these persist across sessions)
- **Improve 24/7.** Keep the loop in LOOP.md running continuously:
  - our own strategy experiments;
  - leaderboard and ladder-match monitoring;
  - submissions for every tournament and qualifier.
- **Every simulated match must test a new, meaningful, distinct strategy hypothesis.** Hypotheses come from our real ladder games, our own bots, or postmortems. **Never simulate for its own sake** (no idle soak runs).
- **Every experiment ends in a detailed analysis session.** Use `tools/analyze_match.py` to cover the gem race, opening tempo, deaths with killers, per-champion lines, and replay stdout. Write one folder per simulated match, `results/simulated-matches/<date>_<HHMM>_<cand>/notes.md`, following its `TEMPLATE.md`:
  1. the previous simulated match analysed, in the same format as a real-match note;
  2. the new hypothesis and the evidence (real and simulated) that it has promise;
  3. the test;
  4. this match analysed;
  5. the verdict.

  Feed new hypotheses back into STRATEGIES.md. The user calls this "the critical learning process".
- **Analyse every real ladder match carefully, from now on** (user, 1 Nov). Real-match insights are worth more than self-play.
  - Catch up on the most recent sets first, then keep up with each new one.
  - Write one folder per real match (the 5 games vs one team): `results/real-matches/<date>_<HHMM>_<opponent>_<group8>/notes.md`. Follow its `TEMPLATE.md`:
    1. the games played;
    2. their strategy vs ours;
    3. which strategy was superior and what we learn;
    4. our weaknesses and hypotheses.
  - Fold the notes into the short, rewritten-not-appended `results/real-matches/INSIGHTS.md` (laid out like `postmortems/INSIGHTS.md`) and `WEAKNESSES.md`.
  - The workflow, with flowcharts, is in the repo README; keep the README in sync when the process changes (user, 1 Nov).
  - Prioritise hypotheses from these insights.
  - **Keep learning from simulated matches too.** Self-play experiments, their analysis sessions and the gate continue alongside. The user only asked to prioritise real matches, not to drop self-play (1 Nov).
- **Always keep a ready-to-submit best bot:** `results/CHAMPION`, `submissions/READY.zip` and `results/READY.md`.
  - Look actively for improved candidates. A screen result of ≥ 55% vs the champion goes straight to the full gate.
  - Upload a promoted bot right away, so the live bot is always our best.
- **A submission must be *certain* to outperform the current bot.** The LOOP.md §4 gate:
  - ≥ 82/140 on `--maps all` (95% Wilson lower bound above 50%);
  - a paired gauntlet ≥ the champion's;
  - a clean release-mode run;
  - an analysis that confirms the mechanism.

  Never ship 55% near-misses or untested last-minute candidates. Freeze uploads in the last 60 min before a tournament lock.
- **Uploads that pass the gate are pre-authorised.** Ask the user before anything else that changes the team account (eligibility, team settings, `match-groups create`, which uses the team's shared quota).
- **Commit and push milestones** to branch `ians-linux-bot` so teammates can follow.
- **Language:** the user asked for C++. Measurements showed no fuel advantage for code like ours: the C++ starter uses ~19× less fuel per turn on a 25× smaller budget. So Python is the main line, and `bots/cpp_port` (parity, 0 fuel exhaustions) is the parallel track. Switch only when C++ passes the gate against the Python champion.

## Layout (`ians linux bot/`)
| Path | What |
|---|---|
| `bots/<name>/src/*.py` | Bots. `main.py` dispatches draft vs play; `bot.py` holds the logic. The champion is named in `results/CHAMPION` |
| `bots/cpp_port/` | C++ port of the champion (`DESIGN.md`: fuel benchmarks and design; `NOTES.md`: status) |
| `tools/eval.py A B` | Head-to-head on a map set, both sides (`--maps quick\|sprint\|all\|a,b`, `--keep`). Prints a `SUMMARY` line |
| `tools/analyze_match.py` | Post-game analysis: one stats JSON gives a narrative; `--summary <folder> --games` contrasts wins with losses |
| `tools/gauntlet.py CAND` | Candidate vs the reference pool. Appends to `results/gauntlet.jsonl` (git-tracked) |
| `tools/tournament.py A B C ...` | Round-robin matrix |
| `tools/newbot.py SRC DST` | Fork a bot safely (validated names, no build cache) |
| `tools/ladder_log.py [files]` | Append real ladder games to `results/ladder-games.jsonl` and summarise the record |
| `tools/soak.py` | Random-map soak runs. Only for testing a specific hypothesis, never as an idle loop |
| `postmortems/match_metrics.py matches/<tag>` | Tribute sizes, deaths and gem loss by killer, fuel exhaustion, wards |
| `results/` | STATUS, STRATEGIES, READY, CHAMPION, the ladder logs (`ladder-games.jsonl`, `ladder-versions.json`) and gauntlet results |
| `results/real-matches/` | One folder per real ladder match (`notes.md`), plus `INSIGHTS.md`, `WEAKNESSES.md`, `INDEX.md`, `TEMPLATE.md` and `studies/` |
| `results/simulated-matches/` | One folder per simulated match (`notes.md`), plus `INDEX.md` and `TEMPLATE.md`. `tools/organize_notes.py` keeps both trees and their indexes tidy |
| `docs/` | Official GameRules.md, BotAPI*.md, handbook guides, `CLI_ONLY.md` (site tasks without a browser), `claude-settings.example.json` (optional permission allowlist for an unattended agent) |
| `maps/` | Local map pool (70 maps). Sprints use **unseen** maps, so never special-case map names |
| `cli/cambc` | CLI binary, **gitignored** (99 MB). See Setup |
| `matches/`, `replays/`, `.cambc/`, `submissions/*.zip` | Generated output, gitignored. Copy key numbers into reports |

## Setup on a new machine
```bash
cd "ians linux bot"
curl -L -o cli/cambc https://2026a.battlecode.co.uk/api/v1/distribution/linux-x64/download && chmod +x cli/cambc
# or: python -m pip install --upgrade cambc  (tools/eval.py falls back to `cambc` on PATH or $CAMBC)
./cli/cambc init --yes .      # refreshes sdk/ and maps/, keeps bots/; check `git diff` afterwards
./cli/cambc maps pull         # refresh the published map pool
python3 tools/eval.py sf_base starter-python --maps quick --jobs 4   # smoke test (~1 min on 16 cores)
./cli/cambc login             # interactive, done once by a human (session lasts 7 days); needed for ladder/matches/submit
```
The CLI version must match the platform engine (4.0.0 / engine 2.0.0 on 31 Oct 2026). If `/game/download` lists a newer version, update before evaluating.

**On the FASRC cluster** (from 31 Oct; details in `results/STATUS.md` → "Cluster operating notes"):
- Use `python3.12` for the tools; the system `python3` is 3.6.
- `cli/cambc` and `matches/`/`replays/` are symlinks into holylabs and netscratch.
- Run every eval through `tools/onslurm.sh`. It uses the free `test` partition, the only lane the user allows.
- From 1 Nov the agent runs on a **login node**, where FASRC allows no computation and kills long processes.
  - Run **every** game through `tools/onslurm.sh`, including a single debug game (`tools/onslurm.sh -c 2 -m 2G -t 00:05:00 -J dbg -- ./cli/cambc run A B --map M -o matches/<dir>`).
  - Any script that needs more than about a minute of CPU also goes through `tools/onslurm.sh`.
  - Only editing, git, `sbatch`/`squeue`, `cambc` site commands and quick reads run locally.

## Rules of the road
- **Local games are deterministic:** the same bots on the same map give identical games. Never re-run a map; get evidence from more maps (`--maps all` = 140 games).
- **Strong side bias:** team B wins ~75% of mirror games. Always evaluate both sides, which `tools/eval.py` does by default.
- **Self-play overstates real strength:** v1 beat the starter 100% locally but went 18W-47L on the ladder. Test against imitation opponents of real ladder comps (`imit_test`, `lad_*`, `h3_*`), and treat real ladder results as the ground truth.
- **Run-batch manifests are whitespace-separated and resolve paths relative to the manifest file.** `tools/eval.py` handles this; reuse it.
- **Python fuel is 2.5M per turn.** `fuelExhausted` events mean a suspended turn. Keep them near 0.
- **Never commit** `cli/cambc`, `postmortems/raw/` or `submissions/*.zip` (gitignored). On the dev PC, `git push` needed the Bash sandbox disabled.
- **Submitting:**
  - `./cli/cambc bundle <bot> --output submissions/<bot>.zip`, then `cambc submit <bot> -n "note"` (after login), or upload the zip at /game/submissions.
  - A new upload becomes the selected live version; older versions keep "Make Live" (`cambc submissions activate`).
  - At each tournament deadline the live version is snapshotted, then submissions lock for about an hour.
  - The upload API sometimes returns 503; retry.
