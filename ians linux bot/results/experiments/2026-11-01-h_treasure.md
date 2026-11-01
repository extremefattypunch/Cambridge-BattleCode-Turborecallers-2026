# Experiment: h_treasure, Q27 fix for 02treasure_box (2026-11-01, cluster)

STRATEGIES Q27. Stages: diagnosis (previous workflow stage), implement, targeted screens (2 iterations), all-maps head-to-head (= gate a), analysis session. The verdict is at the end.

## Hypothesis
- **What:** our logic has two separate failures on 02treasure_box, and both are triggered by map structure rather than by the map name.
  - **A. Spawn-heal fight lock (general fight-model bug).** An enemy standing on its own spawn tile heals to full at its turn end (SPAWN_HEALING 1.0), so it dies only to burst landing within one round. `handle_enemies` has no notion of this:
    - its kill time `eh/(my_str+ally_str)` assumes the HP stays down;
    - the chase guard only fires when we fail to *land* hits;
    - `adjacent_melee` stands and trades.

    So the team locks onto unkillable targets for hundreds of rounds with 0 monster damage.
  - **B. Myopic target value.** `choose_target` scores each group as value/time. It gives no credit for a dense, respawning field of 0-strength gem clusters (02treasure-box has 16 single clusters, 112 gems, within Chebyshev 3 of its only altar). So the team walks 43-46 steps to the big outer groups and carries split bags back through the maze.
  - **C. Banking with one far altar.** Bags of 12-13 gems from a 5-way capture stay below BANK_ANY, so they are carried into the next fight.
- **Source: real ladder games.** Record on treasure_box as the live v2 is **2W-3L**, and all five summaries are in `matches/ladder/summary/`. The four with the highest champion-damage/monster-damage ratios of all 34 ladder summaries are treasure_box (the next map, 01shortcut, is at 1.1):

| Match | Side | Opponent (draft) | Result | cdmg / mdmg | Largest enemy healing | Our deaths (≤4 of enemy spawn) | Our altar-cluster clears / theirs | Tributes |
|---|---|---|---|---|---|---|---|---|
| f5832d1d | A | Feral Fog Walkers (HoR, Vesper, Ryth, Ren, Stellar) | W 477-23 | 756,938 / 67,481 = **11.2** | Ryth **705,534** (3 deaths) | 7 (4) | 12 / 3 | 25 |
| 7dd290a4 | A | sub7anr (C&I, Stellar, Prism, Willow, Tavi) | L 0-1002 (r995) | 44,863 / 10,731 = **4.2** | Cassi 49,319 | 21 (11) | **0 / 104** | **0** |
| 7d9e948f | A | Worldwide Gem Thieves (C&I, Stellar, Varg, Ren, Tavi) | W 552-318 | 349,442 / 95,206 = **3.7** | Varg 168,247 | 31 (15) | 25 / 14 | 30 |
| 51bb63c8 | A | six seven (HoR, Vesper, Vendetta, Marcella, Ryth) | L 163-1005 | 80,401 / 52,878 = **1.5** | HoR 46,376 (0 deaths) | 28 (12) | 4 / 24 | 6 |
| fb40725d | B | EXP'D (Ryth, Vesper, Willow, Prism, Tavi) | L 138-1005 | 34,214 / 46,033 = 0.7 | Prism 57,841 | 14 (3) | 6 / 0 | 7 |

  - **How the winners played:**
    - sub7anr put Stellar in the inner box by r47 and cycled the 16 clusters there: 104 inner clears, first tribute r59, 1000 by r995. Four champions fought us at the gap meanwhile, with Willow plus spawn healing.
    - six seven's HoR farmed the clusters from r136 and banked 7-8-gem tributes.
  - **fb40725d (new since the diagnosis) is a different failure:**
    - our first clear came at **r296** (theirs r33);
    - we got 0 kills;
    - their Prism took 33k damage and received 57k healing from Willow and spawn.

    That is a Willow heal sink rather than a spawn heal sink (see new hypothesis Q29).
