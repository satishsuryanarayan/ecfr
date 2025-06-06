import base64

import pytest

from api import create_app
from api.db import init_db


@pytest.fixture(scope="session")
def basic_auth_header():
    original_str = "test_test:password_password"
    str_bytes = original_str.encode("utf-8")
    encoded_bytes = base64.b64encode(str_bytes)
    base64_string = encoded_bytes.decode("utf-8")
    header = {"Authorization": f"Basic {base64_string}"}
    return header


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
