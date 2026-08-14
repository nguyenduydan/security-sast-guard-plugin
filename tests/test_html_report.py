"""Unit tests for HTML report generator."""

from pathlib import Path

from src.infrastructure.html_report_generator import generate_html_report


def test_generate_html_report(tmp_path) -> None:
    """Verify HTML report generation produces valid self-contained HTML."""
    findings = [
        {
            "rule_id": "RCE_RISK",
            "rule_name": "Remote Code Execution",
            "path": "src/app.py",
            "line": 42,
            "severity": "Critical",
            "line_content": "os.system(user_cmd)",
            "remediation": {
                "fix_before": "os.system(user_cmd)",
                "fix_after": "subprocess.run([user_cmd])",
            },
        },
        {
            "rule_id": "XSS_VULNERABILITY",
            "rule_name": "Cross-Site Scripting",
            "path": "src/views.py",
            "line": 15,
            "severity": "High",
            "line_content": "element.innerHTML = userInput",
        },
    ]

    metadata = {
        "scanned_files": 12,
        "total_lines": 1500,
        "duration_seconds": 0.45,
    }

    report_path_str, summary = generate_html_report(
        findings=findings,
        output_dir=str(tmp_path),
        target_path="src/",
        metadata=metadata,
        audit_level="full",
    )

    report_file = Path(report_path_str)
    assert report_file.exists()
    content = report_file.read_text(encoding="utf-8")

    assert "<!DOCTYPE html>" in content
    assert "SAST Security Audit Dashboard" in content
    assert "RCE_RISK" in content
    assert "XSS_VULNERABILITY" in content
    assert "Critical" in content
    assert "High" in content
    assert "HTML report saved to:" in summary
