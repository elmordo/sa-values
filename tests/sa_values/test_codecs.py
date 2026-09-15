# MIT License
#
# Copyright (c) 2026 Authors and contributors listed in the AUTHORS file
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
import json
from typing import Any, TypeVar
from unittest.mock import patch

import pytest
from sqlalchemy import insert, select

from sa_values import SaValues, setup_sa_values
from sa_values.codecs import (
    DataCodec,
    get_default_codec,
    JsonCodec,
    set_default_codec,
    StringCodec,
)
from sa_values.exceptions import DecodingError, EncodingError
from sa_values.table import get_value_table


T = TypeVar("T")


def test_string_codec_encode_success() -> None:
    """Test StringCodec encoding various value types; expect correct UTF-8 byte representations."""
    codec = StringCodec()

    assert codec.encode("hello") == b"hello"
    assert codec.encode("") == b""
    assert codec.encode("héllo 🚀") == "héllo 🚀".encode()
    assert codec.encode(123) == b"123"
    assert codec.encode(True) == b"True"
    assert codec.encode(None) == b"None"
    assert codec.encode(["a", "b"]) == b"['a', 'b']"


def test_string_codec_encode_raises_encoding_error() -> None:
    """Test StringCodec encoding unencodable strings; expect EncodingError chained from UnicodeEncodeError."""
    codec = StringCodec()

    # Lone surrogate string cannot be encoded to UTF-8
    unencodable = "\ud800"
    with pytest.raises(EncodingError, match="Failed to encode value as string") as exc_info:
        codec.encode(unencodable)

    assert isinstance(exc_info.value.__cause__, UnicodeEncodeError)


def test_string_codec_decode_success() -> None:
    """Test StringCodec decoding UTF-8 bytes; expect correct string values."""
    codec = StringCodec()

    assert codec.decode(b"hello") == "hello"
    assert codec.decode(b"") == ""
    assert codec.decode("héllo 🚀".encode()) == "héllo 🚀"


def test_string_codec_decode_raises_decoding_error() -> None:
    """Test StringCodec decoding invalid UTF-8 bytes; expect DecodingError chained from UnicodeDecodeError."""
    codec = StringCodec()

    invalid_bytes = b"\xff\xfe"
    with pytest.raises(DecodingError, match="Failed to decode value as string") as exc_info:
        codec.decode(invalid_bytes)

    assert isinstance(exc_info.value.__cause__, UnicodeDecodeError)


def test_json_codec_encode_success() -> None:
    """Test JsonCodec encoding Python objects; expect valid JSON byte representations."""
    codec = JsonCodec()

    assert codec.encode("hello") == b'"hello"'
    assert codec.encode(42) == b"42"
    assert codec.encode(3.14) == b"3.14"
    assert codec.encode(True) == b"true"
    assert codec.encode(None) == b"null"
    assert codec.encode([1, "two", 3.0]) == b'[1, "two", 3.0]'
    assert json.loads(codec.encode({"key": "value", "num": 10})) == {"key": "value", "num": 10}


def test_json_codec_encode_raises_encoding_error_on_type_error() -> None:
    """Test JsonCodec encoding non-serializable objects; expect EncodingError chained from TypeError."""
    codec = JsonCodec()

    with pytest.raises(EncodingError, match="Failed to encode value as JSON") as exc_info:
        codec.encode(object())

    assert isinstance(exc_info.value.__cause__, TypeError)


def test_json_codec_encode_raises_encoding_error_on_value_error_or_surrogate() -> None:
    """Test JsonCodec encoding circular structures or unencodable surrogates; expect EncodingError."""
    codec = JsonCodec()

    # Circular reference raises ValueError during json.dumps
    circular: list[Any] = []
    circular.append(circular)
    with pytest.raises(EncodingError, match="Failed to encode value as JSON") as exc_info:
        codec.encode(circular)

    assert isinstance(exc_info.value.__cause__, ValueError)

    # Simulated UnicodeEncodeError during encoding
    with patch("json.dumps", side_effect=UnicodeEncodeError("utf-8", "\ud800", 0, 1, "surrogate")):
        with pytest.raises(EncodingError, match="Failed to encode value as JSON") as exc_info:
            codec.encode("test")

        assert isinstance(exc_info.value.__cause__, UnicodeEncodeError)


@pytest.mark.parametrize(
    ("value", "expected"),
    [
        (b'"hello"', "hello"),
        (b"42", 42),
        (b"3.14", 3.14),
        (b"true", True),
        (b"null", None),
        (b'[1, "two", 3.0]', [1, "two", 3.0]),
        (b'{"key": "value", "num": 10}', {"key": "value", "num": 10}),
    ],
)
def test_json_codec_decode_success(value: bytes, expected: Any) -> None:
    """Test JsonCodec decoding JSON bytes; expect correct Python objects."""
    codec = JsonCodec()

    assert codec.decode(value) == expected


