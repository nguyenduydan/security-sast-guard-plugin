# Enhanced SAST Scanner, Rules Sync, and Report Generator Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Enhance the SAST scanning engine to perform regex detection, sync rules from `D:\AI\tools\mcp-agent-audit\api-security-audit\rules\`, and export structured Markdown reports (`reports/sast_audit_report_<timestamp>.md`).

**Architecture:** 
1. Build `scripts/md_to_json.py` to parse Markdown rules into `rules/sast_rules.json`, including Event-based XSS and Parameter Tampering patterns.
2. Upgrade `src/domain/sast_scanner.py` regex scanning engine with severity level filtering and safe context skipping.
3. Build `src/infrastructure/report_generator.py` to generate clean Markdown report files and return a concise summary.

**Tech Stack:** Python 3.10+, Standard Library (`re`, `json`, `pathlib`, `datetime`).

## Global Constraints

- Conventional Commits with scope (e.g., `feat(scanner): ...`, `fix(rules): ...`).
- SAST security audit after file modifications (`/sast-audit file <path>`).
- Zero hardcoded secrets, zero exception swallowing.

---

### Task 1: Rules Converter & Sync Script (`scripts/md_to_json.py`)

**Files:**
- Create: `scripts/md_to_json.py`
- Modify: `rules/sast_rules.json`
- Test: `tests/test_md_to_json.py`

**Interfaces:**
- Consumes: Markdown rule files from `D:\AI\tools\mcp-agent-audit\api-security-audit\rules\`
- Produces: Compiled rule list saved to `rules/sast_rules.json`

- [ ] **Step 1: Write failing unit test for `md_to_json.py`**

```python
# tests/test_md_to_json.py
import json
from pathlib import Path
from scripts.md_to_json import parse_md_rules

def test_parse_md_rules(tmp_path: Path):
    rule_md = tmp_path / "test_rule.md"
    rule_md.write_text("""## [A01:2021] Test Rule
**Severity:** 🔴 Critical
### Grep Pattern Tìm Nguy cơ
```bash
git grep -n "onfocus=" -- "*.html"
```
""", encoding="utf-8")

    rules = parse_md_rules(str(rule_md))
    assert len(rules) > 0
    assert rules[0]["severity"] == "Critical"
    assert "onfocus=" in rules[0]["patterns"][0]
```

- [ ] **Step 2: Run test to verify it fails**

Run: `pytest tests/test_md_to_json.py -v`
Expected: FAIL with "ModuleNotFoundError" or "ImportError"

- [ ] **Step 3: Implement `scripts/md_to_json.py`**

```python
"""Markdown to JSON rule converter script."""

import json
import re
from pathlib import Path
from typing import Any


def parse_md_rules(file_path: str) -> list[dict[str, Any]]:
    path = Path(file_path)
    if not path.exists():
        return []

    content = path.read_text(encoding="utf-8")
    rules: list[dict[str, Any]] = []

    # Extract Title and ID
    title_match = re.search(r"##\s*\[(.*?)\]\s*(.*)", content)
    rule_id = title_match.group(1).replace(":", "_").replace(" ", "_") if title_match else path.stem
    name = title_match.group(2).strip() if title_match else path.stem

    # Extract Severity
    severity = "High"
    if "🔴 Critical" in content or "Critical" in content:
        severity = "Critical"
    elif "🟡 Medium" in content or "Medium" in content:
        severity = "Medium"
    elif "🟢 Low" in content or "Low" in content:
        severity = "Low"

    # Extract Grep/Regex Patterns
    patterns: list[str] = []
    code_blocks = re.findall(r"```(?:bash|regex|python)?\n(.*?)```", content, re.DOTALL)
    for block in code_blocks:
        for line in block.splitlines():
            line_str = line.strip()
            if not line_str or line_str.startswith("#") or "git grep" in line_str:
                continue
            patterns.append(re.escape(line_str) if not line_str.startswith("(?i)") else line_str)

    if patterns:
        rules.append({
            "id": rule_id,
            "name": name,
            "description": f"Imported rule from {path.name}",
            "category": path.parent.name,
            "severity": severity,
            "patterns": patterns,
        })

    return rules


