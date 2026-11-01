# Experiment: h_tempo, a Jungle-first farming build (Q28) (2026-11-01)

## Hypothesis
- **What:** we lose farming races at ~1,500 because our all-Bruiser item build makes us take far more camp damage per camp damage dealt than the teams that beat us. Every ~1,500 team that out-raced us buys a farming or damage-reduction emblem first (Jungle, Durability, Monster, Treasure), then Strength.
  - **The change:** make the first emblem Jungle (-30% damage from camps) on the champion's main stat, and fix the latent `threats()` bug. That bug scaled *total* incoming damage (enemy champions included) by 0.8 whenever a Jungle emblem was owned.
  - **Expected effect:** fewer low-HP recall trips, more farming time and faster races.
- **Source:** ladder pull of 1 Nov (STRATEGIES Q28) and the previous diagnosis stage (traced copies `bots/dbg_q28*`, `matches/q28dbg/`).
  - **The 8 close race losses** (09810aca 00monolith B, 0bbbd76e 00rows A, 2225b1cd and 24554620 00quadrants B, 2fb86344 00quadrants A, 5130aa76 00lanes A, 97d1757c 00split A, 7deecc7a 00road_of_riches B), recomputed with `tools/camp_metrics.py`:

    | | camp taken/dealt (pooled) | gems collected per champion per 100 rounds | damage per monster-active round after r1000 |
    |---|---|---|---|
    | Us | **0.419** | 15.0 | 129 |
    | Them | **0.226** | 17.5 | 181 |

    They reached 1000 at a mean of r1405.
  - **The gap is not only in losses.** In 7 ladder race wins our ratio was still 0.465 against their 0.283.
  - **ez's emblem order in 2fb86344** (00quadrants A, lost 767-1018 at r828):
    - Jungle came first on every champion: Ryth r261, Vesper r292, Marcella r313, Tavi r322, Varg r546.
    - Treasure and Durability followed.
    - Our first emblem was Marcella's Bruiser-Focus at r239; Vesper's first was at r702.
    - Their gold was 3571 against our 1645.

## Setup
- **Candidate:** `bots/h_tempo`, forked from the champion `tb_merge_b` with `tools/newbot.py`. Every change sits behind a flag at the top of `src/bot.py`, keyed only on champion plan and owned items, with no map names.
  - **TEMPO_JUNGLE:** in `bruiser_item()`, a planned champion that owns no Jungle emblem buys `JUNGLE_SHARD_OF_<plan[0] stat>`. That is Strength for Vesper, Vendetta and Tavi; Health for Ryth and Heart of Ruin; Focus for Marcella. Unplanned champions keep the old Jungle → Monster → Power path.
  - **TEMPO_THREAT_FIX:** `threats()` multiplies only the camp sum by 0.7 when Jungle is owned, and drops the 0.8 on the total.
    - `jungle()` now recognises any-stat Jungle emblems.
    - `dps()` applies x1.15 for any-stat Monster emblems.
    - `choose_target`'s existing `dmg_mult = 0.7` now fires for these champions.
  - **TEMPO_JUNGLE_COUNTS** (iteration 1): the Jungle emblem counts as one emblem of its stat in the Bruiser plan.
    - **Why it was needed:** iteration 0 stacked a main-stat Bruiser emblem on top of the Jungle one. At 300 gold Vesper had 10S/1H/1F against the champion's 6S/6H/2F, about 500 HP less in the r150-450 window. The reference `dbg_q28j3` has the same skew.
    - **With the fix:** Jungle replaces the first Bruiser emblem, giving 6S/5H/1F at 300 gold.
  - **TEMPO_STR_ARM** (iteration 2, the final version): after Jungle and one Bruiser emblem, Vesper, Vendetta and Ryth buy a Monster emblem (Strength shards, +15% camp damage). They then follow S:3,H:1 (Vesper, Vendetta) or S:1,H:1 (Ryth).
  - **Verified buy orders** in local smoke games (00lanes):
    - iteration 1: J-S, B-H, B-S…
    - iteration 2: J-S, B-H, Monster-S, then Strength-weighted.
