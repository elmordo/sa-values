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
from sqlalchemy import Connection, create_engine, Engine

from sa_values import SaValues, setup_sa_values


@pytest.fixture()
def value_manager(db_connection) -> SaValues:
    setup_sa_values(db_connection)
    return SaValues(db_connection)


@pytest.fixture()
def db_connection(db_engine) -> Connection:
    return db_engine.connect()


@pytest.fixture()
def db_engine(db_uri) -> Engine:
    return create_engine(db_uri)


@pytest.fixture(params=["sqlite"])
def db_uri(db_type: str) -> str:
    if db_type == "sqlite":
        return "sqlite:///:memory:"
    else:
        raise NotImplementedError
