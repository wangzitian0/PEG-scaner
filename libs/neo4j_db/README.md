# libs/neo4j_db

Shared Neo4j access layer for the PEG Scanner monorepo.

## Responsibilities

- Create and cache the Neo4j driver according to `NEO4J_*` environment settings (reads from Flask settings when available; otherwise looks at environment variables).
- Provide simple helpers for upserting/fetching stock documents (`upsert_stock_document`, `fetch_stock_document`) so backend apps don’t need to reimplement Cypher queries.
- Serve as the central place to extend graph persistence (e.g., future M7 nodes for strategies, relationships between stocks, etc.).

All backend code that needs Neo4j should import from this package instead of creating ad-hoc drivers.
