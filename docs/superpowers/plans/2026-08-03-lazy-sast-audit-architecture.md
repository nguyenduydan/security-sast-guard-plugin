# Lazy SAST Audit Architecture Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Implement the "Lazy Audit" interactive loop and minified context extraction inside the SAST scanner.

**Architecture:** We will implement an extraction utility that reads a file and gathers its imports and the scope (function) of a given line. Then, we will update the `SASTScanner` to leverage this context and present an interactive CLI prompt when a rule violation is detected, allowing the AI to safely permit or deny it.

**Tech Stack:** Python, `pytest` for testing.

## Global Constraints

- Follow PEP8 and use strictly typed Python (Ruff, Mypy compliance).
- Ensure test coverage with pytest.

---

### Task 1: Minified Context Extractor

**Files:**
- Create: `src/domain/context_extractor.py`
- Create: `tests/test_context_extractor.py`

**Interfaces:**
- Produces: `def extract_context(file_path: str, line_number: int) -> dict[str, str]` (returns a dict with keys: `'line_content'`, `'imports'`, `'scope'`)

- [ ] **Step 1: Write the failing test**

```python
import os
import pytest
from src.domain.context_extractor import extract_context


def test_extract_context(tmp_path):
    test_file = tmp_path / "sample.py"
    test_file.write_text(
        "import os\nfrom sys import exit\n\ndef my_func():\n    query = 'SELECT'\n"
    )

    result = extract_context(str(test_file), 4)
    assert result["line_content"].strip() == "query = 'SELECT'"
    assert "import os" in result["imports"]
    assert "from sys import exit" in result["imports"]
    assert result["scope"] == "def my_func():"
```

- [ ] **Step 2: Run test to verify it fails**

Run: `pytest tests/test_context_extractor.py -v`
Expected: FAIL with ModuleNotFoundError or ImportError

- [ ] **Step 3: Write minimal implementation**

```python
import re
from typing import Dict


def extract_context(file_path: str, line_number: int) -> Dict[str, str]:
    imports = []
    scope = "global"
    line_content = ""

    with open(file_path, "r", encoding="utf-8") as f:
        lines = f.readlines()

    for i, line in enumerate(lines):
        line_idx = i + 1
        stripped = line.strip()

        if stripped.startswith("import ") or stripped.startswith("from "):
            imports.append(stripped)

        if stripped.startswith("def ") or stripped.startswith("class "):
            scope = stripped

        if line_idx == line_number:
            line_content = line
            break

    return {
        "line_content": line_content.strip("\n"),
        "imports": "\n".join(imports),
        "scope": scope,
    }
```

- [ ] **Step 4: Run test to verify it passes**

Run: `pytest tests/test_context_extractor.py -v`
Expected: PASS

- [ ] **Step 5: Commit**

```bash
git add tests/test_context_extractor.py src/domain/context_extractor.py
git commit -m "feat: implement context extractor for lazy SAST"
```

---

### Task 2: Interactive Lazy Prompt

**Files:**
- Modify: `src/domain/sast_scanner.py`
- Modify: `tests/test_sast.py`

**Interfaces:**
- Consumes: `extract_context` from `src.domain.context_extractor`
- Produces: Updated `scan()` method that intercepts matches and prompts the user via `input()`.

- [ ] **Step 1: Write the failing test**

Modify `tests/test_sast.py` to add:
```python
import pytest
from unittest.mock import patch
from src.domain.sast_scanner import SASTScanner


def test_sast_scanner_lazy_prompt(tmp_path):
    test_file = tmp_path / "vuln.py"
    test_file.write_text(
        "import sqlite3\ndef fetch():\n    query = 'SELECT * FROM users'\n"
    )

    scanner = SASTScanner()

    # Mocking a regex match detection internally and input() function
    with patch("builtins.input", return_value="Y"):
        with patch.object(
            scanner, "_detect_matches", return_value=[{"line": 3, "rule": "SQLi"}]
        ):
            results = scanner.scan(str(test_file))
            # Since user replied 'Y', it's allowed (filtered out of violations)
            assert len(results) == 0

    with patch("builtins.input", return_value="N"):
        with patch.object(
            scanner, "_detect_matches", return_value=[{"line": 3, "rule": "SQLi"}]
        ):
            results = scanner.scan(str(test_file))
            # User replied 'N', so it remains a violation
            assert len(results) == 1
```

- [ ] **Step 2: Run test to verify it fails**

Run: `pytest tests/test_sast.py -v`
Expected: FAIL because `_detect_matches` doesn't exist and `scan` doesn't prompt `input`.

- [ ] **Step 3: Write minimal implementation**

Modify `src/domain/sast_scanner.py`:
```python
"""SAST Scanner domain component."""

from typing import Any, List, Dict
from .context_extractor import extract_context


class SASTScanner:
    """SAST rule scanner implementation."""

    def _detect_matches(self, path: str) -> List[Dict[str, Any]]:
        # Placeholder for actual regex engine execution
        return []

    def scan(self, path: str) -> List[Dict[str, Any]]:
        """Scan specified file path for SAST rule matches with lazy interactive loop."""
        matches = self._detect_matches(path)
        violations = []

        for match in matches:
            ctx = extract_context(path, match["line"])
            print(
                f"[SAST WARNING] Potential {match['rule']} at `{path}:{match['line']}`."
            )
            print(f"- Line: `{ctx['line_content'].strip()}`")
            print(f"- Scope: `{ctx['scope']}`")
            print(f"- Imports: `{ctx['imports']}`")

            answer = (
                input("? Is this context safe? (Reply Y to allow, N to block): ")
                .strip()
                .upper()
            )
            if answer != "Y":
                violations.append(match)

        return violations
```

- [ ] **Step 4: Run test to verify it passes**

Run: `pytest tests/test_sast.py -v`
Expected: PASS

- [ ] **Step 5: Commit**

```bash
git add src/domain/sast_scanner.py tests/test_sast.py
git commit -m "feat: integrate interactive lazy loop in SAST scanner"
```
