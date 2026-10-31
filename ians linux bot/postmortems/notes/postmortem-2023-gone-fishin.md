# Gone Fishin' - Battlecode 2023 Strategy Report / Postmortem

- **URL:** https://battlecode.org/assets/files/postmortem-2023-gone-fishin.pdf
- **Raw:** ../raw/postmortem-2023-gone-fishin.pdf
- **Event:** MIT Battlecode 2023 ("Tempest")
- **Team / placement:** Gone Fishin' (Carl Guo, Ray Wang, Yuxuan Chen, Temo Toloraia; MIT and Yale). This was a **first-year team**: top 16 and top 32 in the Sprints, then **1st seed into Finals and 2nd place overall**, losing the final to Producing Perfection. Cout for Clout's 2024 guide refers to a member as being from "Gone Fishin'/Sharkin'", so this team line appears to continue as Gone Sharkin', the 2024 champion. "Gone Whalin'" (2025) is probably related too, but that is unverified.
- **Same game as cambc 2026a?** No

## Game summary
HQs (indestructible) spawn carriers (mine Adamantium and Mana at wells, carry anchors), launchers (the main ranged attackers; they attack every turn but move every 2 turns, and vision is larger than attack range) and amplifiers. Terrain includes clouds (slow you and hide units) and currents (push units). Anchors capture islands, which heal allies, and 75% of islands wins. Tiebreaks were islands, then anchors placed, then resources. There was a 64x16-bit shared array, writable only near an HQ, island or amplifier.

## Lessons

### Strategy
- Resource priority follows the decisive unit. Mana makes launchers, and launcher fights decide games, so they mined almost only Mana on small maps, with the Mana:Adamantium split set by map size.
- Late in the season they switched islands from "army follows the anchor carrier" (it clogged and lost track of the carrier) to **capturing the island slightly closer to their own HQ than the enemy's**. Damaged units fall back to friendly islands, so fights happen where they heal.
- **Map-trend betting** (always take the centre islands) won most normal maps but lost the grand final's unusual map. Over-fitting to the expected map style is a real risk. A randomised or evenly spread choice is more robust.

### Micro / combat (they estimate micro is worth +30-50% win rate, compared with ~5% for macro tweaks)
- **Always kite:** attack, then move to the tile that minimises the number of enemy attackers that can see you. Cache the enemy position so you can step back in and hit. With first move, this gives 3 attacks per 4 turns against the enemy's 2. Situational kiting was tested and "always kite" won.
- Tiebreak: **prefer orthogonal over diagonal moves** at equal distance, which keeps formation (advice credited to Super Cow Powers). Avoid vision-reducing terrain while kiting.
- **Chase rules:** chase out of range only if there is nothing else to hit, the target is not a combat unit, or you outnumber them by 2+.
- **Target priority:** for each enemy, count how many allies can hit it right now, compare with its HP, and **prefer targets you can kill this turn**.
- **Spawn formation:** spawn the first 4 attackers in a square with the earliest-spawned (earliest-acting) furthest out, so the front units move first and the group stays together without comms. This alone won about 2/3 of games against the version without it. Turn order shapes formations.
- **Grouping:** leader-following (lowest ID) caused blocking and was removed. The final version regroups for 10 turns after a fight: go to the visible ally closest to the enemy base with the highest HP. Once adjacent, the lower-HP unit stops behind, so damaged units sit behind healthy ones.
- **Blind attacks:** if an attack is unused at the end of the turn, fire into unseen tiles. Priority order: an enemy reported over comms, then the last-seen enemy location, then a random sample biased toward the enemy base.

### Macro / economy
- **Congestion control:** if an HQ senses crowding and the worker count is high, it raises a shared "congested" flag that halts worker production everywhere. Workers mark wells "full" when all mining tiles are taken, and "dangerous" (temporarily) when enemies are seen there.
- Workers count themselves into a shared counter that resets every 100 turns, and that index assigns their resource type (a deterministic ratio with no central controller).
- When no well is visible, workers search along an outward spiral (r = θ), using the seen-tile memory to skip explored areas.

### Pathfinding
- A* and BFS didn't fit the compute budget for them, and a line-sweep obstacle approach had too many edge cases. They kept bug-nav and refined it:
  - **A stack of turn directions** to escape C-shaped traps.
  - **Simulate both left and right wall-follows** for a few steps and pick the shorter, with compute cutoffs. If neither finishes, pick one, randomly at Finals.
  - Never follow map edges.
  - **Treat friendly units as walls 75% of the time and as empty 25% of the time** (randomness breaks deadlocks).
  - Allow movement terrain (currents) when it pushes roughly toward the target.

### Communication (shared-memory bit budget)
- They budgeted the 64x16-bit array field by field: 12-bit locations, HQs, **3 symmetry-elimination bits**, per-HQ congestion bits, worker counters, the 5 nearest wells per resource, **10 recent enemy sightings (12-bit location plus a 2-bit round stamp for staleness)**, amplifier liveness, and 35 islands with 2-bit status. About 200 of 1024 bits stayed unused.
- **MapRecorder:** 1 byte per tile (seen, passable, well, cloud, plus 4 bits of cached direction), used for symmetry elimination and pathing.
- Symmetry scouting moved from a dedicated scout (which wasted an economy unit) to attackers eliminating symmetries on the fly while marching to the guessed enemy base.

### Compute / bytecode
- Compute cutoffs inside the pathfinding simulation so the turn always ends with a move.
- Small codebase (~2.9k lines). Simplicity won over sophisticated algorithms.

### Testing & dev workflow
- They tuned micro hyperparameters by playing against older versions "a million times". Micro changes are hard to evaluate by eye.
- They started with the simplest viable ideas (one resource, rush, assumed symmetry, simple bug) and still reached the Sprint 1 top 16. The assumed-symmetry shortcut backfired in Sprint 1, and they fixed it immediately.
- They reviewed the lost final maps right afterwards: one loss came from a scouting spiral that found distant wells late, the other from the centre-island bet.

### Mistakes / regrets
- Hard-coded symmetry, the leader-follow grouping, and complex pathfinding attempts were all wasted time.
- Over-specialisation to expected map trends cost them the title.

## Transfer to cambc 2026a
- Turn order matters. Within a team, higher priority acts first, then draft order, and the starting team alternates each round. Set `set_priority` so the front-liner moves or initiates first and casters follow. Exploit having first move by attacking and stepping out of range.
- Kill-this-turn target priority: sum the ally damage available now and focus the enemy (or camp) that dies this turn. A kill steals the gems (enemy) or completes the camp group.
- Enemy sighting format for 8-byte shared memory: 7+7 bits of coordinates plus 2 bits of round stamp = 16 bits per sighting, so 2 sightings plus 32 bits for symmetry, camp claims and flags.
- Pathing: bug with a direction stack and left/right simulation, or BFS. Treat allies as walls only probabilistically to avoid deadlock. Fall back on a bounded compute budget.
- Don't over-fit to one map style. Randomise or spread objective choices (which camps and which altar).
