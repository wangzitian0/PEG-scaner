# PEG Scanner Backend

FastAPI + Strawberry GraphQL backend for the PEG Scanner application.

## Architecture (BRN-002)

- **Framework**: FastAPI + Strawberry GraphQL (migrated from Flask + Ariadne)
- **Database**: Neo4j via neomodel
- **Structure**: Three-layer architecture (Resolver → Service → Repository)

## Directory Structure

```
apps/backend/
├── __init__.py
├── main.py              # FastAPI entry point
├── config.py            # Settings re-export
├── resolvers/           # Strawberry GraphQL resolvers
│   ├── __init__.py      # Merged Query type
│   ├── ping.py          # Ping/health check
│   └── stock.py         # Stock/market domain
├── services/            # Business logic layer
│   ├── __init__.py
│   ├── stock_service.py
│   └── seed.py          # Sample data for dev
├── tests/               # Pytest suite
│   ├── conftest.py
│   └── test_graphql.py
├── requirements.txt
├── project.json         # Nx targets
└── README.md
```

## Commands

All commands run from repo root:

```bash
# Install dependencies
npx nx run backend:install

# Start dev server (with hot reload)
npx nx run backend:start
# or directly:
PYTHONPATH=apps/backend:libs:. uvicorn apps.backend.main:app --reload --port 8000

# Run tests
npx nx run backend:test
```

## Environment Variables

| Variable | Default | Description |
|----------|---------|-------------|
| `NEO4J_URI` | `bolt://localhost:7687` | Neo4j connection URI |
| `NEO4J_USER` | `neo4j` | Username |
| `NEO4J_PASSWORD` | `pegscanner` | Password |
| `NEO4J_DATABASE` | (default) | Database name |
| `DB_TABLE_PREFIX` | `dev_` | Node label prefix |
| `API_CORS_ORIGINS` | localhost:5173,5174 | CORS origins |
| `PEG_AGENT_NAME` | `pegscanner-backend` | Agent identifier |

## API Endpoints

- `GET /` - Root status endpoint
- `POST /graphql` - GraphQL API
- `GET /graphql` - GraphQL Playground (dev only)

### GraphQL Queries

```graphql
# Health check
query { ping { message agent timestampMs } }

# PEG candidates list
query { pegStocks { symbol name pegRatio } }

# Single stock page
query ($symbol: String!) {
  singleStock(symbol: $symbol) {
    stock { symbol name companyInfo { sector } }
    dailyKline { timestamp open high low close volume }
    news { title url source publishedAt }
  }
}
```

## Migration Notes (BRN-002)

Migrated from Flask + Ariadne to FastAPI + Strawberry (2024-11-30):

- **Why**: Strong typing, dataclass resolvers, better async support, Pydantic integration
- **Compatibility**: Same GraphQL schema, same test coverage

See [TRD-002](../../docs/specs/tech/TRD-002.strawberry_fastapi.md) for detailed documentation.
