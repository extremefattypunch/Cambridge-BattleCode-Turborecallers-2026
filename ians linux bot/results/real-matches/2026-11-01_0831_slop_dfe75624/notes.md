# vs slop (1574): 1-4, 2026-11-01 08:31 UTC, our v4 (`c2_respawn`)

**Site:** https://2026a.battlecode.co.uk/game/match-groups/dfe75624-e857-4e79-a702-5e1c7f939565
**Data:** `matches/ladder/summary/<matchId>__B.json` for each game (we were team B in all 5); `python3.12 tools/scout.py --group dfe75624-e857-4e79-a702-5e1c7f939565`; `python3.12 -I tools/analyze_match.py` per game.
- **Replays:** in `matches/ladder/replays/<matchId>.repl26a`. Our `team-b.stdout` and `team-b.debug` are empty in all 5 games: no `bot error`, no `submit failed`.
- **Fuel:** fuelExhausted after r1 was 0 for us in 4 games and 1 on fracture (Vesper at r2).
- **Positions:** the summaries hold no per-round positions, so positions come from event coordinates:
  - wards land within 2 tiles of the placer;
  - clears, captures, tributes, shop visits, and kills and deaths are logged where they happen.
- **Map geometry:** from `maps/<map>.map26a` via scout's loader. Throwaway scripts live in the session scratchpad.
- **Evidence and speculation:** unmarked statements come from the data; inferences are marked *speculation*.

## 1. The games played
Slop played the same way on every map:
- **Fighting:** 2-4 champions moved and fought together, and their Vesper Vale took the last hits and snowballed.
- **Farming:** every capture was solo; their 399 captures all had one recipient.
- **Items:** Treasure, then Jungle, then Durability passive emblems, then mass Bruiser shards.

We farmed solo and spread out under our safety model, and we fought only when an enemy reached us. We won only on the map where their carriers had to come to us.

| # | Map | Our side | Result | Gems (us-them) | Rounds | End | Our draft | Their draft |
|---|---|---|---|---|---|---|---|---|
| 1 | 00swirl (45x30, 4 picks) | B | **L** | 30-1008 | 968 | gems | Vesper, Vendetta, Marcella, HoR | HoR, Vendetta, Vesper, Willow |
| 2 | 01fracture (61x71, 5 picks) | B | **L** | 571-1012 | 1400 | gems | Vesper, Vendetta, Marcella, HoR, Ryth | HoR, Vendetta, Vesper, Willow, Varg |
| 3 | 01shortcut (40x40, 4 picks) | B | **W** | 1143-515 | 1725 | gems | Vesper, Vendetta, Marcella, HoR | HoR, Vendetta, Vesper, Willow |
| 4 | 00breadcrumbs (29x29, 3 picks) | B | **L** | 259-1015 | 1028 | gems | Vesper, Vendetta, Marcella | HoR, Vesper, Vendetta |
| 5 | 00ribs (51x85, 5 picks) | B | **L** | 421-820 | 2000 | tiebreak (gems) | Vesper, Vendetta, Marcella, HoR, Ryth | Prism, Vesper, Marcella, Willow, HoR |

Gem race (tributed, us-them) at r250 / r500 / r1000:
- swirl 15-46 / 30-235 / (ended r968, 30-1008);
- fracture 63-54 / 115-130 / 330-430;
- shortcut 0-0 / 186-42 / 370-129;
- breadcrumbs 21-168 / 84-483 / 259-959;
- ribs 0-57 / 21-157 / 321-249.

