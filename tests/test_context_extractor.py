from pathlib import Path

from src.domain.context_extractor import extract_context


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
    }


def test_extract_context_scope_reset_after_func(tmp_path: Path) -> None:
    test_file = tmp_path / "after_func.py"
    test_file.write_text(
        "def helper():\n"
        "    return 1\n"
        "\n"
        "var_after = 100\n"
    )

    result = extract_context(str(test_file), 4)
    assert result["line_content"] == "var_after = 100"
    assert result["scope"] == "global"


def test_extract_context_windows_line_endings(tmp_path: Path) -> None:
    test_file = tmp_path / "windows.py"
    test_file.write_bytes(b"x = 10\r\ny = 20\r\n")

    result = extract_context(str(test_file), 1)
    assert result["line_content"] == "x = 10"

