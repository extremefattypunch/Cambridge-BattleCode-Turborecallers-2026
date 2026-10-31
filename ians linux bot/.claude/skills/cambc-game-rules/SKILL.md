---
name: cambc-game-rules
description: Rules cheat-sheet for Cambridge Battlecode 2026a ("cambc", event cambc2026a). Use whenever reasoning about game mechanics, strategy or drafting, or checking that bot behaviour matches the rules. Covers the win condition and tiebreaks, round/turn order and priority, movement (walk, dash, teleport), camps (HP, strength, range, gold, gems, respawn) and capture, gems/tribute/altars/altar locks, combat, abilities and channels, gold/shards/emblem families/consumables, vision and wards, death/recall/respawn, fuel limits, the draft and draft/shared memory, every champion's stats, both ability slots and passive, and engine constants. Bundles the full official GameRules.md for exact wording.
---

# Cambridge Battlecode 2026a: game rules cheat-sheet

**Source of truth:** `references/GameRules.md` (verbatim copy of the official handbook export `docs/GameRules.md`).
Grep it for exact wording before relying on an edge case:
`grep -n -i "<term>" "$CLAUDE_PROJECT_DIR/.claude/skills/cambc-game-rules/references/GameRules.md"` (or a path relative to the workspace).
Sections are `## The game`, `## Drafting`, `## A champion turn`, `## Maps & movement`, `## Camps & capture`, `## Gems & altars`,
`## Combat & abilities`, `## Items & gold`, `## Vision & wards`, `## Death, recall & recovery`, `## Fuel`, `## Shared memory`,
`## Champion roster`, then one `## <Champion>` per champion. For SDK names and signatures, load the **cambc-bot-api-python** skill.
Values marked *(probe)* were read from the live engine (CLI 4.0.0, engine 2.0.0) via `cambc.constants` / `Champion.design()`.