- **Local reproduction (diagnosis):**
  - `tb_merge_b` as team A vs starter-python, traced: 1,194 of 1,829 engage turns (**65%**) targeted an enemy standing on its own spawn tile. Enemy Tavi received 101,180 healing, and 1000 came only at r1897.
  - 00reverse-spiral A vs starter-python: cdmg/mdmg **19.8**, Willow healed 311,376, and we scored only 186 gems in 2000 rounds.

## Setup
- **Candidate:** `bots/h_treasure`, forked from the champion `tb_merge_b` with `tools/newbot.py`.
  - Only `src/bot.py` differs: about 180 lines, all tagged `h_treasure`, behind named flags at the top of the file. main.py, draft.py and randomness.py are byte-identical to the champion's.
  - Everything keys on static structure: the enemy spawn tiles, the static distance fields, and group geometry. Nothing keys on map names.
- **A. Spawn-heal-aware fighting** (`SPAWN_HEAL_AWARE`, `SPAWN_AVOID`, `HEAL_CHASE_GUARD`):
  - `spawn_healed(e, eh, burst)`. An enemy on `enemy_spawn_bb` with HP greater than `burst` (my_str + ally_str, one round of our damage) is not a target. An enemy on a spawn-adjacent tile that is not channelling needs `eh <= burst * SPAWN_NEAR_KILL` (1.0). Its threat and fight_dps still count.
  - If *every* near enemy is spawn-healed, `handle_enemies` returns False: the enemies are treated as a static hazard, like an awake camp. Farming and banking go on, and the danger branch still retreats at low HP.
  - `adjacent_melee` skips spawn-healed enemies, so there is no stand-and-trade with a healing enemy.
  - **Heal-aware chase guard.** From the first landed hit, if the target's HP after CHASE_MAX (6) rounds of landed hits is still at or above its HP at the start of the window, it is banned for CHASE_BAN (40) rounds.
  - **Turret avoid zone.** Each turn, the union of range+1 around visible enemies standing on their spawn is passed as `avoid` to the farming, capture, respawn-wait and `do_tribute` paths. `step_toward` still falls back to no-avoid when no path exists.
- **B. Target value** (`CHAIN_VALUE` in the final build; `DELIVERY_VALUE` was tested and dropped):
  - **Chain.** For each group, `build_nbrs` (run as its static field is built) lists the 0-strength gem groups within CHAIN_R = 6 walking steps. `choose_target` adds `CHAIN_B (0.5) × gems of the unclaimed neighbours available by arrival`, capped at CHAIN_CAP (3) × the group's value. The `target_order` bound uses value × (1 + CHAIN_CAP), so pruning stays valid.
  - **Delivery (off).** `cost += DELIVER_W × group→altar walk × min(1, share/BANK_REF)`.
- **C. Far-altar banking** (`FAR_ALTAR_BANK`). Bank first when we carry at least BANK_CLOSE gems, `gems × 4 ≥ altar distance`, and the next target's altar distance exceeds ours by more than 8.
- **Final flags:** A on, CHAIN on, C on, DELIVERY off. This is the code screened as `h_treasure_chainc`; the only byte difference is one space in a comment.
- **Screening variants** (all `tools/newbot.py` forks of h_treasure; flags only):

| Variant | Config | Name at screen time |
|---|---|---|
| v1a | A only | `h_treasure` (it held A-only flags during screen 1) |
| v1b | A+B(delivery+chain)+C | `h_treasure_abc` |
| v2a | A+chain | `h_treasure_chain` |
| v2b | A+chain+C (= final) | `h_treasure_chainc` |

- **Maps for the screens:** the 20 affected maps from the diagnosis.
  - Spawn proximity: 02treasure-box, 00reverse-spiral, 00rushbait-v2, 00quadrants, 00gem-fields, 01shortcut.
  - Altar-adjacent cluster fields: 00lost-world, 00anvil, 00breadcrumbs, 00quarry, 01broken-curve, 02crossing, 00road-of-riches.
  - Long delivery legs: 02the-pond, 01islands, 00stampede, adgato-gemcombat5, 01corridors, 02tangle.
  - Plus 02arena.

  Both sides vs `tb_merge_b`, vs `starter-python` and vs `tb_aggro` (different fight logic).
