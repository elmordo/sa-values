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


class SaValueException(Exception):
    """Common base for all exceptions raised by the `sa_values` lib."""


class ConfigurationError(SaValueException, ValueError):
    """Raised when configuration is invalid."""


class InvalidKeyError(SaValueException, KeyError):
    """Raised when an invalid key name is attempted to be stored"""


class StorageError(SaValueException):
    """Raised when a storage operation fails."""


class CodecError(SaValueException, ValueError):
    """Exception raised when codec fails to encode/decode data."""


class EncodingError(CodecError):
    """Exception raised when codec fails to encode data."""


class DecodingError(CodecError):
    """Exception raised when codec fails to decode data."""
