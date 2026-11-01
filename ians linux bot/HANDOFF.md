# Handoff: Turbo Recallers Python bot (cambc 2026a)

_Last updated: 2026-10-31 ~20:15 EDT, at the handoff from the dev PC to the cluster agent. This is the history and reference document. **For what to do next, start at `results/STATUS.md` → "Resume here" and the protocol in `LOOP.md`.** The standing user instructions are in the repo-root `CLAUDE.md`._

## 1. Where things stand
- **Live submission:** `tb_merge_b` (website v2) is selected for Sprint 3; see §3. The current champion bot is named in `results/CHAMPION` (= `tb_merge_b`).
- **Upcoming events** (check https://2026a.battlecode.co.uk/game/tournaments for exact lock times): International qualifiers on 4 Nov, UK qualifiers on 11 Nov, in-person finals on 18 Nov at the Cambridge Union. All sprints and tournaments use **unseen maps**.
- **Ladder context** on 31 Oct: 815 ranked teams. The top 10 are almost all C++, rated about 2,300–2,650.
- **Reality check from the real ladder:** v1 (`tb_splitfarm`) went from 1,500 to **1,410** over its first 13 ranked match sets on 31 Oct. It won **3 sets and lost 10**, with five 0–5 losses against teams rated about 1,400–1,500 (FürFortnite, LigaSiur, Hammer Method, Patient Wolves, mostly harmless).
  - It beat the starter 100% locally, so **our local self-play numbers overstate real strength a lot.**
  - `tb_merge_b` (v2) then went **43W-17L** (72%) on the ladder, rating 1,407 → ~1,491 (plateau). Weak spots: 3-pick maps (6/12), 0-0 gold tiebreaks (02the_pack), and **mirror-meta teams at ~1,500** that play our exact draft better. Details: `results/ladder-analysis-2026-10-31.md`, `results/ladder-games.jsonl`.
- **Our bot lineage:**
  1. `starter-python`, the official starter. It dies about 28–35 times per game.
  2. Builder round: four independent designs. NOTES.md in each bot dir explains its design and lists hard-won engine facts. Results on 20 sprint maps × both sides vs starter-python:

     | bot | result | avg gems | avg deaths |
     |---|---|---|---|
     | `tb_deathball`: team ball / two squads, leader picks the target via shared memory | 40-0 | 901 vs 144 | 3.7 |
     | `tb_splitfarm`: parallel farming, per-champion claims, TP-crystal island crossing | 40-0 | 878 vs 152 | 3.3 |
     | `tb_economy`: draft, items and ability focus | 38-2 | 879 vs 173 | 12.7 |
     | `tb_aggro`: farming plus punishing enemies | 37-3 | 744 vs 185 | 2.4 |

  3. `sf_base` is a frozen copy of `tb_splitfarm`, the baseline for the improvement round.
  4. Improvement round: five agents each patched a copy of `sf_base` (`sf_fuel`, `sf_bank`, `sf_draft`, `sf_pvp`, `sf_maps`). Patches are in `matches/patches/` (gitignored) and also in each bot's CHANGES.md. See §4.
  5. Merge round: `tb_merge_b` is the final Sprint 3 bot. See §4.

## 2. Round-robin among the builder bots (sprint maps, 40 games per pair)
```
SUMMARY tb_deathball vs tb_splitfarm: 12W-28L (30%)  avg gems 502 vs 746
SUMMARY tb_deathball vs tb_aggro: 14W-26L (35%)  avg gems 523 vs 747
SUMMARY tb_deathball vs tb_economy: 21W-19L (52%)  avg gems 694 vs 642
SUMMARY tb_splitfarm vs tb_aggro: 19W-21L (48%)  avg gems 604 vs 620
SUMMARY tb_splitfarm vs tb_economy: 30W-10L (75%)  avg gems 817 vs 423
SUMMARY tb_aggro vs tb_economy: 28W-12L (70%)  avg gems 732 vs 499

win% (row vs column)
               tb_deathba tb_splitfa   tb_aggro tb_economy
tb_deathball            -        30%        35%        52%
tb_splitfarm          70%          -        48%        75%
tb_aggro              65%        52%          -        70%
tb_economy            48%        25%        30%          -

RANKING
  tb_splitfarm     77/120  wins (64%)  avg gems 722
  tb_aggro         75/120  wins (62%)  avg gems 700
  tb_deathball     47/120  wins (39%)  avg gems 573
  tb_economy       41/120  wins (34%)  avg gems 521

```
Conclusion: tb_splitfarm (64%) was chosen as the improvement base. tb_aggro (62%) is close and wins head-to-head 21-19; its fight/retreat logic is worth grafting.

## 3. Submissions (website version history)
| Version | Bot | Note | When |
|---|---|---|---|
| v1 | tb_splitfarm (= sf_base) | interim; split-map farmer with TP crystal crossing. Verified on the platform | 31 Oct 19:31 UTC |
| v2 | **tb_merge_b** | final Sprint 3 bot: splitfarm + fight/flee, banking, pvp focus/locks, meta draft, fuel cache. Selected for the next match | 31 Oct 21:42 UTC |
| v3 | **q24_combo** | tb_merge_b + lock memory, gold tiebreak, group fights, fuel cache. Full gate pass: 87/140 vs tb_merge_b, gauntlet 174/200 (`results/experiments/2026-11-01-q24_combo.md`) | 1 Nov 01:24 UTC |
| v4 | **c2_respawn** | q24_combo + respawn-rule freeze fix. Full gate pass: 89/140 vs q24_combo, gauntlet 177/200, 98/140 vs tb_merge_b (`results/experiments/2026-11-01-c2_respawn.md`) | 1 Nov 04:36 UTC |

`sf_bank` was bundled as an interim upgrade but never uploaded: browser access to the site dropped for a while, and the merge finished first. Zips are in `submissions/` (gitignored).

## 4. Improvement round and merge
Five agents each patched a copy of `sf_base` (`tb_splitfarm`) along one dimension. Each bot dir has CHANGES.md with per-change measurements; the patches (gitignored) are in `matches/patches/`. Results vs sf_base on sprint maps (40 games):

| Bot | vs sf_base | Cross-checks (quick, 24 games) | What it adds |
|---|---|---|---|
| `sf_bank` | **33W-7L (82%)** | 79% vs tb_aggro, 88% vs tb_economy | **Kill-time fight/flee model** (champion deaths 24 → 4 per game), detour-aware census banking, camp-escape safety, stall breaker, chase guard |
| `sf_pvp` | **31W-9L (78%)** | 92% vs tb_aggro, 92% vs tb_economy | Focus on channelling enemies and gem carriers, shared focus target in shared-memory byte 7, stuns to break channels, reactive and proactive altar locks, avoiding locked altars, wards |
| `sf_draft` | 29W-11L (72%) | 88% vs tb_economy | Meta draft (Vesper, Vendetta, Marcella, HoR, Ryth), Bruiser item builds, HoR landing-dash aim, AoE aim, re-target after attack reset |
| `sf_fuel` | 24W-16L (60%) | 83% vs tb_economy | Static distance-field cache, pruned exact target scoring, fuel guards. fuelExhausted down from 180 to 6.5 per game |
| `sf_maps` | 21W-19L (52%), neutral | — | Map-archetype profile in draft memory (jackpot / gated / herd). Not merged; ideas kept for later |

Lessons from the round:
- Literal census banking alone *lost* (9-15). Banking only helped once fights were won.
- The single capture recipient and the item-13 scoring multipliers both lost and are shipped OFF.
- A "travel dash" lost (dash on cooldown when enemies appear).

**Merge round:** three independent merges (`tb_merge_a`: bank→pvp→draft→fuel; `tb_merge_b`: pvp→bank→draft→fuel; `tb_merge_c`: bank→draft→fuel), each validated against `sf_bank`. Results below.

### Merge results (31 Oct, ~17:30 EDT)
| Merge | Patches | vs sf_bank (sprint, 40) | vs tb_aggro (quick) | fuelExhausted/game |
|---|---|---|---|---|
| `tb_merge_a` | bank→pvp→draft→fuel, plus a FUEL_KEEP_TARGET guard | 37W-3L (92%) | 24W-0L | 67 |
| **`tb_merge_b`** | pvp→bank→draft→fuel, plus a fix for the stun-target-left-vision crash | **37W-3L (92%)** | **24W-0L** (also 23W-1L vs tb_economy) | 77 |
| `tb_merge_c` | bank→draft→fuel, no pvp, plus a custom draft order | 30W-10L (75%) | 22W-2L | 27 |

Round-robin among the merges (`results/roundrobin-merges-2026-10-31.txt`): **tb_merge_b 68%**, tb_merge_a 64%, tb_merge_c 19%. tb_merge_a vs tb_merge_b went 20-20.
**tb_merge_b was chosen as the final Sprint 3 bot.** Its NOTES.md explains how each conflict was resolved: sf_bank's kill-time model decides fights, and sf_pvp's focus and channel bias is layered on top.

**Robustness check on all 70 local maps × both sides vs sf_bank:** `125W-15L (89%)`, avg gems 840 vs 251, deaths 6.5 vs 16.4, botFaults 0. Metrics: mean tribute 27.0, camp deaths 1.0/game, fuelExhausted 81.5/game, 380 wards/game, 7.4 consumables/game. Log: `matches/final-mergeb-all.log` (gitignored).

## 5. Known weaknesses and next steps (prioritised)
**Superseded:** the live queue and verdicts are in `results/STRATEGIES.md`, and the immediate resume list is in `results/STATUS.md`. In short:
1. **Q24 combined candidate:** the lock-memory bug fix + gold-tiebreak play + early-fight rule + fuel caching from strategy batch 1 (`results/experiments/2026-10-31-batch1-interim.md`). Build it, analyse it, gate it.
2. **Learn from the real ladder (Q14, Q19):** download our losses (`cambc matches summary/download`), run `tools/analyze_match.py` on them, and find how the mirror-meta teams out-play us.
3. **Map structure (Q20-Q22):** teleport into wolf-ringed altars, fix the respawn-rule freeze, rush open gates.
4. **Fuel (Q25)** and the **C++ track** (`bots/cpp_port`, at parity, 0 exhaustions).

## 6. Overnight improvement protocol (superseded by `LOOP.md`; kept for reference)
For reference, one 2000-round Python game took about 10–20 s of wall time on the 16-core dev PC (24-game eval with `--jobs 6` ≈ 50 s). Use `docs/CLI_ONLY.md` for the browser-free equivalents of site tasks.
1. `CHAMP=$(cat results/CHAMPION)`. Copy it to a new bot: `python3 -I tools/newbot.py $CHAMP <cand>`, which copies it without its build cache and validates the names.
2. Make **one** focused change, taken from §5 or from replay or metric analysis:
   - `python3 tools/eval.py <cand> $CHAMP --maps quick --keep --tag dbg`
   - Then read the replay zip's `team-a.stdout`, and use `postmortems/match_metrics.py matches/dbg`. Death events name the killer.
3. Screen: run `tools/eval.py <cand> $CHAMP --maps quick` (24 games). Drop the change if it scores under 50%.
4. Confirm: run `tools/eval.py <cand> $CHAMP --maps sprint`. Accept at ≥ 55% with `botFaults 0`. For anything touching movement or draft, also run `--maps all` (140 games).
5. Gauntlet: `python3 tools/gauntlet.py <cand> --maps sprint` (logs to `results/gauntlet.jsonl`). It must not regress against the rest of the pool.
6. Promote: write the bot name to `results/CHAMPION`, add a line to §3/§4 of this file, then commit and push to `ians-linux-bot`.
7. Every few hours run `./cli/cambc maps pull`. New maps resemble upcoming unseen maps, so add them to the eval set.
8. **Do not submit to the platform without the user's go-ahead** (it changes the team's live bot). Bundle with `./cli/cambc bundle <bot> --output submissions/<bot>.zip` and leave it ready.

