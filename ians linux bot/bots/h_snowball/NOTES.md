# h_snowball: c2_respawn + an unseen-shooter rule (Q29, early-fight snowballs)

**Lineage.** `python3.12 tools/newbot.py c2_respawn h_snowball`, then
`python3.12 -I matches/snow-tools/patch_snowball.py bots/h_snowball/src/bot.py` (iteration 1, every
piece on), then iteration 2 switched ghosts and zones off (`SNOW_GHOSTS = False`, `SNOW_ZONES = False`;
the beacon follows `SNOW_ZONES`) after the ablation below. Only `src/bot.py` differs from c2_respawn
(final md5 `c86c506429b4f092fae5d1b57b4bddfc`); `main.py`, `draft.py` and `randomness.py` are
byte-identical. Report: `results/experiments/2026-11-01-h_snowball.md`.

## Why
Fuel-free traces (`cambc.debug_block`) of c2_respawn and c2_3pick against tb_merge_b on the
3-pick snowball map-sides (00breadcrumbs A/B, 00fragment B, 00packs A, 01gold-rush B, 02the-pond B):
86 deaths of c2 in 6 games, 56 of them to the game's top killer.
- **Unseen fire (22 of 86 deaths, plus 13 flicker deaths).** An enemy in a bush (from outside you
  cannot see into a bush) shoots a champion that sees nothing: no enemy in sight and no camp in range,
  so the bot keeps farming, or (below 45% HP) starts a recall, which the next hit cancels.
- **Bush-edge flicker.** The champion sees the enemy, steps back, loses sight, resumes farming,
  steps back in, and is hit again. The next ally then walks into the same bush (00fragment B: a
  495-Str, 5,760-HP Vesper killed all three of ours in 20 rounds at one tile).
- 32 of the 86 deaths were within 6 tiles of the same champion's previous death tile.

## What is on (`SNOWBALL = True`; keyed on observed state, never on names)
| Piece | Rule | Final |
|---|---|---|
| Unseen shooter | HP lost since our last turn, with no enemy visible, no awake camp in range now, and more than the camps that could reach our last tile explain (+10): a `Ghost(-1)` on the nearest hidden standable tile within 4 (bush first), strength = the HP lost, range 3, kept 2 rounds. It joins `enemies` / `incoming`, so threat, retreat, `recall_safe` and danger retreat see it; it is never engaged or hit | **on** |
| Memory | `threats_fast` stores every visible enemy's (round, tile, range, strength, health, focus) in `self.emem` | off (only with ghosts or zones) |
| Ghosts | A remembered enemy not visible now, seen within 8 rounds, last tile within 8 of us and not visible to us, and stronger than us 1v1 (`hp x (str + 0.15 focus)` >= 1.3 x ours) | off (`SNOW_GHOSTS`) |
| Dominant zones | An enemy seen within 24 rounds with `hp x dps` >= 2.5 x our max-HP x dps: tiles within its range + 3. `choose_target` x0.2, `pick_altar` +20, farming routes avoid it | off (`SNOW_ZONES`) |
| Beacon | Shared bytes 5-6: the last dominant enemy any ally saw (teams <= 5); allies add a radius-6 zone | off (with zones) |
| End of turn | `snow_end()` (after the step-off) records HP and the camp damage that can reach our tile | on |

## Ablation (all 140 maps; vs c2_respawn / vs tb_merge_b; enemy champions with >= 8 kills and <= 1 death vs tb_merge_b)
| Build | vs c2 | vs tbm | snowball champs vs tbm |
|---|---|---|---|
| c2_respawn (baseline) | (70 mirror) | 98 | 16 |
| iteration 1: unseen + ghosts + zones + beacon | 61 | 108 | 4 |
| `snow_u`: unseen only | 79 | 109 | 14 |
| `snow_ug`: unseen + ghosts | 76 | 102 | 11 |
| `snow_uz`: unseen + zones + beacon | 75 | 99 | 9 |
| **final h_snowball (unseen only)** | **75** | **107** | 14 |

## Constants
`UNSEEN_TTL 2, UNSEEN_R 4` (on); `GHOST_TTL 8, GHOST_RATIO 1.3, ZONE_TTL 24, ZONE_RATIO 2.5, ZONE_PAD 3,
ZONE_TARGET_MULT 0.2, ZONE_ALTAR_PEN 20, BEACON_BYTE 5, BEACON_R 6` (only with the switches on).
With `SNOWBALL = False` the logic is c2_respawn's (a few extra bytecodes remain).

## Debug builds (never submit)
- `bots/dbg_snow_tr` = c2_respawn + `matches/snow-tools/patch_trace.py`; `bots/dbg_snow3_tr` = c2_3pick + the same.
- `bots/dbg_snow_h1` = iteration 1 + trace; `bots/dbg_snow_f` = the final h_snowball + trace.
- Per-turn `T round champ x y hp maxhp str gems [enemies] i<incoming> tags`; ghosts print as
  `G<handle>@dist:hp:str`, the unseen shooter as `G-1`. Runner: `matches/snow-tools/trace_batch.py`.
- Ablation bots `snow_u`, `snow_ug`, `snow_uz` (iteration-1 code with constants disabling pieces).
