# Libs - Shared Libraries (SSOT)

Shared code between `apps/backend` (FastAPI) and `apps/cms` (Django).

## Structure

```
libs/
├── config/              # ⭐ Unified settings (SSOT for all env vars)
├── schema/
│   ├── graphql/         # GraphQL SDL
│   └── whitelist/       # Field validation rules
├── neo4j_models/        # Neo4j node definitions (neomodel)
├── neo4j_repo/          # Repository layer
└── auth/                # JWT token verification
```

## Configuration SSOT (`libs/config/`)

Single source of truth for all environment variables:

```python
from libs.config import settings

# Neo4j
settings.neo4j_bolt_url
settings.db_table_prefix

# PostgreSQL  
settings.database_url

# JWT (for simplejwt compatibility)
settings.jwt_secret_key

# Django
settings.django_secret_key
settings.django_allowed_hosts
```

**Environment contract**: `tools/envs/env.ci` (SSOT for all env vars)

## Third-Party Libraries Used

| Library | Purpose | Used By |
|---------|---------|---------|
| `djangorestframework-simplejwt` | JWT auth | Django |
| `django-fsm` | State machine | Django |
| `dj-database-url` | PostgreSQL URL parsing | Django |
| `neomodel` | Neo4j ORM | Both |

## Auth (`libs/auth/`)

Verifies JWT tokens issued by Django simplejwt:

```python
# FastAPI - verify token from request
from libs.auth import verify_token, get_user_id_from_token

payload = verify_token(token)
user_id = get_user_id_from_token(token)
```

**Note**: Token creation is handled by `djangorestframework-simplejwt` in Django.

## Schema Whitelist (`libs/schema/whitelist/`)

Field validation rules:

```python
from libs.schema.whitelist import validate_company

is_valid, errors = validate_company({'ticker': 'AAPL', 'name': 'Apple'})
```

## Neo4j Models (`libs/neo4j_models/`)

```python
from libs.neo4j_models import Company, DailyQuote, DataBatch
```

| Model | Description |
|-------|-------------|
| Company | Stock entity |
| DailyQuote | OHLCV data |
| EarningsReport | Quarterly financials |
| NewsArticle | News with embeddings |
| DataSource | Provenance |
| DataBatch | Pipeline batch |
| CrawlerTask | Crawler job |
