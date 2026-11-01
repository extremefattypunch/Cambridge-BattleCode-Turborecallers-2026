# h_bosscommit: boss-camp commit timing (STRATEGIES V3L-3)

**Lineage.** `python3.12 tools/newbot.py c2_respawn h_bosscommit`. Only `src/bot.py` differs; `main.py`,
`draft.py` and `randomness.py` are byte-identical to c2_respawn. Every change is tagged `h_bosscommit`.
Report: `results/simulated-matches/2026-11-01_0531_h_bosscommit/notes.md`. Debug copy (BOSS_LOG on): `bots/dbg_bc_trace`.

## Why
Ladder 00contest: v3 lost 0-1000 (中国人能飞) and 400-1000 (Mein Kraft). All 400 of the map's gems are in two
monoliths (200 gems, 20,000 HP, strength 200, range 5); the opponents took the bags from r589-r800, we never did.
c2's model blocks this in two places:
1. `choose_target`'s solo safety model: hit-and-run needs `maxhp > s*(rng+1)+80 = 1,280` and <= 4 cycles, so the
   monolith is rejected until one champion is very tanky (local first boss clears r1150-r1800).
2. The danger check counts every awake camp in range as hitting us, with the free-field exit cost
   `s*(r-d+2)+60` (1,260 HP next to a monolith). A camp hits only the nearest champion.

## Engine fact measured here (trace games bc-trace2, 519 inferred boss hits)
A camp hits the **Chebyshev-nearest champion of either team**: 519/519 hits consistent (Euclidean 496/519,
Manhattan 477/519). **Ties go to the lowest unit id** (56/56).

## Flags (all at the top of bot.py)
| Flag | Value | Meaning |
|---|---|---|
| `BOSS_COMMIT` | True | master switch (static census in `init_boss`) |
| `BOSS_HP` / `BOSS_STR` / `BOSS_STR_MAX` | 15000 / 250 / 600 | boss group: monolith, or total HP >= 15,000, or strength >= 250, but strength <= 600 and value > 0 (no no_tribute guards) |
| `BOSS_SHARE` | 0.5 | boss map: boss groups hold >= 50% of the map's gem RATE (gems / `max_respawn_timer`). 8 local maps: 00contest, 00stampede (1.00), 00great-wall, 00rows, 00anvil, 00monolith, 01starvation, 01gold-rush (0.50-0.61) |
| `BOSS_WAVES` | 1.25 | commit when n_team copies of me kill it with team HP above the reserve (`waves = s_eff*ttk / (k*usable)`) |
| `BOSS_RESERVE_HITS` | 4 | usable HP = maxhp - (s_eff*4+60) |
| `BOSS_MUSTER_K` / `BOSS_MUSTER_MAX` / `BOSS_BAN` | 3 / 30 / 80 | a sleeping boss above 50% HP is woken only with 3 healthy champions near; after 30 rounds at the ring with fewer, ban it 80 rounds |
| `BOSS_RALLY` / `RALLY_BYTE` | True / 6 | shared byte 6 = boss idx+1: a champion whose check passes calls the team; able champions (usable > 0) join; cleared on capture / respawn / a death on the assault |
| `BOSS_NEAREST` | True | team-aware danger for boss camps (nearest-champion rule, lowest-id ties, escape field) |
| `BOSS_JUNGLE` | True | boss maps: Jungle emblem (-30% camp damage) before the Bruiser build |
| `BOSS_LOG` | False | debug only (debug_block prints; BD/BT/BOSS lines) |

## Mechanics
- **Escape field** (`esc_field`): per boss group, walking distance to the nearest walkable tile outside its range
  (built in spare fuel in `build_static_fields`, else on first use). Used for the solo exit cost, for
  `boss_escape` (retreat along the field, dash if it saves a step; replaces the spawn-distance tie-break that
  walked champions into the (14,29) dead-end corner on 00contest), and to filter stand tiles (no dead ends).
- **Danger** (`boss_danger`): a boss camp is ignored while a healthy other champion is nearer (or as near with a
  lower id) and I could still leave; else the exit cost stops when a healthy other champion would become
  nearer, capped by the escape distance.
- `read_claims` skips byte 6 on boss maps. On other maps (boss share < 0.5) the bot plays c2_respawn's logic
  (only init_boss and a few flag tests run).

## Versions
- v0: BOSS_WAVES 3, solo exit cost r-d+1, ties = 1 step, muster timeout -> solo attack. 2W-14L vs c2 on the 8 maps.
- v1: + healthy-cover model, Jungle first, usable with 3 hits. 3W-13L vs c2; corner trap and death spiral.
- v2 (this): escape field, lowest-id ties, BOSS_WAVES 1.25 / 4-hit reserve, rally byte, muster ban (no solo),
  death penalty kept for boss targets.
