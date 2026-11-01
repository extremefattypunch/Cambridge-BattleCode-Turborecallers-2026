# Warwick Wuants (1548): ladder set 95f8259f, 1 Nov 2026, our v3, lost 1-4

- **Opponent:** Warwick Wuants, rating 1548 (ours after the set: 1529).
- **Our version:** website v3 = `bots/q24_combo` (live 01:42-04:42 UTC). The set ran at 02:52 UTC. We were side A (team A) in all 5 games.
- **Record: 1-4.**
  - **W 02the_pack 0-0** (r2000, gold tiebreak 19,400 vs 873).
  - **L 00expanse 558-1015** (r1345, gems).
  - **L 00dunes 470-1019** (r1456, gems).
  - **L 01starvation 294-580** (r2000, gem tiebreak).
  - **L 00swirl 128-1032** (r1500, gems).
- **Link:** https://2026a.battlecode.co.uk/game/match-groups/95f8259f-f65e-44f8-b85b-89d37aa313a0
- **Sources:** `results/ladder-games.jsonl`, `matches/ladder/summary/<id>__A.json`, and `python3.12 -I tools/scout.py --group 95f8259f`.
  - Session scratchpad scripts:
    - `ganks.py`: killer and assisters per death;
    - `mirror.py`: our captures on our-side groups vs theirs on the mirror images;
    - `party.py`: champions per capture;
    - `recalls.py` / `recall2.py`: recall estimate from ward jumps;
    - `tl.py`, `ts.py`, `mapart.py`.
- **Method:** positions come only from events and ward placements. "Recall" counts are estimates: a ward >= 12 tiles from our spawn followed within 25 rounds, with no death, by a ward within 6 of the spawn. Speculation is marked.

**Why this set matters.** Warwick Wuants drafted **our exact five champions**: HoR, Vesper, Marcella, Ryth, Vendetta (truncated to HoR, Vesper, Marcella on 3 picks and adding Ryth on 4). With identical champions they out-farmed us 2-3x. The difference is play and items, not draft (compare Q19, mirror-meta).

| Map (size, picks) | Result | r250 | r500 | r1000 | End | Clears /100r us-them | K/D us | Gold end us-them | Camp dmg taken /1k dealt us-them |
|---|---|---|---|---|---|---|---|---|---|
| 02the_pack (45x45, 3) | **W** | 0-0 | 0-0 | 0-0 | 0-0 r2000 (gold) | 8.45-1.0 | 3/0 | 19,400-873 | 39-174 |
| 00expanse (80x80, 5) | **L** | 56-34 | 142-109 | 458-447 | 558-1015 r1345 | 3.05-8.03 | 3/2 | 4,310-10,026 | **492-115** |
| 00dunes (79x79, 5) | **L** | 43-36 | 214-145 | 409-370 | 470-1019 r1456 | 0.76-2.88 | 8/11 | 1,836-4,710 | **1,042-387** |
| 01starvation (80x80, 5) | **L** | 32-32 | 88-68 | 186-212 | 294-580 r2000 | 1.85-3.05 | 9/7 | 2,100-3,375 | 254-287 |
| 00swirl (45x30, 4) | **L** | 5-15 | 21-45 | 61-431 | 128-1032 r1500 | 2.07-4.2 | 5/20 | 3,673-12,746 | **528-182** |

**We led the gem race at r1000 in two of the four losses** (expanse +11, dunes +39). Starvation was +20 at r500 and -26 at r1000. They won every game in the 1000+ window: expanse -452, dunes -545, starvation -164, swirl -496. **Three of the four losses are scaling losses, not opening losses.** Swirl is the exception: behind from r250.

## 1. Opponent profile

### Draft and roles (mirror comp)
- **Vesper Vale: their carry and killer.**
  - 21 kills, 4 deaths in the set (ours: 2/8); 12,792 gold.
  - Swirl 12/0; dunes 7/1, plus a **solo capture of the 92-gem golem group at r1200 for 106 gems**, tributed as 127.
- **Heart of Ruin: their best farmer, not a fighter.**
  - Expanse 419 gems, 3,437 gold, 25 clears; set K/D 1/9.
  - Focus-built: dash landing 1.5xF; shield 1.5xF.
- **Marcella and Vendetta:** solo farmers and assisters.
- **Ryth:** the weakest (6/14).

