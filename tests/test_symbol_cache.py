# tests/test_symbol_cache.py
import tempfile
from pathlib import Path

from src.domain.models import SymbolMap
from src.infrastructure.symbol_cache import SymbolCache


def test_cache_miss_returns_none():
    with tempfile.TemporaryDirectory() as d:
        cache = SymbolCache(cache_dir=d)
        result = cache.get("/repo", ["request.GET"], "abc123")
        assert result is None


def test_set_then_get_returns_data():
    with tempfile.TemporaryDirectory() as d:
        cache = SymbolCache(cache_dir=d)
        data: SymbolMap = {"user_input": [("app.py", 10)]}
        cache.set("/repo", ["request.GET"], "abc123", data)
        result = cache.get("/repo", ["request.GET"], "abc123")
        assert result == data


def test_different_commit_hash_is_cache_miss():
    with tempfile.TemporaryDirectory() as d:
        cache = SymbolCache(cache_dir=d)
        data: SymbolMap = {"user_input": [("app.py", 10)]}
        cache.set("/repo", ["request.GET"], "abc123", data)
        result = cache.get("/repo", ["request.GET"], "def456")
        assert result is None


def test_cache_file_is_created():
    with tempfile.TemporaryDirectory() as d:
        cache = SymbolCache(cache_dir=d)
        cache.set("/repo", ["request.GET"], "abc123", {"x": [("a.py", 1)]})
        cache_file = Path(d) / "symbol_cache.json"
        assert cache_file.exists()


def test_make_key_is_stable():
    cache = SymbolCache()
    key1 = cache.make_key("/repo", ["a", "b"], "hash1")
    key2 = cache.make_key("/repo", ["b", "a"], "hash1")
    # order-independent (sorted sources)
    assert key1 == key2
