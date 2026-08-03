from pathlib import Path
from unittest.mock import patch

from src.domain.sast_scanner import SASTScanner


def test_sast_scanner_lazy_prompt(tmp_path: Path) -> None:
    test_file = tmp_path / "vuln.py"
    test_file.write_text(
        "import sqlite3\ndef fetch():\n    query = 'SELECT * FROM users'\n"
    )

    scanner = SASTScanner()
    match_item = [{"line": 3, "rule": "SQLi"}]

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



