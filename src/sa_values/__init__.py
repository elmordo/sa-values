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

from collections.abc import Iterator

from sqlalchemy import Connection, delete, insert, select, update

from .table import configuration_value


class ConfigurationValues:
    """Interface for `gx.modules.common.orm.ConfigurationValue`.

    Features:

    * manage single value keys (get, set, has, delete)
    * manage multi-value keys. The multi-value accessor is provided by calling `multi_value_key` method.

    The multi-value keys interface is provided by the `MultiValueKey` class.

    Mutations flush the session; the caller owns the transaction. Keys and values
    are strings, including empty strings.
    """

    def __init__(self, connection: Connection):
        self.connection: Connection = connection

    def get(self, key: str) -> str | None:
        """Return the oldest value by row ID, or None if the key is absent."""
        stmt = (
            select(configuration_value.c.value)
            .where(configuration_value.c.name == key)
            .order_by(configuration_value.c.id)
            .limit(1)
        )
        return self.connection.scalar(stmt)

    def get_keys(self) -> list[str]:
        """Return all keys."""
        stmt = (
            select(configuration_value.c.name)
            .distinct()
            .order_by(configuration_value.c.name)
        )
        return list(self.connection.scalars(stmt))

    def set(self, key: str, value: str) -> None:
        """Store exactly one value for the key, replacing any existing values."""
        stmt = (
            select(configuration_value.c.id)
            .where(configuration_value.c.name == key)
            .order_by(configuration_value.c.id)
        )
        item_ids = list(self.connection.scalars(stmt))
        if item_ids:
            self.connection.execute(
                update(configuration_value)
                .where(configuration_value.c.id == item_ids[0])
                .values(value=value),
            )
            if len(item_ids) > 1:
                self.connection.execute(
                    delete(configuration_value).where(
                        configuration_value.c.id.in_(item_ids[1:])
                    ),
                )
        else:
            self.connection.execute(
                insert(configuration_value).values(name=key, value=value)
            )

    def has(self, key: str) -> bool:
        """Return whether the key has any stored values."""
        return self.get(key) is not None

    def delete(self, key: str) -> None:
        """Remove all values for the key; missing keys are ignored."""
        self.multi_value_key(key).clear()

    def multi_value_key(self, key: str) -> MultiValueKey:
        """Return an accessor sharing this session, without creating any rows."""
        return MultiValueKey(self.connection, key)


class MultiValueKey:
    """Access to multi-value configuration keys.

    Features:

    * iterate over values
    * clear all values
    * get all values
    * manage values (get, set, has, delete)

    Repeated set calls store each value only once for the key. This does not
    guarantee uniqueness across concurrent writers. Reads return distinct values
    in oldest-row order. Mutations flush, leaving transaction control to the caller.
    """

    def __init__(self, connection: Connection, key: str):
        self.connection = connection
        self.key = key

    def __iter__(self) -> Iterator[str]:
        return iter(self.get_all())

    def get_all(self) -> list[str]:
        """Return distinct values in oldest-row order, or an empty list."""
        stmt = (
            select(configuration_value.c.value)
            .where(configuration_value.c.name == self.key)
            .order_by(configuration_value.c.id)
        )
        return list(dict.fromkeys(self.connection.scalars(stmt)))

    def get(self, value: str) -> str | None:
        """Return the matching string, or None if it is absent."""
        stmt = (
            select(configuration_value.c.value)
            .where(
                configuration_value.c.name == self.key,
                configuration_value.c.value == value,
            )
            .limit(1)
        )
        return self.connection.scalar(stmt)

    def has(self, value: str) -> bool:
        """Return whether this key contains the value."""
        return self.get(value) is not None

    def set(self, value: str) -> None:
        """Add the value if absent, leaving other values intact."""
        if not self.has(value):
            self.connection.execute(
                insert(configuration_value).values(name=self.key, value=value)
            )

    def delete(self, value: str) -> None:
        """Remove every matching row; missing values are ignored."""
        self.connection.execute(
            delete(configuration_value).where(
                configuration_value.c.name == self.key,
                configuration_value.c.value == value,
            ),
        )

    def clear(self) -> None:
        """Remove all values for this key; missing keys are ignored."""
        self.connection.execute(
            delete(configuration_value).where(configuration_value.c.name == self.key)
        )
