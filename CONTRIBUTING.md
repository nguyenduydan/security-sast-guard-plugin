# Contributing to Security SAST Guard

Thank you for considering contributing to Security SAST Guard!

## Development Workflow

1. Fork the repository and create your branch from `main`.
2. Install pre-commit hooks:
   ```bash
   pip install pre-commit ruff mypy pytest detect-secrets
   pre-commit install
   pre-commit install --hook-type commit-msg
   ```
3. Make your changes and write unit tests.
4. Ensure all linters and tests pass:
   ```bash
   python -m ruff check .
   python -m ruff format --check .
   python -m mypy --config-file=pyproject.toml control_plane.py src/
   python -m pytest
   ```
5. Commit using Conventional Commits (`feat:`, `fix:`, `docs:`, `refactor:`).
6. Push to your fork and submit a Pull Request.
