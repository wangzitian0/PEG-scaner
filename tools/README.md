# Tools

Shared automation helpers for the PEG Scanner monorepo.

| Script | Description |
| --- | --- |
| [`dev.sh`](./dev.sh) | One-click start/stop wrapper for backend/mobile services. Reads `$ENV` to load env vars, runs commands under `nohup`, and stores logs/PIDs in `x-log/`. Usage: `ENV=.env.dev ./tools/dev.sh start [backend|mobile ...]` and `./tools/dev.sh stop`. |
| [`lint_structure.sh`](./lint_structure.sh) | Verifies the root layout (allowed directories/files, required READMEs). Run via `npm run lint:structure`; CI executes this before tests. |

Add future scripts here (linting, structure checks, data loaders) so every agent knows where to find automation entry points.
