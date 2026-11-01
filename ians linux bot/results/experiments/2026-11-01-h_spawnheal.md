# Experiment: h_spawnheal, Q27 refined (Q27b touching-spawn fix + Q27c gold floor) on q24_combo (2026-11-01, cluster)

STRATEGIES Q27 refined (Q27b, Q27c). Stages (LOOP.md 3a-d): implement, targeted screens (v1, then two iterations: v2, v3), all-maps head-to-head (= gate a), analysis session. The verdict is at the end.

**Result in one line.** The spawn-heal mechanism works where it is aimed: on-spawn engage turns drop from 47-63% to 0%, the enemy's spawn healing falls from 26k-69k to about 1-4k, and 02treasure-box reaches 1000 about twice as fast. The touching-spawn flaw (Q27b) is gone: 4/4 touching-spawn games won against q24_combo, against 2/4 for the mirror seat. But the all-maps head-to-head is **74W-66L (53%)**, below the 82/140 gate, and only **47/100 on the 50 maps outside the screen**. The gold floor (Q27c) holds gold on average (gold at r500 is 1,122 against 1,099 for the mirror seat on the 20 chain maps) but does not save 00breadcrumbs. **Inconclusive: mechanism confirmed, not promotable.**

**Champion change during the run.** The task named q24_combo as champion, and every comparison here is against q24_combo. While these jobs ran, the other workflow promoted **c2_respawn** (commit fac3b36, 89/140 vs q24_combo). Any follow-up should fork c2_respawn, not q24_combo.

## Hypothesis
- **What:** port h_treasure's mechanism A (spawn-heal-aware fighting) and its cluster-chain target value (B) onto the current champion, with the two fixes the h_treasure report asked for.
  - **A. Spawn-heal-aware fighting.** An enemy on its own spawn tile heals to full at its turn end (SPAWN_HEALING 1.0). Fighting it is useless unless one round of our damage kills it.
    - h_treasure's version cut on-spawn engage turns on 02treasure-box from 65% to 0%.
    - Its gate run was dragged down by a flaw in its spawn-*adjacent* rule.
  - **Q27b, the fix for that flaw.** When the two spawn regions touch, the enemy's spawn-adjacent zone covers our own spawn exit, where we heal too.
    - h_treasure lost 00reverse-spiral A and 00rushbait-v2 A to tb_merge_b, both diverging at r1.
    - The fix: exempt that case, or apply the rule only to enemies standing *on* their spawn.
  - **B + Q27c.** The chain bonus values a dense field of 0-strength gem clusters.
    - In h_treasure it starved gold on 00breadcrumbs: 40 and 628 gold, against 3,889 and 3,127 for the mirror; 0 and 19 items.
    - The fix: put a gold floor on the bonus, or leave it out if it does not help.
  - h_treasure's far-altar banking (C) and the delivery term are **not** ported. C was implicated in the 01shortcut deaths; delivery was already dropped.
- **Source:**
  - `results/experiments/2026-11-01-h_treasure.md` (72W-68L vs tb_merge_b, inconclusive).
  - **Ladder ground truth** (`results/ladder-games.jsonl`). The live bots are **2W-6L on 02treasure_box**:
    - v2 is 2-3;
    - v3 (= q24_combo) is 0-3: 19-1015, 588-734 and 0-1002.
    - The opponents reached 1000 at r740-r1322 (Mein Kraft: Vesper/Tavi/Varg/Willow/C&I at r740).

## Setup
- **Candidate:** `bots/h_spawnheal`, made with `python3.12 tools/newbot.py q24_combo h_spawnheal`.
  - Only `src/bot.py` differs: 2,697 → 2,912 lines, 218 changed lines, every change behind a flag in the "h_spawnheal" block at the top.
  - `main.py`, `draft.py` and `randomness.py` are byte-identical to q24_combo.
  - Nothing keys on map names.
  - Details are in `bots/h_spawnheal/NOTES.md`.
- **Port of A** (h_treasure's code, adapted to q24_combo's `handle_enemies`, which runs after `group_balance`):
  - `spawn_healed()`;
  - the "all near enemies are spawn-healed → `return False`" static-hazard rule;
  - the `adjacent_melee` skip;
  - `HEAL_CHASE_GUARD`;
  - the turret avoid zone (`SPAWN_AVOID`), used by the farming, capture, respawn-wait and `do_tribute` walks.
