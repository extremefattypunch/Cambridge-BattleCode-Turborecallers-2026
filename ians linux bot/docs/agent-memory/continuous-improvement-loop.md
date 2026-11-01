---
name: continuous-improvement-loop
description: "Standing rule for the Battlecode project — run local sims, monitor the ladder and submit validated bots continuously (24/7)"
metadata:
  node_type: memory
  type: feedback
  originSessionId: 011a374b-9717-46be-b823-39c7b5bbdb2a
  modified: 2026-10-31T22:32:56.380Z
---

At all times keep the improvement loop going. **Every simulated match must test a new, meaningful, distinct strategy** (from ladder-match research, our own bots or postmortems). Never simulate just to simulate; no idle soak runs. **Every experiment ends in a detailed analysis session** (tools/analyze_match.py: gem race, tempo, deaths/killers, per-champion lines, replay stdout), a written report in results/experiments/, and new hypotheses fed back into STRATEGIES.md. The user calls this the critical learning process. Submit the strongest bot found. Keep these running in parallel:
- strategy experiments of our own: one candidate bot per hypothesis from `results/STRATEGIES.md`, with verdicts recorded;
- monitoring of the leaderboard and our ladder matches on https://2026a.battlecode.co.uk;
- submitting improved bots to the site ahead of every tournament or qualifier deadline.

**Why:** the user (31 Oct 2026) wants the bot to improve 24/7 without waiting for prompts. They pre-authorised submitting validated improvements. Real-ladder results matter more than self-play, which overstated v1 badly.

**How to apply:**
- Follow `ians linux bot/LOOP.md` on each tick. On 31 Oct the work moved to the user's cluster agent; any session must re-create its own scheduler (CronCreate is session-only).
- Always keep a **ready-to-submit best bot**:
  - `results/CHAMPION`, `submissions/READY.zip` and `results/READY.md`;
  - watch for candidates: anything ≥55% vs the champion on sprint goes straight to the full gate;
  - upload promoted bots right away, so the live bot is always the best one.
- A submission must be **certain** to outperform the old bot (user, 31 Oct). Gate:
  - all-maps head-to-head with a 95% Wilson lower bound above 50% (≥82/140);
  - a paired gauntlet ≥ the champion's;
  - release clean;
  - the analysis confirms the mechanism.

  Never ship 55% near-misses, and never upload untested last-minute candidates (they declined h_earlyfight at 57.5% before the Sprint 3 lock).
- Commit and push each promotion ([[commit-push-progress]]).
- Python is the main line. A C++ port runs as a parallel track, and we switch only if C++ wins head-to-head. The user asked for C++, but measurements showed no fuel advantage: the C++ starter uses 19× less fuel per turn on a 25× smaller budget.

See [[cambc-battlecode-project]].
