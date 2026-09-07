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
from sqlalchemy import inspect

from sa_values import SaValues, setup_sa_values, teardown_sa_values


def test_teardown_drops_the_value_table(db_connection) -> None:
    """Test teardown after default setup; expect the default value table to be removed."""
    setup_sa_values(db_connection)

    teardown_sa_values(db_connection)

    assert "sa_values" not in inspect(db_connection).get_table_names()


def test_teardown_is_idempotent(db_connection) -> None:
    """Test teardown called twice after default setup; expect the second call to succeed with no table."""
    setup_sa_values(db_connection)

    teardown_sa_values(db_connection)
    teardown_sa_values(db_connection)

    assert "sa_values" not in inspect(db_connection).get_table_names()


def test_teardown_drops_a_custom_value_table(db_connection) -> None:
    """Test teardown after custom-table setup; expect the configured custom value table to be removed."""
    setup_sa_values(db_connection, "application_values")

    teardown_sa_values(db_connection)

    assert "application_values" not in inspect(db_connection).get_table_names()


def test_setup_can_reinstall_after_teardown(db_connection) -> None:
    """Test setup after teardown removed a populated table; expect a fresh table with only the version row."""
    setup_sa_values(db_connection)
    SaValues(db_connection).set("color", "blue")
    teardown_sa_values(db_connection)

    setup_sa_values(db_connection)

    values = SaValues(db_connection)
    assert values.get("") == "1"
    assert values.get("color") is None
