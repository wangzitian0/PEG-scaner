# PEG Scanner - Project Management

This directory contains files related to project management and tracking. Each major development phase or iteration will have its own subdirectory.

## Structure

- `phrase_i.xxxx/`: Each folder represents a distinct development phase and **must** contain at least:
  - `README.md`: objectives, deliverables, status, and next steps.
  - `plan.md`: goals, scope table, milestones, risks.
  - `iteration_flow.md`: daily/loop procedure (including reminders to read `AGENTS.md` + `docs/AI_EVALUATION.md` and update `project/prompt_log.md`).
  - `checklist.md`: trackable commitments tied to AGENTS/TODOWRITE.
  - `append_promot.md`: local snapshot of prompts pulled from `project/prompt_log.md`.
  - Any additional files (plans, tickets, appendices) relevant to that iteration.
- `regression_tests/`: Shared home for E2E verification scripts (see `regression_tests/README.md`) so infra-level tests stay outside individual packages.
- `scripts/`: Automation helpers such as `scripts/dev.sh` for starting/stopping services with env injection.

## Project Progress

### Phase 0: Proto & Nx Infrastructure
- **Phase Directory:** [`phrase_0.infra/`](./phrase_0.infra/README.md)
- **Scope:** SSOT schema management, proto code generation, Nx workspace/tooling upkeep.
- **Status:** Active (tracking infra items such as ping-pong verification).
- **Key Activities:**
    - Added backend `/api/ping/` endpoint with DRF test coverage; default `manage.py test` now runs the ping suite.
    - Surfaced backend status in the mobile app so Nx/Vite builds can confirm connectivity.
    - Introduced Nx targets (`backend:test`, `mobile:typecheck`) and `regression_tests/ping_pong.py` for shared automation.
    - Recorded infra prompts and plan/checklist under `phrase_0.infra/`.

### Phase 1: Initial Project Setup
- **Phase Directory:** [`phrase_1.initial_setup/`](./phrase_1.initial_setup/README.md)
- **Phase Description:** Setting up the basic project structure, documentation, and tooling as per `AGENTS.md`, and defining the backlog for data pipelines + UI/agent work.
- **Status:** In Progress
- **Key Activities:**
    - Created `TODOWRITE.md`
    - Updated `project/README.md`
    - Logged new prompts and set up iteration management files under `phrase_1.initial_setup/`
    - Captured baseline directory trees (root/project/backend/mobile) for structure audit
    - Ran backend `manage.py test` (currently reports 0 tests) to gauge automation gaps
    - Added `docs/AI_EVALUATION.md` and updated references (including latest `AGENTS.md` edits) so every agent follows the reward mechanism
