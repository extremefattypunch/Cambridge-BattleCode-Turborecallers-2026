# sf_maps: changes vs sf_base

Assignment: INSIGHTS item 11 (map archetypes), item 10 (single capture recipient) and item 13 (scoring multipliers).
Everything uses map *contents*, never map names.

## Files
- `src/mapprofile.py` (NEW). This module runs the draft-phase map analysis and holds the draft-memory codec.
- `src/draft.py`. `submit_profile()` replaces the old `draft_memory.submit(b"tb_splitfarm v1")`. The profile is computed once per draft process.
- `src/bot.py`:
  - one `import mapprofile`;
  - a block of constants after `DEBUG`;
  - about 10 small hooks, each marked with `# sf_maps`;
  - a new section of helper methods at the end of `class Bot` (`# ==== sf_maps additions`).

No existing code was renamed, reordered or reformatted.

## 1. Map profile in the draft (item 11)
`mapprofile.compute()` runs during the draft, with the full map visible and about 250M fuel.

**Memory layout:** 64 bytes, zero-padded to 1024 by the engine:
- `[0]` MAGIC 0xA7
- `[1]` VERSION 1
- `[2]` flags
- `[3]` jackpot group index
- `[4]` herd group index
- `[5]` k, followed by k gate group indexes
- `[22]` m, followed by m enclosed group indexes

Champions read it in `init_static` → `maps_init()`, using `mapprofile.load()` (`cambc.DraftMemoryBuffer()`). If MAGIC or VERSION is wrong, the profile is `None` and the bot behaves exactly like sf_base.

**Flags:**
- **JACKPOT:** one group holds ≥60 gems and ≥35% of the map's gems, and is harmless (or isn't a herd).
- **BRAWL:** jackpot plus ≥50% of the map's gems.
- **HERD:** the top group is harmful with ≥8 camps or ≥15k HP.
- **GATED:** the altar ring is reachable with camps passable but not with camps blocking. The gate groups are the groups whose removal opens a ring tile.
- **ENCLOSED:** a group is walkable but walled in by other camps.

**Detected locally (correct on every map checked):**
- 02guardians: GATED, gates = the two monoliths beside the altar.
- 01boss-battle: GATED + ENCLOSED, gate = a 2-monolith group with 400 strength.
- 00the-line: JACKPOT + BRAWL, 23 gem clusters holding 161 gems.
- 00vault: JACKPOT + BRAWL, 49 clusters holding 343 gems.
- 00crater: JACKPOT.
- 00stampede: HERD, 6 elks wrapped in 14 clusters, 360 strength.
- 00monolith, 00anvil, 02famine, 01starvation, 01gold-rush, 01concentrated-wealth, 00gemfight, 01elk-arena: HERD.
- No flags on 00lanes, 02arena, 01islands, 01big-world, 02harvest, 00corners, 00quadrants, 02the-pond or adgato-gemcombat3.

## 2. Gated altars: hoard, then assault the gate as a team
- **Tribute decision:** when `self.gated`, tribute only if the gate is open (`gate_closed()` checks that the altar ring minus the known-alive camp tiles is empty). This removes the sf_base failure where carriers walked to a monolith tile and stood there for the rest of the game. When the gate is open, every carrier banks immediately.
- **`update_assault()`:** from round 150 (`GATE_ROUND`), or once a champion carries ≥40 gems (`GATE_GEMS`), every champion targets the same gate group. The choice is the damaged gate first, then the one nearest our spawn. A gate is only assaulted if its strength is ≤250 (`ASSAULT_MAX_STR`).
- **`assault_turn()` micro:**
  - **Local damage model** (`nearest_incoming`): an awake camp only hits the nearest champion.
  - **Retreat rule:** retreat when HP ≤ inc × (steps + 1) + 80. Steps drop to 1 when a healthy ally is within distance + 1 of the camp, because that ally takes over the aggro.
  - **Gathering:** wait outside range until min(3, alive) allies are within rng + 5, for at most 60 rounds.
  - The sf_base danger check is skipped while the local model says we are safe (`assault_safe`).
- **`engage_ratio()`:** near the gate, fight enemy champions at a ttk ratio of 1.2 instead of 0.8. sf_base carriers park in the gate corridor and block the siege.
- **Anti-stall:** if a champion's position and HP haven't changed for 50 turns during an assault, it pauses the assault for 100 rounds and farms instead (`STALL_TURNS` / `STALL_PAUSE`).

**Measured** (single games and the archetype A/B, vs sf_base):
- **02guardians as side A:** we won 500-18, 419-0 and 555-0 (sf_base never tributes there).
  - As side B it is still 0-0 and lost on gold. Enemy carriers stand in the 3-wide corridor and our side ends up in a standoff. sf_base self-play also loses side B there (0-0 on gold).
- **01boss-battle, first version with no strength cap:** **110 deaths**, from sieging 40k HP / 400 dmg.
  - With the cap there is no assault, 0 deaths, and we hoard and farm: gold 7818 vs 250 in one game (won on tiebreak). It was 0-0 on both sides in the A/B.

## 3. Jackpot: contest as a team
- **`choose_target`:** a jackpot group claimed by allies gets ×1.5 (`JACKPOT_BOOST`) instead of sf_base's ×0.3 spreading discount. The whole team goes there.
- **`engage_ratio()`:** inside dilate(jackpot tiles, 4), engage enemy champions at a ratio of 1.2 instead of 0.8.

**Measured:**
- **00the-line as side A:** 1078-0, 1147-0 and 1054-0.
  - As side B: 0-1002 and 0-1143. sf_base self-play is also 1159-0 for side A, so this is map/side bias, not our change.
