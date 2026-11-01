# Experiment: h_antistun, anti-stun channel rule (2026-11-01, cluster)

Batch 1, STRATEGIES Q15 / T19. The implement and test stages ran on the dev PC: sprint vs tb_merge_b 20W-20L, vs imit_test 31-9 (base 33-7), vs lad_vcst 25-8 (partial). Their raw games were lost, and the mandatory analysis session never ran. This report covers the full 140-game evaluation on the cluster and that analysis session. The analysis uses the bot's own CHLOG stdout lines, read from the replays, plus a logging-only control bot.

## Hypothesis
- **What:** a stun cancels tribute, recall and teleport channels. So **do not start one while a visible enemy could stun us before it completes.**
  - A threat is an enemy whose stun is ready within the channel's tick count (an unknown cooldown counts as ready), and who is within reach + `ANTI_APPROACH` (1).
  - The stun can be a CC, an area stun, a stunning dash landing, or Marcella's enhanced attack.
  - Reach is the cast range, plus the landing radius, plus 1 if the cast allows walking.
  - **Instead:** hold, hit the stunner if it is in range, and retry.
  - A deferral budget (+1 per block, decaying ×0.95 per turn, cap 6) forces the channel after about 7 consecutive blocked turns.
  - Our Marcella is stun-immune and is exempt.
- **Source:** ladder stats. Team "test" drafts many stuns (Cassi, Stellar, Ren, Ryth, Prism, Tavi), and stuns cancel tribute and recall (Q15, Q14).

## Setup
- **Candidate:** `bots/h_antistun`, code unchanged, forked from the champion `tb_merge_b`.
  - Only `src/bot.py` differs (211 lines added, 4 changed, tagged `h_antistun`): `stun_reach`, `stun_threat`, `stun_blocked` and `hold_vs_stunner`, plus the CHLOG logging (`chan_check` / `chan_start`).
  - Hooks:
    - `do_tribute`, before `submit_gems`;
    - three recall sites (`cross_toward`, the no-goal branch, the idle-recall branch in `play_turn`);
    - `recall_safe`, which now also requires no ready stunner in reach (no budget);
    - the teleport-crystal use in `cross_toward`.
  - `NOTES.md` is a stale copy of tb_merge_b's. draft.py, main.py and randomness.py are byte-identical to the champion's.
- **New control bot `bots/dbg_antistun_off`** (made with `tools/newbot.py h_antistun dbg_antistun_off`):
  - the same file with `ANTISTUN = False`;
  - it makes tb_merge_b's decisions, while keeping the CHLOG bookkeeping and its fuel cost;
  - it is the "before" side of the mechanism measurement. It is not a candidate and can be deleted.
- **Stdout:** `tools/eval.py` forces `--log-limit 0`. `matches/b1-h_antistun-tools/eval_logs.py` runs eval.py unchanged, minus that flag.
  - The parsers used below sit beside it: `chlog.py`, `antcost.py`, `sides.py` and `flips.py`.
  - **Stdout in `.repl26a` is NUL-padded**, about 15 bytes per round. The text lines are intact and in order, so split on `\x00`.
- **Runs.** All ran on the free Slurm `test` partition via `tools/onslurm.sh -c 24 -m 16G`, with `--jobs 16`, cambc 4.0.0 / engine 2.0.0:
  | Job | Command | Tag |
  |---|---|---|
  | 56770550 (gate) | `eval.py h_antistun tb_merge_b --maps all --keep` | `b1-h_antistun-all` |
  | 56770955 | the same pairing with stdout | `b1-h_antistun-logs` |
  | 56770956 | `dbg_antistun_off tb_merge_b --maps all`, stdout | `b1-h_antistun-ctrl-logs` |
  | 56772772 | `h_antistun imit_test --maps sprint`, stdout | `b1-h_antistun-imit-logs` |
  | 56772773 | `dbg_antistun_off imit_test --maps sprint`, stdout | `b1-h_antistun-imit-ctrl-logs` |
- **Baseline for "mirror":** the existing `matches/b1-tb_merge_b-mirror-all`, tb_merge_b vs itself on 70 maps. Each map is one game, so the champion's expected record is 1-1 per map and 70-70 overall.

