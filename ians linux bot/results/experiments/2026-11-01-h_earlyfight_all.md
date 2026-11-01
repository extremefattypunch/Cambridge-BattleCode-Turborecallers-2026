# Experiment: h_earlyfight_all, the group-balance fight rule applied all game (2026-11-01)

STRATEGIES Q12 / T17, batch 1. The bot was implemented and screened on the dev PC (sprint vs tb_merge_b 23W-17L). Its raw games were lost and its analysis session never ran. This report covers the all-maps head-to-head (also the LOOP.md §4a gate run) and the mandatory analysis, run on the cluster. The bot code was not changed.

## Hypothesis
- **What:** score each local fight as `(sum hp x sum dps)` for us (me + allies within 7, or within 4 for the "advantage" ratio) against the enemies within 7.
  - **Advantage (>= 1.4):** the whole local group commits: engage limit +0.4, never "clearly losing", always trade with an adjacent melee.
  - **Disadvantage (<= 0.75):** take no new fights unless the target dies to this hit, trade with an adjacent melee only when it dies in 2 hits, and step back toward the nearest visible ally while still hitting.
  - v2 (`h_earlyfight`) does this only before round 300. v3 (`h_earlyfight_all`, this bot) sets `EARLY_ROUNDS = 2000`, so the rule runs all game.
- **Source:**
  - 00dunes-type losses vs sf_bank: 7 of our champion deaths before r300 against their 1.
  - Diagnostic games: early deaths were a lone non-dash melee trading next to an enemy melee while 2-5 enemies were within 6, or a chase into 3-4 enemies.
  - Census: the *enemy's* early deaths predict our wins; our own early deaths do not.
  - On the dev PC, the all-game variant flipped 01concentrated-wealth on both sides, where the fights happen after r500.

## Setup
- **Candidate:** `bots/h_earlyfight_all`, forked from champion `tb_merge_b`. Only `src/bot.py` differs: `group_balance()`, a rally-aware `retreat()`, `hit_while_leaving()`, and the engage, clearly-losing and adjacent-melee overrides in `handle_enemies`. The draft is unchanged, so every game is a mirror comp.
- **Main run:** `tools/onslurm.sh -c 24 -m 16G -t 00:20:00 -J h_earlyfig -- python3.12 tools/eval.py h_earlyfight_all tb_merge_b --maps all --jobs 16 --keep --tag b1-h_earlyfight_all-all`. That is 70 maps x both sides = 140 games, with Slurm job 56768277 taking 2 min 51 s.
- **Two controls,** each a single 2-3 minute job on the free `test` partition, run to answer the analysis questions with paired evidence:
  - `tb_merge_b vs tb_merge_b --maps all --one-side` (tag `b1-tb_merge_b-mirror-all`, job 56769471). The champion is in the candidate's seat, so this is the true "before" for each map and seat.
  - `h_earlyfight` (v2, rule only before r300) `vs tb_merge_b --maps all` (tag `b1-h_earlyfight_v2-all-control`, job 56769239). v2 is identical to v3 before r300, so v3 against v2 isolates what applying the rule after r300 does.
- **Determinism checks,** as local single games in `matches/b1-h_earlyfight_all-determinism/`:
  - 01shortcut with the candidate as team B, re-run on the login node. The 1,763-event stream is byte-identical to the Slurm eval game.
  - `g_earlyfight` (a byte-identical copy of `h_earlyfight` under another directory name) on the same map reproduces the v2 eval game exactly.
- **Analysis scripts:** `tools/analyze_match.py --summary --games`, per-game narratives, `postmortems/match_metrics.py`, plus ad-hoc phase, paired and repeat-death scripts. The ad-hoc scripts were kept in the session scratchpad and are not in the repo; their numbers are below.

