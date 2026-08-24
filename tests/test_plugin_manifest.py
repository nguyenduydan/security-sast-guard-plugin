"""Unit tests for plugin.json manifest and skill registration synchronization."""

import json
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[1]


def test_plugin_json_skills_sync() -> None:
    plugin_file = REPO_ROOT / "plugin.json"
    assert plugin_file.exists()

    data = json.loads(plugin_file.read_text(encoding="utf-8"))
    skills_in_manifest = set(data.get("skills", []))

    skills_dir = REPO_ROOT / "skills"
    skills_on_disk = {
        d.name
        for d in skills_dir.iterdir()
        if d.is_dir() and not d.name.startswith(".")
    }

    assert skills_in_manifest == skills_on_disk
    assert len(skills_in_manifest) == 8
