# Implementation Plan: Git Incremental Scan, Early Directory Pruning & AI False-Positive Verifier

## Goal
Optimize `security-sast-guard` for enterprise codebases (100,000+ files) by introducing:
1. **Early Directory Pruning (`os.walk` top-down pruning):** Stop traversing into ignored directories (e.g. `node_modules`, `.venv`) at directory boundary level.
2. **Git Incremental Scan:** Automatically detect git repository changes (`git diff --name-only`) to scan only changed/added files instantly.
3. **AI Context Verification Gate (False Positive Filter):** Add a 2-stage verification pipeline where candidate findings are analyzed for safety context (sanitizers, test mocks, parameterization) to auto-discard false positives before generating reports.

---

## Proposed Changes

### 1. `src/domain/ignore_filter.py`
- Add `should_ignore_dir(dir_name: str) -> bool` to allow top-down pruning during directory traversal.

### 2. `src/domain/git_helper.py` (New Module)
- Helper class `GitHelper` to query modified/untracked files using `git diff` and `git status`.
- `get_changed_files(repo_root: Path) -> list[Path] | None`.

### 3. `src/domain/ai_verifier.py` (New Module)
- `AIVerifier` class:
  - Evaluates candidate findings against safety rules (e.g., presence of sanitization wrappers `sanitize()`, `DOMPurify`, parameterized queries `?` or `%s`, test fixtures/mocks, dummy strings).
  - Filters out false positives and attaches confidence score (`VERIFIED_VULNERABILITY` vs `FALSE_POSITIVE`).

### 4. `src/domain/sast_scanner.py`
- Refactor traversal to use `os.walk` top-down with early directory pruning (`dirnames[:] = [d for d in dirnames if not ignore_filter.should_ignore_dir(d)]`).
- Support `git_incremental=True` parameter to scan only changed files when in a git repo.
- Integrate `AIVerifier` in `scan_with_metadata`.

### 5. `src/infrastructure/report_generator.py`
- Display `Git Incremental Mode: ON/OFF` and `AI False-Positives Filtered: X` in metadata summary table.

---

## Verification Plan

### Automated Tests
- `tests/test_git_helper.py`: Unit tests for git status & diff detection.
- `tests/test_ai_verifier.py`: Unit tests for false-positive detection (sanitizers, mocks).
- `tests/test_scanner_performance.py`: Benchmark test verifying top-down pruning skips walking ignored subdirectories.
- Run `pytest`, `mypy src`, and `ruff check src tests`.
