# Just Woke Up - Battlecode 2025 Postmortem

- **URL:** https://battlecode.org/assets/files/postmortem-2025-just-woke-up.pdf
- **Raw:** ../raw/postmortem-2025-just-woke-up.pdf
- **Event:** MIT Battlecode 2025 (Java; "paint 70% of the map" game)
- **Team / placement:** Just Woke Up (Tim Gubskiy, Andy Nguyen; Princeton). **1st place, Final Tournament 2025.** Top 4 in US Qualifiers. Came through the losers' bracket, then beat confused (the 1st seed) in two sets in a row to take the title.
- **Same game as cambc 2026a?** No

## Game summary
2D "Splatoon": teams paint tiles, and the first to 70% coverage wins. There are three static tower types: paint (makes paint), money (makes chips) and defense (shoots units and earns chips). There are three mobile units: soldiers paint tiles and attack towers, moppers clean enemy paint and drain enemy units, and splashers paint over enemy paint in a 3x3 area. Towers are built by painting 5x5 patterns around ruins. SRPs are 5x5 patterns that boost income. Units lose paint when they stand off their own paint or next to allies. Comms are very local: unit-to-tower messages need a paint connection, plus tower-to-tower broadcast.

## Lessons

### Strategy
- They won by doing many basic things well, not with one gimmick. They kept 57 bot versions over about 25 days, so more than two iterations a day, each A/B-tested against older versions.
- Their deciding finals feature was a **counter-meta static defense**: defense towers built only at choke points (walls on two opposite sides), near the map centre, with at most 2 of them. It was neutral or slightly negative in self-play, but it beat the aggressive teams they struggled against. They shipped it on that matchup reasoning, and it decided key games against the 2nd and 3rd place teams.
- **Denial:** they "tainted" enemy-reachable ruins with a single blob of paint, so the enemy could not finish the build without bringing a cleaner.
- **Rush defence:** after being 3-0'd by a rush onto their starting towers, they made towers prioritise anti-rush units whenever enemy soldiers were in range. Protecting the starting economy mattered more than expanding.

### Micro / combat
- **Kiting against static targets:** if out of range, step in and hit; if in range, hit and step out. You land 2 hits for each 1 you take. For finals they **synchronised group attacks** so allied soldiers only entered tower range on even turns, and the tower could hit only one of them per turn.
- Target priority for towers and moppers: the weakest or lowest-resource enemies first, to cut enemy numbers quickly.
- The AoE splasher picks the best 3x3 target in reach, with a minimum-value threshold, plus a "splash anyway if this clears everything visible" rule so it never sits stuck.
- They added a resupply ("rez") behaviour that looked neutral in A/B tests but was kept on a reasoned belief that it would help against other teams.

### Macro / economy
- Each unit has a "return location": after a forced trip home (refill), it goes straight back to its unfinished task instead of re-exploring.
- When a unit has enough resources to build, it heads straight for the last-seen unclaimed ruin rather than wandering.
- Upgrade priority goes to high-traffic towers (3+ allies nearby).
- SRP/tower thresholds were set by map size: towers first on small maps (rush risk), more SRP investment on big maps where compounding has time to pay.
- Starting soldiers explore in the direction they spawned from the tower, which spreads them out cheaply.
- "Zig-zag" exploration: diagonal steps cost the same as straight ones, so zig-zagging toward a target covers more area for free.

### Pathfinding
- Bugnav taken from a prior top team, with a custom tile score (own paint good; adjacency penalty; very heavy penalty for enemy tower range). In wall-follow mode, tiles in enemy tower range count as walls.

### Communication
- 32-bit messages: 3 bits message type, 12 bits x/y, 2 bits tower type, the rest spare. Packed with bit shifts.
- Map "markers" (a secondary paint mark at a fixed offset next to a ruin) encode the planned tower type. Every unit arriving later agrees on the plan, and a later unit with better map knowledge may re-mark it.
- They spent a few opening turns making sure they could hear their own towers (paint-connected), so all units knew every starting tower's location from turn ~1.

### Compute / bytecode
- Expensive per-map state (an int exclusion array for SRP placement) was **updated incrementally as information arrived**, so the decision query was O(1). The first version blew the bytecode limit when two ruins were found at once, so writes were optimised.
- Splasher scoring checks the remaining bytecode and stops scanning early to still act that turn, rather than overrunning and losing the turn.

### Testing & dev workflow
- **A/B script over every map** (borrowed from camel_case's public repo). It shows per-map W/L, then they watch the replays of the maps that flipped.
- **Auto-scrimmage script** that requests ranked/unranked scrims against ~20 top teams after each significant change. They reviewed every loss and every surprising win.
- Code structure: Robot base, then Unit/Tower classes, then one class per type. Each unit has a state machine: sense, then `determineState`, then the state handler, then a **state-invariant post-action** (e.g. painting the correct colour for any tile touched). This avoided long if-chains.

### Meta insights
- Every top team had one or two creative gimmicks (rush, tower flickering, defense towers). Copy what works, but also find your own edge.
- Self-play A/B results can be misleading for features that target specific opponent styles. Judge such features against real opponents.

### Mistakes / regrets
- They copied exploration code they did not understand, it worked poorly, and they had to rip it out. Their advice is to understand any borrowed code.
- An early k-d tree idea was far over budget. A flat 2D int array with incremental updates won.

## Transfer to cambc 2026a
- Build A/B-over-all-maps and auto-scrim scripts first. Watch replays of the maps that flipped.
- State machine plus "return location" memory, so a champion that recalls to heal or shop goes back to its camp or capture.
- Synchronise focus fire on camps and enemies, and kite camps. Camp range 3-5 out-ranges champions, so tank or burst rather than kite.
- Counter-meta static choices (altar locks, wards at choke points) may test neutral in self-play but win against aggressive opponents.
- Denial plays: block camp respawns by standing on spawn tiles, and lock altars.
