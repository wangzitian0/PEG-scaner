"""
Backend Configuration

Re-exports settings from neo4j_repo for convenience.
"""

from neo4j_repo.connection import Settings, get_settings, reset_settings_cache

__all__ = ["Settings", "get_settings", "reset_settings_cache"]