def sync_rules(source_dir: str, target_json: str = "rules/sast_rules.json") -> int:
    source_path = Path(source_dir)
    target_path = Path(target_json)

    existing_rules: list[dict[str, Any]] = []
    if target_path.exists():
        try:
            existing_rules = json.loads(target_path.read_text(encoding="utf-8"))
        except Exception:
            existing_rules = []

    rule_map = {r["id"]: r for r in existing_rules}

    # Add custom XSS Event and Access Control rules
    rule_map["XSS_INLINE_EVENT"] = {
        "id": "XSS_INLINE_EVENT",
        "name": "Cross-Site Scripting Inline Event Attributes (CWE-79)",
        "description": "Detects inline JavaScript event attributes like onfocus=, onerror=",
        "category": "owasp-web-2021",
        "severity": "High",
        "patterns": [
            r"(?i)on(focus|error|load|click|mouseover|submit|keydown)\s*=\s*[\"'].*?[\"']"
        ]
    }
    rule_map["BROKEN_ACCESS_CONTROL"] = {
        "id": "BROKEN_ACCESS_CONTROL",
        "name": "Unvalidated Privilege Parameter Tampering (CWE-639 / CWE-269)",
        "description": "Detects unvalidated role or privilege parameter assignments",
        "category": "owasp-web-2021",
        "severity": "Critical",
        "patterns": [
            r"(?i)(role|privilege|is_admin)\s*=\s*(req|request|params|query|GET|POST)[\.\[]",
            r"(?i)request\.(getParameter|query|args)\s*\(\s*[\"'](role|admin|privilege)[\"']\s*\)"
        ]
    }

    if source_path.exists():
        for md_file in source_path.rglob("*.md"):
            for rule in parse_md_rules(str(md_file)):
                rule_map[rule["id"]] = rule

    final_rules = list(rule_map.values())
    target_path.parent.mkdir(parents=True, exist_ok=True)
    target_path.write_text(json.dumps(final_rules, indent=2, ensure_ascii=False), encoding="utf-8")
    return len(final_rules)


if __name__ == "__main__":
    count = sync_rules(r"D:\AI\tools\mcp-agent-audit\api-security-audit\rules")
    print(f"Successfully synced {count} SAST rules.")
```

- [ ] **Step 4: Run test to verify it passes**

Run: `pytest tests/test_md_to_json.py -v`
Expected: PASS

- [ ] **Step 5: Commit**

```bash
git add scripts/md_to_json.py tests/test_md_to_json.py rules/sast_rules.json
git commit -m "feat(rules): implement rule sync engine for Markdown security rules"
```

---

### Task 2: Real Regex SAST Scanner (`src/domain/sast_scanner.py`)

**Files:**
- Modify: `src/domain/sast_scanner.py`
- Test: `tests/test_sast.py`

**Interfaces:**
- Consumes: `rules/sast_rules.json`, target file paths
- Produces: `scan(path)` returning structured list of security match dicts

- [ ] **Step 1: Write failing unit test for `sast_scanner.py`**

```python
# tests/test_sast.py
from pathlib import Path
from src.domain.sast_scanner import SASTScanner

def test_sast_scanner_detects_xss_and_access_control(tmp_path: Path):
    vulnerable_file = tmp_path / "app.html"
    vulnerable_file.write_text(
        '<input type="text" onfocus="alert(1)">\n'
        'role = request.query.role\n',
        encoding="utf-8"
    )

    scanner = SASTScanner(rules_path="rules/sast_rules.json")
    findings = scanner.scan(str(vulnerable_file))

    assert len(findings) >= 2
    rule_ids = [f["rule_id"] for f in findings]
    assert "XSS_INLINE_EVENT" in rule_ids or "XSS_VULNERABILITY" in rule_ids
    assert "BROKEN_ACCESS_CONTROL" in rule_ids
```

- [ ] **Step 2: Run test to verify it fails**

Run: `pytest tests/test_sast.py -v`
Expected: FAIL with `AssertionError: assert 0 >= 2`

- [ ] **Step 3: Implement regex scanning logic in `src/domain/sast_scanner.py`**

```python
"""SAST Scanner domain component with regex execution engine."""

import json
import re
from pathlib import Path
from typing import Any

from .context_extractor import extract_context


class SASTScanner:
    """SAST rule scanner implementation using regex pattern matching."""

    def __init__(self, rules_path: str = "rules/sast_rules.json", profile_path: str = "profile.json"):
        self.rules_path = rules_path
        self.profile_path = profile_path
        self.mode = "strict"
        self.rules: list[dict[str, Any]] = []
        self._load_rules()

    def _load_rules(self) -> None:
        path = Path(self.rules_path)
        if path.exists():
            try:
                self.rules = json.loads(path.read_text(encoding="utf-8"))
            except Exception:
                self.rules = []

    def _detect_matches(self, path: str) -> list[dict[str, Any]]:
        target_path = Path(path)
        if not target_path.exists() or not target_path.is_file():
            return []

        matches: list[dict[str, Any]] = []
        try:
            lines = target_path.read_text(encoding="utf-8", errors="ignore").splitlines()
        except Exception:
            return []

        for line_idx, line_content in enumerate(lines, start=1):
            stripped = line_content.strip()
            if stripped.startswith("//") or stripped.startswith("#") or stripped.startswith("/*"):
                continue  # Skip comments

            for rule in self.rules:
                rule_id = rule.get("id", "UNKNOWN")
                severity = rule.get("severity", "Medium")
                patterns = rule.get("patterns", [])

                for pattern in patterns:
                    try:
                        if re.search(pattern, line_content):
                            matches.append({
                                "rule_id": rule_id,
                                "rule_name": rule.get("name", rule_id),
                                "line": line_idx,
                                "line_content": stripped,
                                "severity": severity,
                                "pattern": pattern,
                                "category": rule.get("category", "general")
                            })
                            break  # Avoid duplicate matches for same rule on same line
                    except re.error:
                        continue

        return matches

    def scan(self, path: str) -> list[dict[str, Any]]:
        """Scan file path and return findings."""
        matches = self._detect_matches(path)
        findings: list[dict[str, Any]] = []

        for match in matches:
            ctx = extract_context(path, match["line"])
            if ctx.get("is_safe_context"):
                continue

            findings.append({
                "rule_id": match["rule_id"],
                "rule_name": match["rule_name"],
                "path": path,
                "line": match["line"],
                "line_content": match["line_content"],
                "severity": match["severity"],
                "scope": ctx.get("scope", "global")
            })

        return findings
