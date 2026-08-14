### Task 3: Semantic Context Window & Sanitizer Gate in AIVerifier

**Files:**
- Modify: `src/domain/ai_verifier.py`
- Test: `tests/test_performance_and_ai.py`

**Interfaces:**
- Consumes: Finding dictionary with `line_content`, `context_window` (list of strings), `path`, `rule_id`, `severity`.
- Produces: `AIVerifier.is_false_positive(finding: dict[str, Any]) -> bool` inspecting both `line_content` and `context_window` for:
  1. Shell sanitizers: `shlex.quote`, `escapeshellarg`, `escapeshellcmd`, `quote_plus`.
  2. HTML/XSS sanitizers: `dompurify`, `sanitize`, `htmlspecialchars`, `escapehtml`, `validator.escape`, `encodeuricomponent`, `encodeuri`, `bleach.clean`.
  3. Path sanitizers: `path.resolve`, `os.path.basename`, `path.basename`, `os.path.abspath`, `pathlib.path`.
  4. Multi-line SQL parameterized arguments and markers: `params=`, `parameters=`, `%s`, `?`, `$1`, `:param`, `bindparam`, `preparestatement`.
  5. Safe typecasts in context window: `int(`, `float(`, `bool(`, `uuid(`.

- [ ] **Step 1: Write failing tests in `tests/test_performance_and_ai.py`**
  - `test_ai_verifier_sanitizer_in_preceding_line()`
  - `test_ai_verifier_dompurify_in_preceding_line()`
  - `test_ai_verifier_path_sanitizer_in_preceding_line()`
- [ ] **Step 2: Run tests to verify they fail**
- [ ] **Step 3: Update `src/domain/ai_verifier.py`**
  - Extract context window string and check for known sanitizers, parameterized query markers, and safe typecasts in surrounding window.
- [ ] **Step 4: Run tests to verify they pass**
- [ ] **Step 5: Run CI quality gates (`ruff`, `pylint`, `mypy`, `pytest`)**
- [ ] **Step 6: Commit `feat(verifier): add context window sanitizer inspection to AIVerifier`**
