# imit_uvt2: imitation of ladder team "Us V Them" (play, not just draft)

Built for STRATEGIES V3L-1 (`results/simulated-matches/2026-11-01_0608_h_antifocus/notes.md`). Forked from `c2_respawn` with
`tools/newbot.py`, so it farms, banks and shops as competently as our champion. Every change is behind a
`UVT_*` switch at the top of `src/bot.py`; with `UVT = False` the play logic is c2_respawn's (the draft stays).

## What the ladder showed (15 games with full stats, v3 3-7 and v4 1-4)
- Draft Ren, Stellar, Cassi&Issac, then Ryth, Varg (3-pick = 4 bodies against our 3).
- Builds (buyItem events, the same in every game): Ren Bruiser Health x5, Durability Health x5, then Power Focus
  forever (up to 126 shards); Stellar Treasure Focus, Home Health, Durability Health, then Power Focus (up to 166);
  Cassi Power Focus x5, Durability Focus x5, then Bruiser Health; Issac Treasure / Home / Durability, then Power
  Strength; Ryth Bruiser Health, Durability Health, Power Strength.
- **All 2,596 of their wards were placed on bush tiles** (02treasure-box, which has no bushes: 0 wards).
- Our deaths to Stellar / Cassi / Issac lie within 2 tiles of a bush 40-43% of the time (random tiles: 22%), and
  Stellar took 355-659 damage in games where it scored 12-28 kills: the casters fight from bushes, where we
  cannot see (so cannot target) them.
- Kills involve 2-4 of them (1 enemy: 61 of 429 deaths).

## Changes (src/bot.py, src/draft.py)
| Switch | Behaviour |
|---|---|
| draft `PRIORITY` | Ren, Stellar, Cassi&Issac, Ryth, Varg, ... |
| `UVT_BUILD` | the per-champion build orders above (Power shards combine at 5, so "have" = shards + 5 x emblems) |
| `uvt_dps` (enemy_dps / champ_dps) | strength + modifier x focus x (0.5 if the spell is ready else 0.125) + 0.25 x strength per attack reset: the team fights on its real burst |
| `UVT_CAST_FIRST` | in handle_enemies, a ready damage / stun spell with the target in range is cast before any walk (stun first if the target is not stunned) |
| `UVT_KITE` | ranged casters (Stellar, Cassi): cast at range <= 4 when a spell is ready; otherwise step out of every enemy's reach (walk + basic, + dash, or a ready spell's range) |
| `UVT_LURK` (v2) | ranged casters whose spells are down step into a bush tile no visible enemy shares, stay there and basic-attack from cover |
| `UVT_CONVERGE` | the team focus target's coarse 7x7 cell goes into shared byte 6; healthy allies within 14 that carry < 20 gems walk to it |
| `UVT_BUSH_WARDS` | wards only on bush tiles |

## Reproduction (c2_respawn vs imit_uvt2, the 11 ladder maps, both sides)
```
v1 (no lurk)  SUMMARY c2_respawn vs imit_uvt2: 16W-6L (73%)  avg gems 865 vs 608  avg deaths 8.7 vs 19.8  botFaults(A) 0   [matches/uvt2-s1-c2]
v2 (+ lurk)   SUMMARY c2_respawn vs imit_uvt2: 13W-9L (59%)  avg gems 731 vs 703  avg deaths 13.4 vs 19.6  botFaults(A) 0  [matches/uvt2-s2-c2]
```
For reference, `mb_imit_uvt` (tb_merge_b logic + their draft and Power Focus) lost 23-1 to q24_combo.
v2 reproduces the ladder disasters: 00packs A 65-1000 with 31 of our deaths (13 within 8 of our spawn; ladder
85-1005 and 366-554, 43-44 deaths), 01gold-rush B 401-701 with 28 deaths (ladder 363-605, 44 deaths),
00lost-world A 313-1009 (ladder 213-1009), and the near-bush death profile.
