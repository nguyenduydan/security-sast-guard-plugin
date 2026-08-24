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


class _MockNode:
    def __init__(
        self,
        node_type: str,
        start_row: int,
        end_row: int,
        children: list["_MockNode"] | None = None,
        text: bytes = b"",
    ) -> None:
        self.type = node_type
        self.start_point = (start_row, 0)
        self.end_point = (end_row, 0)
        self.children = children or []
        self.text = text


class _MockTree:
    def __init__(self, root_node: _MockNode) -> None:
        self.root_node = root_node


def test_find_enclosing_function_named() -> None:
    ident_node = _MockNode("identifier", 10, 10, text=b"process_data")
    func_node = _MockNode("function_definition", 10, 30, children=[ident_node])
    root = _MockNode("module", 0, 50, children=[func_node])
    tree = _MockTree(root)

    # Line 20 is inside function_definition (rows 10-30 -> line 20 has byte line 19)
    fn_name = ASTConfirmEngine._find_enclosing_function(tree, 20)
    assert fn_name == "process_data"


def test_find_enclosing_function_anonymous() -> None:
    func_node = _MockNode("function_definition", 10, 30, children=[])
    root = _MockNode("module", 0, 50, children=[func_node])
    tree = _MockTree(root)

    fn_name = ASTConfirmEngine._find_enclosing_function(tree, 15)
    assert fn_name == "<anonymous>"


def test_find_enclosing_function_module_level() -> None:
    func_node = _MockNode("function_definition", 10, 30, children=[])
    root = _MockNode("module", 0, 50, children=[func_node])
    tree = _MockTree(root)

    # Line 5 is outside function definition
    fn_name = ASTConfirmEngine._find_enclosing_function(tree, 5)
    assert fn_name is None
