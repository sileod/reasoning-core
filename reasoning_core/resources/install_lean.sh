#!/usr/bin/env bash
set -euo pipefail

usage() {
  cat <<'EOF'
Usage: ./install_lean.sh [OPTIONS]

Prewarm the optional Lean backend.

Options:
  --profile PROFILE     core, mathlib, or both. Default: mathlib.
  --lean-source-build   Allow Mathlib to build from source if binary cache fails.
  --with-python         Also run pip install -e .
  --user                Pass --user to pip install.
  -h, --help            Show this help.

Examples:
  ./install_lean.sh
  ./install_lean.sh --profile core
  ./install_lean.sh --profile both
EOF
}

install_python=0
allow_lean_source_build=0
pip_user=0
profile=mathlib

while [[ $# -gt 0 ]]; do
  case "$1" in
    --profile)
      profile="${2:-}"
      shift
      ;;
    --lean-source-build)
      allow_lean_source_build=1
      ;;
    --with-python)
      install_python=1
      ;;
    --user)
      pip_user=1
      ;;
    -h|--help)
      usage
      exit 0
      ;;
    *)
      echo "Unknown option: $1" >&2
      usage >&2
      exit 2
      ;;
  esac
  shift
done

script_dir="$(cd "$(dirname "$0")" && pwd)"
repo_root="$(cd "$script_dir/../.." && pwd)"
if [[ -f "$repo_root/pyproject.toml" ]]; then
  cd "$repo_root"
fi

PYTHON="${PYTHON:-python3}"

if ! command -v "$PYTHON" >/dev/null 2>&1; then
  echo "Python executable not found: $PYTHON" >&2
  exit 1
fi

if [[ "$install_python" -eq 1 ]]; then
  pip_args=(install -e .)
  if [[ "$pip_user" -eq 1 ]]; then
    pip_args=(install --user -e .)
  fi
  "$PYTHON" -m pip "${pip_args[@]}"
fi

case "$profile" in
  core|mathlib|both) ;;
  *)
    echo "Unknown profile: $profile" >&2
    usage >&2
    exit 2
    ;;
esac

if [[ "$allow_lean_source_build" -eq 1 ]]; then
  export REASONING_CORE_LEAN_ALLOW_SOURCE_BUILD=1
fi

"$PYTHON" - "$profile" <<'PY'
import sys
from reasoning_core.tasks.lean import ensure_lean_core, ensure_lean_mathlib

profile = sys.argv[1]
if profile in ("core", "both"):
    ensure_lean_core(verbose=True)
if profile in ("mathlib", "both"):
    ensure_lean_mathlib(verbose=True)
PY
