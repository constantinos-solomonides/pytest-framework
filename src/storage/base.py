#!/usr/bin/env python3
"""Storage handler base (abstract) class.

Provides the signature all subclasses must implement to ensure compliance with
the base
"""

from abc import ABC, abstractmethod


# NOTE-s
# - It *will* need to be expanded to store other types of values as well. In due time. In due time
# - There's no validation done at the storage level
# - There's no privilege separation taking place
# - Functionalities will be implemented as needed for this (bottom-up approach)
class StorageBase(ABC):
    @abstractmethod
    def __init__(self, *, store_connection_data: dict[str, str] = {}):
        """Constructor for the Storage Interface object

        store_connection_data: Dictionary with required fields to connect.
            The caller must have *some* awareness of how to connect, because
            the appropriate arguments must be passed to it, e.g. IP,
            username, password etc.
        """
        pass

    @abstractmethod
    def store_message(self, message: dict[str, str | dict[str, str]]) -> tuple:
        """Stores given message

        message:    Message received. Can come with or without metadata,
            must be JSON encapsulated ({"":""})
        """
        pass

    @abstractmethod
    def retrieve_messages(self, *, date_range: tuple[str, str] | str | None = None):
        """Retrieves messages from the database

        date_range: The date range to retrieve messages for.
            - If unset or invalid retrieve since 24 hours ago
            - If simple string, then consider this as "from" field, up to
                now
            - If tuple, consider values as to-from range (inclusive)
        """


if __name__ == "__main__":
    e = SystemExit("You cannot call this file directly. Include to use StorageBase instead")
    e.code = 1
    raise e