- **Game 1 (00swirl, L 30-1008).**
  - **The split.** Our 4 champions went to solo targets the safety model accepts:
    - the gold-cluster pairs g21 (24,20) and g9 (36,11); g9 is 7 steps from *their* spawn;
    - the single-elk groups g10 and g11.

    Their Vendetta, Willow and HoR moved together.
  - **The opening fights.**
    - r41 and r47: their Vendetta, with Willow and HoR assisting, killed our Marcella and then our Vendetta at (23,16), next to g11 and 6 steps from our spawn.
    - r94: our Vesper died alone at (37,9), farming g9.
    - r116: our HoR died at (33,24).

    Before r300 we died 7 times and they died once. Gold at r250 was 529-1355.
  - **The spawn camp.** From r343 their group held the ground 1-4 tiles from our spawn. We died at (17,18), 3 tiles north of our spawn, 6 times; there were 4 multi-kill fights; their Vesper went 13/0. Our champions were dead 43-49% of the game.
  - **Their farming.** They took 20 groups on our half for 501 gems, including:
    - g6 (30 gems) at r433;
    - g13 (37 gems, 4 steps from our spawn) at r471;
    - g17 (88 gems) at r824;
    - g15 (44 gems) at r961.
  - **Our banking.** We banked 30 gems in 2 tributes, at r35 and r337. 11 of our 13 captures were worth 0 gems.
- **Game 2 (01fracture, L 571-1012).**
  - **A farming race with few fights.** We died 6 times (2 to camps) and they died twice.
  - **The opening.** Their five champions ran separate solo circuits from r41 and made 16 captures before r300. We made 8, and the first three were shared by 4, 3 and 2 champions: g11's 22 gems were split four ways at r48, and g9's 15 gems three ways at r117.
  - **Gems level, gold not.** Gems were level at r250 (63-54) and r500 (115-130). But they earned 2.2x our gold by r500 (2,058 vs 926) and 1.8x by r1000 (5,264 vs 2,906): 74 clears to our 47, and 29 emblems to our 15 by r1000.
  - **Decisive window, r1000-1400.** They took the 44-59-gem elk groups beside the altars 8 times, all from r1035: g14 x3, g15 x2, g22 x2 and g23 x1, for 427 gems. We took one of them once (g23, r1287).
    - Camp gems in the window: 580 to 167.
    - The gap moved from -100 to -441.
- **Game 3 (01shortcut, W 1143-515).**
  - **The map.** Both altars sit in walled pockets about 45 walking steps from either spawn (scout BFS). From our spawn, (32,12) is two TP-crystal hops away.
  - **Our banking.** We bought 16 crystals and made all 20 of our tributes at (32,12), from r321 (83 gems).
  - **Their banking.** They walked there: 8 tributes, mean 64 gems.
    - **Carrier deaths to camps:** their HoR died to the camp east of the pocket at r245 (57 gems) and r602 (78 gems).
    - **Carrier deaths to us:** our Vesper (8/0) and Vendetta (5/3) killed their carriers on our west flank: (0,0) r193 (28 gems), (1,23) r1025 (77), (7,17) r1036 (63), (4,9) r1512 (78).
    - **Total:** they lost 674 gems on death, 474 to us and 200 to camps. Their Vesper and Willow collected 417 gems and banked none.
  - **Result.** We led from r321 and were 186-42 up at r500.
  - **One execution bug (ours).** Marcella was stranded on the hole-ringed island around g7 from r470 to r928.
    - Her last damage dealt was at r442. Wolf damage stopped at r470, and at r928 she died there to the g7 wolves (camp12) at (19,7), carrying 11 gems.
    - This is the known V3L-2 bug. It is fixed in h_shortcut (T33) but not in v4.
- **Game 4 (00breadcrumbs, L 259-1015).**
  - **The map.** It has only clusters (no camp can hurt anyone) and one central altar at (14,14).
  - **Their loop.** Their HoR looped the six gem clusters 1-3 tiles from the altar and banked after every capture: g0 at r64, banked r66; g4 at r76, banked r80; g1 at r87, banked r89. In total they made 94 tributes averaging 10.8 gems, the first at r52.
  - **Our farming.** We captured the 0-gem gold clusters in the column beside our spawn: 58 of our 109 captures, and 16 of 28 before r300. We carried bags of about 21 gems, with our first tribute at r200.
  - **Their trio.** It killed our champions 12 times and took 98 gems. Their Vesper went 11/0, and HoR and Vendetta both assisted on 7 of those kills.
  - **Result.** We were behind for good from r52.
