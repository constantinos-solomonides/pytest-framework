"""
Shared pytest fixtures for all test levels.

Provides base URLs, HTTP clients, and common test data
used across e2e, integration, and unit tests.
"""

import os

import pytest

BACKEND_URL = os.environ.get("BACKEND_URL", "http://localhost:8000")
FRONTEND_URL = os.environ.get("FRONTEND_URL", "http://localhost:3000")
LOG_TRACKER_URL = os.environ.get("LOG_TRACKER_URL", "http://localhost:8001")

from src.storage.sqlite_handler import SQLiteHandler


@pytest.fixture(scope="class")
def sqlitehandler(tmp_path_factory):
    """Yield an in-memory SQLiteHandler scoped to the test class."""
    db_path = str(tmp_path_factory.mktemp("data") / "test.db")
    sq = SQLiteHandler(store_connection_data={"db_path": db_path})
    yield sq
    sq.close()
