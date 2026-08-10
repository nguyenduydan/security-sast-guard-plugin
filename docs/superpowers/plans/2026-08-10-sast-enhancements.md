# SAST Enhancements Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Enhance the SAST engine with Remediation code snippets, SARIF 2.1.0 report exporter, and smart Git diff base resolution.

**Architecture:** Add remediation metadata to `rules/sast_rules.json`, extend `report_generator.py` with SARIF and remediation rendering, and update `git_helper.py` with remote tracking diff base detection.

**Tech Stack:** Python 3.12, Pytest, Pylint, Mypy, Ruff.

## Global Constraints

- Code coverage and linter rating must remain at 10.00/10 with pylint.
- No unhandled exceptions; output paths must use posix relative path format for labels.

---

### Task 1: Smart Git Diff Base Resolver in `GitHelper`

**Files:**
- Modify: `src/domain/git_helper.py`
- Test: `tests/test_git_helper.py`

**Interfaces:**
- Consumes: Subprocess git commands
- Produces: `GitHelper.get_diff_base(target_dir: Path | str) -> str`

- [ ] **Step 1: Write failing test for `get_diff_base`**

```python
def test_git_helper_get_diff_base(tmp_path: Path) -> None:
    from src.domain.git_helper import GitHelper
    base = GitHelper.get_diff_base(tmp_path)
    assert isinstance(base, str)
```

- [ ] **Step 2: Run test to verify failure**

Run: `python -m pytest tests/test_git_helper.py`

- [ ] **Step 3: Implement `get_diff_base` in `GitHelper`**

Add `get_diff_base` static method to `GitHelper`.

- [ ] **Step 4: Verify test passes**

Run: `python -m pytest tests/test_git_helper.py`

- [ ] **Step 5: Commit**

```bash
git add src/domain/git_helper.py tests/test_git_helper.py
git commit -m "feat(git): add get_diff_base method to GitHelper"
```

---

### Task 2: SARIF 2.1.0 Exporter in `report_generator.py`

**Files:**
- Modify: `src/infrastructure/report_generator.py`
- Test: `tests/test_report_generator.py`

**Interfaces:**
- Consumes: Findings list, metadata
- Produces: `generate_sarif_report(findings, output_dir, target_path, metadata, audit_level) -> tuple[str, str]`

- [ ] **Step 1: Write failing test for `generate_sarif_report`**

```python
def test_generate_sarif_report(tmp_path: Path) -> None:
    from src.infrastructure.report_generator import generate_sarif_report
    findings = [{"rule_id": "XSS_INLINE_EVENT", "path": "app.html", "line": 5, "line_content": "<input>", "severity": "High"}]
    report_file, summary = generate_sarif_report(findings, output_dir=str(tmp_path))
    assert Path(report_file).exists()
    assert ".sarif" in report_file
```

- [ ] **Step 2: Run test to verify failure**

Run: `python -m pytest tests/test_report_generator.py`

- [ ] **Step 3: Implement `generate_sarif_report`**

Add SARIF 2.1.0 generator function with valid schema fields.

- [ ] **Step 4: Verify test passes**

Run: `python -m pytest tests/test_report_generator.py`

- [ ] **Step 5: Commit**

```bash
git add src/infrastructure/report_generator.py tests/test_report_generator.py
git commit -m "feat(report): implement SARIF 2.1.0 report exporter"
```

---

### Task 3: Remediation Snippets in Rules & Markdown Reports

**Files:**
- Modify: `rules/sast_rules.json`
- Modify: `src/infrastructure/report_generator.py`
- Test: `tests/test_report_generator.py`

**Interfaces:**
- Consumes: `remediation` field from SAST rules
- Produces: Markdown report section "💡 Remediation & Security Action Items" with code diff blocks

- [ ] **Step 1: Write failing test for Remediation Snippets in Markdown**

```python
def test_markdown_remediation_snippets(tmp_path: Path) -> None:
    from src.infrastructure.report_generator import generate_markdown_report
    findings = [{"rule_id": "XSS_INLINE_EVENT", "path": "app.html", "line": 5, "line_content": "<input>", "severity": "High", "remediation": {"fix_before": "old", "fix_after": "new"}}]
    report_file, _ = generate_markdown_report(findings, output_dir=str(tmp_path))
    content = Path(report_file).read_text(encoding="utf-8")
    assert "fix_before" in content or "old" in content
```

- [ ] **Step 2: Run test to verify failure**

Run: `python -m pytest tests/test_report_generator.py`

- [ ] **Step 3: Update `sast_rules.json` & `report_generator.py`**

Add remediation metadata to rules and update `_build_remediation_summary` to render code blocks.

- [ ] **Step 4: Verify test passes and run full linter**

Run: `python -m pytest` and `python -m pylint control_plane.py hooks/run_audit_hook.py scripts/md_to_json.py src/ tests/`

- [ ] **Step 5: Commit**

```bash
git add rules/sast_rules.json src/infrastructure/report_generator.py tests/test_report_generator.py
git commit -m "feat(rules): add remediation snippets to rules and report summary"
```
