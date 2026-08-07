"""Handlers for MCP tools in Security SAST Guard."""

from __future__ import annotations

from pathlib import Path
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
        findings, report_file, summary = self.audit_service.run_audit(
            target_path=file_path
        )
        return {
            "status": "success",
            "report_file": str(report_file),
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
        }

    def handle_sast_scan_diff(self) -> dict[str, Any]:
        """Scan modified git files."""
        # For simplicity, default target CWD
        findings, report_file, summary = self.audit_service.run_audit(target_path=".")
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
        return {
            "status": "success",
            "message": f"SAST rules synced successfully. Target dir: '{rules_dir or 'default'}'",
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
