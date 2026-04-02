"""Unit tests for SQLite handler.

Ensures that the basic functionalities can be done with the database:
    * Connect to it
    * Create table
    * Add values
    * Retrieve values
    * Update values
    * Drop table

Tests added:
    * Rows that are primary keys respect the limitation of unique entries
    * Validate that not-null can be given and enforced

Used for TDD (Test Driven Development), remains as UT (Unit Tests)
"""

from src.storage.sqlite_handler import SQLiteHandler

# ======================================================================
# Connection, singleton, and environment-based configuration
# ======================================================================


class TestSQLiteHandlerConnection:
    """Verify connection lifecycle, singleton enforcement, and env config."""

    def test_handler_connects_with_explicit_path(self, tmp_path):
        """An explicit db_path produces a connected handler."""
        db = str(tmp_path / "explicit.db")
        handler = SQLiteHandler(store_connection_data={"db_path": db})
        assert handler.connection is not None
        assert handler.db_path == db
        handler.close()

    def test_singleton_returns_same_instance_for_same_path(self, tmp_path):
        """Two constructions with the same path yield the identical object."""
        db = str(tmp_path / "single.db")
        h1 = SQLiteHandler(store_connection_data={"db_path": db})
        h2 = SQLiteHandler(store_connection_data={"db_path": db})
        assert h1 is h2
        h1.close()

    def test_distinct_paths_yield_distinct_instances(self, tmp_path):
        """Different paths produce independent handler objects."""
        h1 = SQLiteHandler(store_connection_data={"db_path": str(tmp_path / "a.db")})
        h2 = SQLiteHandler(store_connection_data={"db_path": str(tmp_path / "b.db")})
        assert h1 is not h2
        h1.close()
        h2.close()

    def test_reads_db_path_from_environment(self, tmp_path, monkeypatch):
        """Falls back to SQLITE_DB_PATH env var when no explicit path given."""
        db = str(tmp_path / "env.db")
        monkeypatch.setenv("SQLITE_DB_PATH", db)
        handler = SQLiteHandler()
        assert handler.db_path == db
        handler.close()

    def test_defaults_to_memory_without_any_config(self, monkeypatch):
        """Uses :memory: when neither explicit path nor env var is set."""
        monkeypatch.delenv("SQLITE_DB_PATH", raising=False)
        handler = SQLiteHandler()
        assert handler.db_path == ":memory:"
        handler.close()

    def test_close_deregisters_singleton(self, tmp_path):
        """After close(), the path is removed from the instance registry."""
        db = str(tmp_path / "dereg.db")
        handler = SQLiteHandler(store_connection_data={"db_path": db})
        handler.close()
        assert db not in SQLiteHandler.instances

    def test_close_is_idempotent(self, tmp_path):
        """Calling close() twice does not raise or return failure."""
        db = str(tmp_path / "idem.db")
        handler = SQLiteHandler(store_connection_data={"db_path": db})
        ok1, _ = handler.close()
        ok2, _ = handler.close()
        assert ok1
        assert ok2

    def test_new_handler_after_close_reconnects(self, tmp_path):
        """A fresh handler can be created for a path after closing the old one."""
        db = str(tmp_path / "reopen.db")
        h1 = SQLiteHandler(store_connection_data={"db_path": db})
        h1.close()
        h2 = SQLiteHandler(store_connection_data={"db_path": db})
        assert h2.connection is not None
        assert h2 is not h1 or h2.connection is not None
        h2.close()


# ======================================================================
# Table management
# ======================================================================


