"""
Tests for CallGraphBuilder.
"""
from pathlib import Path
from src.domain.call_graph_builder import CallGraphBuilder

def test_import_graph(tmp_path: Path):
    """Test building an import graph for python."""
    # Create a mock repo
    py_dir = tmp_path / "py_proj"
    py_dir.mkdir()
    (py_dir / "main.py").write_text("import py_proj.utils\nfrom py_proj.helpers import do_thing\n")
    (py_dir / "utils.py").write_text("import py_proj.db\n")
    (py_dir / "helpers.py").write_text("from py_proj.db import query\n")
    (py_dir / "db.py").write_text("import os\n")

    builder = CallGraphBuilder(str(tmp_path))
    graph = builder.build_import_graph(["py_proj/main.py"])

    norm_graph = {k.replace('\\', '/'): [v.replace('\\', '/') for v in vals] for k, vals in graph.items()}

    assert "py_proj/main.py" in norm_graph
    assert "py_proj/utils.py" in norm_graph["py_proj/main.py"]
    assert "py_proj/helpers.py" in norm_graph["py_proj/main.py"]
    assert "py_proj/db.py" in norm_graph["py_proj/utils.py"]

def test_trace_to_sinks(tmp_path: Path):
    """Test BFS tracing to sinks."""
    (tmp_path / "app.py").write_text("from db import query\n")
    (tmp_path / "db.py").write_text("from driver import execute\n")
    (tmp_path / "driver.py").write_text("# sink file\n")

    builder = CallGraphBuilder(str(tmp_path))
    chains = builder.trace_to_sinks("app.py", "main_fn", ["driver"])

    assert len(chains) == 1
    chain = chains[0]
    assert chain.entry_fn == "main_fn"
    assert "driver.py" in chain.terminal_sink.replace('\\', '/')
    assert len(chain.steps) == 2
