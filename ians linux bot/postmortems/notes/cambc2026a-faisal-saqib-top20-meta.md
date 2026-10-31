# CambridgeBot (Faisal-Saqib): 2026a strategy docs and a top-20 ladder census

- **URL:** https://github.com/Faisal-Saqib/CambridgeBot (docs index at https://github.com/Faisal-Saqib/CambridgeBot/tree/main/docs)
- **Key docs read:** `docs/TOP20_STRATEGY_CENSUS.md`, `docs/TOP20_DEEP_ANALYSIS.md`, `docs/TOP_TEAM_FINDINGS.md`, `docs/TOP_TEAM_OBSERVATIONS.md`, `docs/MAP_FINDINGS.md`, `docs/FULL_STRATEGY.md`, `docs/TOP20_MAP_TARGETS.md` (skimmed; 97 KB per-map breakdown)
- **Raw copies:** `../raw/cambc2026a-faisal-saqib-*.md`
- **Event:** **Cambridge Battlecode 2026a (cambc2026a), the same game we are playing.** The docs date from 27-28 Oct 2026.
- **Team / placement:** The repo author's bot is mid-ladder. It went 4/10, 2/10, 5/10 and 3/10 in batches of ten online games, and its live v24 is experimental. **Its own strategy is not a winning reference.** The valuable part is that **they downloaded about 1,040 to 1,124 ranked match summaries of the top-20 teams and measured what those teams do.** These are observational statistics, not causal proof.
- **Same game as cambc 2026a?** **Yes.**

## Game summary
This is the champion/MOBA-style game: draft 3 to 5 champions, kill neutral camps, capture camp regions for gems and gold, tribute gems at altars (first to 1,000 tributed gems, otherwise the most tributed gems at round 2000), with per-champion vision, 8 bytes of shared memory and fuel limits. The repo's bot is Rust (and earlier C++). It has a `scripts/gauntlet.py` that plays every map from both sides.

## Meta: what the top 20 actually do (census of 1,869 top-20 team-games)
How many of the 20 teams do each of these *habitually*, meaning in at least half their games:
- **Regular ward placement: 20/20.** Top teams average roughly 86 to 202 ward placements per game, and every champion has about 17 to 29 wards per game. Warding nearly every time it recharges is standard.
- **Low carried-gem loss: 20/20.** Lost carried gems stay at or below 15% of submitted gems, and these games had a 67% win rate. Protecting carriers and banking early is universal among strong teams.
- **One champion captures while the others zone or farm: 19/20.** Single-recipient capture rates are 89 to 98% for almost every top team. Don't stack the whole team on a capture tile.
- **Bruiser-family stat builds: 18/20** (58% win rate). Bruiser Strength, Bruiser Health and Bruiser Focus dominate purchases for every popular champion.
- **Altar locks: 12/20** habitual and 14/20 ever. Some teams use 5 to 10 per game (meow 10.4, new team(4) 10.1, Claudus Maximus 8.3).
- **Teleport crystals: 9/20** habitual and 17/20 ever.
- Rare or losing patterns: Jungle, Treasure, Prospector, Durability, Capture and Monster family builds are almost never habitual and have **low win rates (12 to 34%)**. Small frequent tributes (mean under 25 gems) won only 35%. Linked-pair drafts (Cassi and Issac) were habitual for only 1/20, though they won 60% in the games where they appeared.
- Early aggression (3+ kills before round 200) was never habitual but won **80%** of the 224 games where it happened. This is a possible edge, but it could be a selection effect.

## Team-level numbers (recent 100 games per top-20 team)
- Top win rates: Mite 67%, Intercontinental Fish 62%, Jupiter 60%, German Empire 59%, newer team 57%, NEETCoders 57%.
- Typical per game: about 3 to 10 kills, 4.5 to 12 deaths, **camp deaths of only 0.2 to 1.8** (top teams almost never die to camps), 680 to 850 gems submitted, **mean tribute size about 32 to 56 gems** (they carry 30 to 50 then bank), 2.4 to 3.4 credited attackers per kill (group kills), the top earner holding 41 to 56% of team gold, and farm spread of 12 to 24 tiles (spread out, not one blob).
- Wins tend to arrive around rounds 940 to 1150, by reaching 1,000 gems rather than going to round 2000.

## Draft meta (most common top-20 drafts)
- The core is nearly universal: **Heart of Ruin, Marcella, Vendetta and Vesper Vale** appear for all 20 teams. **Ryth** is common (17 teams).
- Typical 5-picks: HoR + Vesper + Vendetta + Marcella + Ryth (procless, NEETCoders, print dont int, meow, Jupiter, German Empire), or with Tavi in place of Ryth (Mite, the top team). Ad Astra uses HoR + Varg + Marcella + Vesper + Ryth. Intercontinental Fish uses Vesper + Vendetta + HoR + Cassi&Issac + Marcella.
- Rarely picked: Stellar (3 teams), Ren (4), Prism (5), Willow (6), Cassi&Issac (7), Tavi (9), Varg (10).
- Gold and damage share: Marcella (30% gold, 28% damage) and Vesper (27% gold, 25% damage) are the carries. HoR and Vendetta take about 14 to 15% each. Ryth takes about 7 to 9% (a frontline anchor).
- Builds: Vesper is overwhelmingly Bruiser Strength, then Bruiser Health, then Power Strength. Marcella splits Bruiser Focus, Health and Strength. HoR takes Bruiser Health or Focus, and sometimes Jungle Focus. Vendetta takes Bruiser Strength, Health, or Jungle Strength. Ryth takes Bruiser Health.

