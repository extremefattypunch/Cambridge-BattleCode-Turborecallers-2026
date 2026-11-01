---
name: cambc-battlecode-project
description: "Cambridge Battlecode 2026a (cambc) — team Turbo Recallers, Python bots in \"ians linux bot\", Sprint 3 outcome, handoff docs, submission flow"
metadata:
  node_type: memory
  type: project
  originSessionId: 011a374b-9717-46be-b823-39c7b5bbdb2a
  modified: 2026-10-31T21:46:10.097Z
---

User (site account dope.amine2, team "Turbo Recallers") competes in Cambridge Battlecode 2026a (https://2026a.battlecode.co.uk). Sprint 3 locked Sat 31 Oct 2026 23:59 GMT. Our Sprint 3 entry is website v2 = `tb_merge_b` (uploaded 21:42 UTC; v1 = tb_splitfarm was the interim). Next: International qualifiers 4 Nov, UK qualifiers 11 Nov, finals 18 Nov. Tournaments use unseen maps.

State lives IN THE REPO (branch `ians-linux-bot`). **31 Oct ~20:10 EDT: the user moved all ongoing work to a cluster Claude agent** (CLI-only, no browser): the improvement loop, experiments, ladder tracking, research and the C++ track. Handoff: repo-root CLAUDE.md (standing instructions) → results/STATUS.md 'Resume here' → LOOP.md. Ladder watching from the dev PC used the site API: Ladder watching via the site API is part of the loop: `/api/v1/match-groups?scope=team`, `/api/v1/match-groups/<id>` (per-game map, drafts, scores, replayUrl), `/api/v1/submissions`; fetch from the logged-in page. Replay bundles at `/api/v1/matches/<id>/bundle` are async (poll `pollUrl`); downloading them was flaky. Read:
- repo-root `CLAUDE.md`
- `ians linux bot/HANDOFF.md` (lineage, results, prioritised next steps, overnight protocol)
- `results/CHAMPION` (= tb_merge_b) and `results/gauntlet.jsonl`
- `docs/CLI_ONLY.md`
- skills in `ians linux bot/.claude/skills/`
- `postmortems/INSIGHTS.md`

**Why:** the user wants submissions by each deadline, learning from real ladder matches (local self-play overstated v1: 100% vs starter locally, 18W-47L on the ladder; v2 tb_merge_b started 13W-2L), and progress committed for teammates.
**How to apply:**
- Read HANDOFF.md first.
- Submit via the website zip upload or `cambc submit` (needs `cambc login`, untested). The site and GitHub were intermittently unreachable on 31 Oct; retries worked.
- Uploads that pass the LOOP.md certainty gate are pre-authorised. Get the user's OK for any other account change.

See [[cambc-site-notes]] and [[commit-push-progress]].