### Items: every emblem family once, then Bruiser stacking
The order is identical for every champion and every game; only the stat follows the champion (HoR and Marcella Focus/Health, Vesper and Vendetta Strength, Ryth Health/Strength):

**Jungle -> Durability -> Hunter -> Skirmish -> Monster -> Prospector -> Capture -> Collectors -> Tribute -> Bruiser x N**

| | Jungle done | All 9 families done | Bruiser stack |
|---|---|---|---|
| Expanse HoR | r211 | Tribute F at r784 | BruF x10 at r784, then 18 shards at r1177 and 12 at r1293: **13 BruF emblems by the end** |
| Expanse Vesper | r164 | r914 | BruS x16 at r1034, 14 at r1198 ... |
| Swirl Vesper | r102 (with Durability) | **r646** | BruH x11 r729, BruS x13 r768, x9 r861, x17 r905, x16 r971, x24 r1083 |
| Dunes Vesper | r167 | r1219 | BruS x17 r1324 |
| Starvation Vesper | r306 | r1906 | none |

- **Passives collected:**
  - Jungle -30% camp damage;
  - Durability -10% all damage;
  - Hunter +50 gold per kill;
  - Skirmish +5% vs champions;
  - Monster +15% vs camps;
  - Prospector +25% of their own cluster share;
  - Capture: 3-round captures;
  - Collectors: +1% damage per family, so +9%;
  - Tribute: faster channels.
- **Ours:** Bruiser shards only (`BRUISER_PLAN`), so **no passive at all**.
- **Emblems by r1000, theirs vs ours:** expanse 37 vs 21; swirl **42 vs 12**; dunes 11 vs 8; starvation 7 vs 4.
- **No altar locks, no TP crystals.** We bought 3-11 locks per game.

### Farming pattern: pure solo, tight own-side circuit, gold clusters included
- **Party size 1.00-1.06 in every phase of every game** (solo captures 94-100%). Ours: 1.1-1.8, with 4-champion captures.
- **Mirror-pair captures (their own-side group vs our mirror of it).**
  - Expanse:
    - Wolfx2+GemCl+GoldCl: 15 vs **0**;
    - Elk+GoldClx2: 14 vs 7;
    - the four gold-cluster groups: 12+13+13+8 = **46 vs 13**;
    - Wolf+GemCl: 8 vs 5.
  - Dunes: Wolf+GemClx2 12 vs 6; Elk+GemClx4 10 vs 6.
  - Swirl: our-side elk groups g12/g14/g16/g7/g3 (dUs 4-17) **0 captures** by us; they took their mirrors from r809-1239.
- **Camp damage taken per 1k dealt:** expanse 115 vs 492; dunes 387 vs 1,042; swirl 182 vs 528.
- **Monster damage per 100 rounds:** expanse 11,992 vs 7,518; swirl 11,895 vs 3,840; dunes 6,281 vs 2,062.
- **Solo-ing the big groups once itemised.**
  - Expanse after r1000: **solo** captures of the 44-gem Elkx2+GemClx2 corner groups, 47 gems each (44 + Prospector):
    - our-side g5 (8,65) at r1009 and r1269;
    - g9 (9,59) at r1148;
    - g8/g4 (71,12-19) at r1126 and r1150;
    - g1 at r1124 and r1262.
  - Our earlier capture of g9 at r954 took **4 champions, 11 gems each**.
- **Fewer trips home (estimate from ward jumps), theirs vs ours:** expanse 23 vs 36, dunes 12 vs 39, starvation 14 vs 32, swirl 6 vs 17. Our pure-heal recalls, with no purchase within 3 rounds: dunes 27, starvation 21, expanse 9.

### Tribute behaviour
- Medium bags at the nearest altar, **including ours**:
  - expanse 7 tributes, 320 gems at our altar (12,47), next to the our-side corner groups they farmed;
  - dunes 16 tributes, 722 gems at our-side altar (39,35).
- Means: 20.7-35.1. First tributes r67-91.
- No big-bag hoarding except the dunes golem bag (127).

### Fight behaviour
- **Opportunistic early, grouped late on small maps, and Vesper-centred.**
  - On swirl (45x30, spawns about 15 apart) 14 of their 20 kills were 3- or 4-champion ganks.
  - Deaths near our spawn exit: (26,5) x2 at r750-753, (22,7) r918, (24,7) r982, (22,10) r999. Swirl counts 7 our deaths within 6 of our spawn.
