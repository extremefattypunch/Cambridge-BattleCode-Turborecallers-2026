# Experiment: h_goldtie, gold-tiebreak play (2026-11-01, cluster)

Batch 1, STRATEGIES Q2 / T16. The implement and test stages ran on the dev PC (see `bots/h_goldtie/NOTES.md`). Their raw games were lost, and the mandatory analysis session never ran. This report covers the full 140-game evaluation on the cluster and that analysis session.

## Hypothesis
- **What:** at round 2000, equal tributed gems (in practice 0-0) are decided by **lifetime gold earned**, then kills, then Team B.
  - A static map check at init sets `no_tribute` when no altar ring tile can be reached without clearing a "guard" group (total strength ≥ 200 or HP ≥ 15,000).
  - With `no_tribute` set, the bot:
    - values groups by gold;
    - never targets a guard;
    - never banks;
    - buys a Treasure emblem first;
    - ignores carried gems in the fight model.
  - From r300, while both teams have 0 tributed gems, `stalled` turns on gold play. Gold play adds two things:
    - the respawn-rule movement fix;
    - chip mode (30 hit-and-run cycles per group instead of 4 after 12 idle healthy turns).
- **Source:**
  - the real ladder loss on 02the-pack (0-0, lost on gold);
  - 5 of the 15 losses in the 70-map check of the champion were 0-0 tiebreaks;
  - the map study in `NOTES.md`: 02the-pack has a 48-wolf ring, 02guardians and 01boss-battle have monolith-only rings, 02gift-wrapping has wrapped groups, and 01yellow-brick-road has a movement freeze.

## Setup
- Candidate: `bots/h_goldtie` (v2, code unchanged), forked from the champion `tb_merge_b`.
  - Only `src/bot.py` differs, by about 130 lines tagged `h_goldtie`.
  - draft.py, main.py and randomness.py are byte-identical to the champion's.
- Opponent: the champion, `tb_merge_b`.
- Maps: all 70, both sides (140 games). This is also the gate head-to-head (LOOP.md §4a).
- Commands, both on the free Slurm `test` partition through `tools/onslurm.sh` with cambc 4.0.0 / engine 2.0.0:
  - `python3.12 tools/eval.py h_goldtie tb_merge_b --maps all --jobs 16 --keep --tag b1-h_goldtie-all` (job 56768278);
  - a static-detection sweep, job 56768672: `cambc run-batch` with `--rounds 2` and stdout kept, 70 maps × both sides. It reads the slot-0 `GOLDTIE` init line from each replay's `team-a/b.stdout`. Script: `matches/b1-h_goldtie-static/static.sh`; output: `matches/b1-h_goldtie-static/goldtie.txt`.

## Results
```
SUMMARY h_goldtie vs tb_merge_b: 74W-66L (53%)  avg gems 628 vs 637  avg deaths 12.7 vs 12.2  botFaults(A) 0   [all 70 maps x 2, matches/b1-h_goldtie-all]
```
- **Gate (a): FAIL.** 74/140 is below the 82/140 needed. The 95% Wilson interval is 0.446 to 0.609. botFaults is 0.
- **Sprint subset (the 20 SPRINT maps in tools/eval.py, both sides): 18W-22L.** The dev PC recorded **21W-19L**, so the sprint record does **not** reproduce (see the reproduction section below).
  - Maps not at 1-1: 02famine 2-0 and 02guardians 2-0; 00lanes, 01big-world, 00corners and 01concentrated-wealth 0-2. All other sprint maps went 1-1.
- **The 5 tiebreak maps: 9W-1L.** This reproduces the dev-PC 9-1.
  - The other 65 maps: **65W-65L exactly.**

