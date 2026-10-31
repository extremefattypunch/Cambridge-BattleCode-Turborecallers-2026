# Om Nom - "Money Is All You Need" - Battlecode 2025 Postmortem

- **URL:** https://battlecode.org/assets/files/postmortem-2025-om-nom.pdf
- **Raw:** ../raw/postmortem-2025-om-nom.pdf
- **Event:** MIT Battlecode 2025 (paint-coverage game)
- **Team / placement:** Om Nom (Cyril Sharma, Egor Gagushin; Purdue). **3rd place at Finals 2025, after winning the US Qualifiers.** They also placed 5th in 2023 and 4th in 2024.
- **Same game as cambc 2026a?** No

## Game summary
Same 2025 paint game: money and paint resources; soldiers, moppers and splashers; paint, money and defense towers; SRP boost patterns; first to 70% paint wins (or eliminate all enemy units).

## Lessons

### Strategy (big wins came from replay review, not new algorithms)
1. **Don't retreat unconditionally at a resource threshold.** Their soldiers went home at about 50 paint even when they were next to an enemy tower with ~10 attacks left. Making them finish the kill, tower or pattern before going home was a huge win.
2. **Small inefficiencies add up.** Paint penalties they had dismissed as minor turned out to matter. Saving a little paint means a few more attacks, which can decide games. They added a greedy path tiebreak for cheap tiles.
3. **Stay robust to losing a key structure.** They inferred the hidden count of paint towers from public income (see Compute) and rebuilt one when the estimate hit 0.
4. **Let units "live useful lives".** They fixed target-flip-flopping bugs, where a unit switched between targets or repainted the same tile in different colours.
5. **Add some aggression** even as an economy team: an early rush that builds along the way, ruin tainting, and splashers sent toward the enemy via symmetry.
6. **Defend against rushes** by spawning cheap anti-rush units aimed at the incoming attackers.
- **Resource conversion** ("tower nuking"): they had been losing games while sitting on huge money. Converting surplus money into the scarce resource (paint) by destroying and rebuilding a third of their money towers fixed the balance. They once spent 13k money in under 60 rounds and went from 8 units to 23.
- They studied a rival's rush in detail, then dropped it at the last minute because it was high-variance: crushing when it worked, a near-certain loss when it didn't.

### Micro / combat
- **XSquare-style micro, unrolled:** compute per-candidate-square stats for the 9 move options, then pick the best through a chain of tiebreakers (net damage first, then terrain penalty). Soldiers weave in and out of tower range for 2 hits per 1 taken.
- Unit-specific tweaks: moppers don't back off when there are no enemy moppers (so they can chase), and never leave friendly terrain to chase, because they die fast off it.
- They inlined the micro (no objects, no `this` loads) so it was cheap enough to need no bytecode checks.

### Macro / economy
- **Unit production:** time-sliced production (only certain unit types on certain rounds) was bad. They switched to **"pick the next unit, save for it, then build it"**, which keeps a fixed composition ratio. They were rarely money-bound after the opening.
- SRP placement: any soldier may start one centred on itself if it doesn't conflict with towers, farms or other SRPs and no enemies are seen. On completion it adds the candidates 4 tiles away in each cardinal direction to a to-try list. This gives the benefits of a fixed tiling while adapting to the map.

### Pathfinding ("Optimal Bug")
- Each turn, (1) advance a **BugTarget** a few steps along a bug path that treats units as passable, stopping at the vision edge. (2) Run a **bitmask BFS backwards from the BugTarget** over the vision window. (3) Among the neighbours that reduce BFS distance, choose by a heuristic (distance plus terrain penalty).
- This keeps bug's guarantee of reaching the goal, avoids bug's wall-hugging inefficiency and its breakage when units block, and costs only ~1.5k bytecode because the BFS uses bitmasks.
- Bug fixes that mattered: don't walk the map edge, and don't keep changing the target (it reset bug state and stalled progress).

### Communication
- They used almost no explicit comms: just **3 bits for symmetry**. Everything else went through map markers (patterns encode "paint tower", "money tower", "farm", "SRP centre").
- A two-way handshake for tower nuking was considered, but simple local heuristics were good enough.

### Compute / bytecode
- **Don't go over budget on a unit's first turn.** Every new unit allocated a big array and overran its first turn. The early game snowballs, so fixing this alone gave a substantial win rate against their old bot.
- **Infer hidden state from public numbers:** track the change in money over 10 turns and take the max to get the true income. Income = (20 + 3·SRPs)·moneyTowers almost uniquely determines the number of SRPs and money towers, so paint towers = total towers minus money towers. Lookup tables were generated at build time.
- **Bitmask map:** the whole map is stored as 60 `long` rows per feature (walls, ruins, seen), plus mirrored masks. A symmetry check compares entire rows at once (~9x faster, ~1k bytecode, and exhaustive).
- **Jinja templating for code generation:** write unrolled loops, macros and debug prints in templates instead of hand-written generator scripts. Seeds are passed through the build.

### Testing & dev workflow
- A slow first week: they didn't upload for days and didn't know the meta. **Upload early.**
- They compared against old versions continuously. On the final submission day they went from 0-10 to about even against the top two after the last fixes.
- They kept a "bug" (money towers built only splashers late game) because fixing it made results worse. Trust the measurements.
- Tournament maps can differ from ladder maps. Their Elo jumped about 100 when the tournament maps were added, because their bot suited complex, long-rush maps.

### Mistakes / regrets
- Their exploration was just random targets. Several fancier schemes didn't help, and good local heuristics compensated.
- They hard-coded the initial SRP pattern and suffered when a patch changed it.
- They didn't use defense towers ("but maybe should have"), and the winner did.

## Transfer to cambc 2026a
- Commit-to-finish rules: don't recall or leave a camp, capture or tribute mid-way when a few more turns would finish it.
- Python fuel: keep the first play turn and any spawn-time setup under budget, or the bot is suspended and acts on stale data. Precompute in the draft turn (100x fuel) and store results in the 1024-byte draft memory.
- Infer hidden enemy or team state from public numbers (e.g. the gold and gem counters) instead of spending shared memory on it.
- Production analogue: choose the next shop purchase target and save for it, rather than buying whatever is affordable.
- Pathing: BFS over a local window toward a bug-advanced waypoint, with a terrain or danger-weighted tiebreak (bushes, camp aggro range).
