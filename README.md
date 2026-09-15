[![Tests](https://github.com/elmordo/sa-values/actions/workflows/tests.yml/badge.svg)](https://github.com/elmordo/sa-values/actions/workflows/tests.yml)

The `sa-values` (SQLAlchemy values) is designed as light-weight library for storing key-value pairs in database.

# Installation

```shell
pip install sa-values
```

# Quick start

```python
from sqlalchemy import create_engine
from sa_values import setup_sa_values, SaValues

# connect to db and setup sa-values
conn = create_engine("sqlite:///:memory:").connect()
setup_sa_values(conn)

sa_vals = SaValues(conn)
sa_vals.set("key", "value")
print("Stored value: ", sa_vals.get("key"))
```

# Supported DBs

The only officially supported database system is `sqlite`. Other DB systems should work too (experimentally tested on
PostgreSQL), but use it at your own risk.

# Usage

The `sa-values` is based on SQLAlchemy and provides a simple interface for storing and retrieving key-value pairs in a
database.

## Initialization

The `sa-values` use a single table to store all data. Default table name is `sa_values`. Before any operation is
performed, the initialization should be done.

```python
from sqlalchemy import create_engine
from sa_values import setup_sa_values

# connect to db and setup sa-values
conn = create_engine("sqlite:///:memory:").connect()
setup_sa_values(conn)
```

The `setup_sa_values` function accepts the second, optional, parameter `value_table_name`. This can be used to specify a
different table name for storing key-value pairs.

## Single values

When using single values, each key can be stored only once. When setting an exising key, the original value is
overridden.

```python
from sqlalchemy import create_engine
from sa_values import setup_sa_values, SaValues

# connect to db and setup sa-values
conn = create_engine("sqlite:///:memory:").connect()
setup_sa_values(conn)
values = SaValues(conn)

if not values.has("some_value"):
    print("Some_value is not stored")
values.set("some_value", "123")
if values.has("some_value"):
    print("Some_value is stored")
    print("The value is: ", values.get("some_value"))
values.set("some_value", "456")
print("New value is: ", values.get("some_value"))

values.delete("some_value")
if not values.has("some_value"):
    print("Some_value is not stored anymore")

```

## Multiple values

If you want to manage key with more than one value, you can use the `SaValues::multi_value_key(key)`. The method returns
an object for the multi-value key management. Each value must be unique. In case of duplicate values, the second and
following values are ignored.

```python
from sqlalchemy import create_engine
from sa_values import setup_sa_values, SaValues

# connect to db and setup sa-values
conn = create_engine("sqlite:///:memory:").connect()
setup_sa_values(conn)
values = SaValues(conn)

multi_key = values.multi_value_key("multi_key")

multi_key.add("value1")
multi_key.add("value2")
multi_key.add("value2")  # do nothing - each value can be stored only once
multi_key.add("value3")

print("Values: ", multi_key.get_all())  # ["value1", "value2", "value3"]

multi_key.delete("value2")

print("Values: ", multi_key.get())  # ["value1", "value3"]

print("value1 exists: ", multi_key.has("value1"))  # true
print("value10 exists: ", multi_key.has("value10"))  # false

multi_key.clear()  # clear all
```

## Codecs

Codecs define how stored data is serialized into bytes and deserialized back into Python objects.

By default, `sa-values` uses `StringCodec`, which converts values to strings.

### Built-in codecs

The library provides the following built-in codecs in `sa_values.codecs`:

* `StringCodec` (default): Encodes values as UTF-8 string bytes and decodes bytes back to strings.
* `JsonCodec`: Encodes and decodes values as JSON, allowing structured data (dictionaries, lists, numbers, booleans) to
  be stored and retrieved directly.

To use a specific codec, pass it to the `SaValues` constructor:

```python
from sqlalchemy import create_engine
from sa_values import setup_sa_values, SaValues
from sa_values.codecs import JsonCodec

# connect to db and setup sa-values
conn = create_engine("sqlite:///:memory:").connect()
setup_sa_values(conn)

values = SaValues(conn, codec=JsonCodec())

# store structured data
values.set("user_config", {"theme": "dark", "notifications": True, "limit": 50})
print("Config: ", values.get("user_config"))

# multi-value keys with JSON objects
items = values.multi_value_key("items")
items.add({"id": 1, "name": "first"})
items.add({"id": 2, "name": "second"})
print("Items: ", items.get_all())
```

### Global default codec

You can change the default codec used across all `SaValues` instances when no codec is explicitly passed:

```python
from sa_values.codecs import get_default_codec, set_default_codec, JsonCodec

# set JSON codec as the default
set_default_codec(JsonCodec())
```

### Custom codecs

You can implement custom codecs by subclassing `DataCodec` from `sa_values.codecs` and implementing the `encode` and
`decode` methods:

```python
from typing import Any, TypeVar
import msgpack
from sa_values.codecs import DataCodec
from sa_values.exceptions import DecodingError, EncodingError
from sa_values.codecs import DataCodec
from sa_values.exceptions import DecodingError, EncodingError

T = TypeVar("T")


class MsgPackCodec(DataCodec):
    def encode(self, value: Any) -> bytes:
        try:
            return msgpack.packb(value, use_bin_type=True)
        except Exception as exc:
            raise EncodingError("Failed to encode MSGPACK") from exc

    def decode(self, value: bytes, _type: T = Any) -> Any:
        try:
            return msgpack.unpackb(value, raw=False)
        except Exception as exc:
            raise DecodingError("Failed to decode MSGPACK") from exc
```

## Teardown

When the `sa-values` is not needed anymore, it can be tear downed by calling the `teardown_sa_values`

```python
from sqlalchemy import create_engine
from sa_values import SaValues, teardown_sa_values

# connect to db and setup sa-values
conn = create_engine("sqlite:///:memory:").connect()
teardown_sa_values(conn)
```

# Buy me a ~~coffee~~ beer

If you like this library, or you want to support its development, support me by one
cold [beer](https://www.buymeacoffee.com/elmordo). The beer is tasty and full of vitamins :-)
