# h_bosscommit: boss-camp commit timing (STRATEGIES V3L-3)

**Lineage.** `python3.12 tools/newbot.py c2_respawn h_bosscommit`. Only `src/bot.py` differs; `main.py`,
`draft.py` and `randomness.py` are byte-identical to c2_respawn. Every change is tagged `h_bosscommit`.
Report: `results/experiments/2026-11-01-h_bosscommit.md`. Debug copy (BOSS_LOG on): `bots/dbg_bc_trace`.

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
| `BOSS_MUSTER` (**False** in v3), `BOSS_MUSTER_K` / `BOSS_MUSTER_MAX` / `BOSS_BAN` | 3 / 30 / 80 | a sleeping boss above 50% HP is woken only with 3 healthy champions near; after 30 rounds at the ring with fewer, ban it 80 rounds |
| `BOSS_RALLY` / `RALLY_BYTE` | True / 6 | shared byte 6 = boss idx+1: a champion whose check passes calls the team; able champions (usable > 0) join; only the rallied boss gets the commit; cleared on capture / respawn (`BOSS_RALLY_DEATH_CLEAR` False in v3) |
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

## Versions (screens: 8 boss maps x 2 sides vs c2_respawn; c2's own baseline vs tb_merge_b / q24 there: 9/16)
- v0: BOSS_WAVES 3, solo exit cost r-d+1, ties = 1 step, muster timeout -> solo attack. 2/16; 11.6 camp deaths/game.
- v1: + healthy-cover danger model, Jungle first, 3-hit reserve. 3/16; corner trap (14,29) on 00contest.
- v2: + escape field, lowest-id ties, BOSS_WAVES 1.25 / 4-hit reserve, rally byte, muster that bans (never solo),
  death penalty kept for boss targets. 5/16; camp deaths 1.4/game; 685 idle muster turns in the 00contest trace.
- **v3 (this, final):** BOSS_MUSTER = False, rally exclusive to one boss, BOSS_RALLY_DEATH_CLEAR = False. 4/16.
  - Final: 69W-71L vs c2_respawn (all maps; boss maps 4/16, others 65/124).
  - Final: 94W-46L vs tb_merge_b (boss maps 5/16, others 89/124; c2: 98 = 9 + 89).
- Ablations: `bots/h_bosscommit_nj` (BOSS_JUNGLE False) 3/16; `bots/h_bosscommit_v4` (enemy gate 30 rounds within 10 of the boss,
  120-round commit cap, 200-round ban) 3/16.

**Verdict: rejected** (report `results/experiments/2026-11-01-h_bosscommit.md`).
- The commit clears bosses earlier (median r1184 vs c2's r1804) but halves farming on the boss maps (gold 4.0k vs 7.5k).
- Carriers die, and c2 finishes the bosses we chip.
- Known defect: about 76 fuelExhausted per game on the boss maps (00stampede about 500): the stand-tile filter loops goals x camps.
