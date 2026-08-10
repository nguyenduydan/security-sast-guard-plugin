# Sprint 2: MCP Taint Tools — sast_get_dataflow_path + sast_get_taint_context + extend scan output

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Expose taint analysis results through 2 new MCP tools and extend `sast_scan_file`/`sast_scan_diff` to include a `taint_traces` field in their JSON output.

**Architecture:** Sprint 1 must be merged first. MCP schemas get 3 new Pydantic models (DataflowPathResult, TaintContextResult, TaintTraceItem). MCPToolHandlers gets 2 new handle_* methods. sast_scan_file and sast_scan_diff response dicts get a `taint_traces` key. MCP server.py registers 2 new tool names.

**Tech Stack:** Python 3.11+, existing MCP layer (`src/mcp/`), `src/domain/` taint pipeline from Sprint 1

## Global Constraints

- Sprint 1 complete and merged before starting this sprint
- Pylint 10.00/10.00, ruff clean before every commit
- Conventional commit scope: `feat(mcp):`
- No breaking changes to existing MCP tool response shapes — only additions
- All new MCP tools follow the same schema: return `{"status": "success", ...}` or `{"status": "error", "message": "..."}`

---

### Task 1: MCP Schemas — TaintTraceItem, DataflowPathResult, TaintContextResult

**Files:**
- Modify: `src/mcp/schemas.py`
- Test: Extend `tests/test_mcp_schemas.py` (create if missing)

**Interfaces:**
- Produces (as plain dataclasses — not Pydantic — matching existing schema style in schemas.py):
  - `TaintTraceItem(rule_id, source_file, source_line, sink_file, sink_line, trace_path, confidence)`
  - `DataflowPathResult(paths: list[dict], total: int)`
  - `TaintContextResult(file, line, code_snippet, taint_info: dict)`

- [ ] **Step 1: Read existing schemas.py**

View `src/mcp/schemas.py` to understand current schema style (dataclasses vs TypedDict vs raw dicts). Follow the exact same pattern.

- [ ] **Step 2: Write failing test**

```python
# tests/test_mcp_schemas.py
from src.mcp.schemas import TaintTraceItem, DataflowPathResult, TaintContextResult

def test_taint_trace_item_to_dict():
    item = TaintTraceItem(
        rule_id="RULE-001",
        source_file="app.py",
        source_line=10,
        sink_file="db.py",
        sink_line=55,
        trace_path=[{"file": "app.py", "line": 10, "symbol": "x", "step_type": "source_assignment"}],
        confidence=0.75,
    )
    d = item.to_dict()
    assert d["rule_id"] == "RULE-001"
    assert d["confidence"] == 0.75
    assert isinstance(d["trace_path"], list)

def test_dataflow_path_result():
    result = DataflowPathResult(paths=[{"source_file": "a.py"}], total=1)
    assert result.total == 1

def test_taint_context_result():
    result = TaintContextResult(
        file="app.py", line=10,
        code_snippet="user_input = request.GET.get('q')",
        taint_info={"is_source": True, "is_sink": False, "symbol": "user_input"},
    )
    assert result.file == "app.py"
    assert result.taint_info["is_source"] is True
```

- [ ] **Step 3: Run test to verify fails**

```
pytest tests/test_mcp_schemas.py -v
```
Expected: ImportError

- [ ] **Step 4: Add schemas to `src/mcp/schemas.py`**

Append to the end of `src/mcp/schemas.py`:

```python
# ── Taint Analysis Schemas ─────────────────────────────────────────────────

@dataclass
class TaintTraceItem:
    """Serializable taint flow finding for MCP output."""

    rule_id: str
    source_file: str
    source_line: int
    sink_file: str
    sink_line: int
    trace_path: list[dict]
    confidence: float

    def to_dict(self) -> dict:
        return {
            "rule_id": self.rule_id,
            "source_file": self.source_file,
            "source_line": self.source_line,
            "sink_file": self.sink_file,
            "sink_line": self.sink_line,
            "trace_path": self.trace_path,
            "confidence": self.confidence,
        }


@dataclass
class DataflowPathResult:
    """Result of sast_get_dataflow_path MCP tool."""

    paths: list[dict]
    total: int


@dataclass
class TaintContextResult:
    """Result of sast_get_taint_context MCP tool."""

    file: str
    line: int
    code_snippet: str
    taint_info: dict
```

Note: If existing schemas.py does not import `dataclass`, add `from dataclasses import dataclass` at the top.

- [ ] **Step 5: Run test**

```
pytest tests/test_mcp_schemas.py -v
```
Expected: 3 PASSED

- [ ] **Step 6: Commit**

```
git add src/mcp/schemas.py tests/test_mcp_schemas.py
git commit -m "feat(mcp): add TaintTraceItem, DataflowPathResult, TaintContextResult schemas"
```

