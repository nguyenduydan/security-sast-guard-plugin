"""Unit tests for scripts/md_to_json.py rule converter."""

import json
from pathlib import Path

from scripts.md_to_json import parse_md_rules, sync_rules


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