## Results (verbatim)
```
SUMMARY h_earlyfight_all vs tb_merge_b: 84W-56L (60%)  avg gems 684 vs 619  avg deaths 10.6 vs 13.5  botFaults(A) 0
SUMMARY h_earlyfight vs tb_merge_b: 77W-63L (55%)  avg gems 657 vs 606  avg deaths 12.2 vs 13.0  botFaults(A) 0      (v2 control)
SUMMARY tb_merge_b vs tb_merge_b: 32W-38L (46%)  avg gems 590 vs 661  avg deaths 12.5 vs 11.6  botFaults(A) 0         (mirror, one side)
```
- **Gate 4a (head-to-head):** 84/140 ≥ 82, the 95% Wilson interval is [51.7%, 67.7%], and botFaults are 0. **Pass**, by 2 games. Gates 4b (paired gauntlet) and 4c (release run) were not run here.
- **By seat:** as team A, 45W-25L (mirror seat A: 32/70); as team B, 39W-31L (mirror seat B: 38/70).
- **Map pairs:**
  - won both sides: 21 maps;
  - lost both: 7 (00ambush, 00crater, 00expanse, 00lost-world, 01broken-curve, 01corridors, 02the-pond);
  - split: 42.
- **match_metrics (candidate):** 140 games, 3,751 tributes, mean tribute 25.5, of which 437 were small (<10).
  - Deaths: 9.3 per game to champions and 1.2 per game to camps.
  - Gems lost: 84.2 per game to champions and 10.2 per game to camps.
  - **fuelExhausted 84.2 per game**, against 84.7 per game for tb_merge_b in the same games. The mirror's tb_merge_b averaged 80.1 (87.4 in seat A, 72.9 in seat B), so this is not a regression.
  - Wards 405.8 per game, consumables 8.7 per game.
- **analyze_match --summary:**

  | | wins | losses |
  |---|---|---|
  | Gems (us-them) | 856-479 | 426-829 |
  | Kills (us/them) | 16.1/6.0 | 6.9/14.4 |
  | Gem lead at r250 | +10 | -9 |
  | Gem lead at r500 | +40 | -56 |
  | Gem lead at r1000 | +139 | -155 |
  | First tribute (us/them) | 176/187 | 200/176 |
  | Mean tribute | 26.5 | 23.1 |
  | fuelExh per game | 81.0 | 88.9 |

### Sprint subset: does it reproduce the dev-PC record? **No**
| | Dev PC | Cluster (same 20 maps x 2) |
|---|---|---|
| h_earlyfight_all (v3) | 23W-17L, gems 680 vs 617, deaths 10.3 vs 12.7 | **26W-14L (65%)**, gems 703 vs 581, deaths 9.4 vs 13.2 |
| h_earlyfight (v2) | 22W-18L, gems 655 vs 603, deaths 12.2 vs 12.5 | 22W-18L, gems 632 vs 583, deaths 12.4 vs 12.6 |
| tb_merge_b mirror | 5W-15L | 5W-15L |

