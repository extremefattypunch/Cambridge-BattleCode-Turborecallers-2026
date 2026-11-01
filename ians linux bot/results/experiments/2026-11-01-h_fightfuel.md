# Experiment: h_fightfuel (2026-11-01)

## Hypothesis
- **What (STRATEGIES Q13 / T18):** suspended turns lose fights, so cap or cache the expensive sensing and fight code and fights should never suspend. A suspended bot resumes mid-code next round and acts a turn late on stale data.
  - The candidate caches or caps `observe`, `threats`, `retreat`, `kit_units` and `reset_target` behind the switches `OBSERVE_FAST`, `THREATS_FAST`, `RETREAT_FAST` and `KIT_FAST`.
  - It adds two low-fuel early exits: `FUEL_RETREAT_DASH` (350k) and `FUEL_KIT_AIM` (400k).
  - The game logic is otherwise unchanged. `VALIDATE` showed 0 mismatches against the original code (see `bots/h_fightfuel/NOTES.md`).
- **Source:** the 70-map check of tb_merge_b, where its losses averaged 183 fuel exhaustions and its wins 69 (analyze_match --summary).
  - The dev-PC profiling found that most exhaustion is a per-turn **sensing** baseline, not fights. On 02the-pack one champion was over budget on about every second turn with no enemy in sight.
- **Previous status:** sprint vs tb_merge_b 22W-18L (55%) on the dev PC. The raw games were lost and the analysis session never ran.

## Setup
- **Candidate:** `bots/h_fightfuel`, forked from the champion `tb_merge_b`. Code as committed in 8b4bf4b, unchanged here, with `PROF` and `VALIDATE` off.
- **Run:** `tools/onslurm.sh -c 24 -m 16G -t 00:20:00 -J h_fightfue -- python3.12 tools/eval.py h_fightfuel tb_merge_b --maps all --jobs 16 --keep --tag b1-h_fightfuel-all`
  - Slurm job 56768275 on the `test` partition, cambc 4.0.0 / engine 2.0.0.
  - 70 maps × both sides = 140 games; stats and replays are in `matches/b1-h_fightfuel-all/`.
- **This is also the LOOP.md §4a gate head-to-head.**
- **Analysis tools:**
  - `analyze_match.py --summary --games`;
  - per-game narratives of all 68 losses and of the surprising wins;
  - `postmortems/match_metrics.py`, plus the same script mirrored onto tb_merge_b's side;
  - a scratch per-game fuel/fight script. It counts suspensions within ±3 rounds of that champion dealing or taking champion damage ("in-fight"), and champion-caused deaths within 5 rounds after the victim's own suspension ("suspension-linked deaths"). It reads both teams from the same stats JSON.

## Results
```
SUMMARY h_fightfuel vs tb_merge_b: 72W-68L (51%)  avg gems 639 vs 626  avg deaths 12.2 vs 12.9  botFaults(A) 0
```
**Win-rate breakdown:**

| Subset | Record |
|---|---|
| All 140 | **72W-68L (51.4%)**. 95% Wilson lower bound 43.2%. **Gate needs ≥ 82/140: FAIL** |
| Side A / side B | 37W-33L / 35W-35L |
| 20 SPRINT maps (40 games) | **21W-19L (52.5%)**. Dev PC: 22W-18L. **Does not reproduce exactly** (see below) |
| 12 QUICK maps | 12W-12L |
| 50 non-sprint maps | 51W-49L |
| Map pairs (A,B) | WL 25, LW 23, WW 12, LL 10. 48/70 maps split by side |

**Sprint reproduction:** the sprint subset is one game worse than the dev PC (21-19 vs 22-18). The games themselves differ, not just one result: average fuel exhaustion on the sprint subset is 7.2 (h_fightfuel) vs 75.5 (tb_merge_b), against the dev-PC NOTES figures of 6.7 vs 71.2.
- The cluster engine reproduces the dev-PC champion baseline vs imit_test (34-6). Seeds are fixed per map.
- The bot directory was first committed at the handoff (8b4bf4b), after its dev-PC evals. So the most likely cause is that the dev-PC sprint run used an intermediate iteration of the code.
- The dev-PC per-map lines are lost, so the cause cannot be confirmed.
- Both numbers are within sprint noise (about ±8%).