- **Dunes late:** 5-champion ganks at our g3 (29,38): Marcella r1314, Ryth r1318 and Vesper r1404 at (30,33).
- **Expanse:** only 3 kills in 1,345 rounds. They do not hunt when the farm race is enough.
- They lose champions to camps when they over-reach: dunes 5 camp deaths (Vendetta x3 at (39-42,38), next to the 92-gem golem centre).

### Adaptation
None in the plan, but it scales with income:
- on rich, safe maps the family loop completes by r650-900 and the Bruiser stack follows;
- on poor maps (starvation) it never gets past Tribute.

The 3-pick the_pack shows their weakness: all 3 champions froze from r337-478 to r2000 (5,012 quiet champion-rounds, 79 gems never banked). The only altar is enclosed by a 48-wolf ring.

## 2. Per game

### 02the_pack (W 0-0, gold 19,400 vs 873)
- **The map.** The single altar (22,22) sits inside a 48-wolf ring (g0, 192 gems). Our `init_gold` flags it unusable, so `no_tribute` gold play runs.
- **Kills.** Vendetta killed HoR at r109 (22,10), Marcella at r121 (21,17) and Vesper at r249 (26,25).
- **Our play.** 169 clears; Treasure emblem first (h_goldtie), then 125 Bruiser emblems; 754 gems carried and never banked (worthless here).
- **Theirs.** Frozen from about r400.
- **Root.** h_goldtie gold play works, and the opponent has a no-altar freeze.

### 00expanse (L 558-1015, r1345), a pure farming race (3 kills by us, 1 by them)
- **r0-1000: even.** 458-447 at r1000. We tributed first (r49 vs r80) and were ahead at every checkpoint; they went ahead for good at r1029.
- **Gold diverged from the start:** 915 vs 1,132 (r250), 1,715 vs 2,838 (r500), 3,554 vs 6,515 (r1000).
  - Their extra gold was the own-side gold-cluster circuit (46 vs 13 captures) and the Wolfx2+GemCl+GoldCl group near their spawn (15 vs 0).
- **r954.** Vesper, Vendetta, Marcella and HoR captured g9 (8,59) together, 11 gems each. Then:
  - r983: Vendetta died to a camp at (8,64), at g5;
  - r991: Marcella died to their Vesper at (1,57).
- **r1000-1345: the decisive window, 541 camp gems to our 89.**
  - Their solo captures of 44-gem groups listed in §1, two of them ours (g5, g9).
  - Our team took 7 clears: g2 (25,15) x3, g9, g4 (71,13) and two gold clusters.
- **Root.**
  - Item scaling (Jungle + Durability + Monster + Prospector, then 10-13 Bruiser emblems) turned the 44-gem elk groups into solo targets for them.
  - Our solo model still rejects them, so we sent 4 champions or none.
  - Their camp-damage efficiency was 4.3x ours (115 vs 492 per 1k).

### 00dunes (L 470-1019, r1456)
- **Map (decoded).** All gems sit in the centre:
  - g0 (39,39): GemClx8 + Golem, 92 gems;
  - g1/g2: Wolf+GemClx2, 18 each;
  - g3/g4: Elk+GemClx4, 43 each.
- Spawns are in the corners (3-5,3-5) and (73-75,73-75), about 40 path tiles from the centre. The rest is 4-gem wolves in far corners.
- **r0-1000: even fights, we led 409-370.**
  - Their 5 champion-kills of us before r1000:
    - r131 Marcella (36,31) and r156 Vesper (38,31), both by their Vesper;
    - r342 Vendetta, carrying 12, at (49,37);
    - r378 Marcella (51,25);
    - r986 Ryth (46,22), a 5-gank.
  - Our 7 kills before r1000 include HoR's 3 in r704-792.
  - They lost 5 champions to camps: 4 at (39-42,37-38) next to g0, 1 at (51,37) by g4.
- **Our clears: 2 in <300, 8 in 300-1000, 1 after r1000 (11 in total vs 42).**
  - Our team monster damage over the whole game was 30k vs 91k.
  - Our champion damage taken was 50k. The time went into centre skirmishes and heal trips: estimated 39 recalls vs 12, 27 of them with no purchase.