---

### Task 2: `handle_sast_get_dataflow_path` — new MCP tool handler

**Files:**
- Modify: `src/mcp/tools.py`
- Create: `tests/test_mcp_taint_tools.py`

**Interfaces:**
- Consumes:
  - `AuditService.run_taint_analysis(repo_path)` from Sprint 1
  - `TaintFinding` from `src.domain.models`
  - `TaintTraceItem.to_dict()` from `src.mcp.schemas`
- Produces:
  - `MCPToolHandlers.handle_sast_get_dataflow_path(source_pattern: str, sink_pattern: str, repo_path: str = ".") -> dict`
  - Returns: `{"status": "success", "paths": [...], "total": N}`

- [ ] **Step 1: Write failing test**

```python
# tests/test_mcp_taint_tools.py
from unittest.mock import patch, MagicMock
from src.mcp.tools import MCPToolHandlers
from src.domain.models import TaintFinding, TraceStep

def _make_finding():
    step = TraceStep(file="app.py", line=10, symbol="x", step_type="source_assignment")
    return TaintFinding(
        rule_id="RULE-001",
        source_file="app.py", source_line=10, source_pattern="request.GET",
        sink_file="db.py", sink_line=55, sink_pattern="cursor.execute",
        trace_path=[step], confidence=0.75,
    )

def test_get_dataflow_path_returns_success_structure():
    handlers = MCPToolHandlers()
    with patch.object(handlers.audit_service, "run_taint_analysis", return_value=[_make_finding()]):
        result = handlers.handle_sast_get_dataflow_path("request.GET", "cursor.execute")
    assert result["status"] == "success"
    assert result["total"] == 1
    assert len(result["paths"]) == 1
    path = result["paths"][0]
    assert path["source_file"] == "app.py"
    assert path["sink_file"] == "db.py"
    assert path["confidence"] == 0.75

def test_get_dataflow_path_filters_by_source_and_sink():
    handlers = MCPToolHandlers()
    with patch.object(handlers.audit_service, "run_taint_analysis", return_value=[_make_finding()]):
        # filter for a sink that doesn't match
        result = handlers.handle_sast_get_dataflow_path("request.GET", "eval")
    assert result["total"] == 0
    assert result["paths"] == []

def test_get_dataflow_path_empty_findings():
    handlers = MCPToolHandlers()
    with patch.object(handlers.audit_service, "run_taint_analysis", return_value=[]):
        result = handlers.handle_sast_get_dataflow_path("request.GET", "eval")
    assert result["status"] == "success"
    assert result["total"] == 0
```

- [ ] **Step 2: Run test to verify fails**

```
pytest tests/test_mcp_taint_tools.py::test_get_dataflow_path_returns_success_structure -v
```
Expected: AttributeError — method not found

- [ ] **Step 3: Add handler to `src/mcp/tools.py`**

Add import at top of `tools.py`:
```python
from src.mcp.schemas import TaintTraceItem
```

Add method to `MCPToolHandlers` class:

```python
def handle_sast_get_dataflow_path(
    self,
    source_pattern: str,
    sink_pattern: str,
    repo_path: str = ".",
) -> dict:
    """Return all taint flow paths matching source_pattern → sink_pattern."""
    all_findings = self.audit_service.run_taint_analysis(repo_path)
    matched = [
        f for f in all_findings
        if source_pattern in f.source_pattern and sink_pattern in f.sink_pattern
    ]
    paths = [
        TaintTraceItem(
            rule_id=f.rule_id,
            source_file=f.source_file,
            source_line=f.source_line,
            sink_file=f.sink_file,
            sink_line=f.sink_line,
            trace_path=[
                {
                    "file": step.file,
                    "line": step.line,
                    "symbol": step.symbol,
                    "step_type": step.step_type,
                }
                for step in f.trace_path
            ],
            confidence=f.confidence,
        ).to_dict()
        for f in matched
    ]
    return {"status": "success", "paths": paths, "total": len(paths)}
```

- [ ] **Step 4: Run tests**

```
pytest tests/test_mcp_taint_tools.py -v
```
Expected: 3 PASSED

- [ ] **Step 5: Commit**

```
git add src/mcp/tools.py tests/test_mcp_taint_tools.py
git commit -m "feat(mcp): add handle_sast_get_dataflow_path MCP tool handler"
```

---

### Task 3: `handle_sast_get_taint_context` — new MCP tool handler

**Files:**
- Modify: `src/mcp/tools.py`
- Modify: `tests/test_mcp_taint_tools.py`

**Interfaces:**
- Produces:
  - `MCPToolHandlers.handle_sast_get_taint_context(file_path: str, line_number: int, context_lines: int = 10) -> dict`
  - Returns: `{"status": "success", "file": ..., "line": ..., "code_snippet": ..., "taint_info": {...}}`

