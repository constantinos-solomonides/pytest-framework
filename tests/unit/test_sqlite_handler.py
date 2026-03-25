""" Unit tests for SQLite handler

Ensures that the basic functionalities can be done with the database:
    * Connect to it
    * Create table
    * Add values
    * Retrieve values
    * Drop table

Used for TDD (Test Driven Development), remains as UT (Unit Tests)
"""
import pytest

class TestSQLiteHandler:
    def test_connect_to_base(self, sqlitehandler):
        """Remove once real unit tests are implemented."""
        assert sqlitehandler, "Unit test suite not yet implemented"

