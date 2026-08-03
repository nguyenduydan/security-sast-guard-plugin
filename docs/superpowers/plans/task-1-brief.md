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
