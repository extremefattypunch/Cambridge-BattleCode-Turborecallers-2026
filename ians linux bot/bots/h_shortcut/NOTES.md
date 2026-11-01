# h_shortcut: c2_respawn + the V3L-2 low-HP island recall fix

**Lineage.** `python3.12 tools/newbot.py c2_respawn h_shortcut` (champion, website v4), then one patch to `src/bot.py`
(final version = v2 below). Everything else: `bots/c2_respawn/NOTES.md` (q24_combo + h_respawnfix), `bots/q24_combo/NOTES.md`.
Experiment report: `results/simulated-matches/2026-11-01_0531_h_shortcut/notes.md`.

| File | Change |
|---|---|
| `src/bot.py` | c2_respawn + `SHORTCUT_FIX` / `SHORTCUT_FAIL_TURNS` (2,776 -> 2,808 lines) |
| `src/main.py`, `src/draft.py`, `src/randomness.py` | Byte-identical to c2_respawn |
| Controls | `bots/h_shortcut_off2` = this bot with `SHORTCUT_FIX = False` (v2 control); `bots/h_shortcut_off` = the v1 control |

## The bug (STRATEGIES V3L-2, "01shortcut stuck champion")
`play_turn_main`, "recall to heal / shop when safe" (no camp hitting us, not on spawn):

```python
low = hp < maxhp * 0.45
if (low or rich) and spawn_d > 6 and self.recall_safe(me, enemies):
    me.recall() ...
elif low:
    self.step_toward(me, self.spawn)   # result ignored
    return
```

- `spawn_d` is the **Chebyshev** distance to our spawn, so a champion within 6 tiles never recalls; it walks.
- 01shortcut has a hole-ringed island (x 10-19, y 31-34 for team A, mirrored for B). It holds 2 wolves and 2 gold
  clusters (group 8 / 7), 5-7 tiles from our spawn.
  - Dash champions (Vendetta, HoR) and TP-crystal users (Marcella) reach it and farm the wolves down to low HP.
  - They are then in a walk component without our spawn: `step_toward` finds no path, returns False, and the turn ends.
  - HP never regenerates off-spawn, so every later turn is the same. The champion idles until it is killed or the game ends.
- **Traced** with a fuel-free `debug_block` trace (`bots/dbg_cut_trace`); the game reproduced byte-for-byte (`matches/v3l2-trace-a`).
  - Every turn from r650 to r2000, Vendetta sits at (16,32) in walk component 2 (23 tiles) with 220/1000 HP.
  - Her target is group 8, with only the 120-HP gold cluster (14,33) alive.
  - The turn's trail ends `... danger he_none`, i.e. it returns inside the `low` branch.
- A perturbed trace build (`matches/v3l2-trace-a2`) stranded Marcella (380/1400) and HoR (380/1000, carrying 13 gems)
  on the same island from r615 to r2000.

## Patch (v2, `SHORTCUT_FIX = True`, `SHORTCUT_FAIL_TURNS = 3`)
```python
elif low:
    if self.step_toward(me, self.spawn):
        return
    if SHORTCUT_FIX:
        # count consecutive failed steps home (home_fail / home_fail_rnd, set only here)
        if ((self.spawn & self.comp_of(pos)).is_empty() or self.home_fail >= SHORTCUT_FAIL_TURNS) \
                and self.recall_safe(me, enemies):
            me.recall(); self.write_claim(None)   # in try/except
    return
```
The patch is keyed on structure, not on the map.
- **Spawn in another walk component** (island reached by dash or TP crystal): recall at once.
- **Same component, blocked for 3 turns running** (a corridor blocked by units or camps): recall.
- **One-turn block:** keep the old one-turn wait.
- **Enemy that could reach us during the channel** (`recall_safe` False): wait as before; `handle_enemies` ran first anyway.
- **New state:** `home_fail` and `home_fail_rnd` (set in `__init__`), written only on the failed-step path.
- **With `SHORTCUT_FIX = False`:** the logic is c2_respawn's.

**v1** (first screen and first all-maps runs; source in the report) recalled immediately on any failed step. The flag-off
controls showed that it also fired on one-turn unit blocks near spawn. There a recall (5 turns) was slower than waiting one
turn and walking: on 01elk-arena B vs tb_merge_b, Marcella healed at r246 instead of r242.

## Flags
- Debug flags all off (`DEBUG`, `DIAG`, `VALIDATE`, `PROF`, `GOLD_LOG`, `Bot.debug_tb`).
- `RESPAWN_FIX` and every q24_combo switch unchanged.
- `py_compile` passes; `src/__pycache__` removed.
