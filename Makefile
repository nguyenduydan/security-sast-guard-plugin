.PHONY: help install test lint format typecheck audit verify clean

PYTHON ?= python

help:
	@echo "Security SAST Guard Development Commands:"
	@echo "  make install     - Install development dependencies in editable mode"
	@echo "  make test        - Run test suite with pytest"
	@echo "  make lint        - Run Ruff format check, Ruff lint, and Pylint"
	@echo "  make format      - Automatically format code with Ruff"
	@echo "  make typecheck   - Run strict static type checking with MyPy"
	@echo "  make audit       - Run full codebase SAST audit"
	@echo "  make verify      - Run complete CI quality verification gate"
	@echo "  make clean       - Remove cache, temporary test artifacts, and build files"

install:
	$(PYTHON) -m pip install --upgrade pip
	$(PYTHON) -m pip install -e ".[dev]"

test:
	$(PYTHON) -m pytest

lint:
	$(PYTHON) -m ruff format --check .
	$(PYTHON) -m ruff check .
	$(PYTHON) -m pylint control_plane.py src/

format:
	$(PYTHON) -m ruff format .
	$(PYTHON) -m ruff check --fix .

typecheck:
	$(PYTHON) -m mypy --config-file=pyproject.toml control_plane.py src/

audit:
	$(PYTHON) control_plane.py audit codebase --level full

verify: lint typecheck test
	@echo "All verification checks passed successfully!"

clean:
	find . -type d -name "__pycache__" -exec rm -rf {} + 2>/dev/null || true
	find . -type d -name ".pytest_cache" -exec rm -rf {} + 2>/dev/null || true
	find . -type d -name ".mypy_cache" -exec rm -rf {} + 2>/dev/null || true
	find . -type d -name ".ruff_cache" -exec rm -rf {} + 2>/dev/null || true
	find . -type f -name "*.pyc" -delete 2>/dev/null || true
