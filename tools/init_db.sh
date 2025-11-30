#!/bin/bash
# =============================================================================
# 数据库初始化脚本
# 首次部署时运行一次
# =============================================================================

set -e

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(dirname "$SCRIPT_DIR")"

# 加载环境变量
if [ -f "$PROJECT_ROOT/.env" ]; then
    export $(grep -v '^#' "$PROJECT_ROOT/.env" | xargs)
fi

echo "=== PEG Scanner Database Initialization ==="

# -----------------------------------------------------------------------------
# 1. PostgreSQL
# -----------------------------------------------------------------------------
echo ""
echo "[1/4] Checking PostgreSQL..."

PGHOST="${PGHOST:-localhost}"
PGPORT="${PGPORT:-5432}"
PGUSER="${POSTGRES_USER:-postgres}"
PGPASSWORD="${POSTGRES_PASSWORD:-postgres}"
PGDATABASE="${POSTGRES_DB:-pegscanner}"

export PGPASSWORD

# 等待 PostgreSQL 就绪
echo "Waiting for PostgreSQL at $PGHOST:$PGPORT..."
for i in {1..30}; do
    if pg_isready -h "$PGHOST" -p "$PGPORT" -U "$PGUSER" >/dev/null 2>&1; then
        echo "PostgreSQL is ready!"
        break
    fi
    echo "Attempt $i/30..."
    sleep 2
done

# 创建数据库 (如果不存在)
echo "Creating database '$PGDATABASE' if not exists..."
psql -h "$PGHOST" -p "$PGPORT" -U "$PGUSER" -tc \
    "SELECT 1 FROM pg_database WHERE datname = '$PGDATABASE'" | grep -q 1 || \
    psql -h "$PGHOST" -p "$PGPORT" -U "$PGUSER" -c "CREATE DATABASE $PGDATABASE"

echo "✓ PostgreSQL ready"

# -----------------------------------------------------------------------------
# 2. Neo4j
# -----------------------------------------------------------------------------
echo ""
echo "[2/4] Checking Neo4j..."

NEO4J_URI="${NEO4J_URI:-bolt://localhost:7687}"
NEO4J_USER="${NEO4J_USER:-neo4j}"
NEO4J_PASSWORD="${NEO4J_PASSWORD:-pegscanner}"

# 从 URI 提取 host:port
NEO4J_HOST=$(echo "$NEO4J_URI" | sed -E 's|.*://([^:/]+).*|\1|')
NEO4J_PORT=$(echo "$NEO4J_URI" | sed -E 's|.*:([0-9]+).*|\1|')
NEO4J_PORT="${NEO4J_PORT:-7687}"

# 等待 Neo4j 就绪
echo "Waiting for Neo4j at $NEO4J_HOST:$NEO4J_PORT..."
for i in {1..30}; do
    if nc -z "$NEO4J_HOST" "$NEO4J_PORT" 2>/dev/null; then
        echo "Neo4j port is open!"
        sleep 2  # 额外等待服务完全启动
        break
    fi
    echo "Attempt $i/30..."
    sleep 2
done

# 获取 prefix
PREFIX="${DB_TABLE_PREFIX:-dev_}"

# 创建 constraints 和 indexes
echo "Creating Neo4j constraints and indexes (prefix: $PREFIX)..."

# 使用 cypher-shell 或 Python
if command -v cypher-shell &>/dev/null; then
    cypher-shell -a "$NEO4J_URI" -u "$NEO4J_USER" -p "$NEO4J_PASSWORD" <<EOF
// Company
CREATE CONSTRAINT IF NOT EXISTS FOR (n:${PREFIX}Company) REQUIRE n.symbol IS UNIQUE;
CREATE INDEX IF NOT EXISTS FOR (n:${PREFIX}Company) ON (n.name);

// DailyQuote
CREATE INDEX IF NOT EXISTS FOR (n:${PREFIX}DailyQuote) ON (n.date);

// EarningsReport
CREATE INDEX IF NOT EXISTS FOR (n:${PREFIX}EarningsReport) ON (n.fiscal_quarter);

// NewsArticle
CREATE CONSTRAINT IF NOT EXISTS FOR (n:${PREFIX}NewsArticle) REQUIRE n.url IS UNIQUE;
CREATE INDEX IF NOT EXISTS FOR (n:${PREFIX}NewsArticle) ON (n.published_at);

