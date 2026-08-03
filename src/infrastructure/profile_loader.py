"""Profile loader infrastructure component."""

from typing import Any


class ProfileLoader:
    """Security profile loader implementation."""

    def load(self, path: str) -> dict[str, Any]:
        """Load security profile configuration from path."""
        _ = path
        return {}
