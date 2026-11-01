# Experiment: h_antifocus, counter the focus-caster comp "Us V Them" (V3L-1) (2026-11-01, cluster)

**Verdict in one line: kept as a combo component, not promotable alone.**
- **The mechanism is confirmed.**
  - Against `imit_uvt2`, a new imitation that reproduces the ladder failure, the score rose from **76/140 to 105/140**. Paired on the same map-sides, 37 games were gained and 8 lost.
  - Our deaths fell from 15.7 to 9.2 per game. Deaths within 2 tiles of a bush fell from 8.4 to 3.4 per game.
- **Ladder hedge:** **104/140** against tb_merge_b, where c2 scores 98.
- **Gate head-to-head:** **74/140** against c2_respawn, with 0 bot faults. That **fails the ≥ 82 gate**.
- **Known cost:** fuelExhausted events roughly double in every opponent set.

## Hypothesis
- **What:**
  - Ladder team "Us V Them" (~1,539) beats us with Power-Focus casters that fight **from bushes**.
  - c2's threat model can't see this threat:
    - it scores an enemy as `strength + 0.15 x focus`, counted only within `attack_range + 1`, so a ready range-4 nuke is invisible to it;
    - a caster standing in a bush can't be seen at all.
  - Fix: a burst-aware threat model read from the enemy's own ability records and cooldowns, plus detection of damage from hidden attackers, and wards placed into bushes.
- **Source:** `results/ladder-games.jsonl`, 15 games against Us V Them with full stats in `matches/ladder/summary/`:
  - v3 went 3-7, with 31.0 deaths per game (29.2 to champions);
  - v4 went 1-4, with 23.8 deaths per game.
  - Also `results/experiments/2026-11-01-v3-ladder-study.md` (V3L-1).

## Ladder study (15 games; scripts in the scratchpad `uvt2/`: `study.py`, `cohesion.py`, `trace.py`)
- **Record by team size.** 3-pick: 1W-4L at **41.4 deaths per game**. 4-pick: 1W-2L at 26.0. 5-pick: 2W-5L at 20.6.
  - In 3-pick they field 4 bodies (Ren, Stellar, Cassi & Issac) against our 3.
- **Killers of our 429 deaths:** Stellar 132, Ren 105, Cassi 83, Issac 42, Ryth 28, Varg 20, camps 19.
- **Enemies involved per death (killer plus assists):**

  | Enemies involved | Deaths |
  |---|---|
  | 1 | 61 |
  | 2 | 119 |
  | 3 | 114 |
  | 4 | 89 |
  | 5 | 34 |
  | 6 | 12 |
- **How burst lines up over the game.**
  - Before r300, our deaths are team focus fire with small spells: the killer's single spell has a median of 140 damage.
  - After r800, the median killer spell is 684 damage. 59 of 176 late deaths come from a killer whose one spell is ≥ 1,000, i.e. it one-shots our base HP.
  - Damage taken in the death round itself is ≥ 600 in only 45 of 429 deaths. Most deaths take 3-8 rounds, often while the champion is already hurt by camps.
- **Item builds.** Every game shows the same buyItem order:
  - Ren: Bruiser Health ×5, then Durability Health ×5, then Power Focus forever (up to 126 shards).
  - Stellar: Treasure Focus, then Home Health and Durability Health, then Power Focus (up to 166 shards, a nuke of about 2,100 at range 4).
  - Cassi: Power Focus ×5, then Durability Focus ×5, then Bruiser Health.
  - Issac: Treasure Strength, Home Health, Durability Health, then Power Strength.
  - The v4 set's 00rows game used a different build: Monster shards first, then Power Strength on Issac and Varg. That game was lost 789-1010 with only 2 of our deaths, a pure economy loss.
