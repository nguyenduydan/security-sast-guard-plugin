# Sprint 1: SymbolIndexer + TaintTracker + TwoLevelCache

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Xây dựng grep-based taint tracking engine bao gồm SymbolIndexer, TaintTracker, TwoLevelCache và 3 new domain models (TaintFinding, TraceStep, SymbolMap).

**Architecture:** SymbolIndexer grep toàn repo để tìm biến được gán từ source patterns. TaintTracker nhận SymbolMap đó và grep tiếp để tìm sink call sites. TwoLevelCache wraps SymbolIndexer với LRU in-process + file-based persistence keyed by git commit hash.

**Tech Stack:** Python 3.11+, `cachetools` (LRU), `subprocess` (git), `re`, `pathlib`, `dataclasses`, `pytest`

## Global Constraints

- Python >= 3.11 (StrEnum, `X | Y` union types, `list[T]` lowercase generics)
- Pylint score: 10.00/10.00 — zero warnings allowed before commit
- ruff check + ruff format: zero errors before commit
- TDD: write failing test → run → implement → run → commit
- Conventional commit scope: `feat(taint):`
- No hardcoded paths — all paths via `Path` from pathlib
- New domain models go in `src/domain/models.py` (extend existing file)
- Cache file lives at `.sast/symbol_cache.json` (relative to CWD)

---

### Task 1: Domain Models — TaintFinding, TraceStep, SymbolMap

**Files:**
- Modify: `src/domain/models.py`
- Test: `tests/test_taint_models.py` (Create)

**Interfaces:**
- Produces:
  - `TraceStep(file: str, line: int, symbol: str, step_type: str)`
  - `SymbolMap = dict[str, list[tuple[str, int]]]`  # symbol_name → [(file, line)]
  - `TaintFinding(rule_id, source_file, source_line, source_pattern, sink_file, sink_line, sink_pattern, trace_path: list[TraceStep], confidence: float)`

- [ ] **Step 1: Write failing test**

```python
# tests/test_taint_models.py
from src.domain.models import TaintFinding, TraceStep

def test_trace_step_fields():
    step = TraceStep(file="app.py", line=10, symbol="user_input", step_type="source_assignment")
    assert step.file == "app.py"
    assert step.line == 10
    assert step.symbol == "user_input"
    assert step.step_type == "source_assignment"

def test_taint_finding_fields():
    step = TraceStep(file="app.py", line=10, symbol="x", step_type="source_assignment")
    finding = TaintFinding(
        rule_id="RULE-001",
        source_file="app.py",
        source_line=10,
        source_pattern="request.GET",
        sink_file="db.py",
        sink_line=55,
        sink_pattern="cursor.execute",
        trace_path=[step],
        confidence=0.75,
    )
    assert finding.rule_id == "RULE-001"
    assert finding.confidence == 0.75
    assert len(finding.trace_path) == 1
```

- [ ] **Step 2: Run test to verify it fails**

```
pytest tests/test_taint_models.py -v
```
Expected: ImportError — `TraceStep`, `TaintFinding` not defined

- [ ] **Step 3: Add models to `src/domain/models.py`**

Append to bottom of existing `src/domain/models.py`:

```python
# ── Taint Analysis Models ──────────────────────────────────────────────────

# SymbolMap: symbol_name → list of (file_path, line_number) where it appears
SymbolMap = dict[str, list[tuple[str, int]]]


@dataclass(frozen=True)
class TraceStep:
    """One hop in a taint flow trace."""

    file: str
    line: int
    symbol: str
    step_type: str  # "source_assignment" | "intermediate_usage" | "sink"


@dataclass
class TaintFinding:
    """A confirmed source-to-sink taint flow."""

    rule_id: str
    source_file: str
    source_line: int
    source_pattern: str
    sink_file: str
    sink_line: int
    sink_pattern: str
    trace_path: list[TraceStep]
    confidence: float  # 0.0 – 1.0
```

