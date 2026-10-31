# sf_bank: banking, camp safety and the fight/flee model (INSIGHTS items 2, 3 and 9)

Base: `bots/sf_base` (a frozen copy of tb_splitfarm). Only `src/bot.py` changed.
- Every new tunable is a module constant in a commented `sf_bank:` block at the top of the file.
- Every new method sits in a `# --- sf_bank: ...` section or has an `sf_bank` comment.
- No existing code was renamed, reordered or reformatted. `altar_distance()` is now unused but was left in place to keep the diff small.

Patch: `matches/patches/sf_bank.patch` (`diff -ruN bots/sf_base/src bots/sf_bank/src`).
Snapshots of every version are in `matches/sf_bank-snap/v1_bank ... v6_chaseguard`.

## Final result
Final A/B (v6, `--maps sprint`, 40 games, tag `sf_bank-final`):
`SUMMARY sf_bank vs sf_base: 33W-7L (82%)  avg gems 785 vs 302  avg deaths 5.0 vs 25.1  botFaults(A) 0`

| metric (per game, same 40 games) | sf_bank | sf_base |
|---|---|---|
| gems submitted | 785 | 302 |
| mean tribute | **21.7** | 20.0 |
| tributes / game (under 10 gems) | 36.2 (4.4) | 15.1 (3.1) |
| deaths by champion | **4.3** | 24.4 |
| gems lost to champions | **20.5** | 66.6 |
| deaths by camp | **0.7** | 0.8 |
| gems lost to camps | 1.9 | 1.9 |
| fuelExhausted | 384 | 237 (*) |

(*) We are alive for many more turns (sf_base spends about 25 x 60 champion-rounds dead), and dead turns are cheap.
Losses: 02guardians on both sides (0-0, lost on the gold tie-break), 01big-world on both sides (650-844 and 632-796, a pure
farming race with 1-3 deaths, so a likely farming or fuel cost on 100x100 maps that we did not investigate),
and 00quadrants B, 01islands B and 01concentrated-wealth B.
Reference baseline: sf_base vs starter = mean tribute 18.9, deaths_by_camp 1.4, gemsLost_to_champion 13 per game.

**Honest note on mean tribute:** the top-20 target of 32-56 was **not** reached (21.7). The literal census rule
(halved thresholds whenever an enemy was seen in the last 40 rounds) keeps firing in fight-heavy games.
Raising `BANK_ANY`/`BANK_NEAR` or setting `BANK_THREAT_LOSING_ONLY = True` are the obvious next
experiments; neither was measured.

## Changes, in the order they were made and measured
All A/B runs used `tools/eval.py ... --maps quick --jobs 3` (24 games). Metrics come from a
two-sided copy of `postmortems/match_metrics.py` (A = sf_bank, B = sf_base in the same games).
**Self-play note:** sf_base against itself is a snowball coin-flip. One side kills the other
10 to 50 times, and the outcome is set mostly by which side the bot plays (ab1: 00anvil was won by team A
from both sides, while 00gemfight and 01elk-arena were won by team B from both sides). The fight model is what breaks that symmetry.

### 1. Census banking rule (item 2) [kept, but see 3]
- `update_alerts()` records three things: the last round an enemy was seen within 14 tiles, the last
  round an enemy was seen within 8 tiles of each altar, and ally deaths. Ally deaths are an alive-to-dead
  transition over `cambc.champions(ALLY)`, including our own death. `threatened()` is true when an enemy
  was seen in the last 40 rounds, an ally died in the last 100, or HP is under 60%.
- `bank_now()` banks at 30 gems or more anywhere, 15 or more within 15 tiles, and 5 or more within 4.
  The thresholds are halved when threatened. Banking is also forced when banked plus carried reaches
  1000, from round 1900, and by the old end-of-game timing rule.
- `pick_altar()` picks the nearest altar by path. It skips enemy-locked altars and adds 12 to the
  distance of altars where enemies were seen in the last 40 rounds. `do_tribute(me, pref)` walks to that
  altar's ring, falling back to every altar if the ring is blocked.
- Measured on its own (ab1): **9W-15L (38%)**, which is self-play snowball noise. Mean tribute was **18.1 vs 19.6**,
  and tributes under 10 gems were 4.0 vs 4.8 per game. On small maps the rule "within 15 tiles and 15 gems"
  fires constantly, and the threatened halving is on most of the time in fight-heavy games,
  so the literal rule does not raise tribute size.

### 2. Kill-time-ratio fight/flee model (item 9) [kept: the big win]
`handle_enemies()` decision part plus the helpers `enemy_dps`, `champ_dps`, `recall_safe`,
`adjacent_melee` and `strike`:
- ratio = (target HP / (our champion damage + 0.7 x the strength of allies within 4) + 0.5 x approach turns)
  / (our HP / (the damage of every enemy within 6 + awake camps hitting us)).
  Enemy damage is estimated as Strength + 0.15 x Focus. Our damage is Strength plus ability damage / 8,
  without the Monster bonus.
- Engage when ratio <= 0.85. The threshold is 0.7 when we carry 30 gems or more, and gets +0.15 when the
  target carries 15 gems or more. We also engage when the target dies to one hit in range.
  sf_base engaged anything within 6 tiles that could not yet hit it.
- **Clearly losing** means ratio > 1.6 (> 1.0 when carrying 30 gems or more), or more enemies within 6
  than us plus our allies. When clearly losing and outnumbered or rich, we step away before contact.
