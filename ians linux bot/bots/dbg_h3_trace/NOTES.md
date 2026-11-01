# h_3pick: hypothesis Q18 (3-pick maps), from tb_merge_b

**Final state:** `LOCK_MEMORY_FIX = True` (on all maps) and `TRIO_MODE = False`.
The trio-mode code is still in `bot.py`, gated by the flag, so the two tested versions can be re-run.
`draft.py` and `main.py` are identical to tb_merge_b.

## Local 3-pick maps (team size from the draft length in kept stats)
00anvil, 00breadcrumbs, 00collision, 00fragment, 00packs, 01broken-curve, 01gold-rush, 01the-farm,
02arena, 02the-pack, 02the-pond, adgato-gemcombat1 (12 maps, 24 games per opponent).

## New imitation opponents (draft PRIORITY only, rest = tb_merge_b)
- `bots/h3_tvv`: Tavi, Varg, Vendetta (the real 01broken_curve loss to "Blame the Altar").
- `bots/h3_csv`: Cassi&Issac, Stellar, Vesper (fa_kyuu, the 02the_pack loss).
- Varg, C&I, Stellar is the existing `imit_test`.

## What changed

### 1. Lock-memory fix (kept): `pick_altar` skips altars remembered as enemy-locked
**Bug in tb_merge_b.**
- `pick_altar` skipped an enemy-locked altar only while the lock was *in vision*.
- `do_tribute` remembers locks (`locked_altars()`), but lets `pref`, the ring of the altar `pick_altar` chose, override the free ring.
- So when a locked altar was just out of sight, this 2-cycle repeated forever:
  1. `pick_altar` chose the locked altar, because it was near.
  2. The carrier stepped toward it, and the lock came into view.
  3. Next turn, `pick_altar` chose the far altar.
  4. The carrier stepped away, lost sight of the lock, and went back to step 1.

**Traced cases** (debug runs, turn traces in the session log):
- 01broken-curve B vs imit_test: all three carriers held 22/44/44 gems unchanged from r1000 to r1375. Then Varg killed all three within 13 rounds (110 gems lost), and we lost 381-1013.
- 02the-pond A: Marcella held 42 gems for 1644 rounds, and we lost 15-77.

**Fix:** `pick_altar` first refreshes `locked_altars()`, then skips remembered locks.
Smoke test: both games flip, to 1183-525 and 262-91.

**Mechanism check** ("frozen carrier": at least 15 gems held unchanged for 150+ rounds while alive):
| Opponent | Champion-rounds before | After | Change |
|---|---|---|---|
| imit_test | 18234 | 15385 | -16% |
| h3_tvv | 17118 | 11798 | -31% |
| h3_csv | 17694 | 14075 | -20% |

Games affected went from 29 to 21 of 72. Most of the remaining stretches are on 02the-pack, where the only altar sits inside a camp ring and nobody can tribute.

### 2. Trio mode (Q18 behaviour), rejected in both versions
Active only when `len(champions(ALLY)) <= 3`. It uses shared-memory bytes 3-6, which are free with 3 bodies, as an alert: x, y, round, info.

- **v1:**
  - Any champion that sees enemies writes an alert.
  - A free ally converges on it if it is within 12 tiles, has HP of at least 55%, carries fewer than 30 gems, is not in a camp fight or capture, and is in the same walk component.
  - When outnumbered (visible enemies > us + allies within 6), the engage limit is capped at 0.55 for non-channelling targets.
  - Enemies at 7-8 tiles add 0.5× their dps to the fight model.
  - A death alert stops allies converging on that spot.
- **v2 (T3):** v1, changed after a turn trace of 00anvil B vs h3_tvv.
  - **What the trace showed:** 2v2 groups "danced" for 15+ rounds without trading. Engage and retreat flipped every turn as allies and enemies crossed the 6-tile radius, and the outnumbered flag toggled with them.
  - **Commitment:** a target we engaged stays engaged for 4 turns unless we are clearly losing on it.
  - **Ally counting:** allies within 8 count for the numbers check, and within 6 for strength.
  - **Retreat:** ties are broken toward visible allies.
  - **Assist:** only alerts flagged ENGAGE are answered, and only within 10 tiles.

**Why it failed:**
- v1 converged on sightings almost constantly on small 3-pick maps. In its losses our first tribute came at r249, against r121 in its wins. The enemy out-farmed us and snowballed items (their Tavi went 11/0 on 02arena).
- v2 fixed 00anvil vs h3_tvv (deaths 25→4 and 24→16, both sides now won). But it collapsed elsewhere: 00fragment A vs tb_merge_b had 42 deaths. Average deaths rose, and the mirror got worse.

