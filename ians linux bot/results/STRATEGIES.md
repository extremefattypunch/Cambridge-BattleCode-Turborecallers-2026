# Strategy backlog and results

**Rule (user, 31 Oct):** every simulated match must test a **new, meaningful, distinct strategy** with improvement potential, drawn from ladder research, our own bots or postmortems. No simulation for its own sake. Submissions = the strongest bot found.

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

## Queue (highest expected value first; refine with each ladder pull)
| # | Strategy hypothesis | Source | Why it might win |
|---|---|---|---|
| Q1 | **Counter the Varg + Cassi&Issac + Stellar burst comp**: e.g. spread out vs AoE (Stellar 1.4×F radius 1, Varg splash), focus Cassi/Issac (linked deaths = double kill), stun Stellar before her burst | v2's only real losses; v1's 0–5 sets | Most common mid-ladder comp; we lose to it |
| Q2 | **Gold-tiebreak play on gem-less maps**: detect "no safe gems" and maximise lifetime gold (gold clusters, kills, Vesper +33%) | 5/15 losses on the 70-map check were 0–0 tiebreaks | Free wins on gated/herd maps |
| Q3 | **Team assault on gated altars / herds** (reuse sf_maps detection + assault) | sf_maps + census §2.6 | 02guardians side A went 4/4 in isolation |
| Q4 | **Alert-triggered regrouping**: farm spread out, collapse within 3 tiles of a carrier on an enemy sighting or ally death | Census §2.4 (top-20 habit); "rigid cohesion failed" | Avoid being picked off by roaming comps |
| Q5 | **Early aggression / invade**: hunt enemy farmers on their half before round ~200 when we have a power spike | Census §2.8 (3+ early kills → 80% wins) | Snowball via kill gold and stolen gems |
| Q6 | **5-pick draft order** (Ryth 4th, Varg 5th, HoR 6th) | tb_merge_c experiment (+20% on 4/5-pick maps) | HoR is our weakest farmer |
| Q7 | **Carry concentration**: route captures to Vesper/Marcella for faster item spikes | Census §2.4 (Ad Astra) | Earlier carry power |
| Q8 | **Ward intel sharing**: put enemy sightings in shared byte 6 and feed them into fight and banking decisions | INSIGHTS §3 (comms lessons) | Allies avoid ambushes and join fights |
| Q9 | **Danger as path cost, not walls**: hazard memory as soft costs (tb_aggro idea) | GST / Pantheon postmortems | Fewer detours and stalls |
| Q10 | **Heavier TP-crystal use** on large or disconnected maps | Census crystal stats (01starvation 531, big_world 325) | Faster rotations on big maps |
| Q12 | **Win the early fights**: in 00dunes-type losses we died 6 times to champions before round 300, while their Vendetta/Vesper went 9-0/8-0. Avoid isolated early farming near the enemy, or group the first 300 rounds | analyze_match on the 70-map loss set | Losses start with an early gem deficit (−22 at r500) |
| Q13 | **Fuel budgeting in fights**: losses average 183 fuel exhaustions vs 69 in wins. Cap fight/retreat computation and pre-compute threat maps | analyze_match --summary (70-map run) | Suspended turns in fights = lost fights |
| Q14 | **Study team "test"'s real replays** (gemcombat4 `8c4e94e4-7f23-4397-ab51-52b0dbe993df`, 02arena `e73b0c3e-8bb6-4477-8203-703f51191555`): who killed us when, were tributes/recalls stunned. Needs a bundle download (browser or `cambc login`) | ladder-learning | Their play, not their draft, beat us; imitations can't reproduce it |
| Q15 | **Anti-stun channel rule**: don't start a tribute/recall with an enemy caster (Cassi/Stellar/Ren/Ryth) visible within ~5 | ladder-stats | Stuns cancel tribute/recall; test drafts many stuns |
| Q16 | **Varg with a Bruiser plan**, then retest lad_varg4 on all 70 maps | draft-imitation | Varg out-farms HoR by ~55 gems/game, but the swap was neutral (Varg had no item plan) |
| Q17 | **Cassi&Issac linked-fate logic** (keep both alive, kite together) | draft-imitation | Imitations' C&I died 6.5-7.5×/game; needed only if we draft them |
| Q18 | **3-pick draft with a stun anchor** (e.g. Vesper, Vendetta, Ryth) on 3-pick maps only | ladder-stats (02arena loss) | v2 is 0-1 on 3-pick maps, so untested |
| Q11 | **C++ port** (parallel track, user request) | User | Only if it beats the Python champion |
