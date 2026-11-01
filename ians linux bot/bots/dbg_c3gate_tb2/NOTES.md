# c3_teamclear: q24_combo + the Q26 team bootstrap (h_teamclear v2)

**Lineage.** `bots/c3_teamclear` is a fresh fork of the champion `q24_combo`, with every hunk of h_teamclear v2 ported onto it.
- **Source of the port:** `diff -u bots/tb_merge_b/src/bot.py bots/h_teamclear/src/bot.py` (470 lines). h_teamclear changed only `bot.py`; its main.py, draft.py and randomness.py are byte-identical to tb_merge_b's.
- **Why all parts:** the h_teamclear report (`results/experiments/2026-11-01-h_teamclear.md`) ran two ablations.
  - With the wrap fix alone, h_tc_wraponly scored 82/140.
  - With team clear but no wrap fix, h_tc_nowrap scored 64/140.
  - So every part ships, with h_teamclear's exact flag values.
- **Restart from a clean fork.** The folder already held an interrupted, partial port: q24 + about 290 diff lines, NOTES.md still q24's, no record of its state. `src/bot.py` was reset to q24_combo's (the same as `tools/newbot.py q24_combo c3_teamclear`, which refuses an existing folder) and the port was redone from scratch. The old partial file is kept outside the repo, in the session scratchpad.

| File | Change |
|---|---|
| `src/bot.py` | q24_combo plus h_teamclear v2 and the integration below: 3,032 lines (q24: 2,697). Every change is tagged `h_teamclear` or `c3_teamclear`. |
| `src/main.py`, `src/draft.py`, `src/randomness.py` | Byte-identical to q24_combo. |

## Patch 5 (h_teamclear v2): switches and values
All values are identical to h_teamclear's; an AST check compared every constant h_teamclear added.

| Switch | Value | What it does |
|---|---|---|
| `TEAM_CLEAR` | True | **(1) Team option.** In `choose_target`, where the solo checks fail (no direct pass, no hit-and-run within 4 cycles, or no escape tile), it looks for the smallest team k in [c+2, 1+c+idle alive allies] for which the direct check passes with k-1 allies hitting. The option is scored value/(k·(d+ttk_k+6+10)). |
| `TEAM_MAX_STR`, `TEAM_MAX_HP` | 250, 15000 | **Boss exclusion** (`Group.boss`): no team option for a group with strength > 250, total HP ≥ 15,000, or a monolith. |
| `TEAM_TANK_CHECK` | True | The team option also needs s·ttk_k·share/k ≤ maxhp − s·(rng+1) − 80. |
| `TEAM_MUSTER` | True | **(2) Muster.** Before waking a full-HP sleeping group that `muster_need` says needs a team, wait on the ring `dilate(tiles, rng+3) & ~dilate(tiles, rng)` until `team_need` champions are near. |
| `TEAM_MUSTER_COST` | 10.0 | Rounds added to a team option's cost. |
| `TEAM_COMMIT_WAIT`, `TEAM_MUSTER_WAIT`, `TEAM_BAN` | 15, 30, 150 | Ban the group for 150 rounds after 15 rounds at the ring with too few claimers, or 30 rounds without enough champions near. |
| `TEAM_WRAP_FIX` | True | **(a)** Once the target group is awake, its unseen but believed-alive camps count as threats in range. **(b)** The "no live camp visible within 3 of the centre → respawning" guess fires only when every believed-alive camp tile is in view. **(c)** The target group's own dead camp tiles may be stood on while it is alive. |
| `DEAD_MARK` | 255 | Claim byte of a dead champion, so allies do not count it as idle. |
| `PRESENT_BYTE` | 6 | Presence bits (see the byte map below). |
| `TEAM_NEAR_DANGER` | False (as in h_teamclear) | (3) The nearest-champion camp model in the flee check. It screened worse, so it is off. |
| `TEAM_DEBUG` | False | The `TC`/`TCD`/`MUSTER-BAN` prints. |

**Every debug switch is off:** `DEBUG`, `DIAG`, `VALIDATE`, `PROF`, `GOLD_LOG`, `TEAM_DEBUG` and `Bot.debug_tb`. q24's switches and constants are unchanged (an AST check found 0 differences).

## Shared memory: 8 bytes, no collisions
| Byte | Owner | Contents | Writers / readers |
|---|---|---|---|
| 0-5 | tb_splitfarm claims, extended by h_teamclear | One byte per champion slot: 0 = idle (no target), group idx+1 = claim, **255 = dead** (h_teamclear `DEAD_MARK`) | **Writers:** `write_claim` (idx ≥ 254 maps to 0, so a claim is never 255) and `write_dead`. **Reader:** `read_claims`, which loops over `range(PRESENT_BYTE)` = 0-5 and skips its own slot and 255. Slots 0-5 with byte 0 and `s < n_bodies` count as idle allies. |
| 6 | h_teamclear presence bits | Bit s is set when slot s stands inside its claimed, alive group's zone (`dilate(tiles, rng+4)`) | **Writer:** `set_present`, a read-modify-write of its own bit. It is cleared by `write_claim(None)` and `write_dead`. **Reader:** `muster` (claimers of the same group with the bit set count as near). |
| 7 | sf_pvp focus (`FOCUS_BYTE`) | ((enemy index+1) << 5) \| (round & 31) | `write_focus` / `read_focus`. Unchanged. |

- **No q24 patch uses shared memory.** h_3pick's trio bytes were never ported; h_goldtie, h_earlyfight and h_fightfuel write nothing. A grep finds only the four accessors above.
- **Byte 6 was always 0 in q24.** tb_merge_b's `read_claims` read it as a claim byte, and it was never non-zero there. c3 no longer reads it as a claim.
- **Slots never reach bytes 6-7.** A team has at most 6 bodies: 5 picks plus the extra body of the Cassi & Issac pick (rules §13). So `slot` ≤ 5, and `min(slot, 7)` never lands on 6 or 7.

## Conflicts and resolutions
**T1. `threats` was split by h_fightfuel. A textual merge drops WRAP (a) from the live path.**
- *The clash.* h_teamclear's WRAP (a) hunk sits inside tb_merge_b's `threats()`. In q24 that body became `threats_slow()`, and the live path is `threats_fast()` (`THREATS_FAST = True`).
- *What a merge does.* `git merge-file` applies the hunk cleanly, to `threats_slow` only. That silently disables WRAP (a), the part that stopped Vendetta dying to an unseen elk.
- *Resolution.* The hunk is now the method `wrap_hidden(pos, awake, inc)`, with h_teamclear's code verbatim. Both `threats_slow` and `threats_fast` call it after their camp loop and before the enemy loop and the jungle multiplier, which is h_teamclear's placement.
- *The fast-path consumers handle the appended tuples:*
  - `retreat_fast` and `handle_enemies` read only the tuple fields (cp, r, s).
  - The danger check's `c.health()` raises for a hidden camp and falls back to `self.hidden_hp`, as in h_teamclear.

