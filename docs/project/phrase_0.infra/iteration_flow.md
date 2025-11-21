# Iteration Flow – Phase 0 Infra

1. **Pre-work Checklist**
   - Read `AGENTS.md`, `docs/AI_EVALUATION.md`, `../prompt_log.md`.
   - Review open items in `checklist.md` (proto/Nx tasks).

2. **Execution Loop**
   - For proto changes: update `libs/schema/*.proto`, run `nx run backend:generate-proto`, inspect outputs under `apps/backend/stock_research/generated`.
   - For Nx tasks: edit configs, then run `npx nx graph` / `nx show project ...` / `nx run backend:test` / `nx run regression:ping` as needed.
   - Record command outputs/logs under `x-log/` if automated.

3. **Documentation Sweep**
   - Update this phase’s README/plan/checklist as needed.
   - Reflect any impacts in higher-level READMEs (`docs/project/`, docs/, root).

4. **Handoff**
   - Note remaining risks or TODOs in `checklist.md`.
   - Ensure `../prompt_log.md` includes any new prompts before closing the session.