- **Bushes:**
  - **All 2,596 of their wards were placed on bush tiles.** On 02treasure-box, which has no bushes, they placed 0 wards. For comparison, 9% of our wards land on bushes.
  - Our deaths sit closer to bushes than random tiles do:

    | Deaths to | Within 2 of a bush | Within 4 of a bush |
    |---|---|---|
    | Stellar | 42% | 65% |
    | Cassi | 43% | 67% |
    | Issac | 40% | 62% |
    | Random tiles (baseline) | 22% | 43% |
  - Stellar took 376 damage in a 28-kill game (00packs B), 355 in a 19-kill game (00interlock) and 659 in a 12-kill game (00lost-world). We could not see it to hit it.
- **Spawn camping:** 136 of 429 deaths were within 8 tiles of our spawn.
  - 00packs: 18/44, 22/45 and 21/43.
  - 01gold-rush: 15/44 and 16/31.
  - 02treasure-box: 29/33.
  - On 00packs the "camp" is their bush row at y=20 (or y=10), 8 tiles from our spawn corner, which every exit crosses.
- **Cohesion:** they are a loose pack, not a deathball. When one of them places a ward, another is within 3 tiles only 36% of the time (median gap 5-10 tiles). Kills still involve 2-4 of them.
- **Where c2's model misjudges them (code facts):**
  1. `enemy_dps = strength + 0.15 x focus` is used in `group_balance` and the fight dps.
     - Stellar with 99 Power shards (focus about 1,073) scores 191, but it nukes 2,146 at range 4 and follows with an area spell of 1,502.
  2. `threats()` counts enemy strength only within `attack_range + 1`: 2 for Ren, 4 for Stellar and Cassi. Ren's range-4 stun-nuke never counts as incoming.
  3. `retreat_fast` scores tiles with the same reach, so a tile at distance 3 from Ren counts as safe.
  4. `recall_safe` uses `attack_range + 4`, which is 5 for Ren. Ren's dash 2 plus his range-4 stun covers 6.
  5. A caster in a bush is not in `vision.champions()`. It enters no model at all: c2 keeps farming while it is shot, because the danger block only counts camps.
  6. q24's "advantage" branch sets `clearly_losing = False`, which cancels v2's headcount flee.

## Imitation: `bots/imit_uvt2` (from c2_respawn; details in its NOTES.md)
- **Changes from c2_respawn:**
  - their draft and their per-champion build orders;
  - a burst-aware dps for its own fight decisions;
  - spells cast before walking, stun first;
  - Stellar and Cassi **kite**: they cast from range ≤ 4 when a spell is ready, and otherwise stay out of every enemy's reach;
  - **v2 lurk:** with spells down, the casters hide on bush tiles that no visible enemy shares, and basic-attack from cover;
  - the team-focus cell is written to shared memory and allies converge on it;
  - wards go only on bushes.
- **Does it reproduce the failure?** Yes. `mb_imit_uvt` (our logic plus their draft) lost 23-1 to q24.

```
v1 (no lurk), 11 ladder maps   SUMMARY c2_respawn vs imit_uvt2: 16W-6L (73%)  avg gems 865 vs 608  avg deaths 8.7 vs 19.8  botFaults(A) 0
v2 (+ lurk),  11 ladder maps   SUMMARY c2_respawn vs imit_uvt2: 13W-9L (59%)  avg gems 731 vs 703  avg deaths 13.4 vs 19.6  botFaults(A) 0
v2, all maps (baseline)        SUMMARY c2_respawn vs imit_uvt2: 76W-64L (54%)  avg gems 644 vs 656  avg deaths 15.7 vs 19.0  botFaults(A) 0
```
- **Context for 76/140.** c2 beats tb_aggro and imit_test 24-0, and tb_deathball 15-1. 76/140 is the worst c2 score against any local opponent.
- **Loss shapes copied from the ladder (v2):**

  | Map, side | Local | Ladder |
  |---|---|---|
  | 00packs A | 65-1000, 31 of our deaths (13 within 8 of spawn) | 85-1005 and 366-554 |
  | 01gold-rush B | 401-701, 28 deaths | 363-605 |
  | 00lost-world A | 313-1009, Stellar took 484 damage | 213-1009, Stellar took 659 |
  | 00galaxy A | lost | lost |
  | adgato-gemcombat4 A | lost | lost |
  | 01concentrated-wealth A | lost | lost |
