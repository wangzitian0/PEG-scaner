# CMS - Django Admin + Data Pipeline

Django app providing:
- **Auth**: JWT via `djangorestframework-simplejwt`
- **Pipeline**: Workflow via `django-fsm`
- **Admin UI**: `django-unfold`

## Architecture

```
libs/config (SSOT) ─────────────────────────┐
                                            │
┌──────────────────────┐  ┌─────────────────▼────────────┐
│   apps/backend       │  │   apps/cms                   │
│   (FastAPI - READ)   │  │   (Django - WRITE)           │
│                      │  │                              │
│   verify_token()     │  │   simplejwt (issue tokens)   │
│   from libs/auth     │  │   django-fsm (state machine) │
└──────────────────────┘  └──────────────────────────────┘
            │                      │
            └──────────┬───────────┘
                       ▼
              Neo4j + PostgreSQL
```

## Libraries Used

| Library | Purpose |
|---------|---------|
| `djangorestframework-simplejwt` | JWT tokens |
| `django-fsm` | Pipeline state machine |
| `django-unfold` | Modern admin UI |
| `dj-database-url` | PostgreSQL config |
| `django-neomodel` | Neo4j integration |

## Quick Start

```bash
# Install dependencies
cd apps/cms
python3 -m venv .venv
.venv/bin/pip install -r requirements.txt

# Set environment (copy from tools/envs/.env.example)
export DATABASE_URL=postgres://user:pass@localhost:5432/pegscanner

# Migrate
PYTHONPATH=/path/to/PEG-scaner:. .venv/bin/python manage.py migrate

# Create admin user
.venv/bin/python manage.py createsuperuser

# Run
.venv/bin/python manage.py runserver 8001
```

## API Endpoints

| Endpoint | Method | Description |
|----------|--------|-------------|
| `/admin/` | GET | Admin UI |
| `/api/token/` | POST | Get JWT tokens |
| `/api/token/refresh/` | POST | Refresh token |
| `/api/token/verify/` | POST | Verify token |
| `/health/` | GET | Health check |

## Pipeline Workflow (FSM)

```
raw ──▶ cleaning ──▶ clean ──▶ reviewing ──▶ approved ──▶ committed
                                   │
                                   └──▶ rejected ──▶ cleaning (retry)
```

Managed by `django-fsm` in `pipeline/models.py`.

## Environment Variables

All from `libs/config/` (SSOT). See `tools/envs/.env.example`.

Key variables:
- `DATABASE_URL` - PostgreSQL connection
- `NEO4J_URI`, `NEO4J_USER`, `NEO4J_PASSWORD` - Neo4j
- `JWT_SECRET_KEY` - Must match simplejwt signing key
- `DJANGO_SECRET_KEY` - Django secret
