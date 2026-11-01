#!/bin/bash -l
#SBATCH -J cambc-agent
#SBATCH -p test
#SBATCH -c 4
#SBATCH --mem=16G
#SBATCH -t 12:00:00
#SBATCH -o /n/netscratch/hekstra_lab/Lab/ian_poon/battlecode/logs/%x-%j.out
#SBATCH --signal=B:USR1@2400
# Keeps the Claude Code loop alive past the 12 h cap of a free `test` job (or of an OOD desktop).
# It runs the agent session in tmux on this node. 40 min before the time limit it submits its own
# successor, which waits for this job to end and then resumes the same session with a hand-off note.
#   start:  sbatch [--begin=HH:MM] tools/agent_relay.sbatch [JOBID_TO_WAIT_FOR]
#   attach: tools/agent_attach.sh   (srun --overlap into the job, then tmux attach -t cambc-agent)
#           (detach again with Ctrl-b d; quitting claude only makes the relay restart it)
#   stop:   scancel -n cambc-agent
# Env overrides: CLAUDE_SESSION (session id to resume), AGENT_CMD (replaces the claude command, for
# dry runs), RELAY_SBATCH_ARGS (extra sbatch args for the successor), RELAY_GENERATIONS (stop after N).

SESSION=${CLAUDE_SESSION:-5245ba49-8b5b-4d9a-9345-708126bcbea8}
WORKDIR=/n/home05/ianpoon/Cambridge-BattleCode-Turborecallers-2026
SELF="$WORKDIR/ians linux bot/tools/agent_relay.sbatch"
AGENT_CMD=${AGENT_CMD:-claude --resume $SESSION --permission-mode auto}
GEN=${RELAY_GEN:-1}
PREV=${1:-}
NAME=cambc-agent

log() { echo "[$(date '+%F %T')] $*"; }
# sleep N seconds even when the USR1 trap interrupts `wait`
nap() { local end=$((SECONDS + $1)); while [ $SECONDS -lt $end ]; do sleep 5 & wait $!; done; }

sent=0
submit_successor() {
  [ "$sent" = 1 ] && return
  sent=1
  if [ -n "${RELAY_GENERATIONS:-}" ] && [ "$GEN" -ge "$RELAY_GENERATIONS" ]; then
    log "generation $GEN is the last one; no successor"
    return
  fi
  # The test QOS denies a 6th job outright, so retry while evals hold the slots.
  for _ in $(seq 1 60); do
    if out=$(RELAY_GEN=$((GEN + 1)) sbatch --parsable --export=ALL ${RELAY_SBATCH_ARGS:-} "$SELF" "$SLURM_JOB_ID" 2>&1); then
      log "successor $out submitted"
      return
    fi
    log "successor submit failed: $out"
    sleep 30
  done
}
trap submit_successor USR1

if [ -n "$PREV" ]; then
  log "waiting for job $PREV to end"
  while squeue -h -j "$PREV" 2>/dev/null | grep -q .; do nap 20; done
  log "job $PREV has ended"
fi

END=$(squeue -h -j "$SLURM_JOB_ID" -o %e)
NOTE="RELAY (generation $GEN): this session was resumed in Slurm job $SLURM_JOB_ID on $(hostname) (free test partition). This job ends at $END local time; about 40 min before that it queues a successor job, which resumes you when this one ends. Everything session-scoped died with the previous job: the :17/:47 loop-tick cron, running workflows and background commands. Re-create the tick with CronCreate, check results/STATUS.md, the experiment reports and matches/ on disk to see what the interrupted work finished, relaunch what is missing, and start no workflow that cannot finish 30 min before $END."

start_agent() {
  tmux kill-session -t "$NAME" 2>/dev/null
  tmux new-session -d -s "$NAME" -x 220 -y 50 -c "$WORKDIR" "$AGENT_CMD"
  log "agent launched: $AGENT_CMD"
  nap 120
  tmux send-keys -t "$NAME" -l "$NOTE" && tmux send-keys -t "$NAME" Enter
  log "hand-off note sent"
}

start_agent
restarts=0
while :; do
  nap 60
  if ! tmux has-session -t "$NAME" 2>/dev/null; then
    restarts=$((restarts + 1))
    [ "$restarts" -gt 5 ] && { log "agent exited 5 times; giving up"; break; }
    log "agent exited; restart $restarts"
    start_agent
  fi
done