// DataSource
CREATE CONSTRAINT IF NOT EXISTS FOR (n:${PREFIX}DataSource) REQUIRE n.name IS UNIQUE;

// PipelineBatch
CREATE CONSTRAINT IF NOT EXISTS FOR (n:${PREFIX}PipelineBatch) REQUIRE n.batch_id IS UNIQUE;
EOF
    echo "✓ Neo4j constraints created via cypher-shell"
else
    # Fallback: 使用 Python
    echo "cypher-shell not found, using Python..."
    cd "$PROJECT_ROOT/apps/backend"
    if [ -d ".venv" ]; then
        PYTHONPATH="$PROJECT_ROOT:$PROJECT_ROOT/libs:." .venv/bin/python -c "
from neo4j import GraphDatabase
import os

uri = os.environ.get('NEO4J_URI', 'bolt://localhost:7687')
user = os.environ.get('NEO4J_USER', 'neo4j')
password = os.environ.get('NEO4J_PASSWORD', 'pegscanner')
prefix = os.environ.get('DB_TABLE_PREFIX', 'dev_')

driver = GraphDatabase.driver(uri, auth=(user, password))

constraints = [
    f'CREATE CONSTRAINT IF NOT EXISTS FOR (n:{prefix}Company) REQUIRE n.symbol IS UNIQUE',
    f'CREATE INDEX IF NOT EXISTS FOR (n:{prefix}Company) ON (n.name)',
    f'CREATE INDEX IF NOT EXISTS FOR (n:{prefix}DailyQuote) ON (n.date)',
    f'CREATE INDEX IF NOT EXISTS FOR (n:{prefix}EarningsReport) ON (n.fiscal_quarter)',
    f'CREATE CONSTRAINT IF NOT EXISTS FOR (n:{prefix}NewsArticle) REQUIRE n.url IS UNIQUE',
    f'CREATE INDEX IF NOT EXISTS FOR (n:{prefix}NewsArticle) ON (n.published_at)',
    f'CREATE CONSTRAINT IF NOT EXISTS FOR (n:{prefix}DataSource) REQUIRE n.name IS UNIQUE',
    f'CREATE CONSTRAINT IF NOT EXISTS FOR (n:{prefix}PipelineBatch) REQUIRE n.batch_id IS UNIQUE',
]

with driver.session() as session:
    for cypher in constraints:
        try:
            session.run(cypher)
            print(f'  ✓ {cypher[:60]}...')
        except Exception as e:
            print(f'  ! {e}')

driver.close()
print('Done')
"
        echo "✓ Neo4j constraints created via Python"
    else
        echo "⚠ Skipped: no Python venv found. Run manually after setup."
    fi
fi

# -----------------------------------------------------------------------------
# 3. Django Migrations
# -----------------------------------------------------------------------------
echo ""
echo "[3/4] Running Django migrations..."

cd "$PROJECT_ROOT/apps/cms"

# 确保虚拟环境
if [ ! -d ".venv" ]; then
    echo "Creating virtual environment..."
    python3 -m venv .venv
    .venv/bin/pip install -r requirements.txt
fi

# 运行迁移
PYTHONPATH="$PROJECT_ROOT:." .venv/bin/python manage.py migrate --no-input

echo "✓ Django migrations complete"

# -----------------------------------------------------------------------------
# 4. Create superuser (可选)
# -----------------------------------------------------------------------------
echo ""
echo "[4/4] Django superuser..."

if [ -n "$DJANGO_SUPERUSER_USERNAME" ] && [ -n "$DJANGO_SUPERUSER_PASSWORD" ]; then
    echo "Creating superuser: $DJANGO_SUPERUSER_USERNAME"
    PYTHONPATH="$PROJECT_ROOT:." .venv/bin/python manage.py createsuperuser \
        --no-input \
        --username "$DJANGO_SUPERUSER_USERNAME" \
        --email "${DJANGO_SUPERUSER_EMAIL:-admin@example.com}" 2>/dev/null || \
        echo "(superuser may already exist)"
else
    echo "Skipped (set DJANGO_SUPERUSER_USERNAME and DJANGO_SUPERUSER_PASSWORD to create)"
fi

# -----------------------------------------------------------------------------
# Done
# -----------------------------------------------------------------------------
echo ""
echo "=== Initialization Complete ==="
echo ""
echo "Next steps:"
echo "  1. Start services: docker-compose up -d"
echo "  2. Access CMS admin: http://localhost:8001/admin/"
echo ""
