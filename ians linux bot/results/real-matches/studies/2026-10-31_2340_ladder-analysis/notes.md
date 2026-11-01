# Real-ladder analysis, 31 Oct 2026 (Sprint 3 day)

This covers 80 ranked games in 16 sets: v1 (`tb_splitfarm`) played 65 and v2 (`tb_merge_b`) played 15. Sources are `matches/ladder/matches.json` and `matches/ladder/raw/match_groups.json`. I checked /game/matches at about 22:20 UTC and nothing new had finished; the next set (v2 vs fa_kyuu) was queued.
To reproduce, run `python3 -I postmortems/ladder_stats.py .` from the workspace root (pure Python, no CPU load). All tables below come from its output.

**Read every number with its sample size.** v2 has only 15 games against 3 teams, and v1 has 65 games against 13 teams. Results cluster by opponent team, so the effective sample is closer to the number of *sets* (3 and 13) than the number of games.

## 1. Headline

| | Games | Win % (95% CI) | Sets | Avg gems us–them | Avg opp rating | Rating |
|---|---|---|---|---|---|---|
| v1 tb_splitfarm | 18W-47L | 28% (18–40%) | 3W-10L | 352–779 | 1447 | 1500 → 1407 |
| v2 tb_merge_b | 13W-2L | 87% (62–96%) | 3W-0L (5-0, 5-0, 3-2) | 769–309 | 1419 | 1407 → 1442 |

- **The rating step depends on the set score, not just the set result.** The site shows ±16 for a 5-0 set, ±10 for 4-1 and ±3 for 3-2 between near-equal teams. A 3-2 set win is worth about a fifth of a sweep, so every game counts.
- **Implied game-level performance rating:** v1 ≈ 1280 (CI 1180–1380) and v2 ≈ 1745 (CI 1500–1970). The gap is about **+465 Elo**, with a very wide CI (roughly +130 to +790).

## 2. Breakdowns

### 2.1 Team size (number of picks)
| | 3-pick | 4-pick | 5-pick |
|---|---|---|---|
| v1 (Vendetta, Varg, Ryth, +Vesper, +Marcella) | 3W-9L, gems 141–700 | **1W-11L**, gems **94–894** | 14W-27L, gems 490–768 |
| v2 (Vesper, Vendetta, Marcella, +HoR, +Ryth) | 0W-1L (02arena) | **6W-0L**, gems 917–179 | 7W-1L |

- v1's 4-pick draft (Vendetta, Varg, Ryth, Vesper: no Marcella, no HoR) was a disaster.
- v2's meta core went 6-0 on 4-pick maps. The one v2 3-pick game was a loss, but n=1.

### 2.2 End reason and game length
| | gems (someone reached 1000) | tiebreak_gems (r2000) | tiebreak_gold / second_team (0–0) |
|---|---|---|---|
| v1 | 10W-36L, mean 1354 rounds | 4W-10L | 4W-1L |
| v2 | 9W-1L | 3W-1L | 1W-0L (01yellow_brick_road, won only because we were Team B) |

v1's 47 losses:
- **34 were blowouts** (our gems under 40% of theirs). Only 5 were close (at least 70%).
- In 8 the opponent reached 1000 before round 1000; we averaged 72 gems in those. 21 more ended between r1000 and r1599 (we averaged 189), 7 at r1600 or later (297), and 11 on the r2000 tiebreak (307 vs 677).
- **So v1 was out-scored about 2.5× on average, not edged out.** That fits being killed or out-farmed for the whole game, not a late-game banking problem.
- We did not have replays, so I could not split "out-farmed" from "out-fought". The CLI isn't logged in, and the bundle in `raw/` is only a pending-job stub.

v2's two losses were both against team **test** (1432):
- **adgato_gemcombat4** (5-pick): they reached 1000 by **round 577**, 1018–361. That is the fastest loss in the whole dataset. Out of 80 games, the opponent got under r750 only 3 times; the other two were v1 games at 742 and 753.
- **02arena** (3-pick): 298–932 at the r2000 tiebreak.
- Their drafts were Varg, Ryth, Cassi&Issac, Ren, Stellar, and Varg, Cassi&Issac, Stellar.

