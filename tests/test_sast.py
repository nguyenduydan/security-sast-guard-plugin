from pathlib import Path
from unittest.mock import patch

from src.domain.sast_scanner import SASTScanner


def test_sast_scanner_lazy_prompt(tmp_path: Path) -> None:
    test_file = tmp_path / "vuln.py"
    test_file.write_text(
        "import sqlite3\ndef fetch():\n    query = 'SELECT * FROM users'\n"
    )

    scanner = SASTScanner()
    scanner.mode = "strict"
    match_item = [{"line": 3, "rule": "SQLi", "severity": "HIGH"}]

    # Mocking a regex match detection internally and input() function
    with (
        patch("builtins.input", return_value="Y"),
        patch.object(scanner, "_detect_matches", return_value=match_item),
    ):
        results = scanner.scan(str(test_file))
        # Since user replied 'Y', it's allowed (filtered out of violations)
        assert len(results) == 0

    with (
        patch("builtins.input", return_value="N"),
        patch.object(scanner, "_detect_matches", return_value=match_item),
    ):
        results = scanner.scan(str(test_file))
        # User replied 'N', so it remains a violation
        assert len(results) == 1


def test_sast_scanner_real_regex_detection(tmp_path: Path) -> None:
    test_file = tmp_path / "app.py"
    test_file.write_text(
        '<input onfocus="alert(1)">\n'
        "role = request.query.role\n"
        "# role = request.query.role\n"
        '// <input onfocus="alert(1)">\n'
    )

    scanner = SASTScanner()
    scanner.mode = "strict"

    with patch("builtins.input", return_value="N"):
        results = scanner.scan(str(test_file))

    assert len(results) == 2
    rule_ids = [r["rule_id"] for r in results]
    assert "XSS_INLINE_EVENT" in rule_ids
    assert "BROKEN_ACCESS_CONTROL" in rule_ids
    lines = [r["line"] for r in results]
    assert lines == [1, 2]

