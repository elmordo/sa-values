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
from abc import ABC, abstractmethod
import json
from typing import Any, TypeVar

from sa_values.exceptions import DecodingError, EncodingError


T = TypeVar("T")


class DataCodec(ABC):
    """Data format codec used when storing/retrieving data from `SaValues` storage.

    The class defines two methods:

    * `encode` - used when data is stored into the storage
    * `decode` - used when data is retrieved from the storage
    """

    @abstractmethod
    def encode(self, value: Any) -> bytes:
        """Encode data into the byte format.

        Raises:
            `sa_values.exceptions.EncodingError`: If encoding fails.
        """

    @abstractmethod
    def decode[T](self, value: bytes) -> T:
        """Decode data from the byte format.

        Raises:
            `sa_values.exceptions.DecodeError`: If decoding fails.
        """


class StringCodec(DataCodec):
    """Use strings for storing data.

    Each value is converted into a string. The string representation is returned.
    """

    def encode(self, value: Any) -> bytes:
        try:
            return str(value).encode()
        except UnicodeEncodeError as exc:
            raise EncodingError("Failed to encode value as string") from exc

    def decode(self, value: bytes) -> str:
        try:
            return value.decode()
        except UnicodeDecodeError as exc:
            raise DecodingError("Failed to decode value as string") from exc


class JsonCodec(DataCodec):
    """Use JSON format for stored values"""

    def encode(self, value: Any) -> bytes:
        try:
            return json.dumps(value).encode()
        except (TypeError, ValueError, UnicodeEncodeError) as exc:
            raise EncodingError("Failed to encode value as JSON") from exc

    def decode[T](self, value: bytes) -> T:
        try:
            return json.loads(value)
        except json.JSONDecodeError as exc:
            raise DecodingError("Failed to decode value as JSON") from exc


_default_codec = StringCodec()


def get_default_codec() -> DataCodec:
    """Get default codec."""
    return _default_codec


def set_default_codec(codec: DataCodec) -> None:
    """Set the app-wide default codec.

    The default codec is used when no codec is provided to `sa_values.values`.
    """
    global _default_codec
    _default_codec = codec