- **Q27b, two parts:**
  - **Static:** `SPAWN_TOUCH_D = 3`.
    - If the spawn regions are within Chebyshev 3, the spawn-adjacent rule and the turret zone are off for the game. The on-spawn rule stays.
    - Spawn-to-spawn distances on the 70 local maps were computed from the h_treasure diagnosis map dumps. Only 00reverse-spiral and 00rushbait-v2 qualify (d_ss = 1). 02treasure-box has d_ss = 4, then 00quadrants at 6 and 00gem-fields at 7; the other 65 maps are at 11 or more.
  - **Dynamic:** `SPAWN_SELF_EXEMPT`, which turns the spawn rules off while we stand on or next to our own spawn. It was on in v1 and **off from v2 on** (see §2).
- **v2 addition, `SPAWN_NEAR_EVIDENCE`.** The spawn-adjacent rule assumes the enemy steps back to heal, so it applies only to an enemy we have *seen* heal at its spawn:
  - its HP rose by more than 50 while it stood on or next to its spawn;
  - we saw it again within 3 rounds;
  - and this happened in the last 200 rounds.
- **Port of B with Q27c:**
  - `CHAIN_VALUE` uses h_treasure's `build_nbrs` and bonus unchanged, and is off under `no_tribute`. The `target_order` bound is loosened only while the chain is on.
  - The gold floor `CHAIN_GOLD_FLOOR`: the chain bonus runs only while this champion's earned gold is at least `CHAIN_GOLD_RATE × (round − CHAIN_GOLD_GRACE)`.
  - Earned gold comes from `gold_tick()`, which sums the positive deltas of gold on hand. `shop()` credits income before buying and resets the reference after.
  - The rate is anchored on the q24 mirror, where median per-champion income is 0.58 gold/round.
- **Screen variants** (all `tools/newbot.py` forks of h_spawnheal; flags only):

| Variant | Spawn rules | Chain |
|---|---|---|
| `sh_v1a` | self-exempt **on**, touch D 3, adjacent rule always on | off |
| `sh_v1b` | as v1a | on, floor 0.3 gold/round, grace 100 |
| `sh_v2a` | self-exempt **off**, adjacent rule evidence-gated | off |
| `sh_v2b` (**final**) | as v2a | on, floor **0.6**, grace 100 |
| `sh_v3` | as v2a | on, floor 0.6, grace **0** |

- **Final:** `h_spawnheal` = `sh_v2b`, byte-identical `src/`.
- **Screen maps:** the 20 affected maps from the h_treasure report. These include all four maps the task named: 02treasure-box, 00reverse-spiral, 00rushbait-v2 and 00breadcrumbs. The other 16 are 00quadrants, 00gem-fields, 01shortcut, 00lost-world, 00anvil, 00quarry, 01broken-curve, 02crossing, 00road-of-riches, 02the-pond, 01islands, 00stampede, adgato-gemcombat5, 01corridors, 02tangle and 02arena.
  - Each variant played both sides against `q24_combo` and against `starter-python` (different logic), so 80 games per variant.
- **Baselines:**
  - **vs q24:** the q24_combo mirror on all maps, `matches/plc-mirror` (placebo workflow). The placebo report shows it game-for-game identical to its rerun `plc2-mirror`. Its A and B games are identical, so the null result is exactly 20/40 on the screen and 70/140 on all maps.
  - **vs starter:** `q24_combo vs starter-python` on the 20 maps (`q27r-base-sp`).
- **Jobs.** All ran on the free Slurm `test` partition via `tools/onslurm.sh -c 24 -m 16G -t 00:20:00`, `eval.py ... --jobs 16 --keep`, cambc 4.0.0 / engine 2.0.0.