- [ ] **Step 4: Run test to verify pass**

```
pytest tests/test_taint_models.py -v
```
Expected: 2 PASSED

- [ ] **Step 5: Commit**

```
git add src/domain/models.py tests/test_taint_models.py
git commit -m "feat(taint): add TaintFinding, TraceStep domain models and SymbolMap type alias"
```

---

### Task 2: SymbolIndexer — grep-based source assignment finder

**Files:**
- Create: `src/domain/symbol_indexer.py`
- Create: `tests/test_symbol_indexer.py`

**Interfaces:**
- Consumes: `SymbolMap` from `src.domain.models`
- Produces:
  - `SymbolIndexer(repo_path: str)`
  - `SymbolIndexer.index(sources: list[str]) -> SymbolMap`
  - `SymbolIndexer.extract_symbol_name(line: str, source: str) -> str | None`

- [ ] **Step 1: Write failing tests**

```python
# tests/test_symbol_indexer.py
import textwrap, tempfile, os
from pathlib import Path
from src.domain.symbol_indexer import SymbolIndexer

def _make_repo(files: dict[str, str]) -> str:
    """Create a temp directory with given files."""
    d = tempfile.mkdtemp()
    for name, content in files.items():
        p = Path(d) / name
        p.parent.mkdir(parents=True, exist_ok=True)
        p.write_text(content, encoding="utf-8")
    return d

def test_index_finds_simple_assignment():
    repo = _make_repo({
        "views.py": textwrap.dedent("""\
            user_input = request.GET.get('q')
            name = request.GET.get('name')
        """)
    })
    indexer = SymbolIndexer(repo)
    result = indexer.index(["request.GET"])
    assert "user_input" in result
    assert "name" in result
    assert result["user_input"][0] == ("views.py", 1)

def test_index_skips_non_assignment_lines():
    repo = _make_repo({
        "views.py": "print(request.GET.get('q'))\n"
    })
    indexer = SymbolIndexer(repo)
    result = indexer.index(["request.GET"])
    assert len(result) == 0

def test_extract_symbol_name_simple():
    indexer = SymbolIndexer(".")
    sym = indexer.extract_symbol_name("user_input = request.GET.get('q')", "request.GET")
    assert sym == "user_input"

def test_extract_symbol_name_no_match():
    indexer = SymbolIndexer(".")
    sym = indexer.extract_symbol_name("print(request.GET)", "request.GET")
    assert sym is None
```

- [ ] **Step 2: Run test to verify fails**

```
pytest tests/test_symbol_indexer.py -v
```
Expected: ModuleNotFoundError

- [ ] **Step 3: Implement `src/domain/symbol_indexer.py`**