### Tiebreak maps (us = h_goldtie; gold = lifetime `earnedGold` summed over champions)
| Map | Side | Result | Gems us-them | Gold us vs them | Clears us/them | fuelExh us/them | Our carried gems at r2000 |
|---|---|---|---|---|---|---|---|
| 01boss-battle | A | W | 0-0 | **27,655 vs 1,715** | 114 / 15 | 402 / 277 | 2,596 |
| 01boss-battle | B | W | 0-0 | **29,929 vs 4,749** | 114 / 30 | 259 / 292 | 3,085 |
| 02guardians | A | W | 0-0 | **17,031 vs 723** | 97 / 14 | 2 / 1 | 2,132 |
| 02guardians | B | W | 0-0 | **14,124 vs 696** | 91 / 8 | 0 / 0 | 1,857 |
| 02the-pack | A | W | 0-0 | **15,491 vs 1,618** | 127 / 16 | 97 / **2,249** | 568 |
| 02the-pack | B | W | 0-0 | **20,267 vs 539** | 183 / 10 | 196 / 239 | 600 |
| 02gift-wrapping | A | W | **60-0** | 454 vs 0 | 2 / 0 | 18 / 0 | 0 |
| 02gift-wrapping | B | W | **60-0** | 441 vs 0 | 2 / 0 | 5 / 0 | 0 |
| 01yellow-brick-road | A | W | 21-2 | 484 vs 466 | 2 / 2 | **1,352** / 127 | 0 |
| 01yellow-brick-road | B | L | 0-15 | 0 vs 210 | 0 / 1 | 205 / **2,623** | 0 |

**Baseline.** In a `tb_merge_b` mirror both bots play identically, so each map is 1-1 (Team B wins the identical game). The champion's expected record on these 5 maps is therefore 5-5. h_goldtie's 9-1 is **+4 games**, which accounts exactly for 74 = 70 + 4.

### match_metrics (h_goldtie side, 140 games)
```
games 140  tributes 3507  mean tribute 25.1  small(<10) 411
  consumablesBought 1186 (8.5/game)   deaths_by_camp 134 (1.0/game)   deaths_by_champion 1646 (11.8/game)
  fuelExhausted 10219 (73.0/game)     gemsLost_to_camp 1053 (7.5/game) gemsLost_to_champion 11666 (83.3/game)
  wardPlacement 56102 (400.7/game)
```
- `fuelExhausted` in the same 140 games:
  - all maps: h_goldtie **10,219**, tb_merge_b **13,051**;
  - excluding the 5 tiebreak maps: 7,683 vs 7,243 (+6%, noise-level; the per-map counts are close on both sides, e.g. 00lanes 692/1,017 and 743/726, 02stalactites 444/364, 00vault 320/268).
- Most of tb_merge_b's surplus comes from its stuck loops on 02the-pack A (2,249) and 01yellow-brick-road B (2,623).

### analyze_match --summary (wins vs losses)
| metric | wins | losses |
|---|---|---|
| gem lead r250 / r500 / r1000 | +19 / +55 / +132 | −32 / −65 / −165 |
| first tribute us / them | 192 / 241 | 240 / 182 |
| kills us / them | 14.9 / 7.0 | 7.1 / 17.1 |
| gem loss us / them | 63 / 127 | 122 / 59 |
| gold us / them | 7,170 / 3,685 | 3,815 / 6,368 |
| fuelExh us | 74.9 | 70.8 |

## Analysis session

### Did the targeted mechanism change? Yes, exactly where intended
1. **`no_tribute` fires on exactly 01boss-battle, 02guardians and 02the-pack, on both sides, and nowhere else.**
   - The stdout sweep gave 6 of 140 `GOLDTIE no_tribute True` lines, with 1 altar each and 0 usable. The guard tiles were 30 (boss-battle), 2 (guardians) and 48 (the-pack).
   - The other 134 lines were `no_tribute False`, and on those 67 maps **every altar is usable**, so `pick_altar` is unchanged there.
   - Second witness: across the 140 eval games, Treasure emblems (bought only under `no_tribute`) appear only on those 3 maps, one per champion.