| Job | Contents | Tag(s) |
|---|---|---|
| 56816386 | baseline q24_combo vs starter-python | `q27r-base-sp` |
| 56816385 | v1a vs q24_combo, vs starter-python | `q27r-v1a-q24`, `q27r-v1a-sp` |
| 56816387 | v1b vs q24_combo, vs starter-python | `q27r-v1b-q24`, `q27r-v1b-sp` |
| 56820868 | v2a | `q27r-v2a-q24`, `q27r-v2a-sp` |
| 56820867 | v2b | `q27r-v2b-q24`, `q27r-v2b-sp` |
| 56821545 | v3 | `q27r-v3-q24`, `q27r-v3-sp` |
| **56822272** | **gate:** `tools/onslurm.sh -c 24 -m 16G -t 00:20:00 -J h_spawnheal -- python3.12 tools/eval.py h_spawnheal q24_combo --maps all --jobs 16 --keep --tag q27r-all` | `q27r-all` |

- **Traces** (local `cambc run`, at most 2 at a time).
  - **Trace copies:** `dbg_q24sh_trace` (q24_combo), `dbg_sh_trace` (= v1b), `dbg_sh2_trace` (= v2b). Each is bot.py byte-identical to its source plus a wrapper `main.py`.
  - **The wrapper hooks** `write_focus` and `strike`. It logs one `E round slot flag hp` line per engage turn: flag 2 = target on its own spawn, 1 = next to it.
  - **It also counts:**
    - `spawn_healed` skips;
    - chase-guard bans;
    - marked heal-hoppers;
    - target and gold state every 25 rounds.
  - **Prints** go through `cambc.debug_block`.
  - **Output:** `matches/q27r/tr/<name>/us.txt`.
  - **Single-flag copies:** `dbg_sh_trace_ncg` (chase guard off) and `dbg_sh2_trace_nav` (turret zone off).
- **Analysis scripts** (scratch):
  - per-game comparison against the mirror seat or baseline game;
  - first-divergence round from the per-round timelines;
  - spawn distance and chain eligibility from the map dumps;
  - gold and gem pace at r500.

## Results (verbatim)
Screens, 20 maps × both sides:
```
SUMMARY q24_combo vs starter-python: 40W-0L (100%)  avg gems 916 vs 84  avg deaths 3.1 vs 32.7  botFaults(A) 0      [baseline]
SUMMARY sh_v1a vs q24_combo: 18W-22L (45%)  avg gems 659 vs 716  avg deaths 8.8 vs 9.3  botFaults(A) 0
SUMMARY sh_v1a vs starter-python: 40W-0L (100%)  avg gems 918 vs 94  avg deaths 3.5 vs 30.0  botFaults(A) 0
SUMMARY sh_v1b vs q24_combo: 21W-19L (52%)  avg gems 688 vs 668  avg deaths 8.9 vs 8.6  botFaults(A) 0
SUMMARY sh_v1b vs starter-python: 39W-1L (98%)  avg gems 863 vs 79  avg deaths 3.4 vs 28.0  botFaults(A) 0
SUMMARY sh_v2a vs q24_combo: 18W-22L (45%)  avg gems 672 vs 698  avg deaths 9.2 vs 9.6  botFaults(A) 0
SUMMARY sh_v2a vs starter-python: 40W-0L (100%)  avg gems 901 vs 76  avg deaths 4.0 vs 31.1  botFaults(A) 0
SUMMARY sh_v2b vs q24_combo: 27W-13L (68%)  avg gems 767 vs 637  avg deaths 8.7 vs 9.6  botFaults(A) 0
SUMMARY sh_v2b vs starter-python: 39W-1L (98%)  avg gems 898 vs 79  avg deaths 3.8 vs 28.9  botFaults(A) 0
SUMMARY sh_v3 vs q24_combo: 26W-14L (65%)  avg gems 747 vs 645  avg deaths 8.5 vs 9.5  botFaults(A) 0
SUMMARY sh_v3 vs starter-python: 39W-1L (98%)  avg gems 896 vs 91  avg deaths 3.8 vs 30.0  botFaults(A) 0
```
Gate head-to-head, all 70 maps × both sides:
```
SUMMARY h_spawnheal vs q24_combo: 74W-66L (53%)  avg gems 683 vs 652  avg deaths 10.1 vs 10.1  botFaults(A) 0
```
- **Gate (a): FAIL.** 74/140 is below the 82 needed. The 95% Wilson interval is 0.446-0.609. botFaults is 0.
- **Gates (b) and (c)** (gauntlet, release run) were not run, because (a) failed.
- **Fuel:** `match_metrics` fuelExhausted is **1,010 (7.2/game)** against 1,005 (7.2/game) for the q24 mirror. No fuel regression.
- **Against the mirror seat:**
  - 27 games gained and 23 lost;
  - 22 games byte-identical to the mirror;
  - for the 118 that diverged, the median first-divergence round is 32.5.
