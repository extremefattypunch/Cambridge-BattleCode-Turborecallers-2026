# Cambridge Battlecode Postmortem (Make Fire, Ismail Fateen)

- **URL:** https://ismailfateen.me/blog/cambc_postmortem
- **Raw copy:** `../raw/ismailfateen-cambc-postmortem.md` (DOM-to-markdown extraction made in a headless browser on 2026-10-31; images are listed as `[image: alt url]` but were not downloaded)
- **Event/year:** Cambridge Battlecode 2026, the **earlier** edition run on docs.battlecode.cam: 5 sprints, then an International Qualifier, then in-person finals in Cambridge. Python bots were written against the `cambc` API (`Controller ct`).
- **Same game as cambc 2026a?** **NO.** That edition was a builder/RTS game: destroy the enemy **core**, or after 2000 rounds win on resource tiebreaks. Its pieces were titanium and axionite ores, harvesters, conveyors, bridges, splitters, foundries, launchers, sentinels, gunners and builder bots with `self_destruct`/`fire`/`heal`. There are no champions, camps, gems, altars, drafts or items. Only the generic engineering lessons transfer.
- **Team:** "Make Fire" (two competitive programmers, Ismail Fateen and Ahmed Emara; first Battlecode for both).
- **Placement:** Round of 16 in Sprints 1, 2, 4 and 5. They peaked at **#2 on the ladder** during Sprint 2. In the International Qualifier they finished **one win short of qualifying for the Cambridge finals**, losing twice to Muteki (winners bracket, then losers bracket). They name **bwaaa** as the team that later knocked Muteki out in the finals.
- **Linked pages (not saved; GitHub did not load from this machine before the time limit):**
  - Their bot source: https://github.com/ismailfateen/makefire-battlecode
  - Bug2 pathfinding they ported: https://github.com/maxwelljones14/BattleCode2023/blob/main/src/MPWorking/Pathfinding.java (4 Musketeers, MIT BC 2023)
  - Game spec of that edition: https://docs.battlecode.cam/spec/overview
  - A passing mention: the team "pantheon" used Voronoi partitioning, which the author points to as an example of a much more sophisticated bot.

## Game summary (their edition, not ours)
Each team had a core and builder bots on a symmetric grid with walls and ore tiles. Bots built harvesters on titanium or axionite ores and connected them to the core with conveyors or bridges so the resources were banked. That economy paid for more bots and for defensive or offensive structures: launchers throw enemy bots, sentinels and gunners are turrets. You won by destroying the enemy core, or on resource tiebreaks at round 2000. The devs rebalanced often between sprints: self-destruct was nerfed after S1, bridges after S2, and a 50-unit cap was added in S2.

## Lessons by category

### Strategy
- **Roles matter.** Pure random role assignment can leave you over-committed to one role. They switched to a fixed spawn order cycle (Explorer, Attacker, OreDenier x2, Explorer, Attacker x2, Explorer, OreDenier). The core picked each new bot's role and **encoded it in the spawn direction**: spawning south of the core meant Explorer, southeast meant Attacker, and so on, so no communication was needed.
- **"All bots identical" did badly.** Their S4 unified bot ran a priority list each turn (heal, then go to ore, then connect to core, then attack, then wander). In practice it drifted into economy, because bots kept seeing ores on the way to the enemy and diverting. The fix was a **hybrid**: generalist "everything doers" for economy, plus dedicated DEFENSE_FOCUSED and ATTACK_FOCUSED bots, so defence and offence never starve.
  - *For 2026a:* give each champion a fixed role (farmer, tributer/carrier, fighter or ganker) through draft memory or the 8-byte shared memory. Don't let every champion greedily chase the nearest camp.
- **Symmetry exploitation.** The enemy core is at one of three symmetric images of your own (vertical, horizontal or rotational). Attackers cycled through those candidates and dropped each one once close enough to rule it out. They cached the confirmed location so every later query returned it.
  - *For 2026a:* maps are symmetric too, so the enemy spawn, altars and mirrored camps can be computed at turn 0 (or in the draft with the full-map view) and stored in draft memory.
- **Early aggression worked while defences were weak.** Rushing the core put them #2 on the ladder briefly during S2, until the meta caught up.
- **Denial/harassment as a role.** Their "ore blocker" built barriers on enemy ores, and later bots attacked enemy conveyors near the enemy core and replaced them with sentinels. Rough 2026a analogues: altar locks on the enemy altar, standing on enemy camp spawn tiles to delay respawn, and stealing kills on carriers.

### Micro/combat
- Their launcher logic threw enemy bots to the tile farthest from the core. A bug kept the core location at (-1,-1), which broke it silently from S2 until the qualifier (April 13). They only found it after posting their code publicly and asking for help. The fixed version threw enemies **back toward where they came from**.
  - *Lesson:* assert that cached "known" positions are actually initialised. One sentinel default value can disable a whole subsystem without any error.
