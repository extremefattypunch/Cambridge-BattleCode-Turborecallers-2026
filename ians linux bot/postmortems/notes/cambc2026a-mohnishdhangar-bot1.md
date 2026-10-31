# MohnishDhangar/Cambc: Bot1 v4 (cambc2026a C++ bot), strategy notes

- **URL:** https://github.com/MohnishDhangar/Cambc (strategy at `bots/Bot1/STRATEGY.md`)
- **Raw copy:** `../raw/cambc2026a-mohnishdhangar-bot1-STRATEGY.md`
- **Event:** **Cambridge Battlecode 2026a**, the same game as ours. It was written against SDK 2.2.5 and engine 0.0.3. The README says it was updated to CAMBC/SDK 3.0.1 on 20 Oct 2026.
- **Team / placement:** Unknown and probably not top-tier. Its evaluation is only against its own frozen versions and the starter bot (it beat the starter 34/34). It was designed from paired platform games against an opponent called "lll". **Treat it as a source of ideas, not as proven meta.**
- **Same game as cambc 2026a?** **Yes.** Some constants may differ from the current engine (see caveats).

## Game summary
Same game as ours: drafted champions farm camps and clusters, capture them for gems and gold, and tribute at altars.

## Strategy
- **Draft by map type, classified from camp contents, not map hashes.**
  - Ordinary maps: Tavi, Varg, Vendetta, Ryth, Vesper. Varg is picked first when groups of 3 or more camps are common, because his splash hits the whole group.
  - **Monolith maps**, where every gem-bearing group has at least 10,000 initial HP: Stellar, Prism, Tavi, Ren, Varg (casters).
  - Large non-monolith objective (for example, a six-elk plus six-gem-cluster group): Varg, Ren, Stellar, Tavi, Ryth.
  - The 2026a draft sees the whole map, so classifying it in the draft and storing the profile in draft memory is natural.
- **Siege policy for very high-HP objectives.** Casters farm gold first. They become eligible to siege at 180 or more Focus, or from round 400 if their HP is at least 45%. They hold firing positions **outside every remaining live monster's attack range but within spell range of a target**, cast on cooldown, and stand next to the group as outer monsters die. Damage persists while a monster sleeps, which they verified from replays. Clearing and capturing are treated as separate jobs.

## Macro / economy
- **One elected recipient per capture.** Choose by distance, occupancy, equipment investment (the least-invested champion gets preference, so upgrades spread) and slot order. Cache that choice until the capture finishes. Helpers step off the reward tiles and go find other work. Re-elect if the recipient dies, recalls, picks up gems or abandons the claim. This matches the top-20 pattern of single-recipient captures (see the Faisal-Saqib notes).
- Claims are planning hints, not proof that an ally is actually helping.
- Only awake, living monsters count as camp danger. A sleeping, damaged camp is not a threat.

## Items
- Basic-attack farmers: Monster Strength, then Jungle Strength, then Health bought on spawn, then more Strength.
- Objective casters: Power Focus twice, then Durability Health.
- Caveat: the top-20 census suggests Bruiser builds win more, and that Monster and Jungle builds have low win rates.

## Compute / fuel
- A smaller navigation and decision loop, with **two shared-purpose static distance fields** instead of one field per altar, to keep fuel down. 102 release-mode games ran with zero fuel exhaustion.
- They keep fuel reserves for actions.

## Testing & dev workflow
- A deterministic local regression suite: **all 17 maps x both sides x several frozen baselines** (v1, v3, starter), run by `evaluate_v4.py` with `--jobs 2`. It records source hashes, replay inputs, statistics, stdout and diagnostics into a new output directory per run, and never overwrites old versioned zips.
- A paired platform analysis: download online replays against one opponent and compare versions map by map, with an offline HTML explorer for the opponent analysis.
- Each release is kept as a zip plus wasm, so rollback is easy.

## Mistakes / regrets
- **v2 caused runtime and strategy regressions.**
- **v3 reduced deaths but lost income**, and it underperformed against lll on the platform. Being too cautious, with over-careful travel and repeated rallies, cost more gems than it saved.
- Replacing the whole farming policy at once reduced income, so v4 kept v1's farming core and changed only capture allocation and objective handling. The lesson is to change one subsystem at a time.
- Known weaknesses: the compact 30x30 map, contested routes on 100x100, side-dependent losses, disagreement over capture recipients under partial vision, and optimistic estimates of help from claimed camps.

## Caveats against our rules sheet
- The doc claims spell ranges are *Euclidean* 4 and monster ranges Chebyshev 3. Our rules sheet says all ranges are Chebyshev, and gives camp ranges of wolf 3, elk 4, golem 4 and monolith 5. Under the current engine, an "outside monster range, inside spell range 4" siege position is impossible against a monolith (range 5) and against elk or golem (range 4); it only works against wolves. Re-verify with the engine before copying the idea.
