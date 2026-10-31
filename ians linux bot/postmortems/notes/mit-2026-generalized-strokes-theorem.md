# MIT Battlecode 2026 Postmortem: "Generalized Stroke's Theorem" (2nd overall)

- **Title:** Battlecode 2026 Postmortem (Urav Tanna, Seth Lifland, Andre Mao, of Generalized Stroke's Theorem), dated 7 March 2026, 10 pages
- **URL:** https://battlecode.org/assets/files/postmortem-2026-generalized-strokes-theorem.pdf
- **Raw copies:** `../raw/postmortem-2026-generalized-strokes-theorem.pdf` (original PDF) and `../raw/postmortem-2026-generalized-strokes-theorem.txt` (pdftotext -layout)
- **Bot source code (linked from the PDF):** https://github.com/uravt/Battlecode26 (final package `src/Version40/`; behaviours in `src/Version40/BabyRatBehaviors`; message types in `src/Version40/Communication/SqueakInfo.java`)
- **Event:** MIT Battlecode 2026, "Uneasy Alliances" (Java, January 2026, with sprints, US qualifiers and finals)
- **Team and placement:** Generalized Stroke's Theorem, three 2nd-year students at the University of Virginia (two in their 5th Battlecode year, one rookie). They were finalists for the second time and finished **2nd overall**. The winner was "subscribe to caterpillow".
- **Same game as cambc 2026a?** **No.** It is a different engine, language and game. The transferable parts are architecture, communication design, pathfinding technique, micro method, handling neutral NPCs, and dev workflow. Each section below ends with a "cambc translation".

## Game summary (MIT BC26 "Uneasy Alliances")
Two teams of robot rats share a map with neutral robot **cats**, the first non-player units in Battlecode history. There are two unit types. **Baby Rats** are 1x1, have a *directional vision cone* and can carry/"ratnap" and **throw** other units. **Rat Kings** have a 3x3 footprint and are the team's home/bank. The economy is **cheese** from cheese mines, which baby rats carry back to the Rat King. Terrain includes walls and **dirt**, which can be dug through at an action-cooldown cost. A team wins by destroying all cats or all enemy Rat Kings. Teams can cooperate against the cats, but most games ended with one team backstabbing the other before the cats died. Compute was limited to 17,500 Java bytecodes per unit per turn, and a unit that runs over is halted mid-execution. Baby rats cannot write the team shared array, so their only decentralised channel was "squeaks", short broadcast messages.

## 1. Architecture / code structure (section 2, "Structure and Modularity")
- Earlier seasons had left them with 3,000-line monolithic files that made late-season iteration painful. This year they used the **Strategy pattern**:
  - **State Updater:** the macro decision-maker. At the start of each turn it reads the sensed state and **selects one Behavior** for the unit.
  - **Behavior interface:** separate implementations for micro (combat), exploration, cheese scavenging and so on. The chosen behavior's `execute()` runs that turn.
  - Each Behavior is a **singleton**, so it keeps persistent data across turns even while the unit switches between other behaviors.
- They weren't sure it made them faster to iterate, but it made experimenting easy and kept the codebase organised late in the season. The joke is that it sometimes looks like FizzBuzz Enterprise Edition.
- **cambc translation:** give each champion a per-turn `choose_behavior()` over persistent behavior objects, such as `FarmCamp`, `Capture`, `ReturnAndTribute`, `Recall/Heal+Shop`, `Fight`, `Escort`, `DenyAltar(lock)`, `Ward/Scout`. Keep state that must survive behavior switches inside these objects: the current camp target, the path cache, the last-seen enemy and the tribute plan. That way you can add or swap a behavior (for example an altar-lock ambush) close to a deadline without touching the rest. Keep it lightweight in Python, because every method call and attribute lookup costs fuel.

## 2. Communication (section 3)
### Shared array
- They used the shared array only lightly, for high-level strategic facts: Rat King locations, **map symmetry**, cheese mine locations and candidate Rat King formation coordinates. Baby rats could not write it.

### Squeaks (main channel)
- Messages were bit-packed. The **first 3 bits are a type header**, and each message type implements a Java **sealed interface** `SqueakInfo`, which keeps encode/decode polymorphic and modular.
  The repo shows 7 message types: EnemyRatKing, FormRatKing, NearbyCat, Symmetry, Pickup, Presence and CheeseMine (7 types fit a 3-bit header).
- Squeaks were designed to be **easy to extend and debug**. Because they were the only way for baby rats to coordinate without the king, a robust encode/decode framework mattered.
- **"Squeak maximisation"** (section 6.1): during micro, every baby rat squeaked **its own health, nearest enemy's health, nearest enemy's direction and location** every turn. Allies could then build a 360-degree picture despite each unit having only a vision cone. This mattered because enemies beside or behind you could ratnap you regardless of your health. In crowded fights this pushed them over the bytecode limit, and they judged the trade worth it.
- **cambc translation:**
  - Our analogue of the vision cone is **per-champion vision that is not shared with allies**, so the "broadcast what you see" idea transfers directly, but our channel is only **8 bytes per team**.
    Use a fixed layout rather than a stream of tagged messages. One option is 1 byte per champion for status (behavior id plus a "carrying many gems / in danger / channelling" flag), plus 2 to 4 bytes for "most important enemy sighting" (x, y, round mod 256, and a coarse HP or champion id). Overwrite the sighting by priority, for example an enemy near our altar, an enemy carrying gems, or a low-HP enemy.
    If we need more message kinds, a small **type header** (2 to 3 bits) on a rotating slot copies their design. Write the encode/decode in one module so it is easy to change.
  - Their shared array held "symmetry + resource locations + rally points". For us, **draft memory (1,024 bytes, read-only during play)** is the natural home for map-static facts computed during the draft, which has the whole map visible and 100x fuel. Candidates are symmetry, the camp list with types and centroids, altar positions, chosen rally/ward spots and per-champion route assignments. That frees all 8 shared bytes for dynamic data.

## 3. Pathfinding (section 4)
### 3a. Their pre-2026 toolkit (described for newcomers)
- **Unrolled BFS:** with a 17.5k bytecode cap, loop-termination checks add up, so Dijkstra or A* are usually too expensive. They used a fixed-radius BFS, unrolled and expanding radially outward in a fixed order. It doesn't guarantee shortest paths even within the radius, but it is good enough.
- **Bug Nav (stack-based, adopted from Gone Fishin' 2023):** while following an obstacle, push the blocked directions onto a stack. If the stack isn't empty, try those directions, and once it is empty resume heading straight to the target.
  When the bot first hits an obstacle it **simulates both left-hand and right-hand following for N steps and picks whichever ends closer to the target**.
  It turns away from map borders immediately, since hugging the edge is rarely good. It keeps a **set of "turn locations"**, and if it would turn at a location where it has turned before, it reverses direction to avoid infinite loops.
- **BugBFS hybrid:** run the local BFS and watch whether it is making progress. If BFS stops reducing the distance, switch to Bug Nav, and switch back once BFS can make progress again. It is bytecode-heavy but works in almost all cases.

### 3b. 2026 adaptations, by phase ("The Dirt Plight")
- **Start to Sprint 1:** they ported the 2025 code and added a **global 2D array of persistent terrain memory** (dirt, passability), so units could plan through areas outside their current vision.
  **Bug:** the logic assumed 1x1 units, so it was **completely broken for 3x3 Rat Kings**. It didn't hurt them until mobile kings became meta later. They also added a **safety filter that keeps baby rats off tiles a cat can see**, which prevented many pointless deaths.
- **Sprint 1 to Sprint 2:** nobody worked on the bot for a whole week, with one member at a conference and another busy. They call this a massive blow. At Sprint 2 they lost games purely because units couldn't handle dirt obstacles, so "dirt-aware pathing" became their top priority.
- **Sprint 2 to US Qualifiers:** first fix was to **treat all dirt as passable** and simply stall when the action cooldown got too high. This forced units to mine through and explore high-dirt regions, and it won decisively on maps where key mines were buried (their Figure 1, a symmetric map with mines in the corners and centre).
  Then they found too much needless digging, which hurt during "cheese famines", so they **added a dig cost to the BFS** as a tunable "laziness" knob. They still believe aggressive digging is often right, because it opens lanes and raises long-run throughput.
- **US Qualifiers to Finals:** units were getting stuck trying to micro through walls. They wrote a **bit-shifting reachability check** that computes full reachability, including outside vision, for about 300 bytecodes.
  Inspired by that and by **Om Nom's 2025 postmortem**, they began **rewriting BFS with bitboards**. The old high-school BFS was robust but cost 6 to 8k bytecodes. The new one wasn't as reliable by the deadline, so they kept the old one and plan to finish it for 2027.
- **cambc translation:**
  - **Terrain memory:** our maps are static and the **whole map is visible during the draft**. Precompute passability (walls, holes, altars, spawn tiles) once. Holes are not walkable but are dash-able and don't block sight; bushes are walkable but block sight.
    Persist it per champion, from module globals or the first play turn (2x fuel), and only overlay dynamic blockers (units) from current vision.
  - **Bitboard BFS in Python:** Python big ints make cheap bitboards. Store `passable` as one `W*H`-bit int, with column-wrap masks for E/W shifts. Expand a BFS frontier with 8 shifts, an OR and an AND per layer.
    A per-layer bitset gives a distance field or reachability test with roughly `distance` iterations of a few big-int ops instead of a per-cell Python loop. This is likely to save a lot of fuel under the 2.5M/turn Python budget on 100x100 maps, so benchmark it with fuel counters before committing.
    Their story is also a warning: **don't swap in a rewritten pathfinder right before a deadline unless it's been regression-tested**. Ship the robust slow one if the fast one isn't proven.
  - **Cache distance fields** to fixed targets (each altar, our spawn, each camp group) once, then read the gradient each turn with O(1) lookups instead of searching every turn.
  - **Cost-weighted rather than binary obstacles:** their dig cost maps to adding a **danger cost** (not a block) for tiles inside an **awake camp's attack range** (3 to 5 Chebyshev, camps never move, they hit the nearest champion) and inside known enemy threat ranges.
    Their "never step into cat-visible tiles" filter maps to "don't path through an awake camp's range unless you are the designated tank or on a farming run".
  - **Multi-tile footprint bug:** check that pathing and the movement masks agree with the SDK on edge cases such as dash over holes, own spawn vs enemy spawn tiles, altars being unwalkable, and hidden blockers in bushes returning `False` (retry elsewhere, nothing is spent).
  - The stuck-detection fallback (BFS stopped making progress, switch to Bug Nav) is cheap insurance. Detect "no progress for k turns" and switch mode or target.

## 4. Macro / economy (section 5)
- They saw the game as micro-heavy with some real macro trade-offs. Teams differed most on **when a baby rat should bring cheese back to the king**, the carry-vs-bank threshold.
- **How they improved macro: copy stronger teams.** They queued scrimmages against teams above them, reverse-engineered their macro (which they say is far easier than reverse-engineering micro, pathing or comms), copied it, and kept whatever won. Their Rat-King-on-cheese-mine formation, the **magic numbers for how many baby rats to build and when**, and much else came from this. They admit they didn't originate or iterate much on macro.
- **Baby Rat Taxi (their one original macro idea):** low-cheese rats carried high-cheese rats (150+ cheese) back to the king. It helped in those cases, but they were rare, so the overall economic impact was small.
  Costs: extra action cooldown if you then meet an enemy, and a cat pounce kills both rats at once.
- **cambc translation:**
  - The "when to go home with cheese" question is our **"when to stop farming and tribute"** threshold. Tribute time is `ceil(gems/10)` turn ends, the whole current bag is banked at completion, carried gems go to whoever kills you, and they are destroyed if a camp kills you.
    Make the threshold a **tunable magic number** that depends on distance to the altar, nearby enemy presence and current HP, rather than a constant.
  - Watch the top cambc teams' replays for macro you can copy cheaply: draft composition, opening camp order (clusters first?), when they contest the Monolith, carry threshold, item/emblem build order, use of altar locks, and how many champions stay together.
  - The taxi lesson generalises: **rare-situation features have low ROI**. Prioritise behaviors that fire every game, like opening farm routes, tribute timing and recall/heal discipline, over clever edge cases.
  - One aggressive-digging lesson also generalises: actions with up-front cost that raise long-run throughput (their digging, maybe our early clearing of camps that sit on routes, or buying Monster/Jungle emblems early) can be net positive. Tune with a knob and measure.

## 5. Micro / combat (section 6)
- **Base method: "XSquare-style micro"** (a common Battlecode pattern). When in micro mode, evaluate each of the **9 candidate tiles** (8 moves plus staying) on features such as passability and proximity to allies, enemies and cats. Then a **chain of if/else pairwise comparisons** decides whether tile A beats tile B, and the best tile wins.
- **Information maximisation (6.1):** micro is only as good as its inputs. With vision cones, flank and rear threats matter most, so they broadcast each rat's own HP and nearest-enemy info every turn (see Comms) to give every unit near-360-degree awareness. Their Figure 2 is a spreadsheet of squared distances around a unit, marking the small attack radius and the forward-facing vision cone.
- **Cat micro (6.2):**
  - Against cats, avoid cat vision. If that isn't possible, avoid the **"cat path"**, the 2 to 3 tiles directly in front of the cat, because a forward move kills anything there.
  - While fighting enemies near cats: maximise distance from the cat and avoid the cat path, but **don't weight cat avoidance so heavily that enemy decisions get worse**. Enemies are smarter and more predictable than cats, so avoiding enemy ratnaps came first.
- **Throwing (6.3):** enumerate every reasonable **move + turn + throw** combination and score each by where the thrown unit ends up: hits a cat, an enemy, a wall, an ally, or leaves vision without hitting anything.
  Out of combat with no cats visible, they **held a captured enemy for several turns before considering a throw**, both to save bytecode and in case a better-value throw (another enemy or a cat) appeared.
  Some combos were empirically bad and were **pruned from the candidate set**, for example "move forward, face the current direction, throw", which tended to walk them into enemies or cats.
- **Improving micro (6.4):** watch a lot of games, both your own and better teams'. **Follow individual units into fights** and ask why each one decided what it did. Fix one dumb decision at a time in a way that **minimally disturbs the decisions that were already good**.
  They reverse-engineered a stronger micro team ("Old But Gold") from replays. This is hard because you can't see their inputs, but they say it is worth it.
- **cambc translation:**
  - **Tile scoring:** score the 9 walk tiles, plus dash destinations (up to 2 steps, which can cross holes) for champions with Dash.
    Useful features: can I attack or cast on my priority target from here (ranged champions: move OR attack; "excl" spells forbid walking), number of enemies that can reach me next turn, whether I'm in an awake camp's range (camps hit the **nearest** champion), distance to allies and healer, and distance to our altar/spawn when low.
    Use a pairwise comparator or a weighted score, but keep the order of priorities explicit and easy to tweak.
  - **Enumerate action combos**, as they enumerated move+turn+throw. Our combos are move ± basic attack ± ability ± attack reset, plus a dash variant and a consumable variant. Score them by expected damage, kill chance and stun value, and **prune combos that test badly**. Remember the engine rules: one cast per turn; attack reset only after the attack has been used; ranged champions can walk or attack but not both.
  - **Hold the high-value action:** like holding a ratnapped enemy for a better throw, **save stuns and altar locks for channel interrupts**. Stun cancels recall, tribute and teleport, and a newly placed altar lock cancels enemy tribute channels. Don't spend them on chip damage.
  - **Neutral-threat handling = camps:** camps don't move, have ranges of 3 to 5 that out-range our basic attacks, and target the nearest champion.
    The "cat path" maps to the "camp danger ring". When fighting enemies near a camp, weight **enemy threat above camp threat**, as they did, but don't stand as the nearest champion to an awake Golem or Monolith. Better still, bait enemies into being nearest.
  - **Broadcast HP and nearest enemy** through shared memory so a champion that can't see a flanker still knows about it, within the 8-byte budget.

## 6. Compute / bytecode / fuel optimisation
- They ran under a 17,500 bytecode cap. Running over halts the unit mid-turn, which is like cambc's "suspended mid-code, resumes next round on stale data".
- Their techniques: unrolled fixed-order BFS, bitboard reachability (~300 bytecodes for full reachability), and the planned bitboard BFS rewrite (old BFS cost 6 to 8k).
- They **deliberately accepted going over budget in big fights** for better-informed micro. They also argue that the community's push to "spam codegen" and micro-optimise is **overrated compared with strategy and replay review**.
- **cambc translation:**
  - Python gets 2.5M fuel per turn, with 100x on the first draft turn and 2x on the first play turn.
    Put heavy static analysis in the draft turn, since the whole map is visible, and keep its result in draft memory or module globals.
    Use bitboards (Python big ints) for reachability and flood fills, cache distance fields, and **add a fuel guard** that skips optional work, such as extra combo enumeration, when fuel is low. A mid-turn suspension makes us act a turn late, which is worse in a 1v1 fight than in their swarm game.
  - Don't over-invest in micro-optimisation before the strategy is right. Profile first and optimise only the hot path.

## 7. Testing and dev workflow
- **Replay review was their main tool.** They suspect they spent more time reviewing scrims than writing code. Watching games is the best way to improve micro, and scrimming against higher-ranked teams is the best way to improve macro.
- **Scrim up the ladder** and copy what works, keeping changes only if they improve results, which is a lightweight A/B loop.
- **Fix decisions one at a time while protecting the good ones**, which is effectively regression-awareness at the decision level.
- **Modularity** (Strategy pattern, singleton behaviors) kept late-season iteration possible.
- **Try many strategies and don't get attached:** they admit they sometimes clung to ideas that weren't working, and that you can't know which ideas win until you try them.
- **cambc translation:**
  - Before Sprint 3 locks in about 5 hours, prioritise watching our own losses on the ladder and the top teams' replays over new features. Fix the most frequent dumb decision first.
  - Keep a local regression harness (our bot vs previous versions and vs the starter bot, across all maps and both sides A/B) and accept a change only if it doesn't lose ground.
  - Version the bot in folders (`VersionNN`) so you can roll back a broken late change, as their `Version40` naming suggests.

## 8. Meta / draft insights
- Their game had no draft. The meta insights were:
  - **Alliances were unstable.** Cooperation against cats usually ended in a backstab before the cats were dead.
  - **Mobile Rat Kings became meta late**, which exposed the 3x3-footprint pathing bug they had ignored. The meta shifts during a season, so expect it.
  - **Cheese-return heuristics** were the main macro differentiator between teams.
- **cambc translation:** expect the cambc meta to shift between sprints, for example toward more aggressive ganking of gem carriers, altar-lock denial, Monolith contests or particular draft comps.
  Code that relies on "this situation never happens" (their immobile-king assumption) will break when it does. Our equivalents might be "enemies never contest our altar" or "the Monolith is never taken early". Check top-team replays for the current meta before each sprint.

## 9. Mistakes and regrets
1. **A lost week of development between Sprint 1 and Sprint 2.** Sprint 2 exposed glaring weaknesses (dirt handling) that a week of work would have fixed. Continuous iteration matters.
2. **Hidden shape assumptions:** the pathing assumed 1x1 units, which broke the 3x3 Rat Kings once mobile kings became meta.
3. **Too much needless digging** before they added a dig cost, which hurt the economy during cheese famines.
4. **A late bitboard BFS rewrite** that wasn't reliable by the final deadline, so the expensive old BFS shipped.
5. **Going over bytecode in crowded fights** because of squeak maximisation. They accepted this as a trade-off, but it was a known cost.
6. **The Baby Rat Taxi** had low impact because the situation was rare.
7. **They under-invested in original macro** and admitted they don't enjoy iterating on it.
8. **Over-attachment to failing ideas** (general reflection).

## 10. Concrete takeaways for our cambc 2026a bot (ranked)
1. Spend the remaining pre-lock time on **replay review**: follow single champions through lost fights and fix the most common bad decision without breaking good ones. Then **copy top teams' macro** (comp, farm order, tribute threshold, item build), which is easier to reverse-engineer than micro.
2. Implement **tile-scoring micro over 9 walk tiles plus dash tiles** and **enumerate move/attack/ability/reset combos**. Prune combos that test badly and **hold stuns and altar locks for channel interrupts** (enemy tribute or recall).
3. Use **8 bytes of shared memory as a fixed-layout broadcast** of per-champion status and the top-priority enemy sighting, to make up for unshared vision. Put static map facts (symmetry, camps, altars, routes) in **draft memory**, computed with the draft's 100x fuel.
4. Use **Python big-int bitboards** for reachability and BFS, **cache distance fields** to altars, spawn and camps, and add a **fuel guard**. Don't swap in an untested pathfinder right before a lock.
5. Treat camp attack ranges and enemy threat zones as **path costs, not walls**. Never be the nearest champion to an awake big camp unless you are the designated tank, and weight enemy champions above camps in fights.
6. Make the **carry-vs-tribute threshold a tunable function** of distance to altar, HP and visible enemies (gems are lost on death, and camp kills destroy them).
7. Keep code modular (behavior objects plus a selector) so late changes are low-risk, and keep versioned snapshots for rollback.

## Further reading (official battlecode.org "Past Years" list; not deep-read here)
Source: https://battlecode.org/past.html (extract saved at `../raw/battlecode-org-past-html-postmortem-links.md`)

**2026 (Uneasy Alliances; winner: subscribe to caterpillow; finals video https://youtu.be/HVhT7MgSyUE)**
- Generalized Stroke's Theorem (2nd overall), this document: https://battlecode.org/assets/files/postmortem-2026-generalized-strokes-theorem.pdf
- food: https://www.alext.app/Battlecode_Postmortem_2026.pdf
- 3MiceWalkIntoABar: https://www.outercloud.dev/blogs/battlecode-2026/
- Lorem Ipsum: https://battlecode.org/assets/files/postmortem-2026-lorem-ipsum.pdf
- Sloppy Joe Pirates (video): https://youtu.be/8PEjZTzAjSA

**2025 (Chromatic Conflict; winner: Just Woke Up; finals video https://youtu.be/lVtX8-I_cWQ)**
- Just Woke Up (1st overall): https://battlecode.org/assets/files/postmortem-2025-just-woke-up.pdf
- confused (2nd overall): https://battlecode.org/assets/files/postmortem-2025-confused.pdf
- Om Nom (3rd overall; the bit-shifting BFS that GST cites): https://battlecode.org/assets/files/postmortem-2025-om-nom.pdf
- SPAARK (HS 1st): https://battlecode.org/assets/files/postmortem-2025-spaark.pdf
- The Kragle: https://battlecode.org/assets/files/postmortem-2025-the-kragle.pdf

**Also cited inside this postmortem**
- Gone Fishin' 2023 (2nd), source of the stack-based Bug Nav: https://battlecode.org/assets/files/postmortem-2023-gone-fishin.pdf
- GST bot code: https://github.com/uravt/Battlecode26

*Access note:* battlecode.org and github.com timed out from the sandbox's curl, so the PDF was fetched with WebFetch, which saved the binary, and copied byte-for-byte into raw/. raw.githubusercontent.com was reachable and was used only to read two small repo files as data.