### 2.3 Opponent draft composition
The mid-ladder meta is **not** the top-20 meta. Pick counts over 80 games:

| | Picks |
|---|---|
| Mid-ladder (ours, 80 games) | Stellar 51, Varg 49, Ryth 45, Cassi&Issac 45, Tavi 39, then Vesper 24, Vendetta 23, Ren 20, Marcella 19, Prism 17, HoR 16, Willow 8 |
| Top-20 census (INSIGHTS §2.1) | HoR, Marcella, Vendetta and Vesper drafted by 20/20 teams, Ryth by 17/20, Tavi 9/20 |
| | Rare in the top 20: Stellar (3 teams), Ren (4), Prism (5), Willow (6), Cassi&Issac (7), Varg (10) |

Our record with and without each opponent pick:

| Opp drafted | v1 with | v1 without | v2 with |
|---|---|---|---|
| Varg | **7W-34L (17%)** | 11W-13L (46%) | 6W-2L |
| Ren | **2W-14L (12%)** | 16W-33L | 3W-1L |
| HoR | **0W-10L** | 18W-37L | 6W-0L |
| Willow | **0W-8L** | 18W-39L | – |
| Tavi | 8W-28L (22%) | 10W-19L (34%) | 3W-0L |
| Cassi&Issac | 11W-25L (31%) | 7W-22L (24%) | 7W-2L |
| Stellar | 14W-27L (34%) | 4W-20L (17%) | 8W-2L |
| Prism | 9W-6L (60%) | 9W-41L | 2W-0L |
| Vesper | 9W-10L (47%) | 9W-37L | 5W-0L |

- **v1's worst pairs** were Ren+Varg 0W-11L, Cassi&Issac+Varg 2W-18L and Tavi+Varg 4W-25L. Its best were Stellar+Vesper 6W-2L, Prism+Ryth 8W-4L and Prism+Stellar 7W-4L.
- **Opponent first pick (v1):** Varg 4W-18L, HoR/Vesper/Marcella 0W-10L combined, Stellar 5W-3L.
- **Caveat: this is heavily confounded by team identity.** Each team drafts almost the same five every game.
  - The 0-5 sets came from Varg/Cassi&Issac/Tavi teams (Hammer Method, LigaSiur, Patient Wolves), a HoR/Ren/Stellar/Ryth/Varg team (mostly harmless) and a Willow/HoR/meta team (FürFortnite).
  - "Varg is bad for us" really means "the stronger teams near 1450 tended to play a melee Varg frontline".
- **v2 contradicts a pure-composition story.**
  - It beat **ShadowKnight 5-0**, 922–128 on average, with Varg+Stellar+Cassi&Issac+Marcella.
  - It lost 2 of 5 to **test**, which played Varg/Cassi&Issac/Stellar plus Ren.
  - It beat **RE:SLIGHT_SMILE 5-0**, which played *exactly* the top-20 meta (HoR, Ryth, Marcella, Vesper, Vendetta). We look strong in the meta mirror.
  - What separates test from ShadowKnight is bot quality plus Ren (stun + retaliation), and possibly more stuns per fight: Cassi 1-round stun at range 4, Ren 1.1×F + stun, Stellar 2×F burst at range 4. Stuns cancel tributes and recalls. **This is a hypothesis to check in the replays.**

### 2.4 Maps and side
- **v1 by map prefix:** 00* 10W-26L, **01\* 1W-12L**, 02* 7W-6L, adgato* 0W-3L.
- **v2 losses:** 02arena and adgato_gemcombat4. No map was played twice by v2.
- **Side, v1 only:** side a 3W-22L (12%), side b 15W-25L (38%). This is almost certainly the opponent effect: four of the five 0-5 sets were on side a, and the side is fixed per set. v2 was side b in every game, so its side is untested.
- **0–0 maps:** v1 won 02the_pack ×3 and 00contest on tiebreak_gold, and lost 01yellow_brick_road. v2 won 01yellow_brick_road on tiebreak_second_team, which is a coin-flip-like win from being Team B.

## 3. How predictive was local self-play?

