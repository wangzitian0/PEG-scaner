# Phase 0 Plan – Proto & Nx Infrastructure

| # | Work Package | Description | Owner | Status |
|---|--------------|-------------|-------|--------|
| 1 | Proto Governance | Maintain `libs/schema/` definitions, codegen rules, and documentation. | Codex | Pending |
| 2 | Nx Workspace Health | Keep `nx.json`, per-project configs, and shared targets up to date. | Codex | Pending |
| 3 | Codegen Automation | Ensure `nx run backend:generate-proto` integrates with CI/logging. | Codex | Pending |
| 4 | Infra Documentation | Document how other phases consume proto/Nx (README updates). | Codex | Completed |
| 5 | Nx Targets | Add backend test target, mobile typecheck target, regression ping target. | Codex | Completed |
| 6 | Tooling Verification | Regularly run `nx graph`, lint, and smoke tests to validate infra（documented via tools/dev.sh + regression targets). | Codex | Completed |
| 7 | Ping-Pong Flow | Backend `/api/ping/`, mobile indicator, regression script `apps/regression/ping_pong.py`. | Codex | Completed |

## Milestones

- **M0:** Phase established with documentation placeholders (this commit).
- **M1:** Proto codegen automation script validated (backend + future clients).
- **M2:** Nx targets formalized for backend/mobile/test flows.

## Risks

- Schema drift between components.
- Nx executor changes causing regressions.

## Mitigations

- Keep schema changes isolated to this phase, with explicit notifications to dependent phases.
- Document Nx command usage/examples in `iteration_flow.md`.
