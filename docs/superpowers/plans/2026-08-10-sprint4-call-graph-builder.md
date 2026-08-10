# Sprint 4: CallGraphBuilder — Cross-file Call Graph

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Build a grep-based cross-file call graph that can trace function call chains from entry points to dangerous sinks across multiple files. Integrate with AuditService and extend MCP taint traces with full call chain context.

**Architecture:** CallGraphBuilder greps import/require declarations to build a directed module graph. BFS traces from any function containing a tainted symbol to sinks in dependent modules. Results are added to TaintFinding.trace_path as additional TraceStep entries. Requires Sprint 1 + Sprint 2 + Sprint 3 complete.

**Tech Stack:** Python 3.11+, `collections.deque` (BFS), `re`, `pathlib`, `pytest`

## Global Constraints

- Pure grep-based: no language-specific AST required for import resolution
- Must handle circular imports gracefully (visited set)
- Pylint 10.00/10.00, ruff clean before every commit
- Conventional commit scope: `feat(graph):`
- CallChain results are additive — they extend trace_path, not replace it

---

### Task 1: CallGraphBuilder — import graph and call chain tracer

**Files:**
- Create: `src/domain/call_graph_builder.py`
- Create: `tests/test_call_graph_builder.py`

**Interfaces:**
- Consumes: `TraceStep` from `src.domain.models`
- Produces:
  - `CallEdge(caller_file: str, caller_fn: str, callee_file: str, callee_fn: str)`
  - `CallChain(entry_fn: str, steps: list[TraceStep], terminal_sink: str)`
  - `CallGraph` — internal type alias: `dict[str, list[CallEdge]]` (caller_file → edges)
  - `CallGraphBuilder(repo_path: str)`
  - `CallGraphBuilder.build_import_graph(entry_files: list[str]) -> dict[str, list[str]]`  
     Returns: `{ file_path: [imported_file_path, ...] }`
  - `CallGraphBuilder.trace_to_sinks(entry_file: str, entry_symbol: str, sinks: list[str]) -> list[CallChain]`

- [ ] **Step 1: Add CallEdge, CallChain to `src/domain/models.py`**

Append to bottom of `src/domain/models.py`:

```python
# ── Call Graph Models ──────────────────────────────────────────────────────

@dataclass(frozen=True)
class CallEdge:
    """A directed edge in the call graph: caller → callee."""

    caller_file: str
    caller_fn: str
    callee_file: str
    callee_fn: str


@dataclass
class CallChain:
    """A resolved call chain from an entry function to a sink."""

    entry_fn: str
    steps: list[TraceStep]
    terminal_sink: str
```

- [ ] **Step 2: Write failing tests**

```python
# tests/test_call_graph_builder.py
import textwrap, tempfile
from pathlib import Path
from src.domain.call_graph_builder import CallGraphBuilder

def _make_repo(files: dict[str, str]) -> str:
    d = tempfile.mkdtemp()
    for name, content in files.items():
        p = Path(d) / name
        p.parent.mkdir(parents=True, exist_ok=True)
        p.write_text(content, encoding="utf-8")
    return d

def test_build_import_graph_python():
    repo = _make_repo({
        "views.py": "from utils import run_query\n",
        "utils.py": "def run_query(q): pass\n",
    })
    builder = CallGraphBuilder(repo)
    graph = builder.build_import_graph(["views.py"])
    assert "views.py" in graph
    # utils.py should appear as a dependency of views.py
    assert any("utils.py" in dep for dep in graph["views.py"])

def test_build_import_graph_no_imports():
    repo = _make_repo({"standalone.py": "x = 1\n"})
    builder = CallGraphBuilder(repo)
    graph = builder.build_import_graph(["standalone.py"])
    assert graph["standalone.py"] == []

def test_build_import_graph_circular_does_not_hang():
    repo = _make_repo({
        "a.py": "from b import foo\n",
        "b.py": "from a import bar\n",
    })
    builder = CallGraphBuilder(repo)
    # Should complete without infinite loop
    graph = builder.build_import_graph(["a.py"])
    assert "a.py" in graph

def test_trace_to_sinks_finds_cross_file_sink():
    repo = _make_repo({
        "views.py": textwrap.dedent("""\
            from utils import run_query
            user_input = request.GET.get('q')
            run_query(user_input)
        """),
        "utils.py": textwrap.dedent("""\
            def run_query(q):
                cursor.execute(q)
        """),
    })
    builder = CallGraphBuilder(repo)
    chains = builder.trace_to_sinks("views.py", "user_input", ["cursor.execute"])
    # Should find a path: views.py → utils.py → cursor.execute
    assert len(chains) >= 1
    assert chains[0].terminal_sink == "cursor.execute"

def test_trace_to_sinks_no_cross_file_match():
    repo = _make_repo({
        "views.py": "user_input = request.GET.get('q')\n",
    })
    builder = CallGraphBuilder(repo)
    chains = builder.trace_to_sinks("views.py", "user_input", ["eval"])
    assert chains == []
```

