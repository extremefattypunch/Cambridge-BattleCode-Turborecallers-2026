# Experiment: c3_teamclear, LOOP.md §4 promotion gate vs q24_combo (2026-11-01, cluster)

STRATEGIES **Q26 merge** (h_teamclear's team bootstrap ported onto the Q24 combo). This report covers the full promotion gate (a-d) of the frozen candidate `bots/c3_teamclear` against `q24_combo`, the champion named in the task, plus the mandatory analysis session. No candidate code was changed.

**Gate result: FAIL. Do not promote.**
- **(a) FAIL.** 80/140 (57.1%). The 95% Wilson interval is [0.489, 0.650], so its lower bound is under 0.5 and the score is 2 short of 82. botFaults 0.
- **(b) PASS.** Gauntlet 176/200 against the champion's 174. The worst per-opponent change is 0.
- **(c) FAIL on fuel, strictly read.** The release game was clean: 0 crashes, 0 bytes of stdout, no `bot error`. But fuelExhausted was **9.5 per game against q24's 7.3** in the same 140 games.
  - More than half of the excess is one suspended first turn per champion on 28 of 70 maps.
  - Per-turn fuel is equal.
- **(d) Does not confirm a decisive gain.**
  - The mechanism works where it was aimed: on 02gift-wrapping, 38 team clears and 1000-0 on both sides. Against starter-python on that map, 2/2 wins where q24 goes 0/2 at 0-80.
  - But the +10 over the q24 mirror sits almost entirely on maps without team-only groups: +9 on 48 maps against +1 on the 22 census maps.
  - On the other 18 census maps (all but 02gift-wrapping, 01yellow-brick-road and the two no-tribute gold maps), c3 cleared *fewer* team-only groups than q24 did in the same games: 23 against 33.
  - The win/loss flips against the mirror (+38/−28) are within trajectory noise (z ≈ 1.2). A functionally identical traced copy scored 78/140, with 105/140 games identical.
  - Muster time is a measurable cost, and it sits in the slices that did not gain: 241 muster turns per game on large maps, against 33 on small maps. On 01corridors one champion spent 550 of 2,000 rounds at a muster ring (§3).
  - A new 0-80 standoff loss to starter-python on 02treasure-box is base-code behaviour, not team logic.

**Context the orchestrator should know:** while this gate ran, `results/CHAMPION` became **`c2_respawn`** (commit fac3b36: q24 + the Q21 respawn fix, 89/140 vs q24). Even a pass here would have needed a gate against c2. READY.md already names the follow-up, "c4 = c2 + team clear". The "New hypotheses" section lists what c4 should change.

## Hypothesis
- **What:** q24_combo plus h_teamclear v2.
  - **TEAM_CLEAR:** the team option in `choose_target`.
  - **TEAM_TANK_CHECK.**
  - **TEAM_MUSTER:** gather on a ring before waking a group that needs a team; shared presence bits.
  - **TEAM_WRAP_FIX (a)/(b)/(c).**
  - **Claim/dead/presence bytes 0-6.**
  - Integration with q24's chip mode as described in `bots/c3_teamclear/NOTES.md` (T1-T6).
  - h_teamclear scored 91/140 vs tb_merge_b. The question is whether the bootstrap still adds a decisive gain on top of q24 (87/140 vs tb_merge_b).
- **Source:**
  - `results/simulated-matches/2026-11-01_0153_h_teamclear/notes.md`, whose recommended next step was "merge Q26 into the Q24/Q21 combo";
  - real ladder losses on 02gift_wrapping: 0-1028 and 16-1006 with 0 team-group clears;
  - the c3 smoke run: 24/30 vs tb_merge_b on the 15 most-affected maps.

## Setup
- **Candidate:** `bots/c3_teamclear` (frozen; 3,032-line `bot.py`; `main.py`, `draft.py` and `randomness.py` byte-identical to q24's). Champion for this gate: `q24_combo`. Engine: cambc 4.0.0 / engine 2.0.0. Multi-game runs used the free Slurm `test` partition through `tools/onslurm.sh`.
- **(a)** job 56823328, exit 0, games in `matches/gate-c3-all/`:
  `tools/onslurm.sh -c 24 -m 16G -t 00:20:00 -J c3-gate -- python3.12 tools/eval.py c3_teamclear q24_combo --maps all --jobs 16 --keep --tag gate-c3-all`
- **(b)** job 56823333, exit 0, appended to `results/gauntlet.jsonl` (commit field 6f62d12), games in `matches/g-c3_teamclear-vs-*`:
  `tools/onslurm.sh -c 24 -m 16G -t 00:30:00 -J c3-gaunt -- python3.12 tools/gauntlet.py c3_teamclear --pool sf_bank,tb_merge_a,tb_aggro,imit_test,lad_vcst --maps sprint --jobs 16 --note "gate c3_teamclear"`
  - Champion baseline: `results/gauntlet.jsonl`, note "gate q24_combo", 174/200.
- **(c)** run locally; output in `matches/gate-c3-release/` (`run.log`, `stats.json`, unzipped bundle in `bundle/`):
  `./cli/cambc run c3_teamclear q24_combo --map 01big-world --release -o matches/gate-c3-release --statistics matches/gate-c3-release/stats.json --json`
- **(d) starter-python check** (job 56823384, exit 0, `matches/c3gate-c3-starter`, `matches/c3gate-q24-starter`):
  `tools/onslurm.sh -c 16 -m 8G -t 00:15:00 -J c3-start -- bash -c "python3.12 tools/eval.py c3_teamclear starter-python --maps 02gift-wrapping,02treasure-box --jobs 4 --keep --tag c3gate-c3-starter; python3.12 tools/eval.py q24_combo starter-python --maps 02gift-wrapping,02treasure-box --jobs 4 --keep --tag c3gate-q24-starter"`
- **"Before" baseline:** `matches/plc2-mirror` (q24 vs q24, from the placebo study). Each map's A and B games are identical there. The mirror game's seat-A result is the "before" for c3 as team A, and its seat-B result is the "before" for c3 as team B. The mirror scores 70/140.
- **Diagnostic copies** (never evaluate them):
  - `bots/dbg_c3tc` (existing): c3 plus counters every 250 rounds, functionally identical.
  - `bots/dbg_c3gate_tb2` and `bots/dbg_c3gate_tb4` (new, via `tools/newbot.py c3_teamclear ...`): c3 plus a state print every 50 rounds from r400. They reproduced the starter game exactly.
  - `bots/dbg_c3gate_tbox` (DEBUG on) and `bots/dbg_c3gate_tb3` (per-turn branch trace): both re-rolled the game, so they were used only qualitatively.
- **Traced census:** `dbg_c3tc` vs q24_combo on all 70 maps, both sides, with bot stdout. eval.py disables logs, so `matches/c3gate-tools/tcall.py` calls run-batch directly; tag `c3gate-tc-all`, job 56825823. It was parsed with `matches/c3gate-tools/tcparse.py`.
- **Analysis scripts:**
  - `analyze_match.py --summary --games` and per-game narratives;
  - `postmortems/match_metrics.py`;
  - `matches/q26-tc/tools/q26metrics.py` (the census of the 73 team-only groups);
  - `matches/q26-tc/tools/fuelfile.py` (per-turn fuel);
  - session scratch scripts for both-sides metrics, map families and flips against the mirror, and loss classification. Their numbers are copied below.

## Results (verbatim)
```
SUMMARY c3_teamclear vs q24_combo: 80W-60L (57%)  avg gems 746 vs 624  avg deaths 9.4 vs 10.3  botFaults(A) 0
GAUNTLET c3_teamclear: 176/200 (88%) on maps=sprint
SUMMARY c3_teamclear vs starter-python: 3W-1L (75%)  avg gems 752 vs 39  avg deaths 1.0 vs 35.0  botFaults(A) 0
SUMMARY q24_combo vs starter-python: 2W-2L (50%)  avg gems 515 vs 122  avg deaths 2.0 vs 67.2  botFaults(A) 0
```
Release game (`run.log`):
```
Team B (q24_combo) wins: round limit (2000) reached with more gems
  A    c3_teamclear   815     0      1        7180        0  Vesper Vale, Vendetta, Marcella, Heart of Ruin, Ryth
  B    q24_combo      911     0      0        7749        0  Vesper Vale, Vendetta, Marcella, Heart of Ruin, Ryth
```

### Gate table
| Gate | Requirement | Result | |
|---|---|---|---|
| (a) head-to-head | ≥ 82/140, Wilson LB > 0.5, botFaults 0 | **80/140 (57.1%)**, Wilson 95% [**0.489**, 0.650], botFaults 0 | **FAIL** |
| (a) side split | (report) | as team A **39/70** (mirror seat A 33/70, **+6**); as team B **41/70** (mirror seat B 37/70, **+4**) | |
| (b) gauntlet total | ≥ 174 | **176/200** | PASS |
| (b) per opponent | no drop > 4 | sf_bank 40-0 (q24 39-1, **+1**); tb_merge_a 24-16 (24-16, **0**); tb_aggro 40-0 (39-1, **+1**); imit_test 36-4 (36-4, **0**); lad_vcst 36-4 (36-4, **0**) | PASS |
| (c) release | 0 crashes, no `bot error` | 0 crashes. team-a/b `.stdout` and `.debug` are 0 bytes. 01big-world: q24 won 911-815 at r2000, the same as eval game 01big-world A | PASS |
| (c) fuel | c3 ≤ q24 in gate-c3-all | **9.5 vs 7.3** fuelExhausted per game (1,334 vs 1,025; c3 higher in 70 games, lower in 17, equal in 53). In the release game, 51 vs 45 | **FAIL** (see §4) |
| (d) analysis | mechanism changed; gain not an artefact | the mechanism changed on 02gift-wrapping; the gain is not where the mechanism acts and is within noise | **FAIL** |

**gate_pass = false.**

### Paired metrics (same 140 games, per game; both-sides script)
| Metric | c3_teamclear | q24_combo (opponent) | q24 mirror seat (before) |
|---|---|---|---|
| gems banked | **745.8** | 624.2 | 685.2 |
| camp clears | **56.0** | 52.7 | 54.4 |
| team-only (census) group clears | **1.73** (242) | 1.28 (179) | 1.19 (166) |
| ...of which shared by ≥ 2 of our champions | **0.62** (87) | 0.27 (38) | 0.23 (32) |
| clears shared by ≥ 2 champions (any group) | 8.39 | 8.01 | 7.75 |
| deaths to camps | **0.98** | 1.04 | 1.00 |
| deaths to champions | **8.47** | 9.24 | 9.38 |
| earned gold | **5,881** | 5,233 | 5,468 |
| fuelExhausted | 9.53 | **7.32** | 7.18 |

`match_metrics.py matches/gate-c3-all` (c3 side): tributes 4,201, mean 24.9, small(<10) 490; deaths_by_camp 137 (1.0/game); deaths_by_champion 1,186 (8.5/game); fuelExhausted 1,334 (9.5/game); gemsLost_to_camp 937 (6.7/game); gemsLost_to_champion 8,688 (62.1/game); wards 427.4/game; consumables 8.7/game.

**`analyze_match --summary --games`** (80 wins / 60 losses):

| Metric | wins | losses |
|---|---|---|
| gems us-them | 893-454 | 550-851 |
| first clear us / them | r48 / r54 | r42 / r40 |
| first tribute us / them | r157 / r198 | r141 / r209 |
| clears us / them | 55.5 / 44.1 | 56.7 / 64.2 |
| kills us / them | 12.1 / 5.9 | 5.4 / 11.9 |
| camp deaths us | 0.9 | 1.1 |
| gem lead r250 / r500 / r1000 | +35 / +84 / +158 | +2 / −16 / −95 |
| fuelExh us | 11.3 | 7.2 |
| mean tribute | 26.3 | 22.2 |

Losses look like q24's: the opening is not behind (first tribute r141 vs r209, lead +2 at r250). They are decided by mid-game fights (K/D 5.4/11.9) and clear counts (56.7 vs 64.2).

## Analysis session

### 1. Did the targeted mechanism change? Yes on wrapped maps, hardly elsewhere
**Census of the 73 team-only groups on 22 maps** (q26metrics; never cleared in the tb_merge_b mirror, rejected solo by every champion, feasible with 4 allies):

| Run | Distinct groups cleared ≥ 1 | Clears | Gems | Capture split (mean champions) |
|---|---|---|---|---|
| c3 (gate-c3-all, 140 games) | **41/73** | 242 | 8,989 | 1.61 (1:140, 2:45, 3:18, 4:14, 5:10, none:15) |
| q24 as c3's opponent (same games) | 34/73 | 179 | 6,205 | |
| q24 mirror, seat A / seat B (70 games each) | 22/73 / 15/73 | 107 / 59 | 3,797 / 2,120 | 1.15 |

**Per targeted map** (team-only clears c3 A+B | q24 opponent A+B | mirror seat A + seat B; results c3 A,B):

| Map | c3 | q24 opp | mirror | c3 result A,B |
|---|---|---|---|---|
| **02gift-wrapping** | **19+19** | 0+2 | 1+1 | **W W** (1000-0 r816, 1004-8 r1166) |
| **01yellow-brick-road** | 0+**25** | 0+1 | 0+0 | W W (134-2; 1011-250) |
| 01boss-battle (no tribute) | 61+67 | 53+63 | 57+45 | W L (gold) |
| 02guardians (no tribute) | 12+16 | 16+11 | 36+3 | W W (gold) |
| 00corners | 5+2 | 4+3 | 0+3 | L W |
| 00reverse-spiral | 0+6 | 5+0 | 0+3 | L W |
| 00expanse | 0+3 | 4+1 | 1+0 | L W |
| 01the-farm | 0+3 | 0+0 | 0+2 | W L |
| 00great-wall | 0+2 | 4+0 | 1+2 | L L |
| 01shortcut | 1+1 | 0+2 | 1+0 | W W |
| 00swirl | 0+0 | 2+5 | 4+0 | L L |
| 02treasure-box | 0+0 | 0+1 | 3+0 | W W |
| 00pilgrimage, 00road-of-riches, 01fracture, 02crossing | 0 | 0-1 each | 1 each | mixed |
| 00lost-world, 00quadrants, 01big-world, 01corridors, 01islands, 02harvest | 0 | 0 | 0 | mixed |

- **02gift-wrapping is the clean mechanism win.**
  - Both games: first clear r29 (A) and r27 (B), 19 team clears each, 0 camp deaths, 1000-0 and 1004-8. q24 made 0 and 2 clears.
  - In the q24 mirror, each seat makes one chip clear (r~350) and the game ends 44-44, with seat B winning the tiebreak. So the map is a coin flip for q24 and a certainty for c3.
- **Against a different-logic opponent** (task item; starter-python):

  | Map | c3 A | c3 B | q24 A | q24 B |
  |---|---|---|---|---|
  | 02gift-wrapping | **W 1008-44**, 18 clears (all team-only), first r29 | **W 1000-32**, 19, r27 | **L 0-80**, 0 clears | **L 0-80**, 0 clears |
  | 02treasure-box | **L 0-80**, 16 clears, 0 tributes | W 1001-0 | W 1032-328 | W 1027-0 |

  The local q24-vs-q24 mirror hides q24's zero-clear blind spot: q24 sits at spawn on 02gift-wrapping and loses 0-80 to the starter, as it did on the ladder. c3 removes it. The 02treasure-box A loss is analysed in §3.
- **01yellow-brick-road B** (1011-250; mirror seat B lost 0-41) is the Q21 freeze released by WRAP (b)/(c): 25 team-only clears, 47 clears in total. In the mirror game that seat made 0 clears and the other seat 3. c2_respawn's fix targets the same freeze.
- **On the other 18 targeted maps the team option adds nothing measurable.** c3 made **23** team-only clears there, q24 in the same games **33**, and the mirror **23**.
  - On 8 of the 10 targeted-map regressions (below), c3 made 0 team-only clears.
  - q24 already reaches many of these groups solo once it has items.
- **Camp deaths did not rise** (the task's "camp deaths from team clears" question).
  - Overall 0.98 vs 1.04 per game (mirror 1.00).
  - On targeted maps 1.61 vs 1.50 (mirror 1.68).
  - Only 11 of c3's 137 camp deaths were next to a team-only group (nearest group centre, census coordinates): 00lost-world A ×4 at group 10, 01yellow-brick-road ×2, 02guardians ×2, and one each on 00reverse-spiral, 00road-of-riches and 01corridors. q24 had 10.
  - Camp deaths within 60 rounds before a shared (≥ 2-champion) clear of the nearest group: 8 for c3, 7 for q24.
  - Gauntlet: 0.71 vs 0.70 per game.
  - The 02gift-wrapping team bouts cost 0 camp deaths on both sides.

### 2. Is the gain spread across map families and sides? No: it is off-target and within noise
**Flips against the q24 mirror seat:** +38 gains, −28 losses, net **+10**.
- Under a symmetric null over 66 flips, the standard deviation of the net is about 8.1, so z ≈ 1.2.
- The placebo study measured a 35% flip rate for re-rolled games.

| Family | c3 W/n (A, B) | mirror seat W | net | gains / losses |
|---|---|---|---|---|
| **census targeted maps (22)** | 23/44 (9, 14) | 22 | **+1** | 11 / 10 |
| **other maps (48)** | 57/96 (30, 27) | 48 | **+9** | 27 / 18 |
| 00 maps | 39/70 (17, 22) | 35 | +4 | 20 / 16 |
| 01 maps | 15/30 (7, 8) | 15 | 0 | 7 / 7 |
| 02 maps | 18/30 (10, 8) | 15 | +3 | 8 / 5 |
| adgato | 8/10 (5, 3) | 5 | +3 | 3 / 0 |
| small ≤ 35×35 | 29/40 (16, 13) | 20 | **+9** | 13 / 4 |
| medium ≤ 2,500 tiles | 29/50 (13, 16) | 25 | +4 | 13 / 9 |
| **large > 2,500 tiles (25 maps)** | 22/50 (10, 12) | 25 | **−3** | 12 / 15 |
| 3 champions/side | 15/24 | 12 | +3 | 6 / 3 |
| 4 champions/side | 22/32 | 16 | +6 | 10 / 4 |
| **5 champions/side** | 43/84 | 42 | **+1** | 22 / 21 |
| no-tribute (01boss-battle, 02guardians, 02the-pack) | 5/6 | 3 | +2 | 2 / 0 |
| sprint subset | 22/40 | 20 | +2 | 7 / 5 |

- **Map pairs (A,B):** WW 24, LL 14, WL 15, LW 17.
  - **Won both:** 00fragment, 00gem-fields, 00interlock, 00lanes, 00lost-world, 00packs, 00quarry, 00split, 00the-line, 00vault, 01concentrated-wealth, 01gold-rush, 01shortcut, 01yellow-brick-road, 02arena, 02gift-wrapping, 02guardians, 02harvest, 02the-pack, 02treasure-box, 02uncharted-lands, adgato-gemcombat2, adgato-gemcombat4, adgato-gemcombat5.
  - **Lost both:** 00breadcrumbs, 00collision, 00great-wall, 00pilgrimage, 00stampede, 00swirl, 01corridors, 01islands, 01starfish, 01starvation, 02crossing, 02cuts, 02famine, 02tangle.
- **The team option should matter most with 5 champions and team-only groups. Those are exactly the slices that did not improve** (+1 and +1).
  - The net gain sits on small maps and on 3- or 4-champion maps. There the traced census shows only 15-37 muster turns per game and 3-7 team picks, so c3 behaves almost like q24 apart from WRAP (b)/(c) and fuel.
  - On large and 5-champion maps it musters 214-241 turns per game (§3).
- **Overlap with c2_respawn** (`matches/gate-c2-all`, same mirror reference):
  - c3 and c2 share 21 of their 38 gains each. Independence predicts 38·38/70 ≈ 20.6.
  - They share 9 losses against an expected 7.6.
  - So the individual flips cannot be attributed to the shared Q21-type mechanism; they look like re-rolls.
- **A direct re-roll check:** the functionally identical traced copy `dbg_c3tc` reproduced the gate game exactly on 00swirl A, 02crossing A and 00dunes A, but **won** 00expanse A 1003-646 where c3 lost 900-1008.

### 3. Losses: every one classified (60)
Classification (from the stats JSONs):
- **fight**, enemy kills ≥ ours + 5: 30 (15 regressions against the mirror seat, 15 also lost in the mirror);
- **race**: 27 (12 regressions, 15 also lost);
- **0-0 gold tiebreak**: 3 (00stampede A is a regression; 00stampede B and 01boss-battle B were also lost in the mirror).

**The 10 regressions on census-targeted maps:**

| Game | Type | Score | c3 / q24 team-only clears | Notes |
|---|---|---|---|---|
| 00swirl A | fight | 188-1029, K/D 3/36 | 0 / 2 | Trace (reproduced exactly): only **9 team picks and 11 muster turns** by r1750 (the game ended at r1848). The team logic was idle; WRAP (b)/(c) fired 96/140 times. A fight re-roll. |
| 02crossing A | fight | 319-1008 (r1006), K/D 2/12 | 0 / 0 | Trace (reproduced): 22 team picks, **79 muster turns** (slot 3: 68 by r1000). q24 led from r100. |
| 00great-wall B | fight | 634-1022, K/D 7/13 | 2 / 0 | The smoke run already flagged this muster cost (`NOTES.md`: 170 muster turns, mostly walk-in turns and resets). |
| 00pilgrimage B | fight | 341-465 | 0 / 0 | Low-scoring map; also lost in the A seat. |
| 01islands B | fight | 754-1002, K/D 0/6 | 0 / 0 | fuelExh 88 vs 94 (an islands crossing map; both bots exhaust). |
| 00expanse A | race | 900-1008 | 0 / 4 | **The traced copy won this game 1003-646**: a re-roll. |
| 00road-of-riches A | race | 685-1005 | 0 / 0 | Led +83 at r250, then lost the mid-game race. |
| 01corridors B | race | 392-438 | 0 / 0 | 5 camp deaths (1 at a team-only group). |
| 01fracture A | race | 830-857 | 0 / 0 | Close race; fuelExh 7 vs 0. |
| 01the-farm B | race | 802-948 | 3 / 0 | −105 at r250; first tribute r303 vs r105. |

**Other notable losses:**
- **00dunes A** (601-1010, a race, a large non-targeted map). The trace reproduced it exactly: **225 muster turns, 157 of them by slot 3 before r500** (about 31% of that champion's early game), with 0 bans. Lead −71 at r250, 6 camp deaths. This is the clearest muster cost found. Group 0 (8 gems + golem) is solo-rejected at base stats, but the mirror clears it 5 times solo once items arrive. c3 instead waits at its ring.
- **01big-world A** (the release game, 815-911). c3 tributed first (r80 vs r279) but cleared 49 against 65. 27 of its 49 clears were shared by ≥ 2 champions, so on a 100×100 map the team spent clears splitting captures.
- **The biggest fight losses** were 00oasis B 103-1002 (K/D 3/33), 01elk-arena B 58-1022 (7/29), 00crater B 185-1000 (0/25), 01hooks A 154-1001 (12/34) and 01starfish B 209-1007 (11/38).
  - All are snowball maps where the mirror's own seats split.
  - 00oasis, 01elk-arena and 01hooks were each won on the other side by a similar margin (836-326, 1032-144, 1012-22).
- **00contest A 0-600 and 00stampede A/B 0-0 on gold:** also lost in the mirror seat, except 00stampede A, where gold was 8,669 vs 9,485.

**The traced census of all 70 maps** (`c3gate-tc-all`; `dbg_c3tc` vs q24_combo, both sides, job 56825823, 140/140 games, parsed by `tcparse.py`):
- **Reproduction.** **105 of 140 games are identical** to the gate games, and the traced copy scored **78/140** (gate: 80). This is a free placebo-type replicate of c3: it also falls short of 82.
- **Totals per game** (summed over slots):
  - muster turns **139.3**;
  - turns with `team_need > 1`: 208.6;
  - team picks 20.4;
  - bans 0.9;
  - chip picks 0;
  - hidden-camp threats (WRAP a) 20.4;
  - WRAP (b) 22.6;
  - WRAP (c) 156.4.
- **Muster time sits where c3 does not gain:**

  | Slice | Muster turns/game (by r500) | Team picks/game | c3 net vs mirror (§2) |
  |---|---|---|---|
  | large maps (> 2,500 tiles) | **241.3** (104.8) | 25.1 | **−3** |
  | medium | 122.3 (43.9) | 26.5 | +4 |
  | small (≤ 35×35) | 33.0 (11.4) | 6.8 | **+9** |
  | 5 champions/side | **213.8** (86.6) | 30.6 | **+1** |
  | 4 champions/side | 36.5 (12.6) | 6.6 | +6 |
  | 3 champions/side | 15.5 (8.8) | 2.9 | +3 |
  | targeted maps / other maps | 195.9 / 113.3 | 40.0 / 11.4 | +1 / +9 |
  | gate games that **lost** a mirror-seat win (28) | **216.7** (79.3) | 24.3 | |
  | gate games that **gained** a mirror-seat loss (38) | 122.2 (59.6) | 18.4 | |
  | 02gift-wrapping (2) | 187.0 (144.0) | **186.0** | +1 (W W) |

  - Traced losses averaged 173 muster turns per game, against 112 for traced wins. In the reproduced subset the figures are 145 vs 77, and the most-mustering slot averaged 72 vs 40 turns.
  - Win rate by muster turns per game: 0 → 27/46; 1-49 → 14/27; 50-149 → 15/23; ≥ 150 → 22/44.
  - This is correlational, because large 5-champion maps also have more team-only groups. But it fits the mechanism: a mustering champion is idle, and on 02gift-wrapping the musters convert into clears (186 team picks for 187 muster turns), while elsewhere they mostly do not.
- **Worst cases** (reproduced):
  - **01corridors: 1,225 (A) and 1,172 (B) muster turns. One champion spent 550 / 528 of the 2,000 rounds at a muster ring, with 19 / 15 bans.** Both games were lost (488-548, 392-438), and c3 made 0 team-only clears there. The mirror is L/W.
  - 02famine 642 / 693 muster turns, both lost (655-1006, 891-953).
  - 01concentrated-wealth 643 / 472, both won.
  - 01big-world A 316 (the release game).
  - 02fields B 368 (lost).
  - Diverged: 00ambush A 1,087.

**c3 vs starter-python, 02treasure-box A: 0-80, a 1,500-round standoff, not team logic.**
- The game reproduces exactly locally, and also with `dbg_c3tc`, `dbg_c3gate_tb2` and `dbg_c3gate_tb4`.
- Counters: 1 team pick and 1 muster turn in the whole game (slot 4, before r250).
- From r450 to r2000:
  - The three surviving starter champions stand still at (18,14), (20,14) and (20,16), next to the central altar at (17,17), with 770-1,120 HP and 7 gems each. They had already tributed 80 by r250.
  - Our five hold 8-18 gems each, below BANK_ANY = 30, at 460-800 HP. That is above the 45% recall threshold, so they never heal.
  - Two of them retreat from the enemies through `handle_enemies` every turn (per-turn trace).
  - Three walk toward capture tiles of reward-available groups 8, 5 and 15 at (16,20), (20,18) and (20,20). Those tiles lie inside the enemies' zone, and the champions never arrive.
  - No clears after r524, except two at r1913-1921. 0 tributes.
- q24 won the same pairing 1032-328. Its trajectory never reached this standoff.
- Every code path involved is q24's: bank thresholds, the recall rule and `handle_enemies`. Team logic is not involved. The state was reached through a re-rolled opening (first kill r24, first clear r129 against the starter's r76). It is a new loss pattern: an enemy that parks at the altar after banking first wins on the round limit.

### 4. Fuel (gate c)
- **fuelExhausted by round** (gate-c3-all, c3 / q24):

  | Rounds | c3 | q24 |
  |---|---|---|
  | r1-5 | 369 | 184 |
  | r6-50 | 262 | 212 |
  | r51-300 | 308 | 244 |
  | r301-1000 | 314 | 313 |
  | r1001+ | 81 | 72 |
  | **total** | **1,334** | **1,025** |

  - **+185 of the +309 is in r1-5.** On 28 of 70 maps, c3 suspends exactly one turn per champion at r1 or r2, identically on both sides. q24 does not, or does less: 00dunes, 00expanse, 00galaxy, 00ribs and 01fracture give 5 vs 0; 00lanes 10 vs 5; 01big-world 15 vs 10. On 1 map c3 suspends less.
  - **The probable cause is h_teamclear's boss gate in `Group.__init__`.** It makes one `is_monolith()` API call per camp of every non-boss group at init; q24 makes none. That pushes the first turn over budget on camp-rich maps.
  - **After r5:** 965 vs 841 (+0.9/game). Per game, c3 is higher in 41, lower in 22 and equal in 77.
- **Per-turn fuel is not higher** (fuelfile.py over all turns of the 140 games):

  | | Turns | Mean | Median | p95 | p99 | Turns ≥ 2.5M |
  |---|---|---|---|---|---|---|
  | c3 | 1,022,565 | 1,062,360 | 1,065,342 | 1,873,559 | 2,136,239 | 1,722 |
  | q24 | 1,022,574 | 1,072,577 | 1,074,396 | 1,870,609 | 2,132,586 | 1,617 |

- **Gauntlet:** 12.3 vs 8.8 fuelExhausted per game, with the same shape (r1-5: 666 vs 310; r51-300: 808 vs 540).
- **Reading.** Strictly, gate (c) fails. Practically, the cost is one lost first turn per champion on large maps plus a small mid-game tail. The first part is cheap to fix (New hypotheses, item 2).

### 5. Surprising wins
- **02gift-wrapping A/B** (1000-0 r816, 1004-8 r1166): the team cascade (see §1). The only structural win.
- **01yellow-brick-road B 1011-250:** in the mirror this seat lost a near-frozen 0-41 game with 0 clears. c3 made 47 clears and 25 team-only clears; the WRAP (b)/(c) freeze release.
- **01hooks B 1012-22 (K/D 45/16)** and **00quarry A 1044-188:** snowball maps that flipped.
  - The mirror seat lost 01hooks 0-1001, and c3 lost the A side 154-1001.
  - The mirror's 00quarry A was a 120-1002 carrier stall (0 tributed by r500, 46 by r750).
  - These are re-rolls, not mechanism wins.
- **No-tribute maps:** 5/6 won on gold, against 3/6 in the mirror.
  - 01boss-battle A: 27,194 vs 23,587.
  - 02guardians A/B: 8,911 vs 8,060 and 11,391 vs 5,878.
  - 02the-pack A/B: 16,552 vs 15,258 and 19,254 vs 13,467.
  - 01boss-battle B was lost on gold, 26,564 vs 28,378.
  - The team option is gold-valued there (NOTES T6). The c3 smoke run vs tb_merge_b showed the same.

## Verdict
**Rejected for promotion: the gate fails on (a), (c)-fuel and (d).**
- **(a)** 80/140 is short of 82; its Wilson lower bound is 0.489.
- **(b)** passes.
- **(c)** The release game is clean, but fuelExhausted is 9.5 vs 7.3.
- **(d)** The mechanism is real on 02gift-wrapping, and the starter-python check confirms it fixes q24's ladder blind spot there (0-80 → 1000+). But it adds nothing measurable on the other targeted maps.
  - The aggregate +10 lies on maps where team logic is nearly inactive (small and 3-4-champion maps), and it is statistically indistinguishable from fuel-divergence re-rolls. The traced replicate scored 78/140.
  - Where team logic is active outside 02gift-wrapping (large and 5-champion maps), muster idling costs about as much as the team clears gain.

**Keep the idea; do not ship this bot.** The ladder value is real (two ladder losses on 02gift_wrapping), so the team bootstrap should be re-gated in a narrower form on top of the new champion c2_respawn ("c4"). Never ship TEAM_CLEAR without a Q21-class fix (h_teamclear ablation 64/140); c2 carries one.

## New hypotheses generated
1. **Team option only as an idle fallback (c4 design).** Evaluate the team option only when the champion has no solo target (`best is None` after the solo/chip pass), or only for groups that no champion can solo even with its current items.
   - **Evidence:** every 02gift-wrapping gain came from champions with no solo option. On the other 18 targeted maps c3 made 23 team-only clears against q24's 33, so the team option displaced solo play without clearing more. On 5-champion maps the result was +1 net.
   - **Why:** it keeps the gift-wrapping fix and removes the muster and capture-splitting costs where q24 already farms.
2. **Lazy boss gate (fuel).** Compute `Group.boss` on first use (when a team option is first considered) or from camp kinds read in the same loop, not with one `is_monolith()` call per camp in `Group.__init__`.
   - **Evidence:** +185 first-turn fuelExhausted (r1-5) on 28/70 maps, one per champion at r1-2 on both sides. q24 has no such calls.
   - **Why:** it makes gate (c) pass and returns the first turn on large maps.
3. **Cumulative muster budget per group and per champion.** For example, at most 40 muster turns per group per 300 rounds, counting walk-in turns, with the ban firing on the budget rather than on the resettable 15/30-round clocks. Also consider no muster at all when the group is farther than ~25 tiles on large maps.
   - **Evidence** (traced census, §3):
     - 139 muster turns per game overall; 241 on large maps and 214 on 5-champion maps, which are exactly the slices with no net gain (−3 and +1);
     - games that lost a mirror-seat win: 217 per game, against 122 for gains;
     - 01corridors: one champion spent 550 of 2,000 rounds at a ring, with 19 bans; lost both sides with 0 team-only clears;
     - 00dunes A: slot 3, 157 muster turns before r500 (reproduced loss);
     - 02gift-wrapping, by contrast: 187 muster turns for 186 team picks.
   - **Why:** the clock-reset design (h_teamclear) lets a champion idle at a ring for hundreds of rounds on contested or large maps.
4. **Altar-camp standoff breaker** (new loss pattern, base code).
   - **The trigger:** we are behind on tributes, no gems have been banked for N (~150) rounds, and visible enemies idle within ~4 of the preferred altar.
   - **The response:**
     - recall and heal to full, since the 45% recall threshold kept our 460-800-HP champions from healing for 1,500 rounds;
     - lower the bank threshold;
     - commit all champions together to the altar fight, or bank at another altar.
   - **Evidence:** c3 vs starter-python on 02treasure-box A, 0-80. Three starter champions parked at (18,14), (20,14) and (20,16) by the altar (17,17) from r450 to r2000. Our five held 8-18 gems each and never banked or engaged. Team logic was inactive (1 pick, 1 muster turn). The code paths involved are q24's (bank thresholds, the 45% recall rule, `handle_enemies`), so q24 can probably reach the same state, though that was not observed here.
   - **Why:** a 0-80 round-limit loss to the weakest opponent. Ladder opponents that bank early and then turtle at the altar would exploit it.
5. **Gate design note.** The gate's (d) check should compare flips on the maps where the mechanism acts against flips elsewhere, as the family table in §2 does. Here the off-target slice carried the whole gain.
   - Re-rolls alone move a score by several games: the placebo replicates of q24 vs tb_merge_b scored 85 and 90 against the gate run's 87. This traced c3 replicate scored 78 against 80.
   - Recommend adding the "targeted vs other" split, and a muster/activity census of the new logic, to every gate report.
