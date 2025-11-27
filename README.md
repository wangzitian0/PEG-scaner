# PEG Scanner

This project is a stock analysis tool for quantitative stock selection, focusing on US stocks. It is being developed using an "AI-native" approach, where an AI agent (like me) actively participates in the development process.

The core requirements and instructions for the agent are defined in [AGENTS.md](./AGENTS.md).

## Installation

To set up the Nx monorepo workspace, navigate to the project's root directory and run the following command:

```bash
npx nx init peg-scanner --prefer-free-syntax
```

This command will initialize the Nx workspace directly within the current directory, naming it `peg-scanner`. Follow any prompts to configure the workspace. It's recommended to choose an "integrated" monorepo style for mixed technologies (React Native and Python).

### System prerequisites

You need the following tools installed on the host (not provided automatically by Nx):
- Docker or Podman (daemon/machine running) — used by regression scripts to start Neo4j (`neo4j:5`).
- Python 3.9+ — backend virtualenv is created via `nx run backend:install`.
- Node.js + npm — front-end tooling and Nx CLI (`npm install`).

Rationale: keeping Python/Node on the host keeps dev/test fast (Nx targets spawn local processes). Only Neo4j runs in a container during regressions; if you prefer full containerization for backend/frontend too, add a compose stack, but the current flow expects host Python/Node.

### Dependency boundaries (to avoid cross-app leaks)
- JS/TS: A single root `package.json`/`package-lock.json` is used for all apps/libs. Use Nx tags and `nx lint` (with dep-graph rules) to prevent forbidden imports (e.g., FE code pulling BE-only utilities). Add tags in each `project.json` and enforce with `nx.json` `implicitDependencies`/`namedInputs`/`targetDefaults` as needed.
- Python: Backend and future Python libs share one venv via `nx run backend:install` unless a library has conflicting deps (then create a dedicated requirements/venv and target). Keep imports layered (libs -> apps), not the reverse.
- Data/SSOT: Contracts live in `libs/schema/schema.graphql`; no ad-hoc JSON. Backend/FE/regression consume the same SDL to prevent drift.

### Production API domains
- Frontend defaults to `window.location.origin/graphql` on web. To force an API domain (e.g., `https://api.truealpha.club/graphql`), set `PEG_GRAPHQL_URL` at build/runtime.
- Ensure Cloudflare/your reverse proxy routes `/graphql` to the backend service.

## Development Workflow

1. Run `npm run lint:structure` to ensure the workspace layout remains compliant.
2. Start the full stack (Neo4j via Docker, Flask backend, Metro, Vite) with **one command**:
   ```bash
   npm run dev
   ```
   Requirements: Docker CLI (for the Neo4j container). The script lints the repo, clears Vite cache, boots a `neo4j:5` container (configurable via `NEO4J_CONTAINER`, `NEO4J_HTTP_PORT`, `NEO4J_BOLT_PORT`, `NEO4J_AUTH`, `NEO4J_DOCKER_IMAGE`), and spawns `nx run backend:start`, `nx run mobile:start`, and `nx run mobile:serve`. Hit `Ctrl+C` to gracefully terminate everything, including the Neo4j container.
3. Run automated checks while servers are running:
   - Backend GraphQL tests: `npx nx run backend:test`
   - Regression ping: `npx nx run regression:ping` (backend server must be running)
   - Infra E2E (backend + web reachability): `npx nx run regression:infra-flow`
   - Full web E2E (backend + Vite + Playwright): `npx nx run regression:web-e2e`
   - Mobile typecheck: `npx nx run mobile:typecheck`
4. For manual control or headless environments, use `./tools/dev.sh start|stop [backend|mobile …]`; logs/PIDs live under `x-log/`.

## Crawler + Neo4j

The crawler stores graph-shaped stock metadata inside Neo4j and feeds the single stock page.

