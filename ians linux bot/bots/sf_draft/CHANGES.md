# sf_draft: changes on top of sf_base

Assignment: INSIGHTS section 4, item 4 (meta draft) and item 5 (Bruiser builds), plus handling of the full ability kits.
Every A/B below is `tools/eval.py <bot> sf_base`. "quick" means 12 maps x 2 sides (24 games), and "sprint" means 20 maps x 2 sides (40 games).
The changes were stacked and measured one at a time. Each row is cumulative.

| Step | quick A/B vs sf_base | avg gems (us vs base) | avg deaths (us vs base) | mean tribute | deaths_by_camp/game | gemsLost_to_champion/game |
|---|---|---|---|---|---|---|
| 1. Draft only | 14W-10L (58%) | 569 vs 432 | 12.2 vs 19.1 | 19.4 | 0.9 | 53.8 |
| 2. + Bruiser items | 16W-8L (67%) | 661 vs 346 | 9.2 vs 21.5 | 21.9 | 1.1 | 32.5 |
| 3. + kit usage (shipped) | **18W-6L (75%)** | 684 vs 338 | 11.0 vs 24.8 | 23.4 | 1.1 | 54.4 |
| 4. + travel dash (reverted) | 16W-8L (67%) | 639 vs 429 | 14.0 vs 18.7 | 22.8 | 1.2 | 66.0 |

botFaults(A) was 0 in every run.

**Final results:**
- **Sprint A/B vs sf_base:**
  `SUMMARY sf_draft vs sf_base: 29W-11L (72%)  avg gems 605 vs 400  avg deaths 10.8 vs 21.1  botFaults(A) 0`
  - Metrics: mean tribute 23.1, deaths_by_camp 0.9/game, gemsLost_to_camp 3.7/game, gemsLost_to_champion 48.4/game, fuelExhausted 299/game.
  - Fuel is unchanged from sf_base's 300/game.
- **Cross-check vs tb_economy (quick):**
  `SUMMARY sf_draft vs tb_economy: 21W-3L (88%)  avg gems 929 vs 360  avg deaths 4.3 vs 48.9  botFaults(A) 0`
  - sf_base on the same set: `18W-6L (75%)  avg gems 885 vs 413  avg deaths 7.5 vs 48.9`.
- **Per champion over the 40 sprint games** (monsterDamageDone / deaths / collectedGems / kills):
  | Champion | monsterDamageDone | deaths | collectedGems | kills |
  |---|---|---|---|---|
  | Vesper | 21.9k | 1.6 | 194 | 5.7 |
  | Vendetta | 21.9k | 1.6 | 179 | 9.1 |
  | Marcella | 16.2k | 2.8 | 146 | 3.0 |
  | Ryth | 15.9k | 3.0 | 129 | 2.2 |
  | HoR | 6.2k | 3.5 | 97 | 1.2 |
  - Base champions ranged from 11.9k to 16.1k monster damage and from 3.8 to 5.6 deaths.
  - HoR is still the weak slot. A follow-up could try Varg or Tavi fifth, or a different HoR build.

## 1. Draft (`src/draft.py`): the meta core
- The new `PRIORITY` is Vesper Vale, Vendetta, Marcella, Heart of Ruin, Ryth, then Tavi, Varg, Ren and the rest.
  - The old list is kept above it and shadowed, so the diff stays small.
