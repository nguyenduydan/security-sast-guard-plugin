# tests/test_taint_models.py

from src.domain.models import TaintFinding, TraceStep


def test_trace_step_fields():
    step = TraceStep(
        file="app.py", line=10, symbol="user_input", step_type="source_assignment"
    )
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
