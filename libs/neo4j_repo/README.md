# libs/neo4j_repo

Shared Neo4j data access layer for the PEG Scanner monorepo.

## Directory Structure

```
libs/neo4j_repo/
├── __init__.py           # Public exports
├── connection.py         # Settings & connection management
├── repositories/
│   ├── __init__.py
│   └── stock_repository.py   # Stock data CRUD
├── models/
│   ├── __init__.py
│   └── stock.py          # neomodel node definitions
└── README.md
```

## Usage

### Basic Usage

```python
from neo4j_repo import StockRepository

repo = StockRepository()

# Upsert stock data
repo.upsert_stock_payload({
    "symbol": "AAPL",
    "name": "Apple Inc.",
    "sector": "Technology",
    "daily_kline": [...],
    "news": [...]
})

# Fetch stock data
payload = repo.fetch_stock_payload("AAPL")

# List PEG candidates
candidates = repo.list_peg_candidates()
```

### FastAPI Integration

```python
from fastapi import FastAPI
from neo4j_repo import lifespan

app = FastAPI(lifespan=lifespan)
```

## Environment Variables

| Variable | Default | Description |
|----------|---------|-------------|
| `NEO4J_URI` | `bolt://localhost:7687` | Neo4j connection URI |
| `NEO4J_USER` | `neo4j` | Username |
| `NEO4J_PASSWORD` | `pegscanner` | Password |
| `NEO4J_DATABASE` | (default) | Database name |
| `DB_TABLE_PREFIX` | `dev_` or `prod_` | Node label prefix |

## Architecture

```
StockRepository
    ↓
StockDocumentNode (neomodel)
    ↓
Neo4j Database
```
