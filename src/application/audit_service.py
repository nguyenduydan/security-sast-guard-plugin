import json
from pathlib import Path
from typing import Any

from src.domain.sast_scanner import SASTScanner
from src.infrastructure.integrity_checker import IntegrityChecker
from src.infrastructure.profile_loader import ProfileLoader
from src.infrastructure.profile_resolver import ProfileResolver
from src.infrastructure.report_generator import generate_markdown_report


from src.infrastructure.version_loader import get_plugin_version


class AuditService:
    """Orchestrates SAST audits, profile evaluation, and report generation."""

    def __init__(
        self,
        profile_path: str = "profile.json",
        rules_path: str = "rules/sast_rules.json",
    ):
        if profile_path == "profile.json":
            self.profile_path = ProfileResolver.resolve_profile_path()
        else:
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
        self.profile_path = ProfileResolver.resolve_profile_path()
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

        path = ProfileResolver.resolve_profile_path()
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
            if checksum_path.exists():
                IntegrityChecker.update_signature(path, checksum_path)
            self._reload_profile()
            return True
        except (json.JSONDecodeError, OSError):
            return False

    def set_mode(self, mode: str) -> bool:
        """Set active operation mode (strict | draft) in profile configuration."""
        valid_modes = ("strict", "draft")
        normalized = mode.lower().strip()
        if normalized not in valid_modes:
            return False

        path = ProfileResolver.resolve_profile_path()
        if not path.exists():
            return False

        try:
            with open(path, encoding="utf-8") as f:
                data = json.load(f)

            data["mode"] = normalized

            with open(path, "w", encoding="utf-8") as f:
                json.dump(data, f, indent=2, ensure_ascii=False)
                f.write("\n")

            checksum_path = path.parent / ".profile.sha256"
            if checksum_path.exists():
                IntegrityChecker.update_signature(path, checksum_path)
            self._reload_profile()
            return True
        except (json.JSONDecodeError, OSError):
            return False

    def _resolve_project_id(self) -> str:
        """Resolve project_id from profile, manifest file, or workspace directory name."""
        pid = str(self.profile.get("project_id", "")).strip()
        ignored_placeholders = ("project_local", "unknown", "auto", "")
        if pid and pid.lower() not in ignored_placeholders:
            return pid

        cwd = Path.cwd()
        pyproject = cwd / "pyproject.toml"
        if pyproject.exists():
            try:
                for line in pyproject.read_text(encoding="utf-8").splitlines():
                    if line.strip().startswith("name ="):
                        found_name = line.split("=", 1)[1].strip().strip('"\'')
                        if found_name:
                            return found_name
            except (OSError, ValueError, KeyError):
                pass

        pkg_json = cwd / "package.json"
        if pkg_json.exists():
            try:
                data = json.loads(pkg_json.read_text(encoding="utf-8"))
                if data.get("name"):
                    return str(data["name"])
            except (OSError, ValueError, KeyError):
                pass

        return cwd.name

    def _resolve_stack(self) -> str:
        """Auto-detect project tech stack if not explicitly set in profile."""
        if self.profile.get("stack"):
            return str(self.profile["stack"])
        cwd = Path.cwd()
        is_python = (
            (cwd / "pyproject.toml").exists()
            or (cwd / "requirements.txt").exists()
            or (cwd / "setup.py").exists()
        )
        if is_python:
            return "python"
        if (cwd / "package.json").exists():
            return "node"
        if (cwd / "pom.xml").exists() or (cwd / "build.gradle").exists():
            return "java"

        if (cwd / "go.mod").exists():
            return "go"
        return "general"

    def _resolve_version(self) -> str:
        """Resolve plugin version dynamically from version loader."""
        return get_plugin_version()



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
            "version": self._resolve_version(),
            "project_id": self._resolve_project_id(),
            "stack": self._resolve_stack(),
            "mode": self.profile.get("mode", "strict"),
            "audit_level": self.profile.get("audit_level", "full"),
            "deny_count": len(firewall.get("deny", [])),
            "confirm_count": len(firewall.get("confirm", [])),
            "sast_rules_count": len(sast_rules),
            "checksum_valid": checksum_valid,
        }