**T2. `choose_target` hit-and-run block: q24's chip mode vs the team option (the two bootstraps).**
- *The two changes.*
  - q24 (h_goldtie) changed the cycles limit to `GOLD_CHIP_CYCLES (30) if self.chip else 4`. Chip mode is gold play only, after 12 idle healthy turns.
  - h_teamclear replaced the same `continue` lines with "hit-and-run within 4 cycles, else team option, else skip".
- *What would fight.* `muster_need` recomputes "can I solo it?" with the fixed 4-cycle limit. A group chosen through chip mode would therefore usually get `team_need ≥ 2` (whenever some team of up to `n_bodies` passes). The chip champion would then wait at the ring, and after `TEAM_COMMIT_WAIT` rounds with nobody else committed it would **ban** the group for 150 rounds. That would break q24's chip path.
- *Resolution.*
  1. The hit-and-run test within 4 cycles comes first, as in both sources.
  2. Otherwise both alternatives are computed:
     - the team option, when `TEAM_CLEAR` is on and the group is not a boss;
     - the chip option: `self.chip`, cycles ≤ 30 and `escape_ok`, with q24's cost `cycles*30`.
  3. If both exist, the cheaper per-champion cost wins: k·(d+ttk_k+6+10+wait) against d+ttk+6+cycles·30+wait.
  4. A chip pick sets `best_chip`, and **a chip pick never musters** (`team_need = 0`).
- *Equivalences.* With chip mode off, this is exactly h_teamclear. Where no team option exists (boss groups, too few free allies), it is exactly q24. The rewrite is equivalent to q24's `budget <= 0 → continue` (cycles = BIG) and to its `cycles > limit or not escape_ok → continue`.
- *No double counting of claims.*
  - Both alternatives see the same claim count c: chip as `tdps = dps + 55c`, as in q24; the team option as k ≥ c+2 bodies, as in h_teamclear.
  - Only one alternative is taken per group, and there is still one claim byte per champion. Neither path writes extra claims.
  - The presence bit is set by any claimer standing near an alive group, whichever path chose it. That is correct, because the champion really is near.
- *Measured.* In the instrumented copy (below), chip mode turned on only at r1994-1998 on 01boss-battle, for 3 of 5 champions. There were 0 chip picks in any traced game. With team options available, champions are rarely idle for 12 turns.
- *Known edge case (not handled, rare).* A chip-mode champion may wake a group that teammates are still mustering for (claims c ≥ 1 and the team needs more). The musterers then see it awake and join (`muster` returns False for an awake group). Nothing deadlocks.

**T3. The respawn step-off rule: h_goldtie's `blocks_respawn` and WRAP (c).**
- *The two changes.* q24 made "step off a camp tile" conditional on `blocks_respawn(pos)`; in gold play that means only respawning groups' tiles. h_teamclear exempts the target group's own tiles while it is alive.
- *Resolution.* The merged condition is the AND of both: `status != 1 and on a camp tile and not WRAP-exempt and blocks_respawn(pos)`.
- *No overlap.* In gold play, a WRAP-exempt tile belongs to a status-0 group, so `blocks_respawn` is already False there.

**T4. Name clash in `muster`.** h_teamclear's local `pm = buf[PRESENT_BYTE]` shadows q24's module function `pm()`, h_fightfuel's profiler checkpoint. It was harmless, because `muster` never calls `pm()`, but it is renamed `pbits`. A no-op `pm("muster")` checkpoint was added after a muster turn (`PROF` is off).

**T5. The current-turn data audit.** The team check reads the following:

| Reader | Reads | Freshness |
|---|---|---|
| `choose_target` / `team_k` / `muster_need` | claims, `idle_allies`, `last_claims`, `claim_buf`; G.hp / G.status; own hp / dps / maxhp | `read_claims()` runs at the top of every `choose_target`. G.* comes from this turn's `observe` (fast and slow agree; VALIDATE in h_fightfuel). Own stats are live API reads. |
| `muster` | `awake`, allies, `claim_buf`, `last_claims`, `team_need` | `awake` comes from this turn's `threats`, and allies from live `vision.champions`. Claims and `team_need` come from this turn's `choose_target`, which always runs before `muster`: either in the tribute block (whose `tgt` is reused) or in the farming block. |
| `set_present` | G.status, `pos` | This turn. |
| `wrap_hidden` (WRAP a) | `self.target`, G.status / G.hp, `awake` | `self.target` is the group chosen **last** turn. This is h_teamclear's design: threats run before `choose_target`. Its state and `awake` are this turn's. |
| danger check | `self.hidden_hp` | Reset and refilled by this turn's `threats`. |
| `TEAM_NEAR_DANGER` (off) | `last_claims` | Last turn's claims, as in h_teamclear. It is off. |

- **h_fightfuel's caches are never read by team code.**
  - `esrc` (enemies, per turn) is read only by `retreat_fast`. It is cleared at the start of `play_turn` and refilled by `threats`.
  - `camp_rng` and `spawn_cd` are static.
  - `kit_units_fast` and the `retreat_fast` memo are per call.
- **q24's group-balance rule** (`group_balance`, `hit_while_leaving`, rally retreats) reads live API data. It never sees the presence bits or claims.

**T6. Other overlaps, all without conflict.**
- **`__init__` / `init_static`:** both sides' state is kept, plus `n_bodies = len(handles)`.
- **The dead branch:** `write_dead()` (with `TEAM_CLEAR`) replaces `write_claim(None)`. The dead mark is cleared on the first live turn.
- **Guard vs boss groups.** h_goldtie's `guard` (strength ≥ 200 or HP ≥ 15,000) sets value 0 under `no_tribute`, so those groups are never targeted there. h_teamclear's `boss` (strength > 250, HP ≥ 15,000 or a monolith) only excludes team options. Under `no_tribute`, team options exist only for non-guard groups, valued by **gold**. That is the report's follow-up hypothesis "gold-valued team targets on no-tribute maps", and the merge implements it for free.
- **The stuck guard (`note_progress`)** does not run on muster turns, as in h_teamclear.

**How the port was checked.**
- **Mechanical reference.** `git merge-file -p --diff3 q24 tb_merge_b h_teamclear` gives 4 conflicts: `__init__`, the `choose_target` block, the presence-bit vs chip-mode lines, and the step-off condition. The port differs from that reference only in:
  - those 4 regions, resolved as above;
  - T1 (`wrap_hidden` in both threats paths; the reference had it in `threats_slow` only);
  - T4;
  - comments.
- **AST.** Each of the following is identical to h_teamclear's (docstrings aside): `Group.__init__`, `read_claims`, `write_dead`, `set_present`, `group_zone`, `write_claim`, `team_k`, `muster_need` and `nearest_incoming`. `muster` differs only by the `pbits` rename.
- **Static checks.** `py_compile` passes. Every `self.` attribute that is read is also assigned, and there are no duplicate definitions or constants.

