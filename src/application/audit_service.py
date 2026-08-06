import json
from pathlib import Path
from typing import Any

from src.domain.sast_scanner import SASTScanner
from src.infrastructure.integrity_checker import IntegrityChecker
from src.infrastructure.profile_loader import ProfileLoader
from src.infrastructure.report_generator import generate_markdown_report


class AuditService:
    """Orchestrates SAST audits, profile evaluation, and report generation."""

    def __init__(
        self,
        profile_path: str = "profile.json",
        rules_path: str = "rules/sast_rules.json",
    ):
        self.profile_path = self._resolve_path(profile_path)
        self.rules_path = self._resolve_path(rules_path)
        self.profile_loader = ProfileLoader()
        self.profile: dict[str, Any] = {}
        self._reload_profile()
        self.scanner = SASTScanner(
            profile_path=str(self.profile_path),
            rules_path=str(self.rules_path),
        )

    def _resolve_path(self, target_path: str) -> Path:
        """Resolve path, falling back to repository root if not found in CWD."""
        p = Path(target_path)
        if not p.exists():
            repo_root = Path(__file__).parents[2]
            alt = repo_root / target_path
            if alt.exists():
                return alt
        return p

    def _reload_profile(self) -> dict[str, Any]:
        """Reload profile configuration directly from disk."""
        self.profile = self.profile_loader.load(str(self.profile_path))
        return self.profile

    def run_audit(self, target_path: str) -> tuple[list[dict[str, Any]], str, str]:
        """Execute SAST audit on target path and return findings and report."""
        self._reload_profile()
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

        path = self._resolve_path("profile.json")
        if not path.exists():
            return False

        try:
            with open(path, encoding="utf-8") as f:
                data = json.load(f)

            data["audit_level"] = normalized

            with open(path, "w", encoding="utf-8") as f:
                json.dump(data, f, indent=2, ensure_ascii=False)
                f.write("\n")

            checksum_path = path.parent / ".profile.sha256"
            IntegrityChecker.update_signature(path, checksum_path)
            self._reload_profile()
            return True
        except (json.JSONDecodeError, OSError):
            return False

    def get_status(self) -> dict[str, Any]:
        """Return operational status of security guard with real-time disk state."""
        self._reload_profile()
        firewall = self.profile.get("command_firewall_overlay", {})

        sast_rules = self.scanner.get_rules(force_reload=True)

        checksum_path = self.profile_path.parent / ".profile.sha256"
        checksum_valid = False
        if checksum_path.exists():
            checksum_valid = IntegrityChecker.verify_integrity(
                self.profile_path, checksum_path
            )

        return {
            "project_id": self.profile.get("project_id", "unknown"),
            "stack": self.profile.get("stack", "unknown"),
            "mode": self.profile.get("mode", "strict"),
            "audit_level": self.profile.get("audit_level", "full"),
            "deny_count": len(firewall.get("deny", [])),
            "confirm_count": len(firewall.get("confirm", [])),
            "sast_rules_count": len(sast_rules),
            "checksum_valid": checksum_valid,
        }