- **Split by map set:**

| Map set | Games | Candidate wins | Mirror-seat wins | Gold, candidate / mirror |
|---|---|---|---|---|
| Screen maps that are chain-eligible | 24 | 16 | 12 | 0.94 |
| Screen maps, other | 16 | 11 | 8 | 1.04 |
| **Non-screen**, chain-eligible | 16 | 9 | 8 | 1.01 |
| **Non-screen**, other | 84 | 38 | 42 | 0.99 |
| **All non-screen maps** | **100** | **47** | **50** | |

"Chain-eligible" means at least 4 groups with a 0-strength gem group within Chebyshev 6, which is 20 maps.

- **The 40 screen-map games of the gate are byte-identical to the `sh_v2b` screen games** (40/40: same outcome, scores and per-round timelines). So the gate's 27/40 on those maps is the screen result itself, and the gate's new information is the 47/100 elsewhere.

`analyze_match --summary matches/q27r-all` (74 wins / 66 losses):

| metric | wins | losses | mirror (W / L) |
|---|---|---|---|
| gem lead r500 / r1000 | +69 / +136 | −30 / −130 | |
| kills us / them | 12.8 / 6.6 | 4.6 / 11.7 | 13.2 / 5.5 |
| gold us / them | 5,882 / 3,985 | 4,859 / 6,858 | 6,634 / 4,303 |
| first tribute us | 218 | 173 | 183 / 176 |
| fuelExh us | 7.5 | 6.9 | 7.3 / 7.0 |

## Analysis session
### 1. Did the targeted mechanism change? Yes.
**Traces.** The same seeds and drafts, `dbg_q24sh_trace` (before) and `dbg_sh2_trace` (final logic). The q24 trace reproduced the eval game exactly on 02treasure-box A vs starter: 1032-328, r1888.

| Game (us) | On-spawn engage turns | Largest enemy healingReceived | Rounds to 1000 / our gems | cdmg / mdmg |
|---|---|---|---|---|
| 02treasure-box A vs starter, before | **1,112 / 2,036 (55%)** | Vendetta **69,381** | **r1888** | 1.80 |
| same, v1 (self-exempt on) | 124 / 675 (18%), all r32-200 | 5,770 | r1127 | 0.49 |
| same, **final** | **0 / 515 (0%)** | **810** | **r760** | 0.53 |
| 02treasure-box B vs starter, before | 585 / 1,243 (47%) | Stellar 26,303 | r1630 | 0.83 |
| same, **final** | **0 / 392** | 1,960 | **r777** | 0.45 |
| 00reverse-spiral A vs starter, before | 379 / 597 (63%) | Tavi 27,905 | 634 gems in 2000 | 0.59 |
| same, v1 | 5 / 362 (1%) | 1,020 | r1993 | 0.19 |
| same, **final** | 0 / 98 | 905 | 821 gems in 2000 | 0.03 |
| 02treasure-box A vs q24, before | 46 / 670 (7%) | 23,602 | L 524-1053 | 0.33 |
| same, final (trace) | 0 / 764 | 26,867 | W 719-708 at r2000 | 0.64 |
| 02treasure-box B vs q24, before | 70 / 848 (8%) | 12,266 | W r1585 | 0.44 |
| same, final (trace) | 0 / 550 | 25,375 | **L 589-1002** | 0.38 |

- **On-spawn engagement is gone** in every final-logic game.
  - Against starter-python, which parks on its spawn, the enemy's spawn healing collapses from 26k-69k to about 1-4k (traces 0.8-2k, eval games 0.5-3.8k), and 02treasure-box tempo roughly doubles.
  - q24_combo parks on its spawn much less (7-8% of our engage turns before). Against it the healing figure does not move: it heals by its own recalls and spawn visits, not from our wasted damage.
- **Eval games**, the same logic under the eval bot names:

