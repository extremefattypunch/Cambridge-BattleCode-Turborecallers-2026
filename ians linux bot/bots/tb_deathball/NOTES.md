# tb_deathball — notes

Cambridge Battlecode 2026a (cambc) Python bot, built for Sprint 3 (only unseen maps, so nothing
in it depends on a map name).

## Strategy

* **Draft** (`src/draft.py`): a fixed preference list made of tanky melee damage first, then a
  two-body pick, a healer, then casters: Vendetta, Varg, Cassi & Issac (one pick, two bodies),
  Willow, Ryth, Marcella, Tavi, Ren, Stellar, Vesper Vale, Prism. Draft memory just holds a
  tag.
* **Leader / ball**: the leader is the first living ally in roster order of its squad. It scores
  every camp group as `(gems + 0.12*gold) / (travel + clear_time + wait + 6)`:
  * travel: path distance from a native `DistanceField` over the static terrain;
  * clear_time: group HP / team DPS (strength + 0.2*focus, summed over living members);
  * wait: the group's known respawn time minus travel. Groups more than 25 rounds away from
    respawning are skipped.
  It rejects a group when the estimated damage soaked (`0.6*sum_str*clear_time`) is more than
  55% of the squad's current HP. It also skips groups inside the hazard zone of another awake
  camp, and groups it recently could not reach. A new target must score 35% better than the
  current one before the leader switches (hysteresis). The leader publishes the target in shared
  memory. Followers read it and only use their own target when the shared value is stale.
* **Squads**: when 4 or more bodies are alive and each roster-parity half has at least 2
  members, the team splits into two balls by roster index parity. Squad 0 publishes its target at
  shared-memory bytes 0-1 and squad 1 at bytes 5-6, and squad 1 excludes squad 0's target.
  Otherwise there is one ball.
* **Engage**: the squad waits up to 12 turns, per target, until at least min(squad, 3) allies are
  within 5 tiles before waking a sleeping group whose strength is above 20. Spells go first,
  because some spells exclude walking. Then the bot basic-attacks the lowest-HP camp in range,
  then uses attack-reset and attacks again. A melee champion moves and attacks in the same turn;
  a ranged one does only one of the two. Willow heals the ally missing the most HP, and Varg
  shields when hurt.
* **Capture**: when the group is dead and its state is `CampGroupRewardAvailable`, everyone walks
  onto the spawn tiles. If the group is respawning, a follower reports it to the leader through
  shared memory bytes 2-4 and steps off the spawn tiles.
* **Tribute**: a champion tributes when its bag is 18 or more gems, when the round is 1870 or
  later, when an altar is 2 or fewer path-tiles away, or when it carries 8+ gems and an altar is
  6 or fewer path-tiles away. Distance is path distance, not Chebyshev: altars across holes
  matter.
* **Shopping**: the champion recalls to shop when it holds 150+ gold, carries 3 or fewer gems, has
  no threat nearby and is not within 7 tiles of its target. Melee build: 5 Jungle health
  (emblem: -30% camp damage), then 5 Monster strength (+15% camp damage), then alternating Power
  strength and Power health. Ranged build is the other way round. Willow: Jungle health, then
  Power focus.
* **Survival**: an awake camp that is not our target projects a hazard zone (its range + 1).
  Paths avoid these zones, and a champion standing in one leaves first. At low HP
  (`hp < max(30%, 2.5*incoming)`) a champion steps out of range, recalls once below 50%, and
  heals at spawn to 92% before it rejoins.
* **Enemies**: if an enemy champion is in range, the bot uses damage/stun spells on the weakest
  enemy within 4 and basic-attacks the weakest one in range.

## Mechanics learned (engine / API)

* **Waking camps**: a starter-style bot (or an enemy) that hits the Monolith next to gem
  clusters keeps it awake for as long as anyone stands in range. It then kills whoever farms the
  clusters. In v1, all 31 deaths on 00anvil came from that one Monolith. Treating awake
  non-target camps as no-go zones took deaths from 31 to 2.
* **Blocked respawns**: a champion standing on a spawn tile of a respawning group stops the whole
  group from respawning ("any occupied spawn tile delays the entire group"). A bot that waits on
  the tile for the respawn deadlocks forever, so step off.