## 1. Objective, end of game and tiebreaks
- Kill camps, **capture** their region to receive gems and gold, carry the gems to an **altar** and **tribute** them. Only tributed gems score, and they are permanent. Carried gems can be stolen when you die.
- **The first team to 1,000 tributed gems wins immediately.** Otherwise the game ends after round 2,000, and the tiebreaks are, in order:
  tributed gems → **lifetime gold earned** (not gold on hand; Tavi sale refunds don't count) → champion kills → **Team B wins** (the team that acted second in round 1).
- Gold buys stat items. It doesn't score directly, but it is tiebreak #2.

## 2. Round structure and turn order (exact)
1. **Round start:** camp respawns → existing spell/ward updates → **camp captures** → camp turns. At the start of its turn a camp expires zero-timer buffs, acts if awake, then decrements cooldowns and buffs (including new ones) at turn end. Sleeping camps still tick.
2. **Champion turns:** teams alternate, and **the starting team swaps every round**. Within a team, **higher priority acts first, then draft order**. `set_priority` takes effect **next round** and persists.
3. **At a champion's turn start**, zero timers resolve in this order: respawn → ward recharge → buff/shield expiry → **channels complete** (recall, tribute, teleport).
   **At turn end**, timers decrement without triggering. **Spawn healing happens at turn end.**
- **Dead champions still get a turn**, so they can shop.
- Consequences: a capture (round start) can add gems before your tribute completes (your turn start). Camps act before your next turn.

## 3. What a champion may do each turn
- **One ordinary move** (1 tile, any of 8 directions; every champion has move speed 1), **one basic attack**, and **one successful ability cast** shared across both slots.
- **Melee** (basic range 1) can move *and* attack in the same turn. **Ranged** (basic range 3) does move **or** basic attack: either uses up the other.
  Damaging ranged spells marked "Excludes walking" follow the same rule: you can't cast after walking or walk after casting.
- **Attack reset** abilities restore the basic-attack allowance. They only work once the attack has been used (the engine rejects "An available attack cannot be reset").
- All ranges are **Chebyshev** (diagonals count 1). Basic attacks need a **visible** target and deal **Strength** before modifiers.
- Ability cooldown is **8 owner turn ends per slot** (reads 8 right after casting, 7 next turn, and so on).
- **Ward:** needs its charge, which recharges over 10 owner turn ends. **Consumables:** need one in inventory (carry ≤1 of each).
- **Shop** on your own spawn tiles or while dead (Tavi buys shards anywhere). Purchases per turn are unlimited.
- **Channels** (recall, tribute, teleport) block other actions until they finish or are cancelled. Recall and tribute each allow **one start and one cancel per turn**.

## 4. Map and movement
Grid sizes range from 30×30 to 100×100. Maps are symmetric (horizontal, vertical or 180° rotation). +y is north.

| Tile | Walk onto | Dash over | Blocks sight | Notes |
|---|---|---|---|---|
| Wall | no | no | yes | A TP crystal can go past walls |
| Hole | no | **yes** | no | |
| Bush | yes | yes | **yes** (from outside) | From inside you see the whole connected bush and out of it |
| Altar | no | — | — | Tribute from Chebyshev ≤1 |
| Spawn tile | own team only | — | — | Heals to full at your turn end; shop here |

- **Walk:** 1 adjacent tile. **Dash** (ability): up to 2 steps including diagonals along a legal path. It may cross holes but not walls.
  **Teleport crystal** (consumable): to a tile within 3 (Chebyshev), ignoring terrain in between. It **channels for 3 owner turn ends**; damage doesn't stop it, enemy stun or death does, and **it can't be cancelled**.
- **You can never land on** a wall, hole, altar, enemy spawn tile or occupied tile.
- **Hidden blockers:** if a destination that looks legal holds an **unseen** unit (for example an enemy in a bush), the action returns **false**, that tile is revealed for the rest of the round, and **no allowance, cooldown or consumable is spent**, so you can retry elsewhere. A destination already **known** to be occupied raises an error. This applies to walk, dash and TP crystal.
- Ask the SDK for movement masks rather than re-deriving walking rules. The SDK masks account for visible units.

## 5. Camps (monsters)
| Monster | HP | Str (dmg/turn) | Atk range | Gold | Gems | Respawn | Gems per 1k HP |
|---|---|---|---|---|---|---|---|
| Wolf | 1,350 | 20 | 3 | 40 | 4 | 40 rds | 3.0 |
| Elk | 2,400 | 60 | 4 | 90 | 15 | 60 rds | 6.3 |
| Golem | 5,000 | 120 | 4 | 160 | 36 | 80 rds | 7.2 |
| Gem cluster | 120 | 0 | 0 | 0 | 7 | 50 rds | **58** |
| Gold cluster | 120 | 0 | 0 | 20 | 0 | 50 rds | — |
| Monolith | 20,000 | 200 | 5 | 300 | 200 | 150 rds | 10 |

- A **camp group** is a set of monsters connected cardinally (4-neighbour). Rewards combine across the whole group.
  The group **respawns together** after its reward is claimed, using the **longest** member respawn time. **Any occupied spawn tile delays the whole group's respawn.**
- Camps are neutral until hit. **Damage wakes the group.** Awake monsters attack the **nearest champion** each turn and go back to sleep after **2 rounds** with no champion in range.
- Camps have vision 8 and **see through bushes**. They **don't move or chase**.
- Camp attack ranges (3–5) out-range melee (1) and ranged (3) champions. Tank or burst them.
- **If a camp kills you, your carried gems are destroyed** (no one gets them).
- Rough solo maths: a 45-Str attacker needs 30 hits for a Wolf (taking about 600 damage) and 54 for an Elk (about 3,240 damage). Clusters die in about 3 hits for free value.

## 6. Capture
- Once **every monster in the group is dead**, occupy **at least one** of its spawn tiles **uncontested**.
- At a capture phase (round start) your team starts a **5-round** timer (CAPTURE_TIME 5). Later capture phases count it down.
  A **Capture emblem** holder caps the remaining time at **3**. This also applies when the holder joins mid-capture. It never increases a shorter timer, and the reduction persists if the holder leaves while an ally keeps capturing.
- **Leaving the region empty, or an enemy entering, resets progress.** Extra allies don't speed it up.
- Rewards are **split among the allies present at completion**, and the lowest ID gets any integer remainder.
  **Prospector** adds +25% of *your own share* of **cluster** rewards (rounded down separately for gold and gems).
- After rewards are claimed, the respawn timer starts and counts down by 1 each round.

## 7. Gems, tribute and altars
- To tribute, stand within **Chebyshev 1 of an altar** carrying ≥1 gem and start a **tribute channel**.
- **Duration = max(1, ceil(gems_at_start / 10))** owner turn ends. 1–10 gems take 1 tick, 11–20 take 2, and so on. The **Tribute emblem** makes it 33% shorter (rounded up, minimum 1).
  The timer decrements at turn end **including the starting turn** and completes at your **next turn start** after it reaches 0. So 1–10 gems started on turn T are banked at the start of turn T+1.
- The length is based on the bag when you start, but **completion tributes the whole current bag**, including gems gained since. Captures resolve before channels.
- Damage does **not** interrupt a tribute. **Stun, death, or a newly placed enemy altar lock** does. You can also cancel it manually.

### Altar locks
- A consumable costing 10 gold; you can carry 1. Place it on an altar **within 2 tiles**.
- A lock blocks **enemy** tributes at that altar (its owner's team can still tribute there). Placing it **cancels existing enemy tribute channels** at that altar.
- **Five basic attacks** remove it (ALTAR_LOCK_HITS 5). The handbook says a tribute attempt on a locked altar is converted into a basic attack on the lock.

## 8. Combat, abilities, channels
- Basic attack damage = Strength. Spells deal Focus × multiplier (for example Stellar: 70 Focus × 2 = 140).
- Damage modifiers: Durability −10% incoming; Jungle −30% from camps; Monster +15% to camps; Skirmish +5% to champions; Collectors +1% per unique completed family; Heart of Ruin up to +50%. Shields absorb damage first.
- **Stun lasts 1 round.** It interrupts recall, tribute and teleport. Marcella is immune.
- Unit-target spells need a **visible valid target**. Ground spells hit an area (radius 1 = 3×3). Self spells are self-cast.

| Channel | Length (owner turn ends) | Interrupted by | Manual cancel |
|---|---|---|---|
| Recall | 5 (3 with Home) | damage, stun, death | yes |
| Tribute | max(1, ceil(gems/10)) (−33% with Tribute) | stun, death, new altar lock (**not damage**) | yes |
| TP crystal | 3 | enemy stun, death (not damage) | **no** |

Every channel ticks down at owner turn end and executes at the owner's **next turn start** once it reaches zero.

## 9. Gold, items and the shop
- **Gold sources:** captures (camp and cluster gold), **100 base gold per champion kill** (killer only; assists get 0; Hunter adds +50 before bonuses; a linked Cassi/Issac death gives one reward), Marcella's +2 gold per tributed gem, Vesper's +33%, and Treasure's +10% (bonuses add: 43%).
  There is **no passive income** (PASSIVE_GOLD 0) and champions **start with 0 gold** *(probe)*.
- **Shards cost 30 gold.** Each adds that champion's **growth** for one stat (Strength, Health or Focus). **Five matching shards auto-combine** into the family's emblem (150 gold total). **Greed** needs 25 shards (750 gold).
  **You can't buy emblems directly.** Only a *completed* emblem gives its passive. A second emblem of the same family adds no passive, but **all shard stats stack**.
- Buying Health on spawn heals by the amount gained. Tavi's off-spawn purchases raise max HP without healing.
- **Only Tavi can sell** (on spawn, at full purchase price). Refunds don't count as earned gold.

| Emblem family | Stat value of the emblem | Passive (completed emblem only) |
|---|---|---|
| Monster | 5 shards | +15% damage to camps |
| Power | **6** shards | none (one extra shard of stats) |
| Durability | 5 | −10% incoming damage |
| Treasure | 5 | +10% gold gained |
| Jungle | 5 | −30% damage from camps |
| Home | 5 | recall 5 → 3 turn ends |
| Bruiser | 5 of the chosen stat + 1 of each other | none |
| Tribute | 5 | tribute 33% shorter (rounded up, ≥1) |
| Capture | 5 | team capture timer capped at 3 |
| Prospector | 5 | +25% of own cluster-reward share (rounded down) |
| Hunter | 5 | +50 gold per champion kill |
| Skirmish | 5 | +5% damage to champions |
| Greed | **35** (combines at 25 shards / 750 gold) | none |
| Collectors | 5 | +1% damage per unique completed family (including itself) |

**Consumables** cost 10 gold each, you carry at most 1 of each, and they follow the same shop location rules:
**Altar lock** (place on an altar within 2; see §7) and **Teleport crystal** (range 3, ignores terrain, 3-turn channel; see §4).

## 10. Vision and wards
- Champions see **8 tiles** using symmetric shadowcasting (Albert Ford's algorithm). **Walls and bushes block sight; holes don't.**
  From outside a bush you can't see into or past it. Inside one, you see the whole connected bush cluster and out of it, but not into *other* bushes.
- **Vision is per champion:** your own plus **your own ward**. It is **not shared with allies**, so use shared memory to communicate.
- **Wards:** each champion has one free ward. You place it within **2 tiles** (a 5×5 area), it has **vision radius 6**, it is **permanent** and can't be damaged.
  Placing again **replaces** the old ward. The charge recharges over **10 owner turn ends**.
- A tile revealed by a hidden blocker stays visible for 1 round (TILE_REVEAL_ROUNDS 1).

## 11. Death, respawn, recall
- On death, the **killer gets all carried gems and 100 base gold**. Assists get nothing. **Camp kills destroy the gems.**
- You respawn at your next turn start after **60** owner turn-end ticks, once a spawn tile is free, at full HP with abilities reset. Dead champions still take turns, so they can shop.
- **Cassi and Issac share a fate.** If either dies both die, losing both bags, and the killer gets one kill reward (100 gold plus both bags' gems).
- **Recall** takes 5 owner turn ends (3 with Home), and the starting turn counts. You arrive at a **turn start**, so **stay on spawn until that turn ends** to heal to full.
  Damage or stun cancels it, and you keep your gems. Start it somewhere safe.

## 12. Fuel (compute)
- Fuel is Wasmtime fuel, roughly CPU instructions, and is deterministic. Per turn: C++/Rust **100k**, OCaml 500k, **Python 2.5M** (25×).
  The **first draft turn gets 100×** (Python ≈250M) and the **first play turn gets 2×** (Python ≈5M). Unused fuel doesn't carry over.
- **When you run out, the bot is suspended mid-code and resumes from that point next round**, so actions land a turn late on stale data. Budget work.

## 13. Draft, draft memory, shared memory
- Each team picks **3–5** champions, depending on the map. There is one pick per draft round, and both teams pick **simultaneously** with picks revealed as they go.
  You can't pick the same champion twice for your team, but mirror picks against the opponent are allowed.
  **Cassi & Issac are one pick that gives two champions**, so the team gets an extra body.
- The whole map is visible during the draft, and the draft has extra fuel.
  If a draft bot yields, runs out of fuel or crashes without picking, the remaining picks are **random**.
- **Draft memory** is 1,024 bytes, written during the draft and **read-only for all your champions** during play.
- **Shared memory** is **8 bytes** per team, readable and writable for the whole match and invisible to the opponent.

## 14. Champions
All champions have vision 8 and move 1, both slots have 8-turn cooldowns, and there is one cast per turn. Basic range is melee 1 / ranged 3. "r4" means Chebyshev cast range 4.
"excl" means *Excludes walking* (can't combine with a walk that turn). HP/Str/Focus are shown as base / +growth per matching shard.

| Champion | Type | HP | Str | Focus | Slot 0 | Slot 1 | Passive |
|---|---|---|---|---|---|---|---|
| Ryth | Melee | 1200/+100 | 45/+4.5 | 100/+10 | **Area stun**: 1×F dmg + 1-rd stun, radius 1, ground r4, excl | Attack reset | +Str = 1% of bonus HP |
| Vesper Vale | Ranged | 1000/+100 | 45/+5 | 100/+10 | Attack reset | Dash 2 | +33% gold (43% with Treasure) |
| Vendetta | Melee | 1000/+100 | **70**/+6 | 100/+10 | Attack reset | Dash 2 | Any kill (camps too) resets all her cooldowns |
| Cassi (+Issac) | Ranged | 600/+65 | 30/+3 | 100/+13 | Damage 2×F, enemy/camp r4, excl | **Stun** 1 rd, no dmg, enemy/camp r4, walking OK | Linked death with Issac |
| Issac (+Cassi) | Melee | 900/+80 | 45/+3 | 100/+10 | Attack reset | Dash 2 | Linked death with Cassi |
| Stellar | Ranged | 650/+65 | 30/+3.5 | 70/+8.5 | Damage 2×F, r4, excl | AoE 1.4×F radius 1, ground r4, excl | none |
| Prism | Ranged | 700/+65 | 35/+2.5 | 80/+8 | Dmg 1.5×F + 1-rd stun, r4, excl | AoE 1×F radius 1, ground r4, excl | +1.5 Focus per carried gem |
| Marcella | Melee | 1200/+100 | 45/+4.5 | 60/+**14** | **Enhanced** attack reset: next enhanced attack stuns 1 rd | Damage 2×F, r4, excl | Stun-immune; +2 gold per gem tributed |
| Tavi | Ranged | 900/+75 | 45/+5 | 110/+10 | Attack reset | Dmg 1.6×F + 1-rd stun, r4, excl | Buys shards anywhere (consumables only on spawn or dead); can sell on spawn for full price |
| Willow | Ranged | 700/+50 | 55/+3 | **140**/+5 | **Heal** another ally up to 3×F, r4, walking OK | Attack reset | none |
| Ren | Melee | 900/+100 | 35/+5 | 100/+9 | Dmg 1.1×F + 1-rd stun, r4, excl | Dash 2 | Retaliates 0.2×F on whoever damages him (even as he dies) |
| Varg | Melee | 1000/+100 | 45/+5 | 100/+10 | Attack reset | Self-shield 2.5×F for 5 turns | Basic attacks splash Str to other enemies/camps within radius 1 of the target |
| Heart of Ruin | Melee | 1000/+100 | 30/+3 | 100/+10 | Self-shield 1.5×F for 5 turns | Dash 2; on landing 1.5×F to radius 1 + 1-turn stun | +0→50% to all damage, linear in missing HP% (shields don't count) |

*(probe)* `AbilityInfo` details: every "Dash 2" is `AbilityDash(range=2)`, and only Heart of Ruin's has `radius=1, modifier=1.5, duration=1`.
Ryth slot 0 is `AbilityAoeDamage(duration=1)` (the stun); Stellar and Prism AoE have duration 0. Prism, Tavi and Ren's damage+stun are `AbilityCc(modifier>0)`; Cassi's stun is `AbilityCc(modifier=0)`.
Target masks: damage and CC = enemies and camps; AoE = enemies, camps and ground; heal = allies; attack reset and shields = self; dash = ground.
Every champion's `camp_damage_multiplier` is 1.0.

**Draft enum vs runtime enum (they differ!):** `ChampionDraft` runs RYTH 0, VESPER_VALE 1, VENDETTA 2, **CASSI_AND_ISSAC 3**, STELLAR 4, PRISM 5, MARCELLA 6, WILLOW 7, REN 8, VARG 9, TAVI 10, HEART_OF_RUIN 11.
`ChampionType` runs RYTH 0, VESPER_VALE 1, VENDETTA 2, CASSI 3, ISSAC 4, STELLAR 5 … HEART_OF_RUIN 12 (draft index ≥4 ⇒ type = draft + 1).
Heart of Ruin (draft 11) **is draftable** *(probe)*, even though the starter bot's `range(11)` comment says "released champions only".

## 15. Engine constants *(probe, `cambc.constants`)*
CAPTURE_TIME 5 · CAMP_SLEEP_TIME 2 · RESPAWN_TIME 60 · RECALL_TIME 5 · SUBMIT_GEM_DURATION_MULTIPLIER 0.1 · SUBMIT_GEM_BASE_DURATION 0 ·
SUBMIT_GEM_MINIMUM_DURATION 1 · SUBMIT_GEMS_RANGE 1 · MAX_ROUNDS 2000 · WINNING_GEMS 1000 · KILL_GOLD 100 · ASSIST_GOLD 0 · PASSIVE_GOLD 0 ·
SPAWN_HEALING 1.0 · ACTIVE_WARDS 1 · SHARED_MEMORY_BYTES 8 · DRAFT_MEMORY_BYTES 1024 · TILE_REVEAL_ROUNDS 1 · WARD_COOLDOWN 10 ·
WARD_LIFETIME −1 (permanent) · WARD_VISION_RADIUS 6.0 · WARD_PLACEMENT_RADIUS 2.0 · ALTAR_LOCK_HITS 5 · TP_CRYSTAL_TIME 3.
Passive tuning (`constants.passive_abilities`): PRISM_FOCUS_PER_GEM 1.5, VARG_SPLASH_RADIUS 1.0, VESPER_VALE_BONUS_GOLD_PERCENT 33,
MARCELLA_TRIBUTE_GOLD_PER_GEM 2, RYTH_HEALTH_STRENGTH_RATIO 0.01, REN_RETALIATION_FOCUS_RATIO 0.2, HEART_OF_RUIN_MISSING_HEALTH_DAMAGE_MAX_BONUS 0.5.
Item data *(probe)*: shards cost 30 with combine_count 5 (Greed 25). Emblems are `is_purchasable() == False`. Point values: shard 1, Power emblem 6, Bruiser-Health emblem 5 HP/1 Str/1 Focus, Greed emblem 35.

## 16. Strategy-relevant implications (derived, not official)
- Gem clusters (7 gems for 120 HP) and Monoliths (200 gems) are the outliers. Wolves are poor gem value but safe early gold.
- Tribute in batches of ≤10 for single-tick channels, or carry more and accept a longer channel. The whole bag is banked either way, but carried gems are at risk.
- Enemy altar locks plus stuns are the counter to tributes. Watch `has_altar_lock` before walking to an altar.
- Standing on a camp's spawn tile blocks that group's respawn. That can deny the enemy or delay your own farm.
- Priority and the alternating starting team decide who acts first in close fights and captures.
