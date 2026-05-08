Contributing
============

Please follow these steps to contribute code or documentation to this repository.

Pre-commit and formatting
-------------------------

This project uses `pre-commit` to run formatters and linters automatically on
commit. Please install pre-commit hooks locally:

```bash
pip install pre-commit
pre-commit install
pre-commit run --all-files
```

Formatting policy
-----------------

- Black and Ruff are used for code formatting and linting.
- Line length is set to 100 characters via `pyproject.toml`.
- If you need an exception for a specific long literal, prefer `# noqa: E501`.

Running tests
-------------

Install development/test dependencies (see `dev-requirements.txt`) and ensure
you have a local Postgres and (optionally) Solr instance running if running
integration tests. To run unit tests:

```bash
export DJANGO_SETTINGS_MODULE=ppa.settings
pytest
```

Adapter development
-------------------

- Add adapters under `examples/adapters/` with an `adapter.yaml` and optional
  `templates/` directory.
- Use `python manage.py adapter_validate` to check adapters and
  `python manage.py build_adapter_solr` to inspect generated Solr fields.


