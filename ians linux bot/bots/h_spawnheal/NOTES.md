# h_spawnheal: STRATEGIES Q27 refined (Q27b + Q27c) on top of q24_combo

**Lineage.** `tools/newbot.py q24_combo h_spawnheal`, then h_treasure's mechanism A (spawn-heal-aware
fighting) and its cluster-chain value (B) ported from the h_treasure diff against tb_merge_b, with the
two fixes the h_treasure report asked for. h_treasure's far-altar banking (C) and the delivery term
are **not** ported. Report: `results/experiments/2026-11-01-h_spawnheal.md`.

Only `src/bot.py` differs from q24_combo (2,697 -> 2,912 lines). `main.py`, `draft.py` and
`randomness.py` are byte-identical to q24_combo. Every change is behind a module flag at the top of
`bot.py` (block "h_spawnheal"). Nothing keys on map names.

## Final flags (= screen variant `sh_v2b`)
| Flag | Value | What |
|---|---|---|
| `SPAWN_HEAL_AWARE` | True | `spawn_healed(e, eh, burst)`: an enemy on its own spawn tile with HP > one round of our damage (my_str + ally_str) is not a target. If every near enemy is spawn-healed, `handle_enemies` returns False (a static hazard, like an awake camp). `adjacent_melee` skips them too. Their damage still counts in threat, fight_dps and group_balance. |
| `SPAWN_NEAR_KILL` | 1.0 | Spawn-adjacent, not channelling: needs kill within this many rounds (only for proven heal-hoppers, see below). |
| `SPAWN_AVOID` | True | Turret zone: range+1 of visible enemies standing on their spawn is an `avoid` mask for farming, capture, respawn-wait and `do_tribute` walks (falls back to no-avoid when no path). |
| `HEAL_CHASE_GUARD` | True | From the first landed hit, if a target's HP after CHASE_MAX (6) rounds of landed hits is not below its HP at the window start, ban it for CHASE_BAN (40) rounds. |
| `SPAWN_TOUCH_D` | 3 | **Q27b (static).** If the spawn regions are within 3 (Chebyshev), the enemy spawn-adjacent zone meets ours: the spawn-adjacent rule and the turret zone are off for the game. On the 70 local maps this is exactly 00reverse-spiral and 00rushbait-v2 (d_ss = 1); 02treasure-box has d_ss = 4. The on-spawn rule stays. |
| `SPAWN_SELF_EXEMPT` | **False** | Q27b (dynamic, v1 only): spawn rules off while we stand on / next to our own spawn. Off because it re-created 124 opening on-spawn engages (r32-200, all at full HP) on 02treasure-box. |
| `SPAWN_NEAR_EVIDENCE` | True | v2: the spawn-adjacent rule applies only to an enemy we saw heal at its spawn (HP up by > HOP_GAIN 50 while on/next to its spawn, seen again within HOP_SEEN 3 rounds) in the last HOP_MEMORY 200 rounds. `note_hoppers()` runs each turn after `threats()`. Against every local opponent it almost never fires (0-2 marked enemies per game), so locally the adjacent rule is effectively off. |
| `CHAIN_VALUE` | True | h_treasure B: `choose_target` adds CHAIN_B (0.5) x gems of unclaimed, available 0-strength gem groups within CHAIN_R (6) walking steps, capped at CHAIN_CAP (3) x the group's value; `target_order` bound uses value x (1 + CHAIN_CAP) for such groups only while the chain is on. Neighbour lists are built with each static field (`build_nbrs`). Off under `no_tribute`. |
| `CHAIN_GOLD_FLOOR` | True | **Q27c.** `chain_active()`: the chain bonus runs only while this champion's earned gold >= CHAIN_GOLD_RATE x (round - CHAIN_GOLD_GRACE). Earned gold is tracked by `gold_tick()` (positive deltas of gold on hand; `shop()` credits income before buying and resets the reference after). |
| `CHAIN_GOLD_RATE` | 0.6 | ~ the median per-champion income in the q24 mirror (0.58 gold/round). v1 used 0.3. |
| `CHAIN_GOLD_GRACE` | 100 | v3 (`sh_v3`) tried 0: 26-14 vs q24 on the screen (v2b 27-13), breadcrumbs gold better as A only. Not adopted. |

Note: the source comment above `SPAWN_NEAR_EVIDENCE` attributes the 02arena B regression to the
spawn-adjacent rule. Later traces showed that game is changed by the **on-spawn** skip: in v2 no
heal-hopper is ever marked (so the adjacent rule never fires), the result is identical with the turret
zone off (`dbg_sh2_trace_nav`) and with the chain off (`sh_v2a`), and the first divergence is slot 2
skipping an on-spawn enemy 7 times before r100 where q24 engaged at r83 (v1: also identical with the
chase guard off). The comment was left as is so the gated bytes stay unchanged.

## Screen variants (all `tools/newbot.py` forks; flags only)
| Bot | Config |
|---|---|
| `sh_v1a` | A + Q27b (self-exempt on, touch D 3), always-on adjacent rule, chain off |
| `sh_v1b` | sh_v1a + chain + gold floor 0.3 / grace 100 |
| `sh_v2a` | self-exempt off, adjacent rule evidence-gated, chain off |
| `sh_v2b` | sh_v2a + chain + gold floor 0.6 / grace 100 (= final) |
| `sh_v3` | sh_v2b with grace 0 |

Trace copies (wrapper `main.py` only, bot.py byte-identical to the source): `dbg_q24sh_trace`
(q24_combo), `dbg_sh_trace` (v1b), `dbg_sh2_trace` (v2b), plus `dbg_sh_trace_ncg` (chase guard off)
and `dbg_sh2_trace_nav` (turret zone off). Output: `matches/q27r/tr/<name>/us.txt` (`E round slot flag hp`
per engage turn, flag 2 = target on its spawn, 1 = next to it; `S` cumulative counters every 50 rounds;
`T` target/gold state every 25 rounds).