- [ ] **Step 1: Write failing test**

Add to `tests/test_mcp_taint_tools.py`:

```python
import tempfile
from pathlib import Path

def test_get_taint_context_returns_code_snippet():
    with tempfile.TemporaryDirectory() as d:
        f = Path(d) / "app.py"
        f.write_text("line1\nuser_input = request.GET.get('q')\nline3\n", encoding="utf-8")
        handlers = MCPToolHandlers()
        with patch.object(handlers.audit_service, "run_taint_analysis", return_value=[_make_finding()]):
            result = handlers.handle_sast_get_taint_context(str(f), 2, context_lines=3)
    assert result["status"] == "success"
    assert "user_input" in result["code_snippet"]
    assert result["line"] == 2
    assert isinstance(result["taint_info"], dict)

def test_get_taint_context_file_not_found():
    handlers = MCPToolHandlers()
    result = handlers.handle_sast_get_taint_context("/nonexistent/file.py", 1)
    assert result["status"] == "error"
    assert "not found" in result["message"].lower()
```

- [ ] **Step 2: Run test to verify fails**

```
pytest tests/test_mcp_taint_tools.py::test_get_taint_context_returns_code_snippet -v
```
Expected: AttributeError

- [ ] **Step 3: Add handler to `src/mcp/tools.py`**

```python
def handle_sast_get_taint_context(
    self,
    file_path: str,
    line_number: int,
    context_lines: int = 10,
) -> dict:
    """Return code snippet and taint context around the given file:line."""
    path = Path(file_path)
    if not path.exists():
        return {"status": "error", "message": f"File not found: {file_path}"}
    try:
        lines = path.read_text(encoding="utf-8", errors="ignore").splitlines()
    except OSError as exc:
        return {"status": "error", "message": str(exc)}

    start = max(0, line_number - context_lines - 1)
    end = min(len(lines), line_number + context_lines)
    snippet = "\n".join(lines[start:end])

    # Cross-reference with taint findings to populate taint_info
    all_findings = self.audit_service.run_taint_analysis(str(path.parent))
    is_source = any(
        f.source_file in file_path and f.source_line == line_number
        for f in all_findings
    )
    is_sink = any(
        f.sink_file in file_path and f.sink_line == line_number
        for f in all_findings
    )
    flows_to = [
        f"{f.sink_file}:{f.sink_line}"
        for f in all_findings
        if f.source_file in file_path and f.source_line == line_number
    ]

    return {
        "status": "success",
        "file": file_path,
        "line": line_number,
        "code_snippet": snippet,
        "taint_info": {
            "is_source": is_source,
            "is_sink": is_sink,
            "flows_to": flows_to,
            "sanitized": False,  # Phase 2 (AST) will update this
        },
    }
```

- [ ] **Step 4: Run all taint tool tests**

```
pytest tests/test_mcp_taint_tools.py -v
```
Expected: 5 PASSED

- [ ] **Step 5: Commit**

```
git add src/mcp/tools.py tests/test_mcp_taint_tools.py
git commit -m "feat(mcp): add handle_sast_get_taint_context MCP tool handler"
```

---

### Task 4: Extend `sast_scan_file` and `sast_scan_diff` with `taint_traces`

**Files:**
- Modify: `src/mcp/tools.py` (update 2 existing handlers)
- Test: `tests/test_mcp_scan_taint_output.py` (Create)

- [ ] **Step 1: Write failing test**

```python
# tests/test_mcp_scan_taint_output.py
from unittest.mock import patch
from src.mcp.tools import MCPToolHandlers
from src.domain.models import TaintFinding, TraceStep

def _make_finding():
    step = TraceStep(file="app.py", line=10, symbol="x", step_type="source_assignment")
    return TaintFinding(
        rule_id="RULE-001",
        source_file="app.py", source_line=10, source_pattern="request.GET",
        sink_file="db.py", sink_line=55, sink_pattern="cursor.execute",
        trace_path=[step], confidence=0.75,
    )

def test_scan_file_includes_taint_traces():
    handlers = MCPToolHandlers()
    with patch.object(handlers.audit_service, "run_audit", return_value=([], "", "0 findings")):
        with patch.object(handlers.audit_service, "run_taint_analysis", return_value=[_make_finding()]):
            result = handlers.handle_sast_scan_file("app.py")
    assert "taint_traces" in result
    assert len(result["taint_traces"]) == 1
    assert result["taint_traces"][0]["rule_id"] == "RULE-001"

def test_scan_diff_includes_taint_traces():
    handlers = MCPToolHandlers()
    with patch.object(handlers.audit_service, "run_audit", return_value=([], "", "0 findings")):
        with patch.object(handlers.audit_service, "run_taint_analysis", return_value=[]):
            result = handlers.handle_sast_scan_diff()
    assert "taint_traces" in result
    assert result["taint_traces"] == []
```