- **Never turn our back on an adjacent melee enemy we can hit.** Melee can walk and attack in the same
  turn, so fleeing only gives it free hits. We stand and trade unless we are clearly losing and a dash
  or our spawn (2 tiles or closer) offers a real escape.
- Recall only when every visible enemy is farther than its range + 4, both in the enemy branch and in the
  general "low HP / rich" recall. Otherwise we walk toward spawn. Damage cancels a recall.
- `retreat()` tie-breaks: after camp danger, it prefers tiles away from enemies, then tiles toward our
  spawn. Dash is only used when the first three keys improve.
- ab2 (1+2): **22W-2L (92%)**, gems 897 vs 220. Champion deaths fell from **29.0 to 3.5** per game for
  us against them, and gems lost to champions from **79.0 to 14.4** per game.

### 3. Detour-aware banking (item 2 refinement) [kept]
"Within N tiles" is measured as the **detour**: path to the altar + Chebyshev distance from the altar to
the next target − path to the target. So we bank when the altar is on the way.
- Rules: 30 or more gems anywhere; 15 or more if the detour is 8 or less; 5 or more if the detour is 3 or less.
  The thresholds are still halved when threatened.
- Set `BANK_DETOUR = False` to get the literal census rule back.
- ab3 (1+2+3): **24W-0L**. Mean tribute rose from **18.4 to 20.8** and tributes per game fell from
  48.7 to 41.4 (fewer altar trips). Gems were 863 vs 193.
- `BANK_THREAT_LOSING_ONLY` (default False) is an untested option that counts an enemy sighting as a
  threat only when the fight model would not engage.

### 4. Camp safety (item 3) [kept]
- `escape_ok(G, comp)`: hit-and-run attrition (the multi-cycle branch of `choose_target`) is only allowed
  when the component we attack from has a walkable tile outside the group's attack range.
  On 01islands, champions of both bots kept dying to the same elk next to a small island
  (5 camp deaths per game for us in ab2's 01islands A game).
- Death memory: the group we were targeting when we died gets x0.3 score for 250 rounds.
  This stops repeat deaths at the same spot, whatever the killer.
- In the camp-danger retreat, an adjacent melee enemy that dies to our next hit is finished instead of fled from.
- 01islands single game: 1 camp death, against 5 in ab2's game. ab4 (1-4): **23W-1L**, gems
  **966** vs 183, camp deaths 0.7 vs 0.8 per game, champion deaths 3.2 vs 32.5.

### 5. Stall breaker [kept, neutral]
If we keep stepping away from enemies we are not clearly losing to, the `self.stall` score
(+1 per retreat, x0.98 per turn) goes above 25. We then hold our ground and keep farming or banking,
with hysteresis down to 10. ab5: **23W-1L**, gems 970 vs 200 (neutral, kept as a safety net).

### 6. Chase guard [kept: fixes a reproducible 0-gem game]
In the v4 cross-check against tb_economy, 00anvil (team A) ended **0-720**. Reproduced and instrumented,
it turned out tb_economy parks 2 to 4 champions on the gem-cluster tiles next to the map's only altar.
Our champions "engaged" one that they could never reach, alternating each turn between chasing it and
walking to the altar, and carried 23 gems for 1,800 rounds. Now an enemy that we engage for 6 turns
without landing a basic attack is ignored for 40 rounds. The same game becomes **1044-205**.
The engage no-op is inherited from sf_base's engage branch.

## Cross-checks against other opponents (quick, 24 games)
- **Final v6** `sf_bank vs tb_economy`: `SUMMARY sf_bank vs tb_economy: 21W-3L (88%)  avg gems 931 vs 360  avg deaths 3.1 vs 45.0  botFaults(A) 0`.
  00anvil A is now won (it was the v4 stall). The 3 losses are listed in `matches/sf_bank-xeco2.log`.
- **Final v6** `sf_bank vs tb_aggro`: `SUMMARY sf_bank vs tb_aggro: 19W-5L (79%)  avg gems 819 vs 534  avg deaths 8.9 vs 30.2  botFaults(A) 0`.
  sf_base got 9W-15L (38%). 02the-pond is lost on both sides against tb_aggro, and 01islands is weak against both opponents.
- `sf_bank vs tb_economy`: **21W-3L (88%)**, avg gems 916 vs 373, deaths 3.2 vs 43.7.
  sf_base / tb_splitfarm on the same 12 maps got 18W-6L (75%), from `matches/rr-tb_splitfarm-vs-tb_economy`.
- `sf_bank vs tb_aggro`: **18W-6L (75%)**, avg gems 827 vs 486, deaths 8.4 vs 28.9.
  sf_base got 9W-15L (38%), from `matches/sf_pvp-baseline-xag.log`.

## Independent / optional parts of the patch
- **Banking** (items 1 and 3 above) is independent of the fight model. It consists of the constants
  `BANK_*`/`ALTAR_DANGER_PEN`, `update_alerts`, `threatened`, `pick_altar`, `detour`, `bank_detour`,
  `bank_now`, the `pref` argument of `do_tribute`, and the tribute block in `play_turn`.
  `update_alerts` is also called in the dead branch.
- **Fight model** (2, 5 and 6) lives in `handle_enemies` and its helpers.
  The `recall_safe` guard on the general recall in `play_turn` and the `retreat()` tie-breaks can be
  taken separately.
- **Camp safety** (4) is `escape_ok`, the death memory (`died_at`, `was_dead`, a penalty line in
  `choose_target`) and the finish-kill in the camp-danger block.
- **Shared memory:** not touched (claims stay in bytes 0-7 as in sf_base). All new state is per champion.