`match_metrics.py` output, with the same metrics mirrored for tb_merge_b in the same 140 games:

| Metric (per game) | h_fightfuel | tb_merge_b |
|---|---|---|
| fuelExhausted | **4.8** (676 total) | **73.3** (10,261 total) |
| deaths by champion | 10.9 | 11.7 |
| deaths by camp | 1.2 | 1.1 |
| gems lost to champions | 79.0 | 79.1 |
| gems lost to camps | 7.7 | 8.1 |
| mean tribute | 24.9 | 25.1 |
| botFaults | 0 | 0 |

`analyze_match --summary` key rows (wins vs losses, "us" = h_fightfuel):

| Metric | Wins (72) | Losses (68) |
|---|---|---|
| fuel_us | 4.4 | 5.3 |
| tb_merge_b fuel in the same games | 60.2 | **87.1** |
| first tribute us / them | 138 / 165 | 207 / 223 |
| kills us / them | 15.5 / 6.8 | 7.7 / 15.3 |
| gem lead at r250 / r500 / r1000 | +32 / +78 / +147 | −13 / −43 / −126 |
| mean tribute | 26.3 | 22.3 |

## Analysis session

### 1. Did the targeted mechanism change? Yes, completely.

| Fuel metric (per game, same 140 games) | h_fightfuel | tb_merge_b |
|---|---|---|
| fuelExhausted (all) | 4.8 | 73.3 (−93%) |
| suspensions "in a fight" (±3 rounds of champion damage) | **0.1** | **8.1** (−99%) |
| suspension-linked deaths (died ≤ 5 rounds after own suspension), total | **1** | **132** |
| in wins / in losses | 4.4 / 5.3 | 60.2 / 87.1 |

**On the heavy maps** (the three that drove the original loss average):

| Map / side | Result | Suspensions h_fightfuel / tb_merge_b | What decided it |
|---|---|---|---|
| 02the-pack A | L 0-0 | 0 / **1,815** (Marcella 901) | Gold tiebreak, 799 vs 1,704. All 3 deaths by r459, then a frozen standoff |
| 02the-pack B | W 0-0 | 0 / 73 | Gold tiebreak, 1,232 vs 692. Our Marcella went 3/0 by r328 |
| 01yellow-brick-road A | W 4-0 | 15 / 170 | The only tribute on the map: our Ryth, 4 gems at r232, from the only clear (r220) |
| 01yellow-brick-road B | L 0-0 | 51 (our Ryth 17) / 263 | Gold tiebreak, 100 vs 300 (their Marcella 3/0 by r287) |
| 01boss-battle A | L 0-0 | 5 / 316 | Gold tiebreak, 3,899 vs 4,069 |
| 01boss-battle B | W 0-0 | 5 / 294 | Gold tiebreak, 4,555 vs 3,915 |

Heavy maps went 3W-3L, and each map split by side. The suspensions pile up during the long frozen standoff that follows the early skirmishes, when nothing is contested. That is why removing them changed nothing.

Remaining hotspots in h_fightfuel, as NOTES predicted:
- 00vault: 111 and 113 suspensions (Heart of Ruin 57 and 43);
- 01islands: 100 and 96;
- 01yellow-brick-road B: 51;
- 01big-world: 18 and 26.

### 2. Did fewer suspended turns change fight outcomes? No measurable effect.
- **Kills:** h_fightfuel had 1,644 champion kills to tb_merge_b's 1,531 (+7%). Per game, though, it had more kills in 66 games and fewer in 66 (8 equal), so the sign test gives p ≈ 1.0.
- **Gems lost to champions are identical:** 11,061 vs 11,073. The extra kills were on carriers with few gems.
- **Champion damage per game is identical:** 30,460 vs 30,461.
- **Suspensions do not fall in the decisive phase.** Before r300, tb_merge_b's in-fight suspensions were 2.5 per game in h_fightfuel's wins and 1.9 in its losses. Its mid-game (r300-1000) in-fight suspensions were 4.5 vs 2.9. Its all-cause suspensions were about 21 per game before r300 in both groups.
- **The original correlation does not hold.** Here tb_merge_b exhausted *more* in the games it won (87.1 per game) than in the games it lost (60.2). The original "losses 183 vs wins 69" came from map type (stalemate and heavy-sensing maps that end in tiebreaks), not from suspensions causing losses.
- **No dose-response by tb_merge_b's total suspensions:**

  | tb_merge_b suspensions per game | h_fightfuel record |
  |---|---|
  | [0, 10) | 27-21 |
  | [10, 30) | 16-19 |
  | [30, 60) | 9-14 |
  | [60, 100) | 8-4 |
  | 100 or more | 12-10 |
