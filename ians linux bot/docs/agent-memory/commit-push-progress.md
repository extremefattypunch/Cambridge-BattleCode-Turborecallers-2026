---
name: commit-push-progress
description: "In the Battlecode repo, commit and push at each milestone so teammates can follow progress"
metadata:
  node_type: memory
  type: feedback
  originSessionId: 011a374b-9717-46be-b823-39c7b5bbdb2a
  modified: 2026-10-31T19:13:37.591Z
---

Commit and push as work progresses in the Cambridge-BattleCode-Turborecallers-2026 repo (remote github.com/extremefattypunch/...), without waiting to be asked each time.

**Why:** the user's teammates follow progress on GitHub.
**How to apply:** work on branch `ians-linux-bot` (created 2026-10-31 because main is the default branch); push after each milestone (new bot version, eval results, submission). The Bash sandbox can't reach github.com — `git push` needs the sandbox disabled. Never commit `cli/cambc` (99 MB) or `postmortems/raw/` (third-party copies); both are gitignored. See [[cambc-battlecode-project]].
