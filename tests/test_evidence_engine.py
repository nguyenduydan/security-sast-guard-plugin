"""Unit tests for EvidenceEngine, EvidenceNode, and EvidenceGraph."""

from src.domain.evidence_engine import EvidenceEngine, EvidenceGraph, EvidenceNode


def test_evidence_node_and_graph_dataclasses() -> None:
    """Test instantiation and attributes of EvidenceNode and EvidenceGraph."""
    node = EvidenceNode(
        node_id="n1",
        node_type="source",
        file_path="app.py",
        line_number=10,
        code_snippet="data = input()",
        symbol="data",
    )
    assert node.node_id == "n1"
    assert node.node_type == "source"
    assert node.file_path == "app.py"
    assert node.line_number == 10
    assert node.code_snippet == "data = input()"
    assert node.symbol == "data"

    graph = EvidenceGraph(
        finding_id="F-001",
        nodes=[node],
        edges=[],
        program_slice=["L10: data = input()"],
        is_complete_path=False,
    )
    assert graph.finding_id == "F-001"
    assert len(graph.nodes) == 1
    assert graph.is_complete_path is False


def test_is_complete_path_true() -> None:
    """Test is_complete_path returns True for connected source to sink path."""
    engine = EvidenceEngine()
    nodes = [
        EvidenceNode("n1", "source", "main.py", 1, "src = get_user_input()", "src"),
        EvidenceNode("n2", "propagation", "main.py", 2, "buf = src", "buf"),
        EvidenceNode("n3", "sink", "main.py", 3, "exec(buf)", "buf"),
    ]
    edges = [("n1", "n2"), ("n2", "n3")]
    assert engine.is_complete_path(nodes, edges) is True


def test_is_complete_path_false_disconnected() -> None:
    """Test is_complete_path returns False when source and sink are disconnected."""
    engine = EvidenceEngine()
    nodes = [
        EvidenceNode("n1", "source", "main.py", 1, "src = get_user_input()", "src"),
        EvidenceNode("n2", "sink", "main.py", 5, "exec(other_var)", "other_var"),
    ]
    edges: list[tuple[str, str]] = []
    assert engine.is_complete_path(nodes, edges) is False


def test_is_complete_path_false_missing_nodes() -> None:
    """Test is_complete_path returns False when source or sink node is missing."""
    engine = EvidenceEngine()
    nodes_no_sink = [
        EvidenceNode("n1", "source", "main.py", 1, "src = get_user_input()", "src"),
        EvidenceNode("n2", "propagation", "main.py", 2, "buf = src", "buf"),
    ]
    assert engine.is_complete_path(nodes_no_sink, [("n1", "n2")]) is False

    nodes_no_source = [
        EvidenceNode("n1", "sink", "main.py", 3, "exec(buf)", "buf"),
    ]
    assert engine.is_complete_path(nodes_no_source, []) is False


def test_program_slicing_with_source_code() -> None:
    """Test slice_program extracts relevant lines matching nodes and symbols."""
    engine = EvidenceEngine()
    source_code = (
        "# Line 1: Comment\n"
        "val = request.args.get('user')\n"
        "unused_var = 100\n"
        "clean_val = val.strip()\n"
        "# Line 5: Comment\n"
        "execute_query(clean_val)\n"
    )

    nodes = [
        EvidenceNode(
            "n1", "source", "query.py", 2, "val = request.args.get('user')", "val"
        ),
        EvidenceNode(
            "n2", "propagation", "query.py", 4, "clean_val = val.strip()", "clean_val"
        ),
        EvidenceNode(
            "n3", "sink", "query.py", 6, "execute_query(clean_val)", "clean_val"
        ),
    ]

    sliced = engine.slice_program(source_code, nodes)
    assert "L2: val = request.args.get('user')" in sliced
    assert "L4: clean_val = val.strip()" in sliced
    assert "L6: execute_query(clean_val)" in sliced
    assert not any("unused_var" in line for line in sliced)


def test_program_slicing_empty_source_code() -> None:
    """Test slice_program fallback when source code is empty."""
    engine = EvidenceEngine()
    nodes = [
        EvidenceNode("n1", "source", "test.py", 5, "x = 1", "x"),
    ]
    sliced = engine.slice_program("", nodes)
    assert sliced == ["L5: x = 1"]


def test_build_graph_with_source_code_map() -> None:
    """Test build_graph constructs EvidenceGraph with program slice and completeness."""
    engine = EvidenceEngine()
    source_map = {
        "api.py": "raw = input()\nunused = 42\neval(raw)\n",
    }
    nodes = [
        EvidenceNode("n1", "source", "api.py", 1, "raw = input()", "raw"),
        EvidenceNode("n2", "sink", "api.py", 3, "eval(raw)", "raw"),
    ]
    edges = [("n1", "n2")]

    graph = engine.build_graph("FINDING-123", nodes, edges, source_map)
    assert graph.finding_id == "FINDING-123"
    assert graph.is_complete_path is True
    assert "L1: raw = input()" in graph.program_slice
    assert "L3: eval(raw)" in graph.program_slice


def test_build_from_trace() -> None:
    """Test build_from_trace constructs EvidenceGraph from raw trace steps."""
    engine = EvidenceEngine()
    trace_steps = [
        {
            "file": "vuln.py",
            "line": 1,
            "symbol": "cmd",
            "code_snippet": "cmd = request.GET['c']",
            "step_type": "source_assignment",
        },
        {
            "file": "vuln.py",
            "line": 2,
            "symbol": "safe_cmd",
            "code_snippet": "safe_cmd = sanitize(cmd)",
            "step_type": "sanitizer",
        },
        {
            "file": "vuln.py",
            "line": 3,
            "symbol": "safe_cmd",
            "code_snippet": "subprocess.run(safe_cmd)",
            "step_type": "sink",
        },
    ]

    graph = engine.build_from_trace("TRACE-001", trace_steps)
    assert graph.finding_id == "TRACE-001"
    assert len(graph.nodes) == 3
    assert graph.nodes[0].node_type == "source"
    assert graph.nodes[1].node_type == "sanitizer"
    assert graph.nodes[2].node_type == "sink"
    assert graph.edges == [("node_1", "node_2"), ("node_2", "node_3")]
    assert graph.is_complete_path is True
