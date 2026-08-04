"""Profile loader infrastructure component."""

import json
from pathlib import Path
from typing import Any


class ProfileLoader:
    """Security profile loader implementation."""

    def load(self, path: str = "profile.json") -> dict[str, Any]:
        """Load security profile configuration from path."""
        file_path = Path(path)
        if not file_path.exists():
            return {}
        try:
            with open(file_path, encoding="utf-8") as f:
                data: dict[str, Any] = json.load(f)
                return data
        except (json.JSONDecodeError, OSError):
            return {}
