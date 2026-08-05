# Implementation Plan: SAST Zero-Config Ignore & Scan Transparency

## Goal
Enhance `security-sast-guard` with zero-configuration default ignore lists (bút sẵn 20+ folder/ext), optional project `.sastignore` file support, recursive codebase scanning, and transparent metadata reporting (scanned files, lines, duration, ignored count, active level).

---

## Proposed Changes

### 1. `src/domain/ignore_filter.py` (New File)
- **Built-in Defaults:**
  - Folders: `.git`, `.hg`, `.svn`, `node_modules`, `vendor`, `.venv`, `venv`, `env`, `__pycache__`, `.pytest_cache`, `.mypy_cache`, `.ruff_cache`, `.idea`, `.vscode`, `dist`, `build`, `out`, `target`, `.next`, `.nuxt`.
  - Extensions: `.png`, `.jpg`, `.jpeg`, `.gif`, `.ico`, `.svg`, `.pdf`, `.zip`, `.tar`, `.gz`, `.7z`, `.rar`, `.exe`, `.dll`, `.so`, `.dylib`, `.woff`, `.woff2`, `.ttf`, `.eot`, `.mp3`, `.mp4`, `.pyc`, `.pyo`, `.db`, `.sqlite`.
  - Lockfiles: `package-lock.json`, `yarn.lock`, `pnpm-lock.yaml`, `Cargo.lock`, `poetry.lock`.
- **Project `.sastignore` Support:**
  - Automatically loads `.sastignore` from target project root if present and merges custom patterns using `fnmatch`.
- **API:**
  - `should_ignore(path: Path | str) -> bool`

### 2. `src/domain/sast_scanner.py` (Update)
- Integrate `IgnoreFilter`.
- Support directory traversal (recursive scan) when target path is a directory.
- Track metadata during scan:
  - `files_scanned`: int
  - `files_ignored`: int
  - `lines_analyzed`: int
  - `rules_applied`: int
  - `duration_seconds`: float
- Return scan result dictionary containing `findings` and `metadata`.

### 3. `src/infrastructure/report_generator.py` (Update)
- Format metadata into Markdown report with clean summary table showing:
  - Total Files Scanned / Ignored
  - Total Lines Analyzed
  - Active Audit Level (from `profile.json`)
  - Scan Execution Time

### 4. `src/application/audit_service.py` (Update)
- Auto-resolve `audit_level` from `profile.json`.
- Pass metadata cleanly through report generator.

### 5. `tests/test_ignore_filter.py` (New Test Suite)
- Test built-in ignore patterns (venv, node_modules, binaries).
- Test loading custom `.sastignore`.
- Test recursive directory scan and metadata generation.

---

## Verification Plan

### Automated Tests
- Run `pytest` to ensure 100% test pass rate.
- Run `mypy src/` for strict type checking.
- Run `ruff check src/` and `ruff format --check src/`.
- Run `/sast-audit` skill / script to verify transparent report format.
