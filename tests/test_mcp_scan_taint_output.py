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


def test_scan_file_includes_taint_traces():
    handlers = MCPToolHandlers()
    with (
        patch.object(
            handlers.audit_service, "run_audit", return_value=([], "", "0 findings")
        ),
        patch.object(
            handlers.audit_service, "run_taint_analysis", return_value=[_make_finding()]
        ),
    ):
        result = handlers.handle_sast_scan_file("app.py")
    assert "taint_traces" in result
    assert len(result["taint_traces"]) == 1
    assert result["taint_traces"][0]["rule_id"] == "RULE-001"


def test_scan_diff_includes_taint_traces():
    handlers = MCPToolHandlers()
    with (
        patch.object(
            handlers.audit_service, "run_audit", return_value=([], "", "0 findings")
        ),
        patch.object(handlers.audit_service, "run_taint_analysis", return_value=[]),
    ):
        result = handlers.handle_sast_scan_diff()
    assert "taint_traces" in result
    assert result["taint_traces"] == []
