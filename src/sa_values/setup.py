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
from __future__ import annotations

from sqlalchemy import Connection
from sqlalchemy.sql.ddl import CreateTable, DropTable

from sa_values.table import setup_value_table

from .table import get_value_table
from .values import Values


_TABLE_VERSION = 1


def setup_sa_values(
    connection: Connection, value_table_name: str | None = None
) -> None:
    if value_table_name is not None:
        setup_value_table(value_table_name)

    _create_table(connection)

    values = Values(connection)
    values._allow_empty = True

    if not values.has(""):
        values.set("", str(_TABLE_VERSION))
    else:
        current_version = int(values.get(""))
        if current_version != _TABLE_VERSION:
            raise ValueError(f"Invalid table version: {current_version}")


def teardown_sa_values(connection: Connection) -> None:
    _drop_table(connection)


def _create_table(connection: Connection) -> None:
    create_stmt = CreateTable(get_value_table(), if_not_exists=True)
    connection.execute(create_stmt)


def _drop_table(connection: Connection) -> None:
    stmt = DropTable(get_value_table(), if_exists=True)
    connection.execute(stmt)
