"""Unit tests for ProfileResolver."""

from __future__ import annotations

from pathlib import Path

from src.infrastructure.profile_resolver import ProfileResolver


def test_profile_resolver_fallback(tmp_path: Path) -> None:
    res = ProfileResolver.resolve_profile_path(cwd=str(tmp_path))
    assert res.exists()
    assert res.name == "profile.json"


def test_profile_resolver_local_sast(tmp_path: Path) -> None:
    sast_dir = tmp_path / ".sast"
    sast_dir.mkdir()
    local_profile = sast_dir / "profile.json"
    local_profile.write_text('{"profile_name": "test"}', encoding="utf-8")

    res = ProfileResolver.resolve_profile_path(cwd=str(tmp_path))
    assert res == local_profile