* **Vision of camp groups**: `CampGroup.state()` can return `CampGroupAlive` while
  `vision.camps()` shows none of that group's camps (bushes, or partial vision of the spawn
  tiles). Treat that case as "keep walking towards it", never as "respawning".
* **DistanceField reachability**: use the `visited` bitboard from `compute` / `compute_to` to
  test whether a tile was reached; `get()` on a tile that was not reached is meaningless.
* **Ally deadlocks in corridors**: `vision.champion_tiles()` includes allies. A path search that
  treats allies as walls deadlocks the ball in 1-wide corridors. Retry the search with allies
  passable, and only step onto free tiles.
* **Path distance vs Chebyshev**: on hole maps (01islands, 01elk-arena) altars and camps that
  look close are unreachable. All decisions use path distance from a `DistanceField` over
  walls|holes|altars|enemy spawn.
* **Shared memory**: the 8 bytes are plenty for a target id plus a round stamp, used as a
  freshness check. Leaders get a higher `set_priority`, so they act before followers in the same
  round. Priority takes effect from the next round.
* **Logs**: the replay bundle (`.repl26a`) is a zip that contains `team-a.stdout` and
  `team-b.stdout`. That is where `print` output goes; `cambc run` does not echo it.
* **Statistics**: `--statistics x.json --json` events include `death` entries with the killer
  (camp id or champion). That is how the Monolith problem was found.
* **Gold**: gold gets split among the capturers, so a 4-6 body ball earns little gold per body.
  Without the recall-to-shop trip, gold piled up unspent (500+).
* **Fuel**: there were no fuel exhaustions. All heavy work uses native Bitboard and
  DistanceField operations; Python loops only cover camp groups, spawn tiles and visible units.

## Eval history (quick 12-map set, both sides, vs starter-python)

| version | change | result |
| --- | --- | --- |
| v1 | first deathball | 21W-3L (88%), gems 749 vs 221, deaths 4.4 |
| v2 | hazard zones (awake non-target camps) | 23W-1L (96%), gems 772 vs 259, deaths 2.4 |
| v3 | ally-passable pathing, path-distance altars, gate fix, respawn fallthrough fix | 22W-2L (92%), gems 846 vs 230, deaths 2.0 |
| v4 | follower→leader respawn reports, step off spawn tiles, shopping recall | 23W-1L (96%), gems 929 vs 216, deaths 1.4 |
| v5 | stuck detection (6 failed approach turns -> skip group 40 rounds), two-squad split | 24W-0L (100%), gems 1005 vs 160, deaths 2.6 |

Single-game results vary from run to run: the engine seed changes per run, e.g. 01gold-rush A
scored 274 in one v4 run and 461 in another. Compare whole evals, not single games.

Final run on the 20-map sprint set, both sides, vs starter-python (the same code as v5):

`SUMMARY tb_deathball vs starter-python: 40W-0L (100%)  avg gems 901 vs 144  avg deaths 3.7 vs 34.9  botFaults(A) 0`

Quick 12-map set, one side only, vs starter-cpp:
`SUMMARY tb_deathball vs starter-cpp: 12W-0L (100%)  avg gems 1006 vs 186  avg deaths 2.4 vs 32.4  botFaults(A) 0`

## Known weaknesses

* **00stampede and 02guardians: 0 gems for both sides.** We still won these games, but only on
  the lifetime-gold tiebreak. On 00stampede every gem sits in one huge Elk herd, about 6 Elks plus
  clusters, and the danger filter rejects it for a squad and for the full team. On 02guardians we
  also take 16-22 deaths. A "merge both squads for a group too big for a half-team" rule, plus a
  better damage model (only camps within range of the tank actually hit), would fix this. It is
  the next thing to do.

* Only tested against the starter bots. A coordinated enemy ball, or altar locks, are untested.
* No TP crystal or dash use, so groups that can only be reached across holes are ignored.
* The danger model is crude: there is no look-ahead on which ally tanks, and Monolith groups are
  only taken when the team is already strong.
* Squad membership is by roster parity, so Cassi and Issac (linked deaths) always end up in
  different squads.
* `odd state` (group alive but no camps visible) is handled by walking closer; in bushes this can
  waste a few turns.