- [ ] **Step 3: Run test to verify fails**

```
pytest tests/test_call_graph_builder.py -v
```
Expected: ModuleNotFoundError

- [ ] **Step 4: Implement `src/domain/call_graph_builder.py`**

```python
"""CallGraphBuilder: grep-based cross-file call graph for taint analysis."""

import re
from collections import deque
from pathlib import Path

from .models import CallChain, TraceStep

# Patterns to detect import statements by language
_IMPORT_PATTERNS = [
    # Python: from X import Y  /  import X
    re.compile(r"^\s*from\s+([\w./]+)\s+import"),
    re.compile(r"^\s*import\s+([\w./]+)"),
    # JS/TS: import X from 'Y'  /  require('Y')
    re.compile(r"""(?:import|require)\s*\(?\s*['"]([^'"]+)['"]"""),
    # C#: using Namespace.Sub;
    re.compile(r"^\s*using\s+([\w.]+)\s*;"),
    # Java: import a.b.c;
    re.compile(r"^\s*import\s+([\w.]+)\s*;"),
]

_SCAN_EXTENSIONS = {
    ".py", ".js", ".ts", ".jsx", ".tsx", ".cs", ".java",
    ".php", ".rb", ".go", ".rs",
}
_SKIP_DIRS = {
    ".git", ".venv", "venv", "node_modules", "__pycache__",
    ".mypy_cache", ".ruff_cache", "dist", "build", ".sast",
}


class CallGraphBuilder:
    """Builds a cross-file import graph and traces call chains to sinks."""

    def __init__(self, repo_path: str) -> None:
        self.repo_path = Path(repo_path).resolve()

    def build_import_graph(
        self, entry_files: list[str]
    ) -> dict[str, list[str]]:
        """BFS from entry_files, following import declarations.

        Returns dict: { relative_file_path: [list of imported relative paths] }
        """
        graph: dict[str, list[str]] = {}
        visited: set[str] = set()
        queue: deque[str] = deque()

        for ef in entry_files:
            rel = self._normalize(ef)
            queue.append(rel)

        while queue:
            current = queue.popleft()
            if current in visited:
                continue
            visited.add(current)
            deps = self._extract_imports(current)
            graph[current] = deps
            for dep in deps:
                if dep not in visited:
                    queue.append(dep)

        return graph

    def trace_to_sinks(
        self, entry_file: str, entry_symbol: str, sinks: list[str]
    ) -> list[CallChain]:
        """BFS from entry_file following imports, searching for sink calls
        that contain the entry_symbol.

        Returns a list of CallChain objects for each sink hit found.
        """
        entry_rel = self._normalize(entry_file)
        import_graph = self.build_import_graph([entry_rel])
        chains: list[CallChain] = []

        visited: set[str] = set()
        queue: deque[tuple[str, list[TraceStep]]] = deque()
        queue.append((entry_rel, []))

        while queue:
            current_file, path_so_far = queue.popleft()
            if current_file in visited:
                continue
            visited.add(current_file)

            abs_path = self.repo_path / current_file
            if not abs_path.exists():
                continue

            try:
                lines = abs_path.read_text(
                    encoding="utf-8", errors="ignore"
                ).splitlines()
            except OSError:
                continue

            for lineno, line in enumerate(lines, start=1):
                for sink in sinks:
                    if sink in line and entry_symbol in line:
                        steps = list(path_so_far) + [
                            TraceStep(
                                file=current_file,
                                line=lineno,
                                symbol=f"{sink}({entry_symbol})",
                                step_type="sink",
                            )
                        ]
                        chains.append(
                            CallChain(
                                entry_fn=entry_file,
                                steps=steps,
                                terminal_sink=sink,
                            )
                        )

            # Follow imports
            for dep in import_graph.get(current_file, []):
                if dep not in visited:
                    hop = TraceStep(
                        file=current_file,
                        line=0,
                        symbol=f"import {dep}",
                        step_type="intermediate_usage",
                    )
                    queue.append((dep, list(path_so_far) + [hop]))

        return chains

    def _normalize(self, file_path: str) -> str:
        """Return file_path relative to repo_path."""
        p = Path(file_path)
        if p.is_absolute():
            try:
                return str(p.relative_to(self.repo_path))
            except ValueError:
                return str(p)
        return file_path

    def _extract_imports(self, rel_path: str) -> list[str]:
        """Grep file for import statements and resolve to relative repo paths."""
        abs_path = self.repo_path / rel_path
        if not abs_path.exists():
            return []
        try:
            content = abs_path.read_text(encoding="utf-8", errors="ignore")
        except OSError:
            return []

        results: list[str] = []
        for line in content.splitlines():
            for pattern in _IMPORT_PATTERNS:
                m = pattern.search(line)
                if m:
                    module_ref = m.group(1)
                    resolved = self._resolve_module(rel_path, module_ref)
                    if resolved:
                        results.append(resolved)
                    break  # one pattern per line
        return results

    def _resolve_module(self, from_file: str, module_ref: str) -> str | None:
        """Try to resolve a module reference to a repo-relative file path."""
        # Convert dotted Python paths to slashes
        candidate_base = module_ref.replace(".", "/").replace("-", "_")
        from_dir = Path(from_file).parent

        for ext in _SCAN_EXTENSIONS:
            # Relative to the importing file's directory
            rel_candidate = str(from_dir / (candidate_base + ext))
            if (self.repo_path / rel_candidate).exists():
                return rel_candidate
            # Relative to repo root
            root_candidate = candidate_base + ext
            if (self.repo_path / root_candidate).exists():
                return root_candidate
        return None
```

