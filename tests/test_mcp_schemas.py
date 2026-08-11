from src.mcp.schemas import DataflowPathResult, TaintContextResult, TaintTraceItem


def test_taint_trace_item():
    item = TaintTraceItem(
        rule_id="R001",
        source_file="src.py",
        source_line=10,
        sink_file="sink.py",
        sink_line=20,
        trace_path=[{"line": 15, "code": "x = 1"}],
        confidence=0.9,
    )
    assert item.rule_id == "R001"
    assert item.to_dict() == {
        "rule_id": "R001",
        "source_file": "src.py",
        "source_line": 10,
        "sink_file": "sink.py",
        "sink_line": 20,
        "trace_path": [{"line": 15, "code": "x = 1"}],
        "confidence": 0.9,
    }


def test_dataflow_path_result():
    result = DataflowPathResult(paths=[{"path": "p1"}], total=1)
    assert result.total == 1
    assert result.paths == [{"path": "p1"}]


def test_taint_context_result():
    result = TaintContextResult(
        file="f1.py", line=1, code_snippet="print(1)", taint_info={"tainted": True}
    )

    assert result.file == "f1.py"
    assert result.line == 1
    assert result.code_snippet == "print(1)"
    assert result.taint_info == {"tainted": True}
