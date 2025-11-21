# Libraries

Shared libraries and Single Source of Truth assets live under `libs/`. Currently:

| Library | Description |
| --- | --- |
| [`schema/`](./schema/README.md) | Protocol Buffers that define cross-application contracts (stock data, ping response, etc.). Run `npx nx run backend:generate-proto` after edits. |

Add new shared libs here (e.g., reusable TypeScript/Python packages) so every app consumes the same artifacts.