| Map / side | vs starter: before → final (`sh_v2b`) | vs q24: mirror seat → final |
|---|---|---|
| 02treasure-box A | W r1888, heal 69k → W **r936**, heal 1k | L 524-1053 → **W r977** (1003-0) |
| 02treasure-box B | W r1630, heal 26k → W **r1022**, heal 4k | W r1838 → W **r1457** |
| 00reverse-spiral A | W 634 gems, heal 28k → W 931 gems, heal 0.5k | L 516-729 → **W 749-608** |
| 00reverse-spiral B | W r1869, heal 19k → W 967 gems, heal 0.7k (slower) | W → W |
| 00rushbait-v2 A | W r1808 → W 805 gems (slower) | W r1831 → W r1715 |
| 00rushbait-v2 B | W r1786 → W r1761 | L 979-1026 → **W 821-749** |

- **The spawn-adjacent rule is effectively off against every local opponent.** `SPAWN_NEAR_EVIDENCE` marked 0-2 enemies per traced game:
  - treasure-box vs starter: 0 (A) and 1 (B);
  - 2 in one game with the turret zone off;
  - 0 vs q24, on 02arena and on 00reverse-spiral.

  Neither starter-python nor q24_combo heal-hops, so the evidence-gated adjacent rule is **untested** (see Q27h). The final's mechanism is therefore:
  - the on-spawn skip;
  - the static-hazard return;
  - the turret zone;
  - the chase guard.
- **The turret zone pays on 02treasure-box.** The final logic with `SPAWN_AVOID = False` (`dbg_sh2_trace_nav`) reached 1000 at r1078 instead of r760 against starter A.

### 2. Q27b, touching spawns: fixed against the champion, at some cost against starter-python
- **Against q24_combo, all four touching-spawn games are won** (mirror seat 2/4):
  - 00reverse-spiral A turns from L 516-729 into W 749-608;
  - 00rushbait-v2 B turns from L 979-1026 into W 821-749;
  - both maps diverge from the mirror at r1-r4.

  h_treasure, with the unfixed adjacent rule, had lost both A seats to tb_merge_b.
- **Why the dynamic self-exemption was dropped after v1.** On 02treasure-box (d_ss 4) our spawn exit is within range of enemies on their spawn. The exemption re-enabled the fight there:
  - 124 opening engage turns from r32 to r200, all against full-HP targets (900 HP Tavi);
  - 02treasure-box vs starter A took r1127 with it, against r760 without it.

  The static `SPAWN_TOUCH_D` covers the real touching case (d_ss 1) by itself.
- **The remaining cost is against starter-python on touching maps.** The adjacent rule and turret zone are off there, so the cost comes from the on-spawn skip and static-hazard return.
  - **00rushbait-v2 A:** 1136 at r1808 becomes 805 gems in 2000 rounds.
    - It reproduced identically under three bot names and in the trace: 41 on-spawn skips, and our monster damage fell from 106k to 79k.
    - Still a win, 805-24.
  - **00reverse-spiral B:** r1869 becomes 967 gems, still a win.
  - **00reverse-spiral A** goes the other way: 634 → 931 gems.

### 3. Q27c, gold floor: holds gold on average, does not save 00breadcrumbs
- **Pace at r500 on the 20 chain-eligible maps, gate run against the mirror seat.**
  - Earned gold is 1,122 against 1,099; medians 934 against 894.
  - Tributed gems are 235 against 191, a +44 gem lead from the chain.
  - Across whole games the gold ratio is 0.97 on these maps; h_treasure, without a floor, was at 0.88.
  - On the other 50 maps nothing moves on average: gold 1,123 against 1,118 at r500 (medians 1,136 against 1,070), tributed gems 122 against 120.
- **Chain-eligible maps in the gate:** 25 wins against the mirror seat's 20. But only 9 against 8 on the 8 such maps outside the screen.
- **00breadcrumbs is still lost on both sides against q24** (mirror seat 1-1). The map is 3 champions and nothing but single gem and gold clusters.

