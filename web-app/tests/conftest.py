import os
import sys
import pytest
from unittest.mock import MagicMock

# ensuring app module is importable!
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from app import app as flask_app, emotion_db
import auth

@pytest.fixture(autouse=True)
def disable_db(monkeypatch):
    """Replace real MongoDB collections with mocks to isolate tests."""
    mock_coll = MagicMock()
    monkeypatch.setattr('app.emotion_db', mock_coll)
    monkeypatch.setattr('auth.users_coll', mock_coll)

@pytest.fixture
def client():
    flask_app.config['TESTING'] = True
    flask_app.config['WTF_CSRF_ENABLED'] = False
    with flask_app.test_client() as client:
        yield client