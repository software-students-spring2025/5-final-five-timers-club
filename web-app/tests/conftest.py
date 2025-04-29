import pytest
from unittest.mock import MagicMock
import os, sys

# letting tests import app.py, auth.py
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))
from app import app as flask_app
import auth


@pytest.fixture(autouse=True)
def disable_db(monkeypatch):
    mock_coll = MagicMock()
    monkeypatch.setattr("app.emotion_db", mock_coll)
    monkeypatch.setattr("auth.users_coll", mock_coll)


@pytest.fixture
def client():
    flask_app.config.update(
        TESTING=True, WTF_CSRF_ENABLED=False, SERVER_NAME="localhost"
    )
    with flask_app.app_context():
        with flask_app.test_client() as client:
            yield client
