#!/usr/bin/env sh
set -eu

PROJECT_ROOT=$(CDPATH= cd -- "$(dirname -- "$0")/.." && pwd)
COVER_DIR="${TMPDIR:-/tmp}/transcrito-trace-cover"
PYTHON_BIN="${PROJECT_ROOT}/.venv/bin/python"

if [ ! -x "$PYTHON_BIN" ]; then
  PYTHON_BIN="python3"
fi

cd "$PROJECT_ROOT"

if "$PYTHON_BIN" -m coverage --version >/dev/null 2>&1; then
  "$PYTHON_BIN" -m coverage erase
  "$PYTHON_BIN" -m coverage run --source=src -m unittest discover -s tests
  "$PYTHON_BIN" -m coverage report -m
  exit 0
fi

rm -rf "$COVER_DIR"

"$PYTHON_BIN" -m trace \
  --count \
  --summary \
  --missing \
  --coverdir="$COVER_DIR" \
  --ignore-dir=/usr \
  --ignore-dir="$HOME/.local" \
  --ignore-dir="$PROJECT_ROOT/tests" \
  --module unittest discover -s tests
