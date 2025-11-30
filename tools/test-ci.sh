#!/bin/bash
# =============================================================================
# 本地 CI 测试脚本
# =============================================================================
# 使用与 CI 完全相同的 Docker 环境运行测试
#
# 用法:
#   ./tools/test-ci.sh          # 运行全部测试
#   ./tools/test-ci.sh build    # 只构建镜像
#   ./tools/test-ci.sh shell    # 进入测试容器 shell
# =============================================================================

set -e

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(cd "$SCRIPT_DIR/.." && pwd)"
cd "$PROJECT_ROOT"

COMPOSE_FILE="tools/docker/docker-compose.test.yml"

case "${1:-run}" in
  build)
    echo "Building CI test image..."
    docker compose -f "$COMPOSE_FILE" build test-runner
    echo "✓ Build complete"
    ;;
  shell)
    echo "Starting test environment shell..."
    docker compose -f "$COMPOSE_FILE" run --rm test-runner bash
    ;;
  clean)
    echo "Cleaning up test containers..."
    docker compose -f "$COMPOSE_FILE" down -v --remove-orphans
    echo "✓ Cleanup complete"
    ;;
  run|*)
    echo "Starting CI test suite..."
    echo "This replicates the exact CI environment locally."
    echo ""
    
    # Clean up any previous runs
    docker compose -f "$COMPOSE_FILE" down -v --remove-orphans 2>/dev/null || true
    
    # Run tests
    docker compose -f "$COMPOSE_FILE" up \
      --build \
      --abort-on-container-exit \
      --exit-code-from test-runner
    
    EXIT_CODE=$?
    
    # Clean up
    docker compose -f "$COMPOSE_FILE" down -v --remove-orphans 2>/dev/null || true
    
    if [ $EXIT_CODE -eq 0 ]; then
      echo ""
      echo "✓ All CI tests passed!"
    else
      echo ""
      echo "✗ CI tests failed with exit code $EXIT_CODE"
    fi
    
    exit $EXIT_CODE
    ;;
esac

