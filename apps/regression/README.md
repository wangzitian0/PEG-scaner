# Regression Tests

This directory hosts end-to-end (E2E) and integration tests that span multiple subsystems. Unit or module-level tests should stay inside their respective packages (e.g., Flask blueprints, React components). By isolating regression assets here, we can automate “ping-pong” style checks without bloating individual projects.

## Available Tests

| Test | Description | Command |
| --- | --- | --- |
| `ping_pong.py` | Verifies the backend `/api/ping/` endpoint responds with the expected payload. Ensures infra connectivity before frontends rely on it. | `./apps/backend/.venv/bin/python3 apps/regression/ping_pong.py` or `npx nx run regression:ping` (backend server must be running) |
| `check_infra.js` | Spins up backend + Vite web servers, waits for both to respond, then shuts them down. | `npx nx run regression:infra-flow` |
| `run_web_e2e.js` | Builds the mobile web bundle, starts backend + Vite preview, runs Playwright against the production bundle, then cleans up. | `npx nx run regression:web-e2e` |

## Usage

1. Start the backend (for `regression:ping`) or let the script spawn it (`infra-flow` / `web-e2e`).
2. Run the regression test script(s) from the repo root.
3. Capture pass/fail logs under `x-log/` if running in CI.

Future regression suites (e.g., frontend automation that hits live APIs) should live beside this script, following the same documentation pattern.