- **Agreement with the ladder:**
  - Same result on 10 of the 15 ladder map-sides.
  - Near-bush profile across all maps: c2's deaths to Stellar and Cassi are within 2 of a bush 58-60% of the time, against 28% for random tiles.
- **Fidelity gaps:**
  - The imitation is too bush-heavy (58-60% against the ladder's 42%).
  - c2 is worst against it on 5-pick (40/84), but the ladder disaster was 3-pick (15/24 locally).
  - 00interlock A and 00rows A are local wins but ladder losses.

## Counter: `bots/h_antifocus` (c2_respawn plus the changes below; NOTES.md has the switch table)
- **`af_threat(e)`**, computed per visible enemy and cached per turn.
  - Inputs: the enemy's `abilities()`, each ability's `info()` (modifier, range, radius, `exclusive_with_movement`) and its `cooldown()`. All of these work on visible enemies, as verified in the debug stdout: Stellar's burst reads 30 on cooldown, then 267, 586, 1,828 as it gains focus.
  - **reach:** basic range + 1, or + 2 more with a ready dash, or a ready spell's range.
  - **burst:** strength, plus strength again with a ready attack reset, plus modifier × focus for each ready damage, stun or area spell.
- **`AF_ONESHOT` 0.7.** Applies when the summed burst of enemies that can reach us is ≥ 0.7 × our HP. The champion:
  - takes no new fight unless the target dies now;
  - strikes an adjacent melee only if it dies in two hits;
  - retreats, with `retreat_fast` scoring tiles by burst reach and burst damage.
- **Ren-type retaliation passive.** While we hit it, we take 1.5 × 0.2 × focus per turn; this enters the kill-time ratio.
- **`AF_HEADCOUNT`.** The "advantage" branch no longer cancels v2's headcount flee while the burst in reach is ≥ 0.5 × HP.
- **`recall_safe`** requires distance > max(basic range + 4, reach + 2).
- **`AF_UNSEEN` (hidden attacker).**
  - **Detection:** HP lost since the end of our last turn, minus what is explained, > 60. Explained = awake camps × 1.15 + the full burst of visible enemies, ignoring cooldowns + unseen live camps in range.
  - **Response:**
    1. drop the farming target if it is within 6 tiles;
    2. step, or dash when that gains more, away from the unseen bush tiles within 5, until 5 tiles clear (at most 6 turns);
    3. once clear, recall if below 60% HP;
    4. groups within 6 of the spot score ×0.35 for 60 rounds.
- **`AF_SHARE`.** The ambush cell and round go in shared bytes 5 and 6, but only with 5 or fewer bodies. `read_claims` then reads only the claim bytes.
- **`AF_BUSH_WARD`.** For 300 rounds after a hidden hit, or after seeing an enemy whose ready burst is ≥ 0.5 × our max HP, we ward an unseen bush tile within 2. The ward sees into that bush, so the caster becomes a visible target.
- **Iterations** (targeted screens, 11 ladder maps × 2 sides):
  - **v1** = burst model, one-shot, headcount, recall pad, retaliation, and a single step off after a hidden hit.
  - **v2** = final. It adds: one-shot 0.9 → 0.7; leaving to 5 tiles clear with a dash; recall after leaving; dropping the target; shared ambush spot; bush wards.
  - **Why v2.** A debug trace showed v1 was not enough: `bots/dbg_afprobe` is this bot with AF_LOG and DIAG on, game `matches/uvt2-dbg2`, 01gold-rush B.
    - There were 26 unexplained hits of 110-812 HP.
    - 6 of the 12 traced deaths came within 8 rounds after one of those hits.
    - A single step left the champion inside the caster's range: Vendetta took 564 and then 455 at (13,12) and (14,12).

## Results (verbatim SUMMARY lines)
```
v1  11 maps  SUMMARY h_antifocus vs imit_uvt2: 14W-8L (64%)  avg gems 817 vs 684  avg deaths 12.2 vs 19.0  botFaults(A) 0
v2  11 maps  SUMMARY h_antifocus vs imit_uvt2: 17W-5L (77%)  avg gems 879 vs 673  avg deaths 9.8 vs 22.5  botFaults(A) 0
v2  11 maps  SUMMARY h_antifocus vs c2_respawn: 13W-9L (59%)  avg gems 788 vs 732  avg deaths 8.3 vs 9.2  botFaults(A) 0
final, all   SUMMARY h_antifocus vs c2_respawn: 74W-66L (53%)  avg gems 703 vs 674  avg deaths 8.9 vs 11.1  botFaults(A) 0
final, all   SUMMARY h_antifocus vs tb_merge_b: 104W-36L (74%)  avg gems 793 vs 524  avg deaths 7.8 vs 14.1  botFaults(A) 0
final, all   SUMMARY h_antifocus vs imit_uvt2: 105W-35L (75%)  avg gems 774 vs 561  avg deaths 9.2 vs 23.3  botFaults(A) 0
baseline     SUMMARY c2_respawn vs imit_uvt2: 76W-64L (54%)  avg gems 644 vs 656  avg deaths 15.7 vs 19.0  botFaults(A) 0
```
- **Commands.**
  - All runs used `tools/onslurm.sh -c 24 -m 16G` and `python3.12 tools/eval.py <A> <B> --maps all --jobs 16 --keep --tag <tag>`.
  - Tags: `af-all-c2`, `af-all-tbm`, `af-all-imit`, `uvt2-all-c2`; screens `uvt2-s1-c2`, `uvt2-s2-c2`, `af-s1-imit`, `af-s2-imit`, `af-s2-c2`.
- **Versions.** Final h_antifocus `src/bot.py` md5 `0fdc5268...`. The other three files are identical to c2. The imitation was frozen before every all-maps run.

**Per-game metrics** (scratchpad scripts `deaths.py` and `paired.py`; "near bush" = within 2 tiles, "near spawn" = within 8 tiles of our spawn):

| Run (us vs opponent) | 3 / 4 / 5 bodies | Deaths | Near bush | Near spawn | Killed by Ren, Stellar or Cassi | Gem loss | fuelExh | Our wards on bushes |
|---|---|---|---|---|---|---|---|---|
| c2 vs imit_uvt2 | 15/24, 21/32, 40/84 | 15.7 | 8.4 | 2.8 | 10.0 | 97 | 7.0 | 12% |
| **h_antifocus vs imit_uvt2** | **24/24, 24/32, 57/84** | **9.2** | **3.4** | 1.6 | **5.0** | 64 | 18.9 | 25% |
| c2 vs tb_merge_b (`skc2-vs-tbm-all`) | 10/24, 24/32, 64/84 | 9.4 | 4.3 | 1.7 | - | 79 | 6.8 | 13% |
| h_antifocus vs tb_merge_b | 13/24, 26/32, 65/84 | 7.8 | 2.9 | 1.9 | - | 61 | 12.6 | 21% |
| h_antifocus vs c2 (c2's side: fuelExh 6.8) | 12/24, 19/32, 43/84 | 8.9 | 3.1 | 1.5 | - | 60 | 14.1 | 22% |

## Analysis session
- **Did the targeted mechanism change? Yes, on every metric that names it.**
  - **Against the imitation, paired by map-side:**
    - 37 gained and 8 lost (sign test p ≈ 1e-5);
    - 3-pick went from 15/24 to **24/24**;
    - deaths per game fell from 15.7 to 9.2;
    - deaths near bushes fell 60%, from 8.4 to 3.4 per game;
    - deaths to Ren, Stellar or Cassi halved, from 10.0 to 5.0;
    - our wards on bushes doubled, from 12% to 25%.
  - **On the 11-map screen:**
    - damage dealt to Stellar rose from 109k to 122k, and to Cassi from 81k to 99k (bush wards make them targetable);
    - deaths near bushes fell from 140 to 54.
  - **The reproduced disasters flipped:**
    - 00packs A: 65-1000 became W 909-745;
    - 01gold-rush B: 401-701 became W 473-407;
    - 00lost-world A/B both became wins (1016-841 and 1009-442).
- **Debug-game evidence for each rule** (debug builds, so the trajectories differ from the eval):
  - On 01gold-rush B the v2 probe (`matches/uvt2-dbg3`) flagged 40 hidden hits and 90 one-shot turns. 95 of its 379 wards were on bushes, against 37 of 336 for v1.
  - It won 533-490 with 23 deaths. The v1 probe lost 341-484 with 30 deaths.
- **Why the head-to-head against c2 is only 74/140.**
  - **The averages favour h_antifocus:**
    - deaths 8.9 against 11.1, gem rate 13.2 against 12.4, gold 5,859 against 5,343;
    - camp_metrics counts W67, L63, T10 (ties).
  - Win/loss contrast (`analyze_match.py --summary matches/af-all-c2`): the usual mirror profile, decided by fights (K/D 13.5/4.7 in wins against 6.2/11.3 in losses).
  - **Fuel:** h_antifocus has **14.1 fuelExhausted per game against c2's 6.8** in the same games. Our suspensions average 19.0 in losses and 9.7 in wins.
    - The overhead appears against every opponent: 18.9 against the imitation (c2: 7.0) and 12.6 against tb_merge_b (c2: 6.8).
    - **Measured.** One PROF game, `dbg_afprof` vs c2_respawn on 00lanes A (`matches/uvt2-prof`, the map with the most of our suspensions in the head-to-head, 161 against 56):
      - 124 of 5,217 profiled turns were suspended.
      - The AF burst section costs about **120k fuel per turn with enemies near** (254M over 2,111 turns).
      - The hidden-hit check (`af_chk`) costs 180-256k on turns with an unexplained hit.
      - c2's own sections still dominate: `choose` 2.8G, `observe` 1.8G, and `choose_bank` 1.2-1.3M on heavy turns. So the AF code pushes turns that were already near the 2.5M cap over it.
    - **Where the AF cost comes from, read from the code:**
      - `af_step_off` and `af_unseen` compute `min(cheb(p, t))` in Python over up to about 120 unseen tiles × 25 candidate tiles;
      - `af_full` is not cached;
      - `af_threat` makes about 10-15 API calls per visible enemy each turn.
  - **Statistics:** 74/140 is not distinguishable from the mirror's 70. Placebos score 66-68 (`2026-11-01-placebo.md`). So this is no regression, but no promotion either.
- **Losses against the imitation** (35; `analyze_match.py --summary matches/af-all-imit`): economy rather than fights.
  - Clears 38.7 against 56.1; first clear r72 against r57; gem lead −40 at r250.
  - **8 paired regressions where c2 won and h_antifocus lost:**
    - 00ambush B, 00dunes A, 00rushbait-v2 A, 01corridors A, 01shortcut A, 02treasure-box B;
    - 00ribs A/B: 300-999 and 157-1000, with first clear r248 against c2's r144 and 17 clears against 35.
    - The ambush response (stepping off, target penalty ×0.35, recall) costs tempo on some maps.
- **Surprising wins:**
  - 3-pick went 24/24 against the imitation, the ladder's worst case (1-4).
  - Against tb_merge_b, 3-pick went from 10/24 to 13/24, and the 02treasure-box and 02uncharted-lands A games flipped to wins.
- **Scope.**
  - **Not inert:**
    - `retreat_fast` and `recall_safe` use burst reach for every enemy;
    - one-shot fires in mirror fights when 2-3 enemies are in reach of a hurt champion;
    - bush wards follow any big-burst sighting.
  - So it was gated alone: 74/140, which fails ≥ 82.
  - The ladder hedge improved by +6: 23 gained and 17 lost against c2's tb_merge_b games.

## Verdict
**kept, as a counter to merge into the next combo; not promotable alone.**
- **For:**
  - The mechanism is confirmed by a decisive paired result against an imitation that reproduces the ladder failure: 105 against 76/140; 37 gained and 8 lost; deaths −41%.
  - The ladder hedge is up: 104 against 98/140.
  - 0 bot faults.
- **Against:**
  - 74/140 against c2 fails the gate. Don't upload.
  - Fuel exhaustion doubles; this cost has to be removed before a combo gate (V3L-1a).
- I did not edit STRATEGIES, READY, STATUS or CHAMPION. The orchestrator should record:
  - **T-row:** "V3L-1 h_antifocus: 74/140 vs c2, 104 vs tb_merge_b, 105 vs imit_uvt2 (c2 76); kept (combo)".
  - **Queue entries:** the new hypotheses below.

## New hypotheses generated
- **V3L-1a: fuel-clean h_antifocus.**
  - Evidence: fuelExhausted rises 2-2.7× in every opponent set (7.0 → 18.9, 6.8 → 12.6, and 14.1 against c2's 6.8 in the head-to-head). Our suspensions average 19.0 per game in head-to-head losses against 9.7 in wins.
  - Measured cost: about 120k fuel per fight turn in the burst section, and up to 256k on turns with a hidden hit (PROF, `matches/uvt2-prof`).
  - Change:
    - replace the Python `min(cheb)` loops in `af_step_off`, `af_unseen` and `af_hidden_bush` with Bitboard distance rings (dilate the unseen-bush board 1..6 times and test candidates);
    - cache `af_full` per turn;
    - cache each enemy's static ability records (`info()`, `passive()`) by handle, so that only `cooldown()`, strength and focus are read each turn.
  - Then re-gate. The head-to-head may move above 74/140 for free.
- **V3L-1b: low-HP disengage under a burst alert.**
  - Evidence: in v2's debug trace (`uvt2-dbg3`), 5 of 9 traced deaths (r595, r603, r703, r829, r904) followed 5-8 turns at 15-45% HP next to an enemy.
    - Examples: stand-and-trade with a Power-Strength Issac, and being chased by Ren.
    - No rule fired, because c2's kill-time ratio stayed below 1.6 until death.
  - Change: while `af_alert` is active and HP < 45%, engage only kill-now targets and go home.
- **V3L-1c: ambush-response tempo.**
  - Evidence: 8 paired regressions against the imitation are economy losses, e.g. 00ribs B with first clear r248 against r144 and 17 clears against 35.
  - Change: soften the response. Use a target penalty of 0.6, or penalise only after two hidden hits, and skip it when the group is our only reachable target.
- **V3L-1d: imitation fidelity.**
  - The ladder disaster is 3-pick (1-4, 41 deaths per game); `imit_uvt2` hurts c2 most on 5-pick (40/84) and is too bush-heavy (Stellar kills within 2 of a bush: 58% against 42%).
  - The v4 set's build changed to Monster shards, then Power Strength on Issac and Varg (00rows, an economy loss).
  - Next: a v4-build variant and a less bushy lurk rule, to test the economy side.
- **V3L-1e: proactive bush wards.**
  - Under the counter, 21-25% of our wards land on bushes, against 12-13% for c2, and deaths near bushes fell against every opponent, including the mirror (3.1 per game) and tb_merge_b (4.3 → 2.9).
  - Test bush-first ward placement near our farming target on its own, outside the burst alert.
