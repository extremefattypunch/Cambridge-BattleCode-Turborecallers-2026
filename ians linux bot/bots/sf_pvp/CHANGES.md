# sf_pvp: changes on top of sf_base (INSIGHTS items 8, 7 and 6)

All edits are in `src/bot.py`. New code is in one delimited block of methods,
`# --- sf_pvp: focus, locks, wards`, placed just before the `# --- turn` section.
Existing functions get only small edits.

## 1. Carrier and channel focus (item 8)
- **`handle_enemies` target choice.** `focus_bias()` gives each visible enemy within 6 tiles
  (8 tiles for the team focus target) an engage ratio and a priority tier:
  - Tier 0: enemies channelling a tribute or teleport (ratio 1.2), or a recall (ratio 1.0).
  - Tier 1: the team focus target (ratio +0.2).
  - Tier 2: everyone else (ratio 0.8, the same as sf_base).
  - Carried gems add up to +0.3 to the ratio (`gem_count()` is readable for visible enemies).
  - The sort key within a tier is `my_ttk / (1 + gems/20)`, so carriers come first.
  - When we carry 30 or more gems ourselves, the ratio is capped back at 0.8 against
    non-channelling enemies.
  - With no channel, no gems and no focus, the ordering and the 0.8 threshold match sf_base exactly.
