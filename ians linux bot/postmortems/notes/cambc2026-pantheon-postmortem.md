# Cambridge Battlecode Postmortem: Team Pantheon (Grand Finals 1st)

- **URL (PDF):** https://raw.githubusercontent.com/HerbertTheBird/Cambridge-Battlecode/main/postmortem/postmortem.pdf
- **Repo:** https://github.com/HerbertTheBird/Cambridge-Battlecode (bots in `/bots`; `Lethe` was the International Qualifiers bot, `Khaos` the Grand Finals bot)
- **Raw copy:** `../raw/cambc2026-pantheon-postmortem.pdf` and `../raw/cambc2026-pantheon-repo-README.md`
- **Event:** Cambridge Battlecode 2026, the first ("inaugural") Cambridge event, run March to May 2026 on battlecode.cam. Python only, with a wall-clock limit of about 2000 microseconds per unit turn instead of bytecode counting.
- **Team:** Pantheon (Derek Wang, Yufan Wang, Alex Thummalapalli, Ioannis Pantidis). Three of the four were first-time Battlecode players. They merged with "Team Food" partway through.
- **Placement:** **1st at the Grand Finals** (entered as the top seed). Sprints: top 128, then top 8, top 4, top 8, top 4. International Qualifiers: 3rd.
- **Same game as cambc 2026a?** **No.** That game was about builder bots, conveyors, harvesters and turrets (titanium and axionite), and a core you could destroy. The engineering lessons carry over to 2026a: Python performance, bitboards, memoryless scoring, pathfinding, symmetry handling and the dev workflow.

## Game summary
Each team had an immobile 3x3 core that spawned builder bots. Builders walked only on roads or walkable buildings, and they built harvesters on ore, routed conveyors and bridges back to the core, and placed turrets (gunner, sentinel, breach, launcher) that needed ammunition fed to them. Games were won by destroying the enemy core, or on a resource tiebreak at round 2000. Maps were 20x20 to 50x50 and symmetric. Vision was local, and the only communication was markers (one u32 marker per unit per turn).

