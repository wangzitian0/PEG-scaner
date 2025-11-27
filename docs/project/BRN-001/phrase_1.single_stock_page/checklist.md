# Phase 1 Checklist

- [x] Create `phrase_1.single_stock_page` iteration folder with plan/process docs.
- [x] Append user prompts (AGENTS.md request + follow-ups) to `../prompt.md` only.
- [x] Capture baseline directory trees for root, apps/backend, and apps/mobile.
- [x] Run `npx nx run backend:test` (current result: ping test) to document readiness gaps.
- [ ] Draft single-stock data source blueprint covering K-line, news, F10, factor data, and verification workflow.
- [ ] Map `libs/schema/schema.graphql` types到 backend/mobile components and list missing fields.
- [x] Outline agent reward mechanisms tied to requirement coverage, data verification, and testing（`docs/specs/infra/IRD-001.md` + `AGENTS.md` 强制要求）。
- [x] Ensure every agent must read `docs/specs/infra/IRD-001.md` before work (instruction added to `AGENTS.md` & iteration docs，需追踪 AGENTS.md 更新).
- [ ] Produce implementation tickets for:
  - [ ] Backend single-stock data API (K-line + F10 metadata) via GraphQL
  - [ ] Factor calculation service (PEG)
  - [ ] Mobile single-stock UI skeleton (charts/news placeholders) consuming GraphQL
- [ ] Update `../todowrite.md` when new gaps are identified during this phase.
- [x] Implement backend single-stock GraphQL resolver (`singleStock`) with initial K-line + F10 payload.
- [x] Implement mobile single-stock UI skeleton that consumes GraphQL payloads (company info, K-line summary, news placeholder).
- [x] Support queryable single-stock page links (URL `?symbol=` param + manual input) so any ticker can be loaded directly.
- [x] Add crawler app + Flask-Admin to manage crawl jobs, persist graph data to Neo4j, and source the single stock page from the graph.
