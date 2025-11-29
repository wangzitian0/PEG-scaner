# PEG Scanner - Project Management

> **职责**：迭代管理规范 + 当前 Phase 执行状态
> 
> **与 specs/tech/TRD-001.md 的关系**：`TRD-001.md` 是高层规划，本目录是执行记录

This directory contains files related to project management and tracking. Each major development phase or iteration will have its own subdirectory.

## Structure

- `phrase_i.xxxx/`: Each folder represents a distinct development phase and **must** contain at least:
  - `README.md`: objectives, deliverables, status, and next steps.
  - `plan.md`: goals, scope table, milestones, risks.
  - `iteration_flow.md`: daily/loop procedure (including reminders to read `AGENTS.md` + `../../../specs/infra/IRD-001.ai_evaluation.md` and update `./prompt.md`).
  - `checklist.md`: trackable commitments tied to AGENTS/todowrite.
  - `append_promot.md`: local snapshot of prompts pulled from `./prompt.md`.
  - BRN 对齐：业务请求存放于 `docs/origin/BRN-xxx.md`，执行产物放各自 BRN 目录（如 `../BRN-002/`, `../BRN-003/`）。
  - Any additional files (plans, tickets, appendices) relevant to that iteration.
- `../apps/`: Runtime apps live there; refer back when phases touch specific code.

## Project Progress

### Phase 0: Proto & Nx Infrastructure
- **Phase Directory:** [`phrase_0.infra/`](./phrase_0.infra/README.md)
- **Scope:** SSOT schema管理（GraphQL SDL），Nx workspace/tooling upkeep。
- **Status:** Active (tracking infra items such as ping-pong verification).
- **Key Activities:**
    - Added backend `/graphql` ping; default `backend:test` now runs the GraphQL ping suite.
    - Surfaced backend status in the mobile app so Nx/Vite builds can confirm connectivity.
    - Introduced Nx targets (`backend:test`, `mobile:typecheck`) and regression scripts (`ping_pong.py`, `check_infra.js`, `run_web_e2e.js`) for shared automation, including Playwright coverage of the ping indicator.
    - Recorded infra prompts and plan/checklist under `phrase_0.infra/`，关联 BRN-002（协议与通信依赖，对应 `docs/specs/tech/TRD-002.graphql_contracts.md`，原文在 `docs/origin/BRN-002.graphql_protocol_decision.md`）。
    - Authored `phrase_0.infra/deploy.md` as the Cloudflare+VPS TODOwrite with stepwise checks.

### Phase 1: Single Stock Page
- **Phase Directory:** [`phrase_1.single_stock_page/`](./phrase_1.single_stock_page/README.md)
- **Phase Description:** Implementing the single-stock experience (UI + data flow) per `AGENTS.md`, building on top of the initial infra.
- **Status:** In Progress
- **Key Activities:**
    - Created `project/BRN-001/todowrite.md`
    - Updated `project/BRN-001/README.md`
    - Logged new prompts and set up iteration management files under `phrase_1.single_stock_page/`，关联 BRN-003（对应 `docs/specs/product/PRD-001.stock_app_overview.md`，原文在 `docs/origin/BRN-003.single_stock_page.md`）。
    - Captured baseline directory trees (root/apps/backend + apps/mobile) for structure audit
    - Ran `apps/backend/manage.py test` (currently reports 0 tests) to gauge automation gaps
    - Added `specs/infra/IRD-001.ai_evaluation.md` and updated references (including latest `AGENTS.md` edits) so every agent follows the reward mechanism
