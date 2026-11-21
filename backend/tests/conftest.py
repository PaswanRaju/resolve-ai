"""Shared test setup.

Ticket tests run against a real MongoDB (started by docker compose locally, and as a
service container in CI). Each test gets an empty test database.
"""

import os

os.environ.setdefault("MONGO_DB", "resolve_ai_test")  # must be set before the app is imported

import pytest
from fastapi.testclient import TestClient
from pymongo import MongoClient

from app.config import get_settings
from app.main import app


@pytest.fixture
def client():
    settings = get_settings()
    sync = MongoClient(settings.mongo_uri, serverSelectionTimeoutMS=2000)
    sync.drop_database(settings.mongo_db)
    with TestClient(app) as c:
        yield c
    sync.drop_database(settings.mongo_db)
    sync.close()


@pytest.fixture
def new_ticket(client):
    """Create a ticket and return its JSON."""

    def _create(**overrides):
        body = {
            "short_description": "VPN disconnects every 10 minutes",
            "description": "GlobalProtect drops on home Wi-Fi since the last update.",
            "caller": "jdoe",
            "category": "network",
        }
        body.update(overrides)
        res = client.post("/tickets", json=body)
        assert res.status_code == 201, res.text
        return res.json()

    return _create