| Variant | Our gold (A / B) | Result (A / B) |
|---|---|---|
| mirror | 4,465 / 3,340 | W / L |
| v1b (floor 0.3) | 1,473 / 1,075 | L / L |
| final (floor 0.6, grace 100) | 1,488 / 1,712 | L 294-1001 / L 483-1015 |
| v3 (grace 0) | **2,834** / 1,818 | **W** 1001-490 / L |

  - **Trace of the final logic as A vs q24.** The chain was on for all three champions only from r0 to about r150, while they were below the floor during the 100-round grace. It was off for all of them from r200 to r1100. Yet earned gold stayed at 200-480 per champion by r1000, and we lost 189-1015 with K/D 1/12.
  - **So the damage is done in the first ~150 rounds.** Gems first gives q24 the gold lead, and on this item-driven map that becomes a fight snowball the floor cannot undo.
  - **v3 (grace 0) helped one seat only** and was slower against starter A: r1538 against the final's r1113. By my pre-set rule (adopt v3 only if breadcrumbs gold recovered on both seats against q24, the screen did not drop below 24/40, and treasure-box pace held), v2b stayed final. v3's screen, 26-14, is within noise of v2b's 27-13.
- **The chain is worth little beyond the screen.** v2a and v2b differ only in the chain flag; they went 18-22 and 27-13 against q24 on the screen. Out of sample the chain-eligible maps gave +1 (9 against 8).

### 4. Gate run: every loss and the regressions
- **66 losses:** 43 were also lost by the mirror seat, and 23 are new (W → L). A scratch script tabulated every loss against its mirror-seat game: first-divergence round, spawn distance, chain eligibility, gold and K/D. The key rows are below.
- **43 L/L.** Seat or map losses the mirror shares.
  - **14 are byte-identical to the mirror:** 00contest A, 00crater B, 00great-wall A, 00interlock A, 00monolith A, 00pilgrimage A, 00quarry A, 00ribs A, 01hooks B, 02arena A, 02cuts B, 02fields A, 02geodes A and 02gift-wrapping A.
  - **The rest diverged but stayed lost**, e.g. 00swirl B 73-1012 against mirror 39-1003, and 01yellow-brick-road B 62-172 against 0-41.
- **23 W → L**, grouped by cause:
  - **Gem-first, gold-poor on chain maps (6):**

    | Game | Result | Our gold (mirror) | K/D (mirror) |
    |---|---|---|---|
    | 00anvil A | 368-1015 | 2,560 (5,647) | 6/17 (21/0) |
    | 00breadcrumbs A | 294-1001 | 1,488 (4,465) | |
    | 00gemfight B | 677-1071 | 3,495 (5,320) | 9/11 (18/4) |
    | 00road-of-riches A | 542-1009 | 3,662 (4,820) | |
    | 01shortcut B | 276-1004 | | 3/25 (4/9) |
    | adgato-gemcombat3 A | 630-1036 | | |

    All six diverge at r2-r33 except adgato3 (r202). The typical shape is 00anvil A: ahead 141-0 at r250, but behind on gold and items, and the mid-game fights lost. This is the Q27c residue.
  - **Drift (17), on maps with neither chain groups nor spawn proximity (d_ss ≥ 20):**

    | Game | First divergence |
    |---|---|
    | 00collision A | r8 |
    | 00elkring B | r72 |
    | 00expanse A | r405 |
    | 00galaxy A | r24 |
    | 00interlock B | r275 |
    | 00lanes B | r35 |
    | 00oasis B | r215 |
    | 00pilgrimage B | r95 |
    | 00rows B | r44 |
    | 00stampede A | r20 |
    | 00vault B | r16 |
    | 01boss-battle A | r15 (0-0 gold tiebreak) |
    | 01fracture A | r32 |
    | 01starfish B | r12 |
    | 02cuts A | r64 |
    | 02famine B | r10 |
    | 02harvest A | r27 |

    - **Why they diverge at all:** `gold_tick`, `note_hoppers` and `build_nbrs` change fuel use every turn, and our decisions are fuel-gated (placebo report). An on-spawn skip can also fire anywhere an enemy is seen on its spawn.
    - **They are matched by drift gains:**
      - 00ambush A@67, 00corners A@20, 00eight A@186, 00elkring A@241, 00expanse B@143;
      - 00galaxy B@24, 00gemfight A@181, 00lanes A@35, 00oasis A@542, 00stampede B@20, 00the-line B@23;
      - 01elk-arena B@102, 01starfish A@12, 01the-farm A@42, 02guardians B@19.

      Note the many maps that flip in both directions: elkring, expanse, galaxy, lanes, oasis, stampede and starfish.
    - **00galaxy A**, for example, shows the losing shape: ahead 154-25 at r250, first item at r368 (mirror r164), K/D 2/14.
