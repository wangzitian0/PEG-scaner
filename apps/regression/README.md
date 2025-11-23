# Regression Tests

This directory hosts end-to-end (E2E) and integration tests that span multiple subsystems. Unit or module-level tests should stay inside their respective packages (e.g., Flask blueprints, React components). By isolating regression assets here, we can automate “ping-pong” style checks without bloating individual projects.

## Available Tests

| Test | Description | Command |
| --- | --- | --- |
| `ping_pong.py` | Verifies the backend `/api/ping/` endpoint responds with the expected payload. Ensures infra connectivity before frontends rely on it. | `./apps/backend/.venv/bin/python3 apps/regression/ping_pong.py` or `npx nx run regression:ping` (backend server must be running) |
| `check_infra.js` | Spins up a disposable Neo4j container (`pegscanner_regression_neo4j`, data stored under `x-data/neo4j/`), launches the Flask backend and Vite dev server, and verifies they are reachable. | `npx nx run regression:infra-flow` |
| `run_web_e2e.js` | Builds the mobile web bundle, starts the Neo4j + backend stack, runs Playwright against the preview build, and then tears everything down. | `npx nx run regression:web-e2e` |

## Usage

1. Make sure Podman/Docker is available (the scripts call `docker ...` under the hood; on Podman, the wrapper in `tools/bin/docker` will be used automatically).
2. The helper scripts manage Neo4j for you. To rely on an external instance set `SKIP_NEO4J_CONTAINER=1` and expose `NEO4J_URI/USER/PASSWORD`.
3. Run the regression test script(s) from the repo root and capture pass/fail logs under `x-log/` if running in CI.

Future regression suites (e.g., frontend automation that hits live APIs) should live beside this script, following the same documentation pattern.
