# Experiment: h_teamclear, team clears of camp groups no champion can take alone (2026-11-01)

STRATEGIES Q26. Run on the cluster (Slurm `test` partition through `tools/onslurm.sh`, cambc 4.0.0 / engine 2.0.0). Candidate `bots/h_teamclear`; design notes in `bots/h_teamclear/NOTES.md`.

## Hypothesis
- **What:** `choose_target`'s camp-safety check only counts allies that already claim a group (`c`, from the shared-memory claim bytes).
  - A group that every champion rejects at `c = 0` is therefore never claimed and never cleared.
  - On 02gift-wrapping every group is "wrapped": a 3x3 ring of camps round one wall tile, or a 3x5 / 5x3 / 3x7 shape with strength 80-160 and HP 5,880-8,820. All 5 champions reject all 11 groups at base stats: REJECT-cycles 9.0-231 at `c = 0`, ok-direct at `c = 4` (census `matches/q26-census/02gift-wrapping.stdout.txt`).
  - So all 5 champions stand on spawn for 2,000 rounds.
  - Fix: let the team commit as a group (a team option in `choose_target`, a muster before waking the group). This should turn a guaranteed 0 into a race on any map with big groups.
- **Source: real ladder games.** Here a "team group" is one that every champion rejects alone at base stats but that passes the model with 4 allies (census definition). Counts come from `matches/ladder/summary`, joined with the census (`matches/q26-tc/tools/ladderjoin.py`).

  | match | map | opponent | result | team-group clears us/them | their gems |
  |---|---|---|---|---|---|
  | 4ed9456f | 02gift_wrapping | Spawn Campers | L 0-1028 | **0/18** | 0/1044 |
  | 64ffffc3 | 02gift_wrapping | sub7anr | L 16-1006 | **0/21** | 0/1064 |
  | 5316f73a | 00eight | Spawn Campers | L 76-1031 | 1/15 | 37/665 |
  | fb40725d | 02treasure_box | EXP'D | L 138-1005 | 5/21 | 158/867 |
  | 51bb63c8 | 02treasure_box | six seven | L 163-1005 | 8/19 | 261/637 |
  | 2fb86344 | 00quadrants | ez | L 767-1018 | 0/4 | 0/480 |
  | 2225b1cd | 00quadrants | EXP'D | L 982-1008 | 1/7 | 120/840 |
  | 761bfcb0 | 01boss_battle | FürFortnite | L 0-0 (gold) | 2/17 | 38/424 |
  | cb97461c | 02guardians | test | L 0-0 (gold) | 0/4 | 0/176 |

  - sub7anr cleared the first gift-wrapping group at r22 with all 6 bodies in an 18-round bout, then one group about every 45 rounds, reaching 1,006 at r940.
  - Spawn Campers fought in pairs or trios and reached 1,028 by r711, at the cost of 8 camp deaths.
  - Neither opponent touched groups 1-4, and none of the 30 sampled opponents cleared a monolith group.

## Setup
- **Candidate:** `bots/h_teamclear`, forked from the champion `tb_merge_b` with `tools/newbot.py`. Only `src/bot.py` differs (470-line unified diff, every change tagged `h_teamclear`). draft.py, main.py and randomness.py are byte-identical. The flags are at the top of bot.py.
  - **`TEAM_CLEAR` (1).** Where the solo check gives up (no direct pass, no hit-and-run within 4 cycles, or no escape tile), find the smallest k in [c+2, 1 + c + idle alive allies] for which the existing direct check passes with k-1 allies hitting.
    - Score it per champion: `value / (k * (d + ttk_k + 6 + 10))`.
    - Boss groups are excluded: strength > 250, HP ≥ 15,000, or a monolith.
    - A dead champion writes claim byte 255, so it is not counted as idle.
  - **`TEAM_TANK_CHECK`.** The team option also needs `s*ttk_k*0.7/k ≤ maxhp - s*(rng+1) - 80`. The aggro holder flees at about `s*(rng+1)+60` HP, so k champions can absorb only k times this budget.
  - **`TEAM_MUSTER` (2).** Before waking a full-HP sleeping group that I cannot clear alone, wait on the ring `dilate(tiles, rng+3) & ~dilate(tiles, rng)` until `team_need` champions are near.
    - "Near" counts allies seen in vision, plus claimers whose presence bit is set in the free shared byte 6 (v2).
    - The group is banned for 150 rounds after 15 rounds at the ring with too few claimers, or 30 rounds without enough champions near (v2; v1 used 20 and 60).
  - **`TEAM_WRAP_FIX`.** For the target group:
    - **(a)** Once it is awake, its unseen but believed-alive camps count as threats in range.
    - **(b)** The guess "no live camp visible within 3 of G.center → respawning" fires only when every believed-alive camp tile is in view.
    - **(c)** Its dead camp tiles may be stood on while it is alive.
  - **`TEAM_NEAR_DANGER` (3), off.** The nearest-champion camp model in the flee check.
