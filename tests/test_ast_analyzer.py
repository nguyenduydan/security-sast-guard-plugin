"""Tests for ASTPrecisionAnalyzer."""

from pathlib import Path

from src.domain.ast_analyzer import ASTPrecisionAnalyzer


def test_ast_analyzer_constant_string_command_is_safe() -> None:
    analyzer = ASTPrecisionAnalyzer()
    code = 'import os\nos.system("git status")\n'
    is_safe = analyzer.is_safe_sink_call(
        file_path="sample.py",
        line_number=2,
        rule_id="CMD_INJECTION",
        line_content='os.system("git status")',
        code_content=code,
    )
    assert is_safe is True


def test_ast_analyzer_dynamic_variable_is_not_safe() -> None:
    analyzer = ASTPrecisionAnalyzer()
    code = "import os\ncmd = input()\nos.system(cmd)\n"
    is_safe = analyzer.is_safe_sink_call(
        file_path="sample.py",
        line_number=3,
        rule_id="CMD_INJECTION",
        line_content="os.system(cmd)",
        code_content=code,
    )
    assert is_safe is False


def test_ast_analyzer_typecast_int_is_safe() -> None:
    analyzer = ASTPrecisionAnalyzer()
    code = (
        'user_id = int(request.args.get("id"))\n'
        'query = f"SELECT * FROM users WHERE id = {user_id}"\n'
    )
    is_safe = analyzer.is_safe_sink_call(
        file_path="sample.py",
        line_number=2,
        rule_id="SQL_INJECTION",
        line_content='query = f"SELECT * FROM users WHERE id = {user_id}"',
        code_content=code,
    )
    assert is_safe is True


def test_ast_analyzer_typecast_float_and_uuid_is_safe() -> None:
    analyzer = ASTPrecisionAnalyzer()
    code = (
        'price = float(data["price"])\n'
        'uid = UUID(data["uuid"])\n'
        'query = f"UPDATE items SET price = {price} WHERE id = {uid}"\n'
    )
    is_safe = analyzer.is_safe_sink_call(
        file_path="sample.py",
        line_number=3,
        rule_id="SQL_INJECTION",
        line_content='query = f"UPDATE items SET price = {price} WHERE id = {uid}"',
        code_content=code,
    )
    assert is_safe is True


def test_ast_analyzer_list_of_constants_is_safe() -> None:
    analyzer = ASTPrecisionAnalyzer()
    code = 'import subprocess\nsubprocess.run(["git", "status", "--short"])\n'
    is_safe = analyzer.is_safe_sink_call(
        file_path="sample.py",
        line_number=2,
        rule_id="CMD_INJECTION",
        line_content='subprocess.run(["git", "status", "--short"])',
        code_content=code,
    )
    assert is_safe is True


def test_ast_analyzer_non_python_file_returns_false() -> None:
    analyzer = ASTPrecisionAnalyzer()
    is_safe = analyzer.is_safe_sink_call(
        file_path="sample.js",
        line_number=2,
        rule_id="CMD_INJECTION",
        line_content='exec("ls")',
        code_content='exec("ls")',
    )
    assert is_safe is False


def test_ast_analyzer_syntax_error_returns_false() -> None:
    analyzer = ASTPrecisionAnalyzer()
    is_safe = analyzer.is_safe_sink_call(
        file_path="sample.py",
        line_number=1,
        rule_id="CMD_INJECTION",
        line_content="invalid syntax ((((",
        code_content="invalid syntax ((((",
    )
    assert is_safe is False


def test_ast_analyzer_no_target_node_returns_false() -> None:
    analyzer = ASTPrecisionAnalyzer()
    code = "x = 1\n"
    is_safe = analyzer.is_safe_sink_call(
        file_path="sample.py",
        line_number=99,
        rule_id="CMD_INJECTION",
        line_content="",
        code_content=code,
    )
    assert is_safe is False


def test_ast_analyzer_reads_file_from_disk(tmp_path: Path) -> None:
    analyzer = ASTPrecisionAnalyzer()
    test_file = tmp_path / "test_exec.py"
    test_file.write_text('import os\nos.system("uptime")\n', encoding="utf-8")

    is_safe = analyzer.is_safe_sink_call(
        file_path=str(test_file),
        line_number=2,
        rule_id="CMD_INJECTION",
        line_content='os.system("uptime")',
        code_content=None,
    )
    assert is_safe is True
