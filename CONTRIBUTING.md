# Developer & Contributor Guide (CONTRIBUTING.md)

Thank you for contributing to **Security SAST Guard**! This document provides instructions for setting up your development environment, running tests, and submitting contributions.

---

## 🛠️ Development Environment Setup

### 1. Prerequisites
- **Python:** `>= 3.12`
- **Git:** `>= 2.30`

### 2. Install Development Dependencies
```bash
# Clone the repository
git clone https://github.com/nguyenduydan/security-sast-guard-plugin.git
cd security-sast-guard-plugin

# Install developer tools (linter, formatter, type checker, testing, secrets detector)
pip install pre-commit ruff mypy pytest detect-secrets pylint
```

### 3. Enable Git Pre-Commit Hooks
```bash
# Install pre-commit hook (runs linter & type checks before each commit)
pre-commit install

# Install commit-msg hook (enforces Conventional Commits format)
pre-commit install --hook-type commit-msg
```

---

## 🚦 Local Quality Gate & Verification

Before submitting a Pull Request, ensure all local verification checks pass:

```bash
# 1. Run Ruff Linter & Formatter Check
python -m ruff check .
python -m ruff format --check .

# 2. Run Mypy Strict Type Checker
python -m mypy --config-file=pyproject.toml control_plane.py src/

# 3. Run Pylint Analysis
python -m pylint control_plane.py hooks/run_audit_hook.py hooks/run_firewall_hook.py scripts/md_to_json.py src/ tests/

# 4. Run Pytest Suite
python -m pytest

# 5. Run full pre-commit pipeline on all files
pre-commit run --all-files
```

---

## 📝 Conventional Commits Standard

All commit messages must adhere to the Conventional Commits specification:
Format: `<type>(<scope>): <description>`

- `feat`: New feature or SAST rule definition.
- `fix`: Bug fix in scanner or firewall logic.
- `refactor`: Code refactoring without behavior change.
- `docs`: Documentation updates.
- `style`: Code style formatting.
- `ci`: CI/CD workflow changes.

---

## 📬 Submitting a Pull Request

1. Create a feature branch: `git checkout -b feat/my-new-sast-rule`.
2. Commit your changes following Conventional Commits format.
3. Push to your branch and open a Pull Request using our [PULL_REQUEST_TEMPLATE](.github/PULL_REQUEST_TEMPLATE.md).
