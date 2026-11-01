# Strategy batch 1, gate round 1 and C++ port: interim results (2026-10-31, session ended ~20:00 EDT)

These three workflows were **interrupted** when the dev-PC session ended. The implement-and-test stages mostly finished. The independent **analysis sessions and the promotion gate did not run.**

This file recovers everything measured, since `matches/` (raw stats) is gitignored and not in the repo. Each bot dir's `NOTES.md` has the full detail.

**Champion at the time:** `tb_merge_b` (website v2, Sprint 3 entry; ladder 43W-17L, rating ~1,491).

**Gate reminder (LOOP.md §4):** promotion needs ≥ 82/140 on `--maps all` (95% Wilson lower bound above 50%) plus a paired gauntlet, a clean release run and an analysis session. **None of the candidates below has been gated yet.**

## Results per candidate (vs `tb_merge_b` unless noted; "base" = tb_merge_b vs the same opponent)
| Candidate (bot dir) | Hypothesis | Key results | Status / next |
|---|---|---|---|
| `h_3pick` (final = "L", lock-memory fix ON, trio mode OFF) | Q18: 3-pick maps | 3-pick maps (12 maps x 2) vs tb_merge_b **13W-11L**; vs imit_test 21-3 (base 20-4); vs h3_tvv **19-5 (base 16-8)**; vs h3_csv 23-1 (base 22-2). Sprint vs tb_merge_b **22W-18L (55%)**. Trio mode lost (T 7-17, T3 11-13) | **Bug fix found** in tb_merge_b (see below). Gate it on all maps |
| `h_goldtie` (v2) | Q2: gold-tiebreak play | 5 tiebreak maps vs tb_merge_b **9W-1L**; 01boss-battle/02guardians/02the-pack 6-0; vs imit_test on tiebreak maps 8-2 (base 5-5); sprint **21W-19L** (net +1); release clean (won 01boss-battle on gold 27,655 vs 1,715) | Targeted fix works; little effect elsewhere. Combine with others and gate |
| `h_earlyfight` (v2) and `h_earlyfight_all` (v3 = rule all game) | Q12: early fights | v1 sprint 18-22; **v2 sprint 22-18 (55%)**; **v3 sprint 23-17 (58%)**; v2 vs imit_test 32-8 (base 34-6); v2 vs sf_bank on 8 early-death maps 13-3 (base 14-2); v3 vs imit_test 26-5 (partial) | Promising; gate v3 (`h_earlyfight_all`) on all maps |
| `h_fightfuel` | Q13: fuel in fights | Sprint **22W-18L (55%)**; vs imit_test 34-6, vs lad_vcst 34-6; fuel maps 15-11; another 37-map set 15-15 | **Finding:** exhaustion is mostly a per-turn sensing baseline, not fights (below). Analysis + gate pending |
| `h_antistun` | Q15: no tribute/recall/teleport start within reach of a ready stunner | Sprint **20W-20L (50%)**; vs imit_test 31-9 (base 33-7); vs lad_vcst 25-8 (partial; base 30-10) | Neutral to slightly negative: **likely reject**; analysis not run (CHLOG lines in replays) |
| `g_earlyfight`, `g_fightfuel` | gate snapshots | — | Created by gate round 1; no evals ran. Delete or re-gate |
| `g_ef_ff` | merge of earlyfight + fightfuel | — | Created; its NOTES.md is a stale copy of tb_merge_b's; merge state unverified. **Rebuild before use** |
| `cpp_port` | Q11: C++ port | Quick 13W-11L, quick-2 13-11, **sprint 20W-20L (50%)**; release check won on 01big-world; **0 fuel exhaustions** (Python ~87/game) | Faithful parity port, about 3,200 lines. Design in `bots/cpp_port/DESIGN.md`, status in `NOTES.md`. Verify/fix phases did not run |

Imitation opponents added in this batch: `h3_tvv` (Tavi, Varg, Vendetta) and `h3_csv` (Cassi&Issac, Stellar, Vesper), copying the real 3-pick ladder losses.

## Findings worth keeping (evidence in each bot's NOTES.md)
1. **Bug in tb_merge_b: lock-memory 2-cycle** (h_3pick).
   - `pick_altar` only skips an enemy-locked altar while the lock is *in vision*.
   - When the lock is just out of sight, carriers oscillate between a locked altar and a free one forever, holding their gems until they are killed.
   - Example: 01broken-curve B vs imit_test. Three carriers froze from r1000 to r1375, then all three died within 13 rounds and 110 gems were lost.
   - Fix: `LOCK_MEMORY_FIX` (`pick_altar` also skips remembered locked altars).
2. **0-0 maps are structural** (h_goldtie):
   - 02the-pack: the altar ring sits inside a 48-wolf group;
   - 02guardians and 01boss-battle: the only walkable ring tiles are monolith spawn tiles;
   - 02gift-wrapping: every group is wrapped round a wall, so nothing passes the safety model;
   - 01yellow-brick-road: a **movement bug**. A champion standing on a dead camp tile of a half-cleared group is pushed back by the "never block a respawn" rule, which froze all 5 champions for ~1,700 rounds.
3. **Gold play wins tiebreaks by a lot** (e.g. 15-30k vs 0.5-4.7k gold), but only matters on those maps.
4. **Early-fight deaths** (h_earlyfight diagnostics) share one shape:
   - a lone, mostly non-dash melee (Ryth, Marcella, HoR) stands next to an enemy melee and trades for 5-11 turns, while 2-5 enemies are within 6 and 0-1 allies are within 8 (the `adjacent_melee` stand-and-trade rule);
   - or a champion chases a low-HP target into 3-4 enemies.

   Also, our own early deaths don't predict losses; the *enemy's* early deaths do. So the aim is to convert fights, not just avoid them.
5. **Fuel** (h_fightfuel profiling):
   - `observe()` (0.5-1.3M per turn) and `threats()` (0.6-1.3M) read every visible camp through the API (~5 calls of ~3k each per camp) every turn.
   - Loss-heavy exhaustion comes from steady loops on 02the-pack, 01yellow-brick-road and similar, not from fights.
   - The C++ port has 0 exhaustions.
6. **Strong side bias in mirrors.** `tb_merge_b` vs itself one-sided: **team B wins 15/20 sprint maps.** Always evaluate both sides (tools/eval.py does).

## New hypotheses (added to STRATEGIES.md)
- **Q20:** teleport-crystal into a guard-enclosed altar ring (02the-pack). The ring is free and sleeping wolves don't attack.
- **Q21:** universal respawn-rule movement fix (01yellow-brick-road freeze).
- **Q22:** open-gate rush. On no-tribute maps, once a guard dies, rush the carried gems to the altar.
- **Q23:** move `init_gold` / map analysis into the draft (250M fuel) via draft memory, to keep turn 1 fuel-identical.
- **Q24:** **combined candidate** = tb_merge_b + `LOCK_MEMORY_FIX` (h_3pick) + gold play (h_goldtie v2) + early-fight rule (h_earlyfight_all) + fuel caching (h_fightfuel). These touch different subsystems. Build it, gate it on all maps, and expect the gains to add up.
- **Q25:** cheaper sensing: cache camp reads per turn and skip ward-only camps in `observe`/`threats`, in Python and in the C++ port.