## Results
```
SUMMARY h_antistun vs tb_merge_b: 79W-61L (56%)  avg gems 669 vs 608  avg deaths 12.4 vs 13.1  botFaults(A) 0          [gate, all 70 maps x 2]
SUMMARY h_antistun vs tb_merge_b: 79W-61L (56%)  avg gems 669 vs 608  avg deaths 12.4 vs 13.1  botFaults(A) 0          [same, stdout kept]
SUMMARY dbg_antistun_off vs tb_merge_b: 70W-70L (50%)  avg gems 650 vs 623  avg deaths 12.4 vs 13.0  botFaults(A) 0    [logging-only control]
SUMMARY h_antistun vs imit_test: 32W-8L (80%)  avg gems 820 vs 465  avg deaths 4.9 vs 31.3  botFaults(A) 0              [sprint]
SUMMARY dbg_antistun_off vs imit_test: 35W-5L (88%)  avg gems 853 vs 434  avg deaths 4.8 vs 31.0  botFaults(A) 0        [sprint]
```
- **Gate (a): FAIL.**
  - 79/140 is below the 82/140 needed.
  - The 95% Wilson interval is 0.481 to 0.644.
  - botFaults is 0.
- **Sprint subset (the 20 SPRINT maps, both sides): 20W-20L.** This **reproduces the dev-PC sprint record exactly.** The quick subset is 13W-11L.
- **imit_test:** 32-8 here, against **31-9 on the dev PC**, so it does not reproduce exactly. The dev-PC base was 33-7. The cluster's tb_merge_b vs imit_test (`matches/g-tb_merge_b-vs-imit_test`) is 34-6, and the control is 35-5. The direction is the same: the rule is slightly negative against the stun-heavy comp.
- **Determinism:** the stdout run equals the gate run in **140/140 games** (outcome, gems, rounds and deaths per team). The log limit does not change games.
- **Per-map pattern vs tb_merge_b:**
  - 2-0 on 18 maps: 00breadcrumbs, 00collision, 00elkring, 00fragment, 00gem-fields, 00great-wall, 00oasis, 00ribs, 00stampede, 00the-line, 01gold-rush, 01hooks, 02crossing, 02famine, 02fields, 02tangle, 02the-pack, 02treasure-box;
  - 0-2 on 9 maps: 00anvil, 00dunes, 00eight, 00expanse, 00packs, 01boss-battle, 01concentrated-wealth, 01shortcut, 01starvation;
  - 1-1 on 43 maps.
  - By side: A 39/70, B 40/70.
- **match_metrics (h_antistun side, 140 games):**
  ```
  games 140  tributes 3766  mean tribute 24.9  small(<10) 407
  deaths_by_camp 1.2/game  deaths_by_champion 11.2/game  fuelExhausted 84.8/game  gemsLost_to_champion 90.9/game  gemsLost_to_camp 8.1/game  wards 400.3/game
  ```
  - The tb_merge_b mirror gives 11.2 champion deaths per game, 87.4 fuelExhausted, 79.8 gems lost to champions and a mean tribute of 25.1.
  - In the same games, tb_merge_b's fuelExhausted is 86.6 per game, so gate (c) on fuel would be fine.
- **analyze_match --summary, wins vs losses:**

  | Metric | Wins | Losses |
  |---|---|---|
  | Kills (us/them) | 15.3/9.0 | 7.7/14.0 |
  | Gems lost (us/them) | 79/129 | 125/69 |
  | Gem lead at r250 | +10 | -21 |
  | Gem lead at r500 | +41 | -57 |
  | Gem lead at r1000 | +90 | -86 |
  | First tribute | r169 | r194 |
  | Mean tribute | 25.8 | 23.0 |

## Analysis session

### 1. The noise floor: a logging-only change flips 44 of 140 results
- `dbg_antistun_off` makes **exactly tb_merge_b's decisions**:
  - the RNG is position-seeded;
  - the `cands` guard added to the crystal branch is a no-op;
  - `ANTISTUN = False` makes `stun_blocked` return False.
- Only the fuel spent by CHLOG differs. Yet against the mirror:
  - **only 40/140 games are identical;**
  - **44 results flip (22 each way)**, netting exactly 70-70.
- **Cause:** tb_merge_b's decisions read `cambc.fuel_remaining()`:
  - `FUEL_SCORE_FLOOR` cuts off target scoring;
  - `FUEL_BUILD_FLOOR` paces the static-field builds;
  - `FUEL_FIRST_TURN_MIN` decides whether to act on turn 1.

  So any extra work changes choices, and the game diverges chaotically from there.
