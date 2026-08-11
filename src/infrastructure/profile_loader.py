"""Profile loader infrastructure component with optional integrity verification."""

import json
from pathlib import Path
from typing import Any

from src.domain.exceptions import SecurityIntegrityError
from src.infrastructure.integrity_checker import IntegrityChecker
from src.infrastructure.profile_resolver import ProfileResolver


class ProfileLoader:
    """Security profile loader implementation."""

    @staticmethod
    def _get_master_profile_path() -> Path:
        """Return absolute path to master profile.json in plugin root."""
        return Path(__file__).parents[2] / "profile.json"

    def load(
        self,
        path: str = "profile.json",
        verify_integrity: bool = False,
        checksum_path: str = ".profile.sha256",
    ) -> dict[str, Any]:
        """Load profile config, merging master rules with workspace overlay."""
        master_path = self._get_master_profile_path()
        master_data: dict[str, Any] = {}
        if master_path.exists():
            try:
                with open(master_path, encoding="utf-8") as f:
                    master_data = json.load(f)
            except (json.JSONDecodeError, OSError):
                master_data = {}

        target_path = Path(path)
        if path == "profile.json":
            target_path = ProfileResolver.resolve_profile_path()
        elif not target_path.exists():
            return {}

        if not target_path.exists():
            return master_data

        if verify_integrity and Path(checksum_path).exists():
            hash_path = Path(checksum_path)
            if not IntegrityChecker.verify_integrity(target_path, hash_path):
                raise SecurityIntegrityError(
                    f"Security profile integrity check failed for '{path}'."
                )

        try:
            with open(target_path, encoding="utf-8") as f:
                target_data: dict[str, Any] = json.load(f)
        except (json.JSONDecodeError, OSError):
            return master_data

        if target_path.resolve() == master_path.resolve():
            return target_data

        # Merge base profile.json with workspace overlay (.sast/profile.json)
        merged = dict(master_data)
        merged.update(target_data)

        base_overlay = master_data.get("command_firewall_overlay", {})
        target_overlay = target_data.get("command_firewall_overlay", {})

        merged_deny = list(
            dict.fromkeys(base_overlay.get("deny", []) + target_overlay.get("deny", []))
        )
        merged_confirm = list(
            dict.fromkeys(
                base_overlay.get("confirm", []) + target_overlay.get("confirm", [])
            )
        )

        merged["command_firewall_overlay"] = {
            "deny": merged_deny,
            "confirm": merged_confirm,
        }
        return merged
