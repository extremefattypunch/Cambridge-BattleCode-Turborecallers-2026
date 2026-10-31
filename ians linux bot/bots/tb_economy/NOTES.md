# tb_economy: notes

Python bot for Cambridge Battlecode 2026a, Sprint 3. It started as a copy of `bots/starter-python`.

## Strategy
- **Draft** (`src/draft.py`): picks from a fixed priority list built for camp clearing and survival:
  VENDETTA, VARG, CASSI_AND_ISSAC (one pick, two bodies), RYTH, MARCELLA, TAVI, WILLOW, REN,
  VESPER_VALE, HEART_OF_RUIN, PRISM, STELLAR. On maps with many holes (more than 40), REN and
  VESPER_VALE (both have dashes) move up the list. Each pick is wrapped in try/except, and a
  failed pick falls back to the next one. In the draft memory it writes the count of each camp
  kind and the number of groups (not used in the match yet).
- **Choosing a target** (`Bot.choose_target`): runs a native DistanceField from the champion over
  static terrain. For each camp group: value = gems + 0.12 * gold. Kill time = remaining HP /
  team DPS. "Danger" = camp strength * kill time * (0.7 with the Jungle emblem). `need` is the
  smallest number of helpers that keeps danger at or below 3 * current HP. Score = value /
  (distance + kill time + 8). There is a stickiness bonus for the current target. Groups that
  need helpers get a bonus when allies are committed to them. Safe groups get a penalty instead,
  which spreads the team out over gem clusters.
- **Coordination**: each champion writes its target group (index + 1) into its own byte of the
  8-byte shared memory. The slot is the champion's rank by id. Only the leader (the lowest-id
  living ally) may pick a group that needs helpers before anyone else has committed to it.
  Champions wait outside camp range (up to 25 turns) until enough allies are within 5 tiles.
- **Combat order per turn**: support casts (shield when threatened and below 90% HP, heal the
  ally with the lowest HP fraction under 65%, stun the strongest awake attacker or an enemy),
  then damage casts (single target / AoE at the tile that covers the most camps / Heart of Ruin
  landing dash), then a basic attack. After the basic attack it uses the attack reset and hits
  again. Basic attacks never wake unrelated camps that can hit back. Harmless clusters are
  always fine to hit.
- **Survival**: below 35% HP, step out of every threat's range and only then recall. Taking
  damage cancels a recall. Wait on spawn until 95% HP. Below 55% HP, do not start a dangerous
  fight.
- **Gems**: tribute at 25 or more gems, when an altar is within 6 tiles, when below 50% HP with
  10 or more gems, or after round 1850.
- **Items** (bought on spawn or while dead): melee buys 5 Jungle Health shards (emblem: -30% camp
  damage), then 5 Monster Strength, 5 Durability Health, then Power Strength from then on. Ranged
  buys Jungle Health, then Monster Strength, then Power Strength. Casters buy Jungle Health,
  then Monster Focus, then Power Focus.
- **Dash**: dashes on long trips, to the tile within 2 that has the lowest DistanceField value.
  A landing-damage dash is kept for fights.

## Key mechanics learned (important for other bot authors)
1. **Standing on a respawning group's spawn tile blocks its respawn forever.** The rules say "any
   occupied spawn tile delays the entire group". My first version waited on the spawn tiles for
   the camp to come back, and that deadlocked whole maps (gold-rush: 44 gems all game). Skip a
   group while it is respawning (`CampGroupRespawning.timer`), unless you will arrive about when
   it respawns.
2. **The goal must be the camps that are still alive, not every spawn tile of the group.** A
   group stays `CampGroupAlive` until every camp in it is dead. If you path to "the nearest spawn
   tile" you can end up on the tile of a dead member and never attack the rest. Going from that
   to `goals = group.spawn_tiles() & vision.camp_tiles()` took the eval from 88% to 96%.
3. **`cambc.vision.champions(Team.ALLY)` can raise** `cambc.Error: No visible entity of this kind
   occupies the tile` (seen with Cassi & Issac on the team). Use
   `cambc.champions(Team.ALLY)` (it includes allies outside vision) and wrap each call in
   try/except. Before the fix, every turn that reached this call threw, and the champion stood
   still.
4. The bot's `print` output does not appear in `cambc run`. It is stored in the replay bundle,
   which is a zip with `team-a.stdout`, `team-b.stdout`, `*.debug` and `*.fuel`. Pass
   `-o <dir>` and read it with `zipfile`. `import traceback` works inside the WASM Python.
5. `DistanceField.get` returns 65535 for tiles it never reached. Some maps have clusters that
   walking cannot reach (the-pond gem clusters across holes).
6. Fuel: a turn of this bot costs about 0.5M of the 2.5M Python fuel. The DistanceField is
   computed every turn plus once per move; this is fine.
7. Ability slots each have exactly one kind (`AbilityDamage`, `AbilityCc` with modifier = the
   damage part, `AbilityAoeDamage` with a stun duration, `AbilityDash` whose modifier > 0 means
   landing damage). `ability.use(None)` works for self casts (shield, attack reset).

## Eval numbers (vs starter-python)
- First version: 8W-16L (33%). It was far too passive, because of the bugs above.
- After the respawn-deadlock fix: 21W-3L (88%), avg gems 903 vs 308, deaths 10.3 vs 26.8.
- After the alive-camps goal fix (quick 12 maps): **23W-1L (96%), avg gems 1005 vs 214, deaths
  10.1 vs 25.9, botFaults 0**.
- **Final `--maps sprint` (20 maps x 2 sides):
  `SUMMARY tb_economy vs starter-python: 38W-2L (95%)  avg gems 879 vs 173  avg deaths 12.7 vs 31.1  botFaults(A) 0`**.
  The two losses were 00lanes B (910 vs 932) and 01big-world A (258 vs 433). 02guardians: 0 vs 0
  gems; the bot won on tiebreak. 00stampede A: only 120 gems.
- Experiment, rejected: TRIBUTE_GEMS=15 instead of 25. It helped 01big-world but hurt 00lanes a
  lot (1009/910 fell to 635/253), so I reverted it.

## Known weaknesses / TODO
- The draft is a fixed priority list. Draft memory is written but not used. Whether
  HEART_OF_RUIN (11) can be picked was never tested, because it is never reached.
- No TP-crystal or dash pathing to cross holes. Camps that walking cannot reach are skipped.
- Ranged champions walk into melee distance (the goal is the camp tile) instead of kiting at
  range 3.
- Fighting enemy champions is opportunistic only: no focus fire, no altar locks, no stealing
  carried gems.
- The thresholds (TRIBUTE_GEMS=25, DANGER_MULT=3.0, LOW_HP=0.35, HOLD_MAX=25) were tuned only a
  little.
- Respawn memory is per champion; it is not shared through shared memory.
- 02guardians gets 0 gems and 00stampede/01starvation score low or die a lot. Those maps need
  monolith/golem handling with the whole team, or a way across holes.
