#!/usr/bin/env bash
# deploy/deploy.sh — Deploy (or redeploy) the todo app on the VM.
#
# Usage (from your LOCAL machine):
#   ssh todo-vm 'cd ~/todo-app && bash deploy/deploy.sh'
#
# Or run directly ON the VM:
#   cd ~/todo-app && bash deploy/deploy.sh
#
set -euo pipefail

COMPOSE_FILE="docker-compose.prod.yml"
ENV_FILE="deploy/.env"

echo "==> Pulling latest code..."
git pull origin main

echo ""
echo "==> Checking .env file..."
if [ ! -f "$ENV_FILE" ]; then
  echo "ERROR: $ENV_FILE not found!"
  echo "Copy deploy/.env.example to deploy/.env and fill in your secrets."
  exit 1
fi

echo ""
echo "==> Building containers..."
docker compose -f "$COMPOSE_FILE" --env-file "$ENV_FILE" build

echo ""
echo "==> Starting services (detached)..."
docker compose -f "$COMPOSE_FILE" --env-file "$ENV_FILE" up -d

echo ""
echo "==> Waiting for backend health check..."
sleep 5

# Simple health check
HEALTH=$(docker compose -f "$COMPOSE_FILE" --env-file "$ENV_FILE" exec -T backend \
  python -c "import urllib.request; print(urllib.request.urlopen('http://localhost:5001/api/health').read().decode())" 2>/dev/null || echo "FAILED")

if echo "$HEALTH" | grep -qi "ok\|healthy"; then
  echo "Backend is healthy!"
else
  echo "WARNING: Backend health check returned: $HEALTH"
  echo "Check logs with: docker compose -f $COMPOSE_FILE logs backend"
fi

echo ""
echo "==> Current container status:"
docker compose -f "$COMPOSE_FILE" --env-file "$ENV_FILE" ps

echo ""
echo "==> Deploy complete!"
echo "    View logs: docker compose -f $COMPOSE_FILE --env-file $ENV_FILE logs -f"
