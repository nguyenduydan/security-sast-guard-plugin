# SP-1: Critical Bug Fixes Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Fix 3 critical production blockers in `security-sast-guard`: version mismatch across manifest files, missing `firewall` & `version` command handlers in CLI dispatcher, stub `run_audit_hook.py`, missing `sast-audit-level.toml`, and replace empty `test_plugin.py` stub with real assertions.

**Architecture:** Update `gemini-extension.json` and add CI sync validation; add `firewall` and `version` subcommands in `src/cli/dispatcher.py`; implement target-driven execution in `hooks/run_audit_hook.py`; create `commands/sast-audit-level.toml`; update `tests/test_plugin.py` with real unit tests for manifest schema and version consistency.

**Tech Stack:** Python 3.12, Pytest, Pylint, Mypy, GitHub Actions (YAML).

## Global Constraints

- Python >= 3.12, strict type hints (`mypy` pass without errors).
- Zero warnings/errors on `pylint` (10.00/10 rating required).
- Conventional Commits with scope: `fix(cli): ...`, `fix(hooks): ...`, `test(plugin): ...`, `ci(workflows): ...`.
- No breaking changes to existing `AuditService` API.

---

### Task 1: Version Synchronization & Validation

**Files:**
- Modify: `gemini-extension.json`
- Modify: `.github/workflows/ci.yml`
- Test: `tests/test_plugin.py`

**Interfaces:**
- Consumes: `plugin.json` (version field: `"0.10.0"`)
- Produces: `gemini-extension.json` with matching version `"0.10.0"`

- [ ] **Step 1: Write failing test for version consistency**

Update `tests/test_plugin.py`:
```python
"""Tests for plugin structure, manifests, and version consistency."""

import json
from pathlib import Path

REPO_ROOT = Path(__file__).parent.parent


def test_plugin_json_schema_and_version():
    """Verify plugin.json exists, contains required fields, and matches extension manifest."""
    plugin_path = REPO_ROOT / "plugin.json"
    ext_path = REPO_ROOT / "gemini-extension.json"

    assert plugin_path.exists(), "plugin.json must exist"
    assert ext_path.exists(), "gemini-extension.json must exist"

    with open(plugin_path, encoding="utf-8") as f:
        plugin_data = json.load(f)
    with open(ext_path, encoding="utf-8") as f:
        ext_data = json.load(f)

    # Check required fields in plugin.json
    assert "name" in plugin_data
    assert "version" in plugin_data
    assert "main" in plugin_data
    assert "skills" in plugin_data
    assert len(plugin_data["skills"]) > 0

    # Verify version synchronization
    assert (
        plugin_data["version"] == ext_data["version"]
    ), f"Version mismatch: plugin.json={plugin_data['version']} vs gemini-extension.json={ext_data['version']}"
```

- [ ] **Step 2: Run test to verify it fails**

Run: `python -m pytest tests/test_plugin.py -v`  
Expected: FAIL with `Version mismatch: plugin.json=0.10.0 vs gemini-extension.json=0.0.1`

- [ ] **Step 3: Update gemini-extension.json & CI Workflow**

Update `gemini-extension.json`:
```json
{
  "id": "security-sast-guard",
  "name": "Security SAST Guard",
  "version": "0.10.0",
  "description": "SAST Security Guard plugin for Antigravity & Gemini CLI"
}
```

Add step to `.github/workflows/ci.yml` after setup-python:
```yaml
      - name: Verify Manifest Version Consistency
        run: |
          python -c "import json; p=json.load(open('plugin.json')); e=json.load(open('gemini-extension.json')); assert p['version'] == e['version'], f'Mismatch: {p[\"version\"]} vs {e[\"version\"]}'"
```

- [ ] **Step 4: Run test to verify it passes**

Run: `python -m pytest tests/test_plugin.py -v`  
Expected: PASS

- [ ] **Step 5: Run linter and type checker**

