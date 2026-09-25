#!/bin/bash
# Upload a run's JSONL to reasoning-core/$DATASET_NAME. COLLECT_LOOP=1 repeats every
# COLLECT_PERIOD_SECONDS while generation runs (keeping files); a single pass deletes uploaded
# files. One collector per run at a time.
set -euo pipefail
: "${VERSION:?}" "${RUN_DIR:?}" "${DATASET_NAME:?}"

ST=/srv/storage/magnet@storage1.lille.grid5000.fr/dsileo
REPO=$ST/libs/reasoning_core
export PATH="$ST/miniconda3/bin:$PATH" PYTHONPATH="$REPO" HOME="$ST"
export HF_TOKEN="${HF_TOKEN:-$(cat "$ST/.hf_token")}"  # 0600 file, not inline

COLLECT_LOOP=${COLLECT_LOOP:-0}
COLLECT_PERIOD_SECONDS=${COLLECT_PERIOD_SECONDS:-1800}
# Stop looping a little before a 24h walltime; a final single pass picks up the rest.
COLLECT_MAX_SECONDS=${COLLECT_MAX_SECONDS:-82800}
delete=--delete; [[ "$COLLECT_LOOP" == 1 ]] && delete=--no-delete

mkdir -p "$RUN_DIR/upload_state"
exec 9>"$RUN_DIR/upload_state/collect.lock"
flock -n 9 || { echo "collect: another collector holds $RUN_DIR; exiting"; exit 0; }

collect() {
  python -m reasoning_core.generation.collect --rc_path "$RUN_DIR" \
    --dataset_name "$DATASET_NAME" --version "$VERSION-*" --prefix "data/$VERSION" "$delete"
}
[[ "$COLLECT_LOOP" == 1 ]] || { collect; exit; }

deadline=$(( $(date +%s) + COLLECT_MAX_SECONDS ))
while true; do
  echo "collect: round at $(date)"; collect
  (( $(date +%s) + COLLECT_PERIOD_SECONDS > deadline )) && { echo "collect: max runtime"; break; }
  sleep "$COLLECT_PERIOD_SECONDS"
done
