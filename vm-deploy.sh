#!/usr/bin/env bash
set -euo pipefail

echo "VM Deploy: stopping existing compose and removing partial db container (if any)"
sudo docker compose down || true

echo "Removing any stale db container named system-ti-db-1 (silently if not present)"
sudo docker rm -f system-ti-db-1 2>/dev/null || true

echo "Starting backend and frontend (using docker-compose.override.yml to avoid mapping host 5432)"
sudo docker compose -f docker-compose.yml -f docker-compose.override.yml up -d --build backend frontend

echo "Current containers:"
sudo docker compose -f docker-compose.yml -f docker-compose.override.yml ps

echo "If you want to follow backend logs run: sudo docker compose -f docker-compose.yml -f docker-compose.override.yml logs -f backend"

echo "Done."