- The carries and both plain-dash champions come first, so a 3-pick map still gets Vesper, Vendetta and Marcella, with two dashes for crossing.
- Heart of Ruin (draft id 11) is pickable. It shows in the roster of every 4-pick and 5-pick game.
- **Effect:** +4 W-L over 50% and deaths down. 3-4 pick maps went 10W-2L.
  5-pick maps (HoR and Ryth in place of the base's Varg and Marcella) went 4W-6L. HoR is our weakest farmer: monsterDamageDone was about 6-8k, against 15-24k for the others.

## 2. Bruiser builds (`Bot.bruiser_item`, constants `BRUISER_ITEMS`, `BRUISER_PLAN`, `ITEMS_BRUISER`, `JUNGLE_FIRST`)
- **Main-stat weights:**
  - Vesper, Vendetta and Tavi: Strength 2, Health 1.
  - Ryth: Health 2, Strength 1. Her passive turns bonus HP into Strength.
  - Heart of Ruin: Health 1, Focus 1. The shield and the landing dash scale with Focus.
  - Marcella: Focus, Health and Strength, 1 each.
- **Buying rule:** finish a partly bought emblem first, then buy the stat with the lowest shards-per-weight. Champions not in the plan (Varg, Ren and others) keep the old Jungle, then Monster, then Power build.
- **Hook into `shop()`:** one `item = self.bruiser_item(me, counts)` line, plus the old `if` becoming an `elif`.
- **Effect:** 58% to 67%, deaths 12.2 to 9.2, gems lost to champions 53.8 to 32.5 per game.
  Camp deaths rose slightly, from 0.9 to 1.1 per game, after losing the Jungle -30%. That is still inside the top-20 range of 0.2 to 1.8.
- **Our Ryth:** monster damage 12.1k to 19.2k.
- `JUNGLE_FIRST = True` would put the Jungle emblem first again. It was not tested.

## 3. Kit usage (`cast_combat` hooks plus new helpers; each part can be switched off with its own flag)
- **`KIT_LANDING_DASH`** (`cast_landing_dash`, used by HoR slot 1):
  - The dash, which is walking-compatible, lands on the free tile within 2 that has the best score. Each unit within radius 1 of the landing counts: awake or target-group camps +1, enemies +2, enemies that are channelling +4, sleeping camps of other groups -3 so they are not woken.
  - If HoR's basic attack is still unused, it then attacks.
  - The dash is kept for escape below 35% HP.
  - `dps()` now counts the landing damage / 8, as it already did for damage spells.
- **`KIT_AOE_AIM`** (`aim_area`, used by Ryth slot 0 and any ground AoE): casts at the tile in range that hits the most units, instead of the target's own tile.
- **`KIT_RESET_RETARGET`** (`reset_and_hit` and `reset_target`): an attack reset (Vendetta, Vesper, Ryth slot 1, Tavi slot 0, Marcella's enhanced reset) is only used when a live unit is in basic-attack range.
  - If the first hit killed the target, it re-targets: enemy champion first, then the weakest awake or target-group camp.
  - Before this change, the reset fired and its second attack was skipped, which wasted the cooldown. Vendetta's kill passive refreshes her cooldowns, so she now chains hits across clusters.
  - Vendetta's championDamageDone went from 8.4k to 17.1k per game.
- **Unchanged and already correct in sf_base:**
  - HoR's self-shield when incoming > 0.
  - Marcella's 2xF spell (excluded after walking).
  - Tavi's 1.6xF stun.
  - Enemy chase dashes.
- **Effect:** 67% to 75%, avg gems 661 to 684, mean tribute 21.9 to 23.4.
- **Reverted:** a travel dash for Vesper and Vendetta (walk, then dash 2 further down the same distance field when there are no enemies or awake camps).
  - It went 16W-8L, with deaths 11.0 to 14.0 and gems lost to champions 54 to 66 per game. The dash was on cooldown when an enemy showed up.
  - In one gemfight game it also triggered a both-teams stand-off and stall from round 230 to 2000. The likely cause is sf_base's mutual step-away logic.
  - The code is removed from the patch.

## Merge notes
- **`draft.py`:** one hunk, a new `PRIORITY` assigned after the old one. If another patch also edits the draft list, keep this order.
- **`bot.py` top:** new constants after `DEBUG = False` (`_CT`, `BRUISER_*`, `ITEMS_BRUISER`, `JUNGLE_FIRST`, `KIT_*`).
- **`shop()`:** only the first branch of the item choice changed. `bruiser_item()` is a new method placed just before `# ---- combat`. The TP-crystal purchase is untouched.
- **`dps()`:** one `elif` for the landing dash.
- **`cast_combat()`:** three small hooks.
  - A landing-dash call after the shield block.
  - `aim_area` in place of the target tile for AoE casts.
  - The `attacked and target` block now calls `reset_and_hit` and returns. The old loop is kept after it for when the flag is off.
- **New methods**, placed before `pick_camp_in_range`: `kit_units`, `best_area_tile`, `aim_area`, `cast_landing_dash`, `reset_target`, `reset_and_hit`.
  They read `self.target` (the current Group), `self.blocked_now`, `self.walk_block` and `dilate`.
- **Independent parts:** items (2) and kit (3) don't depend on the draft. Kit (3) helps any roster. Each kit flag can be dropped on its own.