- **Game 5 (00ribs, L 421-820 on the gem tiebreak).**
  - **The map.** All gems are in one central arena between two altars, 65-73 steps from both spawns: g0 has 14 gems, g1 and g2 have 43 each. The rest of the map is single gold clusters.
  - **Their draft and opening.** They changed draft (Prism, Vesper, Marcella, Willow, HoR) and banked first (r133 vs our r349).
  - **We won the middle game:** 300 tributed gems to their 92 in r500-1000, and 321-249 at r1000.
  - **Their Vesper then took over.** It had been stacking Bruiser Strength from r871. After r1000 it went 15/0, killing our champions one at a time as they arrived at the arena.
    - We died 18 times after r1000; they died 9 times.
    - Ryth lost a 100-gem bag at (23,52) at r1403.
    - They out-tributed us 571-100 in r1000-2000.
  - **Vesper's gold.** Their Vesper finished 24/1, with 3,422 gold from kills alone, more than our whole team earned (3,118).

## 2. Their strategy compared with ours
| Aspect | Opponent | Us |
|---|---|---|
| Draft and each champion's role | **Core:** HoR, Vendetta, Vesper Vale and Willow; Varg added at 5 picks; HoR, Vesper and Vendetta at 3 picks; Prism, Vesper, Marcella, Willow and HoR on 00ribs. **Vesper is the killer:** 49 of their 79 kills on us, 7 deaths, 6,977 gold from kills at 143 per kill (+33% passive, +10% Treasure). **HoR and Vendetta** are the main gem farmers (HoR collected 450, 350 and 543 gems on swirl, breadcrumbs and ribs) and the assisting fighters. **Willow** heals (7,439 HP on swirl, 7,986 on ribs) and farms little. | Fixed `draft.py` PRIORITY: Vesper, Vendetta, Marcella, HoR, Ryth. Every champion is the same solo farmer under the same rules, and fighting is reactive. Our Vesper is a farmer: 0/8, 0/1, 8/0, 1/3 and 4/3. |
| Item build and timing | **A passive emblem first, then stats:** Treasure in the main stat (HoR at r37 on swirl; Vesper at r164-215), then Jungle, then Durability (not Vesper), then Bruiser spam. On swirl they spent 13,050 gold and ended with 32 Bruiser-S, 25 Bruiser-H and 18 Bruiser-F emblems. **Emblems by r1000:** 86, 29, 7, 12 and 12. | **The first purchase is an altar lock** once we hold 40 gold (swirl: HoR at r50, lock plus 4 Bruiser-H shards). We add a TP crystal where crossing is needed, then only Bruiser shards of the main stat. **We never buy Treasure, Jungle or Durability.** Emblems by r1000: 5, 15, 13, 8 and 9. Gold earned over the set: 17,056 vs their 35,346. |
| Farming: which camps, in which order, how many together, tempo | **Strictly solo:** 399 of 399 captures had one recipient. All champions run separate circuits from about r10-40. **Multi-elk groups unlocked mid-game:** swirl's 2-elk groups from r433, fracture's 44-59-gem altar groups from r1035. **On cluster maps they ignore gold:** breadcrumbs HoR earned 60 gold all game and collected 350 gems. Clears per 100 rounds: 5.68, 5.29, 3.48, 16.05 and 2.35. | **Solo farming under the safety model** (`choose_target`), with claim sharing: 22 of our 242 captures were split between allies. **Gold-heavy:** 0-gem captures were 11 of 13 on swirl and 58 of 109 on breadcrumbs. **Multi-elk groups:** almost never; they are rejected unless already claimed. Clears per 100 rounds: 1.55, 3.36, 3.01, 11.19 and 1.0. |
| Tributes: size, cadence, first tribute | **Bag size follows the altar distance:** 94 tributes of 10.8 gems (median gap 7 rounds) at breadcrumbs' central altar; 8 of 64.4 at shortcut's far pocket; elsewhere 26-39 tributes of 26-31 gems. First tribute at r32, r111, r396, r52 and r133. | **Fixed BANK_ANY 30, BANK_NEAR 15, BANK_CLOSE 5 thresholds:** 2x15, 26x22, 20x57, 12x21.6 and 13x32.4. First tribute at r35, r170, r321, r200 and r349. **Lost on death:** 0, 4, 106, 98 and 150 gems. |
| Fighting: when, whom, where (carrier hunting, ganks, spawn camping, altar contests) | **They fight in groups:** 57 of their 79 kills on us had 2 or more of them involved, and Vesper finishes. **Hunting grounds:** our half and around our spawn. On swirl, 9 of our deaths were within 6 tiles of our spawn. **Spawn camping:** breadcrumbs had 5 deaths near our spawn, and swirl's (17,18) saw 6. **They contest our home altar:** on swirl they tributed at our altar (21,19) 12 times. Kills on us: 29, 4, 4, 12 and 30. | **Reactive kill-time-ratio model with carrier priority.** **0 of our 79 deaths were traded:** we made no kill within 8 rounds and 8 tiles of any of them. Kills: 4, 2, 13, 2 and 19. We won fights only where their carriers came to us: shortcut, with 474 gems taken. |
| Map control: wards, altar locks, crystals | **None:** 0 wards, 0 locks and 0 TP crystals in all 5 games. | **1,805 wards. 63 altar locks bought** (630 gold; about 50 placed by bought minus held), with no measurable effect: placements are not logged, and they still tributed 200 times. **21 TP crystals:** 5 on fracture and 16 on shortcut, where they decided the game. |
| Adaptation across the 5 maps | **Same core draft on 4 maps, a different one on the arena map.** Their tribute size adapts to the altar distance. They have no crossing tools, which cost them the walled-altar map. | **Fixed draft, build, bank thresholds and value function.** TP crossing is the only map-driven behaviour, and it won shortcut. |

