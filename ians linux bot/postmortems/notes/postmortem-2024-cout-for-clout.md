# Cout for Clout - Battlecode 2024 Strategy Guide

- **URL:** https://battlecode.org/assets/files/postmortem-2024-cout-for-clout.pdf
- **Raw:** ../raw/postmortem-2024-cout-for-clout.pdf
- **Code:** https://github.com/ChiMasterBing/battlecode24 (final package `waxingmoon`)
- **Event:** MIT Battlecode 2024 (capture-the-flag "ducks and bread" game)
- **Team / placement:** Cout for Clout (TJHSST high-schoolers: Daniel Qiu, Johnny Liu, Max Wang, David Wei). **1st in the high-school division and 2nd on the final combined leaderboard** (rating above 2000). The overall 2024 champion was Gone Sharkin' (1st) with camel_case 2nd; neither published a postmortem on battlecode.org that I could find.
- **Same game as cambc 2026a?** No

## Game summary
Battlecode 2024: 50 ducks per side, which respawn at spawn zones. Each team must steal the enemy's flags and carry them home. Units level up attack, heal and build through use, and can place traps (explosive, stun, water). There was a shared comms array readable and writable by every unit, and the game was very micro-heavy.

## Lessons

### Strategy
- **Measure the cost of static defenders.** Parking 3 units on the home objective ("sitting duck") meant losing almost every fight. A controlled test of 47 vs 50 units showed the 47-unit side lost about 90% of games. Going all-in on aggression instead gained about 130 rating.
- Instead of parked defenders, they **kept one unit unspawned as an alarm** and used `canSpawn()` on the home pads to detect intruders, then spawned reinforcements exactly when needed. Only one unit was immobilised instead of three.
- **Combat locations:** spawn and send units to where fighting is happening (with the spawn order biased toward the enemy), so units reach fights faster.
- 3 "sniper" units roam the likely enemy objective spots to harass and find undefended targets. A side effect was better scouting and earlier defence alerts.
- They tried copying the top teams' builder-levelling strategy twice and dropped it twice. Only what tests better should survive.

### Micro / combat (the "XSquare is always right" section)
- **Adopt XSquare-style micro:** for each of the 9 move options, compute heuristic stats and pick the best square by comparing them. Their previous if-chain plus combat-BFS micro became unmaintainable. Switching took about 20 minutes (XSquare's 2022 code is public) and moved them from ~1850 to ~1950, and later past 2000.
- Heuristics they layered on top:
  - Bucket behaviour by cooldown state and ranges.
  - Move toward low-HP allies (to protect or heal them) and toward low-HP enemies (to finish them).
  - Move toward stunned allies.
  - Step back if the ally behind you has more HP than you (rotate the front line).
  - Gather at combat locations (Lanchester's square law: concentration wins).
  - Don't over-clump, or you lose movement options.
- **"Chicken" retreat mode:** below an HP threshold that scales with level, avoid enemies and switch to healing.
- **Healer role:** a fixed fraction of units (by ID mod 3) with high heal level prioritise healing and stay behind allies.
- When attack cooldown is nearly ready, it is fine to let the enemy move in and hit you first. You lose no tempo, and stunned enemies get punished.

### Macro / economy
- Trap placement scoring: count the enemies within radius, prefer tiles between the enemy and your flag (fast trigger), and use a + exclusion pattern so traps never double-fire on one unit. The result is layered diagonal trap lines.
- Terrain filling: a checkerboard by default, generalised by counting impassable orthogonal neighbours so it adapts to odd maps.

### Communication
- Built on 4 Musketeers' buffer-pool framework. The shared array has **fixed sections parsed every turn** (ally status, flag states, setup info) plus a **message queue** for rare, varied messages. Writers append; readers track their position. **No slot clearing**, which saves ~75 bytecode per write, and read and write happen in the same turn.
- The queue drives a **squadron system** that summons nearby units to combat locations. A flag being picked up raises a top-priority defend message.
- At game start they communicated each unit's **relative move order**. Enemy flag status and location were kept precise, so units retarget instantly.
- **Flag passing**: the holder hands the objective to an ally nearer home (by Manhattan distance), which doubles carry speed and bypasses friendly-unit congestion. Units that are bug-navigating don't receive passes.

### Compute / bytecode
- Their micro was heavy but ran within budget on the XSquare framework (an array of 9 candidate infos, compared pairwise).

### Testing & dev workflow
- Named packages per milestone (MacroPath, HotlineBling, ..., WaxingMoon), keeping old versions to test against.
- Discovered a defensive hole when a much lower-rated team beat them by sniping flags. **Losses to weak teams expose exploitable holes.**
- Talking to other teams (Chenyx, XSquare) and reading public code gave several key ideas.

### Mistakes / regrets
- Less aggressive micro sometimes got pushed back onto their own spawn, blocking reinforcements, which nearly cost them the HS final.
- Movement cooldown wasn't considered when choosing the flag-pass target.

## Transfer to cambc 2026a
- Use XSquare-style "score each candidate tile" micro for every champion. Feature ideas: expected damage taken from camps and visible enemies, ability to hit a target this turn, distance to allies, HP fraction, standing in a bush, distance to altar or spawn.
- Retreat ("chicken") rule by HP fraction plus recall. Low-HP champions carrying gems should go tribute or recall rather than fight. **Camp kills destroy gems; enemy kills steal them.**
- Concentration (Lanchester): group champions on a camp or fight rather than spreading thin. Rotate damaged front-liners.
- With only 8 bytes of shared memory, use fixed bit-fields (no queue is possible). Encode a combat location or "help" target in about 12-14 bits, as in JWU's 3-bit type plus 12-bit coordinate idea.
- Measure the opportunity cost of any defensive or stationary champion before committing one.