## Strategy observations from scouting individual top-team games
- **Concentrate gold on a carry.** Ad Astra's Vesper earned 64 to 74% of team gold in its wins and dealt up to 81% of champion damage. This came from farming as well as kills. It isn't universal: Mite spreads gold evenly. There is no gold-transfer action, so concentration has to come from routing captures to the carry, since rewards are split only among allies standing on the tile at completion.
- **Group fights, solo captures.** Intercontinental Fish had 4 to 5 credited attackers on 17 of 18 kills, yet a single capture recipient on 15 of 19 captures. Fight as a pack, then let one champion capture while the others guard or move on.
- **Focus is kit-dependent.** Vesper has no Focus-scaled damage, so buy Strength. HoR's shield and dash scale with Focus. Marcella has both an attack reset and a 2xFocus spell, so it's a judgement call.
- **Map-dependence is huge.** The same bot went 5-0 on expanse (spread farming, almost no deaths) and 1-4 on the_line, where one harmless jackpot group holds 161 of 193 gems and the game becomes a brawl over it and its single altar. Starfish lost about 1,800 gems to champion kills. Treasure_box showed 618 fuel-exhaustion events in 5 games.
- Per-map census examples: on 00ambush top teams farm very wide (30-tile spread) and use many locks and crystals. On 00anvil they concentrate on a carry, kill more, and use locks.

## Their bot's design (v20 to v24, Rust): useful mechanics even though it isn't a top bot
- **Farming job score** = value / time / n, where n is the number of champions on the group. Value = gems + gold x w, with w decaying from 0.15 before round 300 to 0.08 before 800 to 0.03 after. Time = travel + respawn wait + clear time + an HP-cost term (expected damage over 60% of max HP, multiplied by the round trip home) + 6.
- Multipliers: x0.4 on the enemy half (x0.75 after round 250), x0.6 near recent enemy sightings, x0.5 near a recent death, and x1.25 hysteresis for the current job. Re-choose every 5 rounds. Harmless clusters within 5 tiles are chained together. Join caps depend on group HP.
- **Jackpot rule:** if a group holds at least 60 gems and at least 35% of the map's gems, every champion within 12 tiles stands on it and the team banks together. "Brawl maps" (one harmless jackpot with at least 50% of the map's gems) mean aggressive play all game.
- **Monolith-gated altars:** hoard gems, and then from round 200 or once holding 60 gems, set a shared flag, gather 3, kill the gate camp together, and bank.
- **Banking thresholds (v22):** bank at 30 or more gems anywhere, 15 or more if an altar is within 15, 5 or more if within 4. When threatened (enemy seen within 14 in the last 40 rounds, an ally died recently, or HP under 60%), halve those thresholds. Always bank when banked + carried reaches 1000, or after round 1900. Cancel a tribute if nearby enemies would kill us first, unless that tribute wins the game.
- **Fight model:** compare kill times (their total HP / (my damage + allies within 8)) against our time to die. "Losing" if the ratio exceeds 1.3, "clearly losing" if it exceeds 1.6 or we are outnumbered. Retreat when HP < 2.5x incoming damage + 10%. Never run from an adjacent melee champion if you can hit back. Prefer gem carriers as targets, and keep a shared focus target in byte 6.
- **Retreat:** search up to 7 steps for a tile outside all threat ranges. Recall when out of danger and more than 6 tiles from spawn. Heal on spawn to 97%.
- **Shared memory layout:** bytes 0 to 5 hold each champion slot's claimed camp group, byte 6 the team focus target, byte 7 flags (monolith gate, support-leader slot, alert generation).
- **Fuel:** precompute static distance maps (to every camp group, altar and spawn) outside the hot path, spend spare fuel precomputing more, and stop job scoring early when fuel is low.
- **Stuck guard:** after 6 turns with no action, skip that altar for 40 rounds or that camp for 30.

## Testing & dev workflow
- Each tweak needs at least 5 to 10 completed **online** matches before the next change, because local results were often misleading (for example, a local 52% screen did not hold up online).
- Unranked scrims only against teams currently in the top 20. They respect the 50 match-groups per hour quota (5 games per group).
- They **download ranked match summaries of top teams** and compute per-team and per-map statistics: draft, item spend, wards, locks, crystals, capture recipients, gem-loss causes, and death causes (camp versus champion).
- Track metrics beyond win rate: carried-gem loss, tribute size and count, deaths by cause, fuel exhaustion and bot faults.
- A gauntlet script plays every map from both sides against a fixed baseline. They keep rollback baselines.

## Mistakes / regrets
- Rigid whole-team cohesion (everyone within 2 to 3 tiles) went 19/280 locally and was rejected. Their "regroup" variant v23 went 3/10 online. Forced formation costs too much farming.
- A ward experiment (v21) went 2/10 and was rejected, even though every top team wards heavily. Their placement logic was probably the problem, not warding itself.
- Concentrated-gold carry (Ad Astra style) lost 0-1046 on the_line, so a carry isn't map-proof.

## Takeaways for us
- Draft the meta core (HoR, Marcella, Vendetta, Vesper, then Ryth or Tavi) unless we have tested a counter.
- Buy Bruiser emblems and skip Jungle, Treasure, Prospector, Capture and Monster.
- Ward every time it's ready, at altars and on the approaches.
- Bank at 30 to 50 gems, earlier when threatened, and escort carriers.
- Fight as a group but capture with one champion.
- Detect map archetypes (jackpot/brawl, monolith gate, open spread) and switch profiles.
