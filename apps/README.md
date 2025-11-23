# Apps

This workspace groups every runnable application managed by Nx:

| App | Path | Description | Key Commands |
| --- | ---- | ----------- | ------------- |
| Backend API | `apps/backend/` | Django service with protobuf contracts, crawler app, Neo4j integration, and REST endpoints. | `npx nx run backend:test`, `npx nx run backend:start`, `python apps/backend/manage.py run_crawler_job --symbol AAPL` |
| Mobile Client | `apps/mobile/` | React Native front-end (Metro dev server + RN bundles). | `npx nx run mobile:typecheck`, `npx react-native run-ios` / `run-android` |
| Regression | `apps/regression/` | Repository-wide end-to-end checks (currently protobuf ping). | `npx nx run regression:ping` |

Follow each app’s local README for environment-specific details. All automation and orchestration should prefer Nx targets to keep the monorepo consistent.
