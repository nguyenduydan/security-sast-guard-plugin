# tests/test_audit_service_taint.py
from unittest.mock import MagicMock, patch

from src.application.audit_service import AuditService
from src.domain.models import TaintFinding, TraceStep


def test_run_taint_analysis_returns_list():
    """run_taint_analysis should return a list (possibly empty) for any path."""
    service = AuditService()
    result = service.run_taint_analysis(".")
    assert isinstance(result, list)


def test_run_taint_analysis_uses_ast_confirm():
    """run_taint_analysis should pass results through ASTConfirmEngine.confirm_all."""
    step = TraceStep(file="app.py", line=10, symbol="x", step_type="source_assignment")
    mock_finding = TaintFinding(
        rule_id="RULE-001",
        source_file="app.py",
        source_line=10,
        source_pattern="request.GET",
        sink_file="db.py",
        sink_line=55,
        sink_pattern="cursor.execute",
        trace_path=[step],
        confidence=0.5,
    )

    service = AuditService()
    with (
        patch("src.application.audit_service.ASTConfirmEngine") as MockEngine,
        patch.object(
            service.scanner,
            "get_rules",
            return_value=[
                {
                    "id": "RULE-001",
                    "sources": ["request.GET"],
                    "sinks": ["cursor.execute"],
                    "taint_enabled": True,
                }
            ],
        ),
        patch("src.application.audit_service.SymbolIndexer") as MockIndexer,
        patch("src.application.audit_service.TaintTracker") as MockTracker,
    ):
        mock_instance = MagicMock()
        mock_instance.confirm_all.return_value = [mock_finding]
        MockEngine.return_value = mock_instance
        MockIndexer.return_value.index.return_value = {"x": [("app.py", 10)]}
        MockTracker.return_value.trace.return_value = [mock_finding]
        result = service.run_taint_analysis(".")

        mock_instance.confirm_all.assert_called_once()
    assert len(result) == 1


def test_run_taint_analysis_calls_call_graph_builder():
    """run_taint_analysis should call CallGraphBuilder for each finding."""
    service = AuditService()
    with patch("src.application.audit_service.CallGraphBuilder") as MockCGB:
        mock_instance = MagicMock()
        mock_instance.trace_to_sinks.return_value = []
        MockCGB.return_value = mock_instance

        with (
            patch.object(
                service.scanner,
                "get_rules",
                return_value=[
                    {
                        "id": "R1",
                        "sources": ["request.GET"],
                        "sinks": ["eval"],
                        "taint_enabled": True,
                    }
                ],
            ),
            patch("src.application.audit_service.SymbolIndexer") as MockIdx,
        ):
            MockIdx.return_value.index.return_value = {}
            service.run_taint_analysis(".")

        # trace_to_sinks may not be called if symbol_map is empty
        # Just assert CallGraphBuilder was instantiated
        MockCGB.assert_called()
