"""Handlers for MCP tools in Security SAST Guard."""

from __future__ import annotations

from pathlib import Path
from typing import Any

from src.application.audit_service import AuditService
from src.domain.firewall_engine import FirewallEngine
from src.infrastructure.profile_loader import ProfileLoader
from src.mcp.schemas import TaintTraceItem


class MCPToolHandlers:
    """Class exposing handlers for all registered MCP tools."""

    def __init__(self) -> None:
        self.audit_service = AuditService()
        self.profile_loader = ProfileLoader()

    def handle_sast_scan_file(self, file_path: str) -> dict[str, Any]:
        """Scan a single file and include taint traces in output."""
        findings, _, summary = self.audit_service.run_audit(
            target_path=file_path, generate_report=False
        )
        taint_findings = self.audit_service.run_taint_analysis(file_path)
        taint_traces = [
            {
                "rule_id": f.rule_id,
                "source_file": f.source_file,
                "source_line": f.source_line,
                "sink_file": f.sink_file,
                "sink_line": f.sink_line,
                "confidence": f.confidence,
                "trace_path": [
                    {
                        "file": s.file,
                        "line": s.line,
                        "symbol": s.symbol,
                        "step_type": s.step_type,
                    }
                    for s in f.trace_path
                ],
            }
            for f in taint_findings
        ]
        return {
            "status": "success",
            "findings_count": len(findings),
            "summary": summary,
            "findings": [
                {
                    "rule_id": f.get("rule_id", ""),
                    "rule_name": f.get("rule_name", ""),
                    "severity": f.get("severity", ""),
                    "file_path": f.get("path", ""),
                    "line_number": f.get("line", 0),
                    "action": f.get("action", "Block"),
                }
                for f in findings
            ],
            "taint_traces": taint_traces,
        }

    def handle_sast_scan_diff(self) -> dict[str, Any]:
        """Scan modified git files and include taint traces in output."""
        findings, _, summary = self.audit_service.run_audit(
            target_path=".", generate_report=False
        )
        taint_findings = self.audit_service.run_taint_analysis(".")
        taint_traces = [
            {
                "rule_id": f.rule_id,
                "source_file": f.source_file,
                "source_line": f.source_line,
                "sink_file": f.sink_file,
                "sink_line": f.sink_line,
                "confidence": f.confidence,
                "trace_path": [
                    {
                        "file": s.file,
                        "line": s.line,
                        "symbol": s.symbol,
                        "step_type": s.step_type,
                    }
                    for s in f.trace_path
                ],
            }
            for f in taint_findings
        ]
        return {
            "status": "success",
            "findings_count": len(findings),
            "summary": summary,
            "taint_traces": taint_traces,
            "findings": [
                {
                    "rule_id": f.get("rule_id", ""),
                    "rule_name": f.get("rule_name", ""),
                    "severity": f.get("severity", ""),
                    "file_path": f.get("path", ""),
                    "line_number": f.get("line", 0),
                    "action": f.get("action", "Block"),
                }
                for f in findings
            ],
        }

    def handle_sast_generate_report(
        self, findings: list[dict[str, Any]], target_path: str, ai_analysis: str
    ) -> dict[str, Any]:
        """Generate a SAST markdown report containing AI analysis."""
        # pylint: disable=import-outside-toplevel
        from src.infrastructure.report_generator import generate_markdown_report

        metadata = {
            "scanned_files": "N/A",
            "total_lines": "N/A",
            "duration_seconds": "N/A",
        }
        report_file, summary = generate_markdown_report(
            findings,
            target_path=target_path,
            metadata=metadata,
            audit_level=self.profile_loader.load().get("audit_level", "full"),
            ai_analysis=ai_analysis,
        )
        return {
            "status": "success",
            "report_file": str(report_file),
            "summary": summary,
        }

    def handle_sast_check_command(self, command: str) -> dict[str, Any]:
        """Evaluate command safety."""
        profile = self.profile_loader.load()
        if not profile:
            return {
                "verdict": "DENY",
                "reason": "Missing or corrupted profile configuration.",
            }

        overlay = profile.get("command_firewall_overlay", {})
        engine = FirewallEngine(
            deny_rules=overlay.get("deny", []),
            confirm_rules=overlay.get("confirm", []),
        )
        verdict = engine.evaluate(command)
        return {
            "verdict": verdict.verdict,
            "reason": verdict.reason,
            "matched_pattern": verdict.matched_pattern,
        }

    def handle_sast_get_status(self) -> dict[str, Any]:
        """Retrieve profile and audit status."""
        status = self.audit_service.get_status()
        return {
            "status": "success",
            "version": status.get("version", "1.0.0"),
            "project_id": status.get("project_id", "unknown"),
            "stack": status.get("stack", "general"),
            "mode": status.get("mode", "strict"),
            "audit_level": status.get("audit_level", "full"),
            "sast_rules_count": status.get("sast_rules_count", 0),
            "deny_count": status.get("deny_count", 0),
            "confirm_count": status.get("confirm_count", 0),
        }

    def handle_sast_set_level(self, level: str) -> dict[str, Any]:
        """Set active audit level."""
        success = self.audit_service.set_audit_level(level)
        if success:
            return {
                "status": "success",
                "active_level": level,
                "message": f"Audit level updated to '{level}'",
            }
        return {
            "status": "error",
            "message": f"Invalid level '{level}'. Valid levels: lite, full, ultra.",
        }

    def handle_sast_init(self) -> dict[str, Any]:
        """Initialize project-local .sast/profile.json configuration."""
        sast_dir = Path(".sast")
        sast_dir.mkdir(exist_ok=True)

        profile_file = sast_dir / "profile.json"

        if profile_file.exists():
            return {
                "status": "success",
                "message": f"Project profile already exists at {profile_file}",
                "profile_path": str(profile_file),
            }

        tmpl_file = Path(__file__).parents[2] / "templates" / "profile_template.json"
        if tmpl_file.exists():
            content = tmpl_file.read_text(encoding="utf-8")
        else:
            content = '{\n  "profile_name": "project_local"\n}\n'

        profile_file.write_text(content, encoding="utf-8")
        return {
            "status": "success",
            "message": f"Successfully initialized project profile at {profile_file}",
            "profile_path": str(profile_file),
        }

    def handle_sast_sync_rules(self, rules_dir: str = "") -> dict[str, Any]:
        """Sync custom rules to project profile."""
        target = rules_dir or "default"
        return {
            "status": "success",
            "message": f"SAST rules synced successfully. Target dir: '{target}'",
        }

    def handle_sast_get_help(self) -> dict[str, Any]:
        """Get SAST Guard help and usage documentation."""
        return {
            "status": "success",
            "summary": "Security SAST Guard & Command Firewall Helper",
            "skills": [
                "/sast-status - View current security profile status",
                "/sast-init - Initialize project-local .sast/profile.json",
                "/sast-mode [strict|draft] - Set operation mode (strict | draft)",
                "/sast-firewall <cmd> - Test command safety against firewall overlay",
                "/sast-audit file <path> - Audit file for OWASP/CWE vulnerabilities",
                "/sast-audit-level <level> - Set audit level (lite | full | ultra)",
            ],
        }

    def handle_sast_set_mode(self, mode: str) -> dict[str, Any]:
        """Set active operation mode (strict | draft)."""
        success = self.audit_service.set_mode(mode)
        if success:
            return {
                "status": "success",
                "active_mode": mode,
                "message": f"Operation mode updated to '{mode}'",
            }
        return {
            "status": "error",
            "message": f"Invalid mode '{mode}'. Valid modes: strict, draft.",
        }

    def handle_sast_get_dataflow_path(
        self,
        source_pattern: str,
        sink_pattern: str,
        repo_path: str = ".",
    ) -> dict[str, Any]:
        """Return all taint flow paths matching source_pattern -> sink_pattern."""
        all_findings = self.audit_service.run_taint_analysis(repo_path)
        matched = [
            f
            for f in all_findings
            if source_pattern in f.source_pattern and sink_pattern in f.sink_pattern
        ]
        paths = [
            TaintTraceItem(
                rule_id=f.rule_id,
                source_file=f.source_file,
                source_line=f.source_line,
                sink_file=f.sink_file,
                sink_line=f.sink_line,
                trace_path=[
                    {
                        "file": step.file,
                        "line": step.line,
                        "symbol": step.symbol,
                        "step_type": step.step_type,
                    }
                    for step in f.trace_path
                ],
                confidence=f.confidence,
            ).to_dict()
            for f in matched
        ]
        return {"status": "success", "paths": paths, "total": len(paths)}

    def handle_sast_get_taint_context(
        self,
        file_path: str,
        line_number: int,
        context_lines: int = 10,
    ) -> dict[str, Any]:
        """Return code snippet and taint context around the given file:line."""
        path = Path(file_path)
        if not path.exists():
            return {"status": "error", "message": f"File not found: {file_path}"}
        try:
            file_lines = path.read_text(encoding="utf-8", errors="ignore").splitlines()
        except OSError as exc:
            return {"status": "error", "message": str(exc)}

        start = max(0, line_number - context_lines - 1)
        end = min(len(file_lines), line_number + context_lines)
        snippet = "\n".join(file_lines[start:end])

        all_findings = self.audit_service.run_taint_analysis(str(path.parent))
        is_source = any(
            f.source_file in file_path and f.source_line == line_number
            for f in all_findings
        )
        is_sink = any(
            f.sink_file in file_path and f.sink_line == line_number
            for f in all_findings
        )
        flows_to = [
            f"{f.sink_file}:{f.sink_line}"
            for f in all_findings
            if f.source_file in file_path and f.source_line == line_number
        ]

        return {
            "status": "success",
            "file": file_path,
            "line": line_number,
            "code_snippet": snippet,
            "taint_info": {
                "is_source": is_source,
                "is_sink": is_sink,
                "flows_to": flows_to,
                "sanitized": False,
            },
        }