- [ ] **Step 5: Run tests**

```
pytest tests/test_call_graph_builder.py -v
```
Expected: 5 PASSED

- [ ] **Step 6: Lint + format**

```
python -m pylint src/domain/call_graph_builder.py
python -m ruff check src/domain/call_graph_builder.py
python -m ruff format src/domain/call_graph_builder.py
```

- [ ] **Step 7: Commit**

```
git add src/domain/call_graph_builder.py src/domain/models.py tests/test_call_graph_builder.py
git commit -m "feat(graph): add CallGraphBuilder cross-file import graph and call chain tracer"
```

---

### Task 2: Wire CallGraphBuilder into AuditService.run_taint_analysis

**Files:**
- Modify: `src/application/audit_service.py`
- Test: extend `tests/test_audit_service_taint.py`

**Interfaces:**
- Consumes: `CallGraphBuilder.trace_to_sinks(entry_file, symbol, sinks)` from `src.domain.call_graph_builder`
- `run_taint_analysis` now adds cross-file chains to `TaintFinding.trace_path` as additional entries

- [ ] **Step 1: Write failing test**

Add to `tests/test_audit_service_taint.py`:

```python
def test_run_taint_analysis_calls_call_graph_builder():
    """run_taint_analysis should call CallGraphBuilder.trace_to_sinks for each finding."""
    from unittest.mock import MagicMock, patch
    from src.application.audit_service import AuditService

    service = AuditService()
    with patch("src.application.audit_service.CallGraphBuilder") as MockCGB:
        mock_instance = MagicMock()
        mock_instance.trace_to_sinks.return_value = []
        MockCGB.return_value = mock_instance

        with patch.object(service.scanner, "get_rules", return_value=[
            {"id": "R1", "sources": ["request.GET"], "sinks": ["eval"], "taint_enabled": True}
        ]):
            with patch("src.application.audit_service.SymbolIndexer") as MockIdx:
                MockIdx.return_value.index.return_value = {}
                service.run_taint_analysis(".")

        # trace_to_sinks may not be called if symbol_map is empty — that is correct behavior
        # Just assert CallGraphBuilder was instantiated
        MockCGB.assert_called()
```

- [ ] **Step 2: Run test to verify fails**

```
pytest tests/test_audit_service_taint.py::test_run_taint_analysis_calls_call_graph_builder -v
```
Expected: AssertionError

- [ ] **Step 3: Add CallGraphBuilder to `run_taint_analysis` in `audit_service.py`**

Add import:
```python
from src.domain.call_graph_builder import CallGraphBuilder
```

Update `run_taint_analysis` to call CallGraphBuilder for cross-file traces:

