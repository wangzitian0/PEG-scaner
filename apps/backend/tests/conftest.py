"""
Test configuration for FastAPI + Strawberry backend.

Uses Starlette TestClient for synchronous testing.
Requires a running Neo4j instance.
"""

import pytest

from neo4j_repo.connection import reset_settings_cache


@pytest.fixture(scope="session", autouse=True)
def setup_env():
    """Reset settings cache at start of test session."""
    reset_settings_cache()


@pytest.fixture
def app():
    """Create test application instance."""
    reset_settings_cache()
    from apps.backend.main import create_app
    return create_app()


@pytest.fixture
def client(app):
    """Synchronous test client using Starlette TestClient."""
    from starlette.testclient import TestClient
    with TestClient(app) as client:
        yield client
