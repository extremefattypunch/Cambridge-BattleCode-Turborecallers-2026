export const meta = {
  name: 'ladder-scout',
  description: 'Scout new real ladder match sets (one analyst per set) and fold them into results/ladder/INSIGHTS.md',
  whenToUse: 'Every loop tick, with args = the new, unscouted match sets: [{group, time, v, opp, rec}]',
  phases: [
    { title: 'Scout', detail: 'one deep analysis note per 5-game match set' },
    { title: 'Insights', detail: 'update results/ladder/INSIGHTS.md and WEAKNESSES.md' },
  ],
}

// Invoked by the loop agent: Workflow({scriptPath: '<repo>/ians linux bot/tools/workflows/ladder_scout.js', args: [...]})
const REPO = '/n/home05/ianpoon/Cambridge-BattleCode-Turborecallers-2026/ians linux bot'
const SITE = 'https://2026a.battlecode.co.uk/game/match-groups/'
const COMMON = `
Project: our Cambridge Battlecode 2026a ("cambc") team "Turbo Recallers", repo at REPO="${REPO}" (quote it: spaces). Rules and champion/item facts: the skills in "${REPO}/.claude/skills/" (cambc-game-rules, cambc-bot-api-python). Our live and past bots: results/ladder-versions.json maps website versions to activation times; v2 = bots/tb_merge_b, v3 = bots/q24_combo, v4 = bots/c2_respawn, later versions per results/READY.md and HANDOFF.md §3. Their logic is in src/bot.py and NOTES.md.
Real ladder data: results/ladder-games.jsonl (one row per game: id, group, time, v, opp, opp_rating, map, side (ours), res, us, them, rounds, end, udraft, odraft). Full engine statistics per game: matches/ladder/summary/<matchId>__<OUR side A|B>.json (events with positions: death/kill/assist, campClear, gemCollection, gemSubmission, gemLoss, buyItem/buyConsumable/itemCombination, wardPlacement, fuelExhausted; championTimelines; teamTimelines; heatmaps). Tools: python3.12 tools/scout.py (profiles both teams: build order, economy, farming and tempo by phase, tributes, fights, map control; --group <id> for a whole set; --json), python3.12 -I tools/analyze_match.py <file> (narrative, us = our team). Our bot's stdout and per-turn fuel trace: cambc matches download <matchId> -o matches/ladder/replays/<id>.repl26a (zip). Missing summary: cambc matches summary <matchId> --json -o matches/ladder/summary/<matchId>__<OUR SIDE>.json (retry on HTTP 429). Map files: maps/<name with hyphens>.map26a.
Rules: python3.12 for tools; analysis only, no game simulations (if one is truly needed it must go through tools/onslurm.sh on the free test partition; never run games locally). Don't edit bots; don't change git state; don't edit results/STATUS.md, STRATEGIES.md, READY.md, CHAMPION, HANDOFF.md; never submit, log in, activate submissions or create match groups. Be concrete: cite map, side, round numbers, champions, positions, gold/gem numbers; separate evidence from speculation; read our bot code before explaining why we behaved as we did.
`
const WEAK = { type: 'array', items: { type: 'object', properties: { weakness: { type: 'string' }, evidence: { type: 'string' }, games: { type: 'integer' }, impact: { type: 'string', enum: ['decisive', 'major', 'minor'] } }, required: ['weakness', 'evidence', 'games', 'impact'] } }
const SET_SCHEMA = { type: 'object', properties: {
  group: { type: 'string' }, opponent: { type: 'string' }, record: { type: 'string' }, note_path: { type: 'string' },
  opponent_strategy: { type: 'string' }, decisive: { type: 'string' }, comparison: { type: 'string' },
  our_weaknesses: WEAK, our_strengths: { type: 'array', items: { type: 'string' } }, hypotheses: { type: 'array', items: { type: 'string' } },
}, required: ['group', 'opponent', 'record', 'note_path', 'opponent_strategy', 'decisive', 'comparison', 'our_weaknesses', 'hypotheses'] }

const sets = args || []
if (!sets.length) return { scouted: [], insights: null }

phase('Scout')
const notes = await parallel(sets.map(s => () => agent(`${COMMON}
TASK: carefully analyse the real ladder match set ${s.group} (${s.time} UTC, our website v${s.v}, vs "${s.opp}", ${s.rec}; site page ${SITE}${s.group}). The 5 games are the rows of results/ladder-games.jsonl with group starting "${s.group}".
Write results/ladder/scouting/2026-11-01-${s.group.slice(0, 8)}-<opponent-slug>.md (use the game date from the rows), in the style of postmortems/notes/, with a header (opponent, their rating, our version, record, maps, link ${SITE}<full group id>) and:
1. Opponent profile: draft and each champion's role; item build order and timing; farming pattern (which camps, in which order, how many champions together, tempo vs ours); tribute behaviour; fight behaviour (when they fight, who they target, whether they hunt our carriers, spawn-camp, gank isolated champions, contest altars, use locks/wards); how they adapted across the 5 maps.
2. Per game: result, gem race at r250/r500/r1000, the decisive moments with round numbers and positions, and the root reason we won or lost.
3. Their strategy vs ours: where theirs was superior (by how much: gold, clears, kills, tempo), where ours was superior, and which rule or threshold in our code causes each gap (function names in the live bot's src/bot.py).
4. Our weaknesses exposed (evidence, impact) and testable, structure-keyed hypotheses (no map or team names in a fix).
Return the structured summary.`, { label: `scout:${s.opp}`.slice(0, 40), phase: 'Scout', schema: SET_SCHEMA })))

phase('Insights')
const done = notes.filter(Boolean)
const insights = await agent(`${COMMON}
TASK: fold ${done.length} new match-set notes into the living insights documents. New notes (structured): ${JSON.stringify(done)}
Full notes: results/ladder/scouting/ (read the earlier ones too).
1. Update results/ladder/WEAKNESSES.md, the ranked weakness ledger: per weakness, the sets and games it decided, evidence links, the code location, and status (queued / in experiment / tested; check results/STRATEGIES.md and results/experiments/). Re-rank by total impact.
2. Create or update results/ladder/INSIGHTS.md for the user to read, laid out like postmortems/INSIGHTS.md:
   - title and an "honesty up front" paragraph: sample size, our versions, rating band, what is evidence and what is speculation;
   - §1 match-set index: a table with time UTC, our version, opponent (rating), record, maps, site link (${SITE}<group id>) and note link; newest first; include every scouted set;
   - §2 what real opponents do better than us, ranked, with counts and evidence;
   - §3 opponent archetypes at our rating, how each beats us, how often we meet it, the counter;
   - §4 where we are genuinely better (keep it);
   - §5 per-version ladder record and trends (from results/ladder-games.jsonl);
   - §6 ranked changes / hypotheses, each with status and a validation plan that does not rely only on self-play;
   - §7 process lessons.
   Keep it current: rewrite sections rather than appending stale text, and put the date and time of the update at the top.
Return the top weaknesses and the new or changed hypotheses.`, { label: 'insights', phase: 'Insights', schema: { type: 'object', properties: { insights_path: { type: 'string' }, ledger_path: { type: 'string' }, top_weaknesses: { type: 'array', items: { type: 'string' } }, new_hypotheses: { type: 'array', items: { type: 'object', properties: { title: { type: 'string' }, rationale: { type: 'string' }, validation: { type: 'string' } }, required: ['title', 'rationale'] } } }, required: ['insights_path', 'top_weaknesses', 'new_hypotheses'] } })
return { scouted: done.map(n => n.group), notes: done, insights }
