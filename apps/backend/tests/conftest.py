"""
Test configuration for FastAPI + Strawberry backend.

Uses Starlette TestClient for synchronous testing.
"""

import os

import pytest

# Set fake mode before importing app
os.environ["NEO4J_FAKE"] = "1"

from neo4j_repo.connection import reset_settings_cache


@pytest.fixture(scope="session", autouse=True)
def setup_env():
    """Ensure fake mode is set for all tests."""
    os.environ["NEO4J_FAKE"] = "1"
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
