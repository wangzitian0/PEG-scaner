import os

import pytest

from pegserver import create_app
from pegserver.config import reset_settings_cache


@pytest.fixture(scope='session')
def app():
    os.environ['NEO4J_FAKE'] = '1'
    reset_settings_cache()
    app = create_app()
    return app


@pytest.fixture()
def client(app):
    return app.test_client()
