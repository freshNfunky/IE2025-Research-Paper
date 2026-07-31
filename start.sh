#!/usr/bin/env bash
#
# Start the interactive live-perception demo.
#
#   ./start.sh          # backend on http://127.0.0.1:8800/
#   ./start.sh 8899     # custom port
#
# On first run (no virtualenv) it creates .venv and installs the dependencies.
# Afterwards it just launches the backend server on 127.0.0.1:<port>.
#
set -euo pipefail

# Repo root = directory of this script (so it works from anywhere).
ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "$ROOT"

PORT="${1:-8800}"
VENV="$ROOT/.venv"
PY="$VENV/bin/python"

# Interpreter used to CREATE the venv. Torch has no wheels for 3.14 yet,
# so prefer 3.12/3.13; fall back to whatever python3 is available.
pick_python() {
  for c in python3.12 python3.13 python3.11 python3; do
    command -v "$c" >/dev/null 2>&1 && { echo "$c"; return; }
  done
  echo "python3"
}

# Decide whether we need to (re)install: no venv, or an incomplete one.
need_install=0
if [ ! -x "$PY" ]; then
  need_install=1
elif ! "$PY" -c 'import uvicorn, fastapi, torch, ultralytics, open_clip' >/dev/null 2>&1; then
  echo ">> Virtualenv found but dependencies are incomplete; (re)installing."
  need_install=1
fi

if [ "$need_install" -eq 1 ]; then
  if [ ! -x "$PY" ]; then
    BOOT="$(pick_python)"
    echo ">> Creating virtualenv with ${BOOT} ..."
    "$BOOT" -m venv "$VENV"
  fi
  echo ">> Installing dependencies (first run downloads torch, this is slow) ..."
  "$PY" -m pip install --upgrade pip
  "$PY" -m pip install --timeout 180 --retries 15 -r "$ROOT/requirements.txt"
  "$PY" -m pip install --timeout 180 --retries 15 -r "$ROOT/app_live/requirements-app.txt"
  echo ">> Environment ready."
fi

echo ">> Live demo backend: http://127.0.0.1:${PORT}/"
exec "$PY" -m uvicorn app_live.server:app --host 127.0.0.1 --port "$PORT"
