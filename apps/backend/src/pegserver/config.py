from __future__ import annotations

import os
from dataclasses import dataclass
from functools import lru_cache
from typing import Iterable, List
from urllib.parse import urlparse, urlunparse

_DEFAULT_CORS = {
    'http://localhost:5173',
    'http://127.0.0.1:5173',
    'http://localhost:5174',
    'http://127.0.0.1:5174',
}


def _split_csv(value: str | None) -> List[str]:
    if not value:
        return []
    return [item.strip() for item in value.split(',') if item.strip()]


def _sanitize_prefix(prefix: str) -> str:
    sanitized = ''.join(ch if ch.isalnum() or ch == '_' else '_' for ch in prefix.strip())
    if sanitized and not sanitized.endswith('_'):
        sanitized = f'{sanitized}_'
    return sanitized


@dataclass(frozen=True)
class Settings:
    env: str
    debug: bool
    agent_name: str
    cors_allowed_origins: List[str]
    neo4j_uri: str
    neo4j_user: str
    neo4j_password: str
    neo4j_database: str
    db_table_prefix: str
    use_fake_graph: bool

    def prefixed_label(self, base: str) -> str:
        prefix = self.db_table_prefix or ''
        return f"{prefix}{base}" if prefix else base

    @property
    def neo4j_bolt_url(self) -> str:
        parsed = urlparse(self.neo4j_uri)
        netloc = parsed.netloc or ''
        if '@' in netloc:
            # strip any existing auth to avoid duplication
            netloc = netloc.split('@', 1)[-1]
        if self.neo4j_user:
            netloc = f"{self.neo4j_user}:{self.neo4j_password}@{netloc or 'localhost'}"
        path = parsed.path or ''
        if self.neo4j_database:
            path = f"/{self.neo4j_database.strip('/')}"
        return urlunparse(parsed._replace(netloc=netloc, path=path))

    def cors_resources(self) -> dict[str, dict[str, Iterable[str]]]:
        return {'/api/*': {'origins': self.cors_allowed_origins or sorted(_DEFAULT_CORS)}}


def _derive_env() -> str:
    return os.getenv('PEG_ENV') or os.getenv('FLASK_ENV') or 'development'


@lru_cache(maxsize=1)
def get_settings() -> Settings:
    env = _derive_env().lower()
    debug = env != 'production' or os.getenv('FLASK_DEBUG') == '1'
    agent_name = os.getenv('PEG_AGENT_NAME', 'pegscanner-backend')

    cors = _split_csv(os.getenv('API_CORS_ORIGINS')) or sorted(_DEFAULT_CORS)

    neo4j_uri = os.getenv('NEO4J_URI', 'bolt://localhost:7687')
    neo4j_user = os.getenv('NEO4J_USER', 'neo4j')
    neo4j_password = os.getenv('NEO4J_PASSWORD', 'neo4j')
    neo4j_database = os.getenv('NEO4J_DATABASE', '').strip()

    prefix = os.getenv('DB_TABLE_PREFIX')
    if not prefix:
        prefix = 'prod_' if env == 'production' else 'dev_'
    prefix = _sanitize_prefix(prefix)

    use_fake_graph = os.getenv('NEO4J_FAKE', '0') == '1'

    return Settings(
        env=env,
        debug=debug,
        agent_name=agent_name,
        cors_allowed_origins=cors,
        neo4j_uri=neo4j_uri,
        neo4j_user=neo4j_user,
        neo4j_password=neo4j_password,
        neo4j_database=neo4j_database,
        db_table_prefix=prefix,
        use_fake_graph=use_fake_graph,
    )


def reset_settings_cache():  # pragma: no cover - used in tests
    get_settings.cache_clear()
