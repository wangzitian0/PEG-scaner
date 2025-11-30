"""
Unified Settings Management (SSOT)

Loads configuration from environment variables.
Provides type-safe access to all settings.
"""

import os
from dataclasses import dataclass
from functools import lru_cache
from pathlib import Path
from typing import List, Optional
from urllib.parse import urlparse, urlunparse

# Load .env file if exists
# Contract: tools/envs/env.ci is the SSOT for all environment variables
from dotenv import load_dotenv

_project_root = Path(__file__).resolve().parent.parent.parent
_env_file = _project_root / '.env'
if _env_file.exists():
    load_dotenv(_env_file)


def _parse_bool(value: Optional[str], default: bool = False) -> bool:
    if value is None:
        return default
    return value.lower() in ('true', '1', 'yes', 'on')


def _parse_int(value: Optional[str], default: int) -> int:
    if value is None:
        return default
    try:
        return int(value)
    except ValueError:
        return default


def _split_csv(value: Optional[str]) -> List[str]:
    if not value:
        return []
    return [item.strip() for item in value.split(",") if item.strip()]


def _sanitize_prefix(prefix: str) -> str:
    sanitized = "".join(ch if ch.isalnum() or ch == "_" else "_" for ch in prefix.strip())
    if sanitized and not sanitized.endswith("_"):
        sanitized = f"{sanitized}_"
    return sanitized


@dataclass(frozen=True)
class Settings:
    """Application settings loaded from environment."""
    
    # Core
    env: str
    debug: bool
    agent_name: str
    
    # Neo4j
    neo4j_uri: str
    neo4j_user: str
    neo4j_password: str
    neo4j_database: str
    db_table_prefix: str
    
    # PostgreSQL
    database_url: str
    
    # JWT
    jwt_secret_key: str
    jwt_access_token_lifetime_minutes: int
    jwt_refresh_token_lifetime_days: int
    
    # Django
    django_secret_key: str
    django_allowed_hosts: List[str]
    
    # CORS
    cors_allowed_origins: List[str]
    
    @property
    def neo4j_bolt_url(self) -> str:
        """Build complete Neo4j bolt URL with credentials."""
        parsed = urlparse(self.neo4j_uri)
        netloc = parsed.netloc or ""
        if "@" in netloc:
            netloc = netloc.split("@", 1)[-1]
        if self.neo4j_user:
            netloc = f"{self.neo4j_user}:{self.neo4j_password}@{netloc or 'localhost'}"
        path = parsed.path or ""
        if self.neo4j_database:
            path = f"/{self.neo4j_database.strip('/')}"
        return urlunparse(parsed._replace(netloc=netloc, path=path))
    
    def prefixed_label(self, base: str) -> str:
        """Get prefixed Neo4j label."""
        return f"{self.db_table_prefix}{base}" if self.db_table_prefix else base
    
    @property
    def is_production(self) -> bool:
        return self.env == "prod"
    
@lru_cache(maxsize=1)
def get_settings() -> Settings:
    """Load settings from environment (cached).
    
    PEG_ENV values: dev, test_xxx, prod
    """
    env = os.getenv("PEG_ENV", "dev").lower()
    debug = _parse_bool(os.getenv("DEBUG"), default=env != "prod")
    agent_name = os.getenv("PEG_AGENT_NAME", "pegscanner-backend")
    
    # Neo4j
    neo4j_uri = os.getenv("NEO4J_URI", "bolt://localhost:7687")
    neo4j_user = os.getenv("NEO4J_USER", "neo4j")
    neo4j_password = os.getenv("NEO4J_PASSWORD") or "pegscanner"  # Empty string fallback
    neo4j_database = os.getenv("NEO4J_DATABASE", "").strip()
    
    # Debug: Log if password is missing in prod
    if env == "prod" and not os.getenv("NEO4J_PASSWORD"):
        import sys
        print("[WARN] NEO4J_PASSWORD not set, using default", file=sys.stderr)
    
    prefix = os.getenv("DB_TABLE_PREFIX")
    if not prefix:
        prefix = "prod_" if env == "prod" else "dev_"
    prefix = _sanitize_prefix(prefix)
    
    # PostgreSQL
    database_url = os.getenv(
        "DATABASE_URL",
        "postgres://postgres:postgres@localhost:5432/pegscanner"
    )
    
    # JWT
    jwt_secret_key = os.getenv("JWT_SECRET_KEY", "dev-secret-change-in-production")
    jwt_access_lifetime = _parse_int(os.getenv("JWT_ACCESS_TOKEN_LIFETIME_MINUTES"), 60)
    jwt_refresh_lifetime = _parse_int(os.getenv("JWT_REFRESH_TOKEN_LIFETIME_DAYS"), 7)
    
    # Django
    django_secret_key = os.getenv("DJANGO_SECRET_KEY", "dev-secret-change-in-production")
    django_allowed_hosts = _split_csv(os.getenv("DJANGO_ALLOWED_HOSTS", "localhost,127.0.0.1"))
    
    # CORS
    cors = _split_csv(os.getenv("API_CORS_ORIGINS")) or [
        "http://localhost:5173",
        "http://localhost:5174",
    ]
    
    return Settings(
        env=env,
        debug=debug,
        agent_name=agent_name,
        neo4j_uri=neo4j_uri,
        neo4j_user=neo4j_user,
        neo4j_password=neo4j_password,
        neo4j_database=neo4j_database,
        db_table_prefix=prefix,
        database_url=database_url,
        jwt_secret_key=jwt_secret_key,
        jwt_access_token_lifetime_minutes=jwt_access_lifetime,
        jwt_refresh_token_lifetime_days=jwt_refresh_lifetime,
        django_secret_key=django_secret_key,
        django_allowed_hosts=django_allowed_hosts,
        cors_allowed_origins=cors,
    )


def reset_settings_cache() -> None:
    """Clear settings cache (for testing)."""
    get_settings.cache_clear()


# Singleton instance
settings = get_settings()

