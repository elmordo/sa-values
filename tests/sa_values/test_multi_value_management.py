# MIT License
#
# Copyright (c) [YEAR] [COPYRIGHT HOLDER]
#
# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the "Software"), to deal
# in the Software without restriction, including without limitation the rights
# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:
#
# The above copyright notice and this permission notice shall be included in all
# copies or substantial portions of the Software.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
# SOFTWARE.
from unittest.mock import patch

import pytest
from sqlalchemy import func, insert, select
from sqlalchemy.exc import DBAPIError

from sa_values.exceptions import StorageError
from sa_values.table import get_value_table


def test_getting_accessor_does_not_create_a_value(value_manager, db_connection) -> None:
    """Test creating an accessor for an unused key; expect no row to be added."""
    value_manager.multi_value_key("colors")

    table = get_value_table()
    row_count = db_connection.scalar(
        select(func.count()).select_from(table).where(table.c.name == "colors")
    )
    assert row_count == 0


def test_set_get_has_and_iteration_preserve_insertion_order(value_manager) -> None:
    """Test three values added to an unused key; expect lookup, presence, and iteration in insertion order."""
    colors = value_manager.multi_value_key("colors")
    colors.add("blue")
    colors.add("green")
    colors.add("red")

    assert colors.get("green") == "green"
    assert colors.get("missing") is None
    assert colors.has("red")
    assert not colors.has("missing")
    assert colors.get_all() == ["blue", "green", "red"]


def test_repeated_set_does_not_insert_duplicates(value_manager, db_connection) -> None:
    """Test adding the same value twice to an unused key; expect one row and one returned value."""
    colors = value_manager.multi_value_key("colors")

    colors.add("blue")
    colors.add("blue")

    table = get_value_table()
    row_count = db_connection.scalar(
        select(func.count())
        .select_from(table)
        .where(table.c.name == "colors", table.c.value == "blue".encode())
    )
    assert row_count == 1
    assert colors.get_all() == ["blue"]


def test_get_all_suppresses_existing_duplicate_rows(value_manager, db_connection) -> None:
    """Test reading a key seeded with duplicate rows; expect distinct values in their oldest-row order."""
    table = get_value_table()
    db_connection.execute(
        insert(table),
        [
            {"name": "colors", "value": "blue".encode()},
            {"name": "colors", "value": "green".encode()},
            {"name": "colors", "value": "blue".encode()},
        ],
    )

    assert value_manager.multi_value_key("colors").get_all() == ["blue", "green"]


def test_delete_removes_every_matching_row(value_manager, db_connection) -> None:
    """Test deleting a duplicated value from seeded rows; expect every matching row removed and other values kept."""
    table = get_value_table()
    db_connection.execute(
        insert(table),
        [
            {"name": "colors", "value": "blue".encode()},
            {"name": "colors", "value": "blue".encode()},
            {"name": "colors", "value": "green".encode()},
        ],
    )
    colors = value_manager.multi_value_key("colors")

    colors.delete("blue")
    colors.delete("missing")

    assert colors.get_all() == ["green"]


def test_clear_only_removes_values_for_its_key(value_manager) -> None:
    """Test clearing one of two populated keys; expect that key empty while the other remains unchanged."""
    colors = value_manager.multi_value_key("colors")
    sizes = value_manager.multi_value_key("sizes")
    colors.add("blue")
    colors.add("green")
    sizes.add("large")

    colors.clear()
    colors.clear()

    assert colors.get_all() == []
    assert sizes.get_all() == ["large"]


def test_empty_string_is_a_valid_value(value_manager) -> None:
    """Test adding an empty string to an unused multi-value key; expect it to be stored and reported as present."""
    values = value_manager.multi_value_key("values")

    values.add("")

    assert values.get("") == ""
    assert values.has("")
    assert values.get_all() == [""]


def test_empty_key_is_rejected(value_manager) -> None:
    """Test creating a multi-value accessor with an empty key; expect ValueError before any row is created."""
    with pytest.raises(ValueError, match="key must be non-empty"):
        value_manager.multi_value_key("")


def test_get_all_raises_storage_error_on_dbapi_error(value_manager, db_connection) -> None:
    """Test get_all operation when DBAPIError occurs; expect StorageError."""
    with patch.object(
        db_connection,
        "scalars",
        side_effect=DBAPIError("statement", {}, Exception("db error")),
    ):
        with pytest.raises(StorageError, match="Cannot get all values of 'colors'"):
            value_manager.multi_value_key("colors").get_all()


def test_get_raises_storage_error_on_dbapi_error(value_manager, db_connection) -> None:
    """Test get operation when DBAPIError occurs; expect StorageError."""
    with patch.object(
        db_connection,
        "scalar",
        side_effect=DBAPIError("statement", {}, Exception("db error")),
    ):
        with pytest.raises(StorageError, match="Cannot get value of 'colors'"):
            value_manager.multi_value_key("colors").get("blue")


def test_add_raises_storage_error_on_dbapi_error(value_manager, db_connection) -> None:
    """Test add operation when DBAPIError occurs on execute; expect StorageError."""
    with patch.object(
        db_connection,
        "execute",
        side_effect=DBAPIError("statement", {}, Exception("db error")),
    ):
        with pytest.raises(StorageError, match="Cannot add value to 'colors'"):
            value_manager.multi_value_key("colors").add("blue")


def test_delete_raises_storage_error_on_dbapi_error(value_manager, db_connection) -> None:
    """Test delete operation when DBAPIError occurs; expect StorageError."""
    with patch.object(
        db_connection,
        "execute",
        side_effect=DBAPIError("statement", {}, Exception("db error")),
    ):
        with pytest.raises(StorageError, match="Cannot delete value of 'colors'"):
            value_manager.multi_value_key("colors").delete("blue")


def test_clear_raises_storage_error_on_dbapi_error(value_manager, db_connection) -> None:
    """Test clear operation when DBAPIError occurs; expect StorageError."""
    with patch.object(
        db_connection,
        "execute",
        side_effect=DBAPIError("statement", {}, Exception("db error")),
    ):
        with pytest.raises(StorageError, match="Cannot clear values of 'colors'"):
            value_manager.multi_value_key("colors").clear()
