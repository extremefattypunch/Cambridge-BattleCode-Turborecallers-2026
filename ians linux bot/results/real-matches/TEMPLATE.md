# Real-match note template

One folder per ladder match: the 5 games we played against one team in one match group. The folder is named `<YYYY-MM-DD>_<HHMM UTC of the first game>_<opponent-slug>_<group8>/`, where group8 is the first 8 characters of the match-group id. Use the exact name `tools/unscouted.py` prints. It holds a single `notes.md` laid out as follows. Copy everything below the line.

---

# vs <Opponent> (<their rating>): <W>-<L>, <date> <HH:MM> UTC, our v<N> (`<bot>`)

**Site:** https://2026a.battlecode.co.uk/game/match-groups/<group id>
**Data:** `matches/ladder/summary/<matchId>__<our side>.json` for each game; `python3.12 tools/scout.py --group <group id>`

## 1. The games played
A brief description of exactly what happened in each game of this match against this team.

| # | Map | Our side | Result | Gems (us-them) | Rounds | End | Our draft | Their draft |
|---|---|---|---|---|---|---|---|---|
| 1 | | | | | | | | |

- **Game 1 (<map>):** two or three sentences. How it unfolded, plus the decisive moment: round, place, which champions.
- ...

## 2. Their strategy compared with ours
| Aspect | Opponent | Us |
|---|---|---|
| Draft and each champion's role | | |
| Item build and timing | | |
| Farming: which camps, in which order, how many together, tempo | | |
| Tributes: size, cadence, first tribute | | |
| Fighting: when, whom, where (carrier hunting, ganks, spawn camping, altar contests) | | |
| Map control: wards, altar locks, crystals | | |
| Adaptation across the 5 maps | | |

## 3. Which strategy was superior, and what we learn
- **Overall (<W>-<L>):** in one sentence, whose strategy was superior over the 5 games, and whether the result came from strategy or from execution and bugs.
- **Per game:** whose approach won, why, and by how much. Give numbers: gold, clears, kills, gem race at r250/r500/r1000.
- **Lessons:** what this match teaches about our bot.
- **Where our approach was better:** what to keep.

## 4. Weaknesses exposed and hypotheses for the testing pipeline
| Weakness | Evidence (game, round, numbers) | Impact (decisive / major / minor) | Code responsible (in the bot that played, `bots/<bot>/src/bot.py`) | Testable hypothesis (keyed on structure, never on map or team names) |
|---|---|---|---|---|
