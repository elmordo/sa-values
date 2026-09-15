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
from sqlalchemy import Integer, LargeBinary, String

from sa_values import table as table_module


def test_get_value_table_lazily_creates_default_table() -> None:
    """Test table access with an empty table registry; expect lazy creation of the default table."""
    table = table_module.get_value_table()

    assert table.name == "sa_values"
    assert table.metadata is table_module._metadata
    assert table_module._metadata.tables["sa_values"] is table


def test_get_value_table_returns_the_same_instance() -> None:
    """Test two accesses after lazy creation; expect both calls to return the identical table object."""
    first = table_module.get_value_table()

    assert table_module.get_value_table() is first


def test_value_table_has_expected_columns() -> None:
    """Test the lazily created default table schema; expect id, name, and value columns with required constraints."""
    table = table_module.get_value_table()

    assert list(table.c.keys()) == ["id", "name", "value"]
    assert isinstance(table.c.id.type, Integer)
    assert table.c.id.primary_key
    assert not table.c.id.nullable
    assert isinstance(table.c.name.type, String)
    assert not table.c.name.nullable
    assert isinstance(table.c.value.type, LargeBinary)
    assert not table.c.value.nullable


def test_setup_value_table_selects_a_custom_name() -> None:
    """Test table setup with an empty registry and custom name; expect that name to become the active table."""
    table_module.setup_value_table("application_values")

    table = table_module.get_value_table()
    assert table.name == "application_values"
    assert table_module._metadata.tables["application_values"] is table


def test_setup_value_table_reuses_registered_table() -> None:
    """Test switching between two registered custom names; expect switching back to reuse the original table object."""
    table_module.setup_value_table("application_values")
    first = table_module.get_value_table()

    table_module.setup_value_table("other_values")
    table_module.setup_value_table("application_values")

    assert table_module.get_value_table() is first
