# Running the bot-improvement agent on a cluster (CLI only, no browser)

Written 31 Oct 2026. **Nothing here has been tested on a cluster yet.** Expect some debugging, and record what you learn in this file.

## What does and doesn't need a browser
| Task | CLI route |
|---|---|
| Local matches, evals, gauntlets | `tools/eval.py`, `tools/tournament.py`, `tools/gauntlet.py` (pure CLI) |
| Map pool refresh | `cambc maps pull` (network) |
| Real opponents | `cambc match-groups create` queues 5 unranked matches vs other teams (**uses the team's shared website quota**, so check `match-groups quota` and be frugal), and `match-groups download` fetches them. `cambc matches` lists and downloads our matches. `cambc ladder` shows the ladder. **All need `cambc login`** |
| Submitting | `cambc submit <bot> -n "note"`, plus `cambc submissions list` and `cambc submissions activate <vN|latest>` to switch the live version. Needs login and **user approval** |
| Announcements, patch notes, eligibility | Not available via CLI. Ask the user to check the site |

`cambc login` is interactive (the session lasts 7 days) and has **not been tried yet**. A human should run it once on the machine that will use it. If it shows a URL or code, finish it in a browser on any device.

## One-time setup (on a login node with internet)
```bash
git clone https://github.com/extremefattypunch/Cambridge-BattleCode-Turborecallers-2026.git
cd Cambridge-BattleCode-Turborecallers-2026 && git checkout ians-linux-bot
cd "ians linux bot"
curl -L -o cli/cambc https://2026a.battlecode.co.uk/api/v1/distribution/linux-x64/download && chmod +x cli/cambc
./cli/cambc --version           # must match /game/download (4.0.0 on 31 Oct)
./cli/cambc init --yes .        # fetches toolchains into ~/.cache/cambc, refreshes sdk/ and maps/
git status                      # init must not have changed bots/; review any sdk/ diff
python3 tools/eval.py sf_base starter-python --maps 00anvil --one-side --jobs 1   # smoke test
```

Notes:
- If compute nodes have no internet, run `init` and `maps pull` on the login node. `~/.cache/cambc` and the workspace must be on a shared filesystem.
- The binary is a dynamically linked x86-64 ELF (glibc). On an ARM cluster, download `linux-arm64` instead.
- Python 3 is needed only for the harness scripts; the bots themselves run inside the engine's WASM Python.

## Throughput
- On the 16-core dev box, one 2000-round Python game used about 1.5–2 cores for 10–20 s.
- A 24-game eval with `--jobs 6` took about 50 s.
- Rule of thumb: `--jobs` ≈ cores / 2 on a dedicated node.
- Unlike `eval.py`, `run-batch` accepts `--timeout <secs>` per match; add it if a node is oversubscribed.

## Unattended agent
- **Permissions:** an overnight agent stalls on permission prompts.
  - `claude-settings.example.json` is a starting allowlist. It runs the harness, `cambc run/maps/matches`, and git add/commit/push to `ians-linux-bot`.
  - It **denies** `cambc submit/submissions/login` and force-pushes, so the agent cannot change the team's live bot.
  - Copy it to `.claude/settings.local.json` at the repo root (personal, gitignore it) or to `.claude/settings.json` (shared with teammates).
  - Check the result with `/permissions`.
  - Path rules involving the `ians linux bot` folder (spaces) are untested; that's why the allowlist uses Bash patterns relative to the workspace.
- **Running it:** run the agent inside `tmux` or `screen` on a node where long processes are allowed, or as a batch job if your cluster permits interactive agents in jobs. Point it at `HANDOFF.md` §6 (overnight protocol) and give it a stop time.
- **Results** persist in git via `results/gauntlet.jsonl`, `results/CHAMPION` and commits on `ians-linux-bot`, so a teammate can review progress from GitHub.
