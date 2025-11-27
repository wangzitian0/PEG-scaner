# Iteration Flow – Phase 0 Infra

1. **Pre-work Checklist**
   - Read `AGENTS.md`, `../../../specs/infra/IRD-001.md`, `../prompt.md`.
   - Review open items in `checklist.md` (GraphQL/Nx tasks).

2. **Execution Loop**
   - For schema changes: update `libs/schema/schema.graphql`, ensure backend resolvers/front-end hooks align, and re-run relevant Nx targets (`backend:test`, `regression:ping`).
   - For Neo4j connection issues: ensure `NEO4J_URI` (may include credentials), `NEO4J_USER`, `NEO4J_PASSWORD` (or `NEO4J_FAKE=1`) are set; if using compose, prefer service name (`bolt://neo4j:7687`).
   - For Nx tasks: edit configs, then run `npx nx graph` / `nx show project ...` / `nx run backend:test` / `nx run regression:ping` as needed.
   - Record command outputs/logs under `x-log/` if automated.

3. **Documentation Sweep**
   - Update this phase’s README/plan/checklist as needed.
   - Reflect any impacts in higher-level READMEs (`docs/project/`, docs/, root).

4. **Handoff**
   - Note remaining risks or TODOs in `checklist.md`.
   - Ensure `../prompt.md` includes any new prompts before closing the session.