- **Iterations** (single local games first, then screens):
  - **v0** (team check only):
    - The cascade picked group 3 (2 elks + 2 wolves, strength 160): 3 camp deaths (camp#42), 5,820 monster damage, no clear.
    - Vendetta died at 360 HP with `incoming=20`, because the far elk was hidden behind the centre wall.
    - Fixes: tank check and (a).
  - **v0b:**
    - Group 5 went to 1,350 HP by r35, then all 5 champions idled for 1,960 rounds next to a live wolf at (16,8) behind the wall. The (b) guess fired every turn, and the dead-tile push-back made them oscillate.
    - Fixes: (b) and (c).
    - Debug game `matches/q26-tc/dbg4`: **1,010-0 by r1119, 25 clears, 0 deaths, first clear r31.**
  - **v1 screen** (below).
    - On 02harvest a weak champion (need 2) waited 60-170 rounds at a ring while stronger claimers fought the same group out of its vision.
    - Other claimers were frozen on just-captured group 12's tiles. That is the Q21 respawn-rule 2-cycle, which h_respawnfix fixes, not this bot.
    - Fixes (v2 = final): shared presence bits; waits cut to 15/30.
- **Opponents and maps:**
  - The 22 maps with "team-feasible, never-cleared" groups (73 groups; `matches/q26-tc/tools/census.py`, output `census_out.txt`), both sides: vs tb_merge_b, starter-python and tb_aggro. The baselines are tb_merge_b vs starter-python and tb_merge_b vs tb_aggro.
  - Then all 70 maps vs tb_merge_b (the gate head-to-head).
  - Two ablations on all 70 maps.
  - The paired gauntlet.
  - One `--release` game.

## Results
```
SUMMARY h_teamclear vs tb_merge_b: 91W-49L (65%)  avg gems 715 vs 566  avg deaths 11.4 vs 12.9  botFaults(A) 0      [FINAL v2, --maps all, matches/ll1-h_teamclear-all, job 56779594]
SUMMARY h_tc_wraponly vs tb_merge_b: 82W-58L (59%)  avg gems 670 vs 613  avg deaths 13.1 vs 12.7  botFaults(A) 0    [ablation: TEAM_WRAP_FIX only, --maps all, matches/ll1-h_tc_wraponly-all, job 56780236]
SUMMARY h_tc_nowrap vs tb_merge_b: 64W-76L (46%)  avg gems 631 vs 653  avg deaths 13.8 vs 11.6  botFaults(A) 0      [ablation: team clear without TEAM_WRAP_FIX, --maps all, matches/ll1-h_tc_nowrap-all, job 56780100]
SUMMARY h_teamclear vs starter-python: 41W-3L (93%)  avg gems 824 vs 74  avg deaths 2.5 vs 34.4  botFaults(A) 0     [v2, 22 maps, matches/q26-scr2-tc-sp, job 56779596]
SUMMARY h_teamclear vs tb_aggro: 42W-2L (95%)  avg gems 847 vs 127  avg deaths 4.8 vs 19.4  botFaults(A) 0         [v2, 22 maps, matches/q26-scr2-tc-aggro, job 56779593]
SUMMARY tb_merge_b vs tb_aggro: 39W-5L (89%)  avg gems 725 vs 193  avg deaths 4.5 vs 17.1  botFaults(A) 0          [baseline, 22 maps, matches/q26-scr2-tbm-aggro, job 56779593]
SUMMARY tb_merge_b vs starter-python: 40W-4L (91%)  avg gems 746 vs 83  avg deaths 2.5 vs 36.0  botFaults(A) 0      [baseline, 22 maps, matches/q26-scr-tbm-sp, job 56777520]
SUMMARY h_teamclear vs tb_merge_b: 28W-16L (64%)  avg gems 726 vs 508  avg deaths 9.5 vs 11.0  botFaults(A) 0       [v1 screen, 22 maps, matches/q26-scr-tc-tbm, job 56777837]
SUMMARY h_tc_nomuster vs tb_merge_b: 28W-16L (64%)  avg gems 710 vs 588  avg deaths 11.3 vs 10.3  botFaults(A) 0     [v1 variant (1) only, 22 maps, matches/q26-scr-nomuster-tbm, job 56777521]
SUMMARY h_tc_neardanger vs tb_merge_b: 23W-21L (52%)  avg gems 691 vs 589  avg deaths 11.5 vs 11.0  botFaults(A) 0   [v1 variant (1)+(2)+(3), 22 maps, matches/q26-scr-neardanger-tbm, job 56778141]
SUMMARY h_teamclear vs starter-python: 43W-1L (98%)  avg gems 819 vs 94  avg deaths 2.7 vs 36.8  botFaults(A) 0     [v1, 22 maps, matches/q26-scr-tc-sp, job 56777519]
GAUNTLET h_teamclear: 164/200 (82%) on maps=sprint     [job 56780237; tb_merge_b baseline 158/200]
```

### Gate (LOOP.md §4)
| Part | Result |
|---|---|
| (a) head-to-head | **91/140 ≥ 82.** 95% Wilson interval 0.568-0.724; botFaults 0. |
| (b) paired gauntlet | **164/200 vs the champion's 158/200.** Per opponent (cand/champ): sf_bank 39/37, tb_merge_a 20/20, tb_aggro 39/40, imit_test 32/34, lad_vcst 34/27. Worst delta −2, within the ≤ 4 allowed. |
| (c) robustness | **Release game clean.** `cambc run h_teamclear tb_merge_b --map 02gift-wrapping --release` gave 1002-0, identical to the eval game (r900), with 0 crashes and 0 `bot error` lines. **fuelExhausted is mixed:** 97.8/game vs 73.5 in the head-to-head, but 77.9 vs 77.0 on the 200-game gauntlet pool. See the fuel section. |
| (d) mechanism | **Confirmed**, with an attribution caveat (see the ablations). |

### match_metrics (head-to-head, 140 games)
```
h_teamclear: tributes 3869  mean 25.9  deaths_by_camp 167 (1.2/game)  deaths_by_champion 1424 (10.2/game)  fuelExhausted 13685 (97.8/game)  gemsLost_to_champion 10814 (77.2/game)
tb_merge_b : tributes 3232  mean 24.5  deaths_by_camp 160 (1.1/game)  deaths_by_champion 1645 (11.8/game)  fuelExhausted 10290 (73.5/game)  gemsLost_to_champion 12299 (87.8/game)
```

### analyze_match --summary, wins (91) vs losses (49)
| metric | wins | losses |
|---|---|---|
| gem lead r250 / r500 / r1000 | +24 / +75 / +179 | +4 / −38 / −144 |
| first tribute us / them | 152 / 204 | 201 / 200 |
| clears us / them | 49.8 / 38.2 | 47.6 / 59.6 |
| kills us / them | 14.4 / 7.1 | 6.9 / 15.9 |
| camp deaths us | 1.1 | 1.3 |
| monster damage us / them | 96,037 / 62,251 | 62,395 / 88,093 |
| fuelExh us | 97.9 | 97.5 |

## Analysis session

### Did the targeted mechanism change? Yes
**02gift-wrapping, our side** (final run unless noted):

| | Mirror (tb_merge_b) | h_teamclear A | h_teamclear B |
|---|---|---|---|
| Result | 0-0, team B wins the tiebreak | **W 1002-0 (r900)** | **W 1032-0** |
| Our clears / first clear | 0 / none | 20 / r32 | 22 / r27 |
| Our first tribute | none | r83 | r76 |
| Our monster damage | 0 | 128,190 | 156,665 |
| Tributes / camp deaths | 0 / 0 | 39 / 0 | 43 / 2 |
| Opponent clears | 0 | 0 | 1 |

- **Against different-logic opponents** (22-map screens):

  | Opponent | Bot | Side A | Side B | Clears us vs them (A, B) |
  |---|---|---|---|---|
  | starter-python | tb_merge_b | 0-80 | 0-80 | 0 vs 5, 0 vs 5 |
  | starter-python | h_teamclear | 1000-32 | 1058-64 | 17 vs 5, 25 vs 7 |
  | tb_aggro | tb_merge_b | 0-1030 | 0-1002 | 0 vs 23, 0 vs 17 |
  | tb_aggro | h_teamclear | 1017-63 | 1104-200 | 18 vs 5, 24 vs 6 |

  The tb_aggro rows reproduce the ladder loss locally: an opponent that clears the wrapped groups wins 1000-0 against the champion.
- **Per-clear participation** (`matches/q26-tc/tools/engage.py`, final A game):
  - r32, group 5 (4 wolves): 27-round bout. All 5 champions dealt damage (855 / 1,400 / 1,545 / 431 / 1,648). Damage taken was 0/640/360/120/40. Capture split 4 ways, 4 gems each.
  - r65: group 9. r109: group 7 (44 gems, split 11×4).
  - r253 and r386: group 0 (2 elks + 14 gem clusters, 128 gems, split 44/42/42).
  - **Comparison with the real opponents:** we made our first clear at r27-32 and reached 1,000 by r900. sub7anr made its first at r22 and reached 1,006 at r940; Spawn Campers reached 1,028 at r711.
- **Capture split over all 89 target-group clears in the 140 games:** 1 champion 39, 2 champions 14, 3 champions 6, 4 champions 19, 5 champions 6, none within 12 rounds 5.
  - Early wrapped-group clears split 3-5 ways.
  - Later, items make some groups solo-able.
- **Coverage of the 73 team-feasible, never-cleared groups** (22 maps, 2,787 gems per clear; `matches/q26-tc/tools/q26metrics.py`):

  | Run | Distinct groups cleared ≥ 1 | Clears | Gems |
  |---|---|---|---|
  | tb_merge_b mirror | 0/73 | 0 | 0 |
  | **h_teamclear, final all-maps run** | **33/73** | 89 | **4,048** |
  | tb_merge_b, as the opponent in the same games | 13/73 | 20 | 808 |

  - **Cleared, per map:** 02gift-wrapping 10/11 (42 clears, 2,174 gems); 01boss-battle 7/14; 00corners 2/2; 00swirl 2/4; 02treasure-box 2/2; 00expanse, 00great-wall, 00lost-world, 01corridors, 01fracture and 02crossing 1/1 each; 00pilgrimage, 00reverse-spiral, 01shortcut and 01the-farm 1 each.
  - **Never cleared:**
    - 00quadrants: the 12-gem-cluster + golem group;
    - 00road-of-riches, 01big-world, 01islands and 02harvest: 2 groups each;
    - 01yellow-brick-road: 8 groups, frozen by Q21;
    - 02guardians: 4 groups (a no-tribute map).
  - In the 22-map screens: 39/73 vs tb_merge_b (v1); 26/73 vs starter-python and 32/73 vs tb_aggro (v2). The baselines were 17/73 for tb_merge_b vs starter-python and 17/73 for tb_merge_b vs tb_aggro.
- **The boss exclusion holds:** no monolith or golem-stack group was team-assaulted (structure gate).

### Attribution: the ablations show two effects
| Bot (vs tb_merge_b, 140 games) | Wins | 22 targeted maps | 48 other maps | Target-group clears / distinct |
|---|---|---|---|---|
| h_tc_nowrap (team clear, no wrap fixes) | 64 | 14/44 | 50/96 | 47 / 22 |
| h_tc_wraponly (wrap fixes only) | 82 | 28/44 | 54/96 | 51 / 24 |
| **h_teamclear (both)** | **91** | **30/44** | **61/96** | **89 / 33** |

- **About 12 of the +21 games over the 70-70 mirror baseline come from TEAM_WRAP_FIX alone.**
  - Its parts (b) and (c) fix the same mechanisms as Q21's h_respawnfix: its (d), the unseen-alive guess, and its (a), the dead-tile push-back. h_respawnfix scored 92/140 on its own.
  - The fixes act on every target group, not only team targets.
- **The team bootstrap adds about 9 more games (82 → 91), plus 38 target-group clears and 2,174 gems on 02gift-wrapping.**
  - +9 is about 1.5-2 standard deviations of the fuel-divergence noise, so the win count alone does not establish it.
  - The mechanism metrics do.
- **Team clears without the wrap fixes are harmful (64/140, 14/44 on the targeted maps).** The team commits to wrapped or long groups and then freezes there, beside hidden live camps or on dead tiles.

### Losses (49): why they were lost
- **Classification** (from the stats JSONs):
  - 23 fight losses (enemy kills ≥ ours + 5);
  - 23 farm/tribute races;
  - 3 0-0 gold tiebreaks: 01boss-battle A, 02the-pack A, 00stampede B.

  14 of the 49 losses are on the targeted maps.
- **Maps lost on both sides:** 00anvil, 00contest, 00galaxy, 01elk-arena, 01starfish, 01starvation, 02famine, 02geodes. These are fight-decided maps where the champion's own mirror and the sibling candidates swing just as wildly:
  - 01elk-arena: mirror 0-1008 (K/D 6/47); h_respawnfix lost both sides with K/D 13/44 and 15/50.
  - 01starfish: mirror 51-1062 (4/45); h_respawnfix lost both sides.
  - 00galaxy: a traced local game (`matches/q26-tc/00galaxy`, debug copy `bots/dbg_tc`) logged **0 team picks and 0 muster turns**. The team logic is inactive there, so the losses are fuel-divergence re-rolls.
  - 02geodes: the trace showed 13 team picks, 235 muster turns and 3 bans, and the traced game was won.
- **Targeted-map losses:**
  - 00corners A (307-1014): we led 285-201 at r750, then stalled. The traced copy also lost; the team logic was idle after r500, and the stall was in tribute-path walking.
  - 02harvest A (228-819): mid-game stall; v1 trace above (presence bits and the Q21 freeze).
  - 00swirl B: a fight loss, K/D 10/43.
  - 00quadrants A: a race, 480-1000 at r832.
  - 01boss-battle A: a gold tiebreak (see below).
  - 01yellow-brick-road B: 0-8, the Q21 freeze.
- **No-tribute maps** (01boss-battle, 02guardians, 02the-pack):
  - Team clears hand out gems that can never be banked, and tb_merge_b then loops on its do_tribute path. Example: the 01boss-battle B screen game vs starter-python made 0 clears after r160, while the carriers held 12-24 gems each.
  - Here gold, not gems, decides the game; h_goldtie's `no_tribute` valuation is the right fix.
  - v1 lost 01boss-battle 0-2 to tb_merge_b on gold (4,155 vs 4,405 and 4,133 vs 4,469). The final run went 1-1.

### Surprising wins
- 02gift-wrapping ×2 (structural 1000-0).
- 02crossing, 02treasure-box, 01shortcut, 01the-farm, 01corridors and 01fracture were won on both sides. Each map has 1-2 target groups cleared 1-3 times.
- The other maps won on both sides (00rows, 00split, 00eight, 00monolith and others) mostly carry the wrap-fix (Q21-like) gain; see the ablation.

### Regressions elsewhere and their cause
- **No systematic regression.**
  - On the 48 non-targeted maps the record is 61/96, with pair patterns WW 21, WL 19 and LL 8.
  - The LL maps are fight maps (see above).
- **Fuel.**
  - fuelExhausted is 97.8/game vs 73.5 in the head-to-head, but the excess is concentrated:
    - median per-game difference +1 (higher in 75 games, lower in 59, equal in 6);
    - the top 10 games hold all of the +3,395 excess;
    - **02the-pack B alone: 2,370 vs 223.** That is the no-tribute do_tribute loop, about 1,000/side in the mirror. 01yellow-brick-road A gave 611 vs 198 (Q21 freeze).
  - **Per-turn fuel is equal.** Decoding the kept `team-*.fuel` files (13-byte header, then little-endian u64 fuel-used per champion turn; `matches/q26-tc/tools/fuelfile.py`) over 1.03M turns per bot:

    | | Mean | Median | p95 |
    |---|---|---|---|
    | h_teamclear | 1,088,575 | 1,085,493 | 2,004,215 |
    | tb_merge_b | 1,094,365 | 1,076,795 | 2,017,675 |

  - On the gauntlet pool: 77.9 vs 77.0 per game.
- **Camp deaths:**
  - head-to-head 1.19 vs 1.14 per game;
  - targeted maps 2.07 vs 1.95, against a mirror baseline of 2.18 on the same maps;
  - gauntlet 0.79 vs 0.55 (+0.24, a small increase worth watching).
  - The muster helps: v1 with muster had 91 camp deaths in 44 games, vs 113 without it.

## Verdict
**Kept: it passes gate (a) 91/140 and gate (b) 164 ≥ 158.** The release game is clean, and the mechanism is confirmed:
- 02gift-wrapping went from 0 clears to about 20 per game, and 0-0 to 1000-0;
- coverage of the 73 team-only groups rose from 0/73 to 33/73 (4,048 gems);
- the cascade has all 5 champions in the first bout.

**Two caveats for the orchestrator:**
1. **Overlap with Q21.** About 12 of the 21 extra wins come from TEAM_WRAP_FIX (b)/(c), which duplicates h_respawnfix's (d)/(a); h_respawnfix scored 92/140 alone. Standalone promotion of h_teamclear would ship a partial Q21 fix in place of the fuller gated one.
   - **Recommended next step:** merge `TEAM_CLEAR + TEAM_TANK_CHECK + TEAM_MUSTER + TEAM_WRAP_FIX(a)` and the claim/presence bytes into the Q24 combo that carries `RESPAWN_FIX`. Keep wrap (b)/(c) only if RESPAWN_FIX's (d)/(a) don't cover the wrapped-group case; they should, because both key on the engine state and dead tiles. Then gate the merge.
   - Team clears without the wrap fixes lose (64/140). **Never ship TEAM_CLEAR without a Q21-class fix.**
2. **Gate (c) fuel, strictly read, is not met** in the head-to-head aggregate (97.8 vs 73.5). Per-turn fuel is identical, and on the gauntlet pool fuelExhausted is equal (77.9 vs 77.0). The excess comes from known tb_merge_b loops (no-tribute do_tribute on 02the-pack, the Q21 freeze) that h_goldtie and h_respawnfix remove.

## New hypotheses generated
- **Merge Q26 into the Q24/Q21 combo** (`TEAM_CLEAR`, `TEAM_TANK_CHECK`, `TEAM_MUSTER`, `TEAM_WRAP_FIX(a)`, dead mark 255, presence byte 6).
  - Evidence: the ablations (64 / 82 / 91) and h_respawnfix 92/140.
  - Why: the team bootstrap only pays with a freeze fix underneath, and the Q21 fix is the gated one.
- **Gold-valued team targets on no-tribute maps** (with h_goldtie's `no_tribute`).
  - Evidence: on 01boss-battle, team clears of gem groups left every carrier holding unbankable gems (0 clears after r160 in the screen game vs starter-python). v1 lost 0-2 on gold to tb_merge_b.
  - Why: gold decides there, and the team option currently ranks by gems.
- **Heterogeneous team check.** Publish each champion's tank budget (or HP class) in shared memory, and size k from the actual teammates rather than my own stats.
  - Evidence: 1000-HP champions find group 0 (2 elks, 128 gems) tank-infeasible, while Marcella and Ryth (1,200 HP) accept it at k=5. Group 0 was first cleared only at r253 (A) and r371 (B, a 5-round finish by Vendetta alone, who took all 128 gems), against sub7anr's ×5 clears from early on.
  - Commit timeouts banned groups 3 times in the 02geodes trace.
  - Why: a faster first clear of the most valuable group.
- **Hidden-camp threats from stale beliefs.** WRAP (a) treats unseen, believed-alive camps of an awake target group as threats. If an ally killed them out of my view, the belief is stale.
  - Evidence: the 00corners trace showed `inc 180, hit_hp 0` lines on a tribute walk (cause not fully isolated).
  - Fix: share kills through shared memory (a per-group alive bitmask), or decay the belief once the group's engine state reads RewardAvailable or Respawning.
  - Why: avoids phantom retreats.
- **Deliberate aggro rotation in team fights.** The aggro holder steps out at its flee threshold while the next-nearest steps in.
  - Evidence: groups 1-4 (strength 120-160) are cleared only late, once items arrive (group 1 at r579 vs starter-python, group 3 at r1086 in debug game 4). No ladder opponent cleared them either.
  - Why: unlocks 6-wolf and 2-elk+2-wolf groups (8,460-8,820 HP) early.
- **The nearest-champion flee model (3) is rejected for now:** 23-21 and 2.30 camp deaths/game, vs 28-16 and 2.07 without it on the same screen.
