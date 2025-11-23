# Tools

Shared automation helpers for the PEG Scanner monorepo.

| Script | Description |
| --- | --- |
| [`dev.sh`](./dev.sh) | Manual start/stop wrapper for backend/mobile services (useful on CI or when you only need one service). Reads `$ENV` to load env vars, runs commands under `nohup`, and stores logs/PIDs in `x-log/`. Usage: `ENV=.env.dev ./tools/dev.sh start [backend|mobile ...]` and `./tools/dev.sh stop`. |
| [`lint_structure.sh`](./lint_structure.sh) | Verifies the root layout (allowed directories/files, required READMEs). Run via `npm run lint:structure`; CI executes this before tests. |
| [`clear_vite_cache.js`](./clear_vite_cache.js) | Deletes `apps/mobile/node_modules/.vite` to avoid the “Outdated Optimize Dep” 504 issue. Automatically invoked by `npm run dev`, but can be run manually if Vite dev servers get stuck. |
| [`envs/manage.py`](./envs/manage.py) | Python CLI for environment management: `dev`, `start`, `restart`, `bootstrap-dev`, `bootstrap-prod`. Handles Neo4j Docker lifecycle, backend/Vite processes, and dependency prep. |
| [`envs/install_system.py`](./envs/install_system.py) | Checks for system-level dependencies (node/npm/python/docker) and prints install commands. Use `--apply` to run the suggested package-manager commands automatically on supported platforms. |

Add future scripts here (linting, structure checks, data loaders) so every agent knows where to find automation entry points.
