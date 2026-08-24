# tests/test_symbol_indexer.py
import tempfile
import textwrap
from pathlib import Path

from src.domain.symbol_indexer import SymbolIndexer


def _make_repo(files: dict[str, str]) -> str:
    """Create a temp directory with given files."""
    d = tempfile.mkdtemp()
    for name, content in files.items():
        p = Path(d) / name
        p.parent.mkdir(parents=True, exist_ok=True)
        p.write_text(content, encoding="utf-8")
    return d


def test_index_finds_simple_assignment():
    repo = _make_repo(
        {
            "views.py": textwrap.dedent("""\
            user_input = request.GET.get('q')
            name = request.GET.get('name')
        """)
        }
    )
    indexer = SymbolIndexer(repo)
    result = indexer.index(["request.GET"])
    assert "user_input" in result
    assert "name" in result
    assert result["user_input"][0] == ("views.py", 1)


def test_index_skips_non_assignment_lines():
    repo = _make_repo({"views.py": "print(request.GET.get('q'))\n"})
    indexer = SymbolIndexer(repo)
    result = indexer.index(["request.GET"])
    assert len(result) == 0


def test_extract_symbol_name_simple():
    indexer = SymbolIndexer(".")
    sym = indexer.extract_symbol_name(
        "user_input = request.GET.get('q')", "request.GET"
    )
    assert sym == "user_input"


def test_extract_symbol_name_no_match():
    indexer = SymbolIndexer(".")
    sym = indexer.extract_symbol_name("print(request.GET)", "request.GET")
    assert sym is None


def test_extract_symbol_name_multilanguage():
    indexer = SymbolIndexer(".")

    # TypeScript / JavaScript
    assert (
        indexer.extract_symbol_name(
            "const apiKey = req.headers['x-api-key'];", "req.headers"
        )
        == "apiKey"
    )
    assert (
        indexer.extract_symbol_name(
            "let userInput: string = req.query.name;", "req.query"
        )
        == "userInput"
    )
    assert (
        indexer.extract_symbol_name("var query = req.body.search;", "req.body")
        == "query"
    )

    # Go walrus
    assert (
        indexer.extract_symbol_name('query := r.URL.Query().Get("q")', "r.URL.Query()")
        == "query"
    )

    # C# / Java typed
    assert (
        indexer.extract_symbol_name(
            'string sql = Request.QueryString["id"];', "Request.QueryString"
        )
        == "sql"
    )
    assert (
        indexer.extract_symbol_name(
            'public static String rawData = request.getParameter("data");',
            "request.getParameter",
        )
        == "rawData"
    )

    # Kotlin / Scala
    assert (
        indexer.extract_symbol_name(
            'val token = request.getHeader("Authorization")',
            "request.getHeader",
        )
        == "token"
    )

    # Python typed
    assert (
        indexer.extract_symbol_name(
            "user_val: str = request.args.get('val')", "request.args"
        )
        == "user_val"
    )