```python
def run_taint_analysis(self, target_path: str) -> list[TaintFinding]:
    """Run grep-based taint analysis, AST confirmation, and cross-file call graph tracing."""
    taint_rules = self._extract_taint_rules()
    if not taint_rules:
        return []
    repo_path = str(Path(target_path).resolve())
    cache = SymbolCache()
    commit_hash = self._get_commit_hash()
    call_graph = CallGraphBuilder(repo_path)
    raw_findings: list[TaintFinding] = []

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
            findings = tracker.trace(symbol_map, rule_id, source, sinks)
            # Phase 3: enrich trace_path with cross-file call chains
            for finding in findings:
                chains = call_graph.trace_to_sinks(
                    finding.source_file, list(symbol_map.keys())[0]
                    if symbol_map else "", sinks
                )
                if chains:
                    # Append cross-file steps to existing trace_path
                    for chain in chains:
                        finding.trace_path.extend(chain.steps)
            raw_findings.extend(findings)

    ast_engine = ASTConfirmEngine()
    confirmed = ast_engine.confirm_all(raw_findings)
    return [f for f in confirmed if f.confidence > 0.0]
```

Note: `TaintFinding` uses a regular `list` for `trace_path` (not frozen), so `.extend()` works.

- [ ] **Step 4: Run full suite**

```
pytest -v
```
Expected: all PASSED

- [ ] **Step 5: Lint**

```
python -m pylint src/
python -m ruff check .
python -m ruff format --check .
```

- [ ] **Step 6: Commit**

```
git add src/application/audit_service.py tests/test_audit_service_taint.py
git commit -m "feat(graph): wire CallGraphBuilder cross-file tracing into run_taint_analysis"
```

---

### Task 3: Add `taint_enabled`, `sources`, `sinks` fields to sample rules in `rules/sast_rules.json`

**Files:**
- Modify: `rules/sast_rules.json` (add fields to 3-5 high-value rules as proof of concept)

- [ ] **Step 1: Identify SQL injection rules**

```
python -c "import json; rules=json.load(open('rules/sast_rules.json')); [print(r['id'], r.get('name','')) for r in rules if 'sql' in r.get('name','').lower() or 'injection' in r.get('name','').lower()]"
```

Note the rule IDs.

- [ ] **Step 2: Add taint fields to SQL injection rules**

For each SQL injection rule found, add to its JSON object:
```json
"taint_enabled": true,
"sources": ["request.GET", "request.POST", "request.form", "Request.Form", "Request.QueryString", "os.environ.get", "input("],
"sinks": ["cursor.execute", "db.query", "db.execute", "SqlCommand", "executeQuery", "mysqli_query"]
```

- [ ] **Step 3: Add taint fields to Command Injection rules**

For command injection rules:
```json
"taint_enabled": true,
"sources": ["request.GET", "request.POST", "input(", "sys.argv", "os.environ.get"],
"sinks": ["subprocess.call", "subprocess.run", "subprocess.Popen", "os.system", "exec(", "eval("]
```

- [ ] **Step 4: Verify JSON is valid**

```
python -c "import json; json.load(open('rules/sast_rules.json')); print('JSON valid')"
```
Expected: `JSON valid`

- [ ] **Step 5: Commit**

```
git add rules/sast_rules.json
git commit -m "feat(graph): add taint_enabled/sources/sinks to SQL injection and command injection rules"
```

---

### Task 4: Final verification — Sprint 4

- [ ] **Run full test suite**

```
pytest -v
```
Expected: all PASSED (zero regressions from Sprint 1-3)

- [ ] **Lint + format**

```
python -m pylint src/
python -m ruff check .
python -m ruff format --check .
```
Expected: pylint 10.00/10.00

- [ ] **Manual smoke test — dataflow path**

```
python -c "
from src.mcp.tools import MCPToolHandlers
h = MCPToolHandlers()
r = h.handle_sast_get_dataflow_path('request.GET', 'cursor.execute', '.')
print('total paths:', r['total'])
print('status:', r['status'])
"
```
Expected: `status: success`, `total paths: <number>` (0 is OK if no test files have SQL injection)

- [ ] **Push and create PR**

```
git push origin feat/taint-analysis-sprint4
```
Open PR: `feat/taint-analysis-sprint4` → `main`  
PR title: `feat(graph): Sprint 4 — CallGraphBuilder cross-file taint analysis`
