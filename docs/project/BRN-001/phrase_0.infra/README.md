# Phase 0 – Infrastructure (GraphQL & Nx)

This phase captures all work related to the foundational tooling: GraphQL schema (SSOT for data contracts) and Nx monorepo orchestration. Any task involving schema evolution, schema loading, Nx workspace wiring, or infra scripts must be scoped here before higher phases depend on it.

## Objectives

- Maintain GraphQL schema definitions (`libs/schema/schema.graphql`) and loading rules consistently across backend/mobile/services.
- Keep Nx configuration (workspace setup, project.json files, shared generators) in a ready-to-use state for subsequent phases.
- Provide onboarding notes/checklists so future phases can reuse infra without rediscovery.
- Host shared regression tests (see `apps/regression/`) for infra-level health checks.

## Deliverables

- `plan.md`: roadmap of pending GraphQL/Nx enhancements or maintenance.
- `iteration_flow.md`: how to operate within this phase (schema updates, Nx commands, verification).
- `checklist.md`: concrete tasks (e.g., ensure schema stays SSOT, Nx targets exist, docs updated).
- `append_promot.md`: prompts impacting infra decisions (mirrored from `../prompt.md`).
- 关联 BRN：`docs/origin/BRN-002.md`（协议与通信依赖，对应 `docs/specs/tech/TRD-002.md`）。

## Status

- **State:** Active
- **Scope Owner:** Codex (AI Agent)
- **Dependencies:** `libs/schema/`, `nx.json`, `apps/backend/project.json`, `apps/mobile/project.json`, `apps/regression/`, and future shared libraries.

## Notes

- When schema files change, run the codegen target noted in `apps/backend/project.json` and capture results in `x-log/`.
- Nx upgrades or new executors should be documented here before touching app-specific phases.
- Ping-pong verification (backend `/graphql` ping + mobile 1px status indicator) lives here because it validates the infra stack end-to-end before higher-level features rely on it; the regression script is in `apps/regression/ping_pong.py`.
- `npm run dev` is the canonical single command for linting structure + launching backend, Metro, and Vite hot reloaders; fall back to `tools/dev.sh start|stop` only when you need manual service lifecycles or custom env injection.
- Infra regressions live under `apps/regression/`: `npx nx run regression:infra-flow` hits backend + Vite directly, while `npx nx run regression:web-e2e` brings up backend/Vite, auto-installs Playwright browsers, and verifies the ping indicator via headless Chromium.

## Adding a New Nx Project

1. Run `npx nx g @nx/js:library <name>` (or the relevant generator) from the repo root.
2. Keep the generated `project.json` beside the new code, mirroring the backend/mobile layout.
3. Add required targets (install/start/test/typecheck) immediately so `tools/dev.sh` and CI can reference them.
4. Update `../README.md` and the appropriate phase README to describe the new module.