## 3. Which strategy was superior, and what we learn
- **Overall (1-4):** slop's strategy was superior, and the result came from strategy, not from execution. A team that fights together around a snowballing Vesper and buys passive emblems before Bruiser stacks beat our spread-out solo farmers on every map except the walled-altar one. Our bot logged no errors and at most 1 fuel exhaustion per game, and its one bug (the stranded Marcella) occurred in the game we won.
- **Per game:**
  - **00swirl, theirs, by a rout.**
    - **Early fights:** they won 6-1 in deaths before r300 (7 of ours to 1 of theirs).
    - **Gold:** 529-1355 at r250 and 819-4579 at r500. Their gold came from 4 early kills, then from multi-elk groups unlocked by Jungle, Durability and Willow heals.
    - **Clears:** 55 to our 15.
    - **Gem race:** -31 at r250 and -205 at r500. The widest swing, -372, came in r750-968, while their trio camped our spawn.
  - **01fracture, theirs, on economy.**
    - **Few fights:** our K/D 2/6, including 2 camp deaths.
    - **Tempo:** 74 to 47 clears; camp-damage rounds were 17-27% of alive time for them and 13-18% for us.
    - **Gold:** 9,132 to 4,283.
    - **The decisive edge:** access to the multi-elk altar groups after r1000. Gems from camps were 580 to 167 in r1000-1400, with gems per capture 34.1 to 12.8.
  - **01shortcut, ours, on map structure and carrier kills.**
    - **The route:** TP hops into the pocket against their 45-step walk.
    - **Gems on death:** they lost 674 and we lost 106.
    - **Kills:** 13 to 4.
    - **Gold:** we led 928-240 at r250 and 6,832-3,932 at the end.
    - **Gem race:** +144 at r500 and +241 at r1000.
  - **00breadcrumbs, theirs.**
    - **Their engine:** a capture-and-bank loop beside the altar (94 tributes) plus a trio that killed us 12 times to 2.
    - **Our captures:** gem clusters 51, gold clusters 58. Theirs: gem clusters 131.
    - **Gem race:** -147 at r250, -399 at r500, -700 at r1000.
  - **00ribs, theirs after r1000.**
    - **Up to r1000 we were better:** +208 in r500-1000, ahead 321-249.
    - **Their Vesper snowball then decided it:** 15/0 after r1000. Our deaths were 18 to 9 in that phase, and the gem race went 100-571.
    - **Gold:** 6,341 to 3,118, with their Vesper's 3,422 kill gold above our team's total.