Run: `python -m pylint tests/test_plugin.py`  
Run: `python -m mypy --config-file=pyproject.toml control_plane.py src/`  
Expected: 10.00/10 pylint rating, 0 mypy errors.

- [ ] **Step 6: Commit**

```bash
git add gemini-extension.json .github/workflows/ci.yml tests/test_plugin.py
git commit -m "fix(manifest): synchronize version to 0.10.0 and add CI version check"
```

---

### Task 2: Implement CLI Dispatcher `firewall` and `version` Handlers

**Files:**
- Modify: `src/cli/dispatcher.py`
- Test: `tests/test_cli.py`

**Interfaces:**
- Consumes: Command line arguments from `sys.argv`
- Produces: `dispatch(args: list[str]) -> int` supporting `firewall` and `version` subcommands

- [ ] **Step 1: Write failing tests for firewall and version CLI commands**

Add to `tests/test_cli.py`:
```python
def test_cli_version_command(capsys):
    """Test 'version' command outputs version information."""
    ret = dispatch(["control_plane.py", "version"])
    assert ret == 0
    captured = capsys.readouterr()
    assert "Security SAST Guard v0.10.0" in captured.out


def test_cli_firewall_command_deny(capsys):
    """Test 'firewall' command checks command string and outputs verdict."""
    ret = dispatch(["control_plane.py", "firewall", "Remove-Item -Recurse -Force C:\\Windows"])
    assert ret == 0
    captured = capsys.readouterr()
    assert "DENY" in captured.out or "CONFIRM" in captured.out


def test_cli_firewall_command_allow(capsys):
    """Test 'firewall' command with benign input."""
    ret = dispatch(["control_plane.py", "firewall", "git status"])
    assert ret == 0
    captured = capsys.readouterr()
    assert "ALLOW" in captured.out
```

- [ ] **Step 2: Run test to verify it fails**

Run: `python -m pytest tests/test_cli.py -k "test_cli_version_command or test_cli_firewall"`  
Expected: FAIL with `Unknown command: version` / `Unknown command: firewall`

- [ ] **Step 3: Implement handlers in `src/cli/dispatcher.py`**

In `src/cli/dispatcher.py`:
Add helper function `_handle_version()` and `_handle_firewall(args: list[str])`:

```python
import platform
import sys
from src.infrastructure.profile_loader import ProfileLoader


def _handle_version() -> int:
    """Handle 'version' command."""
    loader = ProfileLoader()
    profile = loader.load_profile()
    ver = profile.version if profile else "0.10.0"
    print(f"Security SAST Guard v{ver}")
    print(f"Python: {platform.python_version()}")
    print(f"Platform: {platform.platform()}")
    return 0


def _handle_firewall(args: list[str]) -> int:
    """Handle 'firewall' command for command inspection."""
    if len(args) < 2:
        print("Usage: control_plane.py firewall <command_string>")
        return 1
    
    cmd_text = " ".join(args[1:])
    loader = ProfileLoader()
    profile = loader.load_profile()
    if not profile:
        print("DENY: Missing or corrupted profile configuration.")
        return 1

    cmd_lower = cmd_text.lower()
    
    # Check Deny Rules
    for pattern in profile.firewall_deny_rules:
        if pattern.lower() in cmd_lower:
            print(f"DENY: Dangerous pattern matched: '{pattern}'")
            return 0
            
    # Check Confirm Rules
    for pattern in profile.firewall_confirm_rules:
        if pattern.lower() in cmd_lower:
            print(f"CONFIRM: Potentially risky pattern matched: '{pattern}'")
            return 0

    print("ALLOW: Command verified safe by firewall.")
    return 0
```

Update `dispatch()` function in `src/cli/dispatcher.py` to route `version` and `firewall`:
```python
    if cmd == "version":
        return _handle_version()
    if cmd == "firewall":
        return _handle_firewall(args[2:])
```

- [ ] **Step 4: Run tests to verify they pass**

Run: `python -m pytest tests/test_cli.py -v`  
Expected: ALL PASS

