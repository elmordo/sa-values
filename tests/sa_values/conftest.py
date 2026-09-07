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
from sqlalchemy import Connection, create_engine, Engine, MetaData

from sa_values import SaValues, setup_sa_values
from sa_values import table as table_module


@pytest.fixture(autouse=True)
def reset_value_table(monkeypatch) -> None:
    """Give every test an independent value-table registry."""
    monkeypatch.setattr(table_module, "_metadata", MetaData())
    monkeypatch.setattr(table_module, "_value_table", None)


@pytest.fixture()
def value_manager(db_connection) -> SaValues:
    """Setup the a database and create SaValues instance. The SaValues instance is returned"""
    setup_sa_values(db_connection)
    return SaValues(db_connection)


@pytest.fixture()
def db_connection(db_engine) -> Connection:
    """Connect to a database, using the engine"""
    with db_engine.connect() as connection:
        yield connection


@pytest.fixture()
def db_engine(db_uri) -> Engine:
    """Create database engine from db_url"""
    engine = create_engine(db_uri)
    yield engine
    engine.dispose()


@pytest.fixture(params=["sqlite"])
def db_uri(request: pytest.FixtureRequest) -> str:
    """Provide database uri for various database types. (only sqlite supported for now)"""
    db_type = request.param
    if db_type == "sqlite":
        return "sqlite:///:memory:"
    raise NotImplementedError
