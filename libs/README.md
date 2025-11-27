# Libraries

Shared libraries and Single Source of Truth assets live under `libs/`. Currently:

| Library | Description |
| --- | --- |
| [`schema/`](./schema/README.md) | GraphQL SDL (`schema.graphql`) that defines cross-application contracts (ping, peg stocks, single stock page). |

Add new shared libs here (e.g., reusable TypeScript/Python packages) so every app consumes the same artifacts.
