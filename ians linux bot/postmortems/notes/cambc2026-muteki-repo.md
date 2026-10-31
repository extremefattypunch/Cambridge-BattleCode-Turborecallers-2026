# lxorb/muteki: Team Muteki, Cambridge Battlecode 2026 finalist bot

- **URL:** https://github.com/lxorb/muteki (main bot: `/bots/uewomirudake`)
- **Raw copy:** `../raw/cambc2026-muteki-README.md`
- **Event:** Cambridge Battlecode 2026 (spring 2026, the conveyor/builder game, Python)
- **Team / placement:** Team Muteki, an **international finalist, 5th/6th at the Grand Finals**. The team was flown to Cambridge for the in-person finals; a LinkedIn post by member Emil Alexander Vinu turned up in the search results.
- **Same game as cambc 2026a?** **No.** The README is short and has no written postmortem. Most of what transfers is about workflow.

## Game summary
This was the builder/core/conveyor/turret game (see the Pantheon notes).

## Lessons (from the README and commit history)
- **Dev workflow with AI assistance.** Their naming convention marks who wrote each method: `u_` for human-written, `c_` for AI-written, `s_` for strategy sub-methods. This made AI-generated code easy to find and review. One commit is titled "Let Claude cook". For our multi-agent setup, tagging AI-written code paths makes regressions easier to bisect.
- **Auto-formatting on save** (black) and a git submodule for shared code kept merges clean across three people.
- **Local scrimmage:** `cambc run <bot1> <bot2> [--watch] [--map-random]` for quick head-to-heads on random maps.
- **Bugs they fought, going by the commit messages:** units self-destructing their own infrastructure too eagerly ("dont blindly destroy harvesters", "lets not destroy turrets to build turrets", "only self destruct when closing gap possible"), and a core defender that was too passive. The general lesson for 2026a: aggressive "sacrifice" heuristics need hard guards. Examples are suicidal dives into camps (which destroy carried gems), or cancelling tributes too eagerly.
- They tuned toward aggression ("aggressively kill enemies") late in the event.

## Limitations
There is no written strategy document, so detailed lessons would require reading the code. Given the different game and our time limit, we didn't do that.