- [ ] **Step 2: Run test to verify fails**

```
pytest tests/test_mcp_scan_taint_output.py -v
```
Expected: AssertionError — key not found

- [ ] **Step 3: Update `handle_sast_scan_file` in `src/mcp/tools.py`**

Replace current `handle_sast_scan_file` with:

```python
def handle_sast_scan_file(self, file_path: str) -> dict:
    """Scan a single file and include taint traces in output."""
    findings, report_file, summary = self.audit_service.run_audit(target_path=file_path)
    taint_findings = self.audit_service.run_taint_analysis(file_path)
    taint_traces = [
        {
            "rule_id": f.rule_id,
            "source_file": f.source_file,
            "source_line": f.source_line,
            "sink_file": f.sink_file,
            "sink_line": f.sink_line,
            "confidence": f.confidence,
            "trace_path": [
                {"file": s.file, "line": s.line, "symbol": s.symbol, "step_type": s.step_type}
                for s in f.trace_path
            ],
        }
        for f in taint_findings
    ]
    return {
        "status": "success",
        "report_file": str(report_file),
        "findings_count": len(findings),
        "summary": summary,
        "findings": [
            {
                "rule_id": f.get("rule_id", ""),
                "rule_name": f.get("rule_name", ""),
                "severity": f.get("severity", ""),
                "file_path": f.get("path", ""),
                "line_number": f.get("line", 0),
                "action": f.get("action", "Block"),
            }
            for f in findings
        ],
        "taint_traces": taint_traces,
    }
```

- [ ] **Step 4: Update `handle_sast_scan_diff` in `src/mcp/tools.py`**

Replace current `handle_sast_scan_diff` with:

```python
def handle_sast_scan_diff(self) -> dict:
    """Scan modified git files and include taint traces in output."""
    findings, report_file, summary = self.audit_service.run_audit(target_path=".")
    taint_findings = self.audit_service.run_taint_analysis(".")
    taint_traces = [
        {
            "rule_id": f.rule_id,
            "source_file": f.source_file,
            "source_line": f.source_line,
            "sink_file": f.sink_file,
            "sink_line": f.sink_line,
            "confidence": f.confidence,
            "trace_path": [
                {"file": s.file, "line": s.line, "symbol": s.symbol, "step_type": s.step_type}
                for s in f.trace_path
            ],
        }
        for f in taint_findings
    ]
    return {
        "status": "success",
        "report_file": str(report_file),
        "findings_count": len(findings),
        "summary": summary,
        "taint_traces": taint_traces,
    }
```

- [ ] **Step 5: Run all tests**

```
pytest -v
```
Expected: all PASSED

- [ ] **Step 6: Lint**

```
python -m pylint src/
python -m ruff check .
python -m ruff format --check .
```

- [ ] **Step 7: Commit**

```
git add src/mcp/tools.py tests/test_mcp_scan_taint_output.py
git commit -m "feat(mcp): extend sast_scan_file and sast_scan_diff with taint_traces output"
```

---

### Task 5: Register new tools in MCP server

**Files:**
- Modify: `src/mcp/server.py`
- Test: `tests/test_mcp_server_tools.py` (create)

- [ ] **Step 1: Read `src/mcp/server.py`**

View `src/mcp/server.py` to understand how existing tools are registered (likely a list of tool name → handler mappings).

- [ ] **Step 2: Write failing test**

```python
# tests/test_mcp_server_tools.py
from src.mcp.server import get_registered_tool_names  # adjust import to match actual function

def test_dataflow_path_tool_registered():
    names = get_registered_tool_names()
    assert "sast_get_dataflow_path" in names

def test_taint_context_tool_registered():
    names = get_registered_tool_names()
    assert "sast_get_taint_context" in names
```

Note: If `get_registered_tool_names()` does not exist, create it as a simple helper that returns the list of registered tool names from the tool registration dict.

- [ ] **Step 3: Register tools in `src/mcp/server.py`**

Following the existing pattern (e.g., `"sast_scan_file": handlers.handle_sast_scan_file`), add:

```python
"sast_get_dataflow_path": handlers.handle_sast_get_dataflow_path,
"sast_get_taint_context": handlers.handle_sast_get_taint_context,
```

- [ ] **Step 4: Run full test suite**

```
pytest -v
python -m pylint src/
python -m ruff check .
```

- [ ] **Step 5: Commit + push**

```
git add src/mcp/server.py tests/test_mcp_server_tools.py
git commit -m "feat(mcp): register sast_get_dataflow_path and sast_get_taint_context in MCP server"
git push origin feat/taint-analysis-sprint2
```
