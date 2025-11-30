#!/bin/bash
# =============================================================================
# 本地 CI 测试脚本
# =============================================================================
# 使用与 CI 完全相同的环境运行测试
# - Docker: Neo4j + PostgreSQL
# - 宿主机: Node.js/Python 测试
#
# 用法:
#   ./tools/test-ci.sh          # 运行全部测试
#   ./tools/test-ci.sh infra    # 只启动基础设施
#   ./tools/test-ci.sh down     # 停止基础设施
# =============================================================================

set -e

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(cd "$SCRIPT_DIR/.." && pwd)"
cd "$PROJECT_ROOT"

COMPOSE_FILE="tools/docker/docker-compose.infra.yml"

# Detect docker or podman-compose
if command -v docker &> /dev/null; then
  COMPOSE_CMD="docker compose"
elif command -v podman-compose &> /dev/null; then
  COMPOSE_CMD="podman-compose"
elif [ -x "$HOME/.local/bin/podman-compose" ]; then
  COMPOSE_CMD="$HOME/.local/bin/podman-compose"
else
  echo "Error: docker or podman-compose not found"
  exit 1
fi

# Export environment variables
export NEO4J_URI="bolt://localhost:7687"
export NEO4J_USER="neo4j"
export NEO4J_PASSWORD="pegscanner"
export SKIP_NEO4J_CONTAINER="1"
export DATABASE_URL="postgres://postgres:postgres@localhost:5432/pegscanner"

start_infra() {
  echo "Starting infrastructure (Neo4j + PostgreSQL)..."
  $COMPOSE_CMD -f "$COMPOSE_FILE" up -d
  
  echo "Waiting for Neo4j..."
  for i in {1..30}; do
    if curl -s http://localhost:7474 > /dev/null 2>&1; then
      echo "✓ Neo4j ready"
      break
    fi
    sleep 2
  done
  
  echo "Waiting for PostgreSQL..."
  for i in {1..15}; do
    if pg_isready -h localhost -p 5432 -U postgres > /dev/null 2>&1 || \
       docker exec pegscanner-postgres pg_isready -U postgres > /dev/null 2>&1 || \
       podman exec pegscanner-postgres pg_isready -U postgres > /dev/null 2>&1; then
      echo "✓ PostgreSQL ready"
      break
    fi
    sleep 2
  done
}

stop_infra() {
  echo "Stopping infrastructure..."
  $COMPOSE_CMD -f "$COMPOSE_FILE" down -v 2>/dev/null || true
  echo "✓ Infrastructure stopped"
}

run_tests() {
  echo ""
  echo "=== Running structure lint ==="
  npm run lint:structure
  
  echo ""
  echo "=== Running mobile typecheck ==="
  npx nx run mobile:typecheck
  
  echo ""
  echo "=== Running backend tests ==="
  npx nx run backend:test
  
  echo ""
  echo "=== Running infra-flow ==="
  npx nx run regression:infra-flow
  
  echo ""
  echo "=== Running web-e2e ==="
  npx nx run regression:web-e2e
  
  echo ""
  echo "✓ All tests passed!"
}

case "${1:-run}" in
  infra|up)
    start_infra
    echo ""
    echo "Infrastructure running. Run tests with: npm test"
    echo "Stop with: ./tools/test-ci.sh down"
    ;;
  down|stop)
    stop_infra
    ;;
  run|*)
    # Clean up any previous runs
    stop_infra 2>/dev/null || true
    
    # Start infrastructure
    start_infra
    
    # Run tests
    EXIT_CODE=0
    run_tests || EXIT_CODE=$?
    
    # Clean up
    stop_infra
    
    exit $EXIT_CODE
    ;;
esac
