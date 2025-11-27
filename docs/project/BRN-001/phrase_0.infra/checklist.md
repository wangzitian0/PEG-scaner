# Phase 0 Checklist

- [x] GraphQL schema (`libs/schema/schema.graphql`) covers ping/pegStocks/singleStock needs（FE/BE/回归统一，禁止 ad-hoc JSON）。
- [x] Remove protobuf codegen flow，转为直接加载 GraphQL SDL。
- [x] Document GraphQL usage in backend/mobile READMEs。
- [x] Audit `nx.json` + project configs for required targets (install, start, test, etc.). Added backend `test`, mobile `typecheck`, regression `ping`.
- [x] Add instructions for adding new Nx projects/modules（见 Phase 0 README 的 “Adding a New Nx Project”）。
- [x] Track infra-related prompts in `append_promot.md`.
- [x] Implement and verify ping-pong flow via GraphQL (`/graphql` ping)，frontend 1px 状态指示器，回归脚本 `apps/regression/ping_pong.py`。
- [x] Add `regression:infra-flow` (spawns backend + Vite servers, hits ping + web root) to guard three-end connectivity.
- [x] Add Playwright-based regression (`regression:web-e2e`) that auto-installs browsers, spins up backend + Vite, and asserts the 1px indicator reflects backend reachability.
