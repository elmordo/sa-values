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


def test_missing_key(value_manager) -> None:
    """Test missing-key reads with only the setup version row present; expect no value and a false presence check."""
    assert value_manager.get("missing") is None
    assert not value_manager.has("missing")


def test_set_get_and_has(value_manager) -> None:
    """Test storing one key with an empty value set; expect get and has to return the stored value and true."""
    value_manager.set("color", "blue")

    assert value_manager.get("color") == "blue"
    assert value_manager.has("color")


def test_set_replaces_existing_values(value_manager, db_connection) -> None:
    """Test replacing a key with two existing values; expect the new value and exactly one database row."""
    multi_value = value_manager.multi_value_key("color")
    multi_value.add("blue")
    multi_value.add("green")

    value_manager.set("color", "red")

    table = get_value_table()
    row_count = db_connection.scalar(
        select(func.count()).select_from(table).where(table.c.name == "color")
    )
    assert value_manager.get("color") == "red"
    assert row_count == 1


def test_set_keeps_oldest_row_when_cleaning_duplicates(
    value_manager, db_connection
) -> None:
    """Test replacing duplicate rows directly seeded for a key; expect the oldest row retained with the new value."""
    table = get_value_table()
    db_connection.execute(
        insert(table),
        [
            {"name": "color", "value": "blue"},
            {"name": "color", "value": "green"},
        ],
    )
    oldest_id = db_connection.scalar(
        select(table.c.id)
        .where(table.c.name == "color")
        .order_by(table.c.id)
        .limit(1)
    )

    value_manager.set("color", "red")

    rows = db_connection.execute(
        select(table.c.id, table.c.value).where(table.c.name == "color")
    ).all()
    assert rows == [(oldest_id, "red")]


def test_get_keys_returns_distinct_sorted_keys(value_manager) -> None:
    """Test key listing after setup and repeated key writes; expect distinct keys sorted lexicographically."""
    value_manager.set("zebra", "one")
    value_manager.set("alpha", "two")
    value_manager.multi_value_key("alpha").add("three")

    assert value_manager.get_keys() == ["", "alpha", "zebra"]


def test_delete_removes_all_values_and_ignores_missing_key(value_manager) -> None:
    """Test deleting a key with two values and an absent key; expect all target values removed without an error."""
    multi_value = value_manager.multi_value_key("color")
    multi_value.add("blue")
    multi_value.add("green")

    value_manager.delete("color")
    value_manager.delete("missing")

    assert value_manager.get("color") is None
    assert multi_value.get_all() == []


def test_empty_string_is_a_valid_value(value_manager) -> None:
    """Test storing an empty string under a non-empty key; expect it to be retrievable and present."""
    value_manager.set("empty-value", "")

    assert value_manager.get("empty-value") == ""
    assert value_manager.has("empty-value")


def test_empty_key_is_rejected(value_manager) -> None:
    """Test empty-key writes and accessors with the setup table present; expect both operations to raise ValueError."""
    with pytest.raises(ValueError, match="key must be non-empty"):
        value_manager.set("", "value")

    with pytest.raises(ValueError, match="key must be non-empty"):
        value_manager.multi_value_key("")


def test_get_raises_storage_error_on_dbapi_error(
    value_manager, db_connection
) -> None:
    """Test get operation when DBAPIError occurs; expect StorageError."""
    with patch.object(
        db_connection,
        "scalar",
        side_effect=DBAPIError("statement", {}, Exception("db error")),
    ):
        with pytest.raises(StorageError, match="Cannot get value of 'color'"):
            value_manager.get("color")


def test_get_keys_raises_storage_error_on_dbapi_error(
    value_manager, db_connection
) -> None:
    """Test get_keys operation when DBAPIError occurs; expect StorageError."""
    with patch.object(
        db_connection,
        "scalars",
        side_effect=DBAPIError("statement", {}, Exception("db error")),
    ):
        with pytest.raises(StorageError, match="Cannot get keys"):
            value_manager.get_keys()


def test_set_raises_storage_error_on_dbapi_error(
    value_manager, db_connection
) -> None:
    """Test set operation when DBAPIError occurs; expect StorageError."""
    with patch.object(
        db_connection,
        "scalars",
        side_effect=DBAPIError("statement", {}, Exception("db error")),
    ):
        with pytest.raises(StorageError, match="Cannot set value of 'color'"):
            value_manager.set("color", "blue")