- **The in-fight split shrinks under a stricter definition.** Splitting by tb_merge_b's in-fight suspensions gives 36-22 where it had 5 or more and 36-46 where it had fewer. That split is confounded: a team being beaten takes more damage, which creates more "in-fight" windows. Counting only suspensions near damage *dealt*, games with 3 or more went 26-17, which is within noise.
- **Where in-fight suspensions were dense, h_fightfuel won.** Example: 01elk-arena A, where tb_merge_b had 71 in-fight suspensions and 11 suspension-linked deaths. h_fightfuel won 780-300 with kills 49/20. The reverse side (25 in-fight) was lost 302-706. Such games are rare against our own mirror.

### 3. Why the 68 losses were lost
1. **Early skirmishes snowball, and fuel plays no part in them.**
   - **First blood predicts the result.** When h_fightfuel draws first blood it went 49W-28L; when tb_merge_b does, 20W-38L.
   - **Early deaths:** champion deaths before r300 average 1.88 (us) vs 1.28 (them) in losses, and 1.22 vs 2.31 in wins. We had more early deaths than the opponent in 29 of the losses and fewer in only 18.
   - **The lead is settled early.** Excluding tiebreaks, the winner was ahead for good from r ≤ 500 in 35 of the 62 losses.
   - **31% of champion kills before r300** were same-champion duels (Vesper on Vesper, Vendetta on Vendetta). A random pairing would give about 20%.
   - **Examples:**
     - 00crater A: we lost Marcella r70, Vendetta r135, HoR r141 and Ryth r165. Their Vendetta finished 21/0 with 10 Strength emblems, and we lost 90-1007.
     - 00crater B: their Vendetta 13/1, Marcella 6/0; 373-1029.
     - 00eight B: first death r40, kills 1/42, 52-1000. The mirror game, 00eight A, was the exact reverse: first kill r46, kills 37/4, 1045-152.
     - 01broken-curve B: Vesper, Vendetta and Marcella each died to their counterpart at r106/166/199; kills 0/13, 223-1174. Neither team suspended once.
     - 00vault A: 4 deaths r128-180 before our first kill (r344); 0-1061 by r702.
2. **Both-side losses (LL maps, not explained by side):**
   - The 10 maps were 00ambush, 00collision, 00contest, 00crater, 00dunes, 00pilgrimage, 00ribs, 01big-world, 01starvation and 02uncharted-lands.
   - Their kill difference over both sides: −52 (crater), −35 (dunes), −34 (starvation), −25 (ribs), −21 (collision), −14 (contest), −11 (pilgrimage), −7 (ambush), −4 (big-world), −3 (uncharted-lands).
   - tb_merge_b's fuel on these maps was low: 2 to 77 suspensions per pair.
   - So these are early-fight losses, not fuel losses.
   - h_fightfuel had 0 suspensions in 14 of these 20 games. The other 6 were 00ambush (6, 7), 01starvation (4, 3) and 01big-world (18, 26). 01big-world is a low-contact timeout loss (kills 1/0 and 0/5).
3. **0-0 tiebreaks: 6 losses and 5 wins.**
   - The maps were 00stampede, 01boss-battle, 01yellow-brick-road, 02gift-wrapping, 02guardians and 02the-pack.
   - They are decided by lifetime gold, then kills, then team B (h_goldtie / T16 territory).
   - 02gift-wrapping is an exact mirror (0 gold each side), so team B wins.
4. **Tempo:** h_fightfuel tributed first in 42 of its 72 wins (23 later) but in only 29 of its 68 losses (33 later). Mean tribute size was 26.3 in wins and 22.3 in losses.

