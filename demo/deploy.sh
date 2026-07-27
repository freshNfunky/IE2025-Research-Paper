#!/usr/bin/env bash
# deploy.sh — publish the interactive perception demo over SSH/rsync.
#
# Unlike a single-file tool, this demo is a FOLDER (index.html + data/), so we
# sync the whole directory to the target. Connection details come from .env
# (same SSH key as the other felixschaller tools).
#
#   ./deploy.sh          upload the demo
#   ./deploy.sh --dry    show what rsync would do, transfer nothing
#
# Result URL (folder resolves via index.html):
#   https://public.felixschaller.com/tools/<REMOTE_PATH-basename>/
#
# Requires: ssh + rsync. Auth uses SSH_KEY if set in .env, else ssh-agent.

set -euo pipefail
cd "$(dirname "$0")"

DRY=false
[[ "${1:-}" == "--dry" ]] && DRY=true

[[ -f .env ]] || { echo "Missing .env — copy .env.example to .env first." >&2; exit 1; }
set -a
# shellcheck disable=SC1091
source ./.env
set +a

: "${SSH_HOST:?SSH_HOST missing}"
: "${SSH_USER:?SSH_USER missing}"
: "${REMOTE_PATH:?REMOTE_PATH missing}"
SSH_PORT="${SSH_PORT:-22}"

command -v ssh   >/dev/null 2>&1 || { echo "ssh is required."   >&2; exit 1; }
command -v rsync >/dev/null 2>&1 || { echo "rsync is required." >&2; exit 1; }

[[ -f index.html && -d data ]] || {
  echo "✗ run this from the demo/ folder (index.html + data/ expected)." >&2; exit 1; }

SSH_OPTS=(-p "$SSH_PORT" -o StrictHostKeyChecking=accept-new)
[[ -n "${SSH_KEY:-}" ]] && SSH_OPTS+=(-i "$SSH_KEY")
REMOTE="${SSH_USER}@${SSH_HOST}"
RSH="ssh ${SSH_OPTS[*]}"
BASE="${SITE_URL:-https://public.felixschaller.com}"

# Only the files the page actually needs; keep deploy/config/docs off the server.
RSYNC=(rsync -az --delete
  --exclude='.env' --exclude='.env.example' --exclude='deploy.sh'
  --exclude='README.md' --exclude='.DS_Store'
  -e "$RSH" ./ "${REMOTE}:${REMOTE_PATH}/")

echo "Deploying demo/  ->  ${REMOTE}:${REMOTE_PATH}/  (port ${SSH_PORT})"
if $DRY; then
  echo "(dry run — nothing transferred)"
  "${RSYNC[@]}" --dry-run -v || true
  echo "URL would be: ${BASE%/}/tools/${REMOTE_PATH##*/}/"
  exit 0
fi

ssh "${SSH_OPTS[@]}" "$REMOTE" "mkdir -p '${REMOTE_PATH}'"
"${RSYNC[@]}"
echo "✓ uploaded"
echo "Done. Live at: ${BASE%/}/tools/${REMOTE_PATH##*/}/"
