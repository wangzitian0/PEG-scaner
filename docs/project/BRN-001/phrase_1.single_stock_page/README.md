# Phase 1 – Single Stock Page

This iteration focuses on delivering the end-to-end single-stock experience (UI + backend data plumbing) per `AGENTS.md`, leveraging the completed infra work from Phase 0.

## Objectives

- Capture every user prompt and instruction so downstream work remains auditable.
- Define the scope, backlog, and quality gates for the single-stock page (data fetch, UI rendering, chart/news placeholders).
- Outline the day-to-day workflow so that new work items can be prioritized quickly.

## Deliverables

- `plan.md`: Goals, scope, and prioritized backlog for the single-stock page.
- `iteration_flow.md`: Daily operating procedure for this phase.
- `checklist.md`: Trackable list of commitments tied to `AGENTS.md`.
- `append_promot.md`: Prompts that influence this iteration, extracted from the global log.

## Status

- **State:** In Progress
- **Iteration Lead:** Codex (AI Agent)
- **Timebox:** Until the single-stock detail view is functional (backend endpoints, proto wiring, UI skeleton, verification).

## Next Steps

1. Refine the backlog in `plan.md` with concrete work packages (single-stock data flow, UI mock scopes, chart/news placeholders).
2. Sequence the tasks via `iteration_flow.md` and start executing the first checklist items.
3. Report progress back to `../README.md` and `docs/index.md` as milestones are hit.
4. Enforce the AI evaluation mechanism across all agents before starting new technical work, updating references whenever `AGENTS.md` changes.

## Baseline Findings (2025-02-14)

- Repository structure captured via `tree` for root, `docs/project/`, `apps/backend/`, and `apps/mobile/`.
- `backend/manage.py test` currently reports “Ran 0 tests”, so automated coverage remains to be implemented.
