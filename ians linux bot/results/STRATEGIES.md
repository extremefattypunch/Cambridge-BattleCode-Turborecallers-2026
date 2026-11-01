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

## Queue (highest expected value first; refine with each ladder pull)
| # | Strategy hypothesis | Source | Why it might win |
|---|---|---|---|
| Q24 | **Combined candidate (top priority)**: tb_merge_b + LOCK_MEMORY_FIX (h_3pick) + gold play (h_goldtie v2) + early-fight rule (h_earlyfight_all) + fuel caching (h_fightfuel). These touch different subsystems. Build it, run the analysis session, gate on all maps | batch-1 interim | Each piece is +0 to +3 games alone; together they may clear the 82/140 gate |
| Q20 | **TP-crystal into a guard-enclosed altar ring** (02the-pack: the ring is free inside 48 wolves; sleeping wolves don't attack) | h_goldtie analysis | Turns a real ladder 0-0 loss into a gem win |
| Q21 | **Universal respawn-rule movement fix** (01yellow-brick-road: champions froze ~1,700 rounds on a dead camp tile of a half-cleared group) | h_goldtie analysis | Bug fix |
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
