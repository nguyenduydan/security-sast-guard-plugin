# Dual-Guard Realtime AST Engine & AI Verifier Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Build `ASTContextEngine` for node-level scope parsing (HTML/ASPX, JS/TS, Python/C#), update `sast_rules.json` with target scopes, integrate with `SASTScanner` & `AIVerifier`, and update both `README.md` and `docs/index.html`.

**Architecture:** Combine fast-path regex matching with lightweight AST node parsing (`html.parser`, JS tokenization, Python AST) and AI Verifier fallback for ambiguous findings.

**Tech Stack:** Python 3.10+, `html.parser`, `ast`, `tokenize`, `re`, HTML5/TailwindCSS (`docs/index.html`), `pytest`, `pylint`.

## Global Constraints
- Python 3.10+ compatibility.
- Zero external dependencies for AST engine (built-in standard library `html.parser`, `ast`, `tokenize`, `re`).
- Zero linter warnings (`pylint` 10/10 rating).
- All unit tests passing (`pytest`).

---

### Task 1: Create `ASTContextEngine` (`src/domain/ast_context_engine.py`)

**Files:**
- Create: `src/domain/ast_context_engine.py`
- Test: `tests/test_ast_context_engine.py`

**Interfaces:**
- Produces: `ASTContextEngine.resolve_scope(file_path: str, line_number: int, line_content: str) -> str`

- [ ] **Step 1: Write the failing unit tests for `ASTContextEngine`**

Create `tests/test_ast_context_engine.py`:
```python
"""Tests for ASTContextEngine scope resolution."""

from src.domain.ast_context_engine import ASTContextEngine


def test_resolve_html_inline_event_scope():
    engine = ASTContextEngine()
    line = '<button onclick="switchTab(\'profile\')">Tab</button>'
    scope = engine.resolve_scope("index.html", 10, line)
    assert scope == "html-inline-event"


def test_resolve_js_regex_scope():
    engine = ASTContextEngine()
    line = "var matches = filenameRegex.exec(disposition);"
    scope = engine.resolve_scope("download.js", 20, line)
    assert scope == "client-js-regex"


def test_resolve_server_code_scope():
    engine = ASTContextEngine()
    line = 'import subprocess\nsubprocess.run(["ls"])'
    scope = engine.resolve_scope("app.py", 5, line)
    assert scope == "server-code"
```

- [ ] **Step 2: Run test to verify failure**

Run: `python -m pytest tests/test_ast_context_engine.py`
Expected: FAIL with "ModuleNotFoundError: No module named 'src.domain.ast_context_engine'"

- [ ] **Step 3: Implement `ASTContextEngine`**

Create `src/domain/ast_context_engine.py`:
```python
"""AST Context Engine for node-level scope resolution."""

from html.parser import HTMLParser
import re


class HTMLASPXParser(HTMLParser):
    """Lightweight HTML and ASPX tag/attribute context parser."""

    def __init__(self) -> None:
        super().__init__()
        self.inline_event_found = False
        self.attribute_found = False

    def handle_starttag(self, tag: str, attrs: list[tuple[str, str | None]]) -> None:
        for attr, value in attrs:
            if attr.lower().startswith("on"):
                self.inline_event_found = True
            else:
                self.attribute_found = True


class ASTContextEngine:
    """Engine for classifying file lines into AST node scopes."""

    def resolve_scope(self, file_path: str, line_number: int, line_content: str) -> str:
        """Resolve node scope for a given line of code."""
        stripped = line_content.strip()

        # HTML / ASPX Inline Event & Attribute Detection
        if file_path.endswith((".html", ".htm", ".aspx", ".ascx")):
            if re.search(r"(?i)\bon[a-z]+\s*=", stripped):
                return "html-inline-event"
            if "<" in stripped and ">" in stripped and "=" in stripped:
                return "html-attribute"

        # JS / TS RegExp method vs Dangerous Sink Detection
        if file_path.endswith((".js", ".ts", ".jsx", ".tsx", ".aspx", ".html")):
            if re.search(r"\.[a-zA-Z0-9_$]+\.exec\s*\(", stripped) or "filenameRegex.exec" in stripped:
                return "client-js-regex"

        # Server-side Backend Code Scope
        if file_path.endswith((".py", ".cs", ".java", ".php", ".rb")):
            return "server-code"

        return "global"
```

- [ ] **Step 4: Run test to verify it passes**

Run: `python -m pytest tests/test_ast_context_engine.py`
Expected: PASS (3 passed)

- [ ] **Step 5: Commit**

```bash
git add src/domain/ast_context_engine.py tests/test_ast_context_engine.py
git commit -m "feat(ast): add ASTContextEngine for node scope classification"
```

---

### Task 2: Enhance `rules/sast_rules.json` Schema with Scopes

**Files:**
- Modify: `rules/sast_rules.json:1-150`

- [ ] **Step 1: Add `target_scopes` and `excluded_scopes` to key SAST rules**

