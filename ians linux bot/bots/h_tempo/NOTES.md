# h_tempo: Q28 farming-tempo item build (final = iteration 2)

Fork of tb_merge_b. Flags at the top of src/bot.py:
- TEMPO_JUNGLE: the first emblem of a planned champion is Jungle on its main stat (Strength for Vesper/Vendetta/Tavi, Health for Ryth/HoR, Focus for Marcella).
- TEMPO_THREAT_FIX: threats() scales only the camp part by 0.7 when any Jungle emblem is owned (was x0.8 on the total, incl. enemy champions). jungle() recognises any-stat Jungle emblems; dps() recognises any-stat Monster emblems.
- TEMPO_JUNGLE_COUNTS (iteration 1): the Jungle emblem counts as one emblem of its stat in the Bruiser plan, so it replaces the first main-stat Bruiser emblem.
- TEMPO_STR_ARM (iteration 2): after Jungle + one Bruiser emblem, Vesper/Vendetta/Ryth buy a Monster emblem (Strength shards) and then follow S:3,H:1 (Vesper, Vendetta) / S:1,H:1 (Ryth).
Gate vs tb_merge_b on all maps: 75W-65L (54%), not promoted. Report: results/simulated-matches/2026-11-01_0153_h_tempo/notes.md.
Below: tb_merge_b's notes, unchanged.

# tb_merge_b: Sprint 3 merge of sf_pvp, sf_bank, sf_draft and sf_fuel

Base: `bots/sf_base` (frozen tb_splitfarm).
- Integration order: **sf_pvp, then sf_bank, then sf_draft, then sf_fuel**.
- sf_maps is excluded (it was neutral).
- A snapshot of every validated step is in `matches/tb_merge_b-good-s<N>/src`. The final bot is s5.

## Patches included
| Step | Patch | How it went in | Quick A/B vs sf_bank (24 games) |
|---|---|---|---|
| s1 | sf_pvp | Clean `patch -p2`. The result is identical to bots/sf_pvp (measured at 31W-9L vs sf_base), so it was not re-run. | - |
| s2 | + sf_bank | 15 of 19 hunks applied. The 4 rejects were merged by hand: init state, the `do_tribute` ring, the fight/flee helpers, and `handle_enemies`. | 20W-4L (83%) |
| s3 | + sf_draft | Clean `patch -p2`. It covers draft.py, the constants, the `shop()` hook, `dps()`, the `cast_combat` hooks and the kit helpers. | 21W-3L (88%) |
| s4 | + sf_fuel | 8 of 12 hunks applied. The 4 rejects were merged by hand: constants, init state, the `choose_target` tie-break with `note_progress`, and the `altar_distance` call in `play_turn`. sf_bank's banking was then ported onto the static fields (see below). | 22W-2L (92%) |
| s5 | + stun guard fix | After `stun_channel()`, if the target is no longer in vision (the stun killed it), return. Before the fix, `best.position()` raised "Unit is not in vision" and the turn was lost. | 24W-0L (100%) |

The step-2 eval initially ran without sf_bank's helper methods, because hunk 11 had been rejected and only the
`handle_enemies` head was spliced in. A smoke game showed `'Bot' object has no attribute 'recall_safe'`.
The helpers (`enemy_dps`, `champ_dps`, `recall_safe`, `adjacent_melee`, `strike`) were added and the eval was re-run.
The s2 number above is from the fixed run.

## How the conflicts were resolved
### handle_enemies (sf_bank + sf_pvp)
**sf_bank's kill-time model makes the engage and retreat decision.** It uses:
- `champ_dps` and `enemy_dps`;
- `their_ttk = hp / (max(threat, fight_dps) + camp_inc)`;
- engage at ratio <= 0.85 (0.7 when we carry 30 or more gems);
- `clearly_losing`;
- adjacent-melee stand-and-trade;
- the stall breaker;
- the chase guard;
- `recall_safe`.

**sf_pvp is layered on top:**
- `near` also includes the team focus target out to 8 tiles.
- `CHAN_THREAT` weights both `threat` and sf_bank's `fight_dps`. A tribute channel counts 0.5, a teleport 0 and a recall 1.
- `focus_bias()` returns sf_pvp's ratio, which is 0.8 when neutral. **The excess over 0.8 is added to sf_bank's engage limit:**
  - +0.4 for a tribute or teleport channel;
  - +0.2 for a recall;
  - +0.2 for the team focus target;
  - up to +0.3 for carried gems.
  - When we carry 30 or more gems, focus_bias caps this at 0 against non-channelling targets.
  - sf_bank's `FIGHT_CARRIER_BONUS` (+0.15 when the target carries 15 or more gems) is kept as a floor of the
    bonus, not added on top, so carried gems are not counted twice.
- **Target order** uses sf_pvp's key, `(tier, my_ttk / (1 + gems/20), d)`, with sf_bank's `my_ttk` (approach at 0.5 per tile).
- **On engage:**
  1. `write_focus(best)` (shared byte 7).
  2. `moved = stun_channel(me, best, ttk)`. Here `ttk` is the kill time plus the full approach distance, the same meaning as in sf_pvp.
  3. The s5 vision guard.
  4. Dash, step, attack and `cast_combat`.
  5. sf_bank's chase-guard bookkeeping.

### do_tribute (sf_pvp + sf_bank)
1. sf_pvp's lock handling runs first: `locked_altars`, `break_lock`, and walking to the free ring.
2. Then sf_bank's `pref` ring replaces the ring when it has a free tile. `pref` comes from `pick_altar`, which already skips enemy-locked altars.