def test_json_codec_decode_raises_decoding_error() -> None:
    """Test JsonCodec decoding invalid JSON bytes; expect DecodingError chained from JSONDecodeError."""
    codec = JsonCodec()

    with pytest.raises(DecodingError, match="Failed to decode value as JSON") as exc_info:
        codec.decode(b"not valid json")

    assert isinstance(exc_info.value.__cause__, json.JSONDecodeError)


def test_get_default_codec_returns_string_codec() -> None:
    """Test get_default_codec initial return value; expect an instance of StringCodec."""
    default_codec = get_default_codec()

    assert isinstance(default_codec, StringCodec)


def test_set_default_codec_updates_global_codec(monkeypatch) -> None:
    """Test set_default_codec modifies the active default codec; expect get_default_codec to reflect the change."""
    original_codec = get_default_codec()
    monkeypatch.setattr("sa_values.codecs._default_codec", original_codec)

    new_codec = JsonCodec()
    set_default_codec(new_codec)

    assert get_default_codec() is new_codec


def test_sa_values_with_json_codec_single_value(db_connection) -> None:
    """Test SaValues single-value get/set with JsonCodec; expect structured data round-trip and JSON storage."""
    setup_sa_values(db_connection)
    values = SaValues(db_connection, codec=JsonCodec())

    data = {"name": "app", "version": 1, "features": ["auth", "logging"], "active": True}
    values.set("config", data)

    assert values.get("config") == data
    assert values.has("config")

    # Verify underlying stored bytes are JSON formatted
    table = get_value_table()
    raw_bytes = db_connection.scalar(select(table.c.value).where(table.c.name == "config"))
    assert json.loads(raw_bytes) == data


def test_sa_values_with_json_codec_multi_value(db_connection) -> None:
    """Test SaValues multi-value keys with JsonCodec; expect structured items in addition, listing, and deletion."""
    setup_sa_values(db_connection)
    values = SaValues(db_connection, codec=JsonCodec())
    key_accessor = values.multi_value_key("records")

    item1 = {"id": 1, "title": "first"}
    item2 = {"id": 2, "title": "second"}

    key_accessor.add(item1)
    key_accessor.add(item2)

    assert key_accessor.get_all() == [item1, item2]
    assert key_accessor.has(item1)
    assert key_accessor.get(item1) == item1
    assert list(key_accessor) == [item1, item2]

    key_accessor.delete(item1)
    assert key_accessor.get_all() == [item2]
    assert not key_accessor.has(item1)


def test_sa_values_with_custom_codec(db_connection) -> None:
    """Test SaValues with a custom DataCodec implementation; expect custom encoded format in the database."""

    class IntCodec(DataCodec):
        def encode(self, value: Any) -> bytes:
            return int(value).to_bytes(4, byteorder="big", signed=True)

        def decode(self, value: bytes, _type: T = int) -> int:
            return int.from_bytes(value, byteorder="big", signed=True)

    setup_sa_values(db_connection)
    values = SaValues(db_connection, codec=IntCodec())

    values.set("counter", 42)
    assert values.get("counter") == 42

    table = get_value_table()
    raw_bytes = db_connection.scalar(select(table.c.value).where(table.c.name == "counter"))
    assert raw_bytes == (42).to_bytes(4, byteorder="big", signed=True)


def test_sa_values_uses_default_codec_when_omitted(db_connection, monkeypatch) -> None:
    """Test SaValues constructor uses get_default_codec when codec is omitted."""
    custom_codec = JsonCodec()
    monkeypatch.setattr("sa_values.codecs._default_codec", custom_codec)

    setup_sa_values(db_connection)
    values = SaValues(db_connection)

    values.set("payload", {"status": "ok"})
    assert values.get("payload") == {"status": "ok"}


def test_sa_values_raises_encoding_error_on_invalid_data(db_connection) -> None:
    """Test SaValues set and add with incompatible data; expect EncodingError."""
    setup_sa_values(db_connection)
    values = SaValues(db_connection, codec=JsonCodec())

    with pytest.raises(EncodingError, match="Failed to encode value as JSON"):
        values.set("invalid", object())

    with pytest.raises(EncodingError, match="Failed to encode value as JSON"):
        values.multi_value_key("invalid_multi").add(object())


def test_sa_values_raises_decoding_error_on_corrupted_data(db_connection) -> None:
    """Test SaValues get and get_all with unparseable stored bytes; expect DecodingError."""
    setup_sa_values(db_connection)
    table = get_value_table()

    db_connection.execute(
        insert(table),
        [
            {"name": "corrupt_single", "value": b"invalid json content"},
            {"name": "corrupt_multi", "value": b"invalid json content"},
        ],
    )

    values = SaValues(db_connection, codec=JsonCodec())

    with pytest.raises(DecodingError, match="Failed to decode value as JSON"):
        values.get("corrupt_single")

    with pytest.raises(DecodingError, match="Failed to decode value as JSON"):
        values.multi_value_key("corrupt_multi").get_all()