- **h_antistun's +9 over 70, decomposed:**
  - **Against the instrumented control** (same logic, same logging), 63 games are identical, meaning the rule had no effect on them at all.
  - Of the 77 games that changed:
    - **64 had at least one deferral:** h_antistun 36W against the control's 30W (flips +13 / -7; two-sided sign test p ≈ 0.26);
    - **13 had none:** 7W against 4W (+4 / -1). These diverged from the extra `stun_threat` fuel alone.
  - **Against the mirror:** of h_antistun's 18 lost flips, **16 also happen in the control**, so they come from instrumentation and not the rule. Of its 27 gained flips, 16 also happen in the control.
  - In the 75 games where h_antistun never deferred anything, it went 43-32 (57%). That is the same rate as overall.
- **Conclusion:** under this noise a neutral change scores about 70 ± 6.6 wins on 140 games (1 SD, from 44 coin-flip results). **79 is +1.4 SD, and about a third of the +9 comes from games where the rule never fired.**

### 2. Did the targeted mechanism change? Yes, as designed, but it is rare
Channel outcomes from CHLOG (CHS = start, with the threat tag; CHX = outcome at our next turn):

**vs tb_merge_b (140 games)**

| | Control (before) | h_antistun (after) |
|---|---|---|
| Tribute starts | 3,679 | 3,786 |
| Started under threat (ready stunner within reach + 1) | 43 (0.3/game) | 8 |
| Stun-cut, of those | 10 (23%) | 0 |
| Recall starts | 6,029 | 6,204 |
| Started under threat | 96 (0.7/game) | 0 |
| Stun-cut, of those | 15 (16%) | n/a |
| Stun-cut rate of non-threatened starts | 1.0% tribute / 1.1% recall | 1.0% / 1.0% |
| **All stun-cut tributes + recalls** | **127 (0.91/game)** | **99 (0.71/game)** |
| Teleport starts (threatened) | 144 (1) | 145 (1) |

**vs imit_test (40 sprint games)**

| | Control (before) | h_antistun (after) |
|---|---|---|
| Tributes started under threat | 21 (0.5/game) | 2 |
| Stun-cut, of those | 9 (43%) | 1 |
| Recalls started under threat | 29 | 0 |
| Stun-cut, of those | 4 | n/a |
| **All stun-cut tributes + recalls** | **32** | **20** |
| Stun-cut tributes from non-threatened starts | 3 | **9** (displacement, below) |

- **Threat sources:**
  - vs tb_merge_b, Ryth (117 threatened starts) and Heart of Ruin (23), with Marcella about 0;
  - vs imit_test, Ryth (33), Ren (14) and Cassi (4);
  - Tavi and Prism never showed up as threats.
- **Where the threat comes from (control, vs tb_merge_b):**

  | Channel | Stunner within real reach (d ≤ 5) | Stunner at the +1 approach margin (d = 6) |
  |---|---|---|
  | Tribute | stun-cut 10/35 (29%) | stun-cut 0/8 |
  | Recall | stun-cut 2/10 | stun-cut 13/86 (15%) |

  The 5-turn recall gives Ryth time to walk in.
- **Deferral blocks (ANT), vs tb_merge_b, mostly "Ryth at Chebyshev 6, cooldown 0":**

  | Channel | Episodes | Blocked turns | Mean turns/episode |
  |---|---|---|---|
  | Tribute | 69 | 185 | 2.7 |
  | Recall | 109 | 217 | 2.0 |
  | Teleport | 6 | 18 | 3.0 |

  The champions blocked were Vesper (139 lines), Vendetta (144), Ryth (68) and Heart of Ruin (69). Marcella had 0, which confirms the slot mapping and the immunity exemption.
- **Scale:**
  - The rule removes about **0.2 stun cancellations per game** vs tb_merge_b and 0.3 vs imit_test.
  - **Most stun-cuts come from channels started with no ready stunner visible in reach.** These are stunners out of vision, or ones that approach or dash in later, and a vision-based start rule cannot see them.
    - In the control, 102 of 127 (80%) vs tb_merge_b and 19 of 32 (59%) vs imit_test.
    - In h_antistun, 99 of 99 and 19 of 20.
  - **Displacement:** 8 of 99 stun-cuts (vs tb_merge_b) and 2 of 20 (vs imit_test) began within 10 rounds after a deferral of the same channel by the same champion, usually the very next round. The wait did not save them. Examples:
    - 00gemfight A: an 82-gem tribute at r412, the round after an ANT, cut at r416;
    - 01starfish A: an 87-gem tribute at r1107, cut at r1110.

