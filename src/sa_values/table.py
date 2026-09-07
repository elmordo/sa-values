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
from sqlalchemy import Column, Integer, MetaData, String, Table


_metadata = MetaData()

_value_table = None


def get_value_table() -> Table:
    """Get the value table. If the table instance does not exists, create it"""
    global _value_table

    if _value_table is None:
        _value_table = _create_value_table()
    return _value_table


def setup_value_table(table_name: str = "sa_values") -> None:
    """Create the value table with the given name"""
    global _value_table
    _value_table = _create_value_table(table_name)


def _create_value_table(table_name: str = "sa_values") -> Table:
    """Create and return the value table with the given name."""
    if (existing_table := _metadata.tables.get(table_name)) is not None:
        return existing_table

    return Table(
        table_name,
        _metadata,
        Column("id", Integer, primary_key=True),
        Column("name", String, nullable=False),
        Column("value", String, nullable=False),
    )