| Question | Local said | Ladder said | Verdict |
|---|---|---|---|
| Absolute strength of v1 | 40-0 vs starter, 64% in the builder round-robin (best of 4) | 28% games, 3-10 sets, ~1280 performance | **Not predictive.** Beating the starter and our own family says nothing about rank |
| v2 vs v1 improvement | tb_merge_b 89% vs sf_bank (140 games) and sf_bank 82% vs sf_base: chained ≈ +600 Elo (an overestimate, since chaining isn't transitive) | +465 Elo game-level (CI ~+130 to +790) | **Predictive in direction and roughly in size.** Relative self-play gains transferred |
| Which maps v2 loses | Locally tb_merge_b won both sides of 02arena (1006–11, 1005–34) and adgato-gemcombat4 (1024–182, 1013–125). Its local loss maps were 00dunes, 00gem-fields, 00rows, 00the-line, 01boss-battle, ... | Lost exactly those two maps; won 00rows and 01yellow_brick_road | **Not predictive.** The per-map local results told us nothing about ladder per-map risk |
| Which maps v1 loses | sf_base vs sf_bank per map (sprint set) | v1 went 4W-5L on tb_merge_b's local-loss maps vs 14W-42L elsewhere | **No signal** (tiny n) |
| Draft | Local bots draft Varg/Ryth/Vendetta (sf_*), and the census says draft HoR/Vesper/Vendetta/Marcella | The meta core is clearly better on the ladder (4-pick 1-11 → 6-0) | **The census, not self-play, was the predictive source** |

- **Takeaway:** self-play is a decent *relative* A/B instrument within one bot family. It is blind to opponent styles we don't have.
- Our local pool contains no Stellar, Cassi&Issac, Ren, Tavi or Prism drafts, yet those are 4 of the 5 most-picked champions on our ladder band. A 92% local win rate doesn't translate into a ladder win rate.

## 4. Conclusions
1. **v2 is a real, large improvement** (+35 rating in 3 sets, 13-2 games). The meta draft plus fight/flee carried it. Don't regress that core.
2. **The remaining weakness is specific: caster/stun-heavy teams with a melee frontline** (Varg + Cassi&Issac + Stellar + Ren, i.e. team "test"). We lost one game to an r577 blowout. Composition alone doesn't explain it, since we swept ShadowKnight with a similar draft.
3. **4-pick drafting was v1's worst failure** (1-11). v2's 4-pick core (Vesper, Vendetta, Marcella, HoR) fixed it (6-0). 3-pick (Vesper, Vendetta, Marcella) is untested (0-1, n=1).
4. **The mid-ladder (1400-1500) is a different meta from the top 20.** Expect Stellar, Varg, Ryth, Cassi&Issac and Tavi. Our local opponents should look like that, not only like ourselves.
5. **Sweeps matter for rating** (5-0 = +16 vs 3-2 = +3). Reducing the rare blowout losses is worth more than pushing wins from 85% to 90% of margin.

## 5. Recommended next experiments (in order)
1. **Watch the two "test" losses** (02arena e73b0c3e…, adgato_gemcombat4 on the site) after `cambc login`, then run `cambc matches summary <id> --json`.
   - Check who killed whom and when, whether our tributes or recalls were stunned, and how many carried gems we lost.
   - This tells us whether we were out-fought (deaths/gemLoss) or out-farmed. It costs no CPU.
2. **Build an imitation opponent of the mid-ladder style** and add it to the eval pool: a copy of `tb_merge_b` that drafts Varg, Cassi&Issac, Stellar, Ren, Ryth/Tavi.
   - The untracked `bots/lad_*` and `bots/imit_test` dirs look like another agent's work in progress (their NOTES.md files are still tb_merge_b's).
   - Gate future candidates on *both* `vs tb_merge_b` and `vs imitation`.
3. **3-pick draft check:** run Vesper, Vendetta, Marcella vs alternatives such as Vesper, Marcella, Ryth (a stun anchor) on the 3-pick maps only, with `--maps` set to the 3-pick maps, 40+ games.
4. **Anti-stun tribute/recall rule:** don't start a tribute or recall while an enemy caster (Cassi, Stellar, Ren, Ryth) is visible within about 5. Only evaluate it against the imitation opponent; self-play can't measure it.
5. **Keep tracking the ladder:** re-pull `match_groups.json` after each set and rerun this analysis. With 3 v2 sets, every conclusion about v2 except "much better than v1" is within noise.