### 4. Surprising wins
- **00eight A (1045-152):** first kill at r46, then 5 enemy deaths by r187. Our Vesper finished 16/0 with 344 gems. tb_merge_b had 96 suspensions there (35 in-fight, 6 suspension-linked deaths), but they came *after* it fell behind. The mirror game (00eight B) shows the same snowball in the other direction with h_fightfuel suspending 0 times. So the cause is the early skirmish, not fuel.
- **00swirl B (1002-7, kills 58/4)** and **01hooks B (1001-0, kills 40/9)** are the same snowball shape. Their A sides were lost 446-610 and 165-913.
- **Exact mirrors.** On 01corridors, 02arena, 02guardians and 02gift-wrapping both bots played identically (mirror-image stats on the two sides), so each split 1-1.
  - On every other map play diverged, even with 0 suspensions on both sides (01broken-curve B, adgato-gemcombat1 B).
  - The reason: the fuel-dependent branches (`FUEL_SCORE_FLOOR` and `build_static_fields`) take a different path when more fuel is left. Small decision changes then cascade through the early fights.

## Verdict
**Rejected** as a promotion candidate, and as the win-rate hypothesis "suspended turns lose fights".
- **Gate:** 72/140 (51%) with a Wilson lower bound of 43%, so it fails §4a (82/140 needed). botFaults were 0.
- **Mechanism:** fully delivered. Suspensions fell 93% (73.3 → 4.8 per game), in-fight suspensions 99%, and suspension-linked deaths from 132 to 1.
- **Outcome:** unchanged. The kill sign was 66-66, gems lost to champions were identical, and the heavy maps went 3-3.
- **Why:** suspensions happen mostly in idle sensing and standoff phases. Games are decided by early skirmishes, where tb_merge_b suspends only about 2 times per game.
- **Keep the code as infrastructure:** it preserves behaviour and frees about 2M fuel per turn. It is safe to carry in the Q24 combo, but expect +0 head-to-head from it.
- **Deprioritise Q25** (cheaper sensing) as a win-rate lever. The "losses have more exhaustion" correlation was confounded by map type.

## New hypotheses generated
- **Q26: First-strike spacing in early duels.**
  - **Evidence:** first blood → 49W-28L vs 20W-38L; 31% of pre-r300 kills are same-champion duels; losses average 1.88 vs 1.28 early deaths. Examples: 01broken-curve B, Vesper/Vendetta/Marcella killed by their counterparts at r106/166/199; 00crater A, 4 deaths by r165.
  - **Rule:** before r300, never end a turn inside an equal-or-stronger enemy's threat range (its attack range + move) unless we attacked this turn or have local numbers. Hold at threat range + 1 so the enemy must step in and give us the first hit.
  - **Relation to T17:** this complements h_earlyfight_all (T17). T17 is a group rule; this is turn-level initiative.
- **Q27: Spend the freed fuel on early-fight evaluation.**
  - **Evidence:** h_fightfuel leaves about 2M per turn unused (4.8 suspensions per game), while early fights decide about 64/36 of games.
  - **Change:** build on h_fightfuel and add an exact duel or skirmish simulation for engage/flee decisions: HP, damage, cooldowns, turn order (the starting team swaps every round), and stun timing. This turns the fuel headroom into the thing that actually decides games.
- **Q28: Check the fuel fix against non-mirror burst comps.**
  - **Evidence:** in the cluster gauntlet, tb_merge_b's losses to lad_vcst include 01elk-arena B with 43 in-fight suspensions and 15 suspension-linked deaths (K/D 20/55). The dev-PC record was h_fightfuel vs lad_vcst 34-6, against tb_merge_b's cluster baseline of 27-13.
  - **Test:** run the paired sprint gauntlet entry vs lad_vcst (40 games). It is cheap, and it decides whether the fuel module helps on the ladder even though it is neutral in the mirror. Q24's gauntlet would cover it.
- **Finding for T16 / Q2 (not a new hypothesis):** the 11 games that ended 0-0 were decided by lifetime gold from clears and kills (the exception is 02gift-wrapping: 0 gold each, so team B won).
  - On the heavy maps, the gold gap was built in the first ~450 rounds. For example, 02the-pack A: clears 11 vs 21, all deaths by r459.
  - The frozen standoff that followed, where tb_merge_b's suspensions piled up, changed nothing.
  - This supports gold-tiebreak play (h_goldtie) on those maps.