```python
"""SymbolIndexer: grep-based source assignment finder."""

import re
from pathlib import Path

from .models import SymbolMap

# Matches: <identifier> = <anything containing source_keyword>
# Also matches: <identifier>: <type> = <...> (typed annotations)
_ASSIGN_RE = re.compile(
    r"^[ \t]*([a-zA-Z_]\w*)(?:\s*:\s*\S+)?\s*[:=]=?\s*.*?({SOURCE})"
)

# File extensions to scan (text-based code files)
_SCAN_EXTENSIONS = {
    ".py", ".js", ".ts", ".jsx", ".tsx", ".cs", ".java",
    ".php", ".rb", ".go", ".rs", ".cpp", ".c", ".h",
    ".vue", ".svelte", ".kt", ".swift",
}

# Directories to skip
_SKIP_DIRS = {
    ".git", ".venv", "venv", "node_modules", "__pycache__",
    ".mypy_cache", ".ruff_cache", "dist", "build", ".sast",
}


class SymbolIndexer:
    """Scans a repository to find variable assignments from taint sources."""

    def __init__(self, repo_path: str) -> None:
        self.repo_path = Path(repo_path).resolve()

    def index(self, sources: list[str]) -> SymbolMap:
        """Grep repo files for assignments from any of the source patterns.

        Returns SymbolMap: { symbol_name: [(relative_file_path, line_number)] }
        """
        result: SymbolMap = {}
        for file_path in self._iter_code_files():
            rel = str(file_path.relative_to(self.repo_path))
            try:
                lines = file_path.read_text(encoding="utf-8", errors="ignore").splitlines()
            except OSError:
                continue
            for lineno, line in enumerate(lines, start=1):
                for source in sources:
                    if source not in line:
                        continue
                    symbol = self.extract_symbol_name(line, source)
                    if symbol:
                        result.setdefault(symbol, []).append((rel, lineno))
        return result

    def extract_symbol_name(self, line: str, source: str) -> str | None:
        """Return the LHS variable name if line is a simple assignment from source."""
        escaped = re.escape(source)
        pattern = re.compile(
            r"^[ \t]*([a-zA-Z_]\w*)(?:\s*:\s*\S+)?\s*=\s*.*?" + escaped
        )
        m = pattern.match(line)
        if m:
            return m.group(1)
        return None

    def _iter_code_files(self):
        """Yield Path objects for all code files in repo, skipping ignored dirs."""
        for path in self.repo_path.rglob("*"):
            if path.is_file() and path.suffix in _SCAN_EXTENSIONS:
                if not any(part in _SKIP_DIRS for part in path.parts):
                    yield path
```

- [ ] **Step 4: Run tests to verify pass**

```
pytest tests/test_symbol_indexer.py -v
```
Expected: 4 PASSED

- [ ] **Step 5: Lint + format check**

```
python -m pylint src/domain/symbol_indexer.py
python -m ruff check src/domain/symbol_indexer.py
python -m ruff format src/domain/symbol_indexer.py
```
Expected: pylint 10.00/10.00, ruff 0 errors

- [ ] **Step 6: Commit**

```
git add src/domain/symbol_indexer.py tests/test_symbol_indexer.py
git commit -m "feat(taint): add SymbolIndexer grep-based source assignment finder"
```

---

### Task 3: TaintTracker — source-to-sink flow tracker

**Files:**
- Create: `src/domain/taint_tracker.py`
- Create: `tests/test_taint_tracker.py`

**Interfaces:**
- Consumes:
  - `SymbolMap` from `src.domain.models`
  - `TaintFinding`, `TraceStep` from `src.domain.models`
- Produces:
  - `TaintTracker(repo_path: str)`
  - `TaintTracker.trace(symbol_map: SymbolMap, rule_id: str, source_pattern: str, sinks: list[str]) -> list[TaintFinding]`

- [ ] **Step 1: Write failing tests**

```python
# tests/test_taint_tracker.py
import textwrap, tempfile
from pathlib import Path
from src.domain.taint_tracker import TaintTracker
from src.domain.models import SymbolMap

def _make_repo(files: dict[str, str]) -> str:
    d = tempfile.mkdtemp()
    for name, content in files.items():
        p = Path(d) / name
        p.parent.mkdir(parents=True, exist_ok=True)
        p.write_text(content, encoding="utf-8")
    return d

def test_trace_finds_sink_usage():
    repo = _make_repo({
        "views.py": textwrap.dedent("""\
            user_input = request.GET.get('q')
            cursor.execute(user_input)
        """)
    })
    symbol_map: SymbolMap = {"user_input": [("views.py", 1)]}
    tracker = TaintTracker(repo)
    findings = tracker.trace(
        symbol_map=symbol_map,
        rule_id="RULE-001",
        source_pattern="request.GET",
        sinks=["cursor.execute"],
    )
    assert len(findings) == 1
    f = findings[0]
    assert f.rule_id == "RULE-001"
    assert f.source_file == "views.py"
    assert f.sink_file == "views.py"
    assert f.sink_line == 2
    assert f.sink_pattern == "cursor.execute"
    assert 0.0 <= f.confidence <= 1.0
    assert len(f.trace_path) >= 2

def test_trace_no_sink_returns_empty():
    repo = _make_repo({"views.py": "user_input = request.GET.get('q')\n"})
    symbol_map: SymbolMap = {"user_input": [("views.py", 1)]}
    tracker = TaintTracker(repo)
    findings = tracker.trace(symbol_map, "RULE-001", "request.GET", ["eval"])
    assert findings == []

def test_trace_skips_symbol_not_in_sink_line():
    repo = _make_repo({
        "views.py": textwrap.dedent("""\
            user_input = request.GET.get('q')
            cursor.execute("SELECT 1")
        """)
    })
    symbol_map: SymbolMap = {"user_input": [("views.py", 1)]}
    tracker = TaintTracker(repo)
    findings = tracker.trace(symbol_map, "RULE-001", "request.GET", ["cursor.execute"])
    # sink line exists but doesn't contain the tainted symbol
    assert findings == []
```