- **Attack timeouts plus a blacklist:** stop attacking a target after 30 rounds (the enemy was healing it) and add it to a `was_healed_before` set so the bot doesn't loop straight back.
  - *For 2026a:* cap how long you chip at a camp or enemy you can't out-damage, and blacklist it for N rounds.
- Their attackers sorted possible build spots around a target as empty tiles first, then own buildings (destroy and rebuild), then enemy roads.

### Macro/economy
- Spawn throttling: in the first 500 rounds they only spawned when they could afford about 6 harvesters' worth of titanium, so new bots could actually build. After that the threshold was 3. A unit-cap check kept slots free for turrets.
- Phase constants scaled by map area (thresholds for areas of ≤1200, ≤2500 and larger tiles), on the reasoning that small maps allow earlier aggression.
- A second resource (axionite) was ignored until round 350 (`AXIONITE_START`), with structures pre-built from round 330. Teams that never used it fell behind.
  - *For 2026a:* plan a timed transition, for example from early cluster and wolf farming to elk, golem or monolith once items are bought.
- **Target switching with hysteresis.** When a bot is walking to a far-off ore (far because of walls) and sees a closer one, it switches. It keeps a `visited_ores` set, adding the abandoned target and clearing the set on arrival, so it can't ping-pong between two targets. This "severely" improved results on maze maps (labyrinth, metropolitan_dystopia).
  - *For 2026a:* use the same pattern when re-targeting camps or clusters.

### Pathfinding
- They used Bug2 (ported to Python from 4 Musketeers' 2023 Java with an LLM's help) and never improved it. It was good enough to reach the top 16.
- **Incremental BFS:** a BFS from the core treating unseen tiles as walls, processing at most **500 cells per round** and resuming the next round. The bot then only targets tiles proven reachable, which stopped bridges being built to unreachable spots. *For 2026a with Python at 2.5M fuel per turn:* spread BFS or distance-map work across turns, and use the 100x first draft turn and the 2x first play turn for precomputation.
- **Exploration:** they visited a staggered grid of waypoints (spacing 2r in x and 1.5r in y, offset on alternate rows, r=3), sorted by ring distance from the core and then by angle to approximate a spiral. Only the **first** explorer followed the waypoints; others went to random targets, because two explorers on the same route was waste.
  - *For 2026a:* vision is per champion (8 tiles) and wards give radius-6 vision, so the same staggered-grid idea can place wards or scout routes. Precompute in the draft, since the full map is visible there.

### Communication/shared memory
- They used almost no explicit comms. The spawn-direction trick encoded each bot's role for free.
  - *For 2026a:* the 8-byte shared memory is tiny, so pack only what isn't derivable (which camp each champion claims, an enemy-seen flag and position bucket, a tribute-in-progress flag). Put static data (roles, camp list, routes) in the 1024-byte draft memory.

### Compute/fuel optimisation
- They hit TLE in S4, wrongly blamed Python import overhead, and lost time on that. Profile before guessing.
- Their most expensive function scanned every tile in vision, and for each harvester checked all adjacent cells for links to enemy turrets.
  - *Lesson:* nested scans per tile per turn are what blow the Python budget. Cache results or amortise them across turns, as they did with the incremental BFS.

### Testing & dev workflow
- They rewrote the bot almost every sprint and moved from one file to several modules in S2. The author would start multi-file next time.
- **State management:** ad-hoc booleans like `is_going_to_core` caused many bugs. Switching to per-role `Enum` phases, each mapped to one `run_<phase>` function, made behaviour much easier to reason about. The author says Battlecode is "mostly about having the least amount of bugs", and that a simple bot with few bugs beat clever ideas in this edition.
- S5 shipped with many new bugs and went 1-4 in the top 16. They then used the days before the qualifier to fix bugs instead of adding features.
- They watched games for fun rather than taking notes and regretted it; next time they would watch replays with a checklist.
- They plan to use more AI agents next time and build **tools for the AI** (fast local feedback loops, such as scripted matches and metrics). Most of their pathfinding and helper code was LLM-assisted.

### Meta/draft insights
- Nothing applies to the 2026a draft, since that edition had no draft. One general point: the meta shifted every sprint (self-destruct spam, then bridges, then launcher defence, then conveyor sniping), so expect strategies to need retuning after each balance patch.

### Mistakes they regretted
- The never-initialised core location broke launcher defence for about four sprints.
- Misdiagnosing the TLE (blaming imports).
- Untuned magic constants ("mostly arbitrary with very little testing").
- The unified-role design over-invested in economy.
- Two explorers following identical waypoint paths.
- Locking onto distant targets and ignoring closer ones.
- Shipping a big rewrite for S5 without testing.
- Starting as a single file.
- Watching replays without taking notes.
