# Apps

This workspace groups every runnable application managed by Nx:

| App | Path | Description | Key Commands |
| --- | ---- | ----------- | ------------- |
| Backend API | `apps/backend/` | Flask service with GraphQL contracts (see `libs/schema/schema.graphql`), crawler helpers, Neo4j (neomodel) integration. | `npx nx run backend:test`, `npx nx run backend:start`, `PYTHONPATH=apps/backend/src:. ./apps/backend/.venv/bin/python3 apps/backend/src/manage.py crawler-run --symbol AAPL` |
| Mobile Client | `apps/mobile/` | React Native front-end (Metro dev server + RN bundles) consuming GraphQL. | `npx nx run mobile:typecheck`, `npx react-native run-ios` / `run-android` |
| Regression | `apps/regression/` | Repository-wide end-to-end checks（GraphQL ping）。 | `npx nx run regression:ping` |

Follow each app’s local README for environment-specific details. All automation and orchestration should prefer Nx targets to keep the monorepo consistent.
