#!/usr/bin/env bash
set -euo pipefail

# update_and_restart.sh
# Safe, idempotent script to update repo from origin/main and restart services
# - Backs up .env
# - Fetches origin/main and optionally does a hard reset
# - Rebuilds & restarts backend + frontend WITHOUT starting db (default)
# - Simple healthcheck against /docs
#
# Usage:
#   ./update_and_restart.sh [--reset] [--start-db] [--env-file path]
# Options:
#   --reset      : do `git reset --hard origin/main` instead of a fast-forward pull
#   --start-db   : start the full compose stack including the db service (opt-in)
#   --env-file   : path to .env to use (default: ./ .env)

REPO_ROOT="$(cd "$(dirname "$0")" && pwd)"
ENV_FILE="${REPO_ROOT}/.env"
DOCKER_FILES=("-f" "${REPO_ROOT}/docker-compose.yml" "-f" "${REPO_ROOT}/docker-compose.override.yml")
RESET=false
START_DB=false
HEALTH_PATH="/docs"
HEALTH_RETRIES=12
HEALTH_INTERVAL=5

print_usage() {
  cat <<EOF
Usage: $0 [--reset] [--start-db] [--env-file <path>]

--reset       : force hard reset to origin/main (destructive)
--start-db    : start the full compose stack (includes db) - opt-in
--env-file    : path to env file (default: ./ .env)
EOF
}

while [[ ${#} -gt 0 ]]; do
  case "$1" in
    --reset) RESET=true; shift ;;
    --start-db) START_DB=true; shift ;;
    --env-file) ENV_FILE="$2"; shift 2 ;;
    -h|--help) print_usage; exit 0 ;;
    *) echo "Unknown arg: $1"; print_usage; exit 1 ;;
  esac
done

echo "update_and_restart: repo=$REPO_ROOT env_file=$ENV_FILE reset=$RESET start_db=$START_DB"

cd "$REPO_ROOT"

command -v git >/dev/null 2>&1 || { echo "git not found"; exit 1; }
command -v docker >/dev/null 2>&1 || { echo "docker not found"; exit 1; }
command -v docker-compose >/dev/null 2>&1 || true # optional: we use `docker compose`

# Backup .env
if [ -f "$ENV_FILE" ]; then
  BACKUP_NAME="${ENV_FILE}.backup.$(date +%Y%m%d%H%M%S)"
  cp -v "$ENV_FILE" "$BACKUP_NAME"
  echo ".env backed up to $BACKUP_NAME"
else
  echo "Warning: $ENV_FILE not found. Creating a minimal .env from .env.example if present."
  if [ -f .env.example ]; then
    cp -v .env.example "$ENV_FILE"
    echo "Created $ENV_FILE from .env.example"
  else
    echo "No .env.example found; continuing without .env"
  fi
fi

# Sync with origin/main
git fetch origin
git checkout main || git switch main
if [ "$RESET" = true ]; then
  echo "Resetting hard to origin/main"
  git reset --hard origin/main
  git clean -fd
else
  echo "Pulling origin/main (fast-forward when possible)"
  # prefer fast-forward; if fails, fallback to merge
  if ! git pull --ff-only origin main; then
    echo "Fast-forward failed, doing normal pull"
    git pull origin main
  fi
fi

# Ensure .env still exists (we backed it up)
if [ ! -f "$ENV_FILE" ]; then
  echo "Warning: $ENV_FILE still missing after sync. Create or restore it from backup."
fi

# Show docker compose config small check (DB_HOST/ports)
echo "Docker compose config (DB_HOST/ports):"
docker compose --env-file "$ENV_FILE" ${DOCKER_FILES[@]} config | grep -E "DB_HOST|DB_PORT|HOST_DB_PORT|INTERNAL_DB_PORT|VITE_API_URL" || true

# Start services
if [ "$START_DB" = true ]; then
  echo "Starting full stack including db (this may map port 5432 on host)"
  docker compose --env-file "$ENV_FILE" ${DOCKER_FILES[@]} up -d --build --remove-orphans
else
  echo "Starting only backend and frontend (no db)"
  docker compose --env-file "$ENV_FILE" ${DOCKER_FILES[@]} up -d --build --no-deps backend frontend
fi

echo "Waiting ${HEALTH_INTERVAL}s before healthcheck..."
sleep $HEALTH_INTERVAL

# Healthcheck loop
URL="http://localhost:8000${HEALTH_PATH}"
echo "Healthcheck: $URL"
RETRY=0
while [ $RETRY -lt $HEALTH_RETRIES ]; do
  HTTP_CODE=$(curl -sS -o /dev/null -w "%{http_code}" "$URL" || true)
  if [ "$HTTP_CODE" = "200" ]; then
    echo "Healthcheck passed (200)"
    exit 0
  fi
  echo "Healthcheck attempt $((RETRY+1))/$HEALTH_RETRIES failed (code: ${HTTP_CODE:-none}), sleeping ${HEALTH_INTERVAL}s..."
  sleep $HEALTH_INTERVAL
  RETRY=$((RETRY+1))
done

echo "Healthcheck failed after ${HEALTH_RETRIES} attempts. Showing backend logs for diagnosis:"
docker compose --env-file "$ENV_FILE" ${DOCKER_FILES[@]} logs --no-log-prefix --tail=200 backend || true
exit 2
