"""Tests for report generator infrastructure component."""

from pathlib import Path

from src.infrastructure.report_generator import generate_markdown_report


def test_generate_markdown_report(tmp_path: Path):
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
