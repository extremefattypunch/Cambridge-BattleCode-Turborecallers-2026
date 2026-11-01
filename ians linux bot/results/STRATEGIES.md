# Strategy backlog and results

**Rule (user, 31 Oct):** every simulated match must test a **new, meaningful, distinct strategy** with improvement potential, drawn from ladder research, our own bots or postmortems. No simulation for its own sake. Submissions = the strongest bot found.

**Batch-1 interim results (interrupted 31 Oct):** see `results/experiments/2026-10-31-batch1-interim.md`. Analysis sessions and gates did **not** run for T15-T20.

**Side bias:** in a mirror, team B wins 15/20 sprint maps. Always evaluate both sides.

**Methodology note (31 Oct):** local games are **deterministic**: the same bots on the same map give byte-identical results. Never re-run a map; get more evidence by covering more maps (`--maps all` = 140 games). A 40-game sprint eval has about ±8% map-sampling noise.

**Test protocol:**
1. Implement the strategy in its own candidate bot (`tools/newbot.py <champion> <cand>`).
2. Screen it with `tools/eval.py <cand> <champion> --maps quick`. Where relevant, also test against imitation opponents of the real ladder comps that beat us.
3. Then apply the LOOP.md promotion gate.
4. Record the verdict below: kept, rejected or inconclusive. **Never re-test a rejected idea unchanged.**

Champion: see `results/CHAMPION`.

