# PEG Scanner - Project Management

> **职责**：迭代管理规范 + 当前 Phase 执行状态
> 
> **与 docs/PLAN.md 的关系**：`PLAN.md` 是高层规划，本目录是执行记录

This directory contains files related to project management and tracking. Each major development phase or iteration will have its own subdirectory.

## Structure

- `phrase_i.xxxx/`: Each folder represents a distinct development phase and **must** contain at least:
  - `README.md`: objectives, deliverables, status, and next steps.
  - `plan.md`: goals, scope table, milestones, risks.
  - `iteration_flow.md`: daily/loop procedure (including reminders to read `AGENTS.md` + `docs/AI_EVALUATION.md` and update `./prompt_log.md`).
  - `checklist.md`: trackable commitments tied to AGENTS/TODOWRITE.
  - `append_promot.md`: local snapshot of prompts pulled from `./prompt_log.md`.
  - Any additional files (plans, tickets, appendices) relevant to that iteration.
- `../apps/`: Runtime apps live there; refer back when phases touch specific code.

## Project Progress

### Phase 0: Proto & Nx Infrastructure
- **Phase Directory:** [`phrase_0.infra/`](./phrase_0.infra/README.md)
- **Scope:** SSOT schema management, proto code generation, Nx workspace/tooling upkeep.
- **Status:** Active (tracking infra items such as ping-pong verification).
- **Key Activities:**
    - Added backend `/api/ping/` endpoint with DRF test coverage; default `manage.py test` now runs the ping suite.
    - Surfaced backend status in the mobile app so Nx/Vite builds can confirm connectivity.
    - Introduced Nx targets (`backend:test`, `mobile:typecheck`) and regression scripts (`ping_pong.py`, `check_infra.js`, `run_web_e2e.js`) for shared automation, including Playwright coverage of the ping indicator.
    - Recorded infra prompts and plan/checklist under `phrase_0.infra/`.
    - Authored `phrase_0.infra/deploy.md` as the Cloudflare+VPS TODOwrite with stepwise checks.

### Phase 1: Single Stock Page
- **Phase Directory:** [`phrase_1.single_stock_page/`](./phrase_1.single_stock_page/README.md)
- **Phase Description:** Implementing the single-stock experience (UI + data flow) per `AGENTS.md`, building on top of the initial infra.
- **Status:** In Progress
- **Key Activities:**
    - Created `docs/TODOWRITE.md`
    - Updated `docs/project/README.md`
    - Logged new prompts and set up iteration management files under `phrase_1.single_stock_page/`
    - Captured baseline directory trees (root/apps/backend + apps/mobile) for structure audit
    - Ran `apps/backend/manage.py test` (currently reports 0 tests) to gauge automation gaps
    - Added `docs/AI_EVALUATION.md` and updated references (including latest `AGENTS.md` edits) so every agent follows the reward mechanism
