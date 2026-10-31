# tb_aggro: "farm + punish"

## Strategy
- **Draft** (`src/draft.py`): melee bruisers first, by preference: Vendetta, Varg, Ryth,
  Marcella, Tavi, Ren, Vesper, Willow, Stellar, Prism, Cassi&Issac. Melee champions can walk
  and attack in the same turn, which helps both camp farming and chasing.
  Heart of Ruin (11) is not used.
- **Static setup** (first play turn, which gets 2x fuel): one DistanceField per camp group
  (static walls/holes/altars/enemy spawn), one to altar approach tiles, and one to our spawn.
  Group hp, dps and range come from a fixed camp-stat table. Map names are never used.
- **Team coordination** through the 8-byte shared memory. Byte `slot` (0..5, the rank of
  the champion handle among allies) holds `target_group+1` in its low 7 bits and a
  "ready / at staging" flag in bit 7.
  - Score per group: `(3*gems + 0.5*gold) / (path_dist + kill_turns + 6)`, plus bonuses
    for joining allies' targets and for sticking to the current target.
  - Feasibility: estimated incoming camp damage (`hp/team_dps * camp_dps * 0.75`) must be
    within an hp budget. If a group is not solo-feasible but is team-feasible, the champion
    waits at distance `range+2` until enough allies are flagged ready. Groups with a
    Monolith are never attacked.
  - The champion attacks only camps of its target group, lowest hp first. It casts its
    damage and stun abilities on them and uses an attack reset for a second hit.
- **Never die cheaply**
  - At under 38% hp, or when outnumbered and under 60% hp, the champion first steps out of
    every threat's range (enemies, awake camps), using the shield if it has one, then
    recalls. Recall is cancelled by damage, so recalling inside camp range does not work.
  - It heals on spawn to 90% before leaving.
  - It remembers awake Elk, Golem and Monolith camps for 4 rounds as a "danger zone".
    Pathing avoids these zones (with a fallback to normal pathing), and groups inside them
    get 0.2x score.
  - A stray awake camp that is hitting the champion: if its group is feasible, the champion
    switches target and fights it. Otherwise it backs off and skips its current target for
    40 rounds. This removed a back-and-forth loop that cost a lot of time.
- **Punish (PvP)**
  - Targets visible enemies by `hp - 20*gems - 300*(channelling)`.
  - It attacks enemies in range when the fight looks winnable: no more enemies near than
    allies near and own hp at least 45%, or the target dies to two hits, or own hp is at
    least 1.3x the target's.
  - It chases enemies within 5 tiles that are hurt (under 55%), carry 8 or more gems, or
    are channelling. It does not chase into the enemy spawn or while carrying 20 or more
    gems.
  - Stuns (cc abilities) go first on enemies that are recalling or tributing.
  - It buys an Altar Lock (10g) once it has at least 40 gold. It places the lock on an
    altar within 2 tiles where an enemy is tributing, which cancels their channel.
- **Tribute**: when carrying 30 or more gems, when an altar is within 4 tiles, when
  carrying 12 or more gems with an altar within 12 tiles, when it has no target, or after
  round 1850. Altars with an enemy lock are skipped.
- **Shopping**: Jungle Strength x5 (−30% camp damage and +str), then Monster Strength x5,
  then Durability Health x5, then Jungle Health x5, then Power Strength.

## Engine and API behaviour learned (useful for other bots)
- Bot stdout goes into the replay zip (`*.repl26a` is a zip containing `team-a.stdout`,
  `team-b.stdout`, `*.fuel`). Read it with `zipfile` and strip the `\x00` bytes. The `.fuel`
  file holds per-turn fuel use as u64s.
  - Budgets: 250M on the first draft turn, 5M on the first play turn, 2.5M after that.
    This bot uses about 0.4M per turn.
- `DistanceField.get()` returns **65535** for unreached tiles.
- `Camp._group` (private attribute) is the group handle and matches `int(CampGroup)`. It
  gives a cheap mapping from a visible camp to its group.
- **Standing on a spawn tile of a respawning group blocks its respawn.** If the
  "go to the group tiles" logic does not treat respawning groups as gone, champions can
  deadlock: they stand there forever and the group never respawns. Treat
  `CampGroupRespawning` as gone even when its timer reads 0.
- When a group is partly dead, move toward the *live camp tiles*, not the union of the
  spawn tiles. Otherwise a champion standing on a dead camp's tile thinks it has arrived
  and idles.
- `Champion.remaining_channel_time()` raises "Champion is not channeling" when the
  champion is not channelling.
- Varg's splash and stray hits wake neighbouring camps, such as a Monolith next to gold
  clusters (01gold-rush). The Monolith (range 5, 200 str) then kills anyone farming the
  ring around it.
- Without solo/team feasibility logic, a team of solo-infeasible targets deadlocks
  (02the-pond: 0 gems). The waiting has to be coordinated, here with ready flags in shared
  memory, and it needs a timeout.
- Some camps sit behind holes (01islands, the-pond centre). Their DistanceField value is
  65535, so they must be skipped. Dash or TP crystal would be needed to reach them; this
  bot does not do that.

## Eval numbers (vs starter-python, quick 12 maps x 2 sides)
- v0 (first version): 14W-10L 58%, gems 484 vs 352, deaths 2.0 vs 34
- + coordination and respawn fix: 18W-6L 75%, gems 692 vs 274
- + stall detection: 21W-3L 88%, gems 851 vs 278
- + stray-camp handling: 22W-2L 92%, gems 858 vs 219, deaths 2.5 vs 30.6, botFaults 0
- Final sprint (20 maps x 2): `SUMMARY tb_aggro vs starter-python: 37W-3L (92%)  avg gems 744 vs 185  avg deaths 2.4 vs 33.2  botFaults(A) 0`
  (losses: 02famine A 201-348, 01gold-rush B 440-468, 00stampede A 0-0 lost on the Team-B tiebreak)

## Known weaknesses
- 00stampede: neither side scores (0-0), so Team B wins the tiebreak. Nothing reachable is farmed
  there; it probably needs hole crossing.
- No TP-crystal or dash crossing of holes: 01islands as team A scores only 30 gems.
  Island camps and altars are ignored.
- 02famine (team A) is still lost, 201 vs 348. Deathball travel on large sparse maps is
  slow, and splitting up would farm more there.
- PvP fight evaluation is crude: it counts heads and compares hp, and ignores enemy items
  and abilities. Against stronger PvP bots the deathball may get kited by ranged enemies.
- Enemy sightings are not shared between allies (no free shared-memory bytes left after
  the 6 commit slots).
- Feasibility uses my own strength times the helper count. It does not use the allies'
  real strength or the Jungle/Monster emblem bonuses.
