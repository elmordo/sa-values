# AGENTS.md

## Project overview

`sa-values` is a small SQLAlchemy Core library for storing single-value and
multi-value string keys. SQLite is the only officially supported database.
The package uses a `src` layout and is built with setuptools.

## Repository layout

- `src/sa_values/`: package source.
- `tests/sa_values/`: pytest suite using in-memory SQLite databases.
- `pyproject.toml`: package metadata, dependencies, and Ruff configuration.
- `.github/workflows/tests.yml`: tests on Python 3.12, 3.13, and 3.14.
- `build/`: generated build output; do not edit it directly.

## Environment and commands

Create or activate a virtual environment, then install the package and test
dependencies:

```shell
python -m pip install -e ".[test]"
```

Run the complete test suite from the repository root:

```shell
python -m pytest
```

Run a focused test file or test when iterating:

```shell
python -m pytest tests/sa_values/test_setup.py
python -m pytest tests/sa_values/test_setup.py::test_setup_is_idempotent_and_preserves_values
```

## Implementation conventions

- Keep package code in `src/sa_values/` and expose intentional public APIs from
  `src/sa_values/__init__.py`.
- Use SQLAlchemy Core expressions and `sqlalchemy.Connection`; this project does
  not use the ORM.
- Leave transaction ownership with callers. Library mutations execute against
  the supplied connection and must not commit or roll back it.
- Preserve the empty-name row used by `setup_sa_values()` as the internal table
  version marker. Public keys must remain non-empty, while values may be empty.
- Preserve deterministic ordering: rows are read in ascending primary-key order,
  and multi-value reads remove duplicates while retaining the oldest order.
- Keep setup and teardown idempotent and support custom table names.
- Add type annotations to new and changed interfaces. Follow the existing Ruff
  style: double quotes, four-space indentation, sorted import sections, and two
  blank lines after imports.
- Retain the existing MIT license header when adding Python source or test files.

## Testing expectations

- Add or update tests for every behavior change and regression fix.
- Reuse fixtures from `tests/sa_values/conftest.py`. Its autouse fixture resets
  the module-level SQLAlchemy metadata and table registry for test isolation.
- Assert both public behavior and database state when row count, ordering,
  deduplication, or schema behavior matters.
- Keep tests independent and use the in-memory SQLite fixture unless support for
  another database is explicitly being developed.
- Run the complete pytest suite before handing off changes. Changes must remain
  compatible with the Python versions in the GitHub Actions matrix.

## Documentation and generated files

Update `README.md` when installation steps or user-visible APIs change. Do not
manually modify generated artifacts under `build/`; regenerate them through the
packaging toolchain when a release task requires it.
