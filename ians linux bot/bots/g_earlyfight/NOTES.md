# h_earlyfight: opening-phase group fight rule (STRATEGIES Q12)

Base: `bots/tb_merge_b` (copied with `tools/newbot.py`). Only `src/bot.py` changed; the draft is unchanged.
Current code = **v2** (snapshot in `matches/h_earlyfight-v2-src/`; v1 in `matches/h_earlyfight-v1-src/`).
Sibling variants (same code, one constant changed; all live in my namespace):
- `bots/h_earlyfight_all`: v2 with `EARLY_ROUNDS = 2000` (the group rule all game, "v3").
- `bots/h_earlyfight_diag`: v2 with `DIAG = True` (per-turn log of pos/hp/allies/enemies/balance for
  r < 320). For diagnostics only; never evaluate it (prints cost fuel).

## Evidence that motivated it
- `matches/final-mergeb-all` (tb_merge_b vs sf_bank, 70 maps x 2): the clearest early-fight loss is
  00dunes B (196-1036): 7 of our champion deaths before r300 against their 1, their Vendetta 9-0.
- Our early deaths alone do not predict losses vs sf_bank (wins 1.26 early deaths/game, losses 1.13).
  The *enemy's* early deaths do (wins 1.82, losses 0.60). Against imit_test it is the same picture:
  their early deaths 3.74/game in our wins vs 1.00 in our losses. So "winning the early fights" means
  converting fights, not just avoiding them.
- Diag games (`matches/h_earlyfight-diag/`: 00dunes B, 01starfish B, 00lost-world B, 02stalactites A
  vs sf_bank). Every early champion death had the same shape:
  - A lone, mostly **non-dash melee** (Ryth, Marcella, HoR) **stands next to an enemy melee and trades
    for 5-11 turns**, while **2-5 enemies are within 6** and 0-1 allies are within 8.
    - The cause is `adjacent_melee` stand-and-trade. It only lets a champion with a dash, or one
      next to spawn, walk away.
  - Or a champion **chases a low-hp target into 3-4 enemies**.
    - The kill-time ratio is small because the target is nearly dead.
    - The numbers check `len(near) > n_allies + 1` only applies after the engage decision.
  - Or 3-4 of our champions are 2-6 tiles from a 2v4 / 3v4 fight, but **nobody commits**.
    - Each ally's own ratio `my_ttk / their_ttk` is about 1.0, above the 0.85 limit.
    - `their_ttk` assumes all enemy damage lands on that one ally.
    - Allies only count within 4 tiles, at 0.7 strength.

## What changed (only while `round < EARLY_ROUNDS` = 300)
### The group balance score
In `handle_enemies`, `group_balance()` scores the local fight as `(sum hp x sum dps)` ours divided by theirs.
- **Our side:** me plus allies that are not recalling or teleporting.
- **Their side:** enemies in the engage radius (6), with dps x CHAN_THREAT.
- **dps** = strength + 0.15 focus, the same `enemy_dps` estimate on both sides.

Two ratios are computed:
- **`gb`**: counts allies within `GROUP_R` (7).
- **`gb_near`**: counts allies within `GROUP_ADV_R` (4).

### Behaviour by ratio
- **Advantage** (`gb_near >= GROUP_ADV` 1.4):
  - +`GROUP_ENGAGE_BONUS` (0.4) to the engage limit, for targets within attack range + `GROUP_BONUS_D` (2);
  - `clearly_losing` is forced False;
  - always stand and trade with an adjacent melee.
  - Every nearby ally sees roughly the same picture, so the group commits together.
- **Disadvantage** (`gb <= GROUP_DISADV` 0.75):
  - no new engagement unless the target dies to the next hit;
  - `clearly_losing` is forced True;
  - an adjacent melee is only traded with if it dies in 2 hits.
  - Otherwise, when an enemy is within `GROUP_REGROUP_D` (4) or threatens us, step away with
    `retreat(..., rally)`. Its last tie-break is the distance to the nearest visible ally, not to our
    spawn (spawn if no ally is visible).
  - Then `hit_while_leaving()` still attacks the weakest enemy in reach (a melee can walk and hit).
- **In between:** unchanged tb_merge_b behaviour. From round 300 on, the bot is tb_merge_b.

