### Task 2: Multi-Line Comment & Context Window Extraction in ContextExtractor

**Files:**
- Modify: `src/domain/context_extractor.py`
- Test: `tests/test_context_extractor.py`

**Interfaces:**
- Consumes: Lines list, line number, file path.
- Produces: `context["context_window"]` (code snippet ±5 lines list of strings) and `context["is_safe_context"]` tracking multi-line block comments (`/* ... */`) in `GenericSafeContextStrategy`.

- [x] **Step 1: Write the failing tests in `tests/test_context_extractor.py`**
  - `test_multiline_block_comment_js_is_safe()`
  - `test_context_window_extraction()`
- [x] **Step 2: Run tests to verify they fail**
- [x] **Step 3: Update `src/domain/context_extractor.py`**
  - Implement block comment state tracking in `GenericSafeContextStrategy`.
  - Implement context window extraction `[line - 5, line + 5]` in `extract_context_from_lines`.
- [x] **Step 4: Run tests to verify they pass**
- [x] **Step 5: Run CI quality gates (`ruff`, `pylint`, `mypy`, `pytest`)**
- [x] **Step 6: Commit `feat(context): add multi-line block comment tracking and context window extraction`**
