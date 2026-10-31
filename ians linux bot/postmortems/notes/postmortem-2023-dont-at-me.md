# Don't @ Me - Battlecode 2023 Postmortem

- **URL:** https://battlecode.org/assets/files/postmortem-2023-dont-at-me.pdf
- **Raw:** ../raw/postmortem-2023-dont-at-me.pdf
- **Event:** MIT Battlecode 2023 ("Tempest": resources, islands, anchors)
- **Team / placement:** Don't @ Me (George Zhang, Henry Liao, Parum Misri, Ray Guo; UW Seattle and Georgia Tech). **Finalist in 2023, listed as 7th on the battlecode.org Past Years page.** They qualified by beating the 9th seed 4-1 in the US Qualifiers and entered Finals as roughly an 8th-12th seed. The 2023 winner was Producing Perfection, with Gone Fishin' 2nd and 4 Musketeers 3rd.
- **Same game as cambc 2026a?** No

## Game summary
HQs spawn carriers (which gather two resources, adamantium and mana, from wells), launchers (ranged combat units that move every other turn), amplifiers (comms relays) and anchors. Anchors captured islands that heal nearby allies and give a win condition. Communication was a shared array of 64 ints, writable only near the HQ, an amplifier or an island. The map had clouds that reduce vision and currents that push units.

## Lessons

### Strategy
- Prioritising generality and robustness got them to Finals. At the top, though, **specific strategies for specific map states** beat generic robustness, and they lacked time to build those.
- Unit-building timing: spend every resource immediately on the always-useful units (launchers and carriers) to keep tempo. Enter a "save" mode only for expensive items, and still build the cheap unit when there is excess of one resource.
- Island anchors were built on a schedule (round 250, 500, 750, then every 100 from round 1000). An objective that heals is only valuable once enough units exist to use it.

### Micro / combat (launchers)
- **Target scoring:** unit-type value + damage dealt + missing HP / 2 + 100 if it kills. Always prefer targets already in range.
- **Kiting:** hit, then step back, possibly out of enemy vision. This exploits turn order (the first mover gets a free hit) and lets allies step in behind.
- **Step up:** if an ally is already in range of an enemy, step forward instead of kiting, since single-target enemies can only hit one of you.
- **Fallback:** below half HP and not in combat, go to the nearest captured healing island and stay until full, unless an enemy appears.
- **Follow-first grouping:** each unit follows the first nearby ally that moved this turn, which keeps packs together without comms. They found that top teams won early 3v3s purely because their units stayed adjacent.
- **Move in lockstep:** units only explore on even turns unless in combat, so packs stay synced.
- **Speculative attacks into fog:** if the attack is free (it will be ready again by the next move turn), attack a random cloud tile you can't see into. It is harmless and sometimes hits a hidden enemy.
- **Support units** (amplifiers) keep away from the nearest enemy, attach to the furthest friendly military unit, and repel each other to maximise coverage.

### Macro / economy
- Gathering: the closest wells first, with a per-well cap on workers, a starting resource ratio of about 3:1 that adapts with map size, and an exploration radius that widens over time. They moved assignment logic off the HQ onto the workers themselves, which removed fragile central assignment.
- **"Pinwheel" opening scout:** the 4 opening units go out on the 4 diagonals and then turn 90 degrees, together sweeping the area around the base for key resources.

### Pathfinding
- Three tiers, from most to least compute:
  1. **Unrolled Bellman-Ford** over the vision window, relaxing edges in centre-outward order so 1-2 passes suffice.
  2. **Greedy** (a recursive cost-min that first tries only the target direction and its two neighbours, then the perpendiculars). It was often *more* reliable, and they used it when compute was low, when 1-2-turn optimality mattered (combat), or when vision was reduced.
  3. **Tangent bug** as the fallback when the others return nothing. Its edge cases mostly come from circling other robots.

### Communication (tight shared memory)
- Each 16-bit slot is split into 6 bits x, 6 bits y and 4 bits of flags.
- Four comm classes:
  1. **HQ-owned** (HQ locations, global commands).
  2. **Permanent** (enemy HQs, wells, **symmetry bits**).
  3. **Command** (temporary orders, **double-buffered by round parity**: on even rounds read the odd half and write the even half, so a late-acting unit's message isn't wiped before others read it).
  4. **Report** (a unit reports a location and its state; the HQ folds it into permanent info next round).
- They clear a section by resetting its count instead of zeroing the slots, which saves compute.
- **Local DB plus sync:** units cache discoveries locally and "upload" when in comms range, then "download" when they see the counters change.
- Symmetry: reflect known wells and HQs under the 3 candidate symmetries to rule some out, then mirror known locations to find enemy targets.

### Compute / bytecode
- They optimised only the hot paths: unrolled Bellman-Ford, and a custom linear-probing hash set instead of `java.util` (much cheaper add and contains).
- Regret: as the bot grew, compute became a constraint late in the season. Wished-for techniques included parallel bit tricks, more bit shifts, generated unrolled code, and cheap string-buffer storage.

### Testing & dev workflow
- **Archetype versioning:** DB (dumb bot, days 1-3: explore, attack the nearest thing, act on cooldown), then BB (better pathing and micro), then CB (comms), then EB (experiments), then FB (tuning and bug fixes). Each archetype had 6-10 packages.
- **Sense, think, act** control flow, with sensing cached once per turn.
- Map-specific bugs (clouds, currents) only showed up on new tournament maps. **Test on the newest, weirdest maps.**
- Advice: read the specs and old postmortems. "Make it work, make it right, make it fast". Early losses matter little in a long season.

### Mistakes / regrets
- They couldn't respond to meta shifts during Finals week because of coursework.
- Too little compute optimisation, and comms space was left unused on many turns. They suggest rotating extra info by turn parity, or every 4 turns, to send more over time.

## Transfer to cambc 2026a
- 8 bytes = 64 bits of shared memory. Design fixed fields: e.g. symmetry (2 bits), 1-2 enemy sighting coordinates (7+7 bits each for maps up to 100x100), a focus or help target, and camp-claimed bits. **Time-multiplex fields by round parity** to fit more.
- Compute tiers: greedy for combat moves, BFS or bug for travel, with a fallback.
- Follow-first or lockstep grouping lets champions fight together without comms.
- Score kill targets as value + damage + missing HP + kill bonus. Speculative AoE into bushes when it costs nothing (hidden-blocker rules may also reveal units).
- Fallback to heal at spawn or recall below an HP threshold.
