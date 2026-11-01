#!/bin/bash
# Run one command on the cluster's free `test` partition (0 fairshare) and block until it ends.
#   tools/onslurm.sh [-c CORES] [-m MEM] [-t TIME] [-J NAME] -- CMD ARGS...
# e.g. tools/onslurm.sh -c 32 -m 20G -t 00:40:00 -J gate -- python3.12 tools/eval.py CAND CHAMP --maps all --jobs 16
# Sizing (measured 31 Oct): one game uses ~2.1 cores and ~0.8 GB for ~20-50 s wall,
# so pair `-c 2N` with `--jobs N` and ~1 GB per job. The command runs in the repo folder;
# its output is printed when the job ends (log kept in netscratch .../battlecode/logs).
# `test` allows 5 jobs and 112 cores per user: a full queue is retried, not an error.
# The command runs in a node-local copy of the workspace (bots without build caches, maps,
# tools, sdk), because every run rebuilds bots/<bot>/.cambc/build/bot.wasm in place and
# parallel jobs sharing one bot would read half-written modules. results/, matches/ and
# replays/ link back to the real ones, so outputs land where they always do.
set -u
cores=16 mem=16G time=01:00:00 name=cambc
while [ $# -gt 0 ]; do
  case "$1" in
    -c) cores=$2; shift 2 ;;
    -m) mem=$2; shift 2 ;;
    -t) time=$2; shift 2 ;;
    -J) name=$2; shift 2 ;;
    --) shift; break ;;
    *) break ;;
  esac
done
[ $# -gt 0 ] || { echo "usage: $0 [-c N] [-m MEM] [-t TIME] [-J NAME] -- CMD..." >&2; exit 2; }
ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
LOGS=/n/netscratch/hekstra_lab/Lab/ian_poon/battlecode/logs
mkdir -p "$LOGS"
user_cmd=$(printf '%q ' "$@")
q_root=$(printf '%q' "$ROOT")
cmd="set -e
WS=/scratch/\${USER}_\${SLURM_JOB_ID}/ws
trap 'rm -rf /scratch/\${USER}_\${SLURM_JOB_ID}' EXIT
mkdir -p \"\$WS\"
cd $q_root
rsync -a --exclude .cambc --exclude build --exclude target --exclude '.nfs*' bots maps tools sdk cmake postmortems cli cambc.toml \"\$WS/\" || [ \$? -eq 24 ]
for d in results matches replays; do ln -s \"\$(readlink -f $q_root/\$d)\" \"\$WS/\$d\"; done
export GIT_DIR=\"\$(git -C $q_root rev-parse --absolute-git-dir)\"
cd \"\$WS\"
set +e
$user_cmd"
tmp=$(mktemp -d)
trap 'rm -rf "$tmp"' EXIT
while :; do
  sbatch --parsable --wait -p test -c "$cores" --mem "$mem" -t "$time" -J "$name" \
    -D "$ROOT" -o "$LOGS/%x-%j.out" --wrap "$cmd" >"$tmp/id" 2>"$tmp/err"
  rc=$?
  jid=$(head -n1 "$tmp/id" | cut -d';' -f1)
  [ -n "$jid" ] && break
  if grep -qiE 'MaxSubmit|MaxJobs|temporarily unavailable|timed out|try again' "$tmp/err"; then
    sleep 60
    continue
  fi
  cat "$tmp/err" >&2
  exit 1
done
cat "$LOGS/$name-$jid.out"
echo "[onslurm] job $jid exit $rc"
exit $rc
