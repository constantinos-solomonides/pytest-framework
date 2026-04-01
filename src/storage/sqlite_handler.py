#!/usr/bin/env python3
"""Implements the integration with SQLite database."""

import logging
import os
import sqlite3

from .base import StorageBase

logger = logging.getLogger(__name__)


class SQLiteHandler(StorageBase):
    """SQLite storage handler.

    Enforces a single instance per database path to prevent parallel access
    to the same file.  Connection details are resolved in priority order:
        1. Explicit ``db_path`` key in *store_connection_data*.
        2. ``SQLITE_DB_PATH`` environment variable.
        3. ``:memory:`` (in-memory database).
    """

    _instances: dict[str, "SQLiteHandler"] = {}

    # ------------------------------------------------------------------
    # Construction helpers
    # ------------------------------------------------------------------

    @staticmethod
    def _resolve_db_path(store_connection_data: dict[str, str]) -> str:
        """Determine the database file path from available sources.

        store_connection_data: Caller-supplied connection parameters.

        Returns: Resolved path string.
        """
        if "db_path" in store_connection_data:
            return store_connection_data["db_path"]
        return os.environ.get("SQLITE_DB_PATH", ":memory:")

    def __new__(cls, *, store_connection_data: dict[str, str] | None = None):
        """Return the singleton instance for the resolved db path.

        store_connection_data: Connection parameters dict.

        Returns: SQLiteHandler instance (new or previously created).
        """
        resolved = cls._resolve_db_path(store_connection_data or {})
        if resolved in cls._instances:
            logger.debug("Reusing existing handler for '%s'", resolved)
            return cls._instances[resolved]
        instance = super().__new__(cls)
        cls._instances[resolved] = instance
        logger.debug("Created new handler slot for '%s'", resolved)
        return instance

    def __init__(self, *, store_connection_data: dict[str, str] | None = None):
        """Open a connection to the SQLite database (skipped on reuse).

        store_connection_data: Dictionary with connection details.
            Recognised key: ``db_path`` -- filesystem path to the SQLite file.
            Falls back to ``SQLITE_DB_PATH`` env var, then to ``:memory:``.
        """
        if getattr(self, "_initialised", False):
            return

        self._db_path: str = self._resolve_db_path(store_connection_data or {})

        try:
            self._connection: sqlite3.Connection | None = sqlite3.connect(
                self._db_path
            )
            self._connection.row_factory = sqlite3.Row
        except sqlite3.Error as exc:
            logger.error("Failed to connect to '%s': %s", self._db_path, exc)
            self._instances.pop(self._db_path, None)
            raise

        self._initialised: bool = True
        logger.info("Connected to SQLite database at '%s'", self._db_path)

    # ------------------------------------------------------------------
    # Internal guards
    # ------------------------------------------------------------------

    def _ensure_connected(self) -> tuple[bool, str]:
        """Verify the connection is alive before an operation.

        Returns: (True, "ok") when connected, (False, reason) otherwise.
        """
        if self._connection is None:
            msg = "No active database connection"
            logger.warning(msg)
            return False, msg
        return True, "ok"

    # ------------------------------------------------------------------
    # Table management
    # ------------------------------------------------------------------

    def initialise_table(
        self, table_name: str, schema: dict[str, str]
    ) -> tuple[bool, str]:
        """Create a table with the given schema if it does not already exist.

        table_name: Name of the table to create.
        schema:     {column_name: column_type} pairs,
                    e.g. {"id": "INTEGER PRIMARY KEY", "name": "TEXT"}.

        Returns: (success, message) tuple.
        """
        ok, msg = self._ensure_connected()
        if not ok:
            return False, msg

        if not table_name or not isinstance(table_name, str):
            return False, "table_name must be a non-empty string"
        if not schema or not isinstance(schema, dict):
            return False, "schema must be a non-empty dict"

        columns = ", ".join(f"{col} {col_type}" for col, col_type in schema.items())
        sql = f"CREATE TABLE IF NOT EXISTS {table_name} ({columns})"
        logger.debug("Executing: %s", sql)

        try:
            self._connection.execute(sql)
            self._connection.commit()
        except sqlite3.Error as exc:
            logger.error("Failed to create table '%s': %s", table_name, exc)
            return False, str(exc)

        logger.info("Table '%s' initialised", table_name)
        return True, f"Table '{table_name}' created"

    def drop_table(self, table_name: str) -> tuple[bool, str]:
        """Drop a table from the database.

        table_name: Name of the table to drop.

        Returns: (success, message) tuple.
        """
        ok, msg = self._ensure_connected()
        if not ok:
            return False, msg

        if not table_name or not isinstance(table_name, str):
            return False, "table_name must be a non-empty string"

        sql = f"DROP TABLE IF EXISTS {table_name}"
        logger.debug("Executing: %s", sql)

        try:
            self._connection.execute(sql)
            self._connection.commit()
        except sqlite3.Error as exc:
            logger.error("Failed to drop table '%s': %s", table_name, exc)
            return False, str(exc)

        logger.info("Table '%s' dropped", table_name)
        return True, f"Table '{table_name}' dropped"

    # ------------------------------------------------------------------
    # Data manipulation
    # ------------------------------------------------------------------

    def insert(
        self,
        table_name: str,
        data: dict[str, str | int | float | None]
        | list[dict[str, str | int | float | None]],
    ) -> tuple[bool, str]:
        """Insert one or more rows into a table.

        table_name: Target table name.
        data:       A single {column: value} dict, or a list of such dicts.
                    Batch rows use the column set of the first dict; missing
                    keys in subsequent dicts default to None.

        Returns: (success, message) tuple.
        """
        ok, msg = self._ensure_connected()
        if not ok:
            return False, msg

        if not table_name or not isinstance(table_name, str):
            return False, "table_name must be a non-empty string"
        if not data:
            return False, "data must not be empty"

        rows: list[dict] = data if isinstance(data, list) else [data]
        if not all(isinstance(r, dict) and r for r in rows):
            return False, "Each row must be a non-empty dict"

        columns = list(rows[0].keys())
        placeholders = ", ".join("?" for _ in columns)
        col_names = ", ".join(columns)
        sql = f"INSERT INTO {table_name} ({col_names}) VALUES ({placeholders})"
        logger.debug("Executing: %s (x%d rows)", sql, len(rows))

        try:
            values = [tuple(row.get(c) for c in columns) for row in rows]
            self._connection.executemany(sql, values)
            self._connection.commit()
        except sqlite3.Error as exc:
            logger.error("Insert into '%s' failed: %s", table_name, exc)
            return False, str(exc)

        logger.info("Inserted %d row(s) into '%s'", len(rows), table_name)
        return True, f"Inserted {len(rows)} row(s)"

    def update(
        self,
        table_name: str,
        data: dict[str, str | int | float | None],
        conditions: dict[str, str | int | float | None],
    ) -> tuple[bool, str]:
        """Update rows matching the given conditions.

        table_name: Target table name.
        data:       {column: new_value} pairs to SET.
        conditions: {column: value} pairs ANDed for the WHERE clause.
                    Must be non-empty to prevent accidental full-table updates.

        Returns: (success, message) tuple.
        """
        ok, msg = self._ensure_connected()
        if not ok:
            return False, msg

        if not table_name or not isinstance(table_name, str):
            return False, "table_name must be a non-empty string"
        if not data or not isinstance(data, dict):
            return False, "data must be a non-empty dict"
        if not conditions or not isinstance(conditions, dict):
            return False, "conditions must be a non-empty dict"

        set_clause = ", ".join(f"{col} = ?" for col in data)
        where_clause = " AND ".join(f"{col} = ?" for col in conditions)
        sql = f"UPDATE {table_name} SET {set_clause} WHERE {where_clause}"
        params = list(data.values()) + list(conditions.values())
        logger.debug("Executing: %s | params=%s", sql, params)

        try:
            cursor = self._connection.execute(sql, params)
            self._connection.commit()
        except sqlite3.Error as exc:
            logger.error("Update on '%s' failed: %s", table_name, exc)
            return False, str(exc)

        logger.info("Updated %d row(s) in '%s'", cursor.rowcount, table_name)
        return True, f"Updated {cursor.rowcount} row(s)"

    # ------------------------------------------------------------------
    # Retrieval
    # ------------------------------------------------------------------

    def retrieve(
        self,
        table_name: str,
        conditions: dict[str, str | int | float | None] | None = None,
    ) -> tuple[bool, list[dict[str, str | int | float | None]] | str]:
        """Retrieve rows from a table, optionally filtered.

        table_name: Source table name.
        conditions: Optional {column: value} pairs for filtering (AND).
                    If None, returns all rows.

        Returns: (True, list_of_row_dicts) on success,
                 (False, error_message) on failure.
        """
        ok, msg = self._ensure_connected()
        if not ok:
            return False, msg

        if not table_name or not isinstance(table_name, str):
            return False, "table_name must be a non-empty string"

        if conditions:
            where_clause = " AND ".join(f"{col} = ?" for col in conditions)
            sql = f"SELECT * FROM {table_name} WHERE {where_clause}"
            params = list(conditions.values())
        else:
            sql = f"SELECT * FROM {table_name}"
            params = []

        logger.debug("Executing: %s | params=%s", sql, params)

        try:
            cursor = self._connection.execute(sql, params)
            rows = [dict(row) for row in cursor.fetchall()]
        except sqlite3.Error as exc:
            logger.error("Retrieve from '%s' failed: %s", table_name, exc)
            return False, str(exc)

        logger.info("Retrieved %d row(s) from '%s'", len(rows), table_name)
        return True, rows

    # ------------------------------------------------------------------
    # Lifecycle
    # ------------------------------------------------------------------

    def close(self) -> tuple[bool, str]:
        """Close the database connection and deregister this singleton.

        Returns: (success, message) tuple.
        """
        if self._connection is None:
            logger.debug("Connection already closed for '%s'", self._db_path)
            return True, "Already closed"

        try:
            self._connection.close()
        except sqlite3.Error as exc:
            logger.error("Error closing connection to '%s': %s", self._db_path, exc)
            return False, str(exc)
        finally:
            self._connection = None
            self._instances.pop(self._db_path, None)
            self._initialised = False

        logger.info("Closed connection to '%s'", self._db_path)
        return True, f"Connection to '{self._db_path}' closed"


if __name__ == "__main__":
    e = SystemExit("You cannot call this file directly.")
    e.code = 1
    raise e
