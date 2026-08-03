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
