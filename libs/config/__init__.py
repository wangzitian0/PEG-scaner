"""
Shared Configuration (SSOT)

Single source of truth for all environment-based configuration.
Used by both Django (apps/cms) and FastAPI (apps/backend).

Usage:
    from libs.config import settings
    
    # Neo4j
    print(settings.neo4j_bolt_url)
    
    # JWT
    print(settings.jwt_secret_key)
"""

from .settings import settings, get_settings, Settings

__all__ = ['settings', 'get_settings', 'Settings']

