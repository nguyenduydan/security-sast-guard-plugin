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
        results = scanner.scan(str(test_file), interactive=True)
        # Since user replied 'Y', it's allowed (filtered out of violations)
        assert len(results) == 0

    with (
        patch("builtins.input", return_value="N"),
        patch.object(scanner, "_detect_matches", return_value=match_item),
    ):
        results = scanner.scan(str(test_file), interactive=True)
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


def test_aspnet_false_positive_filtering(tmp_path: Path) -> None:
    test_file = tmp_path / "page.aspx"
    test_file.write_text(
        '<SweetSoft:ExtraButton ID="btnAdd" runat="server" OnClick="btnAdd_Click" />\n'
        '<div><%= GetResourceText("Label_Title") %></div>\n'
        '<div><%= SecurityHelper.Encrypt("/Uploads/CauHoi") %></div>\n'
        '<button onclick="SweetTable.resetColumns()">Reset</button>\n'
        'lbTitleDlDetail.InnerHtml = "Cập nhật loại giấy tờ";\n'
        'onclick=\'<%# "selectExam(this, " + '
        'Container.ItemIndex + "); return false;" %>\'\n'
        '<input onfocus="eval(location.hash)">\n',
        encoding="utf-8",
    )

    scanner = SASTScanner()
    scanner.mode = "strict"

    results = scanner.scan(str(test_file))

    # Only line 7 (the real malicious JS onfocus) should be detected as finding
    # Lines 1-6 should be filtered out as false positives
    lines = [r["line"] for r in results]
    assert lines == [7]


def test_single_file_scan_unignored_even_if_default_ignored(tmp_path: Path) -> None:
    # Create an .aspx file inside a folder named 'docs' (which is default ignored)
    docs_dir = tmp_path / "docs"
    docs_dir.mkdir(parents=True, exist_ok=True)
    test_file = docs_dir / "ExamDetail.aspx"
    test_file.write_text('<input onfocus="eval(location.hash)">\n')

    scanner = SASTScanner()
    res = scanner.scan_with_metadata(str(test_file))

    assert res["metadata"]["scanned_files"] == 1
    assert len(res["findings"]) == 1


def test_sast_scanner_plaintext_secret_ignores_publickeytoken(tmp_path: Path) -> None:
    test_file = tmp_path / "Web.config"
    test_file.write_text(
        '<assemblyIdentity name="Newtonsoft.Json" '
        'publicKeyToken="mock_public_key_token" />\n'
        'var token = "mock_public_key_token";\n'
    )

    scanner = SASTScanner()
    scanner.mode = "strict"
    # We scan the specific file to override ignore filter for Web.config
    results = scanner.scan(str(test_file))

    # The publicKeyToken line should NOT trigger PLAINTEXT_SECRET
    # But the variable assignment `token = "..."` SHOULD trigger it
    lines = [r["line"] for r in results if r["rule_id"] == "PLAINTEXT_SECRET"]
    assert lines == [2]


def test_ast_precision_safe_constants_suppressed(tmp_path: Path) -> None:
    safe_file = tmp_path / "safe_script.py"
    safe_file.write_text(
        'import os\nos.system("git status")\nuser_id = int(request.args.get("id"))\n'
    )

    scanner = SASTScanner()
    res = scanner.scan_with_metadata(str(safe_file))
    assert len(res["findings"]) == 0

    code = 'import os\nos.system("git status")\n'
    findings = scanner.scan_code(code, filename="safe_task.py")
    assert len(findings) == 0


def test_ast_precision_real_vulnerability_detected(tmp_path: Path) -> None:
    vuln_file = tmp_path / "vuln_script.py"
    vuln_file.write_text(
        'import os\nuser_input = request.args.get("cmd")\nos.system(user_input)\n'
    )

    scanner = SASTScanner()
    res = scanner.scan_with_metadata(str(vuln_file))
    assert len(res["findings"]) == 1
    assert res["findings"][0]["rule_id"] == "RCE_RISK"
    assert "context_window" in res["findings"][0]
    assert len(res["findings"][0]["context_window"]) > 0

    code = "import os\nos.system(user_input)\n"
    findings = scanner.scan_code(code, filename="vuln_task.py")
    assert len(findings) == 1
    assert findings[0].rule_id == "RCE_RISK"


def test_scan_code_ai_verifier_and_context_parity(tmp_path: Path) -> None:
    """Ensure scan_code applies ContextExtractor and AIVerifier like scan()."""
    # Safe code with DOMPurify sanitizer preceding line
    safe_code = (
        "const clean = DOMPurify.sanitize(user_input);\n"
        'document.getElementById("out").innerHTML = clean;\n'
    )
    safe_file = tmp_path / "safe_dom.js"
    safe_file.write_text(safe_code, encoding="utf-8")

    scanner = SASTScanner()
    file_findings = scanner.scan(str(safe_file))
    code_findings = scanner.scan_code(safe_code, filename="safe_dom.js")

    # Both file scan and in-memory scan_code filter the sanitized innerHTML finding
    assert len(file_findings) == 0
    assert len(code_findings) == 0
