# CoffeeCoder1015/cambridge-battlecode: ideas repo (peak 9th of 587)

- **URL:** https://github.com/CoffeeCoder1015/cambridge-battlecode
- **Raw copy:** `../raw/cambc2026-coffeecoder-README.md`
- **Event:** Cambridge Battlecode 2026 (the spring 2026 conveyor/builder game, Python, about 2 ms per move)
- **Team / placement:** The repo description says the team finished around 70th of 587 with a **peak of 9th** on the ladder. The README is a curated "highlights" writeup that links to the implementations.
- **Same game as cambc 2026a?** **No**, but the algorithmic ideas transfer.

## Game summary
This was the builder/conveyor/core game (see the Pantheon notes). Builders explore, build harvesters and supply lines, find the enemy core by symmetry, and fight over infrastructure.

## Lessons
### Pathfinding / compute
- **Bucketed A\*.** On an 8-connected grid with uniform step costs, heuristics are integers, so a min-heap can be replaced by an array of buckets. This removes the heap overhead that dominated runtime under a tight per-move budget. For 2026a (Chebyshev moves, uniform cost), BFS or bucketed A\* beats heapq-based A\* in Python fuel.
- **Bug navigation (tangent bug) as a cheap fallback** when the known map is too incomplete for a global search. It uses trail memory and recovery to avoid loops. Useful for unexplored map regions in 2026a, where vision is per-champion with shadowcasting.
- **Frontier exploration.** Generate new targets from reached positions, rank them by distance and age, and penalise inaccessible ones. This produces spiral-like coverage with fewer repeat visits.

### Strategy / macro
- **Hijack rather than destroy.** Their supply system didn't check ownership, so they redirected enemy production into their own line. The 2026a analogue is to look for rules that don't distinguish ownership. For example, standing on a cleared camp's spawn tile blocks that group's respawn whichever team is there, so we can delay enemy farm on their side.
- **Adaptive spending.** A rolling income estimate drives reinvestment, and a dynamic reserve rises during starvation and falls during surplus. This beats fixed spawn or shop timings. For 2026a, gold has no passive income, so shop decisions could use expected gold-per-round.
- **Resumable multi-turn plans.** Record the phase of long constructions so they survive cooldowns and interruptions. For 2026a, recall, tribute and teleport are multi-turn channels, and capture takes 5 rounds. Keep a small per-champion plan state across turns, or re-derive it cheaply from the world.

### Communication
- **Symmetry elimination.** Every mirrored-terrain mismatch rules out horizontal, vertical or rotational symmetry. Three marker bits are enough to share which symmetries have been rejected. In 2026a the whole map is visible during the draft, so symmetry can be computed once with draft fuel and stored in draft memory.

### Testing & dev workflow
- They kept `stable-bots` snapshots plus `starter` and `do_nothing` baselines, ran many parallel experiment directories, and used `cambc run A B` for head-to-head games.

### Regrets / notes
- Several directory names were historical (`q_learning`, `k_learning`) and contained no actual RL. Many experiments existed side by side and not all were active at once, which suggests a scattered codebase.
