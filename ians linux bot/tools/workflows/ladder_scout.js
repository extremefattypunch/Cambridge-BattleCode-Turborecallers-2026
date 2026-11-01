export const meta = {
  name: 'ladder-scout',
  description: 'Analyse new real ladder matches (one note per match folder in results/real-matches/) and fold them into INSIGHTS.md',
  whenToUse: 'Every loop tick, with args = the output of `python3.12 tools/unscouted.py --claim`: [{group, time, v, opp, rec, folder}]',
  phases: [
    { title: 'Scout', detail: 'one deep analysis note per 5-game match set' },
    { title: 'Insights', detail: 'update results/real-matches/INSIGHTS.md, WEAKNESSES.md and INDEX.md' },
  ],
}

// Invoked by the loop agent: Workflow({scriptPath: '<repo>/ians linux bot/tools/workflows/ladder_scout.js', args: [...]})
const REPO = '/n/home05/ianpoon/Cambridge-BattleCode-Turborecallers-2026/ians linux bot'
const SITE = 'https://2026a.battlecode.co.uk/game/match-groups/'
const COMMON = `
Project: our Cambridge Battlecode 2026a ("cambc") team "Turbo Recallers", repo at REPO="${REPO}" (quote it: spaces). Rules and champion/item facts: the skills in "${REPO}/.claude/skills/" (cambc-game-rules, cambc-bot-api-python). Our live and past bots: results/ladder-versions.json maps website versions to activation times; v2 = bots/tb_merge_b, v3 = bots/q24_combo, v4 = bots/c2_respawn, later versions per results/READY.md and HANDOFF.md §3. Their logic is in src/bot.py and NOTES.md.
Real ladder data: results/ladder-games.jsonl (one row per game: id, group, time, v, opp, opp_rating, map, side (ours), res, us, them, rounds, end, udraft, odraft). Full engine statistics per game: matches/ladder/summary/<matchId>__<OUR side A|B>.json (events with positions: death/kill/assist, campClear, gemCollection, gemSubmission, gemLoss, buyItem/buyConsumable/itemCombination, wardPlacement, fuelExhausted; championTimelines; teamTimelines; heatmaps). Tools: python3.12 tools/scout.py (profiles both teams: build order, economy, farming and tempo by phase, tributes, fights, map control; --group <id> for a whole set; --json), python3.12 -I tools/analyze_match.py <file> (narrative, us = our team). Our bot's stdout and per-turn fuel trace: cambc matches download <matchId> -o matches/ladder/replays/<id>.repl26a (zip). Missing summary: cambc matches summary <matchId> --json -o matches/ladder/summary/<matchId>__<OUR SIDE>.json (retry on HTTP 429). Map files: maps/<name with hyphens>.map26a.
All relative paths here are relative to REPO; always use absolute paths ("${REPO}/results/...").
Rules: python3.12 for tools; analysis only, no game simulations (if one is truly needed it must go through tools/onslurm.sh on the free test partition; never run games locally). Don't edit bots; don't change git state; don't edit results/STATUS.md, STRATEGIES.md, READY.md, CHAMPION, HANDOFF.md; never submit, log in, activate submissions or create match groups. Be concrete: cite map, side, round numbers, champions, positions, gold/gem numbers; separate evidence from speculation; read our bot code before explaining why we behaved as we did.
`
const WEAK = { type: 'array', items: { type: 'object', properties: { weakness: { type: 'string' }, evidence: { type: 'string' }, games: { type: 'integer' }, impact: { type: 'string', enum: ['decisive', 'major', 'minor'] } }, required: ['weakness', 'evidence', 'games', 'impact'] } }
const SET_SCHEMA = { type: 'object', properties: {
  group: { type: 'string' }, opponent: { type: 'string' }, record: { type: 'string' }, note_path: { type: 'string' },
  opponent_strategy: { type: 'string' }, decisive: { type: 'string', description: 'per game, the decisive moments' }, comparison: { type: 'string', description: 'which strategy was superior and why' },
  our_weaknesses: WEAK, our_strengths: { type: 'array', items: { type: 'string' } }, hypotheses: { type: 'array', items: { type: 'string' } },
}, required: ['group', 'opponent', 'record', 'note_path', 'opponent_strategy', 'decisive', 'comparison', 'our_weaknesses', 'hypotheses'] }

