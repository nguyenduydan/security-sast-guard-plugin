"""Audit service application orchestrator."""

from typing import Any

from src.domain.sast_scanner import SASTScanner
from src.infrastructure.profile_loader import ProfileLoader
from src.infrastructure.report_generator import generate_markdown_report


class AuditService:
    """Orchestrates SAST audits, profile evaluation, and report generation."""

    def __init__(self, profile_path: str = "profile.json"):
        self.profile_loader = ProfileLoader()
        self.profile = self.profile_loader.load(profile_path)
        self.scanner = SASTScanner(profile_path=profile_path)

    def run_audit(self, target_path: str) -> tuple[list[dict[str, Any]], str, str]:
        """Execute SAST audit on target path and return findings and report."""
        res = self.scanner.scan_with_metadata(target_path)
        findings = res["findings"]
        metadata = res["metadata"]
        audit_level = self.profile.get("audit_level", "full")
        report_md, summary = generate_markdown_report(
            findings,
            target_path=target_path,
            metadata=metadata,
            audit_level=audit_level,
        )
        return findings, report_md, summary

    def get_status(self) -> dict[str, Any]:
        """Return operational status of security guard."""
        firewall = self.profile.get("command_firewall_overlay", {})
        return {
            "project_id": self.profile.get("project_id", "unknown"),
            "stack": self.profile.get("stack", "unknown"),
            "mode": self.profile.get("mode", "strict"),
            "audit_level": self.profile.get("audit_level", "full"),
            "sast_level": self.profile.get("sast_level", "ultra"),
            "deny_count": len(firewall.get("deny", [])),
            "confirm_count": len(firewall.get("confirm", [])),
        }
