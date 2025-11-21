# Regression Tests

This directory hosts end-to-end (E2E) and integration tests that span multiple subsystems. Unit or module-level tests should stay inside their respective packages (e.g., Django apps, React components). By isolating regression assets here, we can automate “ping-pong” style checks without bloating individual projects.

## Available Tests

| Test | Description | Command |
| --- | --- | --- |
| `ping_pong.py` | Verifies the backend `/api/ping/` endpoint responds with the expected payload. Ensures infra connectivity before frontends rely on it. | `./apps/backend/.venv/bin/python3 apps/regression/ping_pong.py` or `npx nx run regression:ping` (backend server must be running) |

## Usage

1. Start the backend (e.g., `./apps/backend/.venv/bin/python3 apps/backend/manage.py runserver`).
2. Run the regression test script(s) from the repo root.
3. Capture pass/fail logs under `x-log/` if running in CI.

Future regression suites (e.g., frontend automation that hits live APIs) should live beside this script, following the same documentation pattern.