## Tested
| # | Strategy | Source | Result vs champion of the day | Verdict |
|---|---|---|---|---|
| T1 | Split-map farming (tb_splitfarm) vs deathball / aggro / economy designs | Builder round | 64% in the round-robin | kept as base |
| T2 | Kill-time fight/flee model + census banking (sf_bank) | INSIGHTS §2.3/2.8 | 82% vs sf_base | kept (in tb_merge_b) |
| T3 | Channel/carrier focus, altar locks, wards (sf_pvp) | INSIGHTS §2.5/2.8 | 78% | kept |
| T4 | Meta draft HoR/Vesper/Vendetta/Marcella/Ryth + Bruiser items (sf_draft) | Top-20 census | 72% | kept |
| T5 | Static distance-field cache + fuel guards (sf_fuel) | GST / Om Nom postmortems | 60%; fuel exhaustion −96% | kept |
| T6 | Map archetype profile (sf_maps: jackpot/gated/herd) | Census §2.6 | 52% (neutral) | inconclusive; parts reusable |
| T7 | Single capture recipient | Census §2.4 | lost 6-18 | rejected |
| T8 | Item-13 score multipliers (gold decay, enemy-half ×0.4) | Census §2.7 | lost 14-26 | rejected |
| T9 | Travel dash (Vesper/Vendetta) | Own idea | 67% vs 75% without | rejected |
| T10 | Literal census banking without fight model | Census §2.3 | lost 9-15 | rejected (only works with T2) |
| T11 | Ladder-common drafts with our logic: lad_vcst (Varg/C&I/Stellar/Tavi/Ren), lad_svrc, lad_hyb | Ladder 31 Oct | tb_merge_b won 68% / 80% / 60%, and 11-1 on the ladder-loss maps | rejected (draft isn't why we lose) |
| T12 | Varg replaces HoR at pick 4 (lad_varg4) | Ladder (Varg = top farmer) | 39W-41L (49%) over 80 games | inconclusive / neutral |
| T13 | Count enemy shield as HP in the kill-time model (tb_v3_cand) | Repro of the losses to "test" | 20W-20L vs champion; 80% vs imit_test (champion 85%) | rejected |
| T14 | Weight Stellar/Cassi burst higher in enemy_dps (tb_v3_burst) | Repro of the losses to "test" | 82% vs imit_test (champion 85%) | rejected |
| T15 | 3-pick play (h_3pick): lock-memory bug fix (kept), trio mode (rejected: 7-17 / 11-13) | Q18, ladder 3-pick losses | Lock fix: 13-11 on 3-pick maps, sprint 22-18; vs h3_tvv 19-5 (base 16-8) | **lock fix: candidate for Q24 combo**; trio mode rejected |
| T16 | Gold-tiebreak play (h_goldtie v2) | Q2 | 9-1 on the 5 tiebreak maps; sprint 21-19 | targeted win; candidate for the Q24 combo |
| T17 | Early-fight group rule (h_earlyfight v2 / h_earlyfight_all v3) | Q12 | v2 sprint 22-18, v3 sprint 23-17 (58%); v1 18-22 | promising; v3 goes into the Q24 combo + gate |
| T18 | Fuel caching for sensing/fights (h_fightfuel) | Q13 | sprint 22-18; 15-15 on another 37-map set | promising (fuel); in the Q24 combo |
| T19 | Anti-stun channel rule (h_antistun) | Q15 | sprint 20-20; vs imit_test 31-9 (base 33-7) | likely reject (analysis not run) |
| T20 | C++ faithful port (cpp_port) | Q11 | sprint 20-20 vs the Python champion; 0 fuel exhaustions | parity reached; keep as a platform for compute-heavy ideas |
| T21 | **Q24 combined candidate (q24_combo)**: lock-memory fix + gold-tiebreak play + group-balance fight rule (all game) + fuel caching | batch-1 interim | **87W-53L vs tb_merge_b on all maps (LB 0.539)**; gauntlet 174/200 vs 158; release clean; fuelExh 8.0 vs 67.9 | **kept: promoted to champion, website v3 (1 Nov)** |
| T22 | Q21 respawn-rule movement fix (h_respawnfix): two freeze causes on 01yellow-brick-road fixed generally | h_goldtie analysis | **92W-48L vs tb_merge_b on all maps**; sprint 23-17 | kept; next: merge into q24_combo and gate |
| T15b | h_3pick on all maps (analysis session) | Q18 | 75/140 vs tb_merge_b; frozen carriers −33% | kept (inside q24_combo) |
| T16b | h_goldtie on all maps | Q2 | 74/140; tiebreak maps won on gold; sprint subset did not reproduce the dev PC | kept (inside q24_combo) |
| T17b | h_earlyfight_all on all maps | Q12 | 84/140; our early deaths −23%, enemy early deaths unchanged | kept (inside q24_combo) |
| T18b | h_fightfuel on all maps | Q13 | 72/140; fuelExh −93%, in-fight suspensions −99%, no win gain alone | rejected alone; kept in q24_combo for fuel headroom |
| T19b | h_antistun on all maps | Q15 | 79/140; risky channel starts fell but events rare | rejected |
| T23 | **Q26 team bootstrap for wrapped/large groups (h_teamclear)**: when the solo safety check rejects a group, a team check with a muster gate lets the first champion commit so claims cascade | Ladder 02gift_wrapping 0-1028 / 16-1006 | **91W-49L vs tb_merge_b on all maps**; gauntlet 164/200 (tb_merge_b 158); 02gift-wrapping 0 clears → 20-22 clears, W 1002-0; ablation: wrap fix alone 82/140, team clear without it 64/140 | **kept**; next: port onto the champion line and gate |
| T24 | Q27 02treasure_box (h_treasure): spawn-heal-aware fighting + cluster-chain value + far-altar banking | Ladder 02treasure_box, lost 3 times | 72W-68L vs tb_merge_b; both mechanisms confirmed (spawn-heal engage turns 65% → 0%), but regressions offset the gain | inconclusive; refine (Q27b-d) |
| T25 | Q28 race tempo (h_tempo): Jungle-first farming item build + Strength arm | 7 lost ladder races | 75W-65L vs tb_merge_b; farming +2-10% but losses became fight blowouts | rejected as built; refinements Q28b-d |
| T26 | **c2_respawn** = q24_combo + Q21 respawn fix | T22 | **89W-51L vs q24_combo (LB 0.553)**; gauntlet 177/200 vs 174; 98/140 vs tb_merge_b; placebo replicate 83/140 | **kept: promoted, website v4 (1 Nov)**; known 3-pick mirror-draft regression |
| T27 | Q30 large-map fix (h_bigmap): claim-rule target 2-cycle in choose_target | q24 gate report | 80W-60L vs q24_combo (LB 0.489) | fails the gate by 2; merge component |
| T28 | Placebo calibration (null changes vs q24_combo) | h_antistun hypothesis | 66/140 and 68/140 (mirror 70); 85 and 90 vs tb_merge_b | the gate's noise floor is below binomial; keep the gate |
| T29 | v3 ladder study (is q24_combo worse than v2 on the ladder?) | ladder 1 Nov | 25 mislabelled games found; rating-controlled −54 Elo [−166, +65], p 0.36; mechanisms 2-4 confirmed on real games | keep v3; successors must also beat tb_merge_b |
| T30 | c3_teamclear = q24_combo + Q26 team bootstrap | T23 | 80W-60L vs q24_combo (LB 0.489); gauntlet 176/200 vs 174; fuel 9.5 vs 7.3 per game | **gate failed**. Team clears fix 02gift-wrapping (0 → 19 clears, W 1000-0, beats starter-python), but muster idling (139 turns/game) cancels the gain elsewhere. Next: team clear only as a fallback when no solo target exists |
| T31 | Q27 refined: spawn-heal-aware fighting with fixes (h_spawnheal) | T24 | 74W-66L vs q24_combo | inconclusive |

## Queue (highest expected value first; refine with each ladder pull)

**Blind spot (1 Nov):** every local opponent (sf_*, tb_*, imit_*, lad_*, h3_*) runs our own farming and safety logic, so maps where *our logic* scores 0 look like 0-0 ties locally. Real opponents score 1000 there (Q26, Q27). Judge map-structure fixes by our own clears and tributes, not only by the local result.
| # | Strategy hypothesis | Source | Why it might win |
|---|---|---|---|
| Q20 | **TP-crystal into a guard-enclosed altar ring** (02the-pack: the ring is free inside 48 wolves; sleeping wolves don't attack) | h_goldtie analysis | Turns a real ladder 0-0 loss into a gem win |
| Q22 | **Open-gate rush**: on no-tribute maps, when a guard dies, rush the carried gems to the altar | h_goldtie analysis | Converts big carried bags |
| Q23 | **Map analysis in the draft** (250M fuel) via draft memory; keep turn 1 fuel-identical | h_goldtie analysis | Removes turn-1 divergence and frees fuel |
| Q25 | **Cheaper sensing**: cache camp reads per turn and skip ward-only camps in observe/threats (Python and C++) | h_fightfuel profiling | observe+threats cost 1-2.6M per turn |
| Q1 | **Counter the Varg + Cassi&Issac + Stellar burst comp**: e.g. spread out vs AoE (Stellar 1.4×F radius 1, Varg splash), focus Cassi/Issac (linked deaths = double kill), stun Stellar before her burst | v2's only real losses; v1's 0–5 sets | Most common mid-ladder comp; we lose to it |
| Q2 (tested T16) | **Gold-tiebreak play on gem-less maps**: detect "no safe gems" and maximise lifetime gold (gold clusters, kills, Vesper +33%) | 5/15 losses on the 70-map check were 0–0 tiebreaks | Free wins on gated/herd maps |
| Q3 | **Team assault on gated altars / herds** (reuse sf_maps detection + assault) | sf_maps + census §2.6 | 02guardians side A went 4/4 in isolation |
| Q4 | **Alert-triggered regrouping**: farm spread out, collapse within 3 tiles of a carrier on an enemy sighting or ally death | Census §2.4 (top-20 habit); "rigid cohesion failed" | Avoid being picked off by roaming comps |
| Q5 | **Early aggression / invade**: hunt enemy farmers on their half before round ~200 when we have a power spike | Census §2.8 (3+ early kills → 80% wins) | Snowball via kill gold and stolen gems |
| Q6 | **5-pick draft order** (Ryth 4th, Varg 5th, HoR 6th) | tb_merge_c experiment (+20% on 4/5-pick maps) | HoR is our weakest farmer |
| Q7 | **Carry concentration**: route captures to Vesper/Marcella for faster item spikes | Census §2.4 (Ad Astra) | Earlier carry power |
| Q8 | **Ward intel sharing**: put enemy sightings in shared byte 6 and feed them into fight and banking decisions | INSIGHTS §3 (comms lessons) | Allies avoid ambushes and join fights |
| Q9 | **Danger as path cost, not walls**: hazard memory as soft costs (tb_aggro idea) | GST / Pantheon postmortems | Fewer detours and stalls |
| Q10 | **Heavier TP-crystal use** on large or disconnected maps | Census crystal stats (01starvation 531, big_world 325) | Faster rotations on big maps |
| Q12 (tested T17) | **Win the early fights**: in 00dunes-type losses we died 6 times to champions before round 300, while their Vendetta/Vesper went 9-0/8-0. Avoid isolated early farming near the enemy, or group the first 300 rounds | analyze_match on the 70-map loss set | Losses start with an early gem deficit (−22 at r500) |
| Q13 (tested T18) | **Fuel budgeting in fights**: losses average 183 fuel exhaustions vs 69 in wins. Cap fight/retreat computation and pre-compute threat maps | analyze_match --summary (70-map run) | Suspended turns in fights = lost fights |
| Q14 | **Study team "test"'s real replays** (gemcombat4 `8c4e94e4-7f23-4397-ab51-52b0dbe993df`, 02arena `e73b0c3e-8bb6-4477-8203-703f51191555`): who killed us when, were tributes/recalls stunned. Needs a bundle download (browser or `cambc login`) | ladder-learning | Their play, not their draft, beat us; imitations can't reproduce it |
| Q15 (tested T19) | **Anti-stun channel rule**: don't start a tribute/recall with an enemy caster (Cassi/Stellar/Ren/Ryth) visible within ~5 | ladder-stats | Stuns cancel tribute/recall; test drafts many stuns |
| Q16 | **Varg with a Bruiser plan**, then retest lad_varg4 on all 70 maps | draft-imitation | Varg out-farms HoR by ~55 gems/game, but the swap was neutral (Varg had no item plan) |
| Q17 | **Cassi&Issac linked-fate logic** (keep both alive, kite together) | draft-imitation | Imitations' C&I died 6.5-7.5×/game; needed only if we draft them |
| Q18 (partly tested T15) | **3-pick draft with a stun anchor** (e.g. Vesper, Vendetta, Ryth) on 3-pick maps only | ladder-stats (02arena loss) | v2 is 0-1 on 3-pick maps, so untested |
| Q19 | **Mirror-meta matchups at ~1500**: Halma _und _Oleck and The Dreamyard draft our exact meta comp (Vesper/Vendetta/Marcella/HoR + Ren/Ryth) and beat us 3-2 each (00quadrants lost by r737, 02uncharted_lands, 00lanes, adgato_gemcombat4, 01fracture, 02famine). Study their replays: target choice, fight timing, items, tribute size. Then test the specific behaviour differences | Ladder 31 Oct ~23:30 UTC | Our 5-pick record fell from 18/20 to 23/32 as our rating rose; the mirror is the main matchup at higher rating |
| Q11 | **C++ port** (parallel track, user request) | User | Only if it beats the Python champion |

## New hypotheses from batch 2 (1 Nov; details and evidence in each report under results/experiments/)
| Hypothesis | Source report | Why it might win |
|---|---|---|
| Q29: side-B opening skirmish on fight maps | q24 gate report | On these maps the opening skirmish decides a 1,000-gem landslide. Tracing group_balance commit/regroup and camp threat in the r<300 fights (cambc run stdout on 01hooks B and 00gem-fields B) could convert 4-5 games, about |
| Q30: large-map farming tempo / 02tangle clear collapse | q24 gate report | Unseen sprint maps include large ones. A fragile farming state that any divergence can fall into costs whole races; this extends Q28. |
| Q31: turn-1 fuel on 100x100 maps (concrete Q23) | q24 gate report | Moving the map analysis into the draft (250M fuel) via draft memory frees the opening turns on exactly the maps where q24 is weakest. |
| Q32: stall-map gold race (00stampede) | q24 gate report | Switching to no_tribute valuation (Treasure first, gold value, no banking walks) when stalled past about r1000 at 0-0 would win gold tiebreaks on stall maps, which real ladder 0-0 games are decided by. |
| Camp-gate vision-flicker 2-cycle fix: remember static camp tiles as walls, or add path hysteresis | 2026-11-01-h_3pick.md | The same freeze shape as the lock bug, still in both bots. Treating remembered live camp tiles as walls, or committing to a route after an A,B,A,B pattern, unfreezes carriers that hold 15-66 gems for 100-400 rounds. |
| Lock-and-hunt: after placing an altar lock, hunt enemy carriers at the lock's vision edge | 2026-11-01-h_3pick.md | Ladder bots with the same lock-memory gap park full bags at a predictable spot. Killing them steals gems and swings the race. |
| Spawn-pin escape: detect a champion repeatedly healing at spawn under enemy fire and sortie as a group | 2026-11-01-h_3pick.md | These are the two worst non-structural losses. Breaking the pin, by regrouping, recalling elsewhere or engaging together, turns total shutouts into contested games. |
| Cheaper lock memory: cache locked_altars() once per turn | 2026-11-01-h_3pick.md | Keeps the confirmed fix while removing fuel overhead. Gate (c) needs fuelExhausted not worse than the champion's, and less fuel pressure means fewer suspended turns. |
| Methodology: a null-change calibration run (tb_merge_b plus one dead API call per turn vs tb_merge_b, all maps) | 2026-11-01-h_3pick.md | Measures the real noise floor of the 140-game gate, so single-mechanism fixes like this one (confirmed mechanism, 54% head-to-head) can be judged correctly. It also shows whether merges like Q24 need paired mechanism met |
| Universal idle chip mode (don't end chip mode at the first tribute) | 2026-11-01-h_goldtie.md | Wrapped and strong-camp maps keep yielding clears, gold and gems. A ladder opponent who keeps chipping would out-farm our 60 gems. |
| Buy Treasure emblems when 'stalled' persists late, not only under no_tribute | 2026-11-01-h_goldtie.md | +10% lifetime gold exceeds typical stalled-game gold margins and flips gold tiebreaks. |
| Make the respawn-rule movement fix unconditional (raise Q21) | 2026-11-01-h_goldtie.md | Unfreezes our team on maps with half-cleared groups. That turns a coin-flip map into a farm win and removes a large fuel sink. |
| Sole-gem-herd assault when both teams are at 0 tributed (Q3-adjacent) | 2026-11-01-h_goldtie.md | A deliberate team assault on the only gem herd decides stalled games outright instead of leaving them to the gold tiebreak. |
| Fuel-independent decisions: fixed work quotas, or static fields precomputed in the draft (extends Q23) | 2026-11-01-h_goldtie.md | Stable play makes small real gains (like this +4) measurable and stackable for the 82/140 gate, and stops results drifting between machines and builds. |
| Open-gate rush on no_tribute maps (Q22 evidence) | 2026-11-01-h_goldtie.md | If any guard dies, one tribute run of 1,000+ gems wins instantly instead of relying on the gold tiebreak. |
| Contested-objective exception to the group-balance 'disadvantage' retreat (fix the seat-B regression) | 2026-11-01-h_earlyfight_all.md | When we contest an altar, or the enemies in range are channelling or low, keep tb_merge_b's engage logic (or lower GROUP_DISADV from 0.75 to about 0.6). This could keep seat A's +13 and recover seat B's lost contests, tu |
| Death-site and fed-carry avoidance via shared memory (feeding stop) | 2026-11-01-h_earlyfight_all.md | Write the last ally death x, y and round into the 8-byte shared memory. Skip camp groups within about 5 tiles of it for about 100 rounds unless group_balance is at least 1.4, and treat an enemy whose strength is at least |
| Endgame carrier audit: frozen carriers and late pickups | 2026-11-01-h_earlyfight_all.md | Check whether LOCK_MEMORY_FIX (h_3pick) or the Q21 respawn fix clears the 00ambush freeze. Then forbid new captures whose capture time plus the walk to an altar can't finish by r2000. That could flip up to 4 close games. |
| Fuel headroom as a stability lever (supports Q25 cheaper sensing) | 2026-11-01-h_earlyfight_all.md | Many turns sit at the fuel cap, so tiny code changes shift exhaustion timing and outcomes chaotically. More headroom makes gate results less noisy and fights more reliable, as well as freeing compute. |
| Opening centre-collision grouping (commit-side of the rule) | 2026-11-01-h_earlyfight_all.md | Hold the first approach to the map centre until 2 or more allies are within 4 tiles. The current rule avoids bad early fights but doesn't create good ones (enemy early deaths are unchanged at 1.71 vs 1.73), so a coordina |
| First-strike spacing in early duels (turn-level initiative) | 2026-11-01-h_fightfuel.md | Early duels between identical champions are decided by who lands the first hit, and those early kills decide most games. Before r300, never end a turn inside an equal-or-stronger enemy's threat range (attack range + move |
| Spend h_fightfuel's freed fuel on exact early-fight evaluation | 2026-11-01-h_fightfuel.md | Fuel headroom only helps if it buys better decisions. Build on h_fightfuel and add an engage/flee duel or skirmish simulation (HP, damage, cooldowns, alternating starting team, stun timing). That targets the actual decis |
| Check whether the fuel fix helps against non-mirror burst comps (lad_vcst) | 2026-11-01-h_fightfuel.md | The fix is neutral in the mirror because the mirror rarely fights while suspended. Against fight-dense burst comps, in-fight suspensions do appear and correlate with deaths. A 40-game paired sprint gauntlet entry vs lad_ |
| Noise-calibrated evaluation: equal-fuel placebo controls and perturbation replicates | 2026-11-01-h_antistun.md | A neutral change scores 70 ± 6.6/140 (± 3.2/40 on sprint), so the >=55% sprint screen passes about 30% of no-op changes. Seeded no-op fuel-burn variants of candidate and champion would give independent games per map (mor |
| No recall in contact: retreat on foot, recall only when disengaged | 2026-11-01-h_antistun.md | Removing even half of these deaths cuts our deaths by about 10% and gem losses by about 10%, and the losses are decided by K/D and gems lost (125 vs 69). recall_safe's kill-time model evidently lets champions start recal |
| Smaller bags when stunners are around (stun-aware banking threshold) | 2026-11-01-h_antistun.md | Tribute length is ceil(gems/10) turns. Keeping channels at 3 turns or fewer when the enemy roster has stunners and one was seen nearby recently attacks the exposure that a vision-based start rule cannot see; most stun-cu |
| (Merge-only) Narrow anti-stun: tributes only within true reach, recalls with the +1 margin | 2026-11-01-h_antistun.md | This keeps the per-event benefit (threatened channels cut 23-43%) while dropping useless tribute deferrals. The total value is at most about 1 game per 140, so only fold it into a merge, never test it alone. |
| Fix tb_merge_b's caught exceptions that lose turns | 2026-11-01-h_antistun.md | Each one is a lost turn, often in a fight. Cheap robustness to bundle with another change; the effect alone is tiny. |
| Universal oscillation guard (any branch) | 2026-11-01-h_respawnfix.md | The stuck guard only counts farming turns with no move and no attack, so any alternating move defeats it. A guard that detects pos[t]==pos[t-2] (or stationary with no attack) for >= 8 turns in any branch, then commits to |
| Contested-capture standoff on long camp groups | 2026-11-01-h_respawnfix.md | Capture progress resets while any enemy is in the region, so on long groups an idle enemy anywhere blocks it forever. Abandoning after ~10 contested rounds, or contesting/killing the blocker, frees the champion and its t |
| Target-choice hysteresis | 2026-11-01-h_respawnfix.md | Committing to a target (switch only if the new score is >= 20% better for several turns) removes a pre-existing idle source that also defeats the stuck guard. |
| Per-camp death-trap memory | 2026-11-01-h_respawnfix.md | Hard-banning a group after 2 deaths to it, or requiring full HP plus an ally, saves the carried gems (11 were lost there) and the respawn time. |
| Respawn denial as a tool (speculative) | 2026-11-01-h_respawnfix.md | An idle champion could park on a high-value respawning group on the enemy's side and deny it gems and gold. Test only after the oscillation guard. |
| Add freeze_metric to every gate analysis | 2026-11-01-h_respawnfix.md | It catches new stalls before they cost games, and it measures idle time for Q28 (where our time goes). |

## New hypotheses from ladder-learning 1 (1 Nov)
| Hypothesis | Source report | Why it might win |
|---|---|---|
| Merge Q26 team bootstrap into the Q24/Q21 combo | 2026-11-01-h_teamclear.md | The team bootstrap only pays off on top of a fix for frozen champions, and the Q21 fix is the one already gated. Merge TEAM_CLEAR, TEAM_TANK_CHECK, TEAM_MUSTER, TEAM_WRAP_FIX(a), the dead mark 255 and presence byte 6 int |
| Gold-valued team targets on no-tribute maps (with h_goldtie no_tribute) | 2026-11-01-h_teamclear.md | Gold decides these maps, and the team option ranks groups by gems. |
| Heterogeneous team sizing from teammates' published tank budgets | 2026-11-01-h_teamclear.md | A faster first clear of the most valuable group, and fewer wasted musters. |
| Shared camp-kill state to drop stale hidden-camp threats | 2026-11-01-h_teamclear.md | Avoids phantom retreats and lost tempo in team play. Publish a per-group alive bitmask, or decay the belief once the engine state reads RewardAvailable or Respawning. |
| Deliberate aggro rotation in team fights | 2026-11-01-h_teamclear.md | Each aggro holder can absorb only about maxhp - s*(rng+1) before fleeing. Rotating the tank (step out at the threshold while the next-nearest steps in) could unlock these groups early. |
| Q27b: touching-spawn exception for the spawn-adjacent rule | 2026-11-01-h_treasure.md | When spawns touch, both sides heal next to their spawn. Skipping enemies adjacent to their spawn then concedes fights and farming. Apply the skip only when we are not within 1 of our own spawn, or when the spawn regions  |
| Q27c: gold floor for the chain bonus | 2026-11-01-h_treasure.md | The chain term lifts gem clusters to about 28 value while gold clusters stay at 5-20, starving item purchases. In any contested game, itemless champions lose every fight. Count H.value (with gold) in the chain, or keep n |
| Q27d: capped delivery term | 2026-11-01-h_treasure.md | A capped term, e.g. min(0.5*d, W*altar_d*share/15), or one restricted to the altar's walk component, may keep the head-to-head gain without the stall. Also check FAR_ALTAR_BANK and turret-avoid walks near Monolith-guarde |
| Willow heal-sink comps (EXP'D imitation) | 2026-11-01-h_treasure.md | The heal-aware chase guard removed starter-python's Willow sink (311k -> under 1k), but no local opponent pairs a healer with competent farming. Build lad_expd to test the guard against off-spawn heal sinks. |
| Evaluation noise floor and non-reproducibility | 2026-11-01-h_treasure.md | A single 140-game gate cannot attribute differences of about 5 games. Measure the null distribution (a flags-off copy of the champion, all maps). Find the nondeterminism source (debug vs release fuel metering; id()-hashe |
| sub7anr-style imitation opponent for the cluster-field blind spot | 2026-11-01-h_treasure.md | Locally no opponent contests the field, so we cannot yet tell whether h_treasure's successors win the field fight or only farm it unopposed. |
| Q28b: adaptive emblem order by observed PvP pressure | 2026-11-01-h_tempo.md | Buy Jungle first only while the team sees little PvP; for example, no ally has been killed by an enemy champion and no enemy champion has been seen near our camps by the first emblem. Otherwise, or after the first PvP de |
| Q28c: Jungle item without riskier targeting | 2026-11-01-h_tempo.md | Leave choose_target's dmg_mult at 1.0, or use it only in the HP budget and not the cycle test, while keeping the Jungle passive. This isolates a behavioural cause (bigger or farther groups at lower HP, so more exposure)  |
| Q28d: Strength arm alone (Monster emblem + Strength-weighted Bruiser), without Jungle | 2026-11-01-h_tempo.md | This may close the late damage gap without the camp-damage-vs-fight trade that sinks the Jungle build on brawl maps. |
| Fuel-dependent non-determinism of local games | 2026-11-01-h_tempo.md | It undermines the 'deterministic, never re-run' rule and adds noise to gate counts on fuel-heavy maps. Q25 (cheaper sensing) would also restore reproducibility. Test: run one pair twice on those maps and diff the results |
| Altar-camping death loop | 2026-11-01-h_tempo.md | After k deaths at the same altar within N rounds, switch altars or regroup before tributing. Any camped single-altar map otherwise becomes a zero-score game, as in the 02treasure_box pattern. |

## New hypotheses from batch 3 and the v3 ladder study (1 Nov)
| Hypothesis | Source report | Why it might win |
|---|---|---|
| V3L-1 Focus-burst threat model | 2026-11-01-v3-ladder-study.md | enemy_dps = strength + 0.15 x focus underrates Power Focus Stellar and Ren nukes. Against Us V Them we went 3-7 with 29 deaths per game, and were spawn-camped on 00packs 0-1020 and 85-1005. Change: score spell burst (multiplier x focus when the spell is off co |
| V3L-2 01shortcut stuck champion | 2026-11-01-v3-ladder-study.md | A champion idles with 0 gems for 1,300-1,700 rounds. v3 went 0-3 on 01shortcut, and v2 shows the same behaviour. It reproduces locally (gate-q24-all 01shortcut__B Vendetta r886-1596; b1-tb_merge_b-mirror-all 01shortcut__A Vendetta r1059-2001). Trace one determ |
| V3L-3 Boss-camp commit timing | 2026-11-01-v3-ladder-study.md | On 00contest the ladder opponent took the 200-gem boss bags 5 times from r800, and we took none despite 88 clears against 49. Local q24 only takes the boss at r1440-1700. Commit earlier when gems come from one giant camp. |
| V3L-4 Economy gap against teams rated 1530+ | 2026-11-01-v3-ladder-study.md | In v3 losses, opponent gold averaged 7,815 against our 4,143, and they cleared 4.9 camps per 100 rounds against our 2.4. They snowballed on Treasure x20-28 and Bruiser Strength x27 builds. Test farming tempo and item builds against imitations of real 1530+ com |
| V3L-5 Whole-set collapses against specific comps | 2026-11-01-v3-ladder-study.md | 5 of 17 v3 sets had 1 win or fewer, against 0 of 22 for v2 (set-variance permutation p 0.03), with the same draft in both versions. The sets were AI Coliseum 0-5 (Vendetta, Cassi&Issac, Ryth, Stellar), Mein Kraft 0-5 (Vesper, Tavi, Varg, Willow, Cassi&Issac),  |
| V3L-6 01xx and 4-pick marginal weakness | 2026-11-01-v3-ladder-study.md | On the ladder v3 went 8/21 on 01xx maps against v2's 13/17 (p 0.006 uncorrected), and 6/14 on 4-pick maps against 13/17. Self-play does not reproduce it: locally q24 went 19/30 on 01xx and 20/32 on 4-pick. Test only with V3L-1 or V3L-5 opponents, never as a se |
| Tooling: tools/ladder_pull | 2026-11-01-v3-ladder-study.md | py should store createdAt in each row and re-derive v for all rows on every run, with the rule 'version = newest version whose predecessor's statusAt is at or before the set's finishedAt'. That rule fits both observed switches. ladder-versions.json '2' holds v |
| c2 H1: step-off deadlock with an enemy in sight (fix candidate for c2) | 2026-11-01-c2_respawn.md | leave_respawn_tile fires only on quiet turns. With idle enemies in sight, a champion on a Respawning spawn tile is never moved, so the group never respawns. That would lose games against opponents that keep farming. Plan |
| c2 H2: gold-play cost of R2 (extends Q32) | 2026-11-01-c2_respawn.md | Tiebreak and ladder 0-0 maps are decided by tiny gold margins. Plan: compare gold-per-round curves and test restoring the narrowed blocks_respawn push-back in gold play only. Weak evidence (2 games): a watch item. |
| c2 H3: contested-capture standoff is now the largest remaining freeze (existing open item, new evidence) | 2026-11-01-c2_respawn.md | With the respawn rule fixed, champions reach contested rows more often. Plan: a capture-branch timeout that fights or retargets after N progress resets with an enemy on the region. |
| c2 Q30 re-measure: large-map weakness largely solved by c2 | 2026-11-01-c2_respawn.md | Re-measure Q30 (large-map farming tempo) on c2 before investing in it; much of q24's large-map weakness looks like the respawn-rule bug. |
| c2 Q29 evidence update: early-fight blowouts remain the main loss class | 2026-11-01-c2_respawn.md | This is the biggest remaining source of losses vs the champion line; Q29 stays top priority. |
| **c2 3-pick mirror-draft regression** (skeptic): vs tb_merge_b c2 won 10/24 3-pick map-sides where q24 won 19/24; 11.2 vs 6.5 deaths per game. Fix candidates: step-off rule only off-fight, or q24 behaviour on 3-pick drafts (team size, not map names) | c2 skeptic | c2 is live; 3-pick maps are ~17% of ladder games |
| c4 = q24 + respawn fix (c2) + team clear (c3) + h_bigmap v2 claim fix and cycle guard | 2026-11-01-h_bigmap.md | Three complementary freeze removals in different code paths. Each is mechanism-confirmed, and each is near or above the gate alone. |
| Fight-standoff breaker in handle_enemies | 2026-11-01-h_bigmap.md | This is the largest remaining class of 2-cycle turns. The fight branch returns before any target logic, so the cycle guard cannot reach it. After N quiet turns in that band: commit if the ratio is above 1, else disengage |
| Cycle guard: perturb movement instead of banning targets when the position cycle survives a ban | 2026-11-01-h_bigmap.md | Target-independent movement cycles exist, and serial bans throw away good targets. Marking the tile pair as no-enter for pathing for about 20 rounds would break them directly. |
| Late-race gem protection on big maps | 2026-11-01-h_bigmap.md | The farming fix now builds leads on big maps that are given back in late fights. Banking before engaging while carrying 15 or more gems after about r1000 could keep them. |
| Seat-specific big-map losses: 01big-world seat A and 00ambush seat A | 2026-11-01-h_bigmap.md | A seat effect that is consistent across bots points to a geometry problem (altar choice or a guarded path) worth one traced study. These maps are where big-map losses remain. |
| Q31 still open: move init_gold's reachable_tiles flood out of turn 1 | 2026-11-01-h_bigmap.md | It costs about 1 opening round on exactly the large maps this experiment targets. |

## New hypotheses from batch 4 (1 Nov)
| Hypothesis | Source report | Why it might win |
|---|---|---|
| c4: team option only as an idle fallback, built on the c2_respawn champion | 2026-11-01-c3_teamclear.md | It keeps the ladder-relevant 02gift-wrapping fix (0-80 to 1000+ vs starter-python) and removes the muster and capture-split costs where solo farming already works. c2 supplies the Q21 freeze fix that team clear needs (h_ |
| Lazy boss gate: compute Group.boss on first use, not with one is_monolith() call per camp at init | 2026-11-01-c3_teamclear.md | It makes gate (c) pass and gives back the first turn on large maps at essentially zero risk. |
| Cumulative muster budget per group and per champion; no musters toward far groups on large maps | 2026-11-01-c3_teamclear.md | The resettable 15/30-round clocks let a champion idle for hundreds of rounds; a budget caps the downside while keeping productive musters. |
| Altar-camp standoff breaker | 2026-11-01-c3_teamclear.md | When behind with no banking progress for ~150 rounds and enemies idle near the altar: heal to full, lower the bank threshold, and commit all champions together or bank elsewhere. It removes a round-limit loss to passive  |
| Gate reports must split targeted vs off-target maps and census the new logic's activity | 2026-11-01-c3_teamclear.md | It stops re-roll gains being credited to a mechanism and shows where a refinement should aim. |
| Q27e: handle spawn-parked enemies as a hazard to avoid, not ignore, against fighters | 2026-11-01-h_spawnheal.md | When all near enemies are spawn-healed, handle_enemies returns False and we farm on inside their range. Stepping out of their range, treating them as awake camps even on touching maps, and re-engaging when they step off  |
| Q27f: win the opening gold race on cluster maps (Q27c residue) | 2026-11-01-h_spawnheal.md | A per-champion floor with a 100-round grace still lets the chain go gem-first in the opening, and on item-driven maps that snowballs. Try: no chain until the first Bruiser emblem (150 gold), a team-level floor in shared  |
| Q27g: altar-box exemption from the gold floor to reach r700 on 02treasure_box | 2026-11-01-h_spawnheal.md | Groups inside the altar's own walled component and within ~8 steps of its ring could chain without the gold floor, buying treasure-box pace without the breadcrumbs gold loss (those clusters are not altar-boxed). |
| Q27h: build a heal-hopper imitation opponent (merge with Q29/Q31) | 2026-11-01-h_spawnheal.md | The spawn-adjacent rule, and Q27e, can only be evaluated against an opponent that steps on its spawn below ~60% HP and steps out to fight, e.g. Willow + Vesper + Tavi. |
| Q30 addendum: judge screened candidates on non-screen maps; renames are safe, source edits are not | 2026-11-01-h_spawnheal.md | Screen selection inflates the gate on screen maps. Reporting the off-screen share removes that bias, and single-map outcome claims need at least 2 perturbations. |
