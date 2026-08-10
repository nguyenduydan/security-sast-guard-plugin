"""Tests for report generator infrastructure component."""

import json
from pathlib import Path

from src.infrastructure.report_generator import (
    generate_markdown_report,
    generate_sarif_report,
)


def test_generate_markdown_report(tmp_path: Path) -> None:
    findings = [
        {
            "rule_id": "XSS_INLINE_EVENT",
            "rule_name": "XSS Event Test",
            "path": "app.html",
            "line": 5,
            "line_content": '<input onfocus="alert(1)">',
            "severity": "High",
            "scope": "global",
        },
        {
            "rule_id": "BROKEN_ACCESS_CONTROL",
            "rule_name": "Parameter Tampering",
            "path": "server.js",
            "line": 12,
            "line_content": "role = request.query.role",
            "severity": "Critical",
            "scope": "global",
        },
    ]

    report_file, summary = generate_markdown_report(findings, output_dir=str(tmp_path))

    assert Path(report_file).exists()
    content = Path(report_file).read_text(encoding="utf-8")
    assert "SAST Security Audit Report" in content
    assert "Critical" in content
    assert "High" in content
    assert "XSS_INLINE_EVENT" in content
    assert "BROKEN_ACCESS_CONTROL" in content

    assert "Total: 2 findings" in summary
    assert "Critical: 1" in summary
    assert "High: 1" in summary
    assert "file://" in summary


def test_generate_markdown_report_custom_template(tmp_path: Path) -> None:
    custom_tmpl = tmp_path / "custom.md"
    custom_tmpl.write_text(
        "CUSTOM REPORT: {{TOTAL_COUNT}} findings in"
        " {{TARGET_PATH}}\n{{FINDINGS_TABLE}}",
        encoding="utf-8",
    )

    findings = [
        {
            "rule_id": "TEST_RULE",
            "path": "test.py",
            "line": 1,
            "line_content": "eval(x)",
            "severity": "High",
            "scope": "global",
        }
    ]

    report_file, _ = generate_markdown_report(
        findings,
        output_dir=str(tmp_path),
        target_path="src/test.py",
        template_path=custom_tmpl,
    )

    content = Path(report_file).read_text(encoding="utf-8")
    assert "CUSTOM REPORT: 1 findings in src/test.py" in content
    assert "TEST_RULE" in content


def test_generate_sarif_report(tmp_path: Path) -> None:
    findings = [
        {
            "rule_id": "CRITICAL_SQLI",
            "rule_name": "SQL Injection",
            "description": "Unsanitized user input in query",
            "path": "db/query.py",
            "line": 42,
            "line_content": "cursor.execute(query)",
            "severity": "Critical",
            "scope": "global",
        },
        {
            "rule_id": "HIGH_XSS",
            "rule_name": "Cross-Site Scripting",
            "path": "views/index.py",
            "line": 15,
            "line_content": "return innerHTML",
            "severity": "High",
            "scope": "global",
        },
        {
            "rule_id": "MED_HARDCODED_KEY",
            "rule_name": "Hardcoded Key",
            "path": "config.py",
            "line": 10,
            "line_content": "SECRET = '123'",
            "severity": "Medium",
            "scope": "global",
        },
        {
            "rule_id": "LOW_INFO_LEAK",
            "rule_name": "Info Leak",
            "path": "logger.py",
            "line": 5,
            "line_content": "print(debug_info)",
            "severity": "Low",
            "scope": "global",
        },
    ]

    report_file, summary = generate_sarif_report(findings, output_dir=str(tmp_path))

    assert Path(report_file).exists()
    assert report_file.endswith(".sarif")
    assert "SAST Audit completed. Total: 4 findings." in summary
    assert "SARIF report saved to:" in summary

    data = json.loads(Path(report_file).read_text(encoding="utf-8"))

    assert data["version"] == "2.1.0"
    assert "$schema" in data
    assert len(data["runs"]) == 1

    run = data["runs"][0]
    assert run["tool"]["driver"]["name"] == "Security SAST Guard"

    rules = run["tool"]["driver"]["rules"]
    assert len(rules) == 4
    rule_ids = {r["id"] for r in rules}
    assert rule_ids == {
        "CRITICAL_SQLI",
        "HIGH_XSS",
        "MED_HARDCODED_KEY",
        "LOW_INFO_LEAK",
    }

    results = run["results"]
    assert len(results) == 4

    # Check level mapping
    res_map = {r["ruleId"]: r for r in results}
    assert res_map["CRITICAL_SQLI"]["level"] == "error"
    assert res_map["HIGH_XSS"]["level"] == "error"
    assert res_map["MED_HARDCODED_KEY"]["level"] == "warning"
    assert res_map["LOW_INFO_LEAK"]["level"] == "note"

    # Check location & message
    sqli_res = res_map["CRITICAL_SQLI"]
    assert (
        sqli_res["locations"][0]["physicalLocation"]["artifactLocation"]["uri"]
        == "db/query.py"
    )
    assert sqli_res["locations"][0]["physicalLocation"]["region"]["startLine"] == 42
    assert "Unsanitized user input in query" in sqli_res["message"]["text"]


def test_generate_sarif_report_empty(tmp_path: Path) -> None:
    report_file, summary = generate_sarif_report([], output_dir=str(tmp_path))

    assert Path(report_file).exists()
    assert "Total: 0 findings." in summary

    data = json.loads(Path(report_file).read_text(encoding="utf-8"))
    assert data["version"] == "2.1.0"
    assert data["runs"][0]["results"] == []
    assert data["runs"][0]["tool"]["driver"]["rules"] == []


def test_generate_markdown_report_with_remediation(tmp_path: Path) -> None:
    findings = [
        {
            "rule_id": "XSS_INLINE_EVENT",
            "rule_name": "XSS Event Test",
            "path": "app.html",
            "line": 5,
            "line_content": '<input onfocus="alert(1)">',
            "severity": "High",
            "scope": "global",
            "remediation": {
                "fix_before": '<input onfocus="eval(user_input)">',
                "fix_after": (
                    '<input id="user-input">\n<script>\n'
                    "el.addEventListener('focus', safeHandler);\n"
                    "</script>"
                ),
            },
        },
        {
            "rule_id": "RCE_RISK",
            "rule_name": "RCE Risk Test",
            "path": "server.py",
            "line": 10,
            "line_content": "os.system(cmd)",
            "severity": "Critical",
            "scope": "global",
            "fix_before": 'os.system("ping " + user_input)',
            "fix_after": 'subprocess.run(["ping", "-c", "1", user_input], check=True)',
        },
    ]

    report_file, _ = generate_markdown_report(findings, output_dir=str(tmp_path))

    assert Path(report_file).exists()
    content = Path(report_file).read_text(encoding="utf-8")

    assert "❌ Vulnerable Code (Before)" in content
    assert "✅ Secure Defense (After)" in content
    assert '<input onfocus="eval(user_input)">' in content
    assert "safeHandler" in content
    assert 'os.system("ping " + user_input)' in content
    assert "subprocess.run" in content