- **r1000-1456: 699 camp gems to our 61.**
  - Their solo captures: g4 r1016 / r1093 / r1174 / r1265 / r1375; our-side g3 r1007 and r1334; g1 r1140; g2 x3; and their Vesper's solo g0 at r1200 (106 gems).
  - Our deaths: r1122 Ryth (27,34) 1-vs-1; r1314/r1318 Marcella and Ryth at (24-29,37) to 5- and 4-champion ganks; r1404 Vesper at (30,33), 5-gank.
- **Root.**
  - The centre is the only gem source and both teams live there.
  - Their item curve (Jungle, Durability, then the Bruiser stack on Vesper) won the late centre. Our champions spent the game walking about 40 tiles home to heal.

### 01starvation (L 294-580, r2000 gem tiebreak)
- **Map.** 80x80; spawns at (1-3,48-50) and (76-78,48-50).
  - The only altars (35,15)/(44,15) sit in a walled box at the top centre.
  - The gem sources are around it: g5 GemClx4 (40,10) 28 gems; 4-gem wolves g6 (26,15) / g7 (53,15).
  - Inside the box, g2 (Elkx4+GemClx4+GoldClx4, 88 gems) and the two 200-gem monoliths were never touched by either team.
- **Race.** 32-32 (r250), 88-68 (r500), 186-212 (r1000), 294-580.
  - Their Vesper made 27 clears, 358 gems.
  - They captured **both** wolves 27 times (we did 8) and our-side gold g3 7x.
- **Our idling: 2,373 quiet champion-rounds** (HoR 648, Vendetta 531, Ryth 450, Marcella 435, Vesper 309).
  - The ward trails show that these are walks. Vendetta jumped from (40,12) at r1287 to the spawn (3,46) at r1298 (a recall, no death). It then walked (12,45), (22,45), (31,40), (26,30), (16,27), (9,19), (16,9), (26,0), (32,3), (34,9), (32,12), reaching (35,14) at r1455: **157 rounds without touching a camp**.
  - HoR did the same: recall at about r1310, back at (37,13) at r1457.
- **Root.**
  - On a map whose farm zone is about 65-100 path tiles from spawn, every heal or shop recall costs about 150 champion-rounds.
  - They recalled less (estimate 14 vs 32) and farmed both sides' wolves.

### 00swirl (L 128-1032, r1500)
- **Map.** 45x30; spawns (26-28,6-8) and (16-18,21-23), about 15 apart; altars (23,10) ours, (21,19) theirs.
  - The elk groups near our spawn: g12 Elkx2+GemCl+GoldCl (dUs 4); g14 Elkx2+GemClx2 (7); g7 Elkx2+GoldClx2 (8); g16 Elkx4+GemClx4+GoldCl (13); g5 Wolfx3+Elk+GemClx3 (17).
- **r0-300: we were fine.**
  - Kills on their HoR at r123 (14,14) and Ryth at r135 (18,11); gold 822 vs 605 at r250.
  - But **we captured none of the elk groups all game**, only the single-elk g10 (6x), gold g20 (12x), g9 and g0 on their side.
- **r300-1000: they grouped and we did not.**
  - r304 Vendetta (32,9) 1-vs-1; r311 Marcella (23,15) 4-gank; r325 HoR carrying 12 at (27,13) 4-gank; r468 HoR carrying 23 at (40,0).
  - Then spawn-exit kills: r750/r753 Vesper and Vendetta at (26,5); r873 (19,11); r918 (22,7); r982 (24,7); r999 (22,10).
  - Their Vesper finished all 9 families at r646 and stacked Bruiser S. Their gold went 1,677 (r500) to 6,759 (r1000).
- **Root.**
  - Kill-fuelled snowball by a 3-4-champion group against our scattered champions.
  - We never farmed the multi-elk groups next to our own spawn, which they took from r809.
  - Their 12/0 Vesper is the visible symptom.

## 3. Their strategy vs ours

