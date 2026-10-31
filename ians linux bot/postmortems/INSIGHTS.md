# Postmortem insights for cambc 2026a (Sprint 3)

Synthesised 2026-10-31 at about 15:20 EDT, roughly 5 hours before the Sprint 3 lock. Sources are in `notes/` (one file per source) and `raw/` (the downloads, treated as untrusted data).
The game rules come from `.claude/skills/cambc-game-rules/SKILL.md` and the API from `.claude/skills/cambc-bot-api-python/SKILL.md`.

**Honesty up front:**
- **No winning team has published a postmortem for 2026a.** The game is still running.
- The only same-game evidence is two GitHub repos. The valuable one is a **census of about 1,040 ranked games played by the current top-20 ladder teams**, compiled by a mid-ladder team (Faisal-Saqib).
  - It shows what the top teams *do*, not why they win. Selection effects are likely.
- Every other source covers a different game: MIT 2020-2026, and the spring-2026 Cambridge builder/conveyor game. They transfer as engineering and process lessons, not as strategy.
- **Our own baseline numbers**, which no source provides, are in section 2.9. They come from `postmortems/match_metrics.py` run over the existing `matches/*-final` folders, all played against `starter-python`.
  Other agents have edited bots since, so re-measure before acting.

---

## 1. Source index

| # | Title | Event / year | Team | Placement | Link | Local notes | Same game (2026a)? |
|---|---|---|---|---|---|---|---|
| 1 | CambridgeBot docs: top-20 strategy census, deep analysis, top-team findings, full strategy | cambc **2026a**, docs from 27-28 Oct 2026 | Faisal-Saqib (Rust bot); the data covers the top-20 ladder teams | Author is mid-ladder; the census covers the top 20 | https://github.com/Faisal-Saqib/CambridgeBot/tree/main/docs | `notes/cambc2026a-faisal-saqib-top20-meta.md` | **yes** |
| 2 | Bot1 v4 STRATEGY.md | cambc **2026a** (SDK 2.2.5 to 3.0.1) | MohnishDhangar | Unknown, probably not top tier | https://github.com/MohnishDhangar/Cambc/blob/main/bots/Bot1/STRATEGY.md | `notes/cambc2026a-mohnishdhangar-bot1.md` | **yes** (some constants are stale) |
| 3 | Pantheon postmortem (bot "Khaos") | Cambridge BC 2026 spring (builder/conveyor game, Python) | Pantheon | **1st, Grand Finals**; 3rd at the International Qualifiers | https://raw.githubusercontent.com/HerbertTheBird/Cambridge-Battlecode/main/postmortem/postmortem.pdf | `notes/cambc2026-pantheon-postmortem.md` | no |
| 4 | Make Fire postmortem | Cambridge BC 2026 spring | Make Fire (Ismail Fateen, Ahmed Emara) | Top 16 in 4 sprints; one win short of the finals | https://ismailfateen.me/blog/cambc_postmortem | `notes/ismailfateen-cambc-postmortem.md` | no |
| 5 | muteki README | Cambridge BC 2026 spring | Muteki | Finalist, 5th/6th | https://github.com/lxorb/muteki | `notes/cambc2026-muteki-repo.md` | no |
| 6 | cambridge-battlecode README | Cambridge BC 2026 spring | CoffeeCoder1015 | Around 70th of 587, peak 9th | https://github.com/CoffeeCoder1015/cambridge-battlecode | `notes/cambc2026-coffeecoder-repo.md` | no |
| 7 | Generalized Stroke's Theorem postmortem | MIT BC 2026 "Uneasy Alliances" | GST | **2nd overall** | https://battlecode.org/assets/files/postmortem-2026-generalized-strokes-theorem.pdf | `notes/mit-2026-generalized-strokes-theorem.md` | no |
| 8 | battlecode.org Past Years (list of links) | MIT 2019-2026 | n/a | n/a | https://battlecode.org/past.html | (inside #7's notes) | no |
| 9 | Just Woke Up postmortem | MIT BC 2025 | Just Woke Up | **1st overall** | https://battlecode.org/assets/files/postmortem-2025-just-woke-up.pdf | `notes/postmortem-2025-just-woke-up.md` | no |
| 10 | confused postmortem | MIT BC 2025 | confused (solo) | **2nd overall** | https://battlecode.org/assets/files/postmortem-2025-confused.pdf | `notes/postmortem-2025-confused.md` | no |
| 11 | Om Nom, "Money Is All You Need" | MIT BC 2025 | Om Nom | **3rd overall**; US Qualifier winner | https://battlecode.org/assets/files/postmortem-2025-om-nom.pdf | `notes/postmortem-2025-om-nom.md` | no |
| 12 | The Kragle postmortem | MIT BC 2025 | The Kragle | About 27th, missed the finals | https://battlecode.org/assets/files/postmortem-2025-the-kragle.pdf | `notes/postmortem-2025-the-kragle.md` | no |
| 13 | Cout for Clout strategy guide | MIT BC 2024 | Cout for Clout | **1st** in the high-school division, 2nd combined | https://battlecode.org/assets/files/postmortem-2024-cout-for-clout.pdf | `notes/postmortem-2024-cout-for-clout.md` | no |
| 14 | Gone Fishin' strategy report | MIT BC 2023 | Gone Fishin' | **2nd overall** (1st seed) | https://battlecode.org/assets/files/postmortem-2023-gone-fishin.pdf | `notes/postmortem-2023-gone-fishin.md` | no |
| 15 | Don't @ Me postmortem | MIT BC 2023 | Don't @ Me | Finalist, 7th | https://battlecode.org/assets/files/postmortem-2023-dont-at-me.pdf | `notes/postmortem-2023-dont-at-me.md` | no |
| 16 | Java Best Waifu (XSquare) postmortem | MIT BC 2020 | Java Best Waifu | **1st overall** | https://battlecode.org/assets/files/postmortem-2020-java-best-waifu.pdf | `notes/postmortem-2020-java-best-waifu.md` | no |

