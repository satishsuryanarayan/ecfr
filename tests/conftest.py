import pytest

from api import create_app
from api.db import init_db


@pytest.fixture(scope="session")
def app():
    app = create_app({'TESTING': True})

    with app.app_context():
        init_db()

    yield app


@pytest.fixture
def client(app):
    return app.test_client()


@pytest.fixture
def runner(app):
    return app.test_cli_runner()
