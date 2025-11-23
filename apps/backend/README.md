# PEG Scanner - Flask Backend

This directory now hosts the Flask + Neo4j backend that powers the ping/pong infra, the PEG stock table, the single stock page (protobuf), and the crawler/admin workflows.

## Structure

- `src/pegserver/`: Flask application factory, API blueprint, CLI, Flask-Admin view, crawler helpers, and the graph store that talks to Neo4j through `neomodel`.
- `src/manage.py`: Flask CLI entrypoint used by Nx (`run`, `crawler-run`, etc.).
- `proto/generated/`: Python code generated from the protobuf contracts in `libs/schema`.
- `tests/`: Pytest suite that exercises the API via the Flask test client (defaults to the in-memory fake store so CI does not need Neo4j).
- `requirements.txt`: Runtime + tooling dependencies (Flask, Flask-Admin, neomodel, grpc tools, yfinance, pytest).

## Commands

All commands run from the repo root:

```bash
# Install python deps + node modules + proto bindings
npx nx run backend:install
npx nx run backend:generate-proto

# Start the dev stack (Neo4j container + backend + Metro + Vite)
npm run dev
# or only the backend with live reload
npx nx run backend:start

# Run backend tests (uses the fake in-memory graph)
npx nx run backend:test

# Run a crawler job (live yfinance or sample fallback)
PYTHONPATH=apps/backend/src:apps/backend/proto/generated:. ./apps/backend/.venv/bin/python3 \
  apps/backend/src/manage.py crawler-run --symbol AAPL --live
```

The CLI also exposes `crawler-job` for seeding Flask-Admin jobs:

```bash
PYTHONPATH=apps/backend/src:apps/backend/proto/generated:. ./apps/backend/.venv/bin/python3 \
  apps/backend/src/manage.py crawler-job --symbol AAPL --name "Live AAPL" --metadata "source=yfinance"
```

## Configuration

Environment variables are read via `pegserver.config.Settings`:

- `NEO4J_URI` / `NEO4J_USER` / `NEO4J_PASSWORD` / `NEO4J_DATABASE` – connection info for Neo4j (defaults match the Podman container started by `tools/envs/manage.py`).
- `NEO4J_DATA_DIR` – host directory mounted into the managed Neo4j container (defaults to `x-data/neo4j/`) so dev + CI can persist the graph between runs.
- `DB_TABLE_PREFIX` – label prefix (defaults to `dev_` or `prod_`) so dev/prod graphs never clash. Tracking events, stock documents, and crawler jobs respect the prefix.
- `API_CORS_ORIGINS` – comma-separated list of allowed origins for `/api/*`.
- `NEO4J_FAKE=1` – enables the lightweight in-memory graph store (used only by tests/regression scripts).

## Features

- `/api/ping/` – protobuf ping response that also writes a `TrackingRecord` node. The tests assert that each call succeeds and serializes correctly.
- `/api/peg-stocks/` – JSON list derived from the latest stock documents, including derived PEG ratios.
- `/api/single-stock-page/?symbol=XYZ` – protobuf payload built from Neo4j (crawler data first, seeded fallbacks if necessary).
- `/admin/` – Flask-Admin console that lists crawler jobs and lets you trigger them. Jobs execute via yfinance when available or synthetic payloads for demos.
- CLI commands (`crawler-run`, `crawler-job`) to wire automation and CI scripts without touching the UI.

Read `AGENTS.md` / `docs/project/**/README.md` before editing any folder so we preserve the agreed layout and infra standards.
