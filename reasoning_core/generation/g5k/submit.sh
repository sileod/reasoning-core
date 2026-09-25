#!/usr/bin/env bash
# Build a generator release into a Hub staging dataset on Grid'5000. Run on a G5K frontend
# (lille), from the storage checkout after `g5k.sh sync`:
#
#   VERSION=rc13 bash reasoning_core/generation/g5k/submit.sh             # full build
#   VERSION=rc13 SMOKE=1 bash reasoning_core/generation/g5k/submit.sh     # 1 node, tiny, no upload
#   VERSION=rc13 COLLECT_ONLY=1 bash reasoning_core/generation/g5k/submit.sh  # final upload pass
#
# Everything a run writes lives in $ST/runs/$VERSION (generated_data/, upload_state/, logs/),
# never in the checkout. Resubmitting the same VERSION resumes: workers skip finished files.
#
# Knobs (env): ROSTER=file (one task per line, `#` comments; default list_tasks()),
# ARRAY_SIZE=16, WALLTIME=24:00:00, ROWS_PER_TASK=20000, LEVELS="0 0 0 1 1 1 2 2 2 3 3 4 4 5 6",
# THREADS (default: run_generate.sh's), DATASET_NAME=staging, SUBMIT_COLLECT=1,
# COLLECT_WALLTIME=24:00:00, COLLECT_PERIOD_SECONDS=1800.
set -euo pipefail
: "${VERSION:?set VERSION, e.g. VERSION=rc13}"
[[ "$VERSION" =~ ^[A-Za-z0-9._-]+$ ]] || { echo "bad VERSION: $VERSION" >&2; exit 2; }

ST=/srv/storage/magnet@storage1.lille.grid5000.fr/dsileo
REPO=$ST/libs/reasoning_core
PY=$ST/miniconda3/bin/python
HERE=$REPO/reasoning_core/generation/g5k

if [[ "${SMOKE:-0}" == 1 ]]; then
  VERSION="$VERSION-smoke" ARRAY_SIZE=1 WALLTIME=1:00:00 ROWS_PER_TASK=32 SUBMIT_COLLECT=0
fi
ARRAY_SIZE=${ARRAY_SIZE:-16}
WALLTIME=${WALLTIME:-24:00:00}
ROWS_PER_TASK=${ROWS_PER_TASK:-20000}
LEVELS=${LEVELS:-0 0 0 1 1 1 2 2 2 3 3 4 4 5 6}
DATASET_NAME=${DATASET_NAME:-staging}
RUN_DIR=$ST/runs/$VERSION
mkdir -p "$RUN_DIR/logs"
cd "$REPO"

collect_cmd="VERSION='$VERSION' RUN_DIR='$RUN_DIR' DATASET_NAME='$DATASET_NAME' \
COLLECT_LOOP=\${COLLECT_LOOP} COLLECT_PERIOD_SECONDS='${COLLECT_PERIOD_SECONDS:-1800}' \
bash '$HERE/collect.sh'"
submit_collect() {  # $1 = loop (1) or single pass (0)
  oarsub -n "${VERSION}_collect" -t besteffort -t idempotent \
    -l "/nodes=1,walltime=${COLLECT_WALLTIME:-24:00:00}" \
    -O "$RUN_DIR/logs/collect.%jobid%.out" -E "$RUN_DIR/logs/collect.%jobid%.err" \
    "${collect_cmd//\$\{COLLECT_LOOP\}/$1}"
}
if [[ "${COLLECT_ONLY:-0}" == 1 ]]; then submit_collect 0; exit; fi

# The fleet conda is 3.10 while dev is newer: one PEP 701 f-string makes the package
# unimportable and every worker dies with an empty build while OAR still says Running.
"$PY" - "$REPO/reasoning_core" <<'EOF'
import ast, pathlib, sys
bad = []
for p in pathlib.Path(sys.argv[1]).rglob("*.py"):
    if "deprecated" in p.parts:
        continue
    try:
        ast.parse(p.read_text(), str(p))
    except SyntaxError as e:
        bad.append(f"{p}:{e.lineno}: {e.msg}")
if bad:
    sys.exit("ABORT: does not parse under Python %s:\n  " % sys.version.split()[0] + "\n  ".join(bad))
EOF

# Freeze the roster for this run: every node reads the same resolved list.
"$PY" - "${ROSTER:-}" "$RUN_DIR/roster.txt" <<'EOF'
import sys
from reasoning_core import get_task, list_tasks
src, out = sys.argv[1:]
if src:
    names = [l.split("#")[0].strip() for l in open(src)]
    names = [n for n in names if n]
else:
    names = list_tasks()
missing = []
for n in names:
    try:
        get_task(n)
    except Exception as e:
        missing.append(f"{n}: {e}")
if missing:
    sys.exit("ABORT: roster does not resolve:\n  " + "\n  ".join(missing))
open(out, "w").write("".join(n + "\n" for n in names))
print(f"roster: {len(names)} tasks -> {out}")
EOF

echo "run: $RUN_DIR  nodes=$ARRAY_SIZE walltime=$WALLTIME rows/task=$ROWS_PER_TASK -> $DATASET_NAME"
oarsub -n "${VERSION}_gen" -t besteffort -t idempotent \
  -l "/nodes=1,walltime=$WALLTIME" --array "$ARRAY_SIZE" \
  -O "$RUN_DIR/logs/gen.%jobid%.out" -E "$RUN_DIR/logs/gen.%jobid%.err" \
  "VERSION='$VERSION' RUN_DIR='$RUN_DIR' ARRAY_SIZE='$ARRAY_SIZE' ROWS_PER_TASK='$ROWS_PER_TASK' \
LEVELS='$LEVELS' THREADS='${THREADS:-}' bash '$HERE/launcher.sh'"
[[ "${SUBMIT_COLLECT:-1}" == 1 ]] && submit_collect 1
echo "follow: tail -f $RUN_DIR/logs/*.out; ls $RUN_DIR/generated_data"