- **Helper bots**, both made with newbot:
  - `bots/h_tempo_s` is byte-identical to the final h_tempo (src), used for the iteration-2 screen.
  - `bots/h_tempo_j` is h_tempo with TEMPO_STR_ARM=False (= iteration 1), used for a diagnostic all-maps run.
- **Opponents and maps:**
  - **Screen:** 13 maps × both sides (26 games per opponent): 00anvil, 00interlock, 00lanes, 00monolith, 00quadrants, 00road-of-riches, 00rows, 00split, 01gold-rush, 01shortcut, 02crossing, 02geodes, 02tangle.
    - These are the 7 ladder race-loss maps plus the other ladder maps where our camp ratio exceeded the opponent's.
    - Opponents: `tb_merge_b`, `tb_aggro` (different logic), `imit_test`, and `starter-python` (uncontested, on the 6 race-loss maps × 2 sides).
  - **Baselines:** `tb_merge_b` against the same opponents on the same maps (`ll1-tbm-scr-*` plus the existing `g-tb_merge_b-vs-*` sprint folders). For the head-to-head, the mirror `b1-tb_merge_b-mirror-all`.
  - **Gate:** `tools/eval.py h_tempo tb_merge_b --maps all --keep --tag ll1-h_tempo-all`.
- **Metric tool:** `python3.12 -I tools/camp_metrics.py [--games] <folders>` (new, read-only).
  - It reports camp taken/dealt (monsterDamageTaken/monsterDamageDone), collectedGems per champion per 100 rounds, damage per monster-active champion-round by phase (P0 <300, P1 300-600, P2 600-1000, P3 1000+), rounds to 500/1000 tributed gems, deaths, kills and fuelExhausted.

## Results
**Iteration 0** (TEMPO_JUNGLE + TEMPO_THREAT_FIX, equivalent to dbg_q28j3 without its TRACE output):
```
SUMMARY h_tempo vs tb_merge_b: 15W-11L (58%)  avg gems 805 vs 754  avg deaths 10.6 vs 11.7  botFaults(A) 0
SUMMARY h_tempo vs tb_aggro: 25W-1L (96%)  avg gems 968 vs 250  avg deaths 5.1 vs 17.6  botFaults(A) 0
SUMMARY h_tempo vs imit_test: 21W-5L (81%)  avg gems 934 vs 584  avg deaths 5.5 vs 25.4  botFaults(A) 0
SUMMARY h_tempo vs starter-python: 12W-0L (100%)  avg gems 1006 vs 180  avg deaths 1.2 vs 29.2  botFaults(A) 0
```
**Baselines** (champion, the 8 screen maps that the sprint gauntlet folders lack; the other 5 maps come from `g-tb_merge_b-vs-*`):
```
SUMMARY tb_merge_b vs tb_aggro: 16W-0L (100%)  avg gems 1018 vs 276  avg deaths 4.1 vs 17.9  botFaults(A) 0
SUMMARY tb_merge_b vs imit_test: 12W-4L (75%)  avg gems 913 vs 687  avg deaths 5.4 vs 20.1  botFaults(A) 0
SUMMARY tb_merge_b vs starter-python: 12W-0L (100%)  avg gems 997 vs 159  avg deaths 1.5 vs 30.2  botFaults(A) 0
```
On the 13 maps, the champion went 26-0 vs tb_aggro and 21-5 vs imit_test. The mirror is 13-13 by construction.