## 7. Engine / API facts that bit us (details in the bots' NOTES.md and the skills)
- **Spawn tiles:** standing on a spawn tile of a respawning camp group blocks its respawn forever. Never idle on camp spawn tiles unless capturing.
- **Group state:** `CampGroup.state()` can say Alive while none of its camps are visible. A group stays Alive until *every* member is dead; path to the live camps, not to a dead member's tile.
- **Bushes:** camps in bushes are invisible from outside, and moving onto a hidden occupant returns False every turn without raising (infinite loop risk).
- **Recall:** damage cancels a recall. Step out of every awake camp's range (3/4/4/5) before recalling. Camps don't chase, don't regenerate while asleep, and go back to sleep after 2 rounds with no champion in range.
- **Pathing:** `vision.champion_tiles()` includes allies, so treating allies as walls deadlocks corridors. `DistanceField.get()` returns 65535 for unreached tiles; use the `visited` bitboard for reachability.
- **Attack resets** raise until you have basic-attacked this turn.
- **`move_towards(t)`** raises when `t` is occupied and you are adjacent.
- **Shared caches:** never mutate cached boards (`walls()`, `altars()`, `spawn_region()`, `spawn_tiles()`).
- **Draft memory** is 1,024 zero-padded bytes; Python state from the draft does not reach champions. Shared memory is 8 bytes for the whole team for the whole match.
- **Fuel budget:** 250M on the first draft turn, 5M on the first play turn, then 2.5M per turn for Python.
- **Bot output:** `print` output exists only inside the replay zip (`team-a.stdout`). `cambc run` does not show it.
- **Tiebreak:** results vary between runs (the engine seed changes), and an exact tie goes to Team B.
