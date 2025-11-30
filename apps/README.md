# Apps

This workspace groups every runnable application managed by Nx:

| App | Path | Description | Key Commands |
| --- | ---- | ----------- | ------------- |
| Backend API | `apps/backend/` | FastAPI service with GraphQL contracts (see `libs/schema/schema.graphql`), crawler helpers, Neo4j (neomodel) integration. | `npx nx run backend:test`, `npx nx run backend:start` |
| CMS | `apps/cms/` | Django admin for auth, CMS content, and graph data writing. Uses django-neomodel for Neo4j. API remains FastAPI-based. | `npx nx run cms:start`, `npx nx run cms:migrate`, `npx nx run cms:seed` |
| Mobile Client | `apps/mobile/` | React Native front-end (Metro dev server + RN bundles) consuming GraphQL. | `npx nx run mobile:typecheck`, `npx react-native run-ios` / `run-android` |
| Regression | `apps/regression/` | Repository-wide end-to-end checks（GraphQL ping）。 | `npx nx run regression:ping` |

## Architecture Overview

```
┌─────────────────┐     ┌─────────────────┐     ┌─────────────────┐
│   Mobile App    │────▶│   Backend API   │────▶│     Neo4j       │
│  (React Native) │     │   (FastAPI)     │     │  (Graph Data)   │
└─────────────────┘     └─────────────────┘     └────────┬────────┘
                                                         │
                        ┌─────────────────┐              │
                        │      CMS        │──────────────┘
                        │   (Django)      │
                        │  Admin + Auth   │
                        └─────────────────┘
```

- **Backend API**: GraphQL queries for reads (FastAPI + Strawberry)
- **CMS**: Admin UI, auth, and graph writes (Django + django-neomodel)
- **Mobile**: Cross-platform UI consuming GraphQL

Follow each app's local README for environment-specific details. All automation and orchestration should prefer Nx targets to keep the monorepo consistent.
