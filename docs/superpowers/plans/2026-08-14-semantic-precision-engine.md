# Multi-Layer Semantic Precision Engine Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Implement Python AST constant evaluation, multi-line comment parsing, and surrounding context window sanitizer verification to dramatically reduce false positives while keeping SAST scanning ultra-fast.

**Architecture:** A three-stage precision filtering pipeline: (1) `ASTPrecisionAnalyzer` for Python syntax & constant propagation, (2) `ContextExtractor` multi-line & context window extraction, and (3) `AIVerifier` semantic sanitizer/typecast gate.

**Tech Stack:** Python 3.10+, `ast`, `tokenize`, `re`, `pytest`, `mypy`, `ruff`, `pylint`.

## Global Constraints

- Must have zero external third-party runtime dependencies (use Python standard library only).
- All changes must pass 100% CI Quality Gates (`ruff`, `pylint`, `mypy`, `pytest`).
- Maintain backward compatibility with existing `SASTScanner.scan_with_metadata()` and `scan_code()`.

---

### Task 1: AST Precision Analyzer for Python Constant Propagation & Typecast Gate

**Files:**
- Create: `src/domain/ast_analyzer.py`
- Test: `tests/test_ast_analyzer.py`

**Interfaces:**
- Consumes: Python source code or file path, line number, rule ID, line content.
- Produces: `ASTPrecisionAnalyzer.is_safe_sink_call(file_path: str, line_number: int, rule_id: str, line_content: str, code_content: str | None = None) -> bool`

- [ ] **Step 1: Write the failing test**

```python
# tests/test_ast_analyzer.py
import pytest
from src.domain.ast_analyzer import ASTPrecisionAnalyzer

def test_ast_analyzer_constant_string_command_is_safe():
    analyzer = ASTPrecisionAnalyzer()
    code = 'import os\nos.system("git status")\n'
    is_safe = analyzer.is_safe_sink_call(
        file_path="sample.py",
        line_number=2,
        rule_id="CMD_INJECTION",
        line_content='os.system("git status")',
        code_content=code,
    )
    assert is_safe is True

def test_ast_analyzer_dynamic_variable_is_not_safe():
    analyzer = ASTPrecisionAnalyzer()
    code = 'import os\ncmd = input()\nos.system(cmd)\n'
    is_safe = analyzer.is_safe_sink_call(
        file_path="sample.py",
        line_number=3,
        rule_id="CMD_INJECTION",
        line_content='os.system(cmd)',
        code_content=code,
    )
    assert is_safe is False

def test_ast_analyzer_typecast_int_is_safe():
    analyzer = ASTPrecisionAnalyzer()
    code = 'user_id = int(request.args.get("id"))\nquery = f"SELECT * FROM users WHERE id = {user_id}"\n'
    is_safe = analyzer.is_safe_sink_call(
        file_path="sample.py",
        line_number=2,
        rule_id="SQL_INJECTION",
        line_content='query = f"SELECT * FROM users WHERE id = {user_id}"',
        code_content=code,
    )
    assert is_safe is True
```

- [ ] **Step 2: Run test to verify it fails**

Run: `pytest tests/test_ast_analyzer.py -v`  
Expected: FAIL with `ModuleNotFoundError: No module named 'src.domain.ast_analyzer'`

- [ ] **Step 3: Write minimal implementation**