class TestSQLiteHandlerTableOperations:
    """Verify table creation, dropping, and error paths."""

    def test_initialise_table_creates_table(self, sqlitehandler):
        """A table is created and can be queried."""
        ok, msg = sqlitehandler.initialise_table("t_create", {"id": "INTEGER PRIMARY KEY", "name": "TEXT"})
        assert ok, msg
        ok, rows = sqlitehandler.retrieve("t_create")
        assert ok
        assert rows == []
        sqlitehandler.drop_table("t_create")

    def test_initialise_table_is_idempotent(self, sqlitehandler):
        """Creating the same table twice succeeds (IF NOT EXISTS)."""
        schema = {"id": "INTEGER", "val": "TEXT"}
        ok1, _ = sqlitehandler.initialise_table("t_idem", schema)
        ok2, _ = sqlitehandler.initialise_table("t_idem", schema)
        assert ok1 and ok2
        sqlitehandler.drop_table("t_idem")

    def test_initialise_multiple_tables(self, sqlitehandler):
        """Several independent tables can coexist."""
        ok_a, _ = sqlitehandler.initialise_table("t_multi_a", {"id": "INTEGER"})
        ok_b, _ = sqlitehandler.initialise_table("t_multi_b", {"name": "TEXT"})
        assert ok_a and ok_b
        ok, _ = sqlitehandler.retrieve("t_multi_a")
        assert ok
        ok, _ = sqlitehandler.retrieve("t_multi_b")
        assert ok
        sqlitehandler.drop_table("t_multi_a")
        sqlitehandler.drop_table("t_multi_b")

    def test_initialise_table_rejects_empty_schema(self, sqlitehandler):
        """An empty schema is refused."""
        ok, _ = sqlitehandler.initialise_table("t_empty", {})
        assert not ok

    def test_initialise_table_rejects_empty_name(self, sqlitehandler):
        """An empty table name is refused."""
        ok, _ = sqlitehandler.initialise_table("", {"id": "INTEGER"})
        assert not ok

    def test_drop_table_removes_table(self, sqlitehandler):
        """After dropping, the table is no longer queryable."""
        sqlitehandler.initialise_table("t_drop", {"id": "INTEGER"})
        ok, msg = sqlitehandler.drop_table("t_drop")
        assert ok, msg
        ok, _ = sqlitehandler.retrieve("t_drop")
        assert not ok

    def test_drop_nonexistent_table_succeeds(self, sqlitehandler):
        """Dropping a table that does not exist is not an error (IF EXISTS)."""
        ok, _ = sqlitehandler.drop_table("no_such_table")
        assert ok


# ======================================================================
# Insert
# ======================================================================


class TestSQLiteHandlerInsert:
    """Verify single-row and batch inserts."""

    def test_insert_single_row(self, sqlitehandler):
        """A single dict is inserted as one row."""
        sqlitehandler.initialise_table("t_ins1", {"id": "INTEGER", "name": "TEXT"})
        ok, msg = sqlitehandler.insert("t_ins1", {"id": 1, "name": "Alice"})
        assert ok, msg
        ok, rows = sqlitehandler.retrieve("t_ins1")
        assert ok and len(rows) == 1
        assert rows[0]["name"] == "Alice"
        sqlitehandler.drop_table("t_ins1")

    def test_insert_multiple_rows(self, sqlitehandler):
        """A list of dicts is inserted as a batch."""
        sqlitehandler.initialise_table("t_ins_m", {"id": "INTEGER", "name": "TEXT"})
        batch = [
            {"id": 1, "name": "Alice"},
            {"id": 2, "name": "Bob"},
            {"id": 3, "name": "Carol"},
        ]
        ok, msg = sqlitehandler.insert("t_ins_m", batch)
        assert ok, msg
        ok, rows = sqlitehandler.retrieve("t_ins_m")
        assert ok and len(rows) == 3
        sqlitehandler.drop_table("t_ins_m")

    def test_insert_into_multiple_tables(self, sqlitehandler):
        """Rows can be inserted into different tables independently."""
        sqlitehandler.initialise_table("t_ins_ta", {"id": "INTEGER", "v": "TEXT"})
        sqlitehandler.initialise_table("t_ins_tb", {"key": "TEXT", "val": "REAL"})

        ok_a, _ = sqlitehandler.insert("t_ins_ta", {"id": 1, "v": "hello"})
        ok_b, _ = sqlitehandler.insert("t_ins_tb", {"key": "pi", "val": 3.14})
        assert ok_a and ok_b

        ok, rows_a = sqlitehandler.retrieve("t_ins_ta")
        assert ok and len(rows_a) == 1
        ok, rows_b = sqlitehandler.retrieve("t_ins_tb")
        assert ok and len(rows_b) == 1

        sqlitehandler.drop_table("t_ins_ta")
        sqlitehandler.drop_table("t_ins_tb")

    def test_insert_supports_null_values(self, sqlitehandler):
        """None values are stored as SQL NULL."""
        sqlitehandler.initialise_table("t_ins_null", {"id": "INTEGER", "opt": "TEXT"})
        ok, msg = sqlitehandler.insert("t_ins_null", {"id": 1, "opt": None})
        assert ok, msg
        ok, rows = sqlitehandler.retrieve("t_ins_null")
        assert ok and rows[0]["opt"] is None
        sqlitehandler.drop_table("t_ins_null")

    def test_insert_rejects_null_values_if_not_null_given(self, sqlitehandler):
        """None values are stored as SQL NULL."""
        sqlitehandler.initialise_table("t_ins_not_null", {"id": "INTEGER", "opt": "TEXT NOT NULL"})
        ok, msg = sqlitehandler.insert("t_ins_not_null", {"id": 1, "opt": None})
        assert not ok, msg
        ok, rows = sqlitehandler.retrieve("t_ins_not_null")
        assert ok and len(rows) == 0
        sqlitehandler.drop_table("t_ins_not_null")

    def test_insert_rejects_empty_dict(self, sqlitehandler):
        """Empty data dict is refused."""
        sqlitehandler.initialise_table("t_ins_ed", {"id": "INTEGER"})
        ok, _ = sqlitehandler.insert("t_ins_ed", {})
        assert not ok
        sqlitehandler.drop_table("t_ins_ed")

    def test_insert_rejects_empty_list(self, sqlitehandler):
        """Empty data list is refused."""
        sqlitehandler.initialise_table("t_ins_el", {"id": "INTEGER"})
        ok, _ = sqlitehandler.insert("t_ins_el", [])
        assert not ok
        sqlitehandler.drop_table("t_ins_el")

    def test_insert_into_nonexistent_table_fails(self, sqlitehandler):
        """Inserting into a missing table returns a failure tuple."""
        ok, _ = sqlitehandler.insert("no_such_table", {"id": 1})
        assert not ok

    def test_primary_key_rejects_duplicates(self, sqlitehandler):
        """Inserting the same primary key twice fails"""
        ok, msg = sqlitehandler.initialise_table("t_primary_keys", {"id": "INTEGER PRIMARY KEY", "name": "TEXT"})
        assert ok, msg
        ok, _ = sqlitehandler.insert("t_primary_keys", {"id": 1, "name": "First"})
        assert ok
        ok, _ = sqlitehandler.insert("t_primary_keys", {"id": 1, "name": "Second"})
        assert not ok
        ok, rows = sqlitehandler.retrieve("t_primary_keys")
        assert ok and len(rows) == 1

        sqlitehandler.drop_table("t_create")


