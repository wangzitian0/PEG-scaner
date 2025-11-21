# Phase 1 Checklist

- [x] Create `phrase_1.initial_setup` iteration folder with plan/process docs.
- [x] Append user prompts (AGENTS.md request + follow-ups) to `../prompt_log.md` only.
- [x] Capture baseline directory trees for root, project, backend, and mobile.
- [x] Run `backend/manage.py test` (current result: 0 tests) to document readiness gaps.
- [ ] Draft data source blueprint covering K-line, news, F10, factor data, and verification workflow.
- [ ] Map `schema/stock.proto` objects to backend/mobile components and list missing fields.
- [x] Outline agent reward mechanisms tied to requirement coverage, data verification, and testing（`docs/AI_EVALUATION.md` + `AGENTS.md` 强制要求）。
- [x] Ensure every agent must read `docs/AI_EVALUATION.md` before work (instruction added to `AGENTS.md` & iteration docs，需追踪 AGENTS.md 更新).
- [ ] Produce initial implementation tickets for:
  - [ ] Backend K-line & F10 fetcher
  - [ ] Factor calculation service (PEG)
  - [ ] Mobile UI skeleton for stock details/factor view
- [ ] Update `docs/TODOWRITE.md` when new gaps are identified during this phase.
