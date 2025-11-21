# PEG Scanner - Project Documentation

This directory contains high-level project documentation, including the overall project plan, architectural decisions, and development phases.

## Index

- [Project Plan](./PLAN.md) - Outlines the major features and development phases.
- [Architecture](./ARCHITECTURE.md) - Describes the overall architecture of the system.
- [AI Evaluation](./AI_EVALUATION.md) - Defines the mandatory reward/score mechanism every agent must follow; keep in sync with any `AGENTS.md` updates.

## Overall Project Goal

To build an AI-native stock analysis tool for quantitative stock selection, primarily focusing on US stocks, with a React Native frontend and a Python backend. The application aims to provide comprehensive stock information, custom factor calculation, intelligent data management, and an AI-powered conversational interface for strategy creation and push notifications.

## Project Progress

### Phase 1: Initial Project Setup
- **Status:** In Progress
- **Description:** Establishing the foundational project structure, documentation, and basic management tools.
- **Key Achievements:**
    - Created `docs/TODOWRITE.md` to track all requirements.
    - Updated `docs/project/README.md` for detailed project phase tracking.
    - Established `docs/project/prompt_log.md` as the single prompt log per new instruction.
    - Created `docs/project/phrase_1.initial_setup/` to hold micro-iteration plans, flows, and checklists.
    - Created `docs/project/phrase_0.infra/` for proto/Nx infrastructure work.
    - Updated root `README.md` with an enhanced directory index.
    - Verified existence of `x-data/` and `x-log/` directories.
    - Captured repository tree snapshots (root/apps/backend + apps/mobile) and ran `apps/backend/manage.py test` (0 tests) to understand the current baseline.
    - Authored `docs/AI_EVALUATION.md` and updated `AGENTS.md` to enforce the agent reward mechanism.
    - Added Phase 0 ping-pong flow (backend `/api/ping/` + mobile 1px status indicator + tests) to validate infra connectivity using shared protobuf contracts.
    - Created `apps/regression/` for centralizing end-to-end scripts (currently `ping_pong.py`).
    - Wired Nx targets (`backend:test`, `mobile:typecheck`, `regression:ping`) so infra checks can run via `nx run ...`.
    - Added `tools/dev.sh` for environment-aware start/stop automation.
- **Next Steps:** Execute the backlog defined in `docs/project/phrase_1.initial_setup/plan.md`, starting with the evaluation mechanism rollout, data-source blueprinting, and schema alignment before UI/data feature coding.
