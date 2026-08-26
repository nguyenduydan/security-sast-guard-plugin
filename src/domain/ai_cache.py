"""SHA-256 Local Response Caching Layer for AI Verifier."""

from __future__ import annotations

import hashlib
import json
import os
import time
from pathlib import Path
from typing import Any


class AICache:
    """Hash-based cache for AI Verification results with 24h TTL."""

    def __init__(self, cache_file: Path | None = None) -> None:
        if cache_file is None:
            home_dir = Path(os.environ.get("USERPROFILE", os.path.expanduser("~")))
            sast_dir = home_dir / ".sast"
            sast_dir.mkdir(parents=True, exist_ok=True)
            self.cache_file = sast_dir / "ai_cache.json"
        else:
            self.cache_file = cache_file

        self.ttl = 86400  # 24 hours in seconds
        self._data: dict[str, dict[str, Any]] = self._load()

    def _load(self) -> dict[str, dict[str, Any]]:
        if not self.cache_file.exists():
            return {}
        try:
            with open(self.cache_file, encoding="utf-8") as f:
                data: dict[str, dict[str, Any]] = json.load(f)
                return data
        except (json.JSONDecodeError, OSError):
            return {}

    def _save(self) -> None:
        try:
            with open(self.cache_file, "w", encoding="utf-8") as f:
                json.dump(self._data, f, indent=2)
        except OSError:
            pass  # Cache write failure is non-fatal: continue without persisting

    @staticmethod
    def compute_key(rule_id: str, line_content: str, file_ext: str = "") -> str:
        """Compute deterministic SHA-256 cache key."""
        raw = f"{rule_id}:{line_content.strip()}:{file_ext}"
        return hashlib.sha256(raw.encode("utf-8")).hexdigest()

    def get(self, key: str) -> bool | None:
        """Get cached verification result (bool or None if miss/expired)."""
        entry = self._data.get(key)
        if not entry:
            return None

        timestamp = entry.get("timestamp", 0)
        if time.time() - timestamp > self.ttl:
            del self._data[key]
            self._save()
            return None

        result: bool = entry.get("is_valid_finding", True)
        return result

    def set(self, key: str, is_valid_finding: bool) -> None:
        """Set cached verification result."""
        self._data[key] = {
            "timestamp": time.time(),
            "is_valid_finding": is_valid_finding,
        }
        self._save()

    def get_advice(self, key: str) -> dict[str, Any] | None:
        """Get cached AI advisor advice payload (dict or None if miss/expired)."""
        entry = self._data.get(key)
        if not entry:
            return None

        timestamp = entry.get("timestamp", 0)
        if time.time() - timestamp > self.ttl:
            del self._data[key]
            self._save()
            return None

        advice: dict[str, Any] | None = entry.get("advice")
        return advice

    def set_advice(self, key: str, advice: dict[str, Any]) -> None:
        """Set cached AI advisor advice payload."""
        self._data[key] = {
            "timestamp": time.time(),
            "advice": advice,
            "is_valid_finding": not advice.get("is_likely_false_positive", False),
        }
        self._save()
