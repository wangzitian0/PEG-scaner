# Phase 1 Plan – Single Stock Page

## Goals

1. **Process Enablement:** Make sure prompts, requirements, and progress are captured so future agents can resume work instantly.
2. **Architecture Readiness:** Validate the monorepo wiring (Nx, schema ownership, backend/mobile alignment) and list gaps.
3. **Data + AI Preparation:** Define how K-line, F10, news, and factor data will be ingested, verified (3-source rule), and exposed to agents.

## Scope

| # | Work Package | Description | Owner | Status |
|---|--------------|-------------|-------|--------|
| 1 | Prompt Logging | Keep `../prompt_log.md` and iteration logs up to date (single source). | Codex | Completed |
| 2 | Iteration Docs | Maintain plan/checklist/flow files for this phase. | Codex | Completed |
| 3 | Data Source Blueprint | List candidate vendors/APIs for K-line, news, F10, factors, and describe verification workflow. | Codex | Todo |
| 4 | Schema Alignment | Map `libs/schema/stock.proto` messages to backend/mobile consumers; note missing structures. | Codex | Todo |
| 5 | Agent Reward Design | Draft reward signals for future agents (quality, coverage, data verification). | Codex | Completed |
| 6 | Single Stock Data Flow | Define data sources (K-line, news, F10) and API contracts for single-stock view. | Codex | Completed (proto + endpoint in place) |
| 7 | UI Skeleton | Design and scaffold single-stock UI (charts/news placeholders) in the mobile app. | Codex | Completed (watchlist + detail view with proto decoding) |
|11 | Crawler + Neo4j | Bootstrap crawler app, admin surface, and Neo4j-backed data pipeline feeding the single stock page. | Codex | Completed |
| 8 | Evaluation Adoption | Enforce AI_EVALUATION doc via `AGENTS.md` and iteration docs; keep in sync when `AGENTS.md` changes. | Codex | In Progress |
| 9 | Execution Tracking | Update `../README.md`, `docs/README.md`, and `docs/TODOWRITE.md` as milestones complete. | Codex | In Progress |
|10 | Baseline Snapshot | Capture repo trees and run backend smoke tests to understand current health. | Codex | Completed |

## Milestones

- **M1:** Prompt log and iteration scaffolding in place. *(Today)*
- **M2:** Data source blueprint + schema gap analysis approved.
- **M3:** Initial implementation tickets derived for backend/mobile (K-line fetcher, PEG calculator, UI stubs).

## Dependencies

- Access to existing backend/mobile codebases.
- Agreement on data vendors or APIs (may require credentials).
- Availability of verification tooling (browser automation/manual check).

## Risks & Mitigations

- **Risk:** Data vendors unavailable or rate-limited.  
  **Mitigation:** Prepare multiple candidates and caching rules in blueprint.
- **Risk:** Documentation drift.  
  **Mitigation:** Lock process via checklist and enforce README updates.
- **Risk:** Reward mechanism unclear.  
  **Mitigation:** Draft concrete metrics (test coverage, requirement completion, data verification count) before coding tasks start.
