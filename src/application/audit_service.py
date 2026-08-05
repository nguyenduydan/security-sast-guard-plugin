import json
from pathlib import Path
from typing import Any

from src.domain.sast_scanner import SASTScanner
from src.infrastructure.integrity_checker import IntegrityChecker
from src.infrastructure.profile_loader import ProfileLoader
from src.infrastructure.report_generator import generate_markdown_report


class AuditService:
    """Orchestrates SAST audits, profile evaluation, and report generation."""

    def __init__(self, profile_path: str = "profile.json"):
        self.profile_path = profile_path
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

    def set_audit_level(self, level: str) -> bool:
        """Set active audit level in profile configuration."""
        valid_levels = ("lite", "full", "ultra")
        normalized = level.lower().strip()
        if normalized not in valid_levels:
            return False

        path = Path(self.profile_path)
        if not path.exists():
            return False

        try:
            with open(path, encoding="utf-8") as f:
                data = json.load(f)

            data["audit_level"] = normalized

            with open(path, "w", encoding="utf-8") as f:
                json.dump(data, f, indent=2, ensure_ascii=False)
                f.write("\n")

            self.profile["audit_level"] = normalized

            checksum_path = Path(".profile.sha256")
            if checksum_path.exists():
                IntegrityChecker.update_signature(path, checksum_path)

            return True
        except (json.JSONDecodeError, OSError):
            return False

    def get_status(self) -> dict[str, Any]:
        """Return operational status of security guard."""
        firewall = self.profile.get("command_firewall_overlay", {})
        return {
            "project_id": self.profile.get("project_id", "unknown"),
            "stack": self.profile.get("stack", "unknown"),
            "mode": self.profile.get("mode", "strict"),
            "audit_level": self.profile.get("audit_level", "full"),
            "deny_count": len(firewall.get("deny", [])),
            "confirm_count": len(firewall.get("confirm", [])),
        }