```python
# src/domain/ast_analyzer.py
"""AST-based Precision Analyzer for evaluating dangerous sinks and constant propagation."""

import ast
from typing import Any

SAFE_TYPECAST_FUNCTIONS: set[str] = {"int", "float", "bool", "UUID", "uuid.UUID"}


class ASTPrecisionAnalyzer:
    """Evaluates Python AST nodes to identify static literals and type-safe variables."""

    def __init__(self) -> None:
        self._ast_cache: dict[str, ast.AST | None] = {}

    def parse_ast(self, file_path: str, code_content: str | None = None) -> ast.AST | None:
        """Parse and cache AST for a file or code snippet."""
        if file_path in self._ast_cache and code_content is None:
            return self._ast_cache[file_path]

        try:
            if code_content is None:
                with open(file_path, encoding="utf-8", errors="replace") as f:
                    code_content = f.read()
            tree = ast.parse(code_content, filename=file_path)
            if file_path:
                self._ast_cache[file_path] = tree
            return tree
        except (SyntaxError, OSError, UnicodeDecodeError):
            return None

    def is_safe_sink_call(
        self,
        file_path: str,
        line_number: int,
        rule_id: str,
        line_content: str,
        code_content: str | None = None,
    ) -> bool:
        """Check if sink invocation on target line contains only constants or safe conversions."""
        _ = rule_id
        tree = self.parse_ast(file_path, code_content)
        if tree is None:
            return False

        typecast_vars: set[str] = set()
        for node in ast.walk(tree):
            if isinstance(node, ast.Assign):
                if isinstance(node.value, ast.Call):
                    func_name = ""
                    if isinstance(node.value.func, ast.Name):
                        func_name = node.value.func.id
                    elif isinstance(node.value.func, ast.Attribute):
                        func_name = node.value.func.attr
                    if func_name in SAFE_TYPECAST_FUNCTIONS:
                        for target in node.targets:
                            if isinstance(target, ast.Name):
                                typecast_vars.add(target.id)

        target_nodes: list[ast.AST] = []
        for node in ast.walk(tree):
            if getattr(node, "lineno", None) == line_number:
                target_nodes.append(node)

        if not target_nodes:
            return False

        for node in target_nodes:
            if isinstance(node, ast.Call):
                if not node.args and not node.keywords:
                    return True
                all_args_safe = True
                for arg in node.args:
                    if not self._is_safe_expr(arg, typecast_vars):
                        all_args_safe = False
                        break
                if all_args_safe:
                    return True

            if isinstance(node, (ast.Assign, ast.Expr)):
                if isinstance(getattr(node, "value", None), ast.JoinedStr):
                    joined: ast.JoinedStr = node.value  # type: ignore[assignment]
                    all_safe = True
                    for val in joined.values:
                        if isinstance(val, ast.FormattedValue):
                            if isinstance(val.value, ast.Name) and val.value.id in typecast_vars:
                                continue
                            if not self._is_safe_expr(val.value, typecast_vars):
                                all_safe = False
                                break
                        elif not isinstance(val, ast.Constant):
                            all_safe = False
                            break
                    if all_safe:
                        return True

        return False

    def _is_safe_expr(self, expr: ast.AST, typecast_vars: set[str]) -> bool:
        if isinstance(expr, ast.Constant):
            return True
        if isinstance(expr, ast.Name) and expr.id in typecast_vars:
            return True
        if isinstance(expr, ast.Call):
            func_name = ""
            if isinstance(expr.func, ast.Name):
                func_name = expr.func.id
            elif isinstance(expr.func, ast.Attribute):
                func_name = expr.func.attr
            if func_name in SAFE_TYPECAST_FUNCTIONS:
                return True
        if isinstance(expr, (ast.List, ast.Tuple, ast.Set)):
            return all(self._is_safe_expr(el, typecast_vars) for el in expr.elts)
        if isinstance(expr, ast.Dict):
            return all(
                (k is None or self._is_safe_expr(k, typecast_vars))
                and self._is_safe_expr(v, typecast_vars)
                for k, v in zip(expr.keys, expr.values)
            )
        return False
```

- [ ] **Step 4: Run test to verify it passes**

Run: `pytest tests/test_ast_analyzer.py -v`  
Expected: 3 passed in 0.05s

- [ ] **Step 5: Commit**

```bash
git add src/domain/ast_analyzer.py tests/test_ast_analyzer.py
git commit -m "feat(ast): add ASTPrecisionAnalyzer for Python constant propagation"
```

---

### Task 2: Multi-Line Comment & Context Window Extraction in ContextExtractor

**Files:**
- Modify: `src/domain/context_extractor.py`
- Test: `tests/test_context_extractor.py`

**Interfaces:**
- Consumes: Lines list, line number, file path.
- Produces: `context["context_window"]` (code snippet ±5 lines) and `context["is_safe_context"]` tracking multi-line block comments (`/* ... */`).

- [ ] **Step 1: Write the failing test**

```python
# Add to tests/test_context_extractor.py
def test_multiline_block_comment_js_is_safe():
    extractor = ContextExtractor()
    lines = [
        "/*\n",
        " * eval(userInput);\n",
        " */\n",
        "const valid = true;\n"
    ]
    ctx = extractor.extract_context_from_lines(lines, line_number=2, file_path="app.js")
    assert ctx["is_safe_context"] is True

def test_context_window_extraction():
    extractor = ContextExtractor()
    lines = [f"line_{i}\n" for i in range(1, 20)]
    ctx = extractor.extract_context_from_lines(lines, line_number=10, file_path="service.py")
    assert "context_window" in ctx
    window_lines = ctx["context_window"]
    assert len(window_lines) == 11
    assert "line_10" in window_lines[5]
```

- [ ] **Step 2: Run test to verify it fails**

Run: `pytest tests/test_context_extractor.py -k "test_multiline_block_comment_js_is_safe or test_context_window_extraction" -v`  
Expected: FAIL

- [ ] **Step 3: Update `src/domain/context_extractor.py` implementation**

Update `GenericSafeContextStrategy` to track multi-line block comment state from line 1 up to target line:
```python
class GenericSafeContextStrategy(ISafeContextStrategy):
    """Fast in-memory safe context checker for non-Python files with multi-line comment state."""

    def is_safe_context(
        self, line_content: str, line_number: int, lines: list[str]
    ) -> bool:
        stripped = line_content.strip()
        if not stripped:
            return True

        if (
            stripped.startswith("#")
            or stripped.startswith("//")
            or stripped.startswith("<!--")
            or stripped.startswith("*")
        ):
            return True

        in_block_comment = False
        max_line = min(line_number, len(lines))
        for i in range(max_line):
            curr = lines[i]
            if "/*" in curr and "*/" not in curr:
                in_block_comment = True
            elif "*/" in curr:
                in_block_comment = False
            elif in_block_comment and (i + 1) == line_number:
                return True

        return in_block_comment
```
And in `extract_context_from_lines`, extract `context_window`:
```python
start_idx = max(0, line_number - 6)
end_idx = min(len(lines), line_number + 5)
context_window = [lines[i].rstrip("\r\n") for i in range(start_idx, end_idx)]
```

