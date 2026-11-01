# h_antifocus: counter the focus-caster / bush-ambush comp (STRATEGIES V3L-1)

Forked from the champion `c2_respawn` (website v4) with `python3.12 tools/newbot.py c2_respawn h_antifocus`.
Only `src/bot.py` changed (c2 md5 `83d844c8...` -> `0fdc5268...`); `draft.py`, `main.py`, `randomness.py` are
byte-identical. Report: `results/simulated-matches/2026-11-01_0608_h_antifocus/notes.md`. Imitation used: `bots/imit_uvt2`.

## Why
Ladder team "Us V Them" (~1,539) beat v3 3-7 and v4 1-4 (29 of our champions dead per game). Their Ren / Stellar /
Cassi stack Power Focus (Stellar up to 166 shards: a 2 x F nuke of ~2,100 at range 4), 100% of their 2,596 wards go
on bush tiles, and our deaths to their casters cluster at bushes. c2's threat model sees an enemy as
`strength + 0.15 x focus` within `attack_range + 1`, i.e. a ready range-4 nuke is invisible to it, and a caster
hidden in a bush (invisible from outside) is not seen at all: c2 keeps farming while it is shot.

## Changes (all behind `AF*` switches; with `AF = AF_UNSEEN = AF_HEADCOUNT = AF_BUSH_WARD = AF_SHARE = False`
the logic is c2_respawn's, apart from `read_claims` reading only the claim bytes when `AF_SHARE`)
| Switch | Where | Behaviour |
|---|---|---|
| `af_threat(e)` | new | per visible enemy, per turn: reach = basic range + 1, + 2 with a ready dash, or a ready damage/stun/area spell's range (+ radius, + 1 if it allows walking); burst = strength (x2 with a ready attack reset) + modifier x focus per ready spell. Read from the enemy's own `abilities()` records and `cooldown()` (both work on visible enemies), never from names |
| `AF_ONESHOT` 0.7 | handle_enemies | summed burst of the enemies whose reach covers us >= 0.7 x our hp: no new fight unless the target dies now, adjacent melee only struck if it dies in two hits, retreat |
| `AF` | retreat_fast | each enemy's danger uses max(basic reach, `af_threat` reach) and max(strength, burst) |
| `AF` | handle_enemies | retaliation passive (Ren): ratio uses + 1.5 x 0.2 x focus incoming per turn while we hit it |
| `AF_HEADCOUNT` | handle_enemies | q24's "advantage" no longer cancels v2's headcount flee while burst in reach >= 0.5 x hp and enemies near > allies near + 1 |
| `AF_RECALL_PAD` | recall_safe | every enemy beyond max(basic range + 4, reach + 2) |
| `AF_UNSEEN` | play_turn_main, right after threats | hp lost since the end of our last turn minus what awake camps, visible enemies (full burst, cooldowns ignored) and unseen live camps in range can explain > 60 -> **hidden attacker**: drop the target if within 6, step (or dash when it gains more) away from the unseen bush tiles within 5 until 5 tiles clear (max 6 turns), then recall below 60% hp; groups within 6 of the spot score x0.35 for 60 rounds |
| `AF_SHARE` | shared bytes 5/6 (only with <= 5 bodies) | the ambush spot's 7x7 cell and round // 4, so teammates down-weight targets there too (TTL 60 rounds) |
| `AF_BUSH_WARD` | try_ward | for 300 rounds after a hidden hit or after seeing an enemy whose ready burst >= 0.5 x our max hp: ward an unseen bush tile within 2 (nearest the ambush spot, else the farming target). A ward inside a bush sees that bush, so the hidden caster becomes visible and targetable |
| `AF_LOG` | debug only | prints ambush / one-shot decisions (False here; `bots/dbg_afprobe` = this bot with AF_LOG and DIAG on) |

## Scope
Most rules only fire against burst or hidden attackers (one-shot needs burst >= 0.7 x hp; bush wards need an alert;
ambush needs unexplained damage). Not inert: `retreat_fast` and `recall_safe` use the ready-dash / ready-spell reach
for every enemy, so mirror fights change too. Measured as a whole bot (gated alone), see the report.

## Tests
See `results/simulated-matches/2026-11-01_0608_h_antifocus/notes.md` (SUMMARY lines for the imitation screens, vs c2_respawn,
vs tb_merge_b and vs imit_uvt2 on all maps).