const sets = args || []
if (!sets.length) return { scouted: [], insights: null }

phase('Scout')
const notes = await parallel(sets.map(s => () => agent(`${COMMON}
TASK: carefully analyse the real ladder match ${s.group} (${s.time} UTC, our website v${s.v}, vs "${s.opp}", ${s.rec}; site page ${SITE}${s.group}). Its 5 games are the rows of results/ladder-games.jsonl whose group starts with "${s.group}".
Write ONE note: ${REPO}/results/real-matches/${s.folder}/notes.md (the folder name comes from tools/unscouted.py; use it verbatim and do not rename it; a .claim file may already be there).
Follow results/real-matches/TEMPLATE.md exactly, in this order (the user's required format):
1. **The games played:** a brief description of exactly what happened in each game against this team, plus the table of results.
2. **Their strategy compared with ours:** the comparison table, covering draft and roles, build, farming, tributes, fighting, map control and adaptation.
3. **Which strategy was superior, and what we learn:** first one overall sentence (whose strategy was superior over the 5 games, and whether the result came from strategy or from execution and bugs). Then, per game, which approach was superior and why, with numbers. Then the lessons, and what we did better.
4. **Weaknesses exposed and hypotheses:** each with evidence, impact, the responsible code in the bot that PLAYED this match (v${s.v}; results/ladder-versions.json and HANDOFF.md §3 map versions to bots/<bot>), and a structure-keyed hypothesis.
Return the structured summary.`, { label: `scout:${s.opp}`.slice(0, 40), phase: 'Scout', schema: SET_SCHEMA })))

phase('Insights')
const done = notes.filter(Boolean)
const insights = await agent(`${COMMON}
TASK: fold ${done.length} new match-set notes into the living insights documents. New notes (structured): ${JSON.stringify(done)}
Start from the current ${REPO}/results/real-matches/INSIGHTS.md and WEAKNESSES.md, which already summarise every earlier note, plus these new notes. Open an earlier note only to check a specific claim; never re-read them all. Cross-match studies are in results/real-matches/studies/.
1. Update results/real-matches/WEAKNESSES.md, the ranked weakness ledger, with at most 25 open rows. Per weakness give:
   - the number of matches and games it decided, and links to at most 3 representative notes (INDEX.md is the full list);
   - the evidence and the code location;
   - its status: queued, in a simulated match, or tested (check results/STRATEGIES.md and results/simulated-matches/INDEX.md).

   Re-rank by total impact. Collapse fixed weaknesses to one line each under "Fixed".
2. Rewrite results/real-matches/INSIGHTS.md for the user to read, laid out like postmortems/INSIGHTS.md. Hard limits: at most 150 lines, at most 8 bullets per section, at most 3 note links per bullet; rewrite rather than append, because detail lives in the per-match notes. Put the update's date and time at the top, then an honesty-up-front paragraph on sample size, our versions and the rating band. Then:
   - §1 What real opponents do better than us, ranked, with counts.
   - §2 Opponent archetypes at our rating: how each beats us, how often we meet it, the counter.
   - §3 Where we are genuinely better (keep it).
   - §4 Per-version ladder record and trends, from results/ladder-games.jsonl.
   - §5 Ranked changes and hypotheses, each with its status and a validation plan that does not rely only on self-play.
   - §6 Process lessons.
3. Run python3.12 tools/organize_notes.py. It moves any notes left in old places and rebuilds results/real-matches/INDEX.md, which lists every match note with its site link.
Return the top weaknesses and the new or changed hypotheses.`, { label: 'insights', phase: 'Insights', schema: { type: 'object', properties: { insights_path: { type: 'string' }, ledger_path: { type: 'string' }, top_weaknesses: { type: 'array', items: { type: 'string' } }, new_hypotheses: { type: 'array', items: { type: 'object', properties: { title: { type: 'string' }, rationale: { type: 'string' }, validation: { type: 'string' } }, required: ['title', 'rationale'] } } }, required: ['insights_path', 'top_weaknesses', 'new_hypotheses'] } })
return { scouted: done.map(n => n.group), notes: done, insights }