- **Gains on the targeted maps (structural):**
  - 02treasure-box A (W 1003-0, r977);
  - 00reverse-spiral A;
  - 00rushbait-v2 B.

  Further chain-map gains: 00anvil B, 00gem-fields B, 00lost-world B, 01broken-curve A, 01islands A, 02crossing B, 02tangle B and adgato-gemcombat5 A.
- **Targeted maps against q24:** 6/8 won; the mirror seat won 4/8.
- **02arena B vs starter-python is a robust regression.**
  - 1010 at r1703 (K/D 23/11) becomes 782 (v1) and 582 (v2), K/D 16-18/31-34.
  - Within each code version it was identical under every name tried. v1 code gave 782-40 as `sh_v1a`, `sh_v1b`, `dbg_sh_trace` and `dbg_sh_trace_ncg` (chase guard off). v2 code gave 582-83 as `sh_v2a`, `sh_v2b`, `sh_v3`, `dbg_sh2_trace` and `dbg_sh2_trace_nav` (turret zone off). So the chain is irrelevant, since v2a equals v2b.
  - No heal-hopper was ever marked, so the adjacent rule did not fire.
  - First divergence: q24's slot 2 engages a non-spawn target (400 HP) at r83, while ours has skipped an on-spawn enemy 7 times by r100 and never engages there. The chase guard cannot act before a first engagement. Willow and Tavi then won the altar fights at (11-16, 12-15): Willow 19/1 K/D.
  - So the on-spawn skip plus the static-hazard return can cost a fight against an opponent that does not heal-hop (Q27e).
  - The `SPAWN_NEAR_EVIDENCE` comment in `bot.py` blames this game on the adjacent rule. That was my v2 hypothesis, and it was wrong. It was left unedited so that the gated bytes stay the same; `NOTES.md` has the correction.
- **adgato-gemcombat5 A vs starter-python, lost 238-357 by v1b, v2b and v3 (identical games).** The team stops scoring at r500.
  - A same-name rerun in a scratch workspace reproduced it exactly.
  - The trace-wrapper rerun won 1008 instead. Its target log still shows the Q21 pattern: 4 of 5 champions oscillating between two tiles next to their target group (e.g. (77,79)/(76,79) on group (78,81)) from r400 to r575.
  - This is the known Q21 stuck loop, fixed separately in c2_respawn; it is not new.

### 5. Methodology
- **Renaming is not a noise source; source edits are.**
  - `h_spawnheal` and `sh_v2b` differ only in name; `src/` is byte-identical. They replayed **40/40 screen games identically**.
  - h_treasure's rename, which also changed one comment space, changed 14/40.
  - Every trace copy, which differs only in `main.py`, diverged from its source on most maps. On 02treasure-box A vs q24 the trace won 1033-36 where the eval game lost 619-1037 (v1b), and on 02treasure-box B vs q24 the final logic won as `sh_v2b` but lost 589-1002 as a trace.
  - So 02treasure-box against q24 is chaotic, and any per-map claim needs several perturbations.
- **Screen-then-gate selection bias, measured.**
  - v2b was chosen among five variants partly on its 27-13 screen.
  - The same bytes scored 47/100 on the 50 maps outside the screen, which is null or slightly negative.
  - The placebo report's selection leak shows up here directly. Choose variants on the screen, but judge them on non-screen maps.

### 6. Ladder ground truth
- **None for this candidate:** it was not promoted.
- **The current ladder record makes the target real:**
  - q24_combo (v3) is 0-3 on 02treasure_box, and v2 is 2-3;
  - 00reverse_spiral is 5-2 across versions;
  - 00breadcrumbs is 3-1.
- **The pace to beat on treasure_box is r740-r1000 (Mein Kraft, sub7anr).** Our final logic reaches 1000 at r760-r1022 against starter-python and at r977/r1457 against q24, against r1630-r1888 for q24 itself.