2. **The gold race is won by a landslide on all six `no_tribute` games.**
   - We earned 14k to 30k gold against tb_merge_b's 0.5k to 4.7k, and cleared 91 to 183 groups against its 8 to 30.
   - The guard exclusion holds: no monolith or wolf ring was opened, and tb_merge_b tributed 0 on all six.
3. **What tb_merge_b does in the same games** (its side of the stats JSON):
   - **01boss-battle B:** its gem carriers keep walking to the same central spot and die there. Our Vesper went 21/0, and 20 of the 21 deaths were at (22-24, 18-19), each with 9 to 34 gems. It lost 424 gems in total.
   - **02guardians A:** tb_merge_b died 17 times, losing 148 gems. Six of those deaths were in the central cluster (22-26, 19-23) from r1391 on.
   - **02the-pack A:** tb_merge_b logged **2,249 fuel exhaustions** and 16 clears. This is the do_tribute loop at the wolf ring that NOTES.md describes.
4. **02gift-wrapping: chip mode works, but only once.**
   - On both sides chip mode cleared 2 wrapped groups (r336-382), and the team tributed 60 gems at r393-409. tb_merge_b made 0 clears and earned 0 gold.
   - **After our own first tribute, `stall_done` switches gold play and chip mode off.** The team then made **0 clears in the remaining ~1,590 rounds** (every champion ended on 32 to 133 gold).
5. **01yellow-brick-road: the stall rule never fired.**
   - Both games had a tribute before r300: tb_merge_b's Heart of Ruin tributed 15 at r159 (B game), and we tributed at r257 (A game).
   - So the gold-play-gated respawn fix stayed off, and **both teams stayed frozen**: 0 to 2 clears per team per game, with 1,352 to 2,623 fuel exhaustions for the frozen side.
   - The A win (21-2) and B loss (0-15) are decided by the early pre-r300 skirmish: their HoR killed ours at r154 at (20,6), and tributed at r159.
6. **The stall rule fired in 14 of 140 games:**
   - the 6 `no_tribute` games;
   - 02gift-wrapping ×2;
   - 00contest ×2 (first tribute r1508/1514);
   - 00stampede ×2;
   - 01elk-arena ×2 (only r300-317).

   It changed the outcome only on 02gift-wrapping. 00contest stayed a mirror (Team A 200, Team B 600 in both games), and 01elk-arena stayed 1-1.

### Nothing regresses on the other maps, but they are reshuffled by fuel chaos
- **The 65 non-tiebreak maps went 65W-65L.** This is exactly the mirror baseline, so there is no net gain or loss.
  - 14 maps produced **identical** games to the mirror (same gems, gold, deaths and rounds): 00crater, 00elkring, 00fragment, 00interlock, 00oasis, 00pilgrimage, 00quarry, 00rows, 00the-line, 01corridors, 02arena and adgato-gemcombat1/3/4.
  - The other 51 maps diverged (51W-51L), with pair patterns WL 15, LW 14, WW 11 and LL 11. That is symmetric noise.
- **Mechanism of the divergence.**
  - Games are deterministic: seeds match across sides, and draft/main/randomness are identical to the champion's.
  - But tb_merge_b branches on `cambc.fuel_remaining()`:
    - `FUEL_BUILD_FLOOR`: static distance-field cache building (bot.py:537);
    - `FUEL_SCORE_FLOOR`: the target-scoring cut-off (bot.py:1064);
    - `FUEL_FIRST_TURN_MIN`: whether to act on turn 1 (bot.py:1809).
  - h_goldtie spends extra bytecode even where its logic is inactive:
    - `init_gold` in turn 1;
    - from r300 until the first tribute, the per-turn `global_submitted_gems` calls;
    - the `gold_play()` and `G.value <= 0` checks.
  - These shift leftover fuel, which flips later decisions and then whole games.
  - **So any change to bot.py reshuffles about 50 of 65 unrelated maps at random.** A real +4-game feature therefore cannot reach 82/140 on its own.