- [ ] **Step 2: Run test to verify fails**

```
pytest tests/test_taint_tracker.py -v
```
Expected: ModuleNotFoundError

- [ ] **Step 3: Implement `src/domain/taint_tracker.py`**

```python
"""TaintTracker: traces tainted symbols from source assignments to sink call sites."""

from pathlib import Path

from .models import SymbolMap, TaintFinding, TraceStep

_SCAN_EXTENSIONS = {
    ".py", ".js", ".ts", ".jsx", ".tsx", ".cs", ".java",
    ".php", ".rb", ".go", ".rs", ".cpp", ".c", ".h",
    ".vue", ".svelte", ".kt", ".swift",
}
_SKIP_DIRS = {
    ".git", ".venv", "venv", "node_modules", "__pycache__",
    ".mypy_cache", ".ruff_cache", "dist", "build", ".sast",
}


class TaintTracker:
    """Traces tainted symbols from SymbolMap to sink call sites in the repo."""

    def __init__(self, repo_path: str) -> None:
        self.repo_path = Path(repo_path).resolve()

    def trace(
        self,
        symbol_map: SymbolMap,
        rule_id: str,
        source_pattern: str,
        sinks: list[str],
    ) -> list[TaintFinding]:
        """For each symbol in symbol_map, grep repo for sink usage lines.

        A match requires BOTH the sink keyword AND the tainted symbol to appear
        in the same line (simple heuristic — no scope analysis at this phase).
        """
        findings: list[TaintFinding] = []
        for symbol, source_locs in symbol_map.items():
            for source_file, source_line in source_locs:
                sink_hits = self._find_sink_hits(symbol, sinks)
                for sink_file, sink_line, sink_pattern in sink_hits:
                    trace = [
                        TraceStep(
                            file=source_file,
                            line=source_line,
                            symbol=symbol,
                            step_type="source_assignment",
                        ),
                        TraceStep(
                            file=sink_file,
                            line=sink_line,
                            symbol=f"{sink_pattern}({symbol})",
                            step_type="sink",
                        ),
                    ]
                    findings.append(
                        TaintFinding(
                            rule_id=rule_id,
                            source_file=source_file,
                            source_line=source_line,
                            source_pattern=source_pattern,
                            sink_file=sink_file,
                            sink_line=sink_line,
                            sink_pattern=sink_pattern,
                            trace_path=trace,
                            confidence=0.5,  # Phase 1 baseline; Phase 2 may update
                        )
                    )
        return findings

    def _find_sink_hits(
        self, symbol: str, sinks: list[str]
    ) -> list[tuple[str, int, str]]:
        """Search all code files for lines containing BOTH a sink and the symbol."""
        hits: list[tuple[str, int, str]] = []
        for file_path in self._iter_code_files():
            rel = str(file_path.relative_to(self.repo_path))
            try:
                lines = file_path.read_text(
                    encoding="utf-8", errors="ignore"
                ).splitlines()
            except OSError:
                continue
            for lineno, line in enumerate(lines, start=1):
                for sink in sinks:
                    if sink in line and symbol in line:
                        hits.append((rel, lineno, sink))
        return hits

    def _iter_code_files(self):
        for path in self.repo_path.rglob("*"):
            if path.is_file() and path.suffix in _SCAN_EXTENSIONS:
                if not any(part in _SKIP_DIRS for part in path.parts):
                    yield path
```

