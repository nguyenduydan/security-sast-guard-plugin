"""Profile loader infrastructure component with optional integrity verification."""

import json
from pathlib import Path
from typing import Any

from src.domain.exceptions import SecurityIntegrityError
from src.infrastructure.integrity_checker import IntegrityChecker
from src.infrastructure.profile_resolver import ProfileResolver


class ProfileLoader:
    """Security profile loader implementation."""

    def load(
        self,
        path: str = "profile.json",
        verify_integrity: bool = False,
        checksum_path: str = ".profile.sha256",
    ) -> dict[str, Any]:
        """Load security profile configuration from path."""
        file_path = Path(path)
        if path == "profile.json":
            file_path = ProfileResolver.resolve_profile_path()

        if not file_path.exists():
            return {}

        if verify_integrity and Path(checksum_path).exists():
            hash_path = Path(checksum_path)
            if not IntegrityChecker.verify_integrity(file_path, hash_path):
                raise SecurityIntegrityError(
                    f"Security profile integrity check failed for '{path}'."
                )

        try:
            with open(file_path, encoding="utf-8") as f:
                data: dict[str, Any] = json.load(f)
                return data
        except (json.JSONDecodeError, OSError):
            return {}
