# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.1.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [0.2.0] - 2026-09-15

### Added

- Pluggable data codec architecture with `DataCodec` abstract base class in `sa_values.codecs`.
- Built-in `StringCodec` (default) for UTF-8 string encoding and decoding.
- Built-in `JsonCodec` for serializing and deserializing structured Python objects (dicts, lists, primitives) to/from
  JSON.
- Global default codec configuration via `get_default_codec()` and `set_default_codec()`.
- Support for instance-level codecs via `codec` parameter in `SaValues`.
- `default_codec` parameter in `setup_sa_values()` for setting the default codec during initialization.
- Optional `_type` parameter in `DataCodec.decode()`, `SaValues.get()`, `MultiValueKey.get()`, and
  `MultiValueKey.get_all()` to assist static type inference.
- Custom exception hierarchy in `sa_values.exceptions`:
    - `SaValueException` (base library exception)
    - `ConfigurationError`
    - `InvalidKeyError`
    - `StorageError`
    - `CodecError`
    - `EncodingError`
    - `DecodingError`

### Changed

- **Breaking Change**: Changed the `value` column data type in the `sa_values` table from `String` to `LargeBinary` to
  support binary-encoded values.
- Standardized error handling across setup, teardown, and data operations to raise custom `SaValueException` subclasses.

## [0.1.0] - 2026-09-07

### Added

- Initial release of `sa-values`.
- Core key-value storage powered by SQLAlchemy Core expressions for SQLite databases.
- `setup_sa_values()` function for database table initialization with custom table name support and schema versioning
  marker.
- `teardown_sa_values()` function for dropping storage tables.
- `SaValues` class for managing single-value keys (`get`, `set`, `has`, `delete`, `get_keys`).
- `MultiValueKey` accessor class via `SaValues.multi_value_key()` for managing multi-value keys (`add`, `get`,
  `get_all`, `has`, `delete`, `clear`) with deterministic ordering and duplicate suppression.
- Validation preventing empty string keys for public entries.
- Test suite with pytest and in-memory SQLite fixtures.