### Where theirs was superior
| Gap | Size | Our code responsible |
|---|---|---|
| **A. Item plan: passives vs bare stats.** | Camp damage per 1k dealt 2.7-4.3x ours (expanse 492 vs 115). Emblems by r1000 12 vs 42 (swirl). Gold from 2-3x the clears. | `shop()` -> `bruiser_item()` with `BRUISER_PLAN` (q24 l.112-124, `JUNGLE_FIRST = False` l.126). We never own Jungle, Durability or Monster. `treasure_item()` only fires under `no_tribute`. T25 (Jungle-first) was rejected for fight blowouts, but **in expanse there were 4 kills in 1,345 rounds**, a pure farming race where Jungle/Durability win (Q28b). |
| **B. Solo-ability of the big elk groups scales with items for them, never for us.** | Expanse r1000+: they soloed 44-gem groups 7 times; our only capture took 4 champions for 11 gems each. Swirl: 0 captures of 5 elk groups within 17 tiles of our spawn. | `choose_target` chip model: `budget = maxhp - s*dmg_mult*(rng+1) - 80`, cycles > 4 means reject (l.1405-1412). `dmg_mult` = 0.7 only with Jungle (`jungle()`), which we never buy. When a group is not solo-ok, the claim multiplier **x1.2** (l.1427-1428) plus `tdps = dps + c*55` attracts more champions to the same group: the 4-champion g9 capture at r954, then a camp death at (8,64) at r983. |
| **C. Own-side circuit includes low-value gold clusters.** | Expanse: 46 vs 13 gold-cluster captures on mirror pairs; Wolfx2+GemCl+GoldCl 15 vs 0. Gold 6,515 vs 3,554 at r1000. | No proximity term in `choose_target` beyond `d` in the cost. Our champions range to far 44-gem corner groups (g9 at 53 tiles) as a pack, rather than circulating the near small groups. *Speculation:* the x1.2 pull and the 1.3 target hysteresis keep the pack together. |
| **D. Heal and shop trips on big maps.** | Estimated recalls vs theirs: dunes 39 vs 12, starvation 32 vs 14, expanse 36 vs 23. Starvation: a recall plus walk-back costs about 150 rounds. Quiet champion-rounds 2,373 (starvation). | `play_turn` recall rules: `low = hp < maxhp*0.45` or `rich = gold >= 150 and carried < 8` or `gold >= 400`, then recall (l.2521-2535). `G is None` means recall if `gold >= 60 or hp < 0.7*maxhp` (l.2608-2616). None of these looks at the distance home. The camp-damage gap (A) makes `low` fire 2-4x as often. |
| **E. Grouping in fights on small maps.** | Swirl: 14 of their 20 kills were 3-4-champion ganks; we spread over gold clusters on both halves (10 of our 31 captures on their side). | `group_balance` reacts only once enemies are within GROUP_R 7. Farming is per-champion with claims pushing champions *apart* (x0.3 for solo-ok claimed groups). Nothing regroups the team when the enemy moves as a pack. |
| **F. Spawn-exit deaths.** | Swirl: 7 deaths within 6 of our spawn, e.g. (26,5) x2 at r750-753, (22,7), (24,7), (22,10). | `play_turn`: `if at_spawn and hp < maxhp*0.92 and incoming == 0: return` (l.2483) heals on spawn, then each champion leaves alone as soon as it is full. With enemies waiting outside (vision 8), `handle_enemies` regroups toward allies, who are also respawning one at a time. Compare the queued "Spawn-pin escape". |

### Where ours was superior
- **Gold-tiebreak play.** the_pack: 19,400 vs 873 (h_goldtie in q24).
- **Early fights.**
  - Swirl: 2 kills by r135 with 0 losses.
  - Dunes r700-800: HoR killed Marcella, Vesper and Ryth (the last carrying 18).
  - the_pack: 3-0.
- **Early gem race.** We led at r1000 on expanse and dunes and were level on starvation: our opening banking is fine. The losses are all in the late game.

## 4. Our weaknesses exposed
| # | Weakness | Evidence | Games | Impact |
|---|---|---|---|---|
| W1 | **No passive-giving items (Jungle/Durability/Monster)**, so poor camp-damage efficiency and late scaling. | Camp damage per 1k: expanse 492 vs 115, dunes 1,042 vs 387, swirl 528 vs 182. Emblems by r1000 12 vs 42 (swirl). Gem windows after r1000: -452, -545, -164, -496. | 4 | decisive |
| W2 | **Big elk groups never become solo targets**; when they are taken, it is by a 4-champion pack. | Expanse: they soloed 44-gem groups 7 times after r1000, including our-side g5/g9. Our g9 capture at r954 had 4 champions, followed by a camp death at (8,64). Swirl: 0 of 5 near elk groups. | 2 | major |
| W3 | **Distance-blind heal/shop recalls on big maps.** | Starvation: 2,373 quiet champion-rounds; Vendetta's 157-round walk-back (r1298-1455). Estimated recalls: dunes 39 vs 12, starvation 32 vs 14. | 3 | major |
| W4 | **Own-side small-group circuit neglected** (gold clusters and Wolf+GemCl near spawn). | Expanse mirror pairs: 46 vs 13 gold clusters, 15 vs 0 Wolfx2+GemCl+GoldCl. Starvation: both wolves 27 vs 8. | 2 | major |
| W5 | **Scattered team against a grouping enemy on small maps; spawn-exit deaths.** | Swirl: 14 of 20 deaths to 3-4-champion ganks; 7 deaths near our spawn; K/D 5/20. | 1 | decisive |