- **Lessons:**
  1. **Splitting into solo farmers against a team that moves in 2-4 feeds kills.**
     - 79 of our champion deaths, none traded; 57 had 2+ enemies involved, and 49 went to one carry.
     - Kill gold is their economy engine: their Vesper's kill gold alone exceeded our whole team's earned gold on swirl (1,859 vs 1,186) and ribs (3,422 vs 3,118), and nearly did on breadcrumbs (1,553 vs 1,637).
  2. **Our economy has no passive emblems,** so the solo safety model never unlocks multi-elk groups.
     - These were swirl's home groups g13, g15, g6 and g17, 4-13 steps from our spawn, and fracture's altar groups.
     - The opponent took them from r430-1035.
     - This repeats V3L-4 (the economy gap against 1530+ teams), now against v4. Their gold was 2.1x ours on fracture and 11x on swirl.
  3. **On cluster maps with a central altar, a gem-and-bank loop beats** our 0.25 gold weight plus 15-30-gem bags. Their HoR won breadcrumbs with 60 gold earned.
  4. **A lead at r1000 is not safe against a fed carry** (ribs). Arriving one at a time at a far objective turns each death into about 130 rounds out of the game: 60 to respawn and about 70 to walk back.
  5. **Crossing tools and carrier hunting win walled-altar maps** against teams that walk (shortcut).
- **Where our approach was better (keep):**
  - **TP-crystal crossing** (`need_crossing`, `cross_toward`, the TP purchase in `shop`): a 2-hop route to an altar the opponent reached only by a 45-step walk past elks.
  - **Carrier hunting** (`focus_bias` gem term, `FIGHT_CARRIER_BONUS`): 474 gems taken on shortcut, where our Vesper went 8/0.
  - **Ribs' middle game:** +208 in r500-1000, with Vendetta at 10 kills overall.
  - **Fuel discipline:** 1 exhaustion after r1 in 5 games, against their 7 (their HoR on swirl at r115, r690 and r830).

