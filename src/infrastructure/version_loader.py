"""Version loader component to retrieve plugin version without hardcoded fallbacks."""

from __future__ import annotations

import json
from pathlib import Path


def get_plugin_version() -> str:
    """Dynamically read version from plugin.json or pyproject.toml."""
    plugin_root = Path(__file__).resolve().parents[2]

    plugin_json = plugin_root / "plugin.json"
    if plugin_json.exists():
        try:
            with open(plugin_json, encoding="utf-8") as f:
                data = json.load(f)
                if data.get("version"):
                    return str(data["version"])
        except (json.JSONDecodeError, OSError):
            pass

    pyproject = plugin_root / "pyproject.toml"
    if pyproject.exists():
        try:
            for line in pyproject.read_text(encoding="utf-8").splitlines():
                if line.strip().startswith("version ="):
                    ver = line.split("=", 1)[1].strip().strip("\"'")
                    if ver:
                        return ver
        except OSError:
            pass

    raise RuntimeError(f"Could not resolve plugin version from {plugin_root}")
