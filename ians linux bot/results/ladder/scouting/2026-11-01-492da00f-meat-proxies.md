# meat proxies (1534): ladder set 492da00f, 1 Nov 2026, our v3, won 5-0

- **Opponent:** meat proxies, rating 1534 (ours after the set: 1529).
- **Our version:** website v3 = `bots/q24_combo` (live 01:42-04:42 UTC). The set ran at 02:42 UTC. We were side B (team B) in all 5 games.
- **Record: 5-0.**
  - W 02stalactites 1008-84 (r523).
  - W 01gold_rush 1029-396 (r1529).
  - W 00galaxy 1005-779 (r1560).
  - **W 00lanes 1008-963 (r1622): won by 45 gems.**
  - W 01starvation 673-163 (r2000, gem tiebreak).
- **Link:** https://2026a.battlecode.co.uk/game/match-groups/492da00f-9b0f-4be6-94cc-a5f40f981d22
- **Sources:** `results/ladder-games.jsonl`, `matches/ladder/summary/<id>__B.json`, and `python3.12 -I tools/scout.py --group 492da00f`.
  - Session scratchpad scripts: `ganks.py`, `mirror.py`, `party.py`, `recalls.py`, `tl.py`, `ts.py` and `mapart.py` (see the 95f8259f report for what each does).
- **Method:** positions come only from events and wards. Speculation is marked.
- **Why scout a 5-0.** Two games were close in the race:
  - lanes, 45 gems;
  - galaxy, behind 60-78 at r250 and only +26 at r1000.
- In lanes they out-farmed us 114 clears to 65 and finished 1,813 gold ahead. In two games we threw away 237 gems through one specific carrier behaviour. Those are the weaknesses a stronger bot will punish.

| Map (size, picks) | Result | r250 | r500 | r1000 | End | Clears /100r us-them | K/D us | Gold end us-them | Gems lost on death us/them |
|---|---|---|---|---|---|---|---|---|---|
| 02stalactites (30x30, 4) | W | 403-0 | 697-84 | — | 1008-84 r523 | 1.15-3.25 | 9/4 | 1,730-1,392 | 143/598 |
| 01gold_rush (31x31, 3) | W | 55-55 | 132-121 | 319-253 | 1029-396 r1529 | 5.36-3.34 | 14/5 | 10,133-2,396 | 11/88 |
| 00galaxy (93x93, 5) | W | 60-78 | 278-225 | 548-522 | 1005-779 r1560 | 4.04-2.63 | 17/16 | 2,977-2,284 | 265/172 |
| 00lanes (90x30, 5) | W | 52-21 | 188-88 | 538-426 | 1008-963 r1622 | **4.01-7.03** | 11/10 | **6,349-8,162** | 50/287 |
| 01starvation (80x80, 5) | W | 28-28 | 111-28 | 343-28 | 673-163 r2000 | 2.6-2.5 | 12/16 | 3,525-3,694 | 48/121 |

## 1. Opponent profile

### Draft and roles
**Draft:** Varg, Ryth, Stellar, Marcella, Tavi (5 picks); the first four on 4 picks; **Varg, Cassi & Issac, Ryth** on 3 picks.

- **Tavi: their best fighter.**
  - 17 kills, 6 deaths in 3 games (starvation 9/1, galaxy 6/2).
  - Its 1.6xF stun at r4 opens our ganks.
- **Stellar: Focus burst (2xF single target, 1.4xF AoE).**
  - 13 kills in 4 games; lanes 6 kills with Power Focus stacking.
  - Also their most fragile champion: 15 deaths, several while carrying.
- **Varg: their top farmer.**
  - Lanes 31 clears, 50k monster damage.
  - Often carries their biggest bags: stalactites 104 and 143; lanes 50; galaxy 49.
- **Marcella and Ryth:** solo farmers.
- **Cassi & Issac (gold rush):** killed 4 times as a linked pair: r263 (12,14), r577 (9,12), r676 (18,12) by our Vendetta, and r923 (20,7) by our Vesper.