## 4. Weaknesses exposed and hypotheses for the testing pipeline
| Weakness | Evidence (game, round, numbers) | Impact (decisive / major / minor) | Code responsible (in the bot that played, `bots/c2_respawn/src/bot.py`) | Testable hypothesis (keyed on structure, never on map or team names) |
|---|---|---|---|---|
| **W1. Lone farmers picked off by an enemy group; no deaths traded** | **Over the set:** 79 deaths to champions; 57 with 2+ enemies involved; 0 traded (no kill by us within 8 rounds and 8 tiles). **Swirl:** our Marcella (r41) and then Vendetta (r47) died alone at (23,16) to Vendetta, Willow and HoR; Vesper died alone at (37,9) at r94 on a 0-gem pair 7 steps from their spawn; 7 deaths to 1 before r300; our champions dead 43-49% of the game. **Breadcrumbs:** 12 kills on us, 11 by Vesper, with HoR and Vendetta assisting on 7. **Ribs:** 30 deaths, mostly single arrivals at the arena. | decisive (swirl, breadcrumbs, ribs) | **`choose_target`** (1390-1455) scores only value / (distance + time-to-kill). It has no term for the distance to allies or for recent enemy sightings near the group. Its claim discount (`score *= 0.3` for soloable groups an ally holds, 1444-1445) actively spreads champions; *speculation:* it sent Vesper past g21 (claimed) to g9. **`handle_enemies`** (1979-2161) acts only once enemies are within 6 (1995). **`group_balance`** (1936-1977) counts allies within `GROUP_R` 7 and `GROUP_ADV_R` 4 (101, 109), so a lone farmer is always "disadvantaged" and walks 1 tile per turn toward allies 10+ tiles away. | **H-pair, pair-farming mode under group pressure.** Trigger: 2+ enemy champions are seen within 4 of each other, or an ally dies to a champion, in the last 60 rounds (one shared-memory bit). Then each champion only takes targets whose centre is within 6 path tiles of a partner's target or position (partners paired by slot), until 150 quiet rounds pass. **Measure:** deaths with 2+ enemies involved, traded deaths, and clears per 100 rounds, against an imitation of this comp. **Related:** extends H-zone (rank 6) and Q29/h_snowball (rank 4); distinct from the rejected blanket enemy-half penalty (T8). |
| **W2. A fed ranged carry snowballs and camps our spawn** | **Their Vesper over the set:** 49 kills, 7 deaths; 6,977 gold from kills at 143 per kill. **Swirl:** 13/0; (17,18), 3 tiles north of our spawn, was a death site 6 times; 4 fights with multiple deaths, none won by us. **Ribs:** 15/0 after r1000. Ryth died carrying 100 gems at (23,52) at r1403, to HoR, Prism and Vesper. | decisive (swirl, ribs); major (breadcrumbs) | **`enemy_dps`** (1877-1881) is strength + 0.15 x focus. **The target key** `(tier, my_ttk/(1+eg/20), d)` (2056) picks the quickest kill (Willow, Prism) and never the carry. **Against the carry,** `best_ratio > FIGHT_FLEE` leads to `retreat` (2145-2160), which moves 1 tile per turn and cannot outrun range 3 plus Dash 2. **Spawn wait** (2549-2550): the at-spawn heal only waits while `incoming == 0`, then each champion walks out alone. | **H-carry, relative-strength carry flag.** Flag an enemy whose strength x max HP is at least 2.5x our team's mean, and write its last-seen tile and round to shared memory. For 30 rounds: no target or path within its attack range + 4 of that tile unless 3+ allies are within 4. When 3+ allies are within 4, it becomes tier-0 focus. A champion on spawn waits until a second ally is ready if the carry was seen within 10 of our spawn. **Measure:** the carry's kills and our spawn-zone deaths. **Related:** complements V2 spawn-pin escape (rank 12) and Q29. |
| **W3. Multi-elk groups never farmed; no passive emblems** | **Swirl:** 0 clears by us of g13 (37 gems, 4 steps from our spawn), g15 (44 gems, 7 steps), g6 (30 gems) and g17 (88 gems). They took them from r433. **Fracture:** after r1000 they captured the 44-59-gem altar groups 8 times (427 gems); we captured them once. **Emblems by r1000:** 5 vs 86 and 15 vs 29. **Base-stat check:** Vendetta on a 2-elk group (5,040 HP, Str 120) needs 24 hit-and-run cycles against a limit of 4, so the group is rejected. | major (decisive on fracture) | **The solo check** in `choose_target` (1413-1434): `dmg_solo`, `budget`, and `cycles > 4` lead to `continue`. **`dmg_mult`** (1394) drops only with a Jungle emblem. **We never buy Jungle:** `shop` (948-976) calls `bruiser_item` (992-1017) first, and it always returns a Bruiser shard for our five drafted champions (`JUNGLE_FIRST = False`, 128), so the Jungle, Monster and Power branches are dead code. Durability is not modelled. | **H-dura, Durability first for the camp tank.** Buy a Durability (Health) emblem as the first emblem for HoR and Ryth (the champions with the highest monster damage taken), and model it as `dmg_mult` 0.9 in `choose_target`. Durability also cuts champion damage, so it should avoid T25's Jungle fight blowouts. Jungle stays conditional (Q28b, rank 8: fracture is the clean low-PvP case, 6 deaths in 1,400 rounds). **Measure:** first-capture round of multi-elk groups and camp-damage rounds per 1k dealt, scoped to maps whose richest groups on our half are multi-elk. |
| **W4. Gold clusters over gem clusters, and no delivery cost, on cluster maps with a central altar** | **Breadcrumbs:** 58 of our 109 captures were 0-gem gold clusters (16 of 28 before r300); our first tribute was at r200 vs their r52; 12 tributes against their 94. Their HoR earned 60 gold and banked 350 gems from the 6 clusters 1-3 tiles from the altar. **Swirl:** 11 of 13 of our captures were worth 0 gems. | major (decisive on breadcrumbs) | **`Group.value = gems + 0.25*gold`** (260) makes a 20-gold cluster worth 5 against 7 for a gem cluster. **The cost** `d + ttk + 6 + extra + wait` (1437) has no altar leg, so gold clusters next to our spawn beat gem clusters next to the altar. **Bank thresholds** `BANK_ANY` 30, `BANK_NEAR` 15 and `BANK_CLOSE` 5 (54-58) are tuned for camps, not clusters. | **H-loop, delivery-aware gem value when every gem source is a cluster** (no camp strength) and one altar is within 5 of 4+ gem groups. Add `min(0.5*d, altar_d)` to the cost of gem groups (the capped Q27d form, rank 58), and keep `BANK_CLOSE`, so captures next to the altar are banked at once. Keep gold weight 0.25 only until the first emblem, then 0.1 for gem-less groups. That respects Q27c's item-starvation caution; this match contradicts Q27f's gold-first premise on such maps. **Measure:** gems per 100 rounds and the first-tribute round on cluster-only maps. |
| **W5. Opening pile-on on non-soloable groups** | **Fracture:** g11 was captured by 4 champions at r48 (22 gems, 5-6 each); g9 by 3 at r117; g17 by 2 at r154. We made 8 captures before r300 against their 16 solo ones; clears per 100 rounds before r300 were 2.67 vs 5.33. | major (fracture tempo) | **`choose_target`:** an ally's claim on a group that is not `solo_ok` multiplies its score by 1.2 (1446-1447), and every claim adds 55 to team DPS (1415). So once one champion commits to a 2-wolf group, each additional champion finds it cheaper and boosted, and piles on. | **H-spread, cap co-claimers at one helper.** For a non-soloable group whose 2-champion check passes, a third claimer gets ×0.3, as for soloable groups. This holds while any other acceptable target exists. Keyed on group HP and strength against champion stats. **Measure:** captures and clears per 100 rounds before r300, and mean recipients per capture. |
| **W6. Champion stranded on a hole-ringed island** | **Shortcut:** Marcella's last damage dealt was at r442 and wolf damage stopped at r470. She then had no metric change until r928, when she died to the g7 wolves (camp12) at (19,7) with 11 gems: 458 idle rounds, in a 4-pick team. | minor here (we won); major on the ladder in general (V3L-2) | **The low-HP walk-home branch** in `play_turn_main`: `elif low: self.step_toward(me, self.spawn); return` (2599-2601). It fails silently from another walk component, and `spawn_d > 6` (2592) blocks the recall. | **No new hypothesis:** this is ladder confirmation for merging h_shortcut (T33) into the V1 combo (rank 5). |
| **W7. Altar locks bought before stats, with no measurable effect** | **Purchases:** 63 locks bought (7, 16, 12, 14 and 14 per game; about 50 placed) for 630 gold; that is 6% of our gold on swirl and 9% on breadcrumbs. **Order:** on swirl the lock was HoR's first purchase (r50), before any shard. **No visible effect:** they tributed 200 times, including 12 times at our home altar on swirl, which `lock_side` never locks. Lock placements are not logged, so the effect cannot be measured. | minor | **`shop`** calls `buy_lock` (955; 2290-2296, `LOCK_MIN_GOLD` 40) before any item. **The proactive lock** in `try_lock` (2325-2334) uses `lock_side` (`LOCK_SIDE_MARGIN` 4, 44), which excludes our own altar. | **H-lockgate:** buy a lock only after the champion's first completed emblem, and use only reactive locks (on a visible enemy tribute channel). **Measure:** emblem timing and the gem race. Low priority; bundle with W3 into any build experiment. |