### shop (sf_pvp + sf_draft)
`buy_lock()` (sf_pvp) runs first, then sf_draft's `bruiser_item()` loop. The TP-crystal purchase is unchanged.

### sf_fuel vs sf_bank banking
Once the static fields exist, `field` and `visited` are None in `play_turn`.
- **`pick_altar(field, visited, rnd, pos)`** now reads **one static field per altar**:
  - keys are `-2 - i`, rooted at the ring of `altar_goals[i]`;
  - they are built by `build_static_fields` and included in `sf_dests` while they are still unbuilt;
  - it falls back to the per-turn field when that altar's field is not built yet, or when `sf_use` is False
    (we stand on a `walk_block` tile).
- sf_fuel's whole-ring field (`-1`) is **no longer queued**, because `altar_distance()` is unused after sf_bank.
- **`detour()`** uses `group_dist(G, pos, field, visited)` instead of `field.get(G.center)`.
- **`choose_target`** keeps sf_bank's death-memory penalty, which multiplies by 0.3. That is at most 1, so the
  pruning bound stays valid. It also keeps sf_fuel's bound skip, fuel floor and index tie-break.
  The stuck guard (`note_progress`) runs at the end of the farming branch.
- `main.py` calls `bot.build_static_fields()` after `play_turn()`.

### Shared memory
- Bytes 0-5: per-champion camp claims (sf_base).
- Byte 7: sf_pvp's focus byte. `read_claims` loops over `range(FOCUS_BYTE)`.
- Byte 6: free.

## Evaluation (final bot = s5)
- **(a) Sprint vs sf_bank, 40 games** (`matches/tb_merge_b-final-vs-bank`):
  `SUMMARY tb_merge_b vs sf_bank: 37W-3L (92%)  avg gems 871 vs 213  avg deaths 5.2 vs 18.0  botFaults(A) 0`
  - Losses:
    - 02guardians A: 0-0, lost on the gold tie-break. sf_bank also loses this map.
    - 01concentrated-wealth on both sides: 386-1026 and 416-1016.
  - The same run on s4 (before the stun guard) went 35W-5L (88%) (`matches/tb_merge_b-final-vs-bank-s4`).
- **(c) Metrics** for (a), from `postmortems/match_metrics.py`, per game:
  | Metric | Per game |
  |---|---|
  | fuelExhausted | 77.3 (sf_bank 384, sf_base about 237, sf_pvp 295) |
  | botFault | 0 |
  | mean tribute | 23.4 |
  | deaths_by_champion | 4.8 |
  | deaths_by_camp | 0.5 |
  | gemsLost_to_champion | 36.4 |
  | gemsLost_to_camp | 1.9 |
  | wards | 446 |
- **(b) Quick vs tb_aggro:**
  `SUMMARY tb_merge_b vs tb_aggro: 24W-0L (100%)  avg gems 1001 vs 177  avg deaths 4.0 vs 31.7  botFaults(A) 0`
  - sf_bank got 19W-5L on this set, and sf_pvp v2 got 22W-2L.
- **Extra, quick vs tb_economy:**
  `SUMMARY tb_merge_b vs tb_economy: 23W-1L (96%)  avg gems 1024 vs 199  avg deaths 2.0 vs 44.5  botFaults(A) 0`
  - The only loss was 01islands B, 890-1016.
- **(d) Platform mode:** `./cli/cambc run tb_merge_b sf_base --map 02crossing --release`.
  - We won 1002-71 by reaching 1000 gems in round 997. Kills were 28-5.
  - **Crashes: 0 for both teams.** No `bot error` lines appeared in stdout.

## Known risks
- **fuelExhausted is not at sf_fuel's level.** It is 77-105 per game, against 6.5 for sf_fuel alone.
  - Most of it is on 00lanes (about 800 per game in s4) and 00gemfight. Profiling 00lanes gave, per turn:
    - `choose_target` 550-650k;
    - `observe` 460-540k;
    - `threats` 300-400k (the ward vision adds camps and enemies to scan);
    - sf_bank's `update_alerts` about 85k;
    - sf_pvp's `try_ward` about 40k.
  - Raising `FUEL_SCORE_FLOOR` or caching `update_alerts` are the obvious next steps. Neither was measured.
- **01concentrated-wealth is lost on both sides against sf_bank.** We die 7-14 times against their 4, and submit fewer
  gems in a farming race. It is probably the sf_draft roster (Vesper, Vendetta, Marcella, HoR, Ryth) or the HoR slot on
  this map. Not investigated.
- **The self-play A/B against sf_bank overstates the gain.** sf_bank lacks sf_pvp's lock-avoidance fix, so it stalls at
  our proactively locked altars. The tb_aggro and tb_economy cross-checks are the more honest numbers.
- **Combined aggression.** The pvp bias stacks on sf_bank's limit, so a channelling, focused carrier can be engaged at a
  ratio up to 1.75 (0.85 + 0.4 + 0.3 + 0.2). A bot that cancels its tribute to fight back could punish this. Lower the ratios in `focus_bias` if
  ladder replays show it.
- **sf_bank's census thresholds use only enemies within `ENEMY_SIGHT` (8).** sf_pvp's `threats()` filter drops
  ward-only sightings, so `last_enemy_near` (14 tiles) and `altar_seen` see fewer enemies than in sf_bank alone.
  This is mildly less conservative banking.
