"""Tests for GitHelper, AIVerifier, and early directory pruning performance."""

import time
from pathlib import Path

from src.domain.ai_verifier import AIVerifier
from src.domain.git_helper import GitHelper
from src.domain.ignore_filter import IgnoreFilter
from src.domain.sast_scanner import SASTScanner


def test_git_helper_detection(tmp_path: Path) -> None:
    # Non-git directory should return False
    assert GitHelper.is_git_repo(tmp_path) is False
    assert not GitHelper.get_changed_files(tmp_path)


def test_ai_verifier_false_positives() -> None:
    verifier = AIVerifier()

    # Sanitized finding should be flagged as false positive
    fp_finding = {
        "rule_id": "XSS",
        "line_content": "const clean = DOMPurify.sanitize(input);",
        "severity": "HIGH",
        "path": "app.js",
    }
    assert verifier.is_false_positive(fp_finding) is True

    # Test file low severity finding should be flagged as false positive
    test_finding = {
        "rule_id": "HARDCODED_KEY",
        "line_content": "key = 'dummy_key'",
        "severity": "LOW",
        "path": "tests/test_api.py",
    }
    assert verifier.is_false_positive(test_finding) is True

    # Real vulnerability should NOT be flagged as false positive
    real_vuln = {
        "rule_id": "SQL_INJECTION",
        "line_content": "query = 'SELECT * FROM users WHERE id = ' + user_id",
        "severity": "CRITICAL",
        "path": "src/db.py",
    }
    assert verifier.is_false_positive(real_vuln) is False


def test_early_directory_pruning(tmp_path: Path) -> None:
    ignore_filter = IgnoreFilter(root_dir=tmp_path)
    assert ignore_filter.should_ignore_dir("node_modules") is True
    assert ignore_filter.should_ignore_dir(".venv") is True
    assert ignore_filter.should_ignore_dir("src") is False


def test_scanner_with_ai_verifier_integration(tmp_path: Path) -> None:
    app_file = tmp_path / "app.js"
    app_file.write_text(
        "const safe = DOMPurify.sanitize(userInput);\n", encoding="utf-8"
    )

    scanner = SASTScanner()
    res = scanner.scan_with_metadata(str(tmp_path))

    assert "metadata" in res
    assert "findings" in res
    # False positive with DOMPurify sanitization should be filtered out
    assert len(res["findings"]) == 0


def test_large_file_scan_performance(tmp_path: Path) -> None:
    # Generate a large 5,000-line ASPX file with 100 vulnerability patterns
    large_aspx = tmp_path / "LargeExamDetail.aspx"
    lines = []
    for i in range(1, 5001):
        if i % 50 == 0:
            lines.append('<input onfocus="eval(location.hash)">\n')
        else:
            lines.append(f"<div>Row content {i}</div>\n")
    large_aspx.write_text("".join(lines), encoding="utf-8")

    scanner = SASTScanner()
    start = time.perf_counter()
    res = scanner.scan_with_metadata(str(large_aspx))
    duration = time.perf_counter() - start

    assert res["metadata"]["scanned_files"] == 1
    assert res["metadata"]["total_lines"] == 5000
    assert len(res["findings"]) == 100
    # Must complete scan of 5,000-line file under 2.0 seconds
    assert duration < 2.0