## Verdict
**Inconclusive: mechanism confirmed, not promotable.**
- **Gate (a) fails.** 74W-66L, Wilson lower bound 0.446, botFaults 0. Only 47/100 off the screen maps.
- **Confirmed:**
  - on-spawn engagement 47-63% → 0%;
  - starter-python's spawn healing 26k-69k → about 1-4k;
  - 02treasure-box 1000 at r760-r1022 instead of r1630-r1888 against starter-python, and both seats won against q24;
  - Q27b fixed: all four touching-spawn games won against q24, mirror seat 2/4.
- **Not solved:**
  - Q27c only partly: average gold held, but 00breadcrumbs is lost on both sides;
  - the spawn-adjacent rule cannot be evaluated locally, because no local opponent heal-hops;
  - the on-spawn skip has a measurable cost against opponents that fight on: 02arena B, 00rushbait-v2 A.
- **Recommendation:**
  - Do not merge h_spawnheal as is.
  - If merged into the c2_respawn line, take only the on-spawn rule, the turret zone and `SPAWN_TOUCH_D` (no chain), after Q27e. Gate it on non-screen maps plus the 02treasure_box ladder record.
  - The chain should wait for Q27f.

## New hypotheses generated (for STRATEGIES.md)
- **Q27e: static-hazard handling of spawn-parked enemies against fighters.**
  - When every near enemy is spawn-healed, `handle_enemies` returns False and we farm on in their range. Instead:
    - step out of their range, treating them as awake camps in the danger and avoid logic, including on touching maps;
    - and re-engage the moment one steps off its spawn;
    - or skip on-spawn enemies only above ~70% HP.
  - Evidence:
    - 02arena B vs starter 1010@r1703 → 582 (K/D 23/11 → 16/34), robust across 4 bot names, first divergence = 7 on-spawn skips before r100;
    - 00rushbait-v2 A vs starter 1136@r1808 → 805;
    - 00reverse-spiral B vs starter r1869 → 967 gems.
- **Q27f: the opening gold race on cluster maps (Q27c residue).**
  - A per-champion floor with a 100-round grace lets the chain run gem-first in r0-150. On item-driven maps the opponent's early gold lead then snowballs, even though the chain is off afterwards.
  - Try:
    - no chain until the champion's first Bruiser emblem (150 gold);
    - or a team-level floor in shared memory;
    - or no chain with three or fewer champions.
  - Evidence:
    - 00breadcrumbs vs q24 gold 1,488/1,712 against the mirror's 4,465/3,340, lost both;
    - trace: chain off from r200 on, still K/D 1/12;
    - grace 0 (v3) recovered the A seat only (2,834, W);
    - the gem-first, gold-poor W → L games: 00anvil A, 00gemfight B, 00road-of-riches A.
- **Q27g: treasure-box pace r700 needs the chain without its floor in the altar box.** A structural exemption: groups within the altar's own walled component and within ~8 steps of the altar ring chain without the gold floor.
  - Ladder: q24_combo 0-3 on 02treasure_box; opponents finish at r740-r1322.
  - Locally: final r760-r1022 against starter-python, r977/r1457 against q24; h_treasure's unfloored chain r590-r885.
  - Check 00breadcrumbs does not regress (its clusters are not altar-boxed).
- **Q27h: a heal-hopper imitation opponent is a prerequisite for the spawn-adjacent rule.** Merge with Q29 and Q31.
  - `SPAWN_NEAR_EVIDENCE` marked 0-2 enemies per local game, so the adjacent rule was never exercised.
  - An `imit_*` bot that steps onto its spawn whenever it is below 60% HP and steps out to fight, e.g. Willow + Vesper + Tavi, would test it and Q27e.
- **Q30 addendum (method).**
  - A bot rename with byte-identical `src/` reproduced 40/40 games, so names are not a noise source. Edits to `main.py`, or to comments, are: h_treasure, and every trace copy here.
  - The screen → gate selection effect is directly visible: 27/40 on the screen maps against 47/100 elsewhere for the same bytes.
  - **Rule proposals:**
    - report and judge a screened candidate's gate on the non-screen maps;
    - treat trace copies as mechanism evidence only, because any `main.py` wrapper perturbs the trajectory;
    - back outcome claims on a single map, such as 02treasure-box against q24, with at least two perturbations, e.g. two placebo-style copies.
