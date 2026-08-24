import textwrap
from pathlib import Path

from src.domain.models import SymbolMap
from src.domain.taint_tracker import TaintTracker


def _make_repo(files: dict[str, str], base_dir: Path) -> str:
    for name, content in files.items():
        p = base_dir / name
        p.parent.mkdir(parents=True, exist_ok=True)
        p.write_text(content, encoding="utf-8")
    return str(base_dir)


def test_trace_finds_sink_usage(tmp_path: Path) -> None:
    repo = _make_repo(
        {
            "views.py": textwrap.dedent("""\
            user_input = request.GET.get('q')
            cursor.execute(user_input)
        """)
        },
        tmp_path,
    )
    symbol_map: SymbolMap = {"user_input": [("views.py", 1)]}
    tracker = TaintTracker(repo)
    findings = tracker.trace(
        symbol_map=symbol_map,
        rule_id="RULE-001",
        source_pattern="request.GET",
        sinks=["cursor.execute"],
    )
    assert len(findings) == 1
    f = findings[0]
    assert f.rule_id == "RULE-001"
    assert f.source_file == "views.py"
    assert f.sink_file == "views.py"
    assert f.sink_line == 2
    assert f.sink_pattern == "cursor.execute"
    assert 0.0 <= f.confidence <= 1.0
    assert len(f.trace_path) >= 2


def test_trace_no_sink_returns_empty(tmp_path: Path) -> None:
    repo = _make_repo({"views.py": "user_input = request.GET.get('q')\n"}, tmp_path)
    symbol_map: SymbolMap = {"user_input": [("views.py", 1)]}
    tracker = TaintTracker(repo)
    findings = tracker.trace(symbol_map, "RULE-001", "request.GET", ["eval"])
    assert not findings


def test_trace_skips_symbol_not_in_sink_line(tmp_path: Path) -> None:
    repo = _make_repo(
        {
            "views.py": textwrap.dedent("""\
            user_input = request.GET.get('q')
            cursor.execute("SELECT 1")
        """)
        },
        tmp_path,
    )
    symbol_map: SymbolMap = {"user_input": [("views.py", 1)]}
    tracker = TaintTracker(repo)
    findings = tracker.trace(symbol_map, "RULE-001", "request.GET", ["cursor.execute"])
    # sink line exists but doesn't contain the tainted symbol
    assert not findings