- **Threat model.** `CHAN_THREAT` weights an enemy's strength in `threat` by its channel:
  tribute 0.5 (it has to cancel before it can hit back), teleport 0 (it can't act), recall 1.
- **Shared focus byte.** Byte `FOCUS_BYTE = 7` of shared memory holds
  `(enemy_index + 1) << 5 | (round & 31)`. The enemy index is the rank of the enemy handle
  in `sorted(cambc.champions(Team.ENEMY))`. The value is fresh for `FOCUS_TTL = 3` rounds.
  - The engaging champion writes it every turn it engages.
  - Allies who see that enemy get tier 1 and +0.2 ratio, and consider it out to 8 tiles.
  - **`read_claims` now loops `range(FOCUS_BYTE)` instead of `range(8)`**, so the focus
    byte is never read as a camp claim. That is the only change to sf_base's claim
    protocol. With at most 6 bodies (Cassi and Issac count as two), claim slots 0-5 are
    unaffected and byte 6 is still free.
- **`stun_channel()` runs before moving** when the chosen target is channelling and isn't Marcella.
  - It uses a CC (unit target), an AoE with a stun duration (Ryth slot 0, ground target),
    or a dash with a landing stun (Heart of Ruin, landing tile within radius 1 of the target).
  - It skips the stun when we would kill the target before its tribute or teleport channel
    ends (`ttk < remaining_channel_time`), so we take the bag instead.
  - For a recall, it stuns only when a basic attack can't reach, since damage already
    cancels a recall.

## 2. Altar locks (item 7)
- **`buy_lock()`**, called from `shop()`: buys one lock (10g) on spawn or while dead,
  when carrying none and gold is at least `LOCK_MIN_GOLD = 40`.
- **`try_lock()`**, called from `play_turn` right after `threats()` (it uses no action allowance):
  - Reactive: if a visible enemy `is_submitting_gems()` within 1 of an altar that is within
    2 of us, lock that altar. This cancels their channel.
  - Proactive: lock any unlocked altar within 2 of us that lies on the enemy side
    (`cheb(altar, enemy spawn) <= cheb(altar, our spawn) + LOCK_SIDE_MARGIN (4)`).
    Our own team can still tribute there.
- **Defensive handling in `do_tribute`:**
  - `locked_altars()` remembers altars last seen with an enemy lock.
  - The carrier walks to the ring of unlocked altars if one is reachable on foot.
  - `break_lock()` basic-attacks an adjacent enemy lock when no unlocked altar is within 8,
    or none is reachable.
  - **Bug fixed:** sf_base stood still forever next to an enemy-locked altar.
    It skipped the locked altar, but `step_toward` returned False because it was already
    on the altar ring.

## 3. Wards (item 6)
- **`try_ward()`**, called every turn in `play_turn` after the channel check: when
  `ward_cooldown() == 0`, place the ward within 2 tiles.
  - Within 4 of an altar, place it on the tile nearest the altar, unless our ward already
    sits within 2 of it.
  - Otherwise, once the old ward is more than 6 tiles away, place it on the tile nearest
    the enemy spawn. Bush tiles break ties.
  - The result is about 330-360 wards per game (about 70 per champion).
- **`threats()` ignores enemies more than `ENEMY_SIGHT = 8` tiles away.** They can only
  be seen through our ward, and without the filter they would trigger sf_base's
  "gems >= 10 and enemies -> tribute now" rule and turn off `safe_finish`.
  They are stored in `self.far_enemies`, which nothing uses yet.
- `USE_WARDS` is a kill switch.

## Measured effect
(quick = 12 maps x 2 sides = 24 games; sprint = 40 games)

| Run | Result | Notes |
|---|---|---|
| sf_base vs tb_aggro (quick, baseline) | 9W-15L (38%) | gems lost to champions 140/game; enemy gems we stole 87/game |
| v1 (focus + stun + reactive locks + lock avoidance + wards) vs tb_aggro | 19W-5L (79%) | kills 28.8 vs 25.1, deaths 14.6 vs 18.6, gems lost to champions 102, stolen 150 |
| v1 vs sf_base (quick) | 17W-7L (71%) | deaths 15.8 vs 26.4; gems lost to champions 99 vs sf_base's 168 |
| v2 (+ proactive locks) vs tb_aggro | 22W-2L (92%) | enemy tributed only 220/game (v1: 425); enemy gems stolen 270/game |
| v2 vs tb_economy (quick) | 22W-2L (92%) | sf_base scored 18W-6L (75%) on the same set. Deaths 3.9 vs sf_base's 7.5; enemy gems stolen 238 vs 160 |
| v2 with `USE_WARDS = False` vs tb_aggro (ablation) | 20W-4L (83%) | Kills 26.7, deaths 17.4 (with wards: 29.0 and 15.6). Wards look mildly positive but within noise, so they stay on |
| **Final: v2 vs sf_base (sprint, 40 games)** | `SUMMARY sf_pvp vs sf_base: 31W-9L (78%)  avg gems 575 vs 216  avg deaths 12.4 vs 20.4  botFaults(A) 0` | Kills 19.4 vs 11.7; gems lost to champions 78.5 vs 123.9; camp deaths 0.7/game; mean tribute 21.0; locks bought 5.6/game; wards 348/game; fuelExhausted 295/game (sf_base 226 in the same run) |

**Caveat on the self-play A/B.** With proactive locks, sf_base stalls next to our locked
altars (the do_tribute bug fixed above), so the A/B against sf_base overstates the gain.
The tb_aggro and tb_economy cross-checks are the honest numbers. tb_aggro routes around
locked altars, and tb_economy breaks them through `submit_gems`.

## Independent / optional parts of the patch
- **Wards** (`try_ward`, its call in `play_turn`, `USE_WARDS`) can be dropped on their own.
  Keep the `ENEMY_SIGHT` filter in `threats()` whenever wards stay.
- **Lock avoidance in `do_tribute`** (`locked_altars`, `break_lock`, the ring edit) is a bug
  fix that is worth keeping even without buying locks, because tb_aggro and probably
  ladder bots place locks.
- **Lock usage** (`buy_lock` in `shop`, `try_lock` after `threats()`, `LOCK_SIDE_MARGIN`):
  the proactive part is the block at the end of `try_lock`.
- **Focus** (`CHAN_THREAT`, `focus_bias`, `read_focus`/`write_focus`, `stun_channel`, the
  `handle_enemies` edits, the `read_claims` bound) is self-contained. If another patch
  rewrites `handle_enemies` (item 9, fight/flee), re-apply three pieces on top of it:
  - the `focus_bias` ratio and key;
  - `write_focus(best)` followed by `moved = self.stun_channel(...)` before moving;
  - the `CHAN_THREAT` weighting.

## Costs and risks
- **Fuel.** fuelExhausted rose by about 50-70 per game against sf_base: 295 vs 226 in the
  final run, and 396 with wards vs 344 without in the tb_aggro ablation. All new per-turn
  work is O(altars + enemies) or a 25-tile scan when the ward is charged, so some of this
  is probably noise.
- **Aggression.** Engaging channelling or carrying enemies at a 1.2-1.5 ratio could
  backfire against a bot that cancels its tribute to fight back. Lower the ratios in
  `focus_bias` if that shows up.
