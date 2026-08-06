"""Tests for plugin structure, manifests, and version consistency."""

import json
from pathlib import Path

REPO_ROOT = Path(__file__).parent.parent


def test_plugin_json_schema_and_version() -> None:
    """Verify plugin.json exists, contains required fields, and matches extension manifest."""
    plugin_path = REPO_ROOT / "plugin.json"
    ext_path = REPO_ROOT / "gemini-extension.json"

    assert plugin_path.exists(), "plugin.json must exist"
    assert ext_path.exists(), "gemini-extension.json must exist"

    with open(plugin_path, encoding="utf-8") as f:
        plugin_data = json.load(f)
    with open(ext_path, encoding="utf-8") as f:
        ext_data = json.load(f)

    # Check required fields in plugin.json
    assert "name" in plugin_data
    assert "version" in plugin_data
    assert "main" in plugin_data
    assert "skills" in plugin_data
    assert len(plugin_data["skills"]) > 0

    # Verify version synchronization
    msg = (
        f"Version mismatch: {plugin_data['version']} vs {ext_data['version']}"
    )
    assert plugin_data["version"] == ext_data["version"], msg