- **00vault as side A:** 343-0 twice without the engage ratio, and 1037-0 with it.
  - As side B: 0-0, with **both** teams frozen at 53 gold. sf_base does the same; not investigated.

## 4. Single capture recipient (item 10): implemented but **OFF** (`CAPTURE_SINGLE = False`)
`capture_skip()` is called from `choose_target`. A group in reward-available state with another ally already standing on its spawn tiles is skipped, so the other champions move on to the next job.

**Measured:** with it ON, the quick A/B went **6W-18L**. With it OFF, the same maps play as an exact mirror of sf_base (see "Determinism" below). Shipped OFF.

## 5. Scoring multipliers (item 13): implemented but **OFF** (`SCORE_MULT = False`)
`score_mult()` combines three things:
- **Gold weight by round:** 0.25 / 0.15 / 0.08 at rounds <300 / <800 / later.
- **Enemy half:** ×0.6 before round 250 and ×0.85 after, for groups nearer the enemy spawn.
- **Recent danger:**
  - ×0.6 for ≥2 own sightings of enemies within 7 tiles in the last 40 rounds, or ×0.85 for one;
  - ×0.5 within 8 tiles of one of our own deaths in the last 120 rounds.

**Measured:**
- Sprint (40 games) with SCORE_MULT ON and CAPTURE_SINGLE OFF: **14W-26L**.
- Sprint with both OFF: 20W-20L.

Shipped OFF.

## Determinism (important for whoever merges)
The engine plus these bots are **deterministic**. Re-running an identical bot gives identical results per map and side.

With both switches OFF, most non-archetype maps replay as an exact mirror of sf_base (00anvil A 1009-21 / B 21-1009, and so on). A W-L of 50% therefore means "behaves like sf_base", and any small per-turn change, including extra fuel use, flips chaotic maps. Self-play W-L differences on non-flagged maps measure chaos as much as quality.

Exception: fuel-heavy maps (01islands, 01big-world, 00lanes, 00quadrants, 02harvest) vary between reruns, probably through fuel-exhaustion timing.

## Final A/B (sprint, 40 games): `SUMMARY sf_maps vs sf_base: 21W-19L (52%)  avg gems 457 vs 467  avg deaths 15.1 vs 13.6  botFaults(A) 0`
- **Metrics:**
  - mean tribute 20.5;
  - deaths_by_camp 2.6/game;
  - gemsLost_to_champion 50.7/game;
  - fuelExhausted 300/game.
- An identical-code rerun (as `../matches/sf_maps-scratch/v3`) gave 20W-20L. It differs only on the fuel-heavy maps listed above.

**Archetype maps in the sprint set:**
- **02guardians:** lost both sides, 0-215 and 0-200. Our siege softened the monolith and sf_base's carriers, parked at the corridor, got the tribute window. Other runs of the same feature gave 555-0, 500-18, 419-0 and 874-0 as side A, so it is high-variance.
- **00stampede:** 1-1 (mirror).
- **00crater** (jackpot): 1-1, 0-0 both sides.

**Earlier archetype A/B** (`--maps 02guardians,00stampede,01boss-battle,00the-line,00vault,00monolith`, without the stall guard):
- 5W-7L. Side A won the-line, vault and guardians; side B is map-biased on the-line and vault.

**Cross-check vs tb_economy (quick):** **21W-3L (88%)**, against 18W-6L (75%) for sf_base (from `matches/sf_pvp-baseline-xeco.log`). That run had CAPTURE_SINGLE ON.

## Tried and rejected (code present but disabled, or not shipped)
- **Herd assault on our-half boss groups** (00monolith: a monolith plus 8 clusters holding 256 gems): lost 164-1007 with 39 deaths. It is disabled via `HERD_ROUND = 99999`.
- **Siege of a gem-starved herd** (00stampede: the herd holds 100% of the gems, 360 strength): 0-0, with 19 and 46 deaths and gold 486 vs 12272. Not shipped; the scratch copy is in `matches/sf_maps-scratch/hd`.

## Independent / optional parts of the patch
- **Draft profile:** `mapprofile.py` plus the `draft.py` change. It is a pure addition, and other features can read `self.prof` flags.
- **Gate logic:**
  - the `self.gated` lines in the tribute decision;
  - `gate_closed()` in the `G is None` branch;
  - `update_assault`, `assault_turn` and `assault_pick`;
  - the `assault_safe` guard on the danger block.
- **Jackpot:** the `JACKPOT_BOOST` branch in `choose_target` and `engage_ratio()`. The `engage_ratio` hook also serves the gate.
- **Capture skip:** one line in `choose_target` plus `capture_skip`/`ally_on`.
- **Score multipliers:** one line in `choose_target` plus `score_mult`. Currently a no-op.

## Merge notes
- **`choose_target` is touched in 4 places:**
  - assault early return at the top;
  - capture skip at the top of the loop;
  - jackpot branch replacing `if c:`;
  - `score *= self.score_mult` after the hysteresis.
- **`play_turn` is touched in 4 places:**
  - `maps_dead` in the dead branch;
  - the archetype hook block before `# ---- danger handling`;
  - the `self.gated` override of `go`;
  - the `G is None` tribute guard.
- **`handle_enemies`:** only the `0.8` constant is replaced, by `self.engage_ratio(me)`.
- **`init_static`:** `self.maps_init(me)` before `self.inited = True`.
- **Shared memory is not used.** The draft-memory format is owned by `mapprofile.py`. If another patch also writes draft memory, merge both payloads into one buffer (keep byte 0 = 0xA7 and byte 1 = version) or move ours to an offset.