### Reproduction of the dev-PC numbers
- **These reproduce:**
  - the tiebreak-map record (9-1, and 6-0 on the three `no_tribute` maps);
  - the gold numbers to the unit for 5 of the 6 `no_tribute` games. 02the-pack is 15,491/1,618 and 20,267/539 (127/183 clears), and 02guardians is 17,031/723 and 14,124/696. 01boss-battle B is 29,929/4,749.
  - the "stall-prone" 4-4 on 00contest, 00the-line, 00rows and 01hooks.
- **01boss-battle A** gives 27,655 vs 1,715. That equals the dev-PC **release-check** game, not the dev-PC debug table (26,392 vs 1,918).
- **The sprint subset does not reproduce: 18-22 here against 21-19 on the dev PC.** The differing maps are:
  - 00lanes: 2-0 on the dev PC, 0-2 here;
  - 01big-world: 1-1 there, 0-2 here;
  - 01starvation: 2-0 there, 1-1 here;
  - 01islands: 0-2 there, 1-1 here.

  None of these has gold play active: no `no_tribute`, and the stall never fires. They are pure fuel-divergence maps.
- Determinism across machines holds for the champion gauntlet (STATUS.md). So the dev-PC sprint and tie3 runs most likely used a slightly different build of h_goldtie.
  - Possible causes are a pre-final edit, or a build-cache race on the dev PC, which lacked onslurm's per-job workspace snapshot.
  - Any bytecode change re-rolls those maps. **The committed code gives 18-22 on sprint.**

### Losses (66): why they were lost
- **Classification:**
  - 29 fight losses (enemy kills ≥ ours + 5);
  - 22 farm/tribute races;
  - 14 mirror-identical side-bias losses (h_goldtie played exactly like tb_merge_b, and Team B won);
  - 1 gold tiebreak.

  These come from an ad-hoc digest over the stats JSONs in `matches/b1-h_goldtie-all`: gem race at r250/500/1000/1500, first tributes, K/D, deaths before r500, gems lost, fuel and top killers for every loss.
- **Outside the stall games, h_goldtie's logic was inactive in every loss, so these are the champion's own mirror losses.**
  - They start early: gem deficit −32 at r250 and −65 at r500; first tribute 240 vs 182.
  - They are fight-driven: K/D 7.1 vs 17.1, and 122 vs 59 gems lost per game.
  - The enemy **Vendetta is the most frequent top killer, in about 25 of the 66 losses**: 00lanes 12 and 20 kills, 01starfish B 23, 02treasure-box B 25, 01starvation A 18, 00crater A 26.
  - Fuel exhaustion is not a loss factor (74.9 in wins vs 70.8 in losses). The high-fuel losses (00lanes about 700/game, 02stalactites A 444, 00vault B 320) are equally high for tb_merge_b in the same game.
- **00stampede B (0-0, lost on gold 8,986 vs 9,487, −5.3%).**
  - Nobody collected a single gem all game, and the stall rule was active from r300.
  - Kill gold decided it: their Vendetta went 16/3.
  - We bought **no Treasure emblem**, because Treasure is only bought under `no_tribute`, not when `stalled`. At +10% gold, a Treasure emblem was worth more than the 501-gold gap.
- **01yellow-brick-road B (0-15):** the movement freeze; see the mechanism section above.
- **Paired losses on 00lanes, 01concentrated-wealth, 00eight, 00reverse-spiral and adgato-gemcombat5:** fight losses (K/D 2/14 to 8/37) on both sides. They are fuel-divergence re-rolls of mirror games.
  - The mirror (Team B wins) would have given 1-1. h_goldtie's divergence happened to fall the losing way here, and the winning way on 11 other maps (WW).