- [ ] **Step 4: Run tests**

```
pytest tests/test_taint_tracker.py -v
```
Expected: 3 PASSED

- [ ] **Step 5: Lint + format**

```
python -m pylint src/domain/taint_tracker.py
python -m ruff check src/domain/taint_tracker.py
python -m ruff format src/domain/taint_tracker.py
```

- [ ] **Step 6: Commit**

```
git add src/domain/taint_tracker.py tests/test_taint_tracker.py
git commit -m "feat(taint): add TaintTracker source-to-sink taint flow tracker"
```

---

### Task 4: TwoLevelCache — LRU in-process + file-based persistence

**Files:**
- Create: `src/infrastructure/symbol_cache.py`
- Create: `tests/test_symbol_cache.py`
- Modify: `pyproject.toml` — add `cachetools` to dependencies

**Interfaces:**
- Consumes: `SymbolMap` from `src.domain.models`
- Produces:
  - `SymbolCache(cache_dir: str = ".sast")`
  - `SymbolCache.get(repo_path: str, sources: list[str], commit_hash: str) -> SymbolMap | None`
  - `SymbolCache.set(repo_path: str, sources: list[str], commit_hash: str, symbol_map: SymbolMap) -> None`
  - `SymbolCache.make_key(repo_path: str, sources: list[str], commit_hash: str) -> str`

- [ ] **Step 1: Add `cachetools` to pyproject.toml**

In `pyproject.toml`, find the `[project]` dependencies list and add:
```toml
"cachetools>=5.0",
```

- [ ] **Step 2: Write failing tests**

```python
# tests/test_symbol_cache.py
import tempfile, json
from pathlib import Path
from src.infrastructure.symbol_cache import SymbolCache
from src.domain.models import SymbolMap

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
```

- [ ] **Step 3: Run test to verify fails**

```
pytest tests/test_symbol_cache.py -v
```
Expected: ModuleNotFoundError

- [ ] **Step 4: Implement `src/infrastructure/symbol_cache.py`**

```python
"""TwoLevelCache for SymbolMap: LRU in-process + file-based persistence."""

import hashlib
import json
from pathlib import Path
from typing import Any

from cachetools import LRUCache

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
            return self._lru[key]
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
            return json.loads(self._cache_file.read_text(encoding="utf-8"))
        except (json.JSONDecodeError, OSError):
            return {}
```

- [ ] **Step 5: Run tests**

```
pytest tests/test_symbol_cache.py -v
```
Expected: 5 PASSED

- [ ] **Step 6: Full suite + lint**

```
pytest -v
python -m pylint src/infrastructure/symbol_cache.py
python -m ruff check .
python -m ruff format --check .
```
Expected: all PASSED, pylint 10.00/10.00

- [ ] **Step 7: Commit**

```
git add src/infrastructure/symbol_cache.py tests/test_symbol_cache.py pyproject.toml
git commit -m "feat(taint): add TwoLevelCache (LRU + file-based) for SymbolIndexer results"
```

---

### Task 5: Wire taint pipeline into AuditService

**Files:**
- Modify: `src/application/audit_service.py`
- Test: Extend `tests/test_audit_service.py` (if not exists, create)

**Interfaces:**
- Consumes:
  - `SymbolIndexer(repo_path)` from `src.domain.symbol_indexer`
  - `TaintTracker(repo_path)` from `src.domain.taint_tracker`
  - `SymbolCache()` from `src.infrastructure.symbol_cache`
  - `TaintFinding` from `src.domain.models`
