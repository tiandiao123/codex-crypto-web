#!/usr/bin/env bash
set -euo pipefail

ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "$ROOT_DIR"

if command -v docker-compose >/dev/null 2>&1; then
  COMPOSE_CMD="docker-compose"
else
  COMPOSE_CMD="docker compose"
fi

echo "[CryptoWeb] Starting services with: $COMPOSE_CMD up -d --build"
sudo $COMPOSE_CMD up -d --build

echo "[CryptoWeb] Services are up:"
sudo $COMPOSE_CMD ps
