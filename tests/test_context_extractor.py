from pathlib import Path

from src.domain.context_extractor import ContextExtractor, extract_context


def test_extract_context(tmp_path: Path) -> None:
    test_file = tmp_path / "sample.py"
    test_file.write_text(
        "import os\nfrom sys import exit\n\ndef my_func():\n    query = 'SELECT'\n"
    )

    result = extract_context(str(test_file), 5)
    assert result["line_content"].strip() == "query = 'SELECT'"
    assert "import os" in result["imports"]
    assert "from sys import exit" in result["imports"]
    assert result["scope"] == "def my_func():"


def test_extract_context_class_scope(tmp_path: Path) -> None:
    test_file = tmp_path / "class_sample.py"
    test_file.write_text(
        "import math\n\n"
        "class DataProcessor:\n"
        "    def process(self):\n"
        "        val = 42\n"
    )

    result = extract_context(str(test_file), 5)
    assert result["line_content"].strip() == "val = 42"
    assert result["imports"] == "import math"
    assert result["scope"] == "def process(self):"


def test_extract_context_global_scope_and_no_imports(tmp_path: Path) -> None:
    test_file = tmp_path / "simple.py"
    test_file.write_text("x = 10\ny = 20\n")

    result = extract_context(str(test_file), 1)
    assert result["line_content"] == "x = 10"
    assert result["imports"] == ""
    assert result["scope"] == "global"


def test_extract_context_line_out_of_bounds(tmp_path: Path) -> None:
    test_file = tmp_path / "short.py"
    test_file.write_text("a = 1\n")

    result = extract_context(str(test_file), 99)
    assert result["line_content"] == ""
    assert result["imports"] == ""
    assert result["scope"] == "global"


def test_extract_context_file_not_found(tmp_path: Path) -> None:
    non_existent = tmp_path / "does_not_exist.py"
    result = extract_context(str(non_existent), 1)
    assert result == {
        "line_content": "",
        "imports": "",
        "scope": "global",
        "is_safe_context": False,
        "context_window": [],
    }


def test_extract_context_scope_reset_after_func(tmp_path: Path) -> None:
    test_file = tmp_path / "after_func.py"
    test_file.write_text("def helper():\n    return 1\n\nvar_after = 100\n")

    result = extract_context(str(test_file), 4)
    assert result["line_content"] == "var_after = 100"
    assert result["scope"] == "global"


def test_extract_context_windows_line_endings(tmp_path: Path) -> None:
    test_file = tmp_path / "windows.py"
    test_file.write_bytes(b"x = 10\r\ny = 20\r\n")

    result = extract_context(str(test_file), 1)
    assert result["line_content"] == "x = 10"


def test_multiline_block_comment_js_is_safe() -> None:
    extractor = ContextExtractor()
    lines = [
        "/*\n",
        " * eval(userInput);\n",
        " */\n",
        "const valid = true;\n",
    ]
    ctx = extractor.extract_context_from_lines(lines, line_number=2, file_path="app.js")
    assert ctx["is_safe_context"] is True


def test_multiline_block_comment_js_no_leading_asterisk_is_safe() -> None:
    extractor = ContextExtractor()
    lines = [
        "/*\n",
        "   eval(userInput);\n",
        "*/\n",
        "const valid = true;\n",
    ]
    ctx = extractor.extract_context_from_lines(lines, line_number=2, file_path="app.js")
    assert ctx["is_safe_context"] is True


def test_multiline_block_comment_html_is_safe() -> None:
    extractor = ContextExtractor()
    lines = [
        "<!--\n",
        "  <script>evil()</script>\n",
        "-->\n",
        "<div>safe</div>\n",
    ]
    ctx = extractor.extract_context_from_lines(
        lines, line_number=2, file_path="index.html"
    )
    assert ctx["is_safe_context"] is True


def test_single_line_comment_does_not_leak_to_next_line() -> None:
    extractor = ContextExtractor()
    lines = [
        "/* short comment */\n",
        "eval(userInput);\n",
    ]
    ctx = extractor.extract_context_from_lines(lines, line_number=2, file_path="app.js")
    assert ctx["is_safe_context"] is False


def test_context_window_extraction() -> None:
    extractor = ContextExtractor()
    lines = [f"line_{i}\n" for i in range(1, 20)]
    ctx = extractor.extract_context_from_lines(
        lines, line_number=10, file_path="service.py"
    )
    assert "context_window" in ctx
    window_lines = ctx["context_window"]
    assert len(window_lines) == 11
    assert "line_10" in window_lines[5]


def test_context_window_bounds() -> None:
    extractor = ContextExtractor()
    lines = ["a\n", "b\n", "c\n"]
    ctx = extractor.extract_context_from_lines(
        lines, line_number=1, file_path="sample.py"
    )
    assert ctx["context_window"] == ["a", "b", "c"]