- Produces:
  - `AuditService.run_taint_analysis(target_path: str) -> list[TaintFinding]`
  - `AuditService.run_audit()` extended return to include `taint_traces: list[TaintFinding]`

- [ ] **Step 1: Write failing test**

```python
# tests/test_audit_service_taint.py
import tempfile, textwrap
from pathlib import Path
from unittest.mock import patch
from src.application.audit_service import AuditService

def test_run_taint_analysis_returns_list():
    """run_taint_analysis should return a list (possibly empty) for any path."""
    service = AuditService()
    result = service.run_taint_analysis(".")
    assert isinstance(result, list)
```

- [ ] **Step 2: Run test to verify fails**

```
pytest tests/test_audit_service_taint.py -v
```
Expected: AttributeError — `run_taint_analysis` not defined

- [ ] **Step 3: Add `_extract_taint_rules` and `run_taint_analysis` to `AuditService`**

Add the following imports at the top of `src/application/audit_service.py`:
```python
import subprocess
from src.domain.symbol_indexer import SymbolIndexer
from src.domain.taint_tracker import TaintTracker
from src.domain.models import TaintFinding
from src.infrastructure.symbol_cache import SymbolCache
```

Add these methods inside the `AuditService` class (after `run_audit`):

```python
def _get_commit_hash(self) -> str:
    """Return current HEAD commit hash, or 'no-git' if not in a git repo."""
    try:
        result = subprocess.run(
            ["git", "rev-parse", "HEAD"],
            capture_output=True, text=True, timeout=5, check=False,
        )
        return result.stdout.strip() or "no-git"
    except (OSError, subprocess.TimeoutExpired):
        return "no-git"

def _extract_taint_rules(self) -> list[dict]:
    """Extract rules with taint_enabled=True from sast_rules.json."""
    all_rules = self.scanner.get_rules()
    return [r for r in all_rules if r.get("taint_enabled")]

def run_taint_analysis(self, target_path: str) -> list[TaintFinding]:
    """Run grep-based taint analysis for all taint-enabled rules."""
    taint_rules = self._extract_taint_rules()
    if not taint_rules:
        return []
    repo_path = str(Path(target_path).resolve())
    cache = SymbolCache()
    commit_hash = self._get_commit_hash()
    findings: list[TaintFinding] = []
    for rule in taint_rules:
        sources = rule.get("sources", [])
        sinks = rule.get("sinks", [])
        rule_id = rule.get("id", "UNKNOWN")
        if not sources or not sinks:
            continue
        for source in sources:
            cached = cache.get(repo_path, [source], commit_hash)
            if cached is not None:
                symbol_map = cached
            else:
                indexer = SymbolIndexer(repo_path)
                symbol_map = indexer.index([source])
                cache.set(repo_path, [source], commit_hash, symbol_map)
            tracker = TaintTracker(repo_path)
            findings.extend(tracker.trace(symbol_map, rule_id, source, sinks))
    return findings
```

- [ ] **Step 4: Run full test suite**

```
pytest -v
```
Expected: all PASSED

- [ ] **Step 5: Lint**

```
python -m pylint src/application/audit_service.py
python -m ruff check .
python -m ruff format --check .
```

- [ ] **Step 6: Commit**

```
git add src/application/audit_service.py tests/test_audit_service_taint.py
git commit -m "feat(taint): wire SymbolIndexer+TaintTracker into AuditService.run_taint_analysis"
```

---

### Task 6: Final verification — Sprint 1

- [ ] **Run full test suite**

```
pytest -v
```
Expected: all PASSED (no regressions)

- [ ] **Lint + format**

```
python -m pylint src/
python -m ruff check .
python -m ruff format --check .
```
Expected: pylint 10.00/10.00, ruff 0 errors

- [ ] **Push and create PR**

```
git push origin feat/taint-analysis-sprint1
```
Then open PR: `feat/taint-analysis-sprint1` → `main`
PR title: `feat(taint): Sprint 1 — SymbolIndexer, TaintTracker, TwoLevelCache`
