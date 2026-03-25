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

# TODO define one sqlite handler fixture for *each* database that will be used in testing
@pytest.fixture(scope="class")
def sqlitehandler():
    sq = SQLiteHandler(store_connection_data = {})
    yield sq
    sq.close()