### Items: Jungle first, then Monster, Treasure, Durability, Power/Home, Power stacking
| Champion | 1st emblem | 2nd | 3rd | Then |
|---|---|---|---|---|
| Varg | Jungle H (stalactites r87, lanes r455, galaxy r588) | Monster S | Treasure S | Durability H, Power S, Home H, then Power S/H x n (lanes: 11 Power S + 8 Power H on the team) |
| Stellar | Jungle F (r179-600) | Monster F | Treasure F | Durability H, Power F, Home H, Power F/H stacking (lanes: 7 Power F shards at r1190) |
| Marcella | Jungle H | Monster S | Treasure S | Durability H, Power S, Home H, Power stacking |
| Ryth | Jungle H | Monster S | Treasure S | Durability H, Power S |
| Tavi | **Monster S** (first shards r60-130; emblem r189-668) | Jungle H | Treasure S | Durability H, Power S, Home H, Power stacking |

- **Emblems by r1000:** lanes 21 of theirs vs 20 of ours. By the end of lanes: **Power 23** emblems.
- **No altar locks, no TP crystals.**

### Farming pattern
- **Pure solo:** capture party size 1.00 in 4 of 5 games; 1.04-1.31 on lanes.
- **Lanes: a tight circuit next to their altar.**
  - Their trio of Wolf+GemCl groups g30/g32/g34 at (36,2-6), 7 tiles from their altar (29,4), was captured **18/16/14 times from r50-62**.
  - The mirror trio g31/g33/g35 on our side (dUs 31, our altar (60,4) 6 tiles away) got **5/2/2** captures from us.
  - That one circuit is 48 vs 9 captures, **528 vs 99 gems**.
  - Their clears per 100 rounds after r1000 were **9.47 vs our 4.17**.
- **Camp damage taken per 1k dealt:** lanes 195 vs our 414; elsewhere similar to ours (galaxy 96 vs 115, starvation 305 vs 324).
- **Idle and fuel-starved.**
  - 38-88 `fuelExhausted` per game after r1 (ours 0-20).
  - Quiet champion-rounds: galaxy 538 (Stellar 172), starvation 1,722 (Stellar 469, Tavi 453, Varg 452).

### Tribute behaviour: late and large, walking big bags into our champions
- **First tribute:** r82 (gold rush), r143 (galaxy), r153 (lanes), r213 (starvation), r300 (stalactites). Ours: r36-130.
- **Stalactites: 1 tribute (84) in 523 rounds.** They captured 437 camp gems before r300 but tributed 0 in that time, and **lost 598 gems on death**.
- **Starvation:** 6 tributes in 2,000 rounds, none between r213 and r1239. They ended carrying 68.
- **Galaxy: they tributed mostly at our-side altar (54,46)** (16 tributes, 645 gems), and we at theirs (38,46) (25, 613): the two central altars are 16 apart.

### Fight behaviour
- **Gank-oriented when they fight.**
  - Our deaths by number of enemy participants: lanes 10 of 10 had >= 2; galaxy 14 of 16; starvation 14 of 16; stalactites 4 of 4.
  - Tavi or Stellar usually lands the kill.
- **They hunt our big carriers.**
  - Galaxy r667: Vendetta carrying 94 at (72,58), by Tavi + Varg, Ryth, Stellar.
  - Stalactites r380: Vesper carrying 143 at (12,5), by Varg + Ryth, Stellar, Marcella.
  - Lanes r724: Ryth carrying 50 at (68,1), by Stellar + 2.
- **They lose 1-vs-1s:** 9 of their 17 deaths in galaxy and 10 of 14 in gold rush were solo kills by us.
- **They die to camps when over-reaching:** gold rush 4 (Ryth r125 (17,10), Varg r434 (19,10), Cassi/Issac r437); lanes 2.

### Adaptation
None: same draft, same item loop, solo farming on every map. The gold-rush 3-pick swaps in Cassi & Issac (a pick that dies twice per kill).

## 2. Per game

### 02stalactites (W 1008-84, r523)
- **Map.** 30x30; adjacent central altars (14,14)/(15,14); gem-cluster fields g6 (8,23) 77, g8 (14,21) 168, g7 (21,23) 77.
- **r21-30.** HoR killed Stellar and Vendetta killed Ryth at (8,12), their half: 2-0 before any farming.
- **Banking.**
  - We took g6 at r52 and banked from r61; 403-0 at r250.
  - They took g8 (168) at r148 and g7, but banked nothing before r300.
