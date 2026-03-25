#!/usr/bin/env python3
""" Implements the integration with SQLite database
"""
from .base import StorageBase

# - [] Add a class variable that may be used (or not) to ensure single / multiple instances allowed
class SQLiteHandler(StorageBase):
    def __init__(self, *, store_connection_data: dict[str, str] = {}):
        """Constructor for the Storage Interface object

        store_connection_data: Dictionary with required fields to connect.
            The caller must have *some* awareness of how to connect, because
            the appropriate arguments must be passed to it, e.g. IP,
            username, password etc.
        """
        pass

    def store_message(self, message: dict[str, str | dict[str, str]]) -> tuple:
        """Stores given message

        message:    Message received. Can come with or without metadata,
            must be JSON encapsulated ({"":""})
        """
        pass

    def retrieve_messages(self, *, date_range: tuple[str, str] | str | None = None):
        """Retrieves messages from the database

        date_range: The date range to retrieve messages for.
            - If unset or invalid retrieve since 24 hours ago
            - If simple string, then consider this as "from" field, up to
                now
            - If tuple, consider values as to-from range (inclusive)
        """
    
    def close(self):
        """Cleanly terminate connection to the database
        """

if __name__ == "__main__":
    e = SystemExit("You cannot call this file directly.")
    e.code = 1
    raise e
