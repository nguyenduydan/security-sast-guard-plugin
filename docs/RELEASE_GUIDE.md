# Release Publishing Workflow & Migration Guide

This document defines the release standards, commit workflows, upgrade guidance (Zero Breaking Changes), and GitHub Release automation for the **security-sast-guard-plugin** project.

---

## 1. Migration Guide: Upgrading from v1.x to v2.0.0 (Zero Breaking Changes)

Security SAST Guard v2.0.0 is architected with **100% Backward Compatibility** as a foundational principle. Developers and AI Agents upgrading from v1.x to v2.0.0 do not need to modify any existing configurations.

### 1.1. Zero Breaking Changes Commitment
- **Existing `.sast/profile.json` Configuration:** Fully preserves all key/value pairs from v1.x. Engine v2.0.0 automatically loads and populates safe default values for the 13 new modular subsystems.
- **CLI Commands & Slash Commands:** All CLI commands (`sast scan`, `sast status`, `sast init`, `sast mode`, `sast level`, `sast rules`) and Slash Commands (`/sast-audit`, `/sast-status`, `/sast-init`, `/sast-mode`, `/sast-audit-level`, `/sast-rules`) maintain identical syntax.
- **MCP Server Stdio Interface:** All 9 Stdio tools from v1.x (`sast_scan_file`, `sast_scan_diff`, `sast_check_command`, `sast_get_status`, `sast_set_level`, `sast_init`, `sast_sync_rules`, `sast_get_help`, `sast_set_mode`) retain their existing signatures. v2.0.0 introduces 3 new tools (`sast_get_dataflow_path`, `sast_get_taint_context`, `sast_generate_report`).

### 1.2. Architecture & Subsystems in v2.0.0
Version v2.0.0 introduces **13 Modular Subsystems** across 3 Tiers:
1. **Tier 1 (Security Core):** 10-Stage Firewall Normalizer, Capability Classifier, Intent Classifier, Multi-Command Chain Analyzer, 4-State Decision Engine, Semantic Fingerprint Tracker, Rule Integrity Validator, Append-Only Audit Log.
2. **Tier 2 (SAST Intelligence):** Evidence Engine & Program Slicer, Bounded Verification Harness, Adaptive Knowledge Base (Sanitizer Registry), CWE/OWASP Mapper & Metrics Engine, Framework Semantics Registry (ASP.NET WebForms, React, Generic).
3. **Tier 3 (Developer Experience):** Pure ANSI TUI Renderer (`TUIRenderer`), Enhanced ISO SARIF 2.1.0 Exporter, 12 MCP Tools Suite.

---

## 2. Semantic Versioning & Release-Please Automation

The project utilizes automated release management via **`release-please` v4** combined with Semantic Versioning (SemVer):

### 2.1. Versioning Rules (SemVer)
- **MAJOR (`v2.0.0`):** Incremented for major architectural overhauls or breaking changes (v2.0.0 completely upgraded the SAST & Firewall subsystems).
- **MINOR (`v2.1.0`):** Incremented when introducing backward-compatible new features, SAST rules, or MCP tools.
- **PATCH (`v2.0.1`):** Incremented for bug fixes, maintenance, refactoring, or dependency updates.

### 2.2. Automated Workflow via Release-Please Bot
- **No Manual Tagging:** Strictly **FORBIDDEN** to execute `git tag` manually or create manual releases via the GitHub UI.
- **No Manual Version Editing:** Do not manually edit version strings in `plugin.json` or `pyproject.toml`.
- The `release-please` bot automatically inspects commits merged into the `main` branch, creates Release PRs (updating versions and `CHANGELOG.md`), and publishes official GitHub Releases with Git Tags upon merging.

---

## 3. Commit Message Standards (Conventional Commits)

All commit messages **MUST** adhere to the Conventional Commits specification with a scope:
`<type>(<scope>): <description>`

### Commit Types (`type`):
- `feat`: New feature or SAST rule addition *(Triggers MINOR version bump)*.
- `fix`: Bug fix in source code, linters, or CI *(Triggers PATCH version bump)*.
- `chore`: Maintenance, cleanup, dependency updates *(Triggers PATCH version bump)*.
- `refactor`: Code refactoring without behavioral modifications *(Triggers PATCH version bump)*.
- `docs`: Documentation updates (`.md`, docstrings) *(No version bump)*.
- `style`: Code style and formatting (Ruff).
- `test`: Adding or updating test suites (pytest).

*Example:* `feat(firewall): add 10-stage deobfuscation normalizer`

---

## 4. Git Branching & Pull Request Workflow (GitHub Flow)

1. **Never commit directly to `main`:** All feature development, bug fixes, and documentation work must occur on dedicated branches (`feat/<name>`, `fix/<name>`, `docs/<name>`).
2. **Create a New Branch:**
   ```bash
   git checkout -b feat/v2-firewall-rules
   ```
3. **Execute Pre-Push Quality Gate:**
   Run the full quality test suite before pushing:
   ```bash
   python -m ruff check .
   python -m ruff format --check .
   python -m pylint control_plane.py src/
   python -m mypy --config-file=pyproject.toml control_plane.py src/
   python -m pytest
   ```
4. **Push Branch & Open Pull Request:**
   ```bash
   git push origin feat/v2-firewall-rules
   ```
   Open a Pull Request on GitHub targeting the `main` branch.

---

## 5. CI Quality Gate & Automated Testing

Every PR targeting `main` must achieve a 100% green pass on the CI Quality Gate Workflow (`.github/workflows/ci.yml`):
- **Linter & Formatting:** Ruff check & format validation with zero warnings.
- **Static Code Analysis:** Pylint 0 errors score.
- **Type Inspection:** MyPy strict mode zero typing errors.
- **Automated Test Suite:** 100% Pytest suite passing.

---

## 6. Emergency Rollback & Patch Release Workflow

In the event a critical defect is identified on a newly published release:
1. Immediately create a hotfix branch from the latest stable commit:
   ```bash
   git checkout -b fix/rollback-patch
   ```
2. Revert the offending commit or apply the minimal necessary fix.
3. Re-run the Quality Gate suite and open a PR to `main` with commit message `fix(core): emergency fix for issue ...`.
4. The `release-please` bot will automatically create a new PATCH Release PR (e.g., `v2.0.1`) to safely supersede the defective release.
