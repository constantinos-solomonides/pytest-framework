#!/usr/bin/env python3
"""Storage handler base (abstract) class.

Provides the signature all subclasses must implement to ensure compliance with
the base.
"""

from abc import ABC, abstractmethod


class StorageBase(ABC):
    """Abstract base for every storage backend.

    Subclasses implement concrete connection logic, table management, and
    CRUD operations.  Return conventions:
        - Mutation methods return ``(bool, str)`` -- success flag + message.
        - Query methods return ``(bool, list[dict] | str)`` -- success flag +
          rows on success, error string on failure.
    """

    @abstractmethod
    def __init__(self, *, store_connection_data: dict[str, str] | None = None):
        """Initialise the storage backend.

        store_connection_data: Key/value pairs needed to connect (e.g. path,
            host, credentials).  When *None*, the implementation should fall
            back to environment variables or sensible defaults.
        """
        pass

    @abstractmethod
    def initialise_table(self, table_name: str, schema: dict[str, str]) -> tuple[bool, str]:
        """Create a table (or equivalent collection) with the given schema.

        table_name: Name of the table to create.
        schema:     Column definitions as {column_name: column_type} pairs,
                    e.g. {"id": "INTEGER PRIMARY KEY", "name": "TEXT"}.

        Returns: (success, message) tuple.
        """
        pass

    @abstractmethod
    def insert(
        self,
        table_name: str,
        data: dict[str, str | int | float | None] | list[dict[str, str | int | float | None]],
    ) -> tuple[bool, str]:
        """Insert one or more rows into a table.

        table_name: Target table name.
        data:       A single {column: value} dict for one row, or a list of
                    such dicts for a batch insert.

        Returns: (success, message) tuple.
        """
        pass

    @abstractmethod
    def update(
        self,
        table_name: str,
        data: dict[str, str | int | float | None],
        conditions: dict[str, str | int | float | None],
    ) -> tuple[bool, str]:
        """Update rows that match the given conditions.

        table_name: Target table name.
        data:       {column: new_value} pairs to set.
        conditions: {column: value} pairs ANDed for the WHERE clause.

        Returns: (success, message) tuple.
        """
        pass

    @abstractmethod
    def retrieve(
        self,
        table_name: str,
        conditions: dict[str, str | int | float | None] | None = None,
    ) -> tuple[bool, list[dict[str, str | int | float | None]] | str]:
        """Retrieve rows from a table, optionally filtered by conditions.

        table_name: Source table name.
        conditions: Optional {column: value} pairs for filtering (AND).
                    If None, all rows are returned.

        Returns: (success, rows_as_list_of_dicts) on success,
                 (success, error_message) on failure.
        """
        pass

    @abstractmethod
    def drop_table(self, table_name: str) -> tuple[bool, str]:
        """Drop a table from the database.

        table_name: Name of the table to drop.

        Returns: (success, message) tuple.
        """
        pass

    @abstractmethod
    def close(self) -> tuple[bool, str]:
        """Cleanly terminate connection to the database.

        Returns: (success, message) tuple.
        """
        pass


if __name__ == "__main__":
    e = SystemExit("You cannot call this file directly.")
    e.code = 1
    raise e