- **Their carriers died at the altars.**
  - r175: Stellar, 84, at (13,14), solo by our Vesper.
  - r198: Marcella, 165, at (18,13).
  - r310: Varg, 104, at (16,14).
  - r469: Varg, 143, at (10,24), by HoR.
  - r483: Marcella, 102, at (18,13).
  - **598 gems** moved to us; their only tribute was Ryth's 84 at r300.
- **Our own leak.**
  - r310: Vesper killed Varg at (16,14) and took 104, then **recalled**: ward (26,0) and a purchase at (28,1) at r316. It now carried **143**.
  - It walked west, with wards at (17,7) r326 and (8,7) r336, toward their Ryth and Stellar wards around (7-9,2-11).
  - It died at (12,5) at r380 to a 4-champion gank with all 143 gems, which went to Varg.
  - *Speculation:* `handle_enemies` engaged on the way, so it never reached the altar.
- **Root.** Their late, huge bags walked into our altar presence (`focus_bias` tier 0 on channellers, kills on carriers). We won despite 17 clears to our 6 before r523.

### 01gold_rush (W 1029-396, r1529), 3 picks vs Varg / Cassi & Issac / Ryth
- **Race.** 55-55 at r250, 132-121 at r500, 319-253 at r1000, then **+389 in r1000-1500**.
- **Gold race (ours):** 1,251 vs 380 (r250), 2,474 vs 860 (r500), 6,064 vs 1,760 (r1000).
  - We farmed 5.36 clears per 100 rounds to 3.34, including 32 enemy-side captures (3,000 base gold).
  - Vesper and Vendetta went 6/0 and 8/1. Each C&I pair kill was one 100-gold reward but two bodies off the map.
- **We won all 7 multi-death fights.** Emblems by r1000: 36 vs 9.
- **The decider.** The centre g0 (GoldClx4 + Monolith, 200 gems) was captured by Vesper, Vendetta and Marcella at r1108 (68/66/66), then twice more. They never took it.
- **Root.** Economy and items: a 3-pick map where our Bruiser fighters snowball, against a fragile C&I pick that also lost 4 champions to camps.

### 00galaxy (W 1005-779, r1560)
- **Map.** 93x93; spawns in opposite corners. The gem-cluster groups and both altars are near the centre, 53-67 path tiles from each spawn.
- **r0-1000: a near-even race (548-522).**
  - Altar fights:
    - r462-465 at (52-54,45): we lost Ryth (21 gems) and Vesper to Ryth + Stellar;
    - r576-587 at (36-40,45-46): we lost Marcella (35) and killed Stellar (20) and Varg (49);
    - r784-791 at (50-51,46-50): we lost Ryth and Vesper to Tavi.
  - Our HoR was quiet r0-135.
- **The leak, r587-667.**
  - Vendetta (melee) took 69 gems from Stellar and Varg at (36-39,45-46), so it stood **within 2 of altar (38,46)** (its r579 ward is at (37,46)).
  - It recalled 6 rounds later: ward (87,87) and purchases at (89,89) at r593.
  - It walked back with **94** gems: (78,78) r603, (68,68) r613, (71,62) r623, (73,48) r633, (68,39) r643 (14 from altar (54,46)), (73,48) r653, (72,58) r663.
  - It died at (72,58) at r667 to Tavi + Varg, Ryth, Stellar. All 94 were lost.
- **r1000-1560: +288.**
  - Our camp gems 517 vs 144; clears 4.63 vs 2.14 per 100 rounds.
  - Their 538 quiet champion-rounds and 88 fuel exhaustions show.
  - Vendetta 12/2 overall (1,200 kill gold).
- **Root.** Late farming tempo against a fuel-starved, idling opponent. The race stayed close for 1,000 rounds partly because we gave away 94 gems at r667 and 23+35 in altar fights.

### 00lanes (W 1008-963, r1622): the near-loss
- **Map.** 90x30; 18 altars; 42 groups.
  - Near each spawn's side altars: a trio of Wolf+GemCl (11 gems) and three Elk+GemCl (22 gems).
- **r0-500: ours.** 188-88 at r500. We tributed first (r88 vs r153).
  - Kills: r262 Tavi; r402-405 Marcella (26) and Tavi (11) at (38-42,7-8), their half.
