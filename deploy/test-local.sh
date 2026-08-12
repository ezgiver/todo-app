#!/usr/bin/env bash
# deploy/test-local.sh — Spin up the full production stack locally and run smoke tests.
#
# Usage:
#   bash deploy/test-local.sh
#
# What it does:
#   1. Builds and starts all containers (backend, frontend, caddy, local postgres)
#   2. Waits for health checks to pass
#   3. Runs HTTP smoke tests against localhost
#   4. Tears everything down
#
# Requirements: docker compose, curl
#
set -euo pipefail

COMPOSE_FILE="docker-compose.test-prod.yml"
BASE_URL="http://localhost"
PASSED=0
FAILED=0

# Colors
GREEN='\033[0;32m'
RED='\033[0;31m'
YELLOW='\033[1;33m'
NC='\033[0m'

cleanup() {
  echo ""
  echo -e "${YELLOW}==> Tearing down containers...${NC}"
  docker compose -f "$COMPOSE_FILE" down -v --remove-orphans 2>/dev/null
  rm -f /tmp/todo_test_cookies.txt
}
trap cleanup EXIT

assert_status() {
  local description="$1"
  local url="$2"
  local expected_status="$3"

  actual_status=$(curl -s -o /dev/null -w "%{http_code}" "$url" 2>/dev/null || echo "000")

  if [ "$actual_status" = "$expected_status" ]; then
    echo -e "  ${GREEN}PASS${NC} $description (HTTP $actual_status)"
    PASSED=$((PASSED + 1))
  else
    echo -e "  ${RED}FAIL${NC} $description (expected $expected_status, got $actual_status)"
    FAILED=$((FAILED + 1))
  fi
}

assert_body_contains() {
  local description="$1"
  local url="$2"
  local expected_text="$3"

  body=$(curl -s "$url" 2>/dev/null || echo "")

  if echo "$body" | grep -qi "$expected_text"; then
    echo -e "  ${GREEN}PASS${NC} $description"
    PASSED=$((PASSED + 1))
  else
    echo -e "  ${RED}FAIL${NC} $description (response did not contain '$expected_text')"
    echo "       Got: ${body:0:200}"
    FAILED=$((FAILED + 1))
  fi
}

echo -e "${YELLOW}==> Building and starting production stack locally...${NC}"
echo "    (This may take a minute on first build)"
echo ""
docker compose -f "$COMPOSE_FILE" up --build -d

echo ""
echo -e "${YELLOW}==> Waiting for services to be healthy...${NC}"

# Wait up to 60 seconds for backend health check
SECONDS_WAITED=0
MAX_WAIT=60
while [ $SECONDS_WAITED -lt $MAX_WAIT ]; do
  BACKEND_HEALTH=$(docker compose -f "$COMPOSE_FILE" ps --format json 2>/dev/null | \
    grep -o '"Health":"[^"]*"' | head -1 || echo "")

  # Also try a direct curl
  if curl -s -f "$BASE_URL/api/health" > /dev/null 2>&1; then
    echo "    Services ready after ${SECONDS_WAITED}s"
    break
  fi

  sleep 2
  SECONDS_WAITED=$((SECONDS_WAITED + 2))
  echo "    Waiting... (${SECONDS_WAITED}s)"
done

if [ $SECONDS_WAITED -ge $MAX_WAIT ]; then
  echo -e "${RED}ERROR: Services did not become healthy within ${MAX_WAIT}s${NC}"
  echo ""
  echo "Container status:"
  docker compose -f "$COMPOSE_FILE" ps
  echo ""
  echo "Backend logs:"
  docker compose -f "$COMPOSE_FILE" logs backend --tail=30
  exit 1
fi

echo ""
echo -e "${YELLOW}==> Running smoke tests...${NC}"
echo ""

# Test 1: Health endpoint
assert_status "GET /api/health returns 200" "$BASE_URL/api/health" "200"

# Test 2: API returns JSON
assert_body_contains "GET /api/health returns JSON" "$BASE_URL/api/health" "status"

# Test 3: Frontend serves HTML
assert_status "GET / returns 200 (frontend)" "$BASE_URL/" "200"
assert_body_contains "GET / returns React app HTML" "$BASE_URL/" "<div id"