- [ ] **Step 4: Run test to verify it passes**

Run: `pytest tests/test_context_extractor.py -v`  
Expected: PASS

- [ ] **Step 5: Commit**

```bash
git add src/domain/context_extractor.py tests/test_context_extractor.py
git commit -m "feat(context): add multi-line block comment tracking and context window extraction"
```

---

### Task 3: Semantic Context Window & Sanitizer Gate in AIVerifier

**Files:**
- Modify: `src/domain/ai_verifier.py`
- Test: `tests/test_performance_and_ai.py`

**Interfaces:**
- Consumes: Finding dictionary with `line_content`, `context_window`, `path`, `rule_id`.
- Produces: `AIVerifier.is_false_positive(finding: dict[str, Any]) -> bool` checking surrounding context window for sanitizers and parameterized markers.

- [ ] **Step 1: Write the failing test**

```python
# Add to tests/test_performance_and_ai.py
def test_ai_verifier_sanitizer_in_preceding_line():
    verifier = AIVerifier()
    finding = {
        "rule_id": "CMD_INJECTION",
        "path": "worker.py",
        "line": 4,
        "line_content": "os.system(safe_cmd)",
        "context_window": [
            "import os",
            "import shlex",
            "safe_cmd = shlex.quote(user_input)",
            "os.system(safe_cmd)",
        ],
        "severity": "HIGH",
    }
    assert verifier.is_false_positive(finding) is True

def test_ai_verifier_dompurify_in_preceding_line():
    verifier = AIVerifier()
    finding = {
        "rule_id": "XSS_DOM",
        "path": "component.js",
        "line": 3,
        "line_content": "element.innerHTML = cleanHtml;",
        "context_window": [
            "const cleanHtml = DOMPurify.sanitize(dirtyInput);",
            "element.innerHTML = cleanHtml;",
        ],
        "severity": "HIGH",
    }
    assert verifier.is_false_positive(finding) is True
```

- [ ] **Step 2: Run test to verify it fails**

Run: `pytest tests/test_performance_and_ai.py -k "test_ai_verifier_sanitizer_in_preceding_line" -v`  
Expected: FAIL

- [ ] **Step 3: Update `src/domain/ai_verifier.py` implementation**

Enhance `AIVerifier.is_false_positive` to inspect both `line_content` and `context_window`:
- Check for shell sanitizers (`shlex.quote`, `escapeshellarg`, `escapeshellcmd`).
- Check for XSS/DOM sanitizers (`dompurify`, `sanitize`, `htmlspecialchars`, `escapehtml`, `validator.escape`).
- Check for path sanitizers (`path.resolve`, `os.path.basename`, `os.path.abspath`).
- Check for multi-line SQL parameterized arguments (`params=`, `%s`, `?`, `:param`).

- [ ] **Step 4: Run test to verify it passes**

Run: `pytest tests/test_performance_and_ai.py -v`  
Expected: PASS

- [ ] **Step 5: Commit**

```bash
git add src/domain/ai_verifier.py tests/test_performance_and_ai.py
git commit -m "feat(verifier): add context window sanitizer inspection to AIVerifier"
```

---

### Task 4: Integration into SASTScanner Pipeline & CI Quality Gate Verification

**Files:**
- Modify: `src/domain/sast_scanner.py`
- Test: `tests/test_sast.py`

**Interfaces:**
- Consumes: Complete files/codebases.
- Produces: High-precision findings with zero false positives on safe constants, typecasts, and sanitized calls.

- [ ] **Step 1: Integrate `ASTPrecisionAnalyzer` and context window in `_detect_matches_file` & `scan_code`**

In `src/domain/sast_scanner.py`:
1. Initialize `self.ast_analyzer = ASTPrecisionAnalyzer()` in `__init__`.
2. In `_detect_matches_file`: Pass `context_window` in finding metadata and run `self.ast_analyzer.is_safe_sink_call(...)` for Python files before adding finding.
3. In `scan_code`: Run AST analyzer check for direct string scans.

- [ ] **Step 2: Run test suite to verify zero regressions**

Run: `pytest`  
Expected: 100% tests PASS

- [ ] **Step 3: Run full CI Quality Gate commands**

```bash
python -m ruff check .
python -m ruff format --check .
python -m pylint control_plane.py src/
python -m mypy --config-file=pyproject.toml control_plane.py src/
python -m pytest
```
Expected: 100% GREEN (Zero errors).

- [ ] **Step 4: Commit**

```bash
git add src/domain/sast_scanner.py tests/test_sast.py
git commit -m "feat(scanner): integrate AST analyzer and context window into scanning pipeline"
```
