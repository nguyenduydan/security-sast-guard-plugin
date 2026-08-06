"""Handlers for MCP tools in Security SAST Guard."""

from __future__ import annotations

from typing import Any

from src.application.audit_service import AuditService
from src.domain.firewall_engine import FirewallEngine
from src.infrastructure.profile_loader import ProfileLoader


class MCPToolHandlers:
    """Class exposing handlers for all registered MCP tools."""

    def __init__(self) -> None:
        self.audit_service = AuditService()
        self.profile_loader = ProfileLoader()

    def handle_sast_scan_file(self, file_path: str) -> dict[str, Any]:
        """Scan a single file."""
        report_file, findings, summary = self.audit_service.run_audit(
            target_path=file_path
        )
        return {
            "status": "success",
            "report_file": str(report_file),
            "findings_count": len(findings),
            "summary": summary,
            "findings": [
                {
                    "rule_id": f.rule_id,
                    "rule_name": f.rule_name,
                    "severity": f.severity,
                    "file_path": f.file_path,
                    "line_number": f.line_number,
                    "action": f.action,
                }
                for f in findings
            ],
        }

    def handle_sast_scan_diff(self) -> dict[str, Any]:
        """Scan modified git files."""
        # For simplicity, default target CWD
        report_file, findings, summary = self.audit_service.run_audit(target_path=".")
        return {
            "status": "success",
            "report_file": str(report_file),
            "findings_count": len(findings),
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
            "project_id": status.get("project_id", "unknown"),
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