### 3. Did waiting cost tempo?
- **vs tb_merge_b: no measurable cost.**
  - Deferrals are short. After a block, the channel started within 40 rounds in 49/69 tribute episodes (median delay 3 rounds) and 96/109 recall episodes (median 2).
  - Only 7 champions died while deferred (6 recall, 1 tribute) across 140 games, losing 59 gems in total.
  - h_antistun against the control, per game:

    | Metric | h_antistun | Control |
    |---|---|---|
    | Tributes | 26.9 | 26.0 |
    | Gems at r300 | 66.5 | 67.3 |
    | Gems at r500 | 136.1 | 137.8 |
    | Median first tribute | r130 | r130.5 |
    | Mean tribute | 24.9 | 25.0 |
- **vs imit_test: a small negative drift** (40 games, inside noise but in the wrong direction):

  | Metric per game | h_antistun | Control |
  |---|---|---|
  | Tributes | 33.8 | 36.1 |
  | Gems submitted | 820 | 853 |
  | Gems lost to champions | 32.8 | 27.9 |

  - **Flips against the control: 0 gained, 3 lost.** The lost ones are 00quadrants A (no deferral at all, so noise), 00quadrants B and 02famine B; 18 of the 40 games are identical.

### 4. Why were the remaining losses lost?
- **The losses are the champion's losses: fights and the early gem race, not stuns.**
  - In the 61 losses: kills 7.7 vs 14.0, gems lost 125 vs 69, behind by 21 gems at r250 and by 57 at r500.
  - **Deaths at or before r500:** 4.0 per game in losses, 3.1 in wins.
  - **Deaths per loss, by killer:** Vendetta 4.3, Vesper 4.2, Marcella 3.1, Ryth 1.2, camps 1.2, HoR 1.1. In wins: 3.2, 2.5, 1.8, 0.6, 1.2, 0.8.
  - **Most-killed of ours:** our Marcella, 4.6 deaths per loss (3.0 per win).
- **Flips explained by noise:** all 9 maps lost on both sides, and 16 of the 18 games lost relative to the mirror, are reproduced by the logging-only control. Examples:
  - **00anvil A (458-742).**
    - A 3-pick map, the rule never fired, and the game is **identical to the control's**.
    - Our first tribute came at r348 against their r35; we were behind from r100.
  - **00vault A (343-1061, mirror 1061-0).**
    - No deferral; identical to the control.
    - We banked 114-gem bags (12-turn channels): 3 tributes against their 10.
    - We collected nothing after r500 and died 15 times to their 9.
  - **00eight B (146-1003, also lost by the control).**
    - An early-fight snowball: their Vesper went 15/1 and their Vendetta 16/1, with 11-13 Strength shards each.
    - We died 44 times, 43 of them to champions.
  - **01starvation A (138-710).** 34 deaths to 9; Vendetta killed us 13 times. Our first item came at r324 against r165.
  - **01concentrated-wealth A (552-945).** Kills 1 vs 16, first item r313 vs r153. This is the known weak map (HANDOFF risk), and the rule never fired.
  - **00lanes B (517-1009).** 27 deaths to 8 (Vendetta 16). It is the fuel hotspot: fuelExhausted 659 against 714.
- **Gem-race shape in losses:** we are behind from r100-r500 in most of them (the "ahead-from" column). Tribute sizes are normal (23.0).
- **The only two losses attributable to the rule** (the control kept the mirror result): 01big-world B (941-976) and 01elk-arena B (402-606).
  - Each had a single recall deferral (Ryth at d = 6).
  - In 01elk-arena B, the control started those recalls under the same threat and both completed. So the deferral changed the trajectory; it did not avoid a stun.

### 5. Surprising wins
- **00ribs B (957-299; mirror 329-1013; control 157-1014).**
  - The game diverged at r483, when h_antistun deferred a 28-gem tribute for 4 turns (Ryth at d = 5).
  - **In the control, the same tribute completed with no stun.** The win is a different trajectory, not a saved channel.
- **01islands A (1004-958; mirror 830-949).** It diverged at r128 (a crystal teleport one round later), **before the first deferral at r160.** That is fuel perturbation from `stun_blocked` calls that did not block.
- **00stampede A, 02the-pack B and 01yellow-brick-road B.** These are 0-0 games decided by the gold tiebreak. They are trajectory noise and say nothing about stuns.

### 6. Other observations
- **Inherited caught exceptions, which lose the turn:**
  - `bot error: No visible entity of this kind occupies the tile.` and `bot error: Unit is not in vision.` appear 11 times in h_antistun's 140 games and 8 times in the control's (00lanes A 4×, 00vault A, 01yellow-brick-road A, 02stalactites B, 02the-pack B).
  - The control also had `Invalid metadata, alignment, overlap or argument.` once, on 00lanes B.
  - These come from tb_merge_b, and botFaults stays 0 because main.py catches them.
