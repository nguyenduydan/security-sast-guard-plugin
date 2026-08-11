import tempfile
from pathlib import Path
from unittest.mock import patch

from src.domain.models import TaintFinding, TraceStep
from src.mcp.tools import MCPToolHandlers


def _make_finding():
    step = TraceStep(file="app.py", line=10, symbol="x", step_type="source_assignment")
    return TaintFinding(
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


def test_get_dataflow_path_returns_success_structure():
    handlers = MCPToolHandlers()
    with patch.object(
        handlers.audit_service, "run_taint_analysis", return_value=[_make_finding()]
    ):
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
    with patch.object(
        handlers.audit_service, "run_taint_analysis", return_value=[_make_finding()]
    ):
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


def test_get_taint_context_returns_code_snippet():
    with tempfile.TemporaryDirectory() as d:
        f = Path(d) / "app.py"
        f.write_text(
            "line1\nuser_input = request.GET.get('q')\nline3\n", encoding="utf-8"
        )
        handlers = MCPToolHandlers()
        with patch.object(
            handlers.audit_service, "run_taint_analysis", return_value=[_make_finding()]
        ):
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
