# Regression Tests

This directory hosts end-to-end (E2E) and integration tests that span multiple subsystems. Unit or module-level tests should stay inside their respective packages. By isolating regression assets here, we can automate checks without bloating individual projects.

## Available Tests

| Test | Description | Command |
|------|-------------|---------|
| `ping_pong.py` | Quick GraphQL `ping` query smoke test | `npx nx run regression:ping` |
| `graphql_e2e.py` | Full GraphQL E2E: ping, pegStocks, singleStock | `npx nx run regression:graphql-e2e` |
| `check_infra.js` | Neo4j + Backend + Vite reachability check | `npx nx run regression:infra-flow` |
| `run_web_e2e.js` | Full web E2E with Playwright | `npx nx run regression:web-e2e` |

## Usage

1. Make sure Podman/Docker is available (the scripts call `docker ...` under the hood; on Podman, the wrapper in `tools/bin/docker` will be used automatically).
2. The helper scripts manage Neo4j for you. To rely on an external instance set `SKIP_NEO4J_CONTAINER=1` and expose `NEO4J_URI/USER/PASSWORD`.
3. Run the regression test script(s) from the repo root and capture pass/fail logs under `x-log/` if running in CI.

Future regression suites (e.g., frontend automation that hits live APIs) should live beside this script, following the same documentation pattern.