### Surprising wins
- **00stampede A (160-0).**
  - The map's only gem source is camp group 10 at (56,23), worth 160 gems. Our Vesper (Bruiser Strength ×15) cleared it at **r1757** and tributed at r1812.
  - In the B game nobody cleared it, and the game went 0-0 to gold. tb_merge_b never cleared it in either game.
- **01boss-battle B (K/D 21/0):** gem-carrying enemies kept walking into our Vesper at one central spot (see the mechanism section).
- **02gift-wrapping ×2:** chip mode's two clears (60 gems) beat tb_merge_b's 0 clears.
- **02the-pack A: won despite an idle Marcella.**
  - Marcella earned only 447 gold (6,710 on the B side) while taking 14,973 champion damage, almost all from the enemy Vesper (13,600).
  - So a third of a 3-champion team was lost to a harassment loop. Eval replays carry no stdout, so the cause is unconfirmed.

## Verdict
**Kept, as a component only. It is not promotable on its own and fails gate (a) with 74/140.**
- The targeted mechanism works exactly as designed and reproduces:
  - static detection is exact (3 maps, both sides);
  - the gold race is won by about 10× on the `no_tribute` maps;
  - chip mode wins 02gift-wrapping;
  - the result is 9-1 on the 5 tiebreak maps, a deterministic +4 games per 140 over the mirror baseline.
- There is no measurable regression elsewhere (65-65).
- But +4 games is far below the +12 the gate needs. On every other map, the fuel-driven re-roll of about 50 maps dominates the measurement.
- Use it in the Q24 combined candidate. Its pieces are confined to `no_tribute` and `stalled` paths, so they are compatible with the other batch-1 changes.

## New hypotheses generated
- **Universal idle chip mode.** Don't switch chip mode off at the first tribute. Allow 30 hit-and-run cycles whenever a healthy champion has had no target for 12 turns.
  - Evidence: 02gift-wrapping A and B made 0 clears from r382 to r2000, after our own tribute at r393 ended `stalled`.
  - Why: more clears, gold and gems on wrapped or strong-camp maps. Against a ladder opponent who keeps chipping, 60 gems would lose.
- **Treasure emblem when stalled late.** Buy Treasure when `stalled` persists past about r800 (0-0 heading to the gold tiebreak), not only under `no_tribute`.
  - Evidence: 00stampede B lost 0-0 on gold 8,986 vs 9,487 (−5.3%), with no gems on the map and no Treasure bought.
  - Why: +10% gold exceeds the margin. The risk is weaker fight stats, which matter on kill-gold maps.
- **Q21, the universal respawn-rule fix, is confirmed and should be raised.** The gold-play-gated fix never fired on 01yellow-brick-road, because tributes at r159 and r257 ended the stall window. Both teams froze for about 1,700 rounds (0 to 2 clears, up to 2,623 fuel exhaustions). Making the fix unconditional unfreezes the map for us.
- **Sole-gem-herd assault when stalled** (Q3-adjacent).
  - Evidence: on 00stampede, the only gem source (group 10 at (56,23), 160 gems) was cleared once at r1757 (A game) and never in the B game.
  - Why: when both teams are at 0 tributed, a deliberate team assault on the only gem herd decides the game outright, instead of the gold tiebreak.
- **Fuel-independent decisions** (extends Q23).
  - tb_merge_b branches on `fuel_remaining()` (static-field cache, scoring cut-off, turn-1 act). So any code change re-rolls about 50 of 65 unrelated maps; here 51 diverged and went 51-51.
  - Replace these with fixed work quotas, or precompute static fields in the draft (250M fuel).
  - Why: play becomes stable, small real gains (like this +4) become measurable and stackable, and dev-PC and cluster numbers stop drifting.
- **Q22 evidence:** on 01boss-battle and 02guardians our champions end with 1,857 to 3,085 carried gems. If a guard ever dies, a single tribute run wins outright (the threshold is 1,000).
