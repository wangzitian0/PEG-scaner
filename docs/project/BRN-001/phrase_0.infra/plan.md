# Phase 0 Plan – GraphQL & Nx Infrastructure

| # | Work Package | Description | Owner | Status |
|---|--------------|-------------|-------|--------|
| 1 | Schema Governance | Maintain `libs/schema/schema.graphql` definitions and documentation（SSOT, no ad-hoc JSON）。 | Codex | Pending |
| 2 | Nx Workspace Health | Keep `nx.json`, per-project configs, and shared targets up to date. | Codex | Pending |
| 3 | Resolver & Client Alignment | Ensure backend resolvers / frontend GraphQL consumers stay aligned with SDL. | Codex | Pending |
| 4 | Infra Documentation | Document how other phases consume GraphQL/Nx (README updates). | Codex | Completed |
| 5 | Nx Targets | Add backend test target, mobile typecheck target, regression ping target. | Codex | Completed |
| 6 | Tooling Verification | Regularly run `nx graph`, lint, and smoke tests to validate infra（documented via tools/dev.sh + regression targets). | Codex | Completed |
| 7 | Ping-Pong Flow | Backend `/graphql` ping, mobile indicator, regression script `apps/regression/ping_pong.py`. | Codex | Completed |

## Milestones

- **M0:** Phase established with documentation placeholders (this commit).
- **M1:** GraphQL schema established并被前后端/回归共用。
- **M2:** Nx targets formalized for backend/mobile/test flows.

## Risks

- Schema drift between components（SDL 与实现/客户端不一致）。
- Nx executor changes causing regressions.

## Mitigations

- Keep schema changes isolated to this phase, with explicit notifications to dependent phases; run regression ping after SDL 变更。
- Document Nx command usage/examples in `iteration_flow.md`.
