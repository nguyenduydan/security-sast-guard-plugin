# Policy Engine & Markdown SAST Rules Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Enhance Security SAST Guard's Policy Engine and Markdown rule converter (`md_to_json.py`) to categorize security findings into 3 risk tiers (`Block`, `Warn`, `Allow`) directly driven by Markdown rule metadata.

**Architecture:** Extend Markdown parser (`scripts/md_to_json.py`) to parse `Action` and `Severity` attributes, update `Finding` domain model (`src/domain/models.py`), and update `sast_scanner.py` policy decision logic to support 3-tier risk handling.

**Tech Stack:** Python 3.11+, dataclasses, re, json, pytest.

## Global Constraints

- Python typing annotations required for all public functions/dataclasses.
- Tests must pass using `pytest`.
- Follow Conventional Commits with scope (`feat(sast): ...`, `fix(sast): ...`).

---

### Task 1: Update Domain Models for Action Support

**Files:**
- Modify: `src/domain/models.py:24-36`
- Test: `tests/test_models.py`

**Interfaces:**
- Consumes: None
- Produces: Updated `Finding` dataclass with `action: str = "Block"` field.

- [ ] **Step 1: Write failing test for updated Finding model**

```python
# Create tests/test_models.py
from src.domain.models import Finding

def test_finding_action_default_and_custom():
    f1 = Finding(
        rule_id="TEST_01",
        rule_name="Test Rule",
        path="src/main.py",
        line=10,
        line_content="eval(x)",
        severity="HIGH",
    )
    assert f1.action == "Block"

    f2 = Finding(
        rule_id="TEST_02",
        rule_name="Warn Rule",
        path="src/main.py",
        line=20,
        line_content="print(x)",
        severity="MEDIUM",
        action="Warn",
    )
    assert f2.action == "Warn"
```

- [ ] **Step 2: Run test to verify it fails**

Run: `pytest tests/test_models.py -v`
Expected: FAIL with Unexpected keyword argument `action` or assertion error.

- [ ] **Step 3: Modify `src/domain/models.py`**

```python
@dataclass(frozen=True)
class Finding:
    """Represents a SAST rule violation finding."""

    rule_id: str
    rule_name: str
    path: str
    line: int
    line_content: str
    severity: str
    scope: str = "global"
    action: str = "Block"
```

- [ ] **Step 4: Run test to verify it passes**

Run: `pytest tests/test_models.py -v`
Expected: PASS

- [ ] **Step 5: Commit**

```bash
git add src/domain/models.py tests/test_models.py
git commit -m "feat(domain): add action field to Finding domain model"
```

---

### Task 2: Enhance Markdown Rule Converter (`md_to_json.py`)

**Files:**
- Modify: `scripts/md_to_json.py:27-36`
- Test: `tests/test_md_to_json.py`

**Interfaces:**
- Consumes: `parse_md_rules(file_path: str)`
- Produces: Structured dictionary containing `action: "Block" | "Warn" | "Allow"`.

- [x] **Step 1: Write failing test for Action parsing in Markdown rules**

```python
# Create tests/test_md_to_json.py
from pathlib import Path
from scripts.md_to_json import parse_md_rules

def test_parse_md_rules_with_action(tmp_path: Path):
    rule_md = tmp_path / "test_rule.md"
    rule_md.write_text(
        """
## [RULE_01] Custom Warning Rule
**Severity:** 🟡 Medium
**Action:** Warn

```regex
(?i)warning_pattern
```
        """.strip(),
        encoding="utf-8"
    )

    rules = parse_md_rules(str(rule_md))
    assert len(rules) == 1
    assert rules[0]["id"] == "RULE_01"
    assert rules[0]["severity"] == "Medium"
    assert rules[0]["action"] == "Warn"
```

- [x] **Step 2: Run test to verify it fails**

Run: `pytest tests/test_md_to_json.py -v`
Expected: FAIL with `KeyError: 'action'`

- [x] **Step 3: Modify `scripts/md_to_json.py`**

Update `parse_md_rules`:
```python
    # Extract Severity
    severity = "High"
    if "🔴 Critical" in content or "Critical" in content:
        severity = "Critical"
    elif "🟡 Medium" in content or "Medium" in content:
        severity = "Medium"
    elif "🟢 Low" in content or "Low" in content:
        severity = "Low"

    # Extract Action
    action = "Block"
    if "Action:" in content:
        action_match = re.search(r"\*\*Action:\*\*\s*(Block|Warn|Allow)", content, re.IGNORECASE)
        if action_match:
            action = action_match.group(1).capitalize()
    elif severity in ("Medium", "Low"):
        action = "Warn" if severity == "Medium" else "Allow"

    # In rule dictionary creation (line 60):
    rules.append(
        {
            "id": rule_id,
            "name": name,
            "description": f"Imported rule from {path.name}",
            "category": path.parent.name,
            "severity": severity,
            "action": action,
            "patterns": patterns,
        }
    )
```

- [x] **Step 4: Run test to verify it passes**

Run: `pytest tests/test_md_to_json.py -v`
Expected: PASS

- [x] **Step 5: Commit**

```bash
git add scripts/md_to_json.py tests/test_md_to_json.py
git commit -m "feat(sast): extract action metadata from markdown rules"
```

---

### Task 3: Update Policy Engine and SAST Scanner Logic

**Files:**
- Modify: `src/domain/sast_scanner.py`
- Test: `tests/test_sast_scanner_action.py`

**Interfaces:**
- Consumes: `Finding` with `action` attribute
- Produces: 3-tier findings evaluation (Block/Warn/Allow).

- [ ] **Step 1: Write failing test for 3-tier SAST scanner findings**

```python
# Create tests/test_sast_scanner_action.py
from src.domain.sast_scanner import SASTScanner
from src.domain.models import Finding

def test_scanner_assigns_action_from_rules():
    rules = [
        {
            "id": "WARN_RULE",
            "name": "Warning Test",
            "description": "Desc",
            "category": "test",
            "severity": "Medium",
            "action": "Warn",
            "patterns": [r"insecure_call"]
        }
    ]
    scanner = SASTScanner(rules=rules)
    findings = scanner.scan_code("insecure_call()", "app.py")
    assert len(findings) == 1
    assert findings[0].action == "Warn"
```

- [ ] **Step 2: Run test to verify it fails**

Run: `pytest tests/test_sast_scanner_action.py -v`
Expected: FAIL (action defaults to Block or missing)

- [ ] **Step 3: Modify `src/domain/sast_scanner.py`**

Ensure `Finding` instantiation in `scan_code` and `scan_file` maps `rule.get("action", "Block")` to `Finding.action`.

- [ ] **Step 4: Run test to verify it passes**

Run: `pytest tests/test_sast_scanner_action.py -v`
Expected: PASS

- [ ] **Step 5: Run full test suite**

Run: `pytest`
Expected: All tests PASS

- [ ] **Step 6: Commit**

```bash
git add src/domain/sast_scanner.py tests/test_sast_scanner_action.py
git commit -m "feat(sast): map rule action to finding dataclass in SASTScanner"
```