- **r500-1622: they out-farmed us.**
  - Clears per 100 rounds 5.86 vs 4.29 (r300-1000), **9.47 vs 4.17 (after r1000)**.
  - Their captures on their side: 90 (1,142 gems). Ours on ours: 40 (639).
  - The gap is mostly the Wolf+GemCl trio (48 vs 9 captures; §1).
  - Our captures went to the Elk+GemCl groups (g7 9, g9 10, g21 5) and to 1-3-capture visits of nine different Wolf+GoldCl groups.
  - Gold flipped: 1,685 vs 1,192 at r500; 3,621 vs 4,029 at r1000; 6,349 vs 8,162 at the end.
  - Their Power stacking (Stellar 7 Power F at r1190; Varg 7 Power H + 6 Power S at r1491) was the late scaling.
- **What saved it: kills on their carriers.**
  - r723: Ryth killed Varg carrying 50 at (67,2), and Ryth died a round later carrying 50 at (68,1).
  - r909: Marcella, 33, at (42,1).
  - r1131-1138: Tavi (37) and Marcella (48) at (44,0-1).
  - Their gems lost on death: **287 vs our 50**. The final margin was 45.
- **Root.** We won by carrier kills while losing the farming race 1.75:1 on clears. *Speculation:* why our champions under-farm the trio is not observable without a trace. The scores in `choose_target` should favour it for every champion (value 21, solo-ok, near an altar). A likely cause is the claim spread (x0.3 for solo-ok claimed groups) pushing the second and third champion to the far Wolf+GoldCl groups.

### 01starvation (W 673-163, r2000 gem tiebreak)
- **Map.** 80x80. All gems are near the top-centre altar box (35,15)/(44,15): GemClx4 g5 (40,10), 28 gems, and 4-gem wolves g6/g7. The box's 88-gem g2 and the two monoliths were never taken (we took g2 once, at r1857).
- **Race.** 28-28 at r250; 111-28 at r500; 343-28 at r1000.
  - **They did not tribute between r213 and r1239.**
  - We killed 12 of their champions around the box (26-54, 4-16), e.g. r309 Marcella (29,13), r514 Varg (37,4), r977 Stellar (39,11).
- **Our tempo was poor too.**
  - 2.6 clears per 100 rounds; **2,165 quiet champion-rounds** (Vesper 755, Vendetta 552, Ryth 433).
  - Our gold trailed all game (3,525 vs 3,694). We bought our first emblem only at r575.
- **Root.** The opponent could not bank (fuel-starved, idle, carriers killed near the altars). We won the gem tiebreak while farming slowly. On this map the long spawn-to-box walk (about 65-100 path tiles) eats our time, the same as against Warwick Wuants on this map (95f8259f report).

## 3. Their strategy vs ours

### Where theirs was superior
| Gap | Size | Our code responsible |
|---|---|---|
| **A. Tight own-side circuit next to an altar.** | Lanes: Wolf+GemCl trio 48 vs 9 captures (528 vs 99 gems); clears after r1000 9.47 vs 4.17; gold 8,162 vs 6,349. | `choose_target` (q24 l.1371) scores per champion with claims: x0.3 if solo-ok and claimed (l.1425-1426), x1.3 for the current target. Nothing rewards *short respawn cycles near an altar*: `cost = d + ttk + 6 + extra + wait` has no term for the trip to bank afterwards. A group 7 tiles from an altar and one 25 tiles away score the same for the same `d`. *Speculation* for the trio itself (no trace). |
| **B. Late scaling items (Jungle, then Power stacking).** | Lanes: Power 23 emblems at the end; their monster damage per 100 rounds 11,944 vs 7,365; camp damage per 1k 195 vs 414. | `shop()`/`bruiser_item()` (`BRUISER_PLAN`, `JUNGLE_FIRST = False`): no camp-mitigation passive (see 95f8259f W1). |

### Where ours was superior (why 5-0)
- **Banking cadence.**
  - First tribute r36-130 vs their r82-300. They carried 84-165-gem bags; our `bank_now` (BANK_ANY 30) rarely does.
  - The carrier-kill differential (gems lost on death, ours vs theirs): stalactites 143 vs 598, lanes 50 vs 287, starvation 48 vs 121.
- **Punishing channelling/carrying enemies.** `focus_bias` puts channellers in tier 0, with a ratio bonus of +min(0.3, gems/100) for carriers. That is how the stalactites altar kills happened.
- **Fuel and idle.**
  - Our fuelExhausted: 0-20 per game vs 38-88.
  - Their quiet rounds: 538 (galaxy) and 1,722 (starvation).