# Test 4: SPA fallback works (unknown route still serves index.html)
assert_status "GET /some/random/path returns 200 (SPA fallback)" "$BASE_URL/some/random/path" "200"

# Test 5: Register a test user (needed for todo creation — routes require auth)
REGISTER_STATUS=$(curl -s -o /dev/null -w "%{http_code}" -X POST "$BASE_URL/api/auth/register" \
  -H "Content-Type: application/json" \
  -d '{"email": "test@example.com", "display_name": "Smoke Test", "password": "TestPass123!"}' 2>/dev/null || echo "000")

if [ "$REGISTER_STATUS" = "201" ] || [ "$REGISTER_STATUS" = "200" ]; then
  echo -e "  ${GREEN}PASS${NC} POST /api/auth/register creates a user (HTTP $REGISTER_STATUS)"
  PASSED=$((PASSED + 1))
else
  echo -e "  ${RED}FAIL${NC} POST /api/auth/register (expected 201, got $REGISTER_STATUS)"
  FAILED=$((FAILED + 1))
fi

# Test 5b: Log in (register doesn't create a session — login is required)
LOGIN_STATUS=$(curl -s -o /dev/null -w "%{http_code}" -X POST "$BASE_URL/api/auth/login" \
  -H "Content-Type: application/json" \
  -c /tmp/todo_test_cookies.txt \
  -d '{"email": "test@example.com", "password": "TestPass123!"}' 2>/dev/null || echo "000")

if [ "$LOGIN_STATUS" = "200" ]; then
  echo -e "  ${GREEN}PASS${NC} POST /api/auth/login returns session cookie (HTTP $LOGIN_STATUS)"
  PASSED=$((PASSED + 1))
else
  echo -e "  ${RED}FAIL${NC} POST /api/auth/login (expected 200, got $LOGIN_STATUS)"
  FAILED=$((FAILED + 1))
fi

# Test 6: Create a todo (authenticated via session cookie)
CREATE_STATUS=$(curl -s -L -o /dev/null -w "%{http_code}" -X POST "$BASE_URL/api/todos/" \
  -H "Content-Type: application/json" \
  -b /tmp/todo_test_cookies.txt \
  -d '{"title": "Smoke test todo"}' 2>/dev/null || echo "000")

if [ "$CREATE_STATUS" = "201" ] || [ "$CREATE_STATUS" = "200" ]; then
  echo -e "  ${GREEN}PASS${NC} POST /api/todos/ creates a todo (HTTP $CREATE_STATUS)"
  PASSED=$((PASSED + 1))
else
  echo -e "  ${RED}FAIL${NC} POST /api/todos/ (expected 201, got $CREATE_STATUS)"
  FAILED=$((FAILED + 1))
fi

# Test 7: Read it back (authenticated)
TODO_BODY=$(curl -s -L -b /tmp/todo_test_cookies.txt "$BASE_URL/api/todos/" 2>/dev/null || echo "")
if echo "$TODO_BODY" | grep -qi "Smoke test todo"; then
  echo -e "  ${GREEN}PASS${NC} GET /api/todos contains created todo"
  PASSED=$((PASSED + 1))
else
  echo -e "  ${RED}FAIL${NC} GET /api/todos did not contain 'Smoke test todo'"
  echo "       Got: ${TODO_BODY:0:200}"
  FAILED=$((FAILED + 1))
fi

# Test 8: Security headers from Caddy
HEADERS=$(curl -s -I "$BASE_URL/" 2>/dev/null || echo "")
if echo "$HEADERS" | grep -qi "x-content-type-options"; then
  echo -e "  ${GREEN}PASS${NC} Security headers present (X-Content-Type-Options)"
  PASSED=$((PASSED + 1))
else
  echo -e "  ${RED}FAIL${NC} Security headers missing"
  FAILED=$((FAILED + 1))
fi

echo ""
echo "==========================================="
echo -e "  Results: ${GREEN}${PASSED} passed${NC}, ${RED}${FAILED} failed${NC}"
echo "==========================================="
echo ""

if [ $FAILED -gt 0 ]; then
  echo "Container logs for debugging:"
  docker compose -f "$COMPOSE_FILE" logs --tail=20
  exit 1
fi

echo -e "${GREEN}All tests passed! Production stack is working correctly.${NC}"