## Strategy
- **Memoryless architecture (the main idea).** Every turn the bot recomputes its decisions from global map knowledge instead of carrying state machines forward. Each builder scores 7 candidate states (attack 9, heal 8, route 7.75, secure 7.5, harvest 4, disrupt 2, explore 1; each number is that state's score ceiling) and runs the highest. Long-term behaviour emerges from these per-turn choices, and stale goals never persist. They credit this with making the bot adaptable and hard to overfit or counter.
- **Score states in descending order of ceiling, and stop early** once the best score found so far is at least the next state's maximum. This avoids paying for scoring states that cannot win. It is cheap and applies directly to our champion job selection (fight, bank, capture, farm, retreat).
- **Small persistent exceptions:** TTL caches (about 100 rounds) for targets that failed recently, so the bot doesn't keep retrying them, and special roles for the first few units (one guard stays near the core, four explorers go in spread-out directions).
- **Emergent territorial tactics:** "ore hopping" pushes the frontier from owned resources, and "seeding" breaks an enemy supply line and drops a turret in the gap.
- **Late aggression paid off.** An "attack route" that extends infrastructure toward the enemy was usually a net win even when it never reached the core, because of the disruption it caused. It was merged hours before the deadline.

## Micro / combat
- **Coordinated one-shots.** Turrets wait so that two of them fire on the same turn and kill a target before enemy builders can heal it. Only the unit that acts later (higher id) waits, because units act in id order. The 2026a equivalent: when several champions can burst a target, fire in priority/draft order so damage lands before a recall or heal, and use `set_priority`, which takes effect the next round.
- **Target priority tiers:** first the things that feed enemy damage, then threats to our assets, then units, then everything else. Tiebreaks: the highest-HP target we can one-shot, then the one furthest from enemy healers, then type weight, then lowest HP.
- Don't hit targets the enemy can heal unless we locally outnumber them, have overwhelming damage, or the target is sealed off.
- **Displacement control:** launchers at chokepoints throw enemies back to where they stood a few turns ago, which wastes their walking time. The 2026a parallel is stuns that interrupt recall or tribute channels, and body-blocking.

## Macro / economy
- A cost-aware build decision: start an expensive project only if a closed-form cost estimate is affordable, with a deliberate discount so the bot isn't too conservative.
- Spawn policy keyed to resource thresholds that scale with unit count. Reserve resources for the tiebreak late in the game (they stopped converting axionite after round 1500 because axionite was tiebreak #1). **2026a parallel:** lifetime gold earned is tiebreak #2, so late-game gold farming has value even when gems are level.
- Deny the enemy economy cheaply once you are rich (barriers on enemy-side ore). The 2026a parallel is standing on enemy-side camp spawn tiles to block respawns, and altar locks.

## Pathfinding
- **Bitboard Dial's algorithm (bucketed Dijkstra)** on Python big integers, using a circular array of frontier bitmasks. It runs in reverse, from the target to the start, so no path reconstruction is needed: you just step to the neighbouring tile with the lowest distance. Edge classes have different costs (normal 1, stepping through a soft threat 20, and so on). Hard threats are never entered. Soft threats are allowed at a higher cost.
- Other units are not treated as obstacles during the search, which prevents oscillation. Occupancy is checked only when choosing this turn's step.
- Tie-breaks among equal moves favour vision (diagonals and zigzags), staying off map edges, and not clumping with allies.
- **Unweighted BFS for "closest X"** queries, which is much faster than Dijkstra. It also has an "enemy point of view" mode for "can they reach it before us?"
- **Voronoi claim partition:** competing simultaneous flood fills from me and from every ally, keeping only the targets I reach first. This stops units from duplicating a job without any communication. It is very applicable to 2026a camp claims, given we have only 8 bytes of shared memory.
- Stuck detection: if there has been no progress for 2 + (id mod 8) turns, take a random step. The id term de-synchronises units.
- Chokepoint detection with a pure-Python Voronoi / medial-axis pipeline that runs **incrementally across turns** as a resumable job with a budget check, and is cached until the wall map changes.

## Communication / shared memory
- Markers carried packed bitfields XOR-ed with a key so other teams couldn't read them from replays.
- **Symmetry broadcast:** units share which symmetries (horizontal, vertical, rotational) have been ruled out, plus compressed terrain samples (5x5 buckets, a 7-bit bucket id and 21 tile bits). Communication was supplementary: no unit depended on it.
- The spawning core told new units their explore direction implicitly, through which tile it spawned them on, at zero communication cost. For 2026a, draft memory (1024 bytes, read-only during play) can hold precomputed plans such as camp-group tables, assignments and distance hints.

## Compute / fuel / bytecode optimisation (Python)
- **Bitboards in Python big integers** (bit n = x + y*W): wall/seen/threat/placement masks combined with C-level bitwise operations. Shifts by 1 and by W translate whole masks. Iterate set bits with the `mask & -mask` lowest-bit idiom, so cost scales with the number of set bits rather than the map area. Note that 2026a maps go up to 100x100 = 10,000 bits, which still works fine.
- **Bit-sliced score planes:** add a constant to the score of every tile in a mask with O(number of planes) big-integer operations, and threshold the whole board in one most-significant-bit-first pass. Cost is independent of how many tiles are scored.
- **Memoize derived masks** on a "structural version" counter that is bumped only when walls or buildings change.
- **Incremental vision updates:** after a move, diff the old and new vision masks and update only the newly seen tiles. Skip walls early, because they never change.
- **Bind hot attributes and methods to locals** before inner loops. **Convert enums to integer indices** once at import and use list lookups instead of dict or frozenset hashing of enums.
- Profile with a per-function self-time table. Their top costs were all map-info and pathfinding, and the biggest single item was the per-tile update.
- A debug `log` bound once at import to a no-op when a flag is off, so log calls cost almost nothing in submissions.
- **Spread expensive analysis over many turns** (resumable job plus budget check). This maps directly onto 2026a fuel: an out-of-fuel bot is *suspended mid-code*, so add a fuel check and save state between phases.

## Testing & dev workflow
- Many named bot versions (Artemis, Demeter, Lethe, Hades, Khaos and sub-versions), with old versions kept as sparring partners. Weekly sprints were used to read the meta.
- They hit a plateau from over-complicated code and did a **full rewrite**, keeping only the map-info and pathfinding modules. The rewrite (Lethe) was what first beat top teams.
- They wrote an Elo progression over time and published their tooling in the repo.

## Meta insights
- Their memoryless approach differs from the usual persistent state machines, and they believe it was a main reason they won.
- Other teams cluttering the map (road spam) broke their earlier marker-based coordination, so they moved coordination to channels that couldn't be disrupted.

## Mistakes / regrets
- A merged, over-complicated codebase caused a plateau and forced a rewrite.
- Marker-based task claiming was fragile and was retired in favour of implicit Voronoi claims.
- They were still adding major features hours before the final deadline. It worked out for them, but it carried risk.

## Transfer to our 2026a bot (Python, 2.5M fuel per turn)
1. Recompute each champion's job from scratch every turn with ceiling-ordered scoring, keeping only small TTL "recently failed" caches.
2. Use big-integer bitboards for walls, bushes, holes, threat zones (camp attack ranges 3 to 5, enemy champion reach) and danger. Use them for flood fills, BFS and Dial's algorithm.
3. Use a Voronoi claim partition for camp groups and altars, so we don't spend shared-memory bytes on claims.
4. Make expensive planning (all-pairs distances, symmetry) a resumable job, and use the first draft turn's 100x fuel to precompute into draft memory.
5. Time burst so that a carrier dies before it can recall or tribute; act in priority order.
