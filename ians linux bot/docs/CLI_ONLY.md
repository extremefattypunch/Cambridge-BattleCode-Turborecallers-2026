# Working without a browser (CLI-only agents)

Facts about the cambc tooling for an agent that has a shell but no browser. How and where it runs is up to that environment.

| Task | CLI route |
|---|---|
| Local matches, evals, gauntlets | `tools/eval.py`, `tools/tournament.py`, `tools/gauntlet.py`, `cambc run` / `run-batch` |
| Map pool refresh | `cambc maps pull` |
| Real opponents | `cambc match-groups create` queues 5 unranked matches against other teams. It **uses the team's shared website quota** (check with `match-groups quota`). `match-groups download` fetches them. `cambc matches` lists and downloads our ladder matches. Needs `cambc login` |
| Ladder | `cambc ladder` (needs login) |
| Submitting | `cambc submit <bot> -n "note"`, plus `cambc submissions list` / `activate <vN\|latest>`. Needs login and **user approval** |
| Announcements, patch notes, eligibility | No CLI route. Ask the user |

- `cambc login` is interactive, the session lasts 7 days, and it is untested so far. A human runs it once.
- Setup commands are in the repo-root `CLAUDE.md`.
- `claude-settings.example.json` (in this folder) is an **optional** starting permission allowlist for an unattended Claude Code agent:
  - It allows only the exact harness scripts (`tools/{eval,tournament,gauntlet,newbot}.py`, `match_metrics.py`), `cambc run/build/bundle/maps`, edits under `bots/` and `results/` and to `HANDOFF.md`, and exact git forms.
  - It denies edits to `tools/`, `postmortems/`, `.git/`, `.claude/` and `cli/`, so allowed scripts can't be rewritten and then run without a prompt. It also denies `cambc submit/submissions/login/match-groups create`, force-pushes, and git `--output`/`--ext-diff`/`-c`.
  - Adapt it as needed and check with `/permissions`.
