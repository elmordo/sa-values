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