## Testable hypotheses (structure-keyed; no map or team names)
1. **H-passives (W1; ladder evidence for Q28b, plus a new item order to test).**
   - **Variant (a), Q28b.** Jungle first while the team has seen little PvP.
   - **Variant (b), new.** Our Bruiser plan, but complete one Jungle and one Durability emblem as the 2nd and 3rd emblems on every champion, regardless of PvP.
   - **Evidence.** The opponent with our exact comp completes Jungle by r100-300 and Durability next, and out-farms us 2-3x in camp-damage efficiency.
   - **Metrics.** Camp damage taken per 1k dealt (target < 250); clears per 100 rounds after r1000; gem windows after r1000; fight K/D (must not drop vs the Q28 failure mode).
   - **Validate.** Against a mirror-comp opponent with this item loop (build an imitation, e.g. `imit_ww`: our bot plus the WW item order, to isolate the item effect).
2. **H-claimcap (W2): stop pack-farming one group.**
   - **Change.** In `choose_target`, drop the x1.2 not-solo-ok claim multiplier once a group already has >= 2 claimants, and cap `tdps = dps + min(c, 1)*55`. The 3rd+ champion should go elsewhere.
   - **Metrics.** Mean capture party size (scout `party.py`: expanse 1.82 in 300-1000); gems per champion-round; camp deaths in team clears.
3. **H-solo-recheck (W2): re-evaluate solo-ability with real mitigation.**
   - **Change.** Use `me.max_health()` and actual `dps(me)` *after items*, which is already done. Also include our Durability/Jungle in `dmg_mult`, so that once (1) lands, the 44-gem elk groups become solo targets (cycles <= 4).
   - **Metric.** Solo captures of groups with strength >= 100 after r800.
   - (This is the mechanism by which (1) pays off; test them together.)
4. **H-farzone-recall (W3): distance-aware recall.**
   - **Change.** When the path distance from the champion to our spawn exceeds ~30:
     - (a) skip the `rich` shop recall unless gold >= 300 *and* hp < 0.7*maxhp;
     - (b) before a `low` recall, prefer strength-0 targets (gem/gold clusters) within 10 while hp >= 0.3*maxhp.
   - **Metrics.** Estimated recalls per game (`recalls.py`); quiet champion-rounds; clears per 100 rounds on maps whose nearest altar is >= 40 path tiles from spawn.
   - **Interaction.** Keep the H-band fix (2026-11-01-b8923d32 report) in mind; it raises recalls in the 45-60% band.
5. **H-homecircuit (W4).**
   - **Change.** Add a small bonus (x1.2) for groups whose path distance to our spawn is less than to the enemy spawn *and* whose respawn is due within the walk time, so idle champions re-clear near groups instead of trekking.
   - **Distinct from** the rejected T8 (an enemy-half x0.4 penalty).
   - **Metric.** Captures of own-side groups per 1,000 rounds vs the enemy's on mirrors (`mirror.py`).
6. **H-packdetect (W5).**
   - **Trigger.** When >= 3 enemies are seen within 8 of each other (from any ally's vision, published in a shared byte).
   - **Effect.** Champions within 15 of that spot regroup at the nearest ally, and champions on spawn wait (up to 20 rounds) until 2 can leave together. Extends "Spawn-pin escape" with a trigger.
   - **Metrics.** Share of our deaths to 3+-champion ganks; deaths within 6 of our spawn.

**Opponent-specific notes (for ladder expectations, not for fixes).**
- A mirror-comp, solo-farming bot with a well-rounded passive item loop. It beats us in any long game on large maps.
- It is beatable early: we led at r1000 three times. Its 3-pick no-altar logic freezes.
- Expect losses to it until W1-W3 are fixed. Closing the game before r1000 (higher-value early targets) is the other lever.