- **Recalls are a death trap (control = the champion's behaviour, vs tb_merge_b):**
  - 328 recall channels ended in death (2.3/game) — 19% of all 1,737 deaths. They lost 2,760 gems, 21% of all 13,019 gems lost. 286 of these deaths were to champions.
  - 1,211 recalls (20%) were cut by damage, and those champions carried 10,511 gems between them.
  - One third of recalls are started while carrying gems.
- **Big bags draw the stuns:**
  - Stun-cut tributes had a mean bag of 60 gems (median 35), against 25 (median 21) for all tributes.
  - Bags of 40 or more are 12.6% of tributes but 43.5% of stun-cuts. Against imit_test: 9.6% vs 50%.

## Verdict
**Rejected.**
- **Gate (a) fails:** 79/140, Wilson lower bound 48.1%. The sprint subset is exactly 50% (20-20) and reproduces the dev PC.
- **The mechanism works as designed but is too rare to matter.**
  - Threatened channel starts fell from 140 to 9 per 140 games, and stun cancellations from 127 to 99 (vs tb_merge_b) and from 32 to 20 (vs imit_test). That is at most about 0.2-0.3 channels per game.
  - Most stun-cuts (80% vs tb_merge_b and 59% vs imit_test, in the champion's own play) start with no ready stunner in sight, which this rule cannot address.
  - The waiting costs little tempo against tb_merge_b, but it was 3 games worse than the control against the stun-heavy imit_test comp. That comp is the one the rule targets.
- **The +9 against tb_merge_b is inside the measured noise floor.**
  - A logging-only control flipped 44 of 140 results and scored 70-70.
  - 16 of the 18 lost flips and 16 of the 27 gained flips are reproduced by that control.
  - The rule-fired games split 13-7 against the control (p ≈ 0.26).
- **Do not re-run unchanged.** Q15's premise holds per event: threatened starts are cut 23-43% of the time, against 1% for others. But its expected value is about 1 game in 140.

## New hypotheses generated
1. **Noise-calibrated evaluation: placebo controls and perturbation replicates** (methodology).
   - **Evidence:** a logging-only change flipped 44/140 results (22/22) and changed 100/140 games, because decisions read `fuel_remaining()`.
     - Over 140 games, a neutral change has SD ≈ ±6.6 wins.
     - Over 40 sprint games, ±3.2, so the "≥ 55% sprint" screen passes about 30% of neutral changes.
   - **Proposal:**
     - **(a)** Judge instrumented or heavier candidates against an equal-fuel placebo of the champion.
     - **(b)** Make K placebo variants of both bots, e.g. a seeded no-op fuel burn on turn 1. Each variant gives an independent game per map, so a gate can use 280-420 games on the same 70 maps without re-running identical games.
2. **Recall is a death trap: no recall in contact** (Q-new).
   - **Evidence:** 19% of our deaths and 21% of gems lost happen inside a recall channel (2.3/game, 87% killed by champions), and 20% of recalls are cut by damage.
   - **Proposal:**
     - forbid starting a recall when an enemy champion is within its attack range + 2 moves, or after champion damage in the last 2 turns;
     - instead, walk toward spawn or allies, and recall once disengaged.
3. **Smaller bags when stunners are around.**
   - **Evidence:** bags of 40 or more are 12.6% of tributes but 43.5% of stun-cut tributes (50% vs imit_test). Long channels (ceil(g/10) turns) are the exposure; 00vault shows 114-gem, 12-turn tributes.
   - **Proposal:** when the enemy roster has stunners (Ryth, HoR, Cassi, Ren, Tavi, Prism) and one was seen within about 12 tiles in the last ~20 rounds, lower sf_bank's banking threshold so channels stay at 3 turns or fewer.
4. **(Merge-only, low value) A narrower anti-stun.**
   - Tributes: only when the stunner is within its true reach. In the control, d = 6 tributes were cut 0/8 while d ≤ 5 tributes were cut 10/35.
   - Recalls: keep the +1 margin (13/86 cut at d = 6).
   - Worth at most about 1 game per 140, so only fold it into another change.
5. **(Robustness) Fix tb_merge_b's caught exceptions** ("No visible entity of this kind occupies the tile", "Unit is not in vision"). Each one loses a turn, about 0.08 per game. Bundle the fix with another change.
