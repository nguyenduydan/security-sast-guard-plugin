"""Unit tests for AICache."""

from __future__ import annotations

from pathlib import Path

from src.domain.ai_cache import AICache


def test_ai_cache_hit_and_miss(tmp_path: Path) -> None:
    cache_file = tmp_path / "ai_cache.json"
    cache = AICache(cache_file=cache_file)

    key = cache.compute_key("API1:2023", "user_input = request.get()", "py")
    assert cache.get(key) is None

    cache.set(key, False)
    assert cache.get(key) is False


def test_ai_cache_persistence(tmp_path: Path) -> None:
    cache_file = tmp_path / "ai_cache.json"
    cache1 = AICache(cache_file=cache_file)
    key = cache1.compute_key("CWE-89", "query = f'SELECT * FROM users'", "py")
    cache1.set(key, True)

    cache2 = AICache(cache_file=cache_file)
    assert cache2.get(key) is True
