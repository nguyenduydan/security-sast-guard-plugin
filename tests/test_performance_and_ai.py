"""Tests for GitHelper, AIVerifier, and early directory pruning performance."""

import time
from pathlib import Path

from src.domain.ai_cache import AICache
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


def test_ai_verifier_sanitizer_in_preceding_line() -> None:
    verifier = AIVerifier()
    finding = {
        "rule_id": "CMD_INJECTION",
        "path": "worker.py",
        "line": 4,
        "line_content": "os.system(safe_cmd)",
        "context_window": [
            "import os",
            "import shlex",
            "safe_cmd = shlex.quote(user_input)",
            "os.system(safe_cmd)",
        ],
        "severity": "HIGH",
    }
    assert verifier.is_false_positive(finding) is True


def test_ai_verifier_dompurify_in_preceding_line() -> None:
    verifier = AIVerifier()
    finding = {
        "rule_id": "XSS_DOM",
        "path": "component.js",
        "line": 3,
        "line_content": "element.innerHTML = cleanHtml;",
        "context_window": [
            "const cleanHtml = DOMPurify.sanitize(dirtyInput);",
            "element.innerHTML = cleanHtml;",
        ],
        "severity": "HIGH",
    }
    assert verifier.is_false_positive(finding) is True


def test_ai_verifier_path_sanitizer_in_preceding_line() -> None:
    verifier = AIVerifier()
    finding = {
        "rule_id": "PATH_TRAVERSAL",
        "path": "file_reader.py",
        "line": 3,
        "line_content": "open(safe_path, 'r')",
        "context_window": [
            "safe_path = os.path.abspath(user_path)",
            "open(safe_path, 'r')",
        ],
        "severity": "HIGH",
    }
    assert verifier.is_false_positive(finding) is True


def test_ai_verifier_sql_parameterized_in_context_window() -> None:
    verifier = AIVerifier()
    finding = {
        "rule_id": "SQL_INJECTION",
        "path": "service.py",
        "line": 4,
        "line_content": "cursor.execute(sql_query, params={'id': user_id})",
        "context_window": [
            "sql_query = 'SELECT * FROM accounts WHERE id = :param'",
            "cursor.execute(sql_query, params={'id': user_id})",
        ],
        "severity": "HIGH",
    }
    assert verifier.is_false_positive(finding) is True


def test_ai_verifier_safe_typecast_in_context_window() -> None:
    verifier = AIVerifier()
    finding = {
        "rule_id": "SQL_INJECTION",
        "path": "views.py",
        "line": 3,
        "line_content": "db.execute(f'SELECT * FROM users WHERE id = {user_id}')",
        "context_window": [
            "user_id = int(request.GET['id'])",
            "db.execute(f'SELECT * FROM users WHERE id = {user_id}')",
        ],
        "severity": "HIGH",
    }
    assert verifier.is_false_positive(finding) is True


def test_ai_verifier_filter_false_positives_batch_with_context(
    tmp_path: Path,
) -> None:
    cache = AICache(cache_file=tmp_path / "cache.json")
    verifier = AIVerifier(cache=cache)

    findings = [
        {
            "rule_id": "CMD_INJECTION",
            "line_content": "subprocess.run(escaped_cmd, shell=True)",
            "path": "exec.py",
            "severity": "HIGH",
            "context_window": [
                "escaped_cmd = escapeshellcmd(raw_cmd)",
                "subprocess.run(escaped_cmd, shell=True)",
            ],
        },
        {
            "rule_id": "XSS",
            "line_content": "render(bleached_text)",
            "path": "view.py",
            "severity": "HIGH",
            "context_window": [
                "bleached_text = bleach.clean(raw_text)",
                "render(bleached_text)",
            ],
        },
        {
            "rule_id": "PATH_TRAVERSAL",
            "line_content": "open(p, 'w')",
            "path": "fs.py",
            "severity": "HIGH",
            "context_window": [
                "p = pathlib.Path(base).resolve()",
                "open(p, 'w')",
            ],
        },
        {
            "rule_id": "COMMAND_INJECTION",
            "line_content": "os.system('rm -rf ' + user_folder)",
            "path": "danger.py",
            "severity": "CRITICAL",
            "context_window": [
                "user_folder = request.GET['folder']",
                "os.system('rm -rf ' + user_folder)",
            ],
        },
    ]

    verified, fp_count = verifier.filter_false_positives(findings)
    assert fp_count == 3
    assert len(verified) == 1
    assert verified[0]["path"] == "danger.py"

    # Second pass should hit cache
    verified2, fp_count2 = verifier.filter_false_positives(findings)
    assert fp_count2 == 3
    assert len(verified2) == 1
    assert verified2[0]["path"] == "danger.py"


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