- **Baselines:**
  - the champion vs starter-python and tb_aggro on these maps (diagnosis folders `q27-spawnprox-*` and `q27-tbox-*`, plus `q27ht-base-*-s2` from this session, job 56778333);
  - the champion mirror `b1-tb_merge_b-mirror-all`.
- **Null expectation vs the champion.** By symmetry a mirror is 1-1 on every map, so a no-op change scores exactly 20/40 on 20 maps and 70/140 on all maps. The comparisons below are against the mirror seat's result.
- **Jobs**, all on the free Slurm `test` partition via `tools/onslurm.sh`, cambc 4.0.0 / engine 2.0.0:

| Job | Contents | Tag(s) |
|---|---|---|
| 56778332 | v1a vs tb_merge_b | `q27ht-a-tbm` |
| 56778331 | v1a vs references | `q27ht-a-starter`, `q27ht-a-aggro` |
| 56778333 | baselines | `q27ht-base-*-s2` |
| 56778523 | v1b vs tb_merge_b | `q27ht-abc-tbm` |
| 56778524 | v1b vs references | `q27ht-abc-*` |
| 56779954 | v2a vs tb_merge_b | `q27ht-ch-tbm` |
| 56780096 | v2a vs references | `q27ht-ch-*` |
| 56779956 | v2b vs tb_merge_b | `q27ht-chc-tbm` |
| 56779957 | v2b vs references | `q27ht-chc-*` |
| **56780666** | gate: `python3.12 tools/eval.py h_treasure tb_merge_b --maps all --jobs 16 --keep --tag ll1-h_treasure-all` | `ll1-h_treasure-all` |

- **Traces.** Local `cambc run` games with a wrapper main.py that logs one line per turn: the engage target and whether it stands on its spawn, `spawn_healed` skips, turret zones and bans. bot.py was unchanged. Output is in `matches/q27ht/tr*/us.txt`.

## Results
### Screens on the 20 targeted maps (verbatim)
```
SUMMARY h_treasure vs tb_merge_b: 16W-24L (40%)  avg gems 626 vs 693  avg deaths 12.2 vs 11.5  botFaults(A) 0        [v1a = A only]
SUMMARY h_treasure vs starter-python: 40W-0L (100%)  avg gems 927 vs 94  avg deaths 3.1 vs 31.6  botFaults(A) 0     [v1a]
SUMMARY h_treasure vs tb_aggro: 39W-1L (98%)  avg gems 951 vs 221  avg deaths 4.8 vs 20.9  botFaults(A) 0           [v1a]
SUMMARY h_treasure_abc vs tb_merge_b: 27W-13L (68%)  avg gems 706 vs 516  avg deaths 9.1 vs 12.8  botFaults(A) 0
SUMMARY h_treasure_abc vs starter-python: 40W-0L (100%)  avg gems 879 vs 75  avg deaths 3.7 vs 30.6  botFaults(A) 0
SUMMARY h_treasure_abc vs tb_aggro: 37W-3L (92%)  avg gems 872 vs 181  avg deaths 4.2 vs 20.1  botFaults(A) 0
SUMMARY h_treasure_chain vs tb_merge_b: 21W-19L (52%)  avg gems 690 vs 610  avg deaths 11.8 vs 11.1  botFaults(A) 0
SUMMARY h_treasure_chain vs starter-python: 40W-0L (100%)  avg gems 924 vs 85  avg deaths 3.6 vs 29.4  botFaults(A) 0
SUMMARY h_treasure_chain vs tb_aggro: 36W-4L (90%)  avg gems 943 vs 234  avg deaths 4.9 vs 19.6  botFaults(A) 0
SUMMARY h_treasure_chainc vs tb_merge_b: 21W-19L (52%)  avg gems 652 vs 631  avg deaths 12.0 vs 11.4  botFaults(A) 0
SUMMARY h_treasure_chainc vs starter-python: 40W-0L (100%)  avg gems 916 vs 88  avg deaths 3.3 vs 29.6  botFaults(A) 0
SUMMARY h_treasure_chainc vs tb_aggro: 38W-2L (95%)  avg gems 930 vs 228  avg deaths 4.6 vs 18.8  botFaults(A) 0
baseline (economy-map half; the spawn-proximity half came from the diagnosis folders, 20W-0L vs each):
SUMMARY tb_merge_b vs starter-python: 19W-1L (95%)  avg gems 826 vs 78  avg deaths 2.0 vs 26.4  botFaults(A) 0
SUMMARY tb_merge_b vs tb_aggro: 19W-1L (95%)  avg gems 845 vs 252  avg deaths 4.3 vs 19.1  botFaults(A) 0
```
| Variant | vs tb_merge_b (null 20/40) | vs starter-python (champion 39-1) | vs tb_aggro (champion 39-1) | Avg rounds vs starter / aggro (champion 1470 / 1427) |
|---|---|---|---|---|
| A only | 16-24 | 40-0 | 39-1 | 1409 / 1421 |
| A+delivery+chain+C | **27-13** (Wilson 0.52-0.80) | 40-0 | 37-3 | 1450 / 1447 |
| A+chain | 21-19 | 40-0 | 36-4 | 1425 / 1422 |
| **A+chain+C (final)** | 21-19 | 40-0 | 38-2 | 1420 / 1426 |