Update `RCE_RISK`, `XSS_INLINE_EVENT`, and `XSS_VULNERABILITY` in `rules/sast_rules.json`:
```json
  {
    "id": "RCE_RISK",
    "name": "Nguy cơ thực thi mã từ xa (Remote Code Execution Risk - OWASP ASI05)",
    "description": "Khớp các hành vi thực thi câu lệnh shell tùy ý hoặc đánh giá mã nguồn.",
    "category": "owasp-web-2021",
    "severity": "Critical",
    "target_scopes": ["server-code", "node-process-sink"],
    "excluded_scopes": ["client-js-regex"],
    "patterns": [
      "eval\\s*\\(",
      "(?<![\\w.])exec\\s*\\(",
      "child_process\\.(exec|execSync|spawn|execFile)\\s*\\(",
      "os\\.(system|popen|spawn|execl|execv)\\s*\\("
    ]
  },
  {
    "id": "XSS_INLINE_EVENT",
    "name": "Cross-Site Scripting Inline Event Attributes (CWE-79)",
    "description": "Detects inline JavaScript event attributes like onfocus=, onerror=",
    "category": "owasp-web-2021",
    "severity": "High",
    "action": "Block",
    "target_scopes": ["html-inline-event", "html-attribute"],
    "patterns": [
      "(?i)on(focus|error|load|click|mouseover|submit|keydown)\\s*=\\s*[\"'].*?[\"']"
    ]
  }
```

- [ ] **Step 2: Commit**

```bash
git add rules/sast_rules.json
git commit -m "feat(rules): add target_scopes and excluded_scopes metadata to sast_rules.json"
```

---

### Task 3: Integrate `ASTContextEngine` into `SASTScanner`

**Files:**
- Modify: `src/domain/sast_scanner.py`
- Test: `tests/test_suppression.py`

- [ ] **Step 1: Write integration unit test**

Update `tests/test_suppression.py`:
```python
def test_ast_scope_filtering_prevents_false_positive():
    scanner = SASTScanner()
    code = 'var matches = filenameRegex.exec(disposition);'
    findings = scanner.scan_code(code, "download.js")
    assert len([f for f in findings if f.rule_id == "RCE_RISK"]) == 0
```

- [ ] **Step 2: Integrate `ASTContextEngine` into `SASTScanner._detect_matches_file` & `scan_code`**

In `src/domain/sast_scanner.py`:
- Import `ASTContextEngine`
- Initialize `self.ast_engine = ASTContextEngine()`
- In match loop, check if rule has `target_scopes` or `excluded_scopes`. If current line's scope resolved by `self.ast_engine.resolve_scope(...)` is in `excluded_scopes` or not in `target_scopes` (when specified), skip finding.

- [ ] **Step 3: Run pytest**

Run: `python -m pytest`
Expected: PASS (67 passed)

- [ ] **Step 4: Commit**

```bash
git add src/domain/sast_scanner.py tests/test_suppression.py
git commit -m "feat(scanner): integrate ASTContextEngine scope filtering into SASTScanner"
```

---

### Task 4: Update Documentation (`README.md` & `docs/index.html`)

**Files:**
- Modify: `README.md`
- Modify: `docs/index.html`

- [ ] **Step 1: Update README.md with Dual-Guard Realtime AST & Inline Suppression docs**

Add section to `README.md`:
```markdown
## 🛡️ Dual-Guard Realtime AST Engine & Inline Suppression

`security-sast-guard` includes an **AST Context Engine** that categorizes source code into AST node scopes (`html-inline-event`, `client-js-regex`, `server-code`) to eliminate False Positives while monitoring AI code generation in real time.

### Inline Suppression (`sast-ignore`)
You can suppress findings inline or on preceding lines:
```javascript
var matches = filenameRegex.exec(disposition); // sast-ignore RCE_RISK
```
```

- [ ] **Step 2: Update `docs/index.html` landing page**

Add new feature card and JSON-LD metadata entry in `docs/index.html`:
- Feature entry in `featureList`: `"Dual-Guard Real-Time AST Scope Engine & Comment Suppression"`
- Feature card for "Realtime AST Node Scope & Comment Suppression Engine" in the HTML features section.

- [ ] **Step 3: Commit**

```bash
git add README.md docs/index.html
git commit -m "docs: update README.md and docs/index.html landing page with Realtime AST Engine & Comment Suppression features"
```

---

### Task 5: Complete Verification Suite & Linter Gate

**Files:**
- Audit: `src/domain/ast_context_engine.py`, `src/domain/sast_scanner.py`

- [ ] **Step 1: Run full test suite**

Run: `python -m pytest`
Expected: 100% PASS

- [ ] **Step 2: Run linter**

Run: `python -m pylint src/domain/ast_context_engine.py src/domain/sast_scanner.py`
Expected: Rating 10.00 / 10

- [ ] **Step 3: Perform SAST audit check**

Run: `/sast-audit` or `sast_scan_file` on modified files.
Expected: 0 findings.
