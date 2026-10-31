# Java Best Waifu (XSquare) - Battlecode 2020 Postmortem

- **URL:** https://battlecode.org/assets/files/postmortem-2020-java-best-waifu.pdf
- **Raw:** ../raw/postmortem-2020-java-best-waifu.pdf
- **Event:** MIT Battlecode 2020 ("Soup": a flooding map, landscapers, drones). This is older than the 2022-2026 window, but it is a champion's writeup by XSquare, whose micro and bugnav code later teams copied.
- **Team / placement:** Java Best Waifu (Ivan Geffner "XSquare" and Daniel Hopping). **1st place, Final Tournament 2020.** XSquare also placed 3rd in 2017 and 4th in 2018.
- **Same game as cambc 2026a?** No

## Game summary
Water slowly floods the map and you lose when your HQ is flooded or buried. Miners gather soup, landscapers dig and deposit dirt (to raise terrain or bury buildings), and drones carry units (they can drop enemies into water). Vaporators give passive income, and net guns shoot drones. Pollution from cows reduces vision.

## Lessons

### Strategy
- Build the **strategy-independent primitives first**: gathering, navigation (bugnav), comms and an easily modifiable build order. They are needed whatever the meta turns out to be.
- **Copy the best idea from the sprint, then add a win condition.** They adopted the sprint winners' "lattice" economy, then added a drone "crunch": mass units at a scheduled round and overwhelm the enemy at once, so the defence can't kill them fast enough.
- **Timed all-in attacks** at fixed rounds (1500, with a second wave at 2200) after building a big economy. They stopped respecting danger maps near the end, when the crunch had to land.
- A **RushManager** switched production when it detected being rushed, with explicit counter-build rules (for example, spawn a counter-unit for each enemy unit; only build drones when the enemy recently spent resources and so can't afford a net gun).
- Their bot did well against both dominant metas (rush and turtle). Being robust to the common strategies matters more than beating one.

### Micro / combat
- **Danger map:** each reported net gun adds +1 to every cell within its range in a map-sized array, and -1 when it is reported destroyed. Drones treat positive cells as walls. This is cheap incremental threat avoidance shared through comms.
- Drones circle the enemy HQ outside gun range, trap enemy workers inside, and pick off strays.

### Macro / economy
- **"Desperation index":** count the turns you have wanted to build something and could afford it. Relax the placement constraints as the index grows (an ideal tile first; after 8 turns a decent tile; after 30 anywhere). This simple anti-stall rule is broadly reusable.
- A prioritised task list per worker (fix flooding inside the wall first, then raise the wall, ...) made behaviour robust on weird maps.
- Fixed production ratios that change at round thresholds.

### Pathfinding
- Bugnav for the whole tournament.

### Communication
- The HQ broadcast its location plus a bitmask of which visible tiles were "interior", so every unit could reconstruct the base layout exactly from one compact message. **Send compact seeds that every unit can expand deterministically.**
- Units broadcast newly seen threats and their destruction.
- Comms in that game were public and could be spoofed. One opponent replayed their old messages. That is not an issue in cambc, where shared memory is invisible to the opponent.

### Compute / bytecode
- Iterate over visible tiles by **walking a precomputed direction sequence** (`loc.add(dir)` costs ~2-3 bytecode) instead of building new coordinates from offset arrays (~15 each). This saved more than 2000 bytecode per turn.
- The HQ used spare compute at the end of its early turns to precompute the wall layout by BFS. **Spread heavy precomputation over idle turns.**

### Testing & dev workflow
- They played no scrims before the Sprint, sent an incomplete bot and lost round 1, but used the sprint to study the best bots.
- Advice: **simplicity, robustness and structured code**. Sophisticated coordination usually flops because everything that can go wrong does. If the strategy changes drastically, rewrite from scratch; it is faster than expected.

### Mistakes / regrets
- Wall-building was less consistent than believed and drowned early on some maps. Bracket luck (avoiding bad matchups) helped.

## Transfer to cambc 2026a
- Primitives first: movement masks and pathing, camp-fight routine, capture, tribute, recall and shop. Then strategy.
- A danger map (camp aggro ranges plus last-seen enemy champion threat) maintained incrementally, used as soft walls by the pather.
- A desperation index or timeout for any waiting behaviour (waiting for a camp respawn, waiting for an ally, contested captures).
- Scheduled pushes, e.g. a team-wide fight or a Monolith attempt timed at a round when all champions are itemised. Can be coordinated through draft memory and the round number alone, with zero shared memory.
- Use the 100x-fuel draft turn as XSquare used idle HQ turns: precompute map analysis (camp list, altar distances, choke points) into the 1024-byte draft memory.