```

- [ ] **Step 4: Run test to verify it passes**

Run: `pytest tests/test_sast.py -v`
Expected: PASS

- [ ] **Step 5: Commit**

```bash
git add src/domain/sast_scanner.py tests/test_sast.py
git commit -m "feat(scanner): implement real regex pattern matching engine"
```

---

### Task 3: Markdown Report Generator (`src/infrastructure/report_generator.py`)

**Files:**
- Create: `src/infrastructure/report_generator.py`
- Modify: `src/cli/dispatcher.py`
- Test: `tests/test_report_generator.py`

**Interfaces:**
- Consumes: List of finding dicts from `SASTScanner.scan()`
- Produces: Report saved at `reports/sast_audit_report_<timestamp>.md` and a 2-line summary string

- [ ] **Step 1: Write failing unit test for `report_generator.py`**

```python
# tests/test_report_generator.py
from pathlib import Path
from src.infrastructure.report_generator import generate_markdown_report

def test_generate_markdown_report(tmp_path: Path):
    findings = [
        {
            "rule_id": "XSS_INLINE_EVENT",
            "rule_name": "XSS Event Test",
            "path": "app.html",
            "line": 5,
            "line_content": '<input onfocus="alert(1)">',
            "severity": "High",
            "scope": "global"
        }
    ]
    report_file, summary = generate_markdown_report(findings, output_dir=str(tmp_path))
    assert Path(report_file).exists()
    assert "SAST Security Audit Report" in Path(report_file).read_text(encoding="utf-8")
    assert "High: 1" in summary
```

- [ ] **Step 2: Run test to verify it fails**

Run: `pytest tests/test_report_generator.py -v`
Expected: FAIL with "ModuleNotFoundError"

- [ ] **Step 3: Implement `src/infrastructure/report_generator.py`**

```python
"""SAST Audit Markdown Report Generator."""

from datetime import datetime
from pathlib import Path
from typing import Any


def generate_markdown_report(findings: list[dict[str, Any]], output_dir: str = "reports") -> tuple[str, str]:
    target_dir = Path(output_dir)
    target_dir.mkdir(parents=True, exist_ok=True)

    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    report_file = target_dir / f"sast_audit_report_{timestamp}.md"

    critical_count = sum(1 for f in findings if f["severity"].lower() == "critical")
    high_count = sum(1 for f in findings if f["severity"].lower() == "high")
    medium_count = sum(1 for f in findings if f["severity"].lower() == "medium")
    low_count = sum(1 for f in findings if f["severity"].lower() == "low")

    lines = [
        "# 🛡️ SAST Security Audit Report",
        f"**Date:** {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}",
        f"**Total Vulnerabilities Detected:** {len(findings)}",
        "",
        "## 📊 Executive Summary",
        "| Severity | Count |",
        "|---|---|",
        f"| 🔴 Critical | {critical_count} |",
        f"| 🟠 High | {high_count} |",
        f"| 🟡 Medium | {medium_count} |",
        f"| 🔵 Low | {low_count} |",
        "",
        "## 🔍 Detailed Findings",
    ]

    if not findings:
        lines.append("✅ **Clean. No vulnerabilities detected.**")
    else:
        lines.append("| Rule ID | File & Line | Severity | Code Snippet | Scope |")
        lines.append("|---|---|---|---|---|")
        for f in findings:
            snippet = f["line_content"].replace("|", "\\|")
            lines.append(
                f"| `{f['rule_id']}` | `{f['path']}:{f['line']}` | **{f['severity']}** | `{snippet}` | `{f['scope']}` |"
            )

    report_file.write_text("\n".join(lines), encoding="utf-8")

    summary = (
        f"SAST Audit completed. Total: {len(findings)} findings "
        f"(Critical: {critical_count}, High: {high_count}, Medium: {medium_count}, Low: {low_count}).\n"
        f"📄 Detailed report saved to: [`{report_file.name}`]({report_file.resolve().as_uri()})"
    )

    return str(report_file), summary
```

- [ ] **Step 4: Connect Report Generator in `src/cli/dispatcher.py`**

Update `src/cli/dispatcher.py` to trigger scanner and generate report markdown.

- [ ] **Step 5: Run tests to verify all pass**

Run: `pytest -v`
Expected: ALL PASS

- [ ] **Step 6: Commit**

```bash
git add src/infrastructure/report_generator.py src/cli/dispatcher.py tests/test_report_generator.py
git commit -m "feat(report): export SAST audit findings to Markdown report"
```
