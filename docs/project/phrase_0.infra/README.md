# Phase 0 – Infrastructure (Proto & Nx)

This phase captures all work related to the foundational tooling: protobuf schemas (SSOT for data contracts) and Nx monorepo orchestration. Any task involving schema evolution, proto compilation, Nx workspace wiring, or infra scripts must be scoped here before higher phases depend on it.

## Objectives

- Maintain protobuf definitions (`schema/`) and codegen rules consistently across backend/mobile/services.
- Keep Nx configuration (workspace setup, project.json files, shared generators) in a ready-to-use state for subsequent phases.
- Provide onboarding notes/checklists so future phases can reuse infra without rediscovery.
- Host shared regression tests (see `apps/regression/`) for infra-level health checks.

## Deliverables

- `plan.md`: roadmap of pending proto/Nx enhancements or maintenance.
- `iteration_flow.md`: how to operate within this phase (schema updates, Nx commands, verification).
- `checklist.md`: concrete tasks (e.g., ensure proto compiles, Nx targets exist, docs updated).
- `append_promot.md`: prompts impacting infra decisions (mirrored from `../prompt_log.md`).

## Status

- **State:** Active
- **Scope Owner:** Codex (AI Agent)
- **Dependencies:** `schema/`, `nx.json`, `apps/backend/project.json`, `apps/mobile/project.json`, `apps/regression/`, and future shared libraries.

## Notes

- When schema files change, run the codegen target noted in `apps/backend/project.json` and capture results in `x-log/`.
- Nx upgrades or new executors should be documented here before touching app-specific phases.
- Ping-pong verification (backend `/api/ping/` + mobile 1px status indicator) lives here because it validates the infra stack end-to-end before higher-level features rely on it; the regression script is in `apps/regression/ping_pong.py`.
- Use `tools/dev.sh start|stop` for a one-click lifecycle; it loads env vars from `$ENV` before launching backend/mobile services.

## Adding a New Nx Project

1. Run `npx nx g @nx/js:library <name>` (or the relevant generator) from the repo root.
2. Keep the generated `project.json` beside the new code, mirroring the backend/mobile layout.
3. Add required targets (install/start/test/typecheck) immediately so `tools/dev.sh` and CI can reference them.
4. Update `../README.md` and the appropriate phase README to describe the new module.
