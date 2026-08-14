### Task 4: Integration into SASTScanner Pipeline & CI Quality Gate Verification

**Files:**
- Modify: `src/domain/sast_scanner.py`
- Test: `tests/test_sast.py`

**Interfaces:**
- Consumes: Complete files/codebases scanning via `SASTScanner.scan_with_metadata` and `SASTScanner.scan_code`.
- Produces: High-precision findings with zero false positives on safe constants, typecasts, and sanitized calls.

- [ ] **Step 1: Integrate `ASTPrecisionAnalyzer` and context window into `src/domain/sast_scanner.py`**
  - Initialize `self.ast_analyzer = ASTPrecisionAnalyzer()` in `SASTScanner.__init__`.
  - In `_detect_matches_file`:
    - Extract `ctx` via `self.context_extractor.extract_context_from_lines(lines, line_idx, str_path)`.
    - Populate `"context_window": ctx.get("context_window", [])` in the finding dictionary.
    - If target file is Python (`.py`) and `self.ast_analyzer.is_safe_sink_call(str_path, line_idx, rule_id, line_content, None)` returns `True`, skip the finding (drop false positive).
  - In `scan_code`:
    - If `filename.endswith(".py")` and `self.ast_analyzer.is_safe_sink_call(filename, line_idx, rule_id, line_content, code)` returns `True`, skip the finding.
- [ ] **Step 2: Add integration tests in `tests/test_sast.py`**
  - Verify scanning Python file with safe `os.system("git status")` or `int(user_id)` produces 0 findings.
  - Verify scanning Python file with real vulnerability `os.system(user_input)` still produces 1 finding.
- [ ] **Step 3: Run full CI Quality Gate verification**
  - `python -m ruff check .`
  - `python -m ruff format --check .`
  - `python -m pylint control_plane.py src/`
  - `python -m mypy --config-file=pyproject.toml control_plane.py src/`
  - `python -m pytest`
- [ ] **Step 4: Commit `feat(scanner): integrate AST analyzer and context window into scanning pipeline`**
