#!/bin/bash
# One node of a generation array submitted by submit.sh. Reads the run's frozen roster and
# writes JSONL to $RUN_DIR/generated_data/$VERSION-<index>/; node logs go to $RUN_DIR/logs/.
set -uo pipefail
: "${VERSION:?}" "${RUN_DIR:?}" "${ARRAY_SIZE:?}" "${ROWS_PER_TASK:?}" "${LEVELS:?}"

ST=/srv/storage/magnet@storage1.lille.grid5000.fr/dsileo
REPO=$ST/libs/reasoning_core
export PATH="$ST/miniconda3/bin:$PATH" PYTHONPATH="$REPO" HOME="$ST"

i=$(( ${OAR_ARRAY_INDEX:-1} - 1 ))
node_dir="$RUN_DIR/logs/node-$i"
mkdir -p "$node_dir"
cd "$node_dir" || exit 1  # the worker writes errors.log to its cwd

mapfile -t tasks < "$RUN_DIR/roster.txt"
# The worker's --num_examples is a per-NODE budget shared across tasks; state the target
# as rows per task across the whole array instead.
num_examples=$(( ROWS_PER_TASK * ${#tasks[@]} / ARRAY_SIZE ))
echo "$(hostname) $(date) $VERSION-$i: ${#tasks[@]} tasks, --num_examples $num_examples"

threads=(); [[ -n "${THREADS:-}" ]] && threads=(--threads "$THREADS")
JOBLOG="$node_dir/generation.log" bash "$REPO/reasoning_core/generation/run_generate.sh" \
  --batch "${threads[@]}" --script_dir "$RUN_DIR" --version "$VERSION-$i" \
  --levels $LEVELS --num_examples "$num_examples" --tasks "${tasks[@]}"
echo "done $VERSION-$i $(date)"
