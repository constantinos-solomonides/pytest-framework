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


@pytest.fixture
def backend_url():
    """Returns the base URL for the SUT backend API."""
    return BACKEND_URL


@pytest.fixture
def frontend_url():
    """Returns the base URL for the SUT frontend."""
    return FRONTEND_URL


@pytest.fixture
def log_tracker_url():
    """Returns the base URL for the log tracker API."""
    return LOG_TRACKER_URL
