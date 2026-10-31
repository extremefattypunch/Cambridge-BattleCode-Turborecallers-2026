# confused (skipiano) - Battlecode 2025 Postmortem

- **URL:** https://battlecode.org/assets/files/postmortem-2025-confused.pdf
- **Raw:** ../raw/postmortem-2025-confused.pdf
- **Event:** MIT Battlecode 2025 (paint-coverage game)
- **Team / placement:** confused (Michael Hahn, a solo competitor from Waterloo). Joined after Sprint 1, held **#1 on the scrimmage ladder** going into the Qualifiers, and was the 1st seed at Finals. **2nd place overall**: unbeaten through the winners' bracket, then lost the grand final 2-3 in a deciding game 5 to Just Woke Up.
- **Same game as cambc 2026a?** No

## Game summary
Same game as Just Woke Up 2025: paint towers, money towers and defense towers; soldiers, moppers and splashers; tower and SRP patterns; a 70% paint win condition; local paint-connected comms.

## Lessons

### Strategy ("game philosophy" from replay analysis)
- After a balance patch killed his rush (starting towers got more HP), he **re-derived the core objective from replays** and aligned the whole bot with two principles:
  1. **Towers are the top priority** for economy and map control.
  2. **Minimise unit idle time.**
- Concrete consequences: no paint wasted under yourself before round 150. Painting your own tile costs 5 and saves 1 per turn, so it is a net loss early. Stay aggressive, because it either kills enemy towers or forces costly defensive spawns. Delay SRPs until 6+ towers, since SRPs scale with tower count and take 50 rounds to pay. Build money towers first and balance them later.
- **Tower flickering**, copied from Gone Whalin at Finals: deliberately destroy and rebuild your own money tower to turn surplus money into paint. It turned surplus into the scarce resource and made the bot robust to losing its paint tower. The result was a 70%+ win rate against his own Qualifiers bot.
- **Ruin tainting**, copied from Asteroid: one paint dot on a ruin blocks the enemy from building there without a cleaner.

### Micro / combat
- Splasher: score a 7x7 window, weighting enemy paint far above empty and boosting tiles near ruins. Splash only if the 3x3 value beats the attack's paint cost. Hold the resource for high-value moments.
- Splashers also poke towers from just outside their range, so they deal damage without taking any.

### Macro / economy
- **Idle timer:** a unit inactive for too long is redirected to the opposite side of the map centre. A default bias toward predicted enemy structures (by symmetry), plus randomness, eventually explores everything.
- Tower marks double as memory: when a marked tower is destroyed, it is rebuilt as a defense tower, but only if enemies are still around (he had been overbuilding them).

### Pathfinding
- Adapted camel_case's 2024 approach: **unrolled Bellman-Ford over the vision window, falling back to bugnav after 3 turns without progress**. Weights favour friendly terrain and avoid hostile terrain.
- He warns against blindly copying pathfinding you cannot modify. He needed to retune the weights for this game.

### Communication
- Comms were so restricted that most top teams, including him, barely used them by the end. The early comms work still clarified what information to keep locally each turn.

### Compute / bytecode
- **Symmetry checking:** assume rotational symmetry by default and head for the map centre, which is the best place to break the symmetry and is close to likely enemy structures. To save bytecode, only compare cells on the far side of each candidate symmetry line or quadrant, and keep a set of already-checked cells.
- He did essentially no bytecode optimisation, and says simple, well-aimed features beat clever algorithms.

### Testing & dev workflow
- Fast start by reusing his own old code plus camel_case's public 2024 framework (one class per unit).
- Extensive **replay analysis of top teams** (Old But Gold, subscribe to caterpillow, Asteroid, Gone Whalin) was his main source of strategy.
- Scrims against the other top teams hovered around 50%. The finals were coin flips decided by map features.

### Meta insights
- Watch other brackets (e.g. the US Qualifiers) for new strategies to copy before Finals.

### Mistakes / regrets
- His exploration was biased toward the centre and missed corner objectives. He lost the deciding final game on a large map with low ruin density and many ruins in the corners. Exploration bias can lose games on adversarial maps.

## Transfer to cambc 2026a
- Write down 2-3 "philosophy" rules from replays (for example: tributed gems are what score, an idle champion is wasted, protect carried gems). Make every feature serve them.
- Spend only when value exceeds cost (for example: only fight or cast when expected damage or gems beat the risk).
- Use symmetry (the map is symmetric) to predict enemy spawn, altars and camps from turn 1. The full map is even visible during the draft.
- Idle timers and anti-stuck rules for champions.
- Make sure exploration and farming cover corner camps as well as the centre.
