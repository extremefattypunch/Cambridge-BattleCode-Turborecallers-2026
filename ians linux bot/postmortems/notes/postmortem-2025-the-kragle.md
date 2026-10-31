# The Kragle - Battlecode 25 Postmortem

- **URL:** https://battlecode.org/assets/files/postmortem-2025-the-kragle.pdf
- **Raw:** ../raw/postmortem-2025-the-kragle.pdf
- **Event:** MIT Battlecode 2025 (paint-coverage game)
- **Team / placement:** The Kragle (Justin Ottesen, Andrew Bank, Matt Voynovich; RPI). Rated around 1800, about 27th overall, and the 10th-ranked US university team. They **narrowly missed Finals**, losing two 2-3 sets in the US Qualifiers. This is not a finalist, but it is included for its "how top teams structure bots" advice and its notes on the XSquare micro framework.
- **Same game as cambc 2026a?** No

## Game summary
Same 2025 paint game as JWU, confused and Om Nom.

## Lessons

### Strategy
- **Opening theory:** each tower can afford two opening units, and a **paired opening** (2 soldiers together) captured an uncontested ruin in about 12 turns. They took a ruin before turn ~20 on 90% of test maps. If only contested ruins were found, the pair rushed. Downside: pairing increased variance, since the pair sometimes missed an obvious ruin because they didn't spread out.
- Their opening often gave them a lead, then they **threw it** through floating resources and idle units (below).

### Macro / economy
- **Floating resources:** dozens of towers each held a little unusable paint below the spawn threshold. On paper they led, but in practice they could not spend it. The fix was for refilling units to leave exactly what a tower needs to build.
- **Idle time:** half of each unit's life went to walking back to refill and queueing. Other teams simply didn't refill: a cheap unit is cheaper to replace than to service, and only high-value units should be preserved. They found this late, by watching others.
- **Battlefront comms:** even rough "where is the front" info greatly reduced idle exploration.

### Pathfinding / map representation
- MapData: one 32-bit int per tile with packed fields (terrain, paint, goal colour, etc.). On a move, only the newly visible tiles are updated; a full rescan is too expensive. Known ruins are re-checked each turn to cover the blind spot.
- A "simulate greedy on the internal map, then simulate bug past obstacles, with a checkpoint stack" pathfinder was too expensive and buggy and was scrapped for classic bugnav. (Om Nom's "bug target + BFS" is the version that works.)

### Decision-making framework (their advice)
- **Goal priority queue:** each goal has a type and a location. Each goal type implements `shouldStart`, `execute` and `shouldStop`. A goal stack/queue stops units forgetting a task when interrupted (a refill, a fight). This fixed ruins being abandoned after a refill trip.
- Separate queues for actions that can run concurrently (for example attack and spawn).

### Micro / combat (their explanation of XSquare micro)
- (a) `doMicro` trigger: enemies are visible, or recently remembered nearby, or HP is low.
- (b) `computeMicroArray`: one MicroInfo per each of the 9 move options.
- (c) MicroInfo holds features such as the number of enemies that can hit the tile, the distance to the closest enemy, and whether it is in range to attack. `isBetterThan` compares two infos lexicographically.
- Attack target choice is kept separate and simple: the lowest-HP enemy in range, attacked whenever possible.
- Typical micro moves: weave in and out of range, split groups against AoE, kite, and push when you have local superiority.

### Compute / bytecode
- Understand the cost model before choosing algorithms (for example, A* is probably infeasible). BFS on even a 20x20 window can eat a whole turn's budget unless unrolled.

### Testing & dev workflow
- Advice:
  - Prepare before the season (code skeleton, map representation, symmetry, bugnav).
  - Budget time toward the best effort-to-result tasks.
  - Prioritise economy, because games snowball and finals maps tend to be larger and slower.
  - Copy what beats you.
  - **Make custom maps that expose your problems.**
  - Keep old versions and test against them; never upload an untested bot right before a deadline.
  - Use a sane git branching workflow.

### Mistakes / regrets
- Time sunk into rewriting proven pathfinding and into a never-decisive survival behaviour.
- Messy goal resolution (if-chains).
- Ignoring other teams' strategies left obvious gaps: they still refilled when others didn't, had a weak build order, and didn't hunt enemy towers.

## Transfer to cambc 2026a
- Goal queue per champion (farm camp X, capture, tribute, recall, shop, defend altar), with explicit start and stop predicates.
- Don't "float" resources. Spend gold on shards promptly, since gold on hand gives no stats, and tribute gems before they are at risk.
- Decide when a trip home (recall or shop) is worth the idle time compared with staying productive.
- Opening theory matters: choose 1-2 opening camps per champion, and gem or gold clusters early (120 HP, about 3 hits) for cheap value.
