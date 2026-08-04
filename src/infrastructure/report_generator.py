"""SAST Audit Markdown Report Generator component."""

from datetime import datetime
from pathlib import Path
from typing import Any


def generate_markdown_report(
    findings: list[dict[str, Any]], output_dir: str = "reports"
) -> tuple[str, str]:
    """Generate Markdown report file for SAST findings and return (path, summary_msg)."""
    target_dir = Path(output_dir)
    target_dir.mkdir(parents=True, exist_ok=True)

    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    report_file = target_dir / f"sast_audit_report_{timestamp}.md"

    critical_count = sum(
        1 for f in findings if str(f.get("severity", "")).lower() == "critical"
    )
    high_count = sum(
        1 for f in findings if str(f.get("severity", "")).lower() == "high"
    )
    medium_count = sum(
        1 for f in findings if str(f.get("severity", "")).lower() == "medium"
    )
    low_count = sum(
        1 for f in findings if str(f.get("severity", "")).lower() == "low"
    )

    lines = [
        "# 🛡️ SAST Security Audit Report",
        f"**Date:** {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}",
        f"**Total Vulnerabilities Detected:** {len(findings)}",
        "",
        "## 📊 Executive Summary",
        "| Severity | Count |",
        "|---|---|",
        f"| 🔴 Critical | {critical_count} |",
        f"| 🟠 High | {high_count} |",
        f"| 🟡 Medium | {medium_count} |",
        f"| 🔵 Low | {low_count} |",
        "",
        "## 🔍 Detailed Findings",
    ]

    if not findings:
        lines.append("✅ **Clean. No vulnerabilities detected.**")
    else:
        lines.append("| Rule ID | File & Line | Severity | Code Snippet | Scope |")
        lines.append("|---|---|---|---|---|")
        for f in findings:
            snippet = str(f.get("line_content", "")).replace("|", "\\|")
            rule_id = f.get("rule_id", "UNKNOWN")
            file_path = f.get("path", "unknown")
            line = f.get("line", 0)
            severity = f.get("severity", "Medium")
            scope = f.get("scope", "global")
            lines.append(
                f"| `{rule_id}` | `{file_path}:{line}` | **{severity}** | `{snippet}` | `{scope}` |"
            )

    report_file.write_text("\n".join(lines), encoding="utf-8")

    file_uri = report_file.resolve().as_uri()
    summary = (
        f"SAST Audit completed. Total: {len(findings)} findings "
        f"(Critical: {critical_count}, High: {high_count}, Medium: {medium_count}, Low: {low_count}).\n"
        f"📄 Detailed report saved to: [`{report_file.name}`]({file_uri})"
    )

    return str(report_file), summary
