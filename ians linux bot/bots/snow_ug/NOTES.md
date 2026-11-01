# h_snowball: c2_respawn + an enemy threat memory (Q29, early-fight snowballs)

**Lineage.** `python3.12 tools/newbot.py c2_respawn h_snowball`, then
`python3.12 -I matches/snow-tools/patch_snowball.py bots/h_snowball/src/bot.py` (the patch script is
the exact, reproducible diff). Only `src/bot.py` differs from c2_respawn; `main.py`, `draft.py` and
`randomness.py` are byte-identical. Report: `results/experiments/2026-11-01-h_snowball.md`.

## Why
Fuel-free traces (`cambc.debug_block`) of c2_respawn and c2_3pick against tb_merge_b on the
3-pick snowball map-sides (00breadcrumbs A/B, 00fragment B, 00packs A, 01gold-rush B, 02the-pond B)
showed that about 40% of our deaths came while the killer was **invisible** to us:
- **Unseen fire.** An enemy in a bush (from outside you cannot see into a bush) shoots a champion
  that sees nothing: no enemy in sight and no camp in range, so the bot keeps farming, or (below
  45% HP) starts a recall, which the next hit cancels, and starts it again every turn until death.
- **Bush-edge flicker.** The champion sees the enemy from inside the bush, steps back (retreat),
  loses sight, resumes farming, steps back in, and is hit again: a 2-cycle that ends in death.
  The next ally then walks into the same bush (00fragment B: a 495-Str, 5,760-HP Vesper killed
  all three of ours in 20 rounds at one tile).
The fed carry (Vesper 10/0 to 21/0) is the result: each such kill gives it 100+ gold and the bag.

## What changed (`SNOWBALL = True`; every rule keys on observed state, never on names)
| Piece | Rule |
|---|---|
| Memory | `threats_fast` stores every visible enemy's (round, tile, range, strength, health, focus) in `self.emem` |
| Unseen shooter | HP lost since our last turn, with no enemy visible, no awake camp in range now, and more than the camps that could reach our last tile explain (+10): a `Ghost(-1)` on the nearest hidden standable tile within 4 (bush first), strength = the HP lost, range 3, kept 2 rounds |
| Ghosts | A remembered enemy not visible now, seen within 8 rounds, last tile within 8 of us and **not visible to us** (if we can see its tile it has left), and stronger than us 1v1 (`hp x (str + 0.15 focus)` >= 1.3 x ours) |
| Use of ghosts | Added to `enemies` (and to `incoming` within their range + 1): they count in `handle_enemies` threat, group balance, retreat danger, `recall_safe`, danger retreat. They are never engaged, struck or hit (`isinstance(e, Ghost)` skips in the engage loop, `adjacent_melee`, `hit_while_leaving`) |
| Dominant zones | An enemy seen within 24 rounds with `hp x dps` >= 2.5 x our max-HP x dps: tiles within its range + 3. `choose_target` x0.2 for groups touching a zone, `pick_altar` +20 for altars inside, farming walks route around it (`avoid`) |
| Beacon | Shared-memory bytes 5-6 carry the last dominant enemy any ally saw this turn (4-bit stamp = round / 4, x / 2, y / 2); allies add a radius-6 zone for 24 rounds. Only for teams of <= 5 (claim slots 0-4); `read_claims` then reads bytes 0-4 only. A stale value is cleared by the first reader (the stamp wraps every 64 rounds) |
| End of turn | `snow_end()` (after the step-off) records HP and the camp damage that can reach our tile |

## Constants
`GHOST_TTL 8, GHOST_RATIO 1.3, UNSEEN_TTL 2, UNSEEN_R 4, ZONE_TTL 24, ZONE_RATIO 2.5, ZONE_PAD 3,
ZONE_TARGET_MULT 0.2, ZONE_ALTAR_PEN 20, BEACON_BYTE 5, BEACON_R 6`.
With `SNOWBALL = False` the logic is c2_respawn's (a few extra bytecodes remain).

## Debug
`bots/dbg_snow_h1` = h_snowball + `matches/snow-tools/patch_trace.py` (per-turn `T` lines; ghosts
print as `G<handle>@dist:hp:str`, the unseen shooter as `G-1`). Debug-only; never submit it.
