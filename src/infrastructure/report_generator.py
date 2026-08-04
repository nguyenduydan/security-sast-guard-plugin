"""SAST Audit Markdown Report Generator component."""

from datetime import datetime
from pathlib import Path
from typing import Any


def _count_severities(findings: list[dict[str, Any]]) -> dict[str, int]:
    counts = {"critical": 0, "high": 0, "medium": 0, "low": 0}
    for f in findings:
        sev = str(f.get("severity", "")).lower()
        if sev in counts:
            counts[sev] += 1
    return counts


def _build_finding_row(f: dict[str, Any]) -> str:
    snippet = str(f.get("line_content", "")).replace("|", "\\|")
    rule_id = f.get("rule_id", "UNKNOWN")
    location = f"{f.get('path', 'unknown')}:{f.get('line', 0)}"
    severity = f.get("severity", "Medium")
    scope = f.get("scope", "global")
    return (
        f"| `{rule_id}` | `{location}` | **{severity}** | "
        f"`{snippet}` | `{scope}` |"
    )


def generate_markdown_report(
    findings: list[dict[str, Any]], output_dir: str = "reports"
) -> tuple[str, str]:
    """Generate Markdown report file for SAST findings."""
    target_dir = Path(output_dir)
    target_dir.mkdir(parents=True, exist_ok=True)

    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    report_file = target_dir / f"sast_audit_report_{timestamp}.md"
    counts = _count_severities(findings)

    lines = [
        "# 🛡️ SAST Security Audit Report",
        f"**Date:** {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}",
        f"**Total Vulnerabilities Detected:** {len(findings)}",
        "",
        "## 📊 Executive Summary",
        "| Severity | Count |",
        "|---|---|",
        f"| 🔴 Critical | {counts['critical']} |",
        f"| 🟠 High | {counts['high']} |",
        f"| 🟡 Medium | {counts['medium']} |",
        f"| 🔵 Low | {counts['low']} |",
        "",
        "## 🔍 Detailed Findings",
    ]

    if not findings:
        lines.append("✅ **Clean. No vulnerabilities detected.**")
    else:
        lines.append("| Rule ID | File & Line | Severity | Code Snippet | Scope |")
        lines.append("|---|---|---|---|---|")
        for f in findings:
            lines.append(_build_finding_row(f))

    report_file.write_text("\n".join(lines), encoding="utf-8")

    file_uri = report_file.resolve().as_uri()
    summary = (
        f"SAST Audit completed. Total: {len(findings)} findings "
        f"(Critical: {counts['critical']}, High: {counts['high']}, "
        f"Medium: {counts['medium']}, Low: {counts['low']}).\n"
        f"Detailed report saved to: [{report_file.name}]({file_uri})"
    )

    return str(report_file), summary
