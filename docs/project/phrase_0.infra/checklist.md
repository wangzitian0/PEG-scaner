# Phase 0 Checklist

- [x] Confirm `schema/stock.proto` matches current backend/mobile requirements（新增 PingResponse 并驱动 FE/BE 使用 protobuf）.
- [x] Run `nx run backend:generate-proto` and store logs（参见 Phase 0 notes与命令输出）。
- [x] Document proto usage in backend/mobile READMEs（新增 protobuf 说明与命令引用）。
- [x] Audit `nx.json` + project configs for required targets (install, start, test, etc.). Added backend `test`, mobile `typecheck`, regression `ping`.
- [x] Add instructions for adding new Nx projects/modules（见 Phase 0 README 的 “Adding a New Nx Project”）。
- [x] Track infra-related prompts in `append_promot.md`.
- [x] Implement and verify ping-pong flow (backend `/api/ping/`, frontend 1px status indicator, regression script `apps/regression/ping_pong.py`, automated tests via `manage.py test stock_research`).
