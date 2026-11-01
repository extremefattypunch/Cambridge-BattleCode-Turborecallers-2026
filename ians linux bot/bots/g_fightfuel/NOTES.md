# h_fightfuel: Q13, fuel budgeting in fights (from tb_merge_b)

**Hypothesis (STRATEGIES Q13).** In the 70-map check, tb_merge_b's losses averaged 183 fuel exhaustions and its wins 69. Suspended turns during fights should lose fights. So we cap or cache the expensive fight code, and fights should then never suspend.

The game logic is unchanged. Every new routine was checked against the original side by side (see "Validation"). The only differences in behaviour are the ones that follow from having more fuel left:
- fewer suspended turns;
- fuel-dependent branches such as `FUEL_SCORE_FLOOR` and `build_static_fields` take the other path;
- two new low-fuel early exits.

## Profiling (what costs fuel)
`PROF = True` in `src/bot.py` turns on a per-section profiler. It records `pm(label)` checkpoints in `play_turn`, `handle_enemies` and `main.py`. The prints use `debug_block`, so they cost no fuel in debug builds. A turn is printed when it used 1.5M or more, or when it was suspended. A checkpoint whose fuel went *up* marks a suspension inside that section.

The first profiling run was the original code against sf_bank (`matches/h_fightfuel-prof`). The runs use these maps because they had the most exhaustion in the 70-map check.

**Most exhaustion is not in fights.** It is a per-turn baseline that runs every turn:
- `observe()` costs 0.5-1.3M per turn and `threats()` 0.6-1.3M. Both read every visible camp through the API, including the camps seen through the ward. That is about 5 API calls of about 3k each, per camp.
- On 02the-pack, one champion was over budget on about every second turn for the whole game: 1,410 suspensions inside `tribute` and 2,057 of 2,362 with no enemy in sight.
- The 70-map loss average is driven by three such steady loops: 02the-pack A 922, 01yellow-brick-road B 867 and 01boss-battle A 357.

**The fight-specific costs:**
- `retreat()` costs 0.4-2.3M. Its `danger(t)` re-reads each enemy's position, range and strength for every candidate tile (up to 25 with a dash). It also loops over every awake camp and every spawn tile.
- `cast_combat` costs up to 1.6M. HoR's landing dash and Ryth's area aim call `kit_units()`, which reads *every* visible camp.
- The `reset_target` fallback also scans every visible camp.
- On 01yellow-brick-road, Vesper sat in a 1000-round standoff, retreating while suspended about every 3rd turn: 83% of the suspensions there had enemies in sight.

## Changes (each behind a switch at the top of `src/bot.py`)
| Switch | Change |
|---|---|
| `OBSERVE_FAST` | `observe_fast`: a visible spawn tile with no camp gives 0 HP, as before. A camp on the tile gives its `health()`. The presence test uses the `vision.camp_tiles()` bitboard, so it is 1 API call per camp instead of about 5. |
| `THREATS_FAST` | `threats_fast`: only awake camps, taken from `vision.awake_camp_tiles()` (asleep camps never hit). The camp range is cached per spawn tile. Each visible enemy's (position, range, strength) is read once and cached for the turn in `self.esrc`. |
| `RETREAT_FAST` | `retreat_fast`: the same 4-key ordering as before. It uses the cached enemy data and only the camps that can matter. A camp counts if its range can reach a candidate within 2, or if it can be the minimiser of the camp-margin key, which keeps that key exact. Each candidate is scored once, and the spawn distance is memoised across turns. The dash search is skipped below `FUEL_RETREAT_DASH` (350k left). |
| `KIT_FAST` | `kit_units_fast`: only units within (cast range + radius), which are the only ones that can be hit. Camps are classified with the awake and asleep bitboards. `reset_target_fast` reads only the units inside our attack tiles. Area aim and HoR's landing dash are skipped below `FUEL_KIT_AIM` (400k left). |

`VALIDATE = True` runs the old and new versions side by side and prints any mismatch. Use it together with `cambc run ... --fuel 25000000`: without spare fuel, the suspended turns make the comparison stale.
- **Result:** 0 mismatches in observe, threats, retreat, kit_units and reset_target.
- **Coverage:** 4 maps × 800 rounds (00crater, 01yellow-brick-road, 00lanes, 02the-pack).

`main.py` prints a traceback after `bot error` only when `Bot.debug_tb` is set. It is off.

## Fuel effect
Re-profiling the same three maps against sf_bank (`matches/h_fightfuel-prof2`), suspensions per game went:
| Map | Before | After |
|---|---|---|
| 02the-pack | 2,466 | 2 |
| 01yellow-brick-road | 899 | 145 |
| 00lanes | 1,127 | 44 |

These are the average fuelExhausted per game in the evals (A = h_fightfuel, B = tb_merge_b, in the same games):
| Eval | h_fightfuel | tb_merge_b |
|---|---|---|
| sprint | 6.7 | 71.2 |
| high-exhaustion map set | 13.9 | 221.0 |

## Results
See `results/experiments/` once the analyst writes them up. The raw lines are in `matches/h_fightfuel-*.log`.

## Remaining hotspots (not in this candidate's scope)
- **01islands** still has 74-100 suspensions per game. They are in `choose_target` (2.0-2.3M) with no enemy in sight. `FUEL_SCORE_FLOOR` only breaks once a best target exists.
- **00vault** still has about 110. It shows 30-47 awake camps. The costs are:
  - `threats` about 0.8M, at 1 camp_at + strength call per awake camp;
  - farming `avoid` and `pick_camp_in_range` about 0.8M;
  - `cast_combat` about 1M;
  - `retreat` 1.8-2.3M, from many camps × 25 dash tiles.

  An adaptive dash floor (cost estimate = tiles × sources) and inlining `cheb` in `danger()` would fix the retreat part.