1. Run Neo4j locally (default URI `bolt://localhost:7687`, user/password `neo4j/pegscanner`, override via `NEO4J_URI`, `NEO4J_USER`, `NEO4J_PASSWORD`). All scripted environments mount data under `x-data/neo4j/` so containers can be started/stopped freely without data loss.
2. Manage crawler jobs with Flask-Admin at `http://127.0.0.1:8000/admin/` or via the CLI:
   ```bash
  PYTHONPATH=apps/backend/src:. ./apps/backend/.venv/bin/python3 \\
     apps/backend/src/manage.py crawler-job --symbol AAPL --name \"AAPL Live\" --metadata \"source=yfinance\"
   ```
3. Execute a job to seed Neo4j (crawler fetches live data via `yfinance`; falls back to a synthetic payload if Yahoo Finance is unreachable):
   ```bash
   npx nx run backend:install
  PYTHONPATH=apps/backend/src:. ./apps/backend/.venv/bin/python3 \\
     apps/backend/src/manage.py crawler-run --symbol AAPL --live
   ```
4. Visit `http://localhost:5173/?symbol=AAPL` – the single stock page reads the GraphQL payload straight from Neo4j (news, K-line, metadata, valuations).

## Environment Tools

Following Nx best practices, environment helpers live under `tools/envs/manage.py`:

- `npm run dev` → `python3 tools/envs/manage.py dev` (lint + clear cache + Neo4j Docker + backend + Metro + Vite; stops everything when command exits).
- `python3 tools/envs/manage.py start` → production-oriented start (Neo4j Docker + backend runserver + production Vite preview, PID files under `x-log/`).
- `python3 tools/envs/manage.py restart` → graceful restart for production (sends SIGTERM, waits, then relaunches).
- `python3 tools/envs/manage.py bootstrap-dev` / `bootstrap-prod` → install dependencies and prep virtualenvs for dev/prod.
- `python3 tools/envs/install_system.py` → check/install system-level prerequisites (Node, npm, Python, Docker). Add `--apply` to execute the recommended package-manager commands automatically (requires proper privileges).

## Continuous Integration

GitHub Actions (`.github/workflows/ci.yml`) runs on every push/PR:

- `backend:test` for GraphQL/API units.
- `regression:infra-flow` which boots a disposable Neo4j container (`pegscanner_ci_neo4j`, data stored under `x-data/neo4j/`), the Flask backend, and Vite dev server to assert connectivity.
- `regression:web-e2e` which builds the web bundle and executes the Playwright ping indicator test against the running services.
- `mobile:typecheck` to keep the RN project healthy.

Use `NEO4J_DATA_DIR` if CI runners need Neo4j data somewhere else (defaults to `x-data/neo4j/`).

## Directory Index

*   [`/docs/`](./docs/README.md): High-level documentation, with navigation at `docs/index.md`, architecture at `docs/arch.md`, immutable inputs under `docs/origin/`, specs under `docs/specs/`, and the active project state under `docs/project/BRN-001/`.
*   [`/apps/`](./apps/README.md): Runtime applications (backend API, mobile client, regression utilities) managed by Nx.
*   [`/libs/schema/`](./libs/schema/README.md): The Single Source of Truth (SSOT) for data structures, defined using GraphQL SDL.
*   [`/tools/`](./tools/README.md): Automation helpers such as [`tools/dev.sh`](./tools/dev.sh) for starting/stopping services with env injection.
*   [`/x-data/`](./x-data/README.md): Stores all data automatically generated by the application (e.g., stock data, calculated factors).
*   [`/x-log/`](./x-log/README.md): Contains logs from the application's various components.
*   [`docs/specs/product/PRD-001.md`](./docs/specs/product/PRD-001.md): Product requirements + functional backlog.
*   [`AGENTS.md`](./AGENTS.md): SOP/checklists and workflow guardrails for every agent (read before making any change).

## Root Files

- `package.json` / `package-lock.json`: Node + Nx dependencies and scripts (e.g., `npm run lint:structure`).
- `nx.json` / `tsconfig.base.json`: Nx workspace + shared TypeScript compiler configuration.
- `.gitignore`, `.prettierrc`, `.prettierignore`: SCM and formatting policies.
- `nx` / `nx.bat`: Nx CLI entry points.
