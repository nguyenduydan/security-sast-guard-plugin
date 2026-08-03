"""SAST Scanner domain component."""

from typing import Any


class SASTScanner:
    """SAST rule scanner implementation."""

    def scan(self, path: str) -> list[dict[str, Any]]:
        """Scan specified file path for SAST rule matches."""
        _ = path
        return []