### Gate head-to-head, all 70 maps × both sides (verbatim)
```
SUMMARY h_treasure vs tb_merge_b: 72W-68L (51%)  avg gems 639 vs 586  avg deaths 12.6 vs 13.1  botFaults(A) 0   [matches/ll1-h_treasure-all, job 56780666]
```
- **Gate (a): FAIL.** 72/140 is below the 82 needed (95% Wilson 0.432-0.596). botFaults is 0.
- Gates (b) gauntlet and (c) release run were not run, because (a) failed.
- **Against the mirror seat:**
  - 39 W/W, 37 L/L;
  - **33 games gained** (lost by the champion's seat, won by us);
  - **31 games lost** (won by the champion's seat, lost by us);
  - only 5 of 140 games are byte-identical to the mirror game.
- **Per map:** 20 maps net +1, 18 maps net -1, 32 maps unchanged.
- **fuelExhausted** (gate c item), h_treasure **14,550** vs tb_merge_b **10,312**.
  - Nearly all the excess is on the two known stuck-loop maps (Q21): 02the-pack B (2,517 vs 58) and 01yellow-brick-road A/B (1,759 vs 149, 764 vs 216).
  - On 02the-pack A it went the other way (1,648 vs 2,299).
  - Excluding those two maps: 7,862 vs 7,590 (+3.6%).
  - The mirror runs at 80 per team-game; we ran at 104 per game.

### match_metrics (h_treasure side, 140 games)
```
games 140  tributes 3814  mean tribute 23.5  small(<10) 579
  consumablesBought 1155 (8.2/game)  deaths_by_camp 169 (1.2/game)  deaths_by_champion 1593 (11.4/game)
  fuelExhausted 14550 (103.9/game)   gemsLost_to_camp 1005 (7.2/game) gemsLost_to_champion 12121 (86.6/game)
  wardPlacement 54509 (389.4/game)
```

### analyze_match --summary (wins vs losses, gate run)
| metric | wins (72) | losses (68) |
|---|---|---|
| gem lead r250 / r500 / r1000 | +26 / +75 / +172 | −6 / −63 / −155 |
| first tribute us / them | 161 / 196 | 198 / 222 |
| kills us / them | 16.1 / 7.7 | 7.4 / 15.3 |
| gem loss us / them | 66 / 113 | 123 / 66 |
| gold us / them | 5,850 / 3,663 | 3,600 / 5,817 |
| fuelExh us | 65.9 | 144.2 |

## Analysis session
### 1. Did the targeted mechanism change? Yes, on both fronts.
**A. Spawn-heal sink**, in deterministic reproductions with the same seeds and the same starter drafts as the diagnosis:

| Metric (team A vs starter-python) | Before (tb_merge_b) | A only | Final (A+chain+C) | Target |
|---|---|---|---|---|
| 02treasure-box engage turns on an on-spawn target (trace) | **1,194 / 1,829 (65%)**, 528 at full HP | 0 / 618 | **0 / 519** | ≈0 |
| 02treasure-box cdmg / mdmg (eval game) | 305,635 / 143,081 = **2.14** | 28,960 / 115,699 = 0.25 | 20,440 / 41,079 = **0.50** | < 0.6 |
| 02treasure-box largest enemy healingReceived | Tavi **101,180** | 1,000 | **1,220** | < 20k |
| 02treasure-box rounds to 1000 (eval / trace) | **r1897** / r1638 | r989 / r1673 | **r722 / r770** | ~r1000 |
| 00reverse-spiral cdmg / mdmg | 317,196 / 16,020 = **19.8** | 0.24 | **0.12** | < 0.6 |
| 00reverse-spiral largest enemy healing | Willow **311,376** | 720 | **900** | < 20k |
| 00reverse-spiral our gems in 2000 rounds | **186** | 761 | **819** | 1000 (not reached) |

- In the final traces, `spawn_healed` fired 131 (02treasure-box) and 130 (00reverse-spiral) times, and the turret zone was active in 72 and 109 champion-turns.
- On 02treasure-box the final config spends **61%** of alive turns inside the inner box (before: 6%), 18% in fights (before: 27%), and 12.3% walking to tribute (before: 15.8%).
- The cdmg/mdmg ratio of the final config is 0.5-0.8 rather than < 0.6 on every game. Monster damage collapses because clusters have 120 HP; absolute champion damage fell from 305,635 to about 20,000.
- **The Willow sink is gone too.** On 00reverse-spiral vs starter-python (Willow drafted), the largest enemy healing was 900 in the final config (a Vendetta) and 480 for the Willow in the A+delivery+chain+C game, against 311,376 before.

**B. Cluster-field economy, 02treasure-box, both sides:**

| Opponent | Champion: rounds to 1000 / altar-cluster clears / mean tribute | Final: rounds to 1000 / clears / mean tribute |
|---|---|---|
| starter-python | A r1897 / 15 / 27.0; B r1344 / 42 / 17.3 | A **r722** / **119** / 9.7; B **r687** / **130** / 9.3 |
| tb_aggro | A r1152 / 79 / 16.2; B r1548 / 1 / 33.8 | A **r590** / **118** / 9.2; B **r742** / **127** / 9.7 |
| tb_merge_b (mirror seat) | A W r1627 / 11; B L | gate: A **W r885** / 123 vs their 3; B **W r814** / 131 vs their 0 |

- These meet every 02treasure-box target: ≥ 60 inner clears, tribute sizes in the 8-15 band, and 1000 by ~r1000. They beat sub7anr's ladder pace (r995) and copy its play: first tribute r72 in the A+delivery+chain+C game vs the champion (sub7anr: r59).
- **Bag deaths.** Deaths while carrying ≥ 10 gems on 02treasure-box in the final config were 0 per game vs starter-python and tb_aggro, 1 and 5 vs the champion (screen), and 2 and 0 vs the champion (gate). Champion baseline across the eight diagnosis opponents: 0-5 per game. No 5-way split capture was observed locally, so the C mechanism is untested against the real failure.
- **The blind spot still applies.** No local opponent contests the cluster field the way sub7anr did. Against the champion, which only drifts in, the final config held the field 123-3 and 131-0.

### 2. Why A alone lost the first screen 16-24 to the champion
- **Divergence analysis.** For each game, `diverge2.py` finds the first round where any champion timeline differs from the mirror game.
- **Spawn-adjacent maps.** The A-only games depart at **r1-r5** on 00reverse-spiral, 00rushbait-v2, 02treasure-box and 01shortcut. Enemies on their spawn are in sight from turn 1 there, so the new logic fires at once.
- **Touching spawns (real flaw).** On 00reverse-spiral the spawns touch (d_ss = 1). The spawn-*adjacent* rule then also skips enemies that stand next to **our** spawn, where we heal just as well.
  - Mirror team A: 15-4 kills, 64,704 champion damage, W 531-159.
  - A-only as team A: 3-12 kills, 7,809 champion damage, L 321-741.
  - This is new hypothesis Q27b.
- **Drift elsewhere.** On other maps the games depart far earlier than the logic fires. On 00anvil the game departs at r28, while the instrumented trace shows the first `spawn_healed`/turret event at r426. The same logic with and without the trace wrapper gave 383-804 and 21-1004.
  - Small fuel differences move fuel-gated decisions: `build_static_fields` above 1M fuel, `choose_target` pruning at `FUEL_SCORE_FLOOR`.
  - The mirror game is chaotic, so a 40-game screen has a noise floor of several games (16/40 is 1.3 SD below 20).
- **Against the reference opponents A is clean.** It went 40-0 and 39-1. Its one loss was 00rushbait-v2 B vs tb_aggro, 660-1027, a touching-spawn map the champion won 1016-0. Many games were byte-identical to the champion's because the new code never fired. Average rounds fell 1470 → 1409 (starter) and 1427 → 1421 (aggro).

### 3. Why the delivery term was dropped despite the best head-to-head (27-13)
- **01shortcut collapses.** Both altars sit in walled boxes about 90-100 walking steps from the farm. The delivery term added ~100 to every group's cost (traced `choose_target` at r240-261: e.g. G2 value 52, cost 200 at distance 66). This swamped value/time, and the team thrashed between targets (7 → 2 → 7 → 8 → 7 → 19).
  - vs tb_aggro: **22** and **258** gems in 2000 rounds (champion: 1067 and 1024).
  - vs starter-python: 624 and 703 (champion: 1018 and 1003).
- **The same pattern on the other long-delivery maps:**
  - 02tangle lost both sides vs tb_aggro (champion won both);
  - 00road-of-riches 916 / 680 vs starter (champion 1028 / 1027);
  - adgato-gemcombat5 483 / 900 vs starter.
- **Why the head-to-head still looked good.** The champion shares our farming logic and cannot punish a stalled farmer. A real opponent that farms normally would. Against the champion, the delivery variant also won several maps on which it was *slower* than the champion against the references (00quarry: r1384 / r1842 vs tb_aggro, champion r1181 / r1273). So its head-to-head edge is not an economy gain; I did not chase the mechanism further. Kept as hypothesis Q27d (capped delivery).

### 4. Gate run: regressions and their causes
- **Net result.** 72/140 = 70 + 2. 64 games changed winner against the mirror seat: 33 gained, 31 lost. The 31 lost games, with the round they depart from the mirror:
  - 00breadcrumbs B@1, 00collision B@56, 00corners B@35, 00eight B@25, 00great-wall A@7, 00monolith B@58, 00packs B@28, 00pilgrimage B@106;
  - 00quadrants A@256, 00quarry B@109, 00reverse-spiral A@1, 00road-of-riches A@29, 00rushbait-v2 A@1, 00split A@45;
  - 01boss-battle A@57, 01broken-curve B@64, 01concentrated-wealth B@136, 01elk-arena B@93, 01hooks B@105, 01islands B@160, 01shortcut A@4, 01starvation B@96, 01the-farm B@618, 01yellow-brick-road A@6;
  - 02geodes A@90, 02tangle A@41, 02the-pack A@16, 02the-pond B@82;
  - adgato-gemcombat2 A@8, adgato-gemcombat4 B@153, adgato-gemcombat5 B@40.

  Most of these depart within the first ~100 rounds on maps where neither the spawn rules nor the chain bonus can apply that early. So they are drift: the same mechanism as §2, where the chain code's extra fuel in `build_static_fields` and the looser `target_order` bound shift fuel-gated decisions. The causes with structure behind them:
- **00breadcrumbs: gold starvation from the chain bonus (real, new).** The map is only single 0-strength gem clusters (22) and gold-only clusters (12). The chain bonus lifts every gem cluster to value ~28, while gold clusters stay at 5-20, so we never farmed gold.
  - Gold earned **628 and 40** (mirror 3,127 / 3,889).
  - Items bought **19 and 0**; "first item: None" as team B.
  - Lost every fight: K/D 4/19 and **0/21**.
  - The delivery variant, which reorders the values, earned normal gold there and won both sides.
  - Across maps with ≥ 4 chain-eligible groups, our gold is 0.88× the mirror seat's (3,157 vs 3,577), with the win count unchanged (25 vs 24). Elsewhere it is 1.02-1.05×.
  - On 02treasure-box we earn about 2,000 gold (mirror seat up to 11,387). That is harmless there because we finish by r885, but it would matter in a contested game. New hypothesis Q27c.
- **01yellow-brick-road A (0-0, gold 0 vs 0, so the tie went to team B) and 02the-pack A (0-0, gold 939 vs 1,658).** Neither map has a chain-eligible group, and neither game shows spawn fights. Both games fell into the **Q21 stuck loop** (1,759 and 1,648 fuel exhaustions) after drifting at r6 and r16. In the mirror the same loop hit the *other* seat. Not caused by the new logic, but it shows which side Q21 hits is drift-dependent.
- **00reverse-spiral A (562-604) and 00rushbait-v2 A (94-228).** Touching-spawn maps that depart at r1: the spawn-adjacent rule flaw from §2 (Q27b).
- **01shortcut A (359-883).** Our deaths rise here in every final-config game: 13 vs the champion; 11 and 9 vs tb_aggro (champion: 3 and 1). There were 13 bag deaths as team A and a 77.5-gem mean tribute vs tb_aggro A. The altar boxes sit inside a Monolith's range-5 zone, and both FAR_ALTAR_BANK and the turret avoid zone change the banking walks there. Not isolated further; logged with Q27d.
- **Guard: deaths on the six spawn-proximity maps vs tb_aggro.**
  - Ours 59 → **56** (A only 50, A+chain 55); theirs 223 → 110. The per-map exception is 01shortcut (3 → 11 and 1 → 9).
  - **The guard partly fails on enemy farming.** tb_aggro's gems on those 12 games rose **1,842 → 2,844**, and ours fell 11,961 → 11,187.
  - Almost all of the rise is two games:
    - **00rushbait-v2 B**, a touching-spawn map: tb_aggro went 0 → 1,027, a loss for us 710-1027 (A only also lost it, 660-1027);
    - 00gem-fields A: 298 → 804, still a win.
  - So engaging less near touching spawns *does* let the enemy farm there (Q27b).
- **Gains.** 02treasure-box (both seats: W r885 and W r814, against a mirror seat that lost as B) is the one clearly structural gain. It is backed by the same speed-up against both reference opponents. The other gained games depart early, e.g. 00lost-world B@28 (1005-521 at r994) and 02crossing B@45. Their reference-opponent finishes are mixed (00lost-world vs tb_aggro: A r1081 → r823, B r922 → r1221), so I count them as drift like the losses.

### 5. Methodology finding: identical logic does not replay identically under another bot name
- The final `h_treasure` is byte-identical in logic to `h_treasure_chainc`: one space in a comment differs, and so does the bot name. The engine seeds are identical (per map).
- On the 20 screen maps vs tb_merge_b, **26/40 games replayed identically, 14 differed, and 5 outcomes flipped**:
  - 00lost-world B;
  - 00quadrants A and B;
  - adgato-gemcombat5 A and B.
- 02treasure-box B went from r1474 to r814.
- The differing games are not confined to maps where the chain code runs: 02tangle has no chain-eligible group, while 00breadcrumbs (22) replayed identically.
- So "local games are deterministic" holds only for byte-identical bots under the same name. The 140-game gate has a noise floor of several games from renames or comment edits alone. Root cause unknown; candidates are heap-layout-dependent hashing (default `id()`-based hashes) and fuel metering in the non-release build. New hypothesis Q30.

### 6. Ladder ground truth
Not available: the candidate is not promoted, so there are no live treasure_box or reverse_spiral games. The ladder metric to watch, if a successor ships, is the cdmg/mdmg ratio (1.5-11.2 in all four high-sink games) and our tributes per game (0-30) on treasure_box.

## Verdict
**Inconclusive: mechanism confirmed, not promotable.**
- **Promotion gate:** fails (a). 72W-68L on all maps, Wilson lower bound 0.432, botFaults 0.
- **Targeted mechanisms: fixed.** Measured in deterministic reproductions:
  - on-spawn engagement 65% → 0%;
  - enemy spawn healing 101k / 311k → about 1k;
  - 02treasure-box 1000 by r590-r885 against every opponent (champion: r1152-r1897, or a loss);
  - 00reverse-spiral 186 → 819 gems vs starter-python.
- **Against the champion it is noise-level.** The champion never fights the sink the way ladder opponents do, which is the blind spot.
- **Two real side effects need fixing before merging:**
  - Q27b, the touching-spawn flaw of the spawn-adjacent rule;
  - Q27c, gold starvation on pure cluster maps.
- **Recommendation:** fix both and merge A + chain into the next combined candidate (Q24 lineage). Do not ship h_treasure alone.

## New hypotheses generated (for STRATEGIES.md)
- **Q27b: touching-spawn exception for the spawn-adjacent rule.**
  - Apply the `SPAWN_NEAR_KILL` skip only when we are not ourselves within 1 tile of our own spawn tiles (both sides heal there). Alternatively, apply it only when the spawn regions are ≥ 3 apart.
  - The on-spawn rule (heals at turn end) stays.
  - Evidence:
    - 00reverse-spiral A vs the champion, A only: 3-12 kills and 7.8k champion damage, vs 15-4 and 64.7k in the mirror;
    - the final config lost 00reverse-spiral A and 00rushbait-v2 A to the champion, both departing at r1;
    - 00rushbait-v2 B vs tb_aggro became a loss (710-1027; the champion won 1016-0) in both A-only and final.
- **Q27c: gold floor for the chain bonus.**
  - Count H.value (gems + 0.25 gold) of 0-strength neighbours instead of gems only; or keep normal gold weighting until the first Bruiser emblem; or let 0-strength gold groups chain too.
  - Evidence: 00breadcrumbs, gold 40 / 628 vs mirror 3,889 / 3,127, items 0 / 19, K/D 0/21 and 4/19. 02treasure-box earned about 2,000 gold vs 11,387 for the mirror seat.
- **Q27d: capped delivery term.**
  - `cost += min(DELIVER_CAP, DELIVER_W × altar_d × share/BANK_REF)` with a cap of about 0.5 × d, or apply the term only within the altar's walk component.
  - Evidence: the delivery variant was the strongest head-to-head screen (27-13, Wilson 0.52-0.80). Uncapped, it stalls on far-altar maps: 01shortcut 22 / 258 gems vs tb_aggro, plus 02tangle and 00road-of-riches.
  - Also check FAR_ALTAR_BANK and turret-avoid walks near Monolith-guarded altar rings (01shortcut deaths 3 → 11).
- **Q29: Willow heal-sink comps** (ladder fb40725d vs EXP'D, 01yellow_brick_road ratio 26.0 with Willow healing 189,390, 01elk_arena ratio 3.4 with Ryth healing 168,287).
  - Build an imitation opponent of EXP'D (Ryth, Vesper, Willow, Prism, Tavi), e.g. `lad_expd`.
  - Test whether the heal-aware chase guard (A4) removes the sink against a healer that is *not* on its spawn. Locally it took starter-python's Willow from 311k to under 1k healing, but no local opponent pairs a Willow with our farming logic.
- **Q30: evaluation noise floor and non-reproducibility.**
  - Identical logic under another bot name replayed 26/40 games identically, with 5 outcome flips. A candidate departs from the mirror in 135/140 games, mostly within the first 100 rounds.
  - Two parts:
    - (a) measure the null distribution once: a flags-off copy of the champion on all maps;
    - (b) find the nondeterminism source (release vs debug fuel metering; `id()`-hashed containers such as the sets of Vec2).
  - Without this, a ±5-game difference on 140 games cannot be attributed.
- **Q31: sub7anr-style imitation opponent for the blind spot.**
  - An opponent that sends Stellar plus Tavi into the 02treasure-box cluster field by r50 and fights at the gap with the other three.
  - Needed to verify that a successor *contests* the field rather than only farming it unopposed.
