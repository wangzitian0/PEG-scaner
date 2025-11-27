# Architecture Documentation

## Technology Stack

### Core
- **Monorepo Management**: [Nx](https://nx.dev) (v22.1.0)
  - Layout: `apps/` for applications, `libs/` for shared libraries
  - Plugins: `@nx/react-native`, `@nx/vite`, `@nx/web`
- **Frontend**: React Native (v0.79.3) / React (v19.0.0)
  - Unified interface for Web, iOS, Android
  - Build Tool: Vite (v7.0.0) for Web
- **Backend**: Python
  - Seamless integration with Backend, Big Data, ML
  - Communication: Protobuf (v7.5.4) for structured data

### AI & Compute
- **Models**: Gemini, Codex, Perplexity, DeepSeek (via OpenRouter for production)
- **Compute**: Local RTX 4090 for low-cost pre-computation
- **AI-Native**: Self-evolving agent system with reward mechanisms (see `docs/specs/infra/IRD-001.md`)

## Configuration & Tooling

### Root Configuration
- **`nx.json`**: Defines the Monorepo structure and plugin configurations.
- **`package.json`**: Manages Node.js dependencies and global scripts.
  - `npm run dev`: Starts the full development environment via `tools/envs/manage.py`.
  - `npm run lint:structure`: Enforces project structure guidelines.
- **`tsconfig.base.json`**: Base TypeScript configuration (Target: ES2015, Module: ESNext).
- **`docker-compose.yml`**: Defines production/staging services.
  - **Backend**: Maps host port `2082` to container port `8000`.
  - **Frontend**: Maps host port `8080` to container port `80`.

## Deployment Strategy

### Infrastructure
- **Orchestration**: [Dokploy](https://dokploy.com/)
- **Traffic Flow**: Cloudflare -> Traefik -> Dokploy (Docker)
