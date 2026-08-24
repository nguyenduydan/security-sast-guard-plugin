"""Unit tests for scripts/md_to_json.py rule converter."""

import json
import sys
from pathlib import Path

from scripts.md_to_json import main, parse_md_rules, sync_rules


def test_parse_md_rules(tmp_path: Path) -> None:
    rule_md = tmp_path / "test_rule.md"
    rule_md.write_text(
        """## [A01:2021] Test Rule
**Severity:** 🔴 Critical
### Grep Pattern Tìm Nguy cơ
```bash
git grep -n "onfocus=" -- "*.html"
```
""",
        encoding="utf-8",
    )

    rules = parse_md_rules(str(rule_md))
    assert len(rules) > 0
    assert rules[0]["severity"] == "Critical"


def test_sync_rules(tmp_path: Path) -> None:
    rules_dir = tmp_path / "source_rules"
    rules_dir.mkdir()
    rule_md = rules_dir / "sample.md"
    rule_md.write_text(
        """## [TEST01] Sample Rule
**Severity:** 🟡 Medium
```regex
test_pattern_123
```
""",
        encoding="utf-8",
    )

    target_json = tmp_path / "output_rules.json"
    count = sync_rules(str(rules_dir), target_json=str(target_json))

    assert count >= 3
    assert target_json.exists()

    data = json.loads(target_json.read_text(encoding="utf-8"))
    rule_ids = [r["id"] for r in data]
    assert "XSS_INLINE_EVENT" in rule_ids
    assert "BROKEN_ACCESS_CONTROL" in rule_ids
    assert "TEST01" in rule_ids


def test_parse_md_rules_with_action(tmp_path: Path) -> None:
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
        encoding="utf-8",
    )

    rules = parse_md_rules(str(rule_md))
    assert len(rules) == 1
    assert rules[0]["id"] == "RULE_01"
    assert rules[0]["severity"] == "Medium"
    assert rules[0]["action"] == "Warn"


def test_main_default_rules_resolution(monkeypatch: object, tmp_path: Path) -> None:
    output_json = tmp_path / "sast_rules.json"
    monkeypatch.setattr(sys, "argv", ["md_to_json.py", "--target", str(output_json)])
    main()
    assert output_json.exists()


def test_sync_rules_filters_empty_patterns(tmp_path: Path) -> None:
    target_json = tmp_path / "rules_with_empty.json"
    target_json.write_text(
        json.dumps(
            [
                {
                    "id": "EMPTY_STUB",
                    "name": "Empty Stub Rule",
                    "patterns": [],
                },
                {
                    "id": "VALID_RULE",
                    "name": "Valid Rule",
                    "patterns": ["valid_regex"],
                },
            ]
        ),
        encoding="utf-8",
    )

    empty_dir = tmp_path / "empty_rules"
    empty_dir.mkdir()
    count = sync_rules(str(empty_dir), target_json=str(target_json))
    assert count >= 1

    data = json.loads(target_json.read_text(encoding="utf-8"))
    rule_ids = [r["id"] for r in data]
    assert "EMPTY_STUB" not in rule_ids
    assert "VALID_RULE" in rule_ids
