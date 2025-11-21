# Tools

Shared automation helpers for the PEG Scanner monorepo.

| Script | Description |
| --- | --- |
| [`dev.sh`](./dev.sh) | One-click start/stop wrapper for backend + mobile services. Reads `$ENV` to load env vars, runs commands under `nohup`, and stores logs/PIDs in `x-log/`. Usage: `ENV=.env.dev ./tools/dev.sh start` and `./tools/dev.sh stop`. |

Add future scripts here (linting, structure checks, data loaders) so every agent knows where to find automation entry points.