- **What matches:** 01concentrated-wealth reproduces the dev-PC scores exactly on both sides (836-482 and 942-531). On the cluster, games are deterministic across nodes and directory names (the checks above).
- **What doesn't:** the averages differ even where the W-L matches, so some dev-PC sprint games were not played by the committed source.
- **Why (two possibilities, which can't be told apart now that the raw games are lost):**
  - **An earlier source revision.** Even a source change that leaves the logic alone moves fuel use and diverges games; see "Noise floor" below.
  - **The dev-PC parallel-build race.** Five batch-1 evals rebuilt `tb_merge_b/.cambc/build/bot.wasm` at once; `tools/onslurm.sh` now avoids this.

## Analysis session

### 1. Did the targeted mechanism change? Yes: we die less early, but we don't kill more
These are paired with the mirror (the champion in the same seat on the same map). All figures are per game for the phases r<300 / 300-999 / ≥1000.

| | Candidate | Mirror (tb_merge_b in our seat) |
|---|---|---|
| Our champion-kill deaths | **1.33** / 4.07 / 3.93 | 1.73 / 4.49 / 4.66 |
| Their champion-kill deaths | 1.71 / 4.93 / **5.76** | 1.73 / 4.49 / 4.66 |
| Gems we lost to champions | 9.7 / 36.9 / 37.6 | 10.4 / 34.6 / 35.8 |
| Gems they lost to champions | 9.5 / 37.5 / 44.4 | 10.4 / 34.6 / 35.8 |
| Gem lead r300 / r500 / r1000 | +4.5 / +1.6 / +15.3 | 0 / 0 / 0 |
| Lifetime gold (us / them) | 5,212 / 4,586 | 4,785 / 4,785 |

- **Early deaths before r300 fall 23%** (1.73 → 1.33). The enemy's early deaths don't move (1.73 → 1.71). The rule makes the opening **safer, not more lethal**, which is the same finding the dev PC made against imit_test.
- **Early kills are converted a bit better.** We were ahead on net early kills in 56 games (the mirror: 49), and won 75% of them (the mirror: 67%). Games level on early kills went 67% (the mirror: 50%; v2: 48%). That edge comes from the post-r300 rule (§2).
- **Per seat, before r300:**
  - Seat A: our early deaths fall 1.63 → 1.14, early gems lost 11.5 → 5.4, and the r300 lead swings from −16 to +7.
  - Seat B: early deaths fall 1.83 → 1.51, **but early gems lost rise from 9.4 to 14.0** (9.3 gems per death against 5.1), and the r300 lead drops from +16 to +2.
- **Per champion (K/D, candidate vs mirror):**
  - Vesper 3.78/1.71 vs 2.92/2.30, submitted 184 vs 160;
  - Vendetta 4.35/2.44 vs 3.93/2.74;
  - Marcella 2.09/2.94 vs 2.33/3.29 (she fights less: champion damage 5.6k vs 7.1k);
  - HoR 1.49/2.30 vs 1.13/2.47;
  - Ryth 1.57/2.61 vs 1.26/2.81.

  Every champion dies less, and ranged Vesper gains the most.

### 2. Does applying the rule all game cause late over-commitment deaths? No, the opposite
v3 against v2 is a paired test: the two are identical before r300, except for the fuel noise below.

| After r300 | v3 (all game) | v2 (r<300 only) | Mirror |
|---|---|---|---|
| Our deaths r300-999 / ≥1000 | 4.07 / **3.93** | 4.54 / 5.10 | 4.49 / 4.66 |
| Their deaths r300-999 / ≥1000 | 4.93 / **5.76** | 4.91 / 5.24 | 4.49 / 4.66 |
| Our "2+ deaths within 15 rounds" ≥r1000 | **0.41** | 0.79 | 0.67 |
| Their "2+ deaths within 15 rounds" ≥r1000 | 0.97 | 0.78 | 0.67 |
| Decisive fights ≥r1000, won/lost (deaths clustered ≤12 rds) | **614/432 (59%)** | 549/535 (51%) | 50% |
| Wins | **84** | 77 | 70 |

- Applying the rule after r300 cuts our late deaths by 23% and halves our late multi-death wipes, without fewer kills. Head-to-head against v2 it flips 27 games for and 20 against.
- The late-game edge shows up in specific maps:
  - **01concentrated-wealth A and B:** first kill at r574, 10-0 kills, 836-482 and 942-531.
  - **00breadcrumbs A:** we were −168 at r250, then won the mid-game fights (our Vesper went 12/0) and won 1001-616. The mirror's seat A lost 588-1001.
- The rule does give gems away on some deaths: v3's mid and late gems lost to champions are 36.9/37.6, against v2's 33.9/34.9. So we die less often but richer. This is concentrated in seat B (45.3/42.1 against v2's 38.9/36.6).

### 3. Where does the +14 over the mirror come from? Almost entirely seat A
- **Seat A:** 45 wins against the mirror's 32, with 24 flips for and 11 against. The gem lead at r1000 goes from −42 to +63.
- **Seat B:** 39 wins against 38, with 15 flips for and 14 against.
- **On about 10 maps the candidate inverts the side bias.**
  - Maps: 00fragment, 00galaxy, 00lanes, 01starfish, 01elk-arena, 01big-world, 02famine, adgato-gemcombat4/5, 00breadcrumbs.
  - In the mirror, team B wins these. With the candidate in either seat, **team A** wins: the candidate wins as A and tb_merge_b wins as A.
- **Example, 01elk-arena:** a central contested altar, where whoever holds it after r300 tributes everything.
  - In the mirror, tb_merge_b in seat B won the early fights 7-3, tributed first at r317 and won 1008-0.
  - The candidate in seat B took 2 kills before r300, then none from r73 to r435, while dying at r264, 280, 345 and 365. It lost 0-1008.
  - The candidate in seat A won 900-180, where the mirror's seat A lost 0-1008.
- So the "disadvantage" retreat gives up contested fights that tb_merge_b, playing the favoured side, would have won.

### 4. Why the remaining 56 losses were lost
- **25 of the 56 are flips against the mirror; 31 are losses tb_merge_b also has in that seat.**
- **Snowball / feeding (21):** we die at least twice as often as them, with at least 10 deaths.
  - Examples: 01hooks A 22-1001 (45 deaths vs 12), 00oasis B 181-1013 (38 vs 3), 02treasure-box B 443-1001 (41 vs 7), 00interlock B 63-1039 (26 vs 2), 00fragment B 94-966 (27 vs 4), 01elk-arena B, 00lost-world A/B, 02fields A, 00eight A.
  - The shape:
    - The enemy Vendetta or Vesper becomes a fed carry: 01hooks Vendetta 29/4 with Strength x20; 00oasis Vesper 19/1, Strength x15; 00fragment Vesper 15/1, Strength x20; 00eight Vendetta 19/0, Strength x19.
    - Then our champions die one at a time, 30-100 rounds apart, at the same sites. 00fragment B lost Marcella, Vendetta and Vesper around (16,4)-(16,11) seven times between r516 and r1052, tributing 0 gems from r500 to r1000. 00interlock B kept dying around (20-24,18).
  - Across all losses, after r300:
    - we die 12.5 times per game against their 5.4;
    - **45% of those deaths are within 4 tiles of one of our deaths in the previous 300 rounds;**
    - **68% are isolated** (no other death of ours within 15 rounds).
  - It is not the rule: tb_merge_b's own losses (our wins) look the same, with 14.2 deaths per game, 49% at a repeat site and 65% isolated. The mirror's losing side: 14.2 per game, 44% repeat. It is a **shared weakness**.
  - The early fight often decides it. On 00eight, the r39-48 centre collision decides the game on both sides: as A we lost it (Vendetta r39, Marcella r44) and lost 181-1019; as B we won it and won 1014-28.
- **Behind on farm, deaths similar (19):** examples are 02tangle B (477-1010: 16 clears vs 53, one champion-kill death in the whole game), 01fracture A (808-1013: 3 deaths vs 0, 61 clears vs 73), 00expanse A/B, 00vault B (0-1139) and 00galaxy B. These are farming-efficiency gaps on big maps, mostly shared with the mirror, so they are not caused by this rule.
- **Close (10):**
  - The list: 00ambush A/B, 00crater A/B, 01big-world B, 01corridors B, 00breadcrumbs B, 00split A, adgato-gemcombat4 B, 00rushbait-v2 B.
  - **Unbanked gems at r2000 exceeded the margin in 4 of them:**
    - 00ambush B lost by 10 holding 126. Four carriers were **frozen** with 29, 63, 17 and 17 gems from r1534-1614 until the end. The mirror's seat B on that map also froze 37 gems from about r1705. This looks like the lock-memory 2-cycle (h_3pick) or the Q21 freeze.
    - 00crater A lost by 27 holding 64, picked up after r1950.
    - 00crater B lost by 52 holding 128.
    - 01corridors B lost by 19 holding 59.
- **Tiebreak or near-0 (6):** 02gift-wrapping A, 02guardians A, 02the-pack A, 01boss-battle A and 00stampede B were 0-0 on lifetime gold; 01yellow-brick-road A was 0-11 (the Q21 freeze map). The 0-0 maps flipped evenly against the mirror (4 for, 4 against). h_goldtie is the targeted fix.
- **Fuel:** losses average 88.9 exhaustions per game against 81.0 in wins. The extremes are map-driven and shared with tb_merge_b in the same games: 00lanes B 1,070 vs 858, 02the-pack 630 vs 1,714, 00vault 484 vs 585, 01yellow-brick-road 415 vs 276. They are not caused by the rule.

### 5. Noise floor (methodology)
- v2 and v3 differ only in the `EARLY_ROUNDS` line (value and comment). Yet **18 of the 140 games diverge before r300**: at r2 in 01shortcut B, r22 in 00eight B, r29 in 00swirl A, and others.
  - The first differing event is a `fuelExhausted` on one side.
  - **7 of those 18 games flipped outcome** (v3 10 wins, v2 7).
- A byte-identical copy under another directory name reproduces exactly. So it is the **source text**, not the bot's name, that shifts fuel use. A turn near the fuel cap then exhausts or not, and the game diverges chaotically.
- **Consequences:**
  - A 140-game head-to-head carries chaos variance of a few games.
  - Snapshot copies made with `tools/newbot.py` are safe.
  - **Any edit after gating, even a comment, invalidates the gate run.**

## Verdict: **kept**
- **Gate 4a passes:** 84/140, Wilson lower bound 51.7%, botFaults 0.
- **The mechanism is confirmed:**
  - our early deaths fall 23% while the enemy's are unchanged;
  - running the rule all game adds +7 wins over the early-only v2 (77 → 84), cuts our late deaths by 23% and halves our late wipes. There is no late over-commitment.
- **Fuel is unchanged** (84.2 vs 84.7 per game).
- **Caveats for the promotion decision:**
  - (a) The margin is 2 games, about the size of the noise floor in §5.
  - (b) The whole gain is in seat A (+13); seat B is flat (+1).
  - (c) Gate 4b (paired gauntlet) and 4c (release run) still need to run before any promotion.
- It remains a good component for the Q24 combination. The combination needs its own 140-game gate, because merging changes the source text (§5).

## New hypotheses generated
1. **Contested-objective exception to the "disadvantage" retreat.**
   - Evidence: seat B gains nothing (39 vs the mirror's 38), and 13 of the 20 flips against that aren't 0-0 or near-0 are seat B. On 01elk-arena B the candidate stopped taking the arena fights tb_merge_b won 7-3. Seat B's early gems lost rose from 9.4 to 14.0.
   - Change: don't regroup (keep tb_merge_b's logic) when the fight is on or next to an altar we are contesting, or when the enemies in range are channelling or low. Alternatively, lower `GROUP_DISADV` from 0.75 to about 0.6.
   - Expected effect: keep seat A's +13 while recovering seat B's lost contests.
2. **Death-site and fed-carry avoidance (feeding stop).**
   - Evidence: in losses (both bots) 45-49% of post-r300 deaths are within 4 tiles of a recent ally death, and 65-68% are isolated. 00fragment B lost 7 champions around (16,4)-(16,11) to a Strength x20 Vesper and her team.
   - Change: put the last ally death site and round in shared memory (8 bytes is enough for x, y and round). Skip camp groups within about 5 tiles of it for about 100 rounds unless `group_balance` ≥ 1.4. Treat an enemy whose strength is at least 2x ours as a no-go radius.
   - Expected effect: this is where 21 of the 56 losses snowball.
3. **Endgame carrier audit.**
   - Evidence: 4 close losses ended holding more unbanked gems than the margin. In 00ambush B, four carriers sat frozen with 126 gems from r1534-1614 until r2000; the mirror froze too.
   - Change: first check whether `LOCK_MEMORY_FIX` (h_3pick) or the Q21 respawn fix clears it. Then stop picking up new groups whose capture plus walk to an altar can't finish by r2000 (00crater: 64 gems picked up after r1950).
4. **Fuel headroom for robustness (supports Q25).**
   - Evidence: source-only changes diverge 13% of games through near-cap fuel turns (§5); the candidate averages 84 exhaustions per game.
   - Change: cheaper sensing would cut exhaustions and make gate results less chaotic, as well as freeing compute.
5. **First-collision fights decide mirror maps.**
   - Evidence: on 00eight the r39-48 centre fight decided the game on both sides (181-1019 vs 1014-28).
   - Change: hold the first approach to the map centre until two or more allies are within 4 tiles. This is a narrow opening-only version of the group rule that also covers the "commit" side.
