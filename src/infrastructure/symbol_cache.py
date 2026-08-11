"""TwoLevelCache for SymbolMap: LRU in-process + file-based persistence."""

import hashlib
import json
from collections import OrderedDict
from pathlib import Path
from typing import Any

try:
    from cachetools import LRUCache
except ImportError:

    class LRUCache(OrderedDict[str, Any]):  # type: ignore[no-redef]
        """Fallback LRU cache using OrderedDict if cachetools is not installed."""

        def __init__(self, maxsize: int = 64) -> None:
            super().__init__()
            self.maxsize = maxsize

        def __getitem__(self, key: Any) -> Any:
            val = super().__getitem__(key)
            self.move_to_end(key)
            return val

        def __setitem__(self, key: Any, value: Any) -> None:
            if key in self:
                self.move_to_end(key)
            super().__setitem__(key, value)
            if len(self) > self.maxsize:
                self.popitem(last=False)


from src.domain.models import SymbolMap

_LRU_MAX_SIZE = 64  # max number of distinct (repo, sources, commit) tuples in memory


class SymbolCache:
    """Two-level cache for SymbolIndexer results.

    Level 1: LRU in-process cache (lost on process exit).
    Level 2: JSON file at <cache_dir>/symbol_cache.json (persists between runs).
    """

    def __init__(self, cache_dir: str = ".sast") -> None:
        self._cache_dir = Path(cache_dir)
        self._cache_file = self._cache_dir / "symbol_cache.json"
        self._lru: LRUCache[str, SymbolMap] = LRUCache(maxsize=_LRU_MAX_SIZE)

    def make_key(self, repo_path: str, sources: list[str], commit_hash: str) -> str:
        """Create a stable, order-independent cache key."""
        raw = f"{repo_path}:{':'.join(sorted(sources))}:{commit_hash}"
        return hashlib.sha256(raw.encode()).hexdigest()

    def get(
        self, repo_path: str, sources: list[str], commit_hash: str
    ) -> SymbolMap | None:
        """Return cached SymbolMap or None on miss."""
        key = self.make_key(repo_path, sources, commit_hash)
        # Level 1: LRU
        if key in self._lru:
            cached: SymbolMap = self._lru[key]
            return cached
        # Level 2: file
        data = self._read_file_cache()
        if key in data:
            symbol_map = self._deserialize(data[key])
            self._lru[key] = symbol_map
            return symbol_map
        return None

    def set(
        self,
        repo_path: str,
        sources: list[str],
        commit_hash: str,
        symbol_map: SymbolMap,
    ) -> None:
        """Write symbol_map to both LRU and file cache."""
        key = self.make_key(repo_path, sources, commit_hash)
        self._lru[key] = symbol_map
        self._cache_dir.mkdir(parents=True, exist_ok=True)
        data = self._read_file_cache()
        data[key] = self._serialize(symbol_map)
        self._cache_file.write_text(
            json.dumps(data, ensure_ascii=False, indent=2), encoding="utf-8"
        )

    # ── serialization helpers ──────────────────────────────────────────────

    @staticmethod
    def _serialize(symbol_map: SymbolMap) -> Any:
        return {k: list(v) for k, v in symbol_map.items()}

    @staticmethod
    def _deserialize(raw: Any) -> SymbolMap:
        return {k: [tuple(pair) for pair in v] for k, v in raw.items()}

    def _read_file_cache(self) -> dict[str, Any]:
        if not self._cache_file.exists():
            return {}
        try:
            data: dict[str, Any] = json.loads(
                self._cache_file.read_text(encoding="utf-8")
            )
            return data
        except (json.JSONDecodeError, OSError):
            return {}
