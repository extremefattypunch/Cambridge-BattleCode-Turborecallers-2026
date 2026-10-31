# tb_splitfarm - split-map efficient farmer

## Strategy
- Draft: fixed priority list of strong solo farmers, dash champions early:
  Vendetta, Varg, Ryth, Vesper Vale, Marcella, Heart of Ruin, Tavi, Ren, ...
- Every champion scores every camp group as value / time
  (value = gems + 0.25*gold; time = path distance + kill time + capture + respawn wait
  + an attrition penalty when the fight needs several recall cycles).
- Spreading: each champion writes its current target group (idx+1) into its own byte of
  the 8-byte team shared memory (slot = rank of its handle among ally handles).
  Groups claimed by an ally are discounted (x0.3) when soloable, and *boosted* (x1.2)
  when they are too heavy to solo (so allies regroup on elks/golem packs); team kill time
  and tank damage assume +55 dps and shared tanking per joining ally.
- Never die to camps: before engaging, estimated damage taken (sum strength * kill time,
  x0.7 for multi-camp groups, x0.7 with Jungle emblem) must fit in HP-150, or the fight
  must be finishable within <=4 hit-and-run cycles. While fighting, if HP <= incoming *
  (steps needed to leave range + 1) + 60 and we cannot finish the camps first, step to the
  adjacent tile with the least incoming damage (dash if available). Recall when out of
  range and HP < 45%; heal to 92% on spawn before leaving.
- Enemy champions: chase/kill when our time-to-kill < 0.8 * their time-to-kill-us
  (dash to close), otherwise step away / recall (and always step away carrying >=15 gems).
- Tribute when gems >= 35, altar within 4 tiles, HP low with >=12 gems, enemies near with
  >=10 gems, team total would reach 1000, no target left, or the round limit is close.
- Shop on spawn/while dead: Jungle shards of strength (emblem: -30% camp damage), then
  Monster shards of strength (+15% camp damage), then alternating Power strength / health.
  Recall to shop when rich (>=150 gold, few gems).
- Unreachable areas: walk components (walls|holes|altars|enemy spawn blocked) computed
  with native reachable_tiles; staging tiles = my component & dilate(target component, r)
  (r=2 dash, r=3 TP crystal). Buys a TP crystal (10g) whenever the map has such areas.
  If the altar is not reachable from an island we recall.

## Engine / API behaviour learned (verified in games)
- Camps do NOT regenerate HP while asleep (monolith stayed at 19145 -> 17015 for 500+
  rounds; a 5-hp gold cluster stayed at 5). So hit-and-run attrition with recalls works.
- Standing on a camp's spawn tile blocks the whole group's respawn forever: a bot that
  "waits" on the tile deadlocks the camp (and its own target loop). Never idle on spawn
  tiles unless capturing.
- Camps standing on bush tiles are invisible from outside the bush cluster. Moving onto a
  hidden occupant returns False (no exception) every turn -> infinite loop if not handled.
  Fix: treat assumed-alive camp tiles as non-enterable, and walk into an adjacent bush tile
  of the same cluster to see them.
- vision.camps()/Camp.is_visible() never report dead camps; detect a dead camp as
  "tile visible and vision.has_camp(tile) is False".
- Replay bundles (.repl26a) are zip files containing team-a.stdout / team-b.stdout - the
  only place bot prints go (`cambc run -o DIR` keeps them).
- --statistics JSON: events of kind "death" have owner = the dying champion and
  entries[].target = the killer (None = killed by a camp).
- Starter Vesper Vale snowballs: +33% gold -> 100+ Power strength shards; it kills
  champions that ignore it. Melee champions must chase ranged attackers (they stand still).
- DistanceField.compute(walls, roots, visited) fills the whole component (no max needed);
  use the visited board to test reachability.

## Eval numbers (tools/eval.py vs starter-python)
- v1 (no enemy handling): quick 15W-9L (62%), gems 457 vs 331, deaths 5.1 vs 38.7.
- see bottom for later runs.

## Known weaknesses
- No multi-hop island crossing; TP landing only within 3 tiles of the staging tile.
- Monolith is never attempted (too much damage per cycle).
- Small dense maps (00gemfight): team spreads and walks too much; the starter's
  4-champion blob farms faster.