### 3. 3-pick draft change: not tested (the evidence goes against it)
Per-champion stats on the 3-pick sets show:
- **Vendetta** is our top killer and top submitter.
- **Marcella** dies most, but she is the stun-immune frontline.

Swapping either for Ryth isn't supported by this data. An earlier similar swap (T12, Varg for HoR) was neutral.

## Evaluation (all kept: `matches/h_3pick-*`)
"Base" is tb_merge_b vs the opponent; the rest are h_3pick vs the opponent.

| Opponent | Base | Lock fix (L) | Trio v1 (T) | Trio v2 (T3) |
|---|---|---|---|---|
| tb_merge_b (mirror, 50% = no change) | — | **13W-11L (54%)** | 7W-17L (29%) | 11W-13L (46%) |
| imit_test (Varg, C&I, Stellar) | 20W-4L (83%) | **21W-3L (88%)** | — | — |
| h3_tvv (Tavi, Varg, Vendetta) | 16W-8L (67%) | **19W-5L (79%)** | 14W-10L (58%) | 20W-4L (83%) |
| h3_csv (C&I, Stellar, Vesper) | 22W-2L (92%) | **23W-1L (96%)** | — | — |

Exact SUMMARY lines:
```
SUMMARY tb_merge_b vs imit_test: 20W-4L (83%)  avg gems 786 vs 242  avg deaths 2.5 vs 32.3  botFaults(A) 0   [matches/h_3pick-base-imit_test]
SUMMARY tb_merge_b vs h3_tvv: 16W-8L (67%)  avg gems 673 vs 408  avg deaths 6.4 vs 15.9  botFaults(A) 0      [matches/h_3pick-base-h3_tvv]
SUMMARY tb_merge_b vs h3_csv: 22W-2L (92%)  avg gems 825 vs 329  avg deaths 3.3 vs 32.0  botFaults(A) 0      [matches/h_3pick-base-h3_csv]
SUMMARY h_3pick vs tb_merge_b: 13W-11L (54%)  avg gems 674 vs 576  avg deaths 10.0 vs 12.2  botFaults(A) 0  [L, matches/h_3pick-L-3p-tb_merge_b]
SUMMARY h_3pick vs imit_test: 21W-3L (88%)  avg gems 832 vs 234  avg deaths 2.2 vs 33.4  botFaults(A) 0    [L, matches/h_3pick-L-3p-imit_test]
SUMMARY h_3pick vs h3_tvv: 19W-5L (79%)  avg gems 747 vs 417  avg deaths 6.1 vs 17.6  botFaults(A) 0       [L, matches/h_3pick-L-3p-h3_tvv]
SUMMARY h_3pick vs h3_csv: 23W-1L (96%)  avg gems 837 vs 342  avg deaths 3.5 vs 32.8  botFaults(A) 0       [L, matches/h_3pick-L-3p-h3_csv]
SUMMARY h_3pick vs h3_tvv: 14W-10L (58%)  avg gems 603 vs 492  avg deaths 8.4 vs 14.6  botFaults(A) 0      [T, matches/h_3pick-T-3p-h3_tvv]
SUMMARY h_3pick vs tb_merge_b: 7W-17L (29%)  avg gems 459 vs 698  avg deaths 12.5 vs 10.1  botFaults(A) 0   [T, matches/h_3pick-T-3p-tb_merge_b]
SUMMARY h_3pick vs h3_tvv: 20W-4L (83%)  avg gems 752 vs 405  avg deaths 8.3 vs 17.8  botFaults(A) 0       [T3, matches/h_3pick-T3-3p-h3_tvv]
SUMMARY h_3pick vs tb_merge_b: 11W-13L (46%)  avg gems 545 vs 570  avg deaths 12.2 vs 11.5  botFaults(A) 0  [T3, matches/h_3pick-T3-3p-tb_merge_b]
```

**Final bot (= L).** One game confirmed it reproduces the L run exactly: 00packs B vs imit_test, 546-248.

Sprint vs tb_merge_b (`matches/h_3pick-sprint`): SPRINT_LINE

## Notes for the analyst
- **02the-pack** (a real ladder loss, 0-0 on the gold tiebreak) is not a fight problem. The single altar is enclosed by a large camp ring, so nobody tributes. It belongs to Q2/Q3 (gold tiebreak or gated-altar assault).
- **Lock fix v1 sends carriers to the next altar, which can be far** (01the-farm). A drafted v2 (`LOCK_BREAK`) costs a remembered-locked altar distance + 8 and breaks the lock when it is chosen. It is untested; it is in the session scratchpad, not in this bot.
- **Real ladder:** the 01broken_curve loss (357-1011) was to the team "Blame the Altar". The lock bug is a plausible cause, but there is no replay to confirm it.