- **Duels.** 9/17 (galaxy) and 10/14 (gold rush) of their deaths were 1-vs-1 kills by us. Vendetta went 28/10 over the set.

## 4. Our weaknesses exposed (even in a 5-0)
| # | Weakness | Evidence | Games | Impact |
|---|---|---|---|---|
| W1 | **Recall with a big bag next to an altar**, then a long walk back carrying it. | Galaxy r587-667: Vendetta, within 2 of altar (38,46) with 69+ gems, recalled at r593 and died at (72,58) at r667 carrying 94. Stalactites r310-380: Vesper took 104 at (16,14), recalled at r316 and died at (12,5) at r380 carrying 143. **237 gems lost in two events.** | 2 | major (decisive against a better opponent) |
| W2 | **Own-side circuit under-farmed.** | Lanes: trio 48 vs 9 captures; clears after r1000 4.17 vs 9.47; gold 6,349 vs 8,162; won by 45. | 1 | major |
| W3 | **Idle/walking time on huge maps.** | Starvation: 2,165 quiet champion-rounds; first emblem r575. Galaxy: HoR quiet r0-135. | 2 | minor (won) |
| W4 | **Altar skirmishes lost 2-for-0 in the centre** (the comp vs Tavi/Stellar stuns). | Galaxy r462 (we lost Ryth with 21 and Vesper) and r784 (Ryth and Vesper to Tavi). | 1 | minor |

## Testable hypotheses (structure-keyed; no map or team names)
1. **H-bankfirst (W1; strong ladder evidence for the queued V3L-2c).**
   - **Change.** In `play_turn` (q24 l.2520-2535, c2 l.2586+), before the `low`/`rich` recall, if `me.gem_count() >= 15` and a usable, non-enemy-locked altar is within 1 (or 2 with one step), and no visible enemy can reach us within the channel length (`ceil(gems/10)` turns, using `recall_safe`-style reach with that horizon), start the tribute instead of recalling. Tribute is **not** interrupted by damage, only by stun or death; recall is interrupted by damage.
   - **If the channel is unsafe.** Recall only if `carried < 15`. Otherwise retreat on foot toward the altar ring, away from the spawn.
   - **Metrics.**
     - Gems lost on death by champions who were within 3 of an altar in the previous 20 rounds (needs a trace locally; on the ladder, use the kill-gain to death-loss chains as here).
     - Mean bag at death.
     - Recalls with >= 15 carried.
   - **Gate.** Full `--maps all` plus a check that fight K/D does not fall (a carrier standing still for 10 turns is exposed).
2. **H-altarloop (W2): value respawn cycles near our altar.**
   - **Change.** Add a banking term to the cost: `cost += 0.5 * altar_dist(G)` (path from the group's centre to the nearest usable altar ring, already available via `sfields[-2-i]`).
   - **Effect.** Small groups beside an altar outrank equal groups far from one, and champions settle into short clear, bank, clear loops like the opponent's lanes trio.
   - **Metrics.** Captures per 1,000 rounds on groups within 10 of an altar; clears per 100 rounds; banking walk tiles per gem.
3. **H-claimspread-near (W2, test with H-claimcap from the 95f8259f report).**
   - **Change.** For solo-ok groups within 12 path tiles of each other, apply the x0.3 claim discount only if the claimant is *at* the group (within 3), so two champions can alternate on a cluster of small groups instead of one being pushed to a far one.
   - **Metric.** Captures on the nearest 3 own-side groups vs the enemy's mirror captures.
4. **H-bigmap-walk (W3, shared with 95f8259f H-farzone-recall).**
   - **Change.** On maps whose usable altars are >= 50 path tiles from our spawn, skip `rich` shopping recalls unless also below 70% HP.
   - **Metric.** Quiet champion-rounds per game (scout `idle`); first-emblem round.

**Opponent-specific notes.**
- A fuel-starved, solo-farming bot with late, huge banking; it loses its bags to anyone who holds the altars.
- Its only real threat is farming tempo on lane maps with a tight altar-side circuit, plus Tavi/Stellar ganks on carriers.
- Expect wins, but by small margins where it farms near its own altars.
