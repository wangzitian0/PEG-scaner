"""
Neo4j Connection Management

Re-exports from libs.config for backward compatibility.
All settings are defined in libs/config/settings.py (SSOT).
"""

from __future__ import annotations

from contextlib import asynccontextmanager
from typing import TYPE_CHECKING

from neomodel import config as neo_config

# SSOT: Import settings from libs.config
from libs.config.settings import Settings, get_settings, reset_settings_cache

if TYPE_CHECKING:
    from fastapi import FastAPI

__all__ = ['Settings', 'get_settings', 'reset_settings_cache', 'get_driver', 'lifespan']


def get_driver() -> None:
    """Initialize neomodel connection."""
    settings = get_settings()
    neo_config.DATABASE_URL = settings.neo4j_bolt_url


@asynccontextmanager
async def lifespan(app: "FastAPI"):
    """FastAPI lifespan hook for Neo4j connection management."""
    settings = get_settings()
    neo_config.DATABASE_URL = settings.neo4j_bolt_url
    yield
    # neomodel doesn't require explicit close
