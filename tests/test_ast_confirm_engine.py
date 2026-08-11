# tests/test_ast_confirm_engine.py
from unittest.mock import patch

from src.domain.ast_confirm_engine import ASTConfirmEngine, ConfirmResult
from src.domain.models import TaintFinding, TraceStep


def _make_finding(source_file="app.py", sink_file="app.py"):
    step = TraceStep(
        file=source_file, line=10, symbol="x", step_type="source_assignment"
    )
    return TaintFinding(
        rule_id="RULE-001",
        source_file=source_file,
        source_line=10,
        source_pattern="request.GET",
        sink_file=sink_file,
        sink_line=55,
        sink_pattern="cursor.execute",
        trace_path=[step],
        confidence=0.5,
    )


def test_is_available_returns_bool():
    engine = ASTConfirmEngine()
    assert isinstance(engine.is_available(), bool)


def test_confirm_returns_confirm_result():
    engine = ASTConfirmEngine()
    finding = _make_finding()
    result = engine.confirm(finding)
    assert isinstance(result, ConfirmResult)
    assert isinstance(result.confirmed, bool)
    assert isinstance(result.reason, str)
    assert 0.0 <= result.updated_confidence <= 1.0


def test_confirm_all_preserves_length():
    engine = ASTConfirmEngine()
    findings = [_make_finding(), _make_finding("b.py", "c.py")]
    updated = engine.confirm_all(findings)
    assert len(updated) == 2


def test_confirm_all_without_tree_sitter_returns_unchanged_confidence():
    """When tree-sitter is not available, confidence stays at 0.5."""
    with patch("src.domain.ast_confirm_engine._TREE_SITTER_AVAILABLE", False):
        engine = ASTConfirmEngine()
        finding = _make_finding()
        updated = engine.confirm_all([finding])
        assert updated[0].confidence == 0.5


def test_confirm_result_fields():
    result = ConfirmResult(
        confirmed=True, reason="Scope confirmed", updated_confidence=0.9
    )
    assert result.confirmed is True
    assert result.updated_confidence == 0.9
