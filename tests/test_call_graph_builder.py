"""
Tests for CallGraphBuilder.
"""

import tempfile
import textwrap
from pathlib import Path

from src.domain.call_graph_builder import CallGraphBuilder


def test_import_graph(tmp_path: Path):
    """Test building an import graph for python."""
    # Create a mock repo
    py_dir = tmp_path / "py_proj"
    py_dir.mkdir()
    (py_dir / "main.py").write_text(
        "import py_proj.utils\nfrom py_proj.helpers import do_thing\n"
    )
    (py_dir / "utils.py").write_text("import py_proj.db\n")
    (py_dir / "helpers.py").write_text("from py_proj.db import query\n")
    (py_dir / "db.py").write_text("import os\n")

    builder = CallGraphBuilder(str(tmp_path))
    graph = builder.build_import_graph(["py_proj/main.py"])

    norm_graph = {
        k.replace("\\", "/"): [v.replace("\\", "/") for v in vals]
        for k, vals in graph.items()
    }

    assert "py_proj/main.py" in norm_graph
    assert "py_proj/utils.py" in norm_graph["py_proj/main.py"]
    assert "py_proj/helpers.py" in norm_graph["py_proj/main.py"]
    assert "py_proj/db.py" in norm_graph["py_proj/utils.py"]


def _make_repo(files: dict[str, str]) -> str:
    d = tempfile.mkdtemp()
    for name, content in files.items():
        p = Path(d) / name
        p.parent.mkdir(parents=True, exist_ok=True)
        p.write_text(content, encoding="utf-8")
    return d


def test_build_import_graph_python():
    repo = _make_repo(
        {
            "views.py": "from utils import run_query\n",
            "utils.py": "def run_query(q): pass\n",
        }
    )
    builder = CallGraphBuilder(repo)
    graph = builder.build_import_graph(["views.py"])
    assert "views.py" in graph
    # utils.py should appear as a dependency of views.py
    assert any("utils.py" in dep for dep in graph["views.py"])


def test_build_import_graph_no_imports():
    repo = _make_repo({"standalone.py": "x = 1\n"})
    builder = CallGraphBuilder(repo)
    graph = builder.build_import_graph(["standalone.py"])
    assert graph["standalone.py"] == []


def test_build_import_graph_circular_does_not_hang():
    repo = _make_repo(
        {
            "a.py": "from b import foo\n",
            "b.py": "from a import bar\n",
        }
    )
    builder = CallGraphBuilder(repo)
    # Should complete without infinite loop
    graph = builder.build_import_graph(["a.py"])
    assert "a.py" in graph


def test_trace_to_sinks(tmp_path: Path):
    """Test BFS tracing to sinks."""
    (tmp_path / "app.py").write_text("from db import query\n")
    (tmp_path / "db.py").write_text("from driver import execute\n")
    (tmp_path / "driver.py").write_text("# sink file\n")

    builder = CallGraphBuilder(str(tmp_path))
    chains = builder.trace_to_sinks("app.py", "main_fn", ["driver"])

    assert len(chains) == 1
    chain = chains[0]
    assert chain.entry_fn == "app.py"
    assert "driver" in chain.terminal_sink.replace("\\", "/")
    assert len(chain.steps) == 2


def test_trace_to_sinks_finds_cross_file_sink():
    repo = _make_repo(
        {
            "views.py": textwrap.dedent("""\
            from utils import run_query
            user_input = request.GET.get('q')
            run_query(user_input)
        """),
            "utils.py": textwrap.dedent("""\
            def run_query(q):
                cursor.execute(q)
        """),
        }
    )
    builder = CallGraphBuilder(repo)
    chains = builder.trace_to_sinks("views.py", "user_input", ["cursor.execute"])
    # Should find a path: views.py → utils.py → cursor.execute
    assert len(chains) >= 1
    assert chains[0].terminal_sink == "cursor.execute"


def test_trace_to_sinks_no_cross_file_match():
    repo = _make_repo(
        {
            "views.py": "user_input = request.GET.get('q')\n",
        }
    )
    builder = CallGraphBuilder(repo)
    chains = builder.trace_to_sinks("views.py", "user_input", ["eval"])
    assert not chains