# ======================================================================
# Retrieve
# ======================================================================


class TestSQLiteHandlerRetrieve:
    """Verify retrieval with and without filters."""

    def test_retrieve_all_rows(self, sqlitehandler):
        """Without conditions, all rows are returned."""
        sqlitehandler.initialise_table("t_ret_all", {"id": "INTEGER", "v": "TEXT"})
        sqlitehandler.insert("t_ret_all", [{"id": 1, "v": "x"}, {"id": 2, "v": "y"}])
        ok, rows = sqlitehandler.retrieve("t_ret_all")
        assert ok and len(rows) == 2
        sqlitehandler.drop_table("t_ret_all")

    def test_retrieve_with_conditions_filters_rows(self, sqlitehandler):
        """Only rows matching conditions are returned."""
        sqlitehandler.initialise_table("t_ret_f", {"id": "INTEGER", "v": "TEXT"})
        sqlitehandler.insert("t_ret_f", [{"id": 1, "v": "x"}, {"id": 2, "v": "y"}])
        ok, rows = sqlitehandler.retrieve("t_ret_f", conditions={"v": "y"})
        assert ok and len(rows) == 1
        assert rows[0]["id"] == 2
        sqlitehandler.drop_table("t_ret_f")

    def test_retrieve_with_multiple_conditions(self, sqlitehandler):
        """Multiple conditions are ANDed together."""
        sqlitehandler.initialise_table("t_ret_mc", {"id": "INTEGER", "a": "TEXT", "b": "TEXT"})
        sqlitehandler.insert(
            "t_ret_mc",
            [
                {"id": 1, "a": "x", "b": "1"},
                {"id": 2, "a": "x", "b": "2"},
                {"id": 3, "a": "y", "b": "1"},
            ],
        )
        ok, rows = sqlitehandler.retrieve("t_ret_mc", conditions={"a": "x", "b": "1"})
        assert ok and len(rows) == 1
        assert rows[0]["id"] == 1
        sqlitehandler.drop_table("t_ret_mc")

    def test_retrieve_returns_empty_list_when_no_match(self, sqlitehandler):
        """Conditions that match nothing yield an empty list, not an error."""
        sqlitehandler.initialise_table("t_ret_nm", {"id": "INTEGER"})
        sqlitehandler.insert("t_ret_nm", {"id": 1})
        ok, rows = sqlitehandler.retrieve("t_ret_nm", conditions={"id": 999})
        assert ok and rows == []
        sqlitehandler.drop_table("t_ret_nm")

    def test_retrieve_returns_dicts(self, sqlitehandler):
        """Each returned row is a plain dict with column-name keys."""
        sqlitehandler.initialise_table("t_ret_dict", {"id": "INTEGER", "name": "TEXT"})
        sqlitehandler.insert("t_ret_dict", {"id": 1, "name": "Alice"})
        ok, rows = sqlitehandler.retrieve("t_ret_dict")
        assert ok
        assert isinstance(rows, list)
        assert isinstance(rows[0], dict)
        assert set(rows[0].keys()) == {"id", "name"}
        sqlitehandler.drop_table("t_ret_dict")

    def test_retrieve_from_nonexistent_table_fails(self, sqlitehandler):
        """Querying a missing table returns a failure tuple."""
        ok, _ = sqlitehandler.retrieve("ghost_table")
        assert not ok


