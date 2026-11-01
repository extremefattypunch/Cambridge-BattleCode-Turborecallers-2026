#!/bin/bash
# Attach this terminal to the relayed Claude agent started by tools/agent_relay.sbatch.
# Detach again with Ctrl-b d (quitting claude only makes the relay restart it; stop: scancel -n cambc-agent).
jid=$(squeue -h -u "$USER" -n cambc-agent -t R -o %i | head -n1)
[ -n "$jid" ] || { echo "no running cambc-agent job"; exit 1; }
# A shell inside another Slurm job (e.g. an OOD desktop) carries SLURM_* variables that confuse srun.
exec env $(env | grep -o '^SLURM_[A-Za-z_]*' | sed 's/^/-u /') srun --jobid "$jid" --overlap --pty tmux attach -t cambc-agent