**Iteration 1** (+ TEMPO_JUNGLE_COUNTS):
```
SUMMARY h_tempo vs tb_merge_b: 18W-8L (69%)  avg gems 850 vs 715  avg deaths 10.9 vs 11.5  botFaults(A) 0
SUMMARY h_tempo vs tb_aggro: 25W-1L (96%)  avg gems 1013 vs 248  avg deaths 4.4 vs 19.2  botFaults(A) 0
SUMMARY h_tempo vs imit_test: 22W-4L (85%)  avg gems 972 vs 583  avg deaths 5.6 vs 25.3  botFaults(A) 0
SUMMARY h_tempo vs starter-python: 12W-0L (100%)  avg gems 1010 vs 147  avg deaths 0.9 vs 28.4  botFaults(A) 0
```
**Iteration 2** (+ TEMPO_STR_ARM; run as the identical copy h_tempo_s):
```
SUMMARY h_tempo_s vs tb_merge_b: 19W-7L (73%)  avg gems 894 vs 681  avg deaths 10.6 vs 11.8  botFaults(A) 0
SUMMARY h_tempo_s vs tb_aggro: 26W-0L (100%)  avg gems 1015 vs 242  avg deaths 4.0 vs 18.5  botFaults(A) 0
SUMMARY h_tempo_s vs imit_test: 24W-2L (92%)  avg gems 995 vs 562  avg deaths 4.8 vs 24.3  botFaults(A) 0
SUMMARY h_tempo_s vs starter-python: 12W-0L (100%)  avg gems 999 vs 174  avg deaths 1.0 vs 28.2  botFaults(A) 0
```
**Gate head-to-head** (final h_tempo = iteration 2, 70 maps × both sides, `matches/ll1-h_tempo-all`, replays kept):
```
SUMMARY h_tempo vs tb_merge_b: 75W-65L (54%)  avg gems 637 vs 652  avg deaths 13.9 vs 11.9  botFaults(A) 0
```
**Diagnostic** (iteration 1 on all maps, `matches/ll1-h_tempo_j-all`):
```
SUMMARY h_tempo_j vs tb_merge_b: 71W-69L (51%)  avg gems 625 vs 665  avg deaths 13.9 vs 11.9  botFaults(A) 0
```
**Gate result: 75/140, below the required 82/140.** botFaults 0. The paired gauntlet and release run were not done, because (a) already fails.