## Validation
**Local games** (this compute node: `holy7c02312`, an OOD job, not a login node; `cambc run`, default log limit):

| Game | Result | Our clears / first clear / first tribute | Camp deaths, deaths | fuelExh | stdout |
|---|---|---|---|---|---|
| `c3_teamclear q24_combo --map 02gift-wrapping` (`matches/c3-local-final`, final code) | **W 1000-0, r817** | **19** / r29 / r81; 45 tributes, 127,815 monster damage | 0, 0 | 5 | team-a and team-b stdout 0 bytes (no traceback, no `bot error`); 0 crashes |
| `q24_combo c3_teamclear --map 02gift-wrapping` (`matches/c3-local-final-b`, c3 as B) | **W 1004-8, r1167** | **19** / r27 / r75; 39 tributes | 0, 1 | 14 | 0 bytes |
| q24 in those games | 0 and 2 clears | Its chip mode never starts: c3 tributes first, so q24 is never `stalled`. | | | |

- **Reference:** h_teamclear on this map vs tb_merge_b won 1002-0 at r900 (20 clears, first r32) and 1032-0 (22 clears, first r27).
- **An identical earlier run.** The first local run (`matches/c3-local`) used the pre-T2 "team first, chip fallback" ordering, before a comment edit. It produced the identical game.

**No-tribute checks** (c3 as A vs tb_merge_b). These are where a team/chip fight would show.

| Map | c3 local (`matches/c3-dbg-boss`, `-guard`) | q24 gate game | h_teamclear |
|---|---|---|---|
| 01boss-battle A | W on gold **30,328** vs 2,646, 116 clears, 0 camp deaths | W 24,108 vs 2,578, 101 clears | L 3,898 vs 4,103, 19 clears |
| 02guardians A | W on gold **18,563** vs 865, 101 clears, K/D 31/0 | W 14,222 vs 443, 94 clears | W 1,726 vs 1,698, 14 clears |

These two local games were run before a comment-only edit. The smoke job below (final file) gave 26,953 vs 2,499 on 01boss-battle A. That is the known fuel-divergence noise: changing only comments re-rolled this game.

**Instrumented copy** `bots/dbg_c3tc` (diagnostic only, never evaluate it). It is c3 plus counters printed every 250 rounds. Sums over the 5 champions:

| Game (dbg_c3tc as A) | Result | Team picks | Muster turns | Bans | Chip picks / chip mode on | WRAP a / b / c events |
|---|---|---|---|---|---|---|
| 02gift-wrapping vs q24 (by r1000) | W 1039-324, r1222 (diverged from c3's game) | 184 | 216 | 0 | 0 / never | 973 / 29 / 502 |
| 01boss-battle vs tb_merge_b | W gold 28,353 vs 1,860 | 15 | 154 | 0 | 0 / r1994-1998 (3 champions) | 35 / 0 / 466 |
| 02crossing vs tb_merge_b | **L 827-1000, identical to the smoke game** | 65 | **284 (270 by slot 0, Vesper Vale)** | 2 | 0 / never | 19 / 44 / 130 |
| 00great-wall vs tb_merge_b | **L 841-1102, identical to the smoke game** | 63 | **259 (slot 0: 172, slot 3: 82)** | 2 | 0 / never | 8 / 89 / 57 |

**Smoke job** (one onslurm job on the test partition, job 56818116, exit 0, tag `c3-smoke-tbm`). It covered the 15 maps where h_teamclear changed most, picked from the q26metrics per-map target-group clears and the result flips of h_teamclear vs q24:
02gift-wrapping, 00great-wall, 02treasure-box, 01corridors, 02crossing, 01fracture, 00pilgrimage, 00lost-world, 00expanse, 00corners, 00swirl, 01boss-battle, 02guardians, 00reverse-spiral and 02harvest. Both sides were played, against tb_merge_b, so the games compare directly with `ll1-h_teamclear-all` and `gate-q24-all`.
```
SUMMARY c3_teamclear vs tb_merge_b: 24W-6L (80%)  avg gems 754 vs 466  avg deaths 8.0 vs 14.9  botFaults(A) 0
```
The same 30 games from the existing runs: h_teamclear 21W-9L, q24_combo 21W-9L.

| On these 30 games (q26metrics) | c3_teamclear | h_teamclear | q24_combo |
|---|---|---|---|
| Wins | **24** | 21 | 21 |
| Clears / game | 60.4 | 48.0 | 59.8 |
| Monster damage / game | 162,052 | 104,405 | 137,483 |
| Target-group clears (gems) | **279 (10,634)** | 87 (3,970) | 217 (7,633) |
| Distinct target groups cleared | **44/50** | 31/50 | 30/50 |
| Capture split, mean champions | 1.46 | 2.17 | 1.25 |
| Camp deaths / game | 1.77 | 2.30 | 1.33 |
| Champion deaths / game | 6.23 | 8.23 | 5.57 |
| fuelExhausted / game | 6 | 56 | 2 |

`postmortems/match_metrics.py matches/c3-smoke-tbm` gave: deaths_by_camp 53 (1.8/game), deaths_by_champion 187 (6.2/game), fuelExhausted 184 (6.1/game), gemsLost_to_champion 54.3/game, mean tribute 23.8.

Per game. Format: result, score (or gold on 0-0 maps), clears/target clears, first clear, camp deaths, fuelExh.
| Map | Side | c3_teamclear | h_teamclear | q24_combo |
|---|---|---|---|---|
| 02gift-wrapping | A | W 1000-0, 19/19, r29, 0, 5 | W 1002-0, 20/20, r32, 0, 83 | W 44-0, 1/1, r353 |
| 02gift-wrapping | B | W 1009-38, 20/20, r27, 0, 14 | W 1032-0, 22/22, r27, 2, 119 | W 44-0, 1/1, r356 |
| 01boss-battle | A | W gold 26,953-2,499, 108/59 | L gold 3,898-4,103, 19/8 | W gold 24,108-2,578, 101/50 |
| 01boss-battle | B | W gold 26,527-4,589, 113/60 | W gold 4,036-3,521, 23/8 | W gold 25,916-4,505, 106/57 |
| 02guardians | A | W gold 18,563-865, 101/40 | W gold 1,726-1,698, 14/0 | W gold 14,222-443, 94/36 |
| 02guardians | B | W gold 18,824-1,006, 102/45 | W gold 3,047-1,891, 28/0 | W gold 19,827-872, 89/42 |
| 00corners | A | W 1029-89, 60/6 | L 307-1014, 35/0 | W 1029-395, 68/6 |
| 00corners | B | W 1017-352, 70/1 | W 1006-117, 77/4 | W 1021-231, 61/4 |
| 00expanse | A | W 1005-947, 71/2 | L 968-1017, 68/1 | W 1011-581, 68/2 |
| 00expanse | B | W 1003-702, 67/1 | W 1001-842, 70/3 | L 726-1036, 66/2 |
| 00swirl | A | W 1040-114, 54/7 | W 1028-157, 51/4 | W 934-80, 56/4 |
| 00swirl | B | W 1002-10, 55/0 | L 279-1021, 24/0 | W 908-170, 46/1 |
| 00reverse-spiral | A | W 876-742, 62/2 | L 347-795, 56/0 | L 301-769, 53/0 |
| 00reverse-spiral | B | W 1002-169, 53/6 | W 599-210, 43/2 | W 1013-471, 54/9 |
| 00pilgrimage | A | W 421-303, 80/0 | L 168-394, 101/0 | L 396-418, 87/0 |
| 00pilgrimage | B | W 485-309, 109/1 | W 372-339, 120/1 | L 253-486, 106/0 |
| 01corridors | A | W 731-317, 23/3 | W 530-310, 25/2 | L 455-627, 18/0 |
| 01corridors | B | W 622-364, 28/2 | W 630-425, 29/1 | W 433-356, 17/0 |
| 02harvest | A | W 939-909, 47/0 | L 228-819, 24/0 | L 706-860, 50/0 |
| 02harvest | B | W 1004-737, 53/1 | W 1008-659, 55/0 | L 691-981, 62/0 |
| 02treasure-box | A | W 1028-127, 37/0 | W 1030-130, 41/2 | W 1023-241, 90/0 |
| 02treasure-box | B | W 1017-252, 35/1 | W 1011-499, 56/1 | W 1009-527, 60/1 |
| 01fracture | A | W 972-957, 68/1 | W 878-867, 66/1 | W 751-742, 61/0 |
| 01fracture | B | **L 830-893**, 62/0 | W 1018-744, 66/0 | L 810-818, 74/0 |
| 00lost-world | A | W 1020-508, 69/0 | W 1009-962, 59/1 | W 1003-963, 62/0 |
| 00lost-world | B | **L 621-1038**, 45/0, K/D 11/31 | L 558-1005 | L 351-1000 |
| 00great-wall | A | **L 841-1102**, 59/0, K/D 11/17 | L 941-942, 57/0 | W 1018-668, 70/0 |
| 00great-wall | B | **L 662-1010**, 52/2, K/D 8/15 | W 1077-809, 54/4 | W 846-696, 65/0 |
| 02crossing | A | **L 827-1000**, 53/0, K/D 11/18 | W 1043-239, 43/1 | W 1022-538, 37/1 |
| 02crossing | B | **L 602-1000**, 36/0, K/D 6/21 | W 1001-311, 52/1 | W 1009-177, 46/0 |

**Reading the smoke** (it checks the merge, not strength):
- **The mechanism carried over.** 02gift-wrapping went from q24's 1 chip clear (44-0) to h_teamclear's ~20 clears and 1000-0. Target-group coverage went from 30/50 to 44/50.
- **The no-tribute maps keep (and slightly exceed) q24's gold-play numbers.** The team path did not displace q24's farming there; h_teamclear alone lost those 10-20k of gold.
- **Fuel stays near q24's level:** 6 vs 2 per game, against h_teamclear's 56.
- **Losses to watch in the gate:**
  - **02crossing A+B and 00great-wall A+B:** q24 won all four, and h_teamclear won 3 of the 4. These are fight losses (K/D 11/18, 6/21, 11/17, 8/15) with 0-2 target clears.
  - The instrumented copy reproduced both A games exactly, and they show a **muster cost**. One champion (Vesper Vale, slot 0) spent 270 turns (02crossing) and 172 turns (00great-wall) mustering for a group that was never cleared, with 2 bans each.
  - The muster clock restarts whenever the champion leaves the zone or is interrupted for more than 10 rounds, as by enemy fights on a contested map. So the 15/30-round bans fire late.
  - This is h_teamclear's logic unchanged. It is a candidate refinement (a cumulative muster budget per group), **not** fixed here: the task is a faithful port.
  - 00lost-world B and 01fracture B were also lost by q24 and/or h_teamclear.
- **Noise caveat.** Byte-level changes re-roll games, as the comment-only edit shows on 01boss-battle. Per-game flips are weak evidence; strength needs the LOOP.md §4 gate.

## Review fixes (adversarial merge review, 1 Nov)
**Result: no merge defect found, so `src/` was not changed.** The review checked the port independently and did not rely on the claims above.

**1. Hunk-for-hunk comparison.**
- *Inputs.* `diff -u tb_merge_b h_teamclear` (470 lines) and `diff -u q24_combo c3_teamclear` (530 lines).
- *Mechanical reference.* `git merge-file -p --diff3 q24 tb_merge_b h_teamclear` was run on scratch copies. It gives the same 4 conflicts listed above.
- *Comparison.* c3 differs from that reference only in the following:
  - the 4 conflict regions, each holding both sides;
  - T1: `wrap_hidden` is called from `threats_fast` too, where the reference had it in `threats_slow` only, and the live path is fast;
  - T4: `pm` renamed to `pbits`;
  - the `pm("muster")` checkpoint;
  - the constants block placed before `def pm`;
  - comments.
- *AST checks.*
  - Unchanged from h_teamclear: `Group.__init__`, the `Group` slots, `read_claims`, `write_dead`, `set_present`, `group_zone`, `write_claim`, `team_k`, `muster_need` and `nearest_incoming`.
  - `muster` differs only by the rename.
  - All 14 constants h_teamclear added have its values.
  - The only q24 constants that changed are those 14 additions.
- *q24 code removed.* Only two pieces:
  - the hit-and-run lines in `choose_target` (`budget <= 0` / `cycles > (30 if chip else 4)` / `escape_ok` → `continue`);
  - the step-off condition, which is now the AND of both sides.
  - Both are justified by T2 and T3.
- *Files.* `main.py`, `draft.py` and `randomness.py` are byte-identical to q24's.

**2. Chip-mode equivalence (T2), proved by case.**
- *What q24 accepted.* q24 accepts a hit-and-run iff `budget > 0`, cycles ≤ (30 if chip else 4) and `escape_ok`, with extra = cycles·30.
- *What c3 accepts.* c3 accepts the solo route iff cycles ≤ 4 and `escape_ok`, or the chip route iff chip, cycles ≤ 30 and `escape_ok`. `budget ≤ 0` gives cycles = BIG, so neither route is open.
  - The union of the two routes is exactly q24's acceptance set, with the same `extra`.
  - So with no team option, c3 behaves as q24, and with chip mode off it behaves as h_teamclear.
- *When both options exist.* The comparison `k·(d+ttk_k+6+10+wait)` vs `d+ttk+6+30·cycles+wait` is the same as comparing the final scores, because the later multipliers (`c`, current target, death memory) are the same for both options.
- *Tie handling.* `best_chip` is set inside the same `if` as `best`, so ties also carry the correct flag.

**3. Shared memory.**
- *Every accessor (grep).*
  - `read_claims`: `read(0, 8)`, using bytes 0-5 and keeping the buffer for byte 6;
  - `write_claim` and `write_dead`: own slot byte;
  - `set_present`: read-modify-write of its own bit in byte 6;
  - `muster`: reads byte 6 from the buffer;
  - `read_focus` / `write_focus`: byte 7.
- *Limits.* At most 6 bodies, so `slot` ≤ 5, and nothing else touches bytes 6-7.
- *Encoding.* A claim byte is never 255, because `idx ≥ 254` maps to 0.

**4. Muster gate vs the group rule (regroup and rally retreat), measured.**
- *Method.* The copy `bots/dbg_c3rev` (c3 plus counters; diagnostic only, never evaluate it) played 00great-wall A vs tb_merge_b. The game reproduced the smoke loss exactly: **L 841-1102, K/D 11/17**.
- *Interruptions.*
  - `handle_enemies` interrupted a pending muster 8 times for slot 0 (4 of them regroups) and 44 times for slot 3 (7 regroups).
  - The danger retreat interrupted it twice.
  - Clock resets because a regroup or retreat took the champion out of the zone: **0**.
- *Where the 170 muster turns of slot 0 went (126 on group 3, 2 bans).*
  - 75 were walk-in turns outside the zone, each of which resets the clock;
  - 10 were resets after a gap of more than 10 rounds;
  - so only about 80 were spent waiting in the zone.
- *Verdict on the "muster cost" above.* It is mostly travel and gaps, not a fight between the regroup step and the muster ring. `handle_enemies` simply runs first. The two never move the champion in opposite directions on the same turn.
- *The re-rolled 02crossing game agrees* (dbg_c3rev: W 1053-823): 1 interruption by `handle_enemies`, and 1 clock reset on leaving the zone.

**5. A position 2-cycle with a constant target (base code, not caused by the merge).**
- *What happened.* A slot-0 trace (`bots/dbg_c3rev_t`) of the same 00great-wall game shows Vesper Vale stepping (34,19)↔(35,19) every round from r254 to r292, 39 rounds, with target group 3 at (9,8) the whole time.
  - The oscillation is the same whether the turn is a muster turn (walking to the ring) or a released farm turn.
  - It happens outside the zone, and no turn in that span returned from `handle_enemies`.
  - So it is movement, not muster vs farm and not regroup.
- *Second case.* A re-rolled game shows slot 3 doing the same at (14,19)↔(15,19) for 25 rounds, toward group 7.
- *Probable cause (an untested hypothesis).* `step_toward` treats only **visible** camp tiles as blocked. One tile further, a camp leaves vision, the route through it reopens, and the champion steps back.
- *Who covers it.* h_bigmap's CYCLE_GUARD (Q30) would catch it, since it fires when pos[t]=pos[t-2]≠pos[t-1] for 6 turns. Team clear makes such far targets more common, but the bug is in tb_merge_b's movement code.

**6. Staleness of cached data.**
- *Camp data read by the team code.* Every read is from this turn or static:
  - `G.hp` / `G.status` from this turn's `observe`;
  - `awake` from this turn's `threats`;
  - `G.ring` / `G.zone` / `escape_cache` / `camp_rng`, which are static (the walk mask never changes);
  - `hidden_hp`, reset in each `wrap_hidden`.
- *Ally data.* `idle_allies`, `last_claims` and `claim_buf` are refreshed by `read_claims` at the top of every `choose_target`, which always runs before `muster`.
- **Minor defect, inherited from h_teamclear, not fixed: presence bits refresh only on farming turns.**
  - Any earlier return keeps last turn's claim and bit: a `handle_enemies` fight, retreat or regroup, the danger retreat, the low-HP walk home, a recall started inside `handle_enemies`, or a channel.
  - A champion that has left its group can therefore still count as "near" for a musterer.
  - *Measured* (bit set, outside the zone, not refreshed since an earlier turn): 36 champion-turns in the 00great-wall game by r1750, and 89 in the 02crossing game by r1250.
  - *Effect on releases.* 2 of the 36 muster releases in those two games counted a bit inside such a stale run. Both were in 02crossing: r60 and r68, on group 0.
  - *Why it is not fixed.* The fix is to clear one's own bit at the start of each live turn when out of the zone. That is a behaviour change, with no in-scope eval to judge it. q24's group rule adds more non-farming turns, so it is a candidate refinement for after the gate.

**7. Flags.**
- `TEAM_*`, `DEAD_MARK` and `PRESENT_BYTE` have h_teamclear's values.
- `DEBUG`, `DIAG`, `VALIDATE`, `PROF`, `GOLD_LOG`, `TEAM_DEBUG` and `Bot.debug_tb` are all False.

**8. Checks on the unchanged `src/`.**
- `py_compile` passes on all 4 files. It was compiled to scratch, so no `__pycache__` is left in `src/`.
- `./cli/cambc run c3_teamclear q24_combo --map 02gift-wrapping -o matches/c3rev-final-gift`:
  - W 1000-0 at r817, identical to `matches/c3-local-final`;
  - 0 crashes, and both stdout files are 0 bytes.

## Next step
- **The gate.** Run the LOOP.md §4 gate **vs q24_combo**: `--maps all` ≥ 82/140, the paired gauntlet ≥ q24's 174/200, a `--release` run, and an analysis.
- **For c4 (q24 + respawn fix + team clear).** h_respawnfix's RESPAWN_FIX (d)/(a) covers the same mechanisms as WRAP (b)/(c). Merge one set and ablate. Keep WRAP (a): the hidden-camp threat is not part of Q21.

---

# Lineage: q24_combo's notes (unchanged from bots/q24_combo/NOTES.md)

# q24_combo: STRATEGIES Q24 combined candidate

**Lineage.** `tools/newbot.py tb_merge_b q24_combo`, then four batch-1 patches ported in this order:
1. h_3pick (lock-memory fix only)
2. h_goldtie v2
3. h_earlyfight_all (v3)
4. h_fightfuel

Each patch scored 52-58% alone vs tb_merge_b on 40 sprint games. Each one keeps its original switch names and values, and no diagnostic output is on.

| File | Change |
|---|---|
| `src/bot.py` | All four patches plus the integration below (2,697 lines; tb_merge_b has 1,935) |
| `src/main.py` | Identical to h_fightfuel's: profiler hooks are no-ops with `PROF = False`, and the traceback runs only with `Bot.debug_tb` (False) |
| `src/draft.py`, `src/randomness.py` | Identical to tb_merge_b. No source changed them |

**How the merge was checked.**
- **Function by function.** Every function in `bot.py` is byte-identical to the one source that changed it, except the functions two or more patches touch: `Bot.__init__`, `init_static`, `pick_altar`, `retreat`, `retreat_fast`, `handle_enemies` and `play_turn`. Each of those was diffed against tb_merge_b and contains every hunk of every patch.
  - `init_gold` and `do_tribute`/`break_lock` differ only by the switches listed below.
- **Constants.** Every module constant a patch adds or changes has the source's value. h_3pick's 17 trio constants are deliberately not ported.
- **Static checks.** `py_compile` passes on all four files. There are no undefined globals (symtable), and no `self.` attribute is read without being assigned.

## Patches and switches
| # | Source | Switches (value) | What it does |
|---|---|---|---|
| 1 | h_3pick ("L") | `LOCK_MEMORY_FIX = True` | `pick_altar` refreshes `locked_altars()` and skips altars remembered as enemy-locked, not only locks in vision. This fixes the 2-cycle that froze carriers (01broken-curve, 02the-pond). Trio mode (`TRIO_MODE`, alerts, assist, commitment) is **not** ported: it was rejected and inert with `TRIO_MODE = False`. |
| 2 | h_goldtie v2 | `GOLD_GUARD_STR = 200`, `GOLD_GUARD_HP = 15000`, `GOLD_STALL_ROUND = 300`, `GOLD_IDLE_TURNS = 12`, `GOLD_CHIP_CYCLES = 30`, `TREASURE_ITEMS` | `init_gold` detects `no_tribute` statically (guard groups) and sets `altar_ok`. Under `no_tribute`: gold value, guard value 0, no banking, Treasure first, and gems are ignored in the fight and recall models. `stalled` (r300+, 0-0) turns on gold play: the respawn-rule fix and chip mode. |
| 2a | (new, diagnostic) | `GOLD_LOG = False` | h_goldtie printed `GOLDTIE no_tribute ...` on slot 0 at init in every game. That print is now behind this switch and off. |
| 3 | h_earlyfight_all (v3) | `EARLY_ROUNDS = 2000` (the rule runs all game), `GROUP_R = 7`, `GROUP_ADV = 1.4`, `GROUP_DISADV = 0.75`, `GROUP_ENGAGE_BONUS = 0.4`, `GROUP_REGROUP_D = 4`, `GROUP_ADV_R = 4`, `GROUP_BONUS_D = 2`; `DIAG = False`, `DIAG_UNTIL = 320` | `group_balance()` scores the local fight as (sum hp × sum dps) ours / theirs. **Advantage:** commit (engage bonus, stand and trade). **Disadvantage:** no new fights; regroup with `retreat(..., rally)` toward visible allies; `hit_while_leaving`. |
| 4 | h_fightfuel | `OBSERVE_FAST`, `THREATS_FAST`, `RETREAT_FAST`, `KIT_FAST` = True; `FUEL_RETREAT_DASH = 350000`, `FUEL_KIT_AIM = 400000`; `VALIDATE = False`, `PROF = False`, `PROF_MIN = 1500000`; `Bot.debug_tb = False` | Bitboard `observe`, awake-only `threats` with a per-turn enemy cache (`self.esrc`), `retreat_fast` (cached sources, memoised scoring, no dash search under 350k fuel), `kit_units_fast` and `reset_target_fast`. `pm()` profiler checkpoints are no-ops. |
| I | (new, integration of 1+2) | `TRIBUTE_USABLE_ONLY = True` | See conflict C1. |

`DEBUG = False` (unchanged).

## Overlaps and how they were resolved
**C1. `pick_altar` / `do_tribute` (patches 1 and 2).**
- *Changes to `pick_altar`.* Both patches add a `continue` to its loop: h_3pick skips remembered-locked altars, and h_goldtie skips `i not in altar_ok`. Both are kept, so an altar is a candidate only if it is usable, not remembered-locked and not locked in vision. The order doesn't change the result.
- *The gap.* When every usable altar is locked, `pick_altar` returns `(BIG, None)` and `do_tribute(me, None)` falls back to `self.altar_ring`. Its `free` ring and `break_lock`'s "free altar within 8" test scan **all** altars, so on a map with some guard-only altars the fallback could send a carrier into a guard ring. That is the 02the-pack stall that h_goldtie removed from `pick_altar`.
- *Fix.* `init_gold` sets `tribute_altars` / `tribute_ring` to the usable altars only when **some but not all** altars are guard-only. Otherwise they are `self.altars` / `self.altar_ring`, so the code is byte-for-byte equivalent to the sources.
  - On all 70 local maps it is a no-op: h_goldtie's static check marks every altar usable on 67 maps and none on 3, and with `no_tribute` `do_tribute` is never called.
  - The submit-if-adjacent loop at the top of `do_tribute` still checks every altar, since standing next to one means it is reachable.
- *Other altar uses* (`try_lock`, wards, alerts, static fields) are unchanged.

**C2. `retreat` signature (patches 3 and 4).**
- *The clash.* h_earlyfight added `rally=None`: the last tie-break is the distance to the nearest visible ally instead of our spawn. h_fightfuel added `dry=False` (its VALIDATE harness) and routes every call to `retreat_fast`, which scores the spawn distance from a static per-tile memo (`self.spawn_cd`).
- *A textual merge would be wrong.* It would have silently dropped the rally in the fast path, because `retreat_fast` always used spawn distances.
- *Resolution.* The signatures are now `retreat(me, awake, enemies, rally=None, dry=False)` and `retreat_fast(me, awake, enemies, rally=None, dry=False)`.
  - With `rally`, `retreat_fast`'s 4th key is `min(cheb(p, t) for p in rally)`. This is exactly the slow `retreat`'s `spawn_pts = rally if rally else self.spawn_pts`.
  - The rally distance is memoised only per call (`memo`), **never** written into the static `spawn_cd`, because the rally points change every turn.
  - The VALIDATE harness passes `rally` to both versions, by keyword.
  - The play_turn danger-retreat passes no rally, so it uses the spawn memo as in h_fightfuel.

**C3. Caches vs later readers (patch 4 vs 2 and 3).** h_fightfuel's only per-turn cache is `self.esrc`: enemy position, range and strength, filled by `threats_fast`. Its readers:
- **`retreat_fast` (the only reader).** Every call site, play_turn's danger retreat and `handle_enemies`, runs after `threats()` in the same turn.
- **Static caches.** `camp_rng` (camp range per spawn tile) and `spawn_cd` are built in `init_static` and are valid all game. `retreat_fast`'s `memo` and `kit_units_fast` are per call.
- **Defensive invariant.** `play_turn` now clears `self.esrc = None` at the start of every turn, so no future path can read last turn's positions. With `esrc` None, `retreat_fast` reads live data, so this changes nothing today.
- **h_earlyfight's `group_balance()` and `hit_while_leaving()`** read live API data (ally and enemy position, health, strength, focus, channel state), not the cache, so they always see the current turn. The `near` list they get is built from live reads in `handle_enemies`. h_fightfuel did not change that part.
- **h_goldtie's code** reads only `G.status` from `observe()` (`blocks_respawn`). `observe_fast` sets the same statuses: VALIDATE in h_fightfuel showed 0 mismatches. It also reads live gem and gold counts.

**C4. `handle_enemies` (patches 2, 3 and 4).** These merged without conflict:
- h_goldtie: `gems = 0` under `no_tribute`, so `rich` is False;
- h_earlyfight's adv/dis logic then overrides `clearly_losing`;
- h_goldtie's `focus_bias` zeroes enemy gems, so the target key's gem term is 0 under `no_tribute`;
- h_fightfuel only adds `pm()` checkpoints, including around the regroup `retreat` call.

**C5. `play_turn` (patches 2, 3 and 4).** The order is:
1. `observe`, then `pm("observe")`;
2. h_goldtie's stall check (as in h_goldtie, before the channel early return);
3. `threats`, then the profiler tag;
4. h_earlyfight's `DIAG` hook (off).

The remaining changes (h_goldtie `carried`, `no_tribute` banking, chip mode, `blocks_respawn`, and h_fightfuel `pm`) don't overlap.

**C6. Turn 1.** `init_static` now runs h_fightfuel's `camp_rng` loop, then h_goldtie's `init_gold`. That is one `reachable_tiles` call plus a loop over the altars.

## Smoke results (merge check only, not evidence of strength)
The smoke games check the merge, not strength. The q24 games diverge from each source's games from turn 1, so a per-game comparison shows each mechanism's *signature*, not its effect size. Strength needs the LOOP.md §4 gate.

**Runs.**
- One onslurm job on the test partition, 56769983, exit 0: 30 games, folders `matches/q24-smoke-*`.
- Source numbers on the vs-tb_merge_b maps come from the existing `matches/b1-<source>-all` runs.
- Three local debug games came from a throwaway instrumented copy (counters plus `GOLD_LOG`). It has since been deleted; the replays are in `matches/q24-dbg-{dunes,curve,pack}`.

**Local check.** `cambc run q24_combo tb_merge_b --map 00anvil` (`matches/q24-local`) won 996-400. It had 0 crashes, empty stdout (no `bot error` lines) and no stderr file. fuelExhausted was 0 for q24_combo and 5 for tb_merge_b.

**Exact SUMMARY lines:**
```
SUMMARY q24_combo vs imit_test: 4W-0L (100%)  avg gems 986 vs 334  avg deaths 2.8 vs 16.5  botFaults(A) 0      [01broken-curve,02the-pond; q24-smoke-lock]
SUMMARY h_3pick vs imit_test: 3W-1L (75%)  avg gems 790 vs 342  avg deaths 2.2 vs 17.0  botFaults(A) 0        [same maps; q24-smoke-lock-src]
SUMMARY tb_merge_b vs imit_test: 1W-1L (50%)  avg gems 756 vs 672  avg deaths 4.5 vs 22.0  botFaults(A) 0     [01broken-curve; q24-smoke-lock-base]
SUMMARY q24_combo vs tb_merge_b: 8W-0L (100%)  avg gems 3 vs 0  avg deaths 1.2 vs 11.0  botFaults(A) 0        [01boss-battle,02guardians,02the-pack,01yellow-brick-road; q24-smoke-goldfuel]
SUMMARY q24_combo vs sf_bank: 4W-0L (100%)  avg gems 1002 vs 204  avg deaths 9.5 vs 30.8  botFaults(A) 0     [00dunes,01starfish; q24-smoke-early]
SUMMARY h_earlyfight_all vs sf_bank: 4W-0L (100%)  avg gems 927 vs 144  avg deaths 16.8 vs 32.8  botFaults(A) 0 [same maps; q24-smoke-early-src]
SUMMARY tb_merge_b vs sf_bank: 3W-1L (75%)  avg gems 836 vs 345  avg deaths 16.0 vs 25.8  botFaults(A) 0      [same maps; q24-smoke-early-base]
```

### Patch 1: lock-memory fix (vs imit_test)
"Frozen" is h_3pick's metric: champion-rounds with 15 or more carried gems unchanged for 150+ rounds, taken from the `gems` timeline.

| Game | tb_merge_b | h_3pick | q24_combo |
|---|---|---|---|
| 01broken-curve B (the traced bug) | L 381-1013, frozen 1638 | W 1183-525, frozen 0 | **W 1168-488, frozen 0** |
| 02the-pond A (the traced bug) | L 15-77, frozen 3162 (`g-tb_merge_b-vs-imit_test`) | W 262-91, frozen 1147 | **W 1007-0, frozen 0** |
| 01broken-curve A | W 1130-331, frozen 0 | L 702-738, frozen 202 | W 1012-510, frozen 0 |
| 02the-pond B | W 1014-15 | W 1014-15 | W 756-339 |

- **Reproducibility.** h_3pick reproduced its NOTES numbers exactly on the cluster (1183-525 and 262-91), so determinism holds across machines.
- **Debug game** (01broken-curve, q24 as B). By r1000 the counters show 35, 94 and 74 `pick_altar` skips per champion of an altar remembered as locked but **out of vision**. Those are exactly the skips tb_merge_b lacked. The game reproduced the smoke game: 1168-488.

### Patch 2: gold play (vs tb_merge_b; the h_goldtie column is from `b1-h_goldtie-all`)
Gold earned, us/them. Every game ended 0-0 on gems and was won on gold.

| Map | Side | h_goldtie | q24_combo | Treasure buys (both bots) |
|---|---|---|---|---|
| 01boss-battle | A | 27,655 / 1,715 | 24,108 / 2,578 | 25 |
| 01boss-battle | B | 29,929 / 4,749 | 25,916 / 4,505 | 25 |
| 02guardians | A | 17,031 / 723 | 14,222 / 443 | 20 |
| 02guardians | B | 14,124 / 696 | 19,827 / 872 | 20 |
| 02the-pack | A | 15,491 / 1,618 | 19,475 / 1,352 | 15 |
| 02the-pack | B | 20,267 / 539 | 21,586 / 1,139 | 15 |

- **Result.** q24 is 6-0, the same as h_goldtie.
- **Debug game** (02the-pack, q24 as A). It printed `GOLDTIE no_tribute True altars 1 usable [] guard_tiles 48`, and chip mode was on for one champion by r1999. It won 0-0 on gold, 18,565 vs 2,232.
- **Other maps.** On 00dunes it printed `no_tribute False ... usable [0, 1]`, and on 01broken-curve `usable [0, 1, 2, 3]`. So `TRIBUTE_USABLE_ONLY` is a no-op there, as designed.
- **01yellow-brick-road** (the stall map): q24 won A 26-0 and B 0-0 on gold (100 vs 0). h_goldtie went W 21-2 and L 0-15 there.

### Patch 4: fuel (fuelExhausted for our side, same games vs tb_merge_b)
| Map | Side | tb_merge_b (opponent in the q24 game) | h_goldtie | h_fightfuel | q24_combo |
|---|---|---|---|---|---|
| 01boss-battle | A | 231 | 402 | 5 | 6 |
| 01boss-battle | B | 270 | 259 | 5 | 6 |
| 01yellow-brick-road | A | 151 | 1,352 | 15 | 22 |
| 01yellow-brick-road | B | 847 | 205 | 51 | 73 |
| 02guardians | A | 0 | 2 | 0 | 0 |
| 02guardians | B | 0 | 0 | 0 | 0 |
| 02the-pack | A | 849 | 97 | 0 | 3 |
| 02the-pack | B | 124 | 196 | 0 | 3 |
| **Total (per game)** | | **2,472 (309)** | **2,513 (314)** | **76 (9.5)** | **113 (14.1)** |

- **Result.** q24 keeps h_fightfuel's fuel profile. Gold play alone (h_goldtie) had 1,352 exhaustions on 01yellow-brick-road A; the combo has 22.
- **The other 22 smoke games.** q24 had 0 exhaustions vs imit_test (4 games) and 3 vs sf_bank (4 games). On those same sf_bank games h_earlyfight_all had 393 and tb_merge_b 257.

### Patch 3: group fight rule all game (vs sf_bank)
Format: result, score, early deaths before r300 (us/them), total deaths (us/them).

| Game | tb_merge_b | h_earlyfight_all | q24_combo |
|---|---|---|---|
| 00dunes A | W 1092-136; 1/2; 7/18 | W 1002-34; 3/6; 7/26 | W 1001-103; 0/4; 2/15 |
| 00dunes B (the traced early-fight loss) | **L 196-1036; 7/1; 20/3** | W 1002-306; 1/1; 13/20 | **W 1002-608; 3/1; 5/17** |
| 01starfish A | W 1041-28; 5/6; 14/39 | W 653-124; 7/3; 32/40 | W 1001-7; 7/5; 17/42 |
| 01starfish B | W 1017-181; 6/2; 23/43 | W 1052-114; 7/4; 15/45 | W 1002-96; 2/6; 14/49 |
| **Sum** | early 19/11, deaths 64/103 | early 18/14, deaths 67/131 | **early 12/16, deaths 38/123** |

**Debug game** (00dunes, q24 as B). It reproduced the smoke game: 1002-608, 16 kills and 5 deaths. By r1000, each of the 5 champions recorded:
- 103-236 advantage turns and 52-116 disadvantage turns;
- 35-107 regroup retreats, with 2 `hit_while_leaving` hits in total;
- 236-760 `retreat_fast` candidates scored by rally distance. That is the C2 integration path working.

No `bot error` or traceback line appeared in any debug log.

## Caveats
- `TRIBUTE_USABLE_ONLY` is untested on a real mixed map: none of the 70 local maps has some but not all altars guard-only. It only matters on unseen maps.
- The group rule reads live API data in `group_balance()`. It does not use h_fightfuel's enemy cache, so it costs the same fuel as in h_earlyfight_all.
- **Next step: the LOOP.md §4 gate.** That means `--maps all` vs tb_merge_b (≥ 82/140), a paired gauntlet, a release run and an analysis session. None of these has been run for q24_combo.

## Review fixes (adversarial merge review, 31 Oct)
**Result: no merge defect found. `src/` was not changed.** The checks below were run independently of the claims above.

**1. Mechanical reference merge.**
- *Method.* tb_merge_b plus h_3pick's two lock-memory hunks (`LOCK_MEMORY_FIX` and the `mem` skip in `pick_altar`), then `git merge-file` with h_goldtie, h_earlyfight_all and h_fightfuel, in that order.
- *Conflicts.* h_goldtie and h_earlyfight_all merged with no conflict. h_fightfuel gave 5 conflicts:
  - the `__init__` state;
  - the `retreat` signature and VALIDATE harness;
  - the regroup `retreat` call in `handle_enemies`;
  - `pm("observe")` vs the stall check;
  - `pm("threats")` vs the DIAG hook.
- *Comparison.* `src/bot.py` differs from this reference only in those 5 regions and in the documented additions:
  - C1 `TRIBUTE_USABLE_ONLY`;
  - C2 `rally` in `retreat_fast` and VALIDATE;
  - C3 `esrc = None`;
  - `GOLD_LOG`;
  - comments.
- *Conflict regions.* Each of the 5 regions holds both sides. This was checked against the diff3 base, so no base-line edit was lost.
- *Conclusion.* Every hunk of every patch is present, and no tb_merge_b code was dropped or duplicated.

**2. AST, function by function.**
- **Single-source functions.** Every function only one source changed is identical to that source's version.
- **No duplicates.** There are no duplicate definitions or constants.
- **Constants.** Every module constant equals its source's value: h_goldtie v2, h_earlyfight_all v3 (`EARLY_ROUNDS = 2000`) and h_fightfuel.
- **Switches.** `DEBUG`, `DIAG`, `VALIDATE`, `PROF`, `GOLD_LOG` and `debug_tb` are off.
- **h_3pick's omitted hunks** in `retreat`, `handle_enemies`, `play_turn`, `read_claims` and `init_static` are all gated by `self.trio`, which is False under `TRIO_MODE = False`. The one exception is the `n_bodies` API call at init, and only trio reads it.

**3. Static checks.**
- py_compile passes.
- There are no undefined globals.
- No `self.` attribute is read without being set.
- Every `self.method(...)` call matches its signature, both positional count and keywords. This matters because most of this code swallows exceptions, so a bad call would fail silently.

**4. Interactions, reviewed by hand.**
- **`retreat_fast` with `rally`.**
  - It orders tiles by the same 4 keys as h_earlyfight's slow `retreat`, where `spawn_pts = rally if rally else self.spawn_pts`.
  - In both versions, an empty rally list falls back to the spawn distance.
  - The rally key is never written into `spawn_cd`.
  - The camp pre-filter (`lim`) depends only on keys 1-2, so it stays exact.
- **`esrc`.**
  - Its only reader is `retreat_fast`, and both call sites run after `threats()` in the same turn.
  - `group_balance()`, `hit_while_leaving()` and the `near` list read live API data.
- **Gold code.** It reads only `G.status`, which `observe_fast` and `observe_slow` set identically, plus its own state.
- **Static memos.** h_fightfuel's `camp_rng` and `spawn_cd` are static, and neither h_goldtie nor h_earlyfight changes their inputs. `G.value` (h_goldtie) is not cached anywhere.
- **Aliasing.** In the default branch, `tribute_ring` is the same object as `altar_ring`. Nothing mutates either in place: `build_static_fields` and `sf_dests` OR them into fresh bitboards.
- **`TRIBUTE_USABLE_ONLY` on a mixed map.** If every usable altar is locked, `free` is empty, so `break_lock` is forced and the carrier walks to a locked usable altar to break the lock. The sources would walk into the guard-only ring instead, which is the intended fix.

**5. Local game.** `./cli/cambc run q24_combo tb_merge_b --map 02arena -o matches/q24-review`:
- W 1002-177 at r1946, with 0 crashes;
- `team-a.stdout` and `team-b.stdout` empty, so no `bot error` line;
- fuelExhausted 0 (tb_merge_b: 1);
- kills/deaths 37/3.
