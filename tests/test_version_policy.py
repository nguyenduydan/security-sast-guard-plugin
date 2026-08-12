"""AST-based Version Policy enforcement tests for Security SAST Guard."""

import ast
import re
from pathlib import Path

VERSION_REGEX = re.compile(r"\b\d+\.\d+\.\d+\b|\bv\d+\.\d+\b")


def _is_version_loader_imported(tree: ast.AST) -> bool:
    """Check if AST tree imports version_loader or AuditService."""
    for node in ast.walk(tree):
        if isinstance(node, ast.Import):
            for alias in node.names:
                if "version_loader" in alias.name or "audit_service" in alias.name:
                    return True
        elif (
            isinstance(node, ast.ImportFrom)
            and node.module
            and ("version_loader" in node.module or "audit_service" in node.module)
        ):
            return True
    return False


def _collect_docstring_nodes(tree: ast.AST) -> set[ast.AST]:
    """Collect all AST Constant nodes that represent docstrings."""
    docstrings: set[ast.AST] = set()

    def check_body(body: list[ast.stmt]) -> None:
        if body and isinstance(body[0], ast.Expr):
            val = body[0].value
            if isinstance(val, ast.Constant) and isinstance(val.value, str):
                docstrings.add(val)

    if hasattr(tree, "body"):
        check_body(tree.body)

    for node in ast.walk(tree):
        if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef, ast.ClassDef)):
            check_body(node.body)

    return docstrings


def find_hardcoded_versions_in_source(
    source_code: str, filename: str = "<unknown>"
) -> list[tuple[int, str]]:
    """
    Parse Python source code using AST and find unauthorized hardcoded version strings.

    Returns a list of (line_number, version_string) tuples.
    Excludes:
    - Files importing version_loader
    - Docstrings and comments
    - URLs and external schemas
    """
    try:
        tree = ast.parse(source_code, filename=filename)
    except SyntaxError:
        return []

    if _is_version_loader_imported(tree):
        return []

    # Build parent pointers for AST nodes
    parent_map: dict[ast.AST, ast.AST] = {}
    for parent in ast.walk(tree):
        for child in ast.iter_child_nodes(parent):
            parent_map[child] = parent

    docstrings = _collect_docstring_nodes(tree)
    violations: list[tuple[int, str]] = []

    for node in ast.walk(tree):
        if isinstance(node, ast.Constant) and isinstance(node.value, str):
            if node in docstrings:
                continue

            val = node.value
            if VERSION_REGEX.search(val):
                parent = parent_map.get(node)
                # Ignore URLs, SARIF specification version "2.1.0"
                if (
                    "http://" in val
                    or "https://" in val
                    or "sarif" in val.lower()
                    or "schemata" in val.lower()
                    or val == "2.1.0"
                ):
                    continue

                # Ignore fallback default values in dict.get("version", "1.0.0")
                if isinstance(parent, ast.Call) and val in ("1.0.0", "0.1.0"):
                    continue

                violations.append((getattr(node, "lineno", 0), val))

    return violations


class TestVersionPolicy:
    """Version Policy Test Suite."""

    def test_version_policy_detects_fake_version(self) -> None:
        """VersionPolicyTest must detect VERSION = '2.0.0' in fake test code."""
        fake_code = """
VERSION = "2.0.0"

def get_current_ver():
    return "v1.5"
"""
        violations = find_hardcoded_versions_in_source(fake_code, "fake_test.py")
        assert len(violations) >= 1
        found_versions = [v[1] for v in violations]
        assert "2.0.0" in found_versions

    def test_version_policy_allows_docstrings_and_version_loader(self) -> None:
        """Docstrings and files importing version_loader must be allowed."""
        code_docstring = '"""Version 2.0.0 module docstring."""\nx = 1'
        assert len(find_hardcoded_versions_in_source(code_docstring)) == 0

        code_loader = """
from src.infrastructure.version_loader import get_plugin_version
VER = "2.0.0"
"""
        assert len(find_hardcoded_versions_in_source(code_loader)) == 0

    def test_repository_version_policy(self) -> None:
        """Scan src/, hooks/, and tests/ for hardcoded version strings."""
        repo_root = Path(__file__).resolve().parent.parent
        target_dirs = [repo_root / "src", repo_root / "hooks", repo_root / "tests"]

        violations_by_file: dict[str, list[tuple[int, str]]] = {}

        for target_dir in target_dirs:
            if not target_dir.exists():
                continue
            for py_file in target_dir.rglob("*.py"):
                # Skip self
                if py_file.name == "test_version_policy.py":
                    continue

                source_code = py_file.read_text(encoding="utf-8")
                file_violations = find_hardcoded_versions_in_source(
                    source_code, filename=str(py_file)
                )
                if file_violations:
                    rel_path = py_file.relative_to(repo_root).as_posix()
                    violations_by_file[rel_path] = file_violations

        msg = f"Found hardcoded version strings: {violations_by_file}"
        assert not violations_by_file, msg