### v1 -> v2 (why v2 exists)
v1 scored **18W-22L (45%)** on the sprint against tb_merge_b. A diag replay of its worst game,
00gemfight A (140-1012), showed three faults:
- **"Advantage" counted allies 7 tiles away that never joined.** Our Marcella dived alone at (13,10)
  into Vendetta + Vesper + Marcella.
- **The engage bonus applied to far targets**, so champions chased into the enemy half.
- **The "regroup" step tied on danger and stood still without attacking.** That game had 0 kills.

v2 changed three things:
- advantage counts only allies within 4;
- the engage bonus applies only to targets within range + 2;
- `hit_while_leaving` was added.

## Results (all games kept, `--keep`)
### Sprint against the champion
```
v1  SUMMARY h_earlyfight vs tb_merge_b: 18W-22L (45%)  avg gems 654 vs 607  avg deaths 11.1 vs 13.4  botFaults(A) 0   matches/h_earlyfight-sprint
v2  SUMMARY h_earlyfight vs tb_merge_b: 22W-18L (55%)  avg gems 655 vs 603  avg deaths 12.2 vs 12.5  botFaults(A) 0   matches/h_earlyfight-v2-sprint
all SUMMARY h_earlyfight_all vs tb_merge_b: 23W-17L (58%)  avg gems 680 vs 617  avg deaths 10.3 vs 12.7  botFaults(A) 0   matches/h_earlyfight-all-sprint
ref SUMMARY tb_merge_b vs tb_merge_b: 5W-15L (25%)  [--one-side self-play: team B wins 15/20 sprint maps]       matches/h_earlyfight-selfplay-base
```

### Against imitations and sf_bank
```
v2  SUMMARY h_earlyfight vs imit_test: 32W-8L (80%)  avg gems 791 vs 462  avg deaths 5.4 vs 29.6  botFaults(A) 0   matches/h_earlyfight-imit
    (champion on the same 40 games: 34W-6L, 85%, matches/mergeb-vs-imit_test)
v2  SUMMARY h_earlyfight vs sf_bank: 13W-3L (81%)  [8 early-death maps x 2]                                     matches/h_earlyfight-bank-early
    (champion on the same 16 games, from final-mergeb-all: 14W-2L)
```
The all-game variant against imit_test and sf_bank is listed at the end.

## Analysis
### Self-play is chaotic; use the round-300 state
In `--one-side` self-play, team B wins 15/20 sprint maps. So a 40-game sprint against tb_merge_b
measures mostly which side bias we flip.
- Flips against the self-play baseline:
  - v1: 6 for us, 8 against;
  - v2: 9 for, 7 against;
  - all-game: 13 for, 10 against.
- The state at round 300 is more sensitive. It predicts the result: v2 wins 15/19 games when ahead at
  r300 and 7/21 when behind.

### Did the targeted mechanism change? Yes, modestly
Round-300 differences against the self-play baseline (as team A):
| Metric at r300 | v2 delta |
|---|---|
| tributed gems | +19 |
| gold | +150 |
| net early kills | +0.55 |

- As team B, v2 gains +7 tributed gems but loses gold.
- Against sf_bank on the early-death maps, the gem lead at r500 went from -96 (champion) to +20.
  - 00dunes B: our early deaths fell from 7 to 1, but we still lost 239-1026 after r300.
  - 00the-line B flipped to a win (630-0, against 55-440).
  - 02stalactites: r500 lead +605/+483, against the champion's -416/+154.
- Against imit_test the opening became **safer but less lethal**: our early deaths 0.75 vs 0.95, theirs
  2.77 vs 3.33. The result was neutral (32 vs 34 wins).

### Where it hurts
"Disadvantage" also blocks fights the kill-time model would have won.
- **00eight A against sf_bank** flipped to a loss, 43-520 with 66 deaths. The baseline drew first
  blood at r43 and r47. v2's first kill came at r130, and the enemy snowballed.
- **00lost-world B** also flipped to a loss.

### The bigger lever is mid-game
The all-game variant turned 01concentrated-wealth into wins on both sides: 836-482 and 942-531,
10-1 kills each. That map is lost on both sides by the champion, by v1, by v2, and by
tb_merge_b against sf_bank. Its fights happen at r500+.

## Verdict and next hypotheses
See the eval summary returned to the orchestrator (results for the all-game variant are appended below).