# ======================================================================
# Update
# ======================================================================


class TestSQLiteHandlerUpdate:
    """Verify row updates."""

    def test_update_modifies_matching_rows(self, sqlitehandler):
        """Rows matching conditions are updated; others untouched."""
        sqlitehandler.initialise_table("t_upd", {"id": "INTEGER", "v": "TEXT"})
        sqlitehandler.insert("t_upd", [{"id": 1, "v": "old"}, {"id": 2, "v": "keep"}])

        ok, msg = sqlitehandler.update("t_upd", {"v": "new"}, {"id": 1})
        assert ok, msg

        ok, rows = sqlitehandler.retrieve("t_upd", conditions={"id": 1})
        assert ok and rows[0]["v"] == "new"
        ok, rows = sqlitehandler.retrieve("t_upd", conditions={"id": 2})
        assert ok and rows[0]["v"] == "keep"
        sqlitehandler.drop_table("t_upd")

    def test_update_multiple_columns(self, sqlitehandler):
        """Several columns can be updated in one call."""
        sqlitehandler.initialise_table("t_upd_mc", {"id": "INTEGER", "a": "TEXT", "b": "TEXT"})
        sqlitehandler.insert("t_upd_mc", {"id": 1, "a": "old_a", "b": "old_b"})
        ok, msg = sqlitehandler.update("t_upd_mc", {"a": "new_a", "b": "new_b"}, {"id": 1})
        assert ok, msg
        ok, rows = sqlitehandler.retrieve("t_upd_mc", conditions={"id": 1})
        assert ok and rows[0]["a"] == "new_a" and rows[0]["b"] == "new_b"
        sqlitehandler.drop_table("t_upd_mc")

    def test_update_with_no_match_reports_zero_rows(self, sqlitehandler):
        """Updating with unmatched conditions succeeds but changes nothing."""
        sqlitehandler.initialise_table("t_upd0", {"id": "INTEGER", "v": "TEXT"})
        sqlitehandler.insert("t_upd0", {"id": 1, "v": "x"})
        ok, msg = sqlitehandler.update("t_upd0", {"v": "y"}, {"id": 999})
        assert ok
        assert " 0 " in msg
        sqlitehandler.drop_table("t_upd0")

    def test_update_rejects_empty_data(self, sqlitehandler):
        """Empty data dict is refused."""
        sqlitehandler.initialise_table("t_upd_e", {"id": "INTEGER"})
        ok, _ = sqlitehandler.update("t_upd_e", {}, {"id": 1})
        assert not ok
        sqlitehandler.drop_table("t_upd_e")

    def test_update_rejects_empty_conditions(self, sqlitehandler):
        """Empty conditions are refused to prevent accidental full-table updates."""
        sqlitehandler.initialise_table("t_upd_ec", {"id": "INTEGER", "v": "TEXT"})
        ok, _ = sqlitehandler.update("t_upd_ec", {"v": "x"}, {})
        assert not ok
        sqlitehandler.drop_table("t_upd_ec")


# ======================================================================
# Operations after close
# ======================================================================


class TestSQLiteHandlerPostClose:
    """Verify graceful failure once the connection has been closed."""

    def test_all_operations_fail_after_close(self, tmp_path):
        """Every mutating and querying method returns (False, ...) after close."""
        db = str(tmp_path / "closed.db")
        handler = SQLiteHandler(store_connection_data={"db_path": db})
        handler.initialise_table("t_pc", {"id": "INTEGER"})
        handler.close()

        ok, _ = handler.initialise_table("t_pc2", {"id": "INTEGER"})
        assert not ok, "initialise_table should fail after close"

        ok, _ = handler.insert("t_pc", {"id": 1})
        assert not ok, "insert should fail after close"

        ok, _ = handler.retrieve("t_pc")
        assert not ok, "retrieve should fail after close"

        ok, _ = handler.update("t_pc", {"id": 2}, {"id": 1})
        assert not ok, "update should fail after close"

        ok, _ = handler.drop_table("t_pc")
        assert not ok, "drop_table should fail after close"