The following were referenced but not saved, because GitHub timed out: the Make Fire bot source, the 4 Musketeers Bug2 `Pathfinding.java`, and the GST bot repo.

---

## 2. What we know about THIS game (2026a): highest-value section

Everything here comes from sources #1 and #2. Numbers are top-20 averages from about 1,040 ranked games and 1,869 team-games, measured 27-28 Oct.
"Habitual" means the team does it in at least half its games.

### 2.1 Draft
- **The core is universal.** Heart of Ruin, Marcella, Vendetta and Vesper Vale are drafted by **20 of 20** top teams. Ryth is drafted by 17 of 20, and Tavi by 9 of 20 as the fifth pick.
- **The most common 5-pick is HoR + Vesper + Vendetta + Marcella + Ryth.** procless, NEETCoders, print dont int, meow, Jupiter, German Empire and Trzy Kwaterki play it in 47 to 70% of their games.
  - **#1 Mite (67% win)** plays Vesper + Vendetta + HoR + **Tavi** + Marcella (66 of 99 games).
  - Intercontinental Fish (#2) uses **Cassi&Issac** as the fifth pick, which gives 5 picks and 6 bodies.
  - Ad Astra plays HoR + Varg + Marcella + Vesper + Ryth.
- **Rarely picked:** Stellar (3 teams), Ren (4), Prism (5), Willow (6), Cassi&Issac (7), Varg (10).
- **Gold and damage share by champion:** Marcella 30% gold and 28% damage; Vesper 27% and 25%. They are the carries. HoR and Vendetta take about 14-15% each. Ryth takes about 7-9% and is the frontline anchor.
- **Pick order for 3-4 picks** is not given by any source. The shares suggest Vesper and Marcella first, then HoR and Vendetta. *(This is an inference.)*
- **Mirror picks are allowed** and picks are simultaneous, so denial drafting is pointless. Draft for our own kit.
- **Our gap:** none of our four bots drafts this core.
  - `tb_aggro` excludes HoR.
  - `tb_deathball` doesn't list HoR at all.
  - `tb_economy` has HoR 10th.
  - `tb_splitfarm` has HoR 6th.
  - All four rank Varg, Cassi&Issac and Willow highly, and the top 20 mostly avoid those three.
- **Caveat:** our combat code must actually use these kits, or the draft change could lose games.
  - HoR: slot 0 is a self-shield (1.5×F). Slot 1 is a dash to a ground tile that lands for 1.5×F in radius 1 plus a stun.
  - Marcella: slot 0 is an enhanced attack reset (the next attack stuns) and only works after the basic attack has been used. Slot 1 is 2×F damage at r4 that excludes walking.
  - Vesper and Vendetta: attack reset plus Dash 2. Vendetta's kills, including camp kills, reset all her cooldowns.
  - Ryth: slot 0 is an area stun (ground, r4, excludes walking). Slot 1 is an attack reset.

### 2.2 Items
- **Bruiser-family shards on the main stat:** 18 of 20 habitual, 58% win rate. Bruiser is also the most stat-efficient family: the completed emblem is worth 5 main + 1 + 1 = 7 shard-points for 150 gold, against 6 for Power and 5 plus a passive for the others.
  - Vesper: Bruiser **Strength**, by far. Her kit has no Focus damage. Then Bruiser Health, then Power Strength.
  - Marcella: Bruiser Focus, Health and Strength in roughly equal parts.
  - HoR: Bruiser Health or Focus. The shield and the dash both scale with Focus, and missing HP is a damage bonus.
  - Vendetta: Bruiser Strength, then Health.
  - Ryth: Bruiser Health.
- **Never habitual among the top 20, with low win rates:** Jungle (27% over 107 games), Treasure (27%), Prospector (34%), Durability (12%, n=8), Monster (20%, n=5), Capture.
  - This is confounded: weaker bots might simply buy them.
  - Even so, `tb_splitfarm`, `tb_economy` and `tb_aggro` all open with **Jungle and Monster**, and **no bot of ours buys Bruiser**.
- Gold has no passive income (it comes only from captures, kills and passives), and **gold on hand gives no stats**. Shop promptly whenever you are on spawn or dead (Tavi can buy shards anywhere).

### 2.3 Banking and gem protection: the one habit all 20 share
- **Low carried-gem loss:** 20 of 20. Lost carried gems stay at or below 15% of submitted gems, and **those games win 67%**.
  Top teams lose very few champions to camps: **0.2 to 1.8 camp deaths per game**. A camp kill destroys the gems.
- **Mean tribute size is 32 to 56 gems.** Teams that tribute small and often (mean under 25) win only **35%**.
  Two top-20 teams are exceptions: print dont int at 23 and Univardisty at 17.6.
  The likely mechanism is that every trip to the altar is walking time not spent farming. Tribute duration is only ceil(gems/10), so a 40-gem tribute costs 4 turns.
- **Source #1's banking rule (v22, its best version):**
  - **Normal:** bank at 30 or more gems anywhere, 15 or more if the altar is within 15 (path distance plus a danger penalty), 5 or more if within 4.
  - **Threatened:** halve those thresholds. Threatened means an enemy was seen within 14 tiles in the last 40 rounds, an ally died in the last 100 rounds, or HP is under 60%.
  - **Always bank** once banked plus carried reaches 1000, or after round 1900.
  - **Altar choice:** the nearest by walking distance, +12 if enemies were seen near it in the last 40 rounds.
  - **While channelling:** cancel the tribute only if nearby enemies would kill us first, unless this tribute wins the game.
- **Our gap (§2.9):** our mean tributes are 13 to 23 gems, and **30 to 46% of our tributes are under 10 gems**.

### 2.4 Captures and team shape
- **One champion captures** (19 of 20 habitual, single-recipient rate 89 to 98%). The others guard, zone or go farm elsewhere.
  A capture splits its reward among the allies standing there, and extra allies don't speed it up. So stacking on a capture only wastes helper time.
  - Source #2's election rule: nearest first, then the least-invested champion (so upgrades spread), then slot order.
  - **Cache the choice until the capture completes.** Re-elect if the recipient dies, recalls or abandons the capture.
- **Fight as a pack, farm spread out.** Top teams average 2.4 to 3.4 credited attackers per kill, and simultaneous clears are a mean 12 to 24 tiles apart.
  - **Rigid whole-team cohesion failed.** "Everyone within 2-3 tiles" went **19/280** locally, and a regroup variant went 3/10 online.
  - What worked better was **alert-triggered regrouping**: farm independently, and close to within about 3 tiles of a leader or carrier only after an enemy sighting or an ally death.
- **Carry concentration is optional.** Ad Astra's Vesper took 64-74% of team gold in its wins, while Mite spreads gold evenly.
  There is no gold-transfer action, so concentration has to come from routing captures to the carry. It lost 0-1046 on the_line, so it isn't map-proof. Low priority for us.

### 2.5 Vision, locks and crystals
- **Wards:** 20 of 20 habitual. Top teams place about 86 to 202 wards per team per game, roughly 17 to 29 per champion. That is close to every time the ward recharges (10 owner turns).
  - Placement: at altars where carriers get ambushed, and on approach lanes toward the enemy.
  - **Our bots place zero wards.**
  - Caveat: source #1's own ward experiment (v21) went 2/10 online, probably because of where it placed them. Placing a ward uses only its own charge, not the move, attack or cast allowance (rules §3), so it costs nothing if it can't throw.
  - The vision only helps the champion that owns the ward, unless that champion relays sightings through shared memory.
- **Altar locks:** 12 of 20 habitual and 14 of 20 ever. Some teams place 5 to 10 a game: meow 10.4, new team(4) 10.1, Claudus Maximus 8.3, SSSA 7.6.
  - A lock costs 10 gold and is bought on spawn or while dead. Place it on an altar within 2.
  - Placing it **cancels enemy tribute channels at that altar**, and it then blocks enemy tributes there until it takes 5 basic attacks.
  - Defensive side: check `vision.has_altar_lock(altar)` (or `altar_lock_tiles(Team.ENEMY)`) before routing a carrier, and choose another altar or break the lock.
  - Only `tb_aggro` references locks at all.
- **Teleport crystals:** 9 of 20 habitual and 17 of 20 ever. Usage is heavily map-dependent. Crystals bought per sample (17 to 41 team-games per map): 01starvation 531, 01big_world 325, 01gold_rush 249, 01concentrated_wealth 230, 02the_pond 198, 00quadrants 189, 01islands 175.
  The common feature is maps with **regions you can't walk to or very long walks**. A crystal is range 3, ignores terrain and channels for 3 turns. Only death or an enemy stun interrupts it.

### 2.6 Map archetypes: a big effect, so detect them in the draft
The same bot went **5-0 on expanse and 1-4 on the_line** (source #1). Per-map census figures for maps that also appear in our local `maps/` (names use `-` locally and `_` in the census):

| Map | Top-20 signal | What it implies |
|---|---|---|
| 00the_line | One harmless jackpot group holds **161 of 193 gems**; mean tribute 59.8; 0 camp deaths | Brawl map: contest the jackpot as a team, bank together, kill carriers |
| 00vault | Mean tribute **149**; 0 camp deaths | Jackpot or brawl |
| 01boss_battle, 02guardians | Mean tribute **197 and 256**; **camp deaths 44 and 49** per sample | Altars are gated by a monolith or strong camps: hoard gems, then gather 3 or more and kill the gate together |
| 00stampede | Mean tribute 112; 266 wards per game; 12 kills | Big hauls, heavy vision |
| 01elk_arena | **19.7 kills per game** (average 7.3); 359 wards; 218 locks | Fighting map |
| 01islands, 01big_world, 01starvation | Crystals 175 / 325 / 531; few kills on islands and big_world | Disconnected regions: buy TP crystals |
| 02the_pond, 01gold_rush | Farm spread about 8-9 tiles; carry share 0.71 on the pond | Compact maps |

**Detection rules from source #1 (draft turn: full map visible, about 250M fuel):**
- **Jackpot:** one group holds 60 or more gems and at least 35% of the map's gems. Every champion within 12 tiles stands on it, and the team banks together.
- **Brawl map:** one harmless group holds 50% or more of the map's gems. Play aggressively all game: chase hurt enemies (under 45% HP) and widen the engage radius from 5 to 8.
- **Monolith-gated altars:** every altar is walled behind a camp.
  - Hoard gems.
  - From round 200, or once holding 60 gems, set a shared-memory flag.
  - Gather min(alive, 3) champions within 9 tiles (or wait at most 60 rounds), kill the gate camp together, then bank.
- **Disconnected regions:** compute walk components (walls, holes, altars and the enemy spawn blocked). If any camp group or altar is unreachable on foot, buy crystals. `tb_splitfarm` already does this.
- Write the profile into **draft memory** (1,024 bytes, read-only during play, zero-padded, so include a version byte).

Source #2 adds a draft rule for monolith maps: if **every** gem-bearing group has at least 10,000 HP, draft casters.
**Its siege trick doesn't work under our rules.** It stands outside a monster's range but inside spell range 4, and it relies on Euclidean ranges. Our engine uses Chebyshev throughout, and elk and golem have range 4 and monolith range 5. It only works against wolves (range 3).

### 2.7 Farming job scoring (source #1, v20/v22; mid-ladder, but concrete)
- **Formula:**
  `score = (gems + gold·w) / (travel + respawn_wait + clear_time + HP_cost/n + 6) / n`
  - n is the number of champions on the group, including me.
  - w = 0.15 before round 300, 0.08 before round 800, then 0.03.
  - clear_time = group HP / (my damage × n).
  - HP_cost = expected damage / (60% of max HP) × (6 + distance from spawn to camp). Each lost "bar" of HP costs a trip home.
  - Skip groups that respawn in more than 25 rounds.
- **Chaining:** harmless clusters within 5 tiles are chained, up to 6 groups.
- **Join caps:** a harmless group takes ceil(HP/700) champions; a dangerous group takes up to 4.
- **Multipliers:**
  - ×0.4 on the enemy half (×0.75 after round 250);
  - ×0.6 where 2 or more enemies were seen in the last 40 rounds;
  - ×0.5 within 8 tiles of one of our deaths in the last 120 rounds;
  - **×1.25 hysteresis** for the current job.
- **Re-choose every 5 rounds.**
- **Stuck guard:** after 6 turns with no action, skip that altar for 40 rounds or that camp for 30.

### 2.8 Fighting champions (source #1)
- **Kill-time model:**
  - Our time to kill = their HP / (my damage + allies within 8).
  - Their time to kill us = our HP / their damage.
  - **Losing** = ours is more than 1.3× theirs. **Clearly losing** = more than 1.6×, or outnumbered within 6 tiles.
  - Carrying 30 or more gems lowers the "clearly losing" ratio to 1.0.
- **Target choice:** the fastest kill in reach. Prefer **gem carriers**. Keep a **shared focus target in one shared-memory byte**.
- **Retreat:**
  - When HP < 2.5 × incoming damage + 10%, unless we can finish the target.
  - **Never run from an adjacent melee champion while we can hit back.**
  - Flee: search up to 7 steps for a tile outside every threat range. **Recall only once out of range**, since damage cancels a recall.
- **Early aggression:** 3 or more kills before round 200 happened in 224 games and **won 80%**. No top team does it habitually, and it is probably partly a selection effect (stronger bots get early kills). Treat it as a hint, not a rule.
- **Mechanics to exploit (rules sheet):**
  - A stun cancels **tribute, recall and teleport**. Marcella is stun-immune.
  - A tribute isn't cancelled by damage.
  - `set_priority` takes effect next round. The starting team alternates every round.
  - Time the burst so a carrier dies before its recall (5 turns, broken by damage) or tribute completes.

### 2.9 Our numbers against these benchmarks
These come from `postmortems/match_metrics.py` over the existing eval folders, all **against starter-python**. The bot versions may be older than the current code.

| Folder | Games | Mean tribute | Tributes < 10 gems | Camp deaths/game | Gems lost to camps/game | Gems lost to champions/game | fuelExhausted/game |
|---|---|---|---|---|---|---|---|
| tb_aggro-final | 40 | 14.4 | 39% | 1.6 | 3.6 | 2.1 | **250** |
| tb_deathball-final | 40 | 14.3 | 32% | 2.5 | 7.7 | 12.7 | 41 |
| tb_economy-final | 40 | 20.9 | 25% | **11.1** | **41.2** | 9.0 | **616** |
| tb_splitfarm-final | 7 | 16.8 | 35% | 2.1 | 5.3 | 27.1 | **1057** |
| *top-20 reference* | | *32 to 56* | | *0.2 to 1.8* | *gem loss ≤ 15% of submitted* | | *(not reported)* |

- **Fuel exhaustion is our biggest silent problem.** On 01islands, `tb_splitfarm`'s Vendetta was suspended on **about 855 of roughly 2,000 rounds**, starting at round 1.
  Each suspension means that champion acts a turn late on stale data (rules §12).
- `tb_economy` dies to camps 5 to 50 times more often than top teams, and every one of those deaths destroys the carried gems.
- Every bot tributes in small batches. The census associates that pattern with a 35% win rate.

---

## 3. Transferable lessons from other games, mapped onto 2026a

| Lesson (source) | Concrete 2026a behaviour |
|---|---|
| **Never blow the compute budget**, especially on a unit's first turn; the early game snowballs (Om Nom #11). Spread expensive analysis over turns with a budget check (Pantheon #3, Make Fire #4) | Check `cambc.fuel_remaining()` inside every scoring loop and break out early with the best result so far. Then always act and `end_turn()`. Build DistanceFields once per static goal and keep them across turns. Do one-off map analysis in the draft (about 250M fuel), or on the first play turn (about 5M) as resumable chunks |
| **Commit to finish** instead of leaving at a fixed resource threshold (Om Nom #11) | Don't retreat from a camp that will die within about 2 turns if our HP covers it. Never cancel a tribute in its final tick unless that would mean death. Don't abandon a capture with 1 to 2 rounds left |
| **XSquare tile-scoring micro** (#16, #13, #7, #11): score the 9 tiles, compare lexicographically | For each of the 9 tiles, plus dash tiles for HoR, Vesper and Vendetta, compute: can I hit my target from here (ranged champions move OR attack; "excl" spells forbid walking), incoming damage next turn (sum of awake camps and visible enemies in range), am I the **nearest champion** to an awake camp (camps hit the nearest), distance to allies, and distance to an altar or spawn when low. Pick by explicit priority |
| **Kite static shooters and sync entries** (Just Woke Up #9) | Camps out-range champions (3 to 5 against 1 or 3), so kiting doesn't work. Instead, **enter a group's range together** so the camp can hit only the nearest champion, and keep ranged champions at full range so the melee stays nearest (source #1 does this too) |
| **Hold the high-value action** (GST #7 held a captured enemy before throwing) | Save stuns (Ryth area stun, HoR landing dash, Marcella enhanced attack, Tavi) and altar locks for an enemy that `is_submitting_gems()`, `is_recalling()` or `is_teleporting()`. Don't spend them on chip damage |
| **Weight smart enemies above dumb neutrals, but stay out of the neutral's lane** (GST cat micro #7) | In a fight near camps, enemy champions come first. Never be the nearest champion to an awake golem or monolith unless you are the tank, and bait enemies into being nearest |
| **Hazards as path costs, not walls** (GST dig cost, Pantheon soft threat cost 20, JWU tower range) | Path with a danger cost for tiles inside awake-camp ranges and last-seen enemy reach, not a hard block. Fall back to plain paths if no route exists. `tb_aggro` already does a version of this with 4-round danger memory |
| **Voronoi claim partition** (Pantheon #3): simultaneous flood fills, each unit takes the targets it reaches first | Divide camp groups without spending shared bytes: compare my distance field value with each ally's (positions from `cambc.champions()` when visible, or their claim byte). This frees shared bytes for a focus target and alerts |
| **Memoryless, ceiling-ordered job scoring** (Pantheon #3, the winner) | Each turn, score fight > bank > capture > farm > roam in descending order of each job's maximum possible score, and stop when no remaining job can beat the best so far. Keep only TTL caches of failed targets. This saves fuel and removes stale-state bugs |
| **Retarget with hysteresis plus a visited set** (Make Fire #4: a big gain on maze maps) and **give up on unfinishable targets** (30-round timeout plus blacklist) | Switch camp target only if the new score exceeds 1.25× the current one. Blacklist a camp or altar for 30 to 40 rounds after 6 turns with no progress, or after the expected kill time runs 2× over |
| **Roles beat identical generalists** (Make Fire #4) | Give each champion a fixed role from the draft: carry (Vesper or Marcella gets the captures), anchor/tank (Ryth or HoR, the "nearest champion" to camps), skirmisher (Vendetta). Store roles in draft memory |
| **Fixed bit-budget comms** (Gone Fishin' #14, Don't @ Me #15, GST #7) | 8 bytes = 64 bits. A suggested layout (source #1 uses a similar one): bytes 0 to k−1 hold one claim/status byte per body (6-bit group id, carrying flag, in-danger flag). k can be 6 with Cassi&Issac in a 5-pick, so map slot = rank of the ally handle. Byte 6 holds the focus enemy index (3 bits) plus a 5-bit round stamp. Byte 7 holds flags (2-3 bit alert generation, gate assault). With k ≤ 5, byte 5 is free for a coarse enemy sighting (x/8, y/8 on a ≤100 map gives 4+4 bits). Symmetry and everything static go in draft memory |
| **Symmetry from turn 1** (#4, #9, #10, #11, #14) | `game_map.symmetry()` gives it directly. Precompute the enemy spawn, mirrored camps and altars nearer the enemy in the draft, and weight the enemy half ×0.4 early |
| **Minimise idle time** (confused #10, Kragle #12) | Add an idle timer: if no move, attack, cast or shop for N turns, force a new job. Give each champion a "return location" so it goes back to its farm after recall or shopping |
| **Test counter-meta features against real opponents** (JWU #9: neutral in self-play, won the final) | Judge altar locks, wards and carrier focus against the strongest *different* bots we have, not against ourselves |
| **Hidden-assumption bugs** (GST 1x1 pathing, Make Fire's never-initialised core at (-1,-1)) | Assert or log sentinel defaults: an unset altar, spawn, focus target or "no group" id = 0 or 255. Our equivalent risks are assuming the altar is always reachable, assuming a single altar, or assuming a 4-5 champion team when the draft can give 3 |

---

## 4. Ranked changes for the next ~3 hours (Python bot)

**How to verify every item** (from `ians linux bot/`):
```
cp -r bots/<lead> bots/<lead>_base                    # frozen baseline, once
python3 tools/eval.py <lead> <lead>_base --maps sprint --jobs 8 --tag ab-<change>
python3 postmortems/match_metrics.py matches/ab-<change>   # tribute size, gem loss by cause, camp deaths, fuel exhaustion
```
- The sprint set is 20 maps × 2 sides = 40 games, so one game is 2.5%. Treat a difference of 2 to 3 wins as noise.
- Accept a change when the **targeted metric moves the right way**, W-L is ≥ baseline, and **botFaults(A) = 0**.
- Then confirm against a *different* opponent (another `tb_*` bot or `starter-python`), because self-play misleads.
- Before shipping, run `--maps all` (70 maps, 140 games).

| Rank | Change | Expected impact | Difficulty | Verify (beyond W-L) |
|---|---|---|---|---|
| 1 | **Kill fuel exhaustion.** Add `cambc.fuel_remaining()` guards in camp/job scoring and pathing loops: stop scoring when fuel is under about 400k, act on the best so far, and always `end_turn()`. Cache static DistanceFields (altars, spawn, each camp group) on the first play turn or across turns; never rebuild them every turn. Move component and region analysis to the draft or the first turn | **High.** We measured 41 to 1,057 suspensions per game, up to about 43% of a champion's turns on 01islands. Every one makes a turn late | Easy-med | `fuelExhausted/game` ≈ 0 on `--maps sprint`, plus `--maps 01islands,01big-world,02treasure-box,01starvation` |
| 2 | **Banking policy from §2.3.** Bank at 30 or more anywhere, 15 or more within 15 path tiles of an altar, 5 or more within 4. Halve the thresholds when threatened (enemy seen within 14 in the last 40 rounds, ally died in the last 100, or HP < 60%). Always bank when banked + carried ≥ 1000 or round ≥ 1900. Pick the nearest altar by path, +12 if enemies were seen near it | **High.** It is the one habit all 20 top teams share, and our tributes are 2 to 3× too small | Easy (constants plus a threat flag) | Mean tribute rises to 30 or more, gems lost per game doesn't rise, average gems submitted rises |
| 3 | **Stop dying to camps** (mainly `tb_economy`). Before waking a group, require expected damage taken (Σ camp Str × clear time, shared across the champions in range) < HP − 150. Mid-fight, retreat when HP < 2.5 × incoming + 10% unless the camp dies first. Step out of range **before** recalling. Never be the nearest champion to an awake golem or monolith unless you are the tank | **High** for `tb_economy` (11 camp deaths and 41 gems lost to camps per game); Low-med for the others | Med | `deaths_by_camp/game` < 2 and `gemsLost_to_camp` near 0 |
| 4 | **Draft the meta core:** Vesper, Marcella, HoR, Vendetta, then Ryth (or Tavi). First check each kit is handled: HoR's ground-target landing dash and its shield; Marcella's enhanced reset only after the attack is used, and her excl 2×F spell; Ryth's ground area stun | **Med-high, uncertain.** It is universal in the top 20, but our micro may favour other kits | Easy (the order list); med if kit handling is missing | Run A/B with only the draft list changed. Check `damage done`/`deaths` per champion in the JSON `champions[].metrics` |
| 5 | **Bruiser builds.** Each champion buys `BRUISER_SHARD_OF_<main>`: Vesper and Vendetta Strength, HoR and Ryth Health, Marcella alternating Focus/Health/Strength, with a Health shard bought on spawn to heal. Drop Jungle, Monster, Treasure and Prospector openers. Shop whenever on spawn or dead | **Med.** 18 of 20 habitual and 58% win; the most stat per gold | Easy | Item events in the JSON (`itemsBought`); camp deaths mustn't rise after losing the Jungle −30% |
| 6 | **Ward on every recharge.** If `ward_cooldown() == 0` (`ward_placement_tiles()` is the 5×5 area), place it: next to the altar while tributing or walking to it; otherwise, if the last ward is more than 8 tiles behind, on the reachable tile within 2 nearest the enemy spawn. Wrap in try/except, since it returns False on a hidden blocker | **Med, uncertain.** 20 of 20 do it, but source #1's version lost. It only pays if the enemy sightings feed threat, banking and fight logic | Easy | `wardPlacement` about 17 or more per champion per game, gems lost to champions per game not up |
| 7 | **Altar locks.** Keep one lock (10g, bought on spawn). If a visible enemy `is_submitting_gems()` within 1 of an altar that is within 2 of me, `consumables()[ConsumableType.ALTAR_LOCK].use(altar)`: this cancels the channel and blocks it. Defensively, don't route a carrier to an altar where `vision.has_altar_lock(altar)` (enemy); use another altar or attack the lock (5 hits) when no enemy is near | **Med.** 12 of 20 habitual; a pure denial play | Easy-med | `consumablesBought` > 0, and lower enemy gems on maps where we meet them at altars (02crossing, 00corners). Check with `--keep` replays |
| 8 | **Carrier and channel focus.** Target priority: enemies channelling (tribute, recall, TP), then carriers (×gems), then fastest kill. Stun channels first. Write the focus enemy index into one shared byte with a round stamp, and have allies within 8 join | **Med-high** in contested games. The killer gets the carried gems plus 100 gold | Med | `kills` and `gemsLost_to_champion` for the enemy (run metrics with the bots swapped); our gem loss per game not up |
| 9 | **Fight/flee model:** kill-time ratio > 1.3 means don't engage; > 1.6 or outnumbered within 6 means retreat unless the target dies this turn. Never turn your back on an adjacent melee champion you can hit. Lower the thresholds to 1.0 when carrying 30 or more gems | **Med** | Med | Champion deaths per game down without kills falling |
| 10 | **Single capture recipient.** Elect deterministically (nearest, then least gold spent, then slot); others step off the spawn tiles and take the next job. Cache the choice until the capture completes | **Med** for deathball-style bots (everyone stands on the tiles today); Low for split farmers | Med | Captures per game and gems per game up; farm spread up |
| 11 | **Map-archetype profile in the draft (§2.6),** written to draft memory: jackpot (≥ 60 gems and ≥ 35% of the map's in one harmless group), monolith-gated altars, disconnected regions → crystals. Use only map *contents*, never names (Sprint 3 maps are unseen) | **Med-high** on those maps, zero elsewhere | Med-hard | `--maps 00the-line,00vault,01boss-battle,02guardians,01islands,01big-world` both sides, then a full `--maps all` to catch regressions |
| 12 | **Hysteresis, stuck guards and an idle timer:** switch job only for > 1.25× score; after 6 turns with no action, blacklist that camp for 30 or that altar for 40; recompute jobs every ~5 rounds, not every turn (also saves fuel) | **Low-med** (mostly removes pathological loops) | Easy | Fewer turns with no action (add a debug counter), no W-L drop |
| 13 | **Gold weight decay plus side and danger multipliers in job scoring (§2.7):** w = 0.15 / 0.08 / 0.03 by round; ×0.4 on the enemy half early; ×0.6 near recent enemy sightings; ×0.5 near recent deaths | **Low-med** | Easy | Average gems up, deaths down |

**If there is only time for four:** do 1, 2, 3 and 5, then 4 once kit handling is checked. They are low-risk, measurable with the harness plus `match_metrics.py`, and backed by the only same-game data we have.
Hold 11 and anything that rewrites movement until the end, and only ship them if they pass `--maps all`.

---

## 5. Dev-process lessons we can still apply today

1. **Freeze a baseline now and change one subsystem at a time.**
   - Source #2 and source #1 both found that wholesale farming rewrites and over-cautious "safety" versions lowered income.
   - Make Fire's untested Sprint 5 rewrite went 1-4. GST shipped the slow but robust BFS rather than an unproven rewrite.
   - Keep the `bots/<lead>_base` copy and a `_vN` copy per accepted change for rollback.
2. **A/B on every map from both sides, then read the flips.**
   - The 2025 champion kept 57 versions in 25 days, more than 2 A/B-tested iterations a day.
   - Use `tools/eval.py --maps sprint` for iteration and `--maps all` (70 maps) as the gate. Re-run only the maps that flipped with `--keep`, and watch those replays.
3. **Measure more than win rate.** Run `postmortems/match_metrics.py` on every eval folder. It reports gems lost by cause, mean tribute, deaths by cause, fuel exhaustion, wards and consumables.
   Top teams are separated by gem loss and camp deaths, not just W-L. A fix can be right even when 40 games can't show a W-L change.
4. **Sprint 3 maps are unseen: generalise.**
   - Never branch on map names. Classify by contents: gem concentration, gated altars, components, size.
   - Test the extremes we have: 30×30 versus 100×100 (source #2 lists both as weak spots), many holes, bush-heavy maps, monolith-only gem maps, and maps where an altar is unreachable on foot.
   - Expect the meta and the tie-break to matter: lifetime gold is tiebreak #2, so late-game gold farming isn't wasted.
5. **No-crash rules.** Each one decides games silently.
   - Wrap every turn in try/except and **always** `cambc.end_turn()`.
   - Don't call the engine at import time.
   - Check preconditions before actions that return None and raise (`attack`, `buy`, `submit_gems`, `recall`).
   - Treat `False` from move, dash, ward or consumable use as "hidden blocker: try another tile".
   - Guard `vision.*_at()` with `has_*`.
   - In the draft, fall back to the next pick if `pick` raises, because random picks are the alternative.
   - Version-tag draft memory, since it is zero-padded.
   - Require `botFaults(A) 0` in the eval summary.
6. **Self-play and local panels mislead.**
   - Source #1's 52% local screen didn't hold online. JWU's winning finals feature was neutral in self-play.
   - Test each change against at least two different opponents (other `tb_*` bots, starter-python).
   - If ladder scrims are available before the lock, scrim teams currently in the top 20 and note per-map results.
7. **Copy macro, not micro.** GST copied the macro of teams above them, because it is the easy part to reverse-engineer.
   We have that macro data already in §2: draft, items, tribute size, wards, locks and capture recipients. That is cheaper than inventing new strategy.
8. **Prioritise behaviours that fire every game.** GST's Baby Rat Taxi rarely fired, so it had low return.
   Banking, fuel, camp safety and shopping fire every game. Map-archetype profiles fire on perhaps 10 to 20% of maps.
9. **Stop features well before the lock.** Pantheon merged late and it worked, but they call it a risk. Make Fire and GST both regretted their late rewrites.
   About 45 minutes before the lock, freeze, run `--maps all` against the baseline and two other bots, and submit the best *measured* version.
10. **Profile before optimising** (Make Fire lost a sprint blaming imports).
    Find which function burns fuel by logging `cambc.fuel_remaining()` deltas around the scoring, pathing and vision phases on one bad map, such as 01islands. Then fix the top item.