- [ ] **Step 5: Run linter and type checker**

Run: `python -m pylint src/cli/dispatcher.py tests/test_cli.py`  
Run: `python -m mypy --config-file=pyproject.toml control_plane.py src/`  
Expected: 10.00/10 pylint, 0 mypy errors.

- [ ] **Step 6: Commit**

```bash
git add src/cli/dispatcher.py tests/test_cli.py
git commit -m "fix(cli): add firewall and version command handlers to CLI dispatcher"
```

---

### Task 3: Implement Functional Audit Hook & Missing Command Definition

**Files:**
- Create: `commands/sast-audit-level.toml`
- Modify: `hooks/run_audit_hook.py`
- Test: `tests/test_audit_hook.py`

**Interfaces:**
- Consumes: Environment variable `SAST_TARGET` or optional command line argument
- Produces: `hooks/run_audit_hook.py` main execution scanning target path and printing concise summary

- [ ] **Step 1: Create `commands/sast-audit-level.toml`**

Write `commands/sast-audit-level.toml`:
```toml
[command]
name = "sast-audit-level"
description = "Set or view SAST audit level (lite | full | ultra)"
```

- [ ] **Step 2: Write failing test for `hooks/run_audit_hook.py`**

Create `tests/test_audit_hook.py`:
```python
"""Tests for audit hook execution."""

import os
from unittest.mock import patch
from hooks.run_audit_hook import main


def test_run_audit_hook_no_target(capsys):
    """Verify audit hook prints usage when no target environment variable is provided."""
    with patch.dict(os.environ, {}, clear=True):
        ret = main()
        assert ret == 0
        captured = capsys.readouterr()
        assert "Audit hook: No target specified" in captured.out


def test_run_audit_hook_with_target(capsys, tmp_path):
    """Verify audit hook scans specified target path."""
    test_file = tmp_path / "test.py"
    test_file.write_text("print('hello')", encoding="utf-8")

    with patch.dict(os.environ, {"SAST_TARGET": str(test_file)}):
        ret = main()
        assert ret == 0
        captured = capsys.readouterr()
        assert "SAST Audit completed" in captured.out or "Clean" in captured.out
```

- [ ] **Step 3: Run test to verify it fails**

Run: `python -m pytest tests/test_audit_hook.py -v`  
Expected: FAIL (`ImportError` or assertion failure)

- [ ] **Step 4: Implement `hooks/run_audit_hook.py`**

Update `hooks/run_audit_hook.py`:
```python
"""PostToolCallExecute Audit Hook entrypoint."""

import os
import sys
from pathlib import Path

# Add project root to sys.path
PROJECT_ROOT = Path(__file__).parent.parent
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from src.application.audit_service import AuditService


def main() -> int:
    """Execute audit hook scanning specified target path."""
    target = os.environ.get("SAST_TARGET", "").strip()
    if not target and len(sys.argv) > 1:
        target = sys.argv[1]

    if not target:
        print("Audit hook: No target specified via SAST_TARGET env or argument.")
        return 0

    service = AuditService()
    _, summary = service.run_audit(target_path=target)
    print(summary)
    return 0


if __name__ == "__main__":
    sys.exit(main())
```

- [ ] **Step 5: Run test to verify it passes**

Run: `python -m pytest tests/test_audit_hook.py -v`  
Expected: PASS

- [ ] **Step 6: Run full test suite and linters**

Run: `python -m pytest`  
Run: `python -m pylint control_plane.py hooks/run_audit_hook.py scripts/md_to_json.py src/ tests/`  
Run: `python -m mypy --config-file=pyproject.toml control_plane.py src/`  
Expected: 100% tests pass, 10.00/10 pylint rating, 0 mypy errors.

- [ ] **Step 7: Commit**

```bash
git add commands/sast-audit-level.toml hooks/run_audit_hook.py tests/test_audit_hook.py
git commit -m "fix(hooks): implement functional audit hook and add missing sast-audit-level command definition"
```