`match_metrics` for the gate run (h_tempo's side):
- 3462 tributes, mean 25.8.
- Deaths: 1.1 per game by camps, 12.8 by champions.
- Gems lost: 106.3 per game to champions.
- fuelExhausted: 87.7 per game. The opponent had 78.0, and tb_merge_b in its own mirror 87.4 / 72.9 for side A / B, so fuel use is not worse than the champion's.

`analyze_match.py --summary matches/ll1-h_tempo-all` (75 wins / 65 losses):
- **Champion deaths:** 6.3 per game in wins, **20.2** in losses. Opponent kills in losses: 20.2.
- **First tribute:** r149 in wins, r283 in losses.
- **Gem lead:** +10 / -17 at r250, +130 / -171 at r1000 (wins / losses).
- **Monster damage:** 101k in wins vs 54k in losses.

## Analysis session

### Did the targeted mechanism change? Yes, consistently
Mean per game, us, by opponent set (baseline = tb_merge_b against the same opponent on the same maps):

| Opponent set | Build | camp taken/dealt | gem rate | dmg per active round P2 / P3 | deaths | kills | r1000 (n) |
|---|---|---|---|---|---|---|---|
| tb_aggro, 26 games | baseline | 0.409 | 18.08 | 127 / 202 | 3.6 | 19.7 | 1416 (24) |
| | it0 | 0.356 | 17.46 | 119 / 180 | 5.1 | 16.7 | 1400 (22) |
| | it1 | 0.358 | 17.74 | 118 / 176 | 4.4 | 18.5 | 1429 (24) |
| | **it2** | **0.343** | **18.50** | 129 / 203 | 4.0 | 17.7 | **1385** (24) |
| imit_test, 26 games | baseline | 0.433 | 15.49 | 118 / 189 | 4.8 | 17.5 | 1533 (17) |
| | it0 | 0.379 | 15.85 | 119 / 179 | 5.5 | 17.3 | 1598 (19) |
| | it1 | 0.395 | 16.40 | 116 / 173 | 5.6 | 17.0 | 1511 (18) |
| | **it2** | **0.370** | **17.03** | 127 / 192 | 4.8 | 16.7 | 1523 (**22**) |
| starter-python (uncontested), 12 games | baseline | 0.419 | 17.13 | 110 / 162 | 1.5 | 11.7 | 1224 (10) |
| | it0 | 0.337 | 17.47 | 109 / 175 | 1.2 | 9.5 | 1189 (10) |
| | it1 | 0.337 | 18.06 | 118 / 173 | 0.9 | 10.8 | 1161 (10) |
| | **it2** | **0.327** | **17.99** | 125 / 190 | 1.0 | 11.0 | **1138** (10) |

Against tb_merge_b, in the same games (us vs them):
- **13 screen maps:**
  - it0: ratio 0.349 vs 0.435, gem rate 13.17 vs 12.81.
  - it1: ratio 0.368 vs 0.432, gem rate 13.75 vs 11.69.
  - it2: ratio 0.341 vs 0.435, gem rate 14.48 vs 11.15, P3 169 vs 139.
- **All 140 games, it2:** ratio 0.344 vs 0.411; gem rate **11.49 vs 11.48**; P3 148 vs 139; deaths **13.9 vs 11.9**; kills 10.7 vs 12.8.

What this shows:
- **Camp damage taken per damage dealt falls by 13-22%** in every set, as predicted (0.42 → ~0.34). The opponents' Jungle teams on the ladder sit at 0.23-0.27, so we close about half the gap.
- **The gem rate gain is smaller than the diagnosis expected:** +5% uncontested and +10% vs imit_test with it2, against the +12% expected from dbg_q28j3. Iteration 0 gained only +2%.
- **The Strength arm is what lifts late damage per active round:** P3 162 → 190 uncontested, 150 → 169 vs the champion. This is the second half of the ladder gap (their late damage per active round was 1.3-2.2x ours).
- **Rounds to 1000 uncontested on the race-loss maps** fell 1224 → 1138 (-7%, n=10).
  - Faster on 7 of 10 finished pairs: 00lanes A -244 and B -174, 00road-of-riches A -250, 00monolith B -199, 00split A -74 and B -25, 00quadrants B -25.
  - Slower on 3: 00quadrants A +34, 00monolith A +55, 00road-of-riches B +36.
  - On 00rows: A 927 → 965 gems at r2000, B 801 → 783.
  - Rounds to 500 did not move (895 → 890). The gain arrives after the first emblem, which matches "83% of the deficit builds after r300". Jungle emblems complete at a median of r371 uncontested (p10-p90: r183-r640) and r422 in the gate run (r161-r908). Ladder ez completed theirs at r261-r322.
- **vs imit_test:** three race-map losses flipped to wins and none the other way: 00quadrants B 824-1000 → 1016-795, 00rows A 795-873 → 921-906, 00split B 600-1017 → 1095-700.

### The gate head-to-head: the gain is structural, and it costs fights
- **Map-level change vs the mirror baseline:** 19 maps gained a game, 12 lost one, 39 were unchanged.
- **Binned by the mirror's total deaths per game** (fight intensity):

  | Map bin | Maps | Baseline wins | it2 wins | it1 wins | Extra deaths for us per game (it2) | Gem rate gap vs opponent (it2) |
  |---|---|---|---|---|---|---|
  | farm (<12) | 12 | 9/24 | **15/24** | 13/24 | +1.3 | **+2.0** |
  | mid (12-24) | 28 | 28/56 | **33/56** | 29/56 | +2.3 | -0.2 |
  | fight (≥25) | 30 | 28/60 | **24/60** | 24/60 | +1.6 | -0.6 |

  Baseline-win counts exclude mirror ties.
- **All 12 worsened maps are brawls,** and our deaths rose on every one:
  - 00eight +36 (B: 28-1038, 40 deaths to 2);
  - 01elk-arena +36 (B: 144-1008, 50 deaths);
  - 00fragment +25;
  - 02stalactites +25;
  - 00crater +14;
  - adgato-gemcombat4 +13 (A: 350-1008 at r694);
  - plus 00contest, 00lost-world, 01broken-curve, 01concentrated-wealth, adgato-gemcombat5, 00breadcrumbs.
- **The improved maps are races:** 00lanes, 00split, 00great-wall, 00expanse, 01big-world, 02crossing, 02geodes, 02tangle, 02harvest, 02cuts, 02uncharted-lands, 01islands, 02the-pond, 00interlock, 00oasis, 00ambush, 00pilgrimage, 01corridors, 01the-farm.
- **The 13 screen maps reproduce 19-7 inside the gate run.** The other 57 maps went 56-58. The targeted screen overstated the all-maps effect, because the maps were chosen as the ones where we lose races.
- **Ladder-side race-loss games, gate run vs the mirror:**
  - Now won: 00quadrants B (427-1023 → 1033-800), 00lanes A (509-1015 → 1005-816, ratio 0.59 → 0.34), 00road-of-riches B (856-1014 → 1014-957).
  - Still won: 00split A.
  - Now lost:
    - 00monolith B (1115-608 → 572-1064): 26 deaths, a fight loss.
    - 00rows A (843-766 → 649-905).
    - 00quadrants A (1023-427 → 409-484 at r2000): a mutual Q21 freeze, 6518 and 6282 frozen champion-rounds.

  Both sides go 4W-3L on these 7, but on different maps.

### Why the remaining losses happen (fight regression)
- **Extra deaths are champion kills,** both iterations about +2 per game:
  - it2: 1789 deaths vs the opponent's 1501;
  - mirror: 785 vs 737 (70 games).
- **They grow late.** Champion-kill deaths per game by phase (r<300 / 300-600 / 600-1000 / 1000+):

  | Run | Us | Them |
  |---|---|---|
  | mirror | 1.63 / 1.97 / 2.60 / 5.01 | 1.83 / 1.91 / 2.49 / 4.30 |
  | it1 | 1.69 / 2.16 / 3.29 / 5.71 | 1.64 / 1.89 / 2.50 / 4.61 |
  | it2 | 1.69 / 2.16 / 3.11 / 5.82 | 1.64 / 1.91 / 2.49 / 4.69 |
- **They are not farming deaths.** Camp damage taken in the 30 rounds before a champion-kill death is 103 for us against 151 for the opponent. The share of those deaths with our own monster damage in the last 30 rounds is 0.33 vs 0.34.
- **We are not dying richer.** Gems per death are 8.1 vs 8.2, and shop visits are 31.2 vs 32.0 per game.
- **We die after absorbing less champion damage:** 1377 vs 1480 in the last 30 rounds.
- **The loss of off-stat HP doesn't explain it.**
  - Each Jungle emblem gives up the Bruiser emblem's +1H/+1F (-100 HP on most champions).
  - Iteration 2 gives up more HP than iteration 1 (Monster emblem, S-heavy plan), yet has the same death count.
  - The leading suspect is behaviour. With Jungle owned, `choose_target`'s `dmg_mult = 0.7` and the camp ×0.7 in `threats()` let a champion commit to bigger and farther groups at lower HP. That likely means longer exposure in contested areas, where the unchanged fight model then loses.
  - This is not verified (no TRACE run); see hypothesis 2.
- **01shortcut A vs tb_aggro (it0, 0-0, 20 deaths):** tb_aggro parked on the altar at (27,14). All 20 of our deaths happened on (27,14)/(27,15), and we lost 855 gems; neither team ever tributed. The baseline tb_merge_b won that game 1067-0, so the build change only steered us into an existing weakness: altar camping.
- **Fuel is not the cause.** fuelExhausted per game: 87.7 for us vs 78.0; tb_merge_b's own mirror was 87.4 / 72.9.
- **Freezes are not worse:**

  | Run | Us | Them |
  |---|---|---|
  | gate | 10.1% | 11.4% |
  | it1 | 10.2% | 11.0% |
  | mirror | 12.9% | 12.1% |

### Surprising: some local games are not reproducible
The same code against the same opponent on the same map gave different games in different Slurm jobs:
- 4 of 26 differ between the iteration-2 screen (h_tempo_s) and the gate run (h_tempo): 00lanes A/B, 00quadrants A, 00road-of-riches B.
- 6 of 26 differ between the iteration-1 screen and h_tempo_j's all-maps run.
- **Every irreproducible game is fuel-heavy:** 117-1726 fuelExhausted per game, against a median of 22 (max 517) for the reproducible ones.
- **Consequence:** the "local games are deterministic" rule holds only for low-fuel games. Gate counts on fuel-heavy maps (00lanes, 00quadrants, 00split, 00road-of-riches) carry run-to-run noise.

## Verdict
**Rejected as a submission candidate:** 75/140 against the required ≥ 82/140.

The targeted mechanism did change, in the predicted direction:
- camp taken/dealt fell from ~0.42 to ~0.34 in every opponent set;
- gem rate rose (+5% uncontested, +10% vs imit_test, +2% vs tb_aggro);
- late damage per active round rose with the Strength arm;
- rounds to 1000 uncontested on the race-loss maps fell by 7%;
- the 13 targeted maps went 19-7 vs the champion.

That gain is confined to farming and mid maps (48/80 vs a baseline of 37/80). On fight-heavy maps it loses (24/60 vs 28/60), and deaths rise by about 2 per game, mostly after r600. Do not re-run this build unchanged. The follow-ups below change the conditions.

## New hypotheses generated
Each is meant for STRATEGIES.md (not edited here, per this task's rules).
1. **Q28b: adaptive emblem by observed PvP pressure.**
   - **Idea:** buy Jungle-first only while the team sees little PvP; otherwise keep the Bruiser build. Example triggers: no ally killed by an enemy champion and no enemy champion seen near our camps by the time of the first emblem purchase. Switch back to Bruiser after the first PvP death.
   - **Evidence:** h_tempo wins farm and mid maps 48/80 against a baseline of 37/80, but fight maps 24/60 against 28/60. The ladder race losses were low-to-mid fight games, with about 18 total deaths per game.
   - **Why:** it keeps the race gain without the brawl loss, and it keys on in-game state, not map names.
2. **Q28c: Jungle without riskier targeting.** Keep the Jungle item but leave `choose_target`'s `dmg_mult` at 1.0, or use the 0.7 only for the HP budget and not the cycle test.
   - **Evidence:**
     - deaths rise by about 2 per game in both iterations, despite different HP;
     - the extra deaths aren't farming deaths and grow after r600;
     - we die after absorbing less damage (1377 vs 1480).
   - **Why:** this isolates whether the regression is behavioural (target choice) or statistical. Run it with a TRACE copy to measure exposure to enemy champions.
3. **Q28d: the Strength arm alone, without Jungle.** Monster emblem plus S-weighted Bruiser for basic-attack farmers.
   - **Evidence:**
     - it2 beats it1 on all maps (75 vs 71) with the same deaths;
     - P3 148 vs 134;
     - gem rate 11.49 vs 11.08;
     - uncontested P3 is 190 for it2 against the champion's 162.
   - **Why:** the late damage-per-active-round gap on the ladder (1.3-2.2x) may be the cheaper fix, with no camp-damage trade.
4. **Fuel-dependent non-determinism.**
   - **Evidence:** 4-6 of 26 games differ between runs with identical code, all with fuelExhausted 117-1726 per game.
   - **Why:** it undermines "never re-run, it's deterministic" for fuel-heavy maps and adds noise to gate counts there. Q25 (cheaper sensing) would also restore reproducibility. Test: run one pair twice on 00lanes, 00quadrants, 00split and 00road-of-riches, and diff.
5. **Altar-camping trap** (seen again).
   - **Evidence:** 01shortcut A vs tb_aggro, 20 deaths at one altar tile, 855 gems lost, 0 tributes.
   - **Why:** after k deaths at the same altar within N rounds, switch altars or wait as a group. Any camped single-altar map turns into a 0-score game otherwise.

## Files
- **Candidate:** `bots/h_tempo` (final = iteration 2).
- **Helper copies:** `bots/h_tempo_s` (= iteration 2) and `bots/h_tempo_j` (= iteration 1).
- **Metric tool:** `tools/camp_metrics.py`.
- **Match folders** (gitignored):
  - `matches/ll1-h_tempo-{scr,it1,it2}-{tbm,aggro,imit,sp}`
  - `matches/ll1-tbm-scr-{aggro,imit,sp}`
  - `matches/ll1-h_tempo-all` (replays kept)
  - `matches/ll1-h_tempo_j-all`
  - `matches/h_tempo-smoke`
