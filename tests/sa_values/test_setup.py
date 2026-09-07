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
import pytest
from sqlalchemy import inspect, select, update

from sa_values import SaValues, setup_sa_values
from sa_values.table import get_value_table


def test_setup_creates_default_table_and_version_row(db_connection) -> None:
    """Test setup on an empty database; expect the default table and version row to be created."""
    setup_sa_values(db_connection)

    table = get_value_table()
    assert table.name == "sa_values"
    assert "sa_values" in inspect(db_connection).get_table_names()
    assert db_connection.execute(
        select(table.c.name, table.c.value)
    ).all() == [("", "1")]


def test_setup_is_idempotent_and_preserves_values(db_connection) -> None:
    """Test setup twice after storing a value; expect the version and existing value to remain unchanged."""
    setup_sa_values(db_connection)
    values = SaValues(db_connection)
    values.set("color", "blue")

    setup_sa_values(db_connection)

    assert values.get("color") == "blue"
    assert values.get("") == "1"


def test_setup_supports_a_custom_table_name(db_connection) -> None:
    """Test repeated setup with a custom table name on an empty database; expect only that table and its version row."""
    setup_sa_values(db_connection, "application_values")
    setup_sa_values(db_connection, "application_values")

    assert get_value_table().name == "application_values"
    assert inspect(db_connection).get_table_names() == ["application_values"]
    assert SaValues(db_connection).get("") == "1"


def test_setup_rejects_an_incompatible_table_version(db_connection) -> None:
    """Test setup with an existing version row changed to 2; expect ValueError for the incompatible version."""
    setup_sa_values(db_connection)
    table = get_value_table()
    db_connection.execute(
        update(table).where(table.c.name == "").values(value="2")
    )

    with pytest.raises(ValueError, match="Invalid table version: 2"):
        setup_sa_values(db_connection)
