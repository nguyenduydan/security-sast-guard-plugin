"""ASTConfirmEngine: tree-sitter-based taint finding confirmation.

tree-sitter is an optional dependency. If not installed, all confirmations
gracefully degrade: findings are returned unchanged with a warning log.
"""

import logging
from dataclasses import dataclass, replace
from typing import Any

from .models import TaintFinding

logger = logging.getLogger(__name__)

# Try to import tree-sitter. Set flag for graceful degradation.
try:
    import tree_sitter_languages
    from tree_sitter import Parser

    _TREE_SITTER_AVAILABLE = True
except ImportError:
    _TREE_SITTER_AVAILABLE = False
    logger.warning(
        "tree-sitter not installed; AST confirmation skipped. "
        "Install with: pip install security-sast-guard[ast]"
    )

# Mapping of file extension ? tree-sitter language name
_EXT_TO_LANG: dict[str, str] = {
    ".py": "python",
    ".js": "javascript",
    ".ts": "typescript",
    ".jsx": "javascript",
    ".tsx": "typescript",
    ".cs": "c_sharp",
    ".java": "java",
    ".php": "php",
    ".rb": "ruby",
    ".go": "go",
    ".rs": "rust",
}


@dataclass(frozen=True)
class ConfirmResult:
    """Outcome of AST-based confirmation of a TaintFinding."""

    confirmed: bool
    reason: str
    updated_confidence: float


class ASTConfirmEngine:
    """Confirms or rejects TaintFindings using tree-sitter AST analysis."""

    def is_available(self) -> bool:
        """Return True if tree-sitter is installed and usable."""
        return _TREE_SITTER_AVAILABLE

    def confirm(self, finding: TaintFinding) -> ConfirmResult:
        """Attempt to confirm a single TaintFinding using AST analysis.

        If tree-sitter is unavailable or the language is unsupported,
        returns a neutral result with the original confidence.
        """
        if not _TREE_SITTER_AVAILABLE:
            return ConfirmResult(
                confirmed=True,
                reason="tree-sitter not available; skipping AST confirmation",
                updated_confidence=finding.confidence,
            )

        from pathlib import Path  # pylint: disable=import-outside-toplevel

        source_path = Path(finding.source_file)
        lang_name = _EXT_TO_LANG.get(source_path.suffix)
        if not lang_name:
            return ConfirmResult(
                confirmed=True,
                reason=f"Unsupported language: {source_path.suffix}",
                updated_confidence=finding.confidence,
            )

        try:
            return self._run_ast_check(finding, lang_name)
        except Exception as exc:  # pylint: disable=broad-except
            logger.warning(
                "AST confirmation failed for %s: %s", finding.source_file, exc
            )
            return ConfirmResult(
                confirmed=True,
                reason=f"AST error: {exc}",
                updated_confidence=finding.confidence,
            )

    def confirm_all(self, findings: list[TaintFinding]) -> list[TaintFinding]:
        """Confirm all findings. Returns new list with updated confidence values.

        Findings with confirmed=False (AST-rejected) get confidence=0.0.
        Findings with confirmed=True get confidence updated from ConfirmResult.
        """
        if not _TREE_SITTER_AVAILABLE:
            return findings

        updated: list[TaintFinding] = []
        for finding in findings:
            result = self.confirm(finding)
            new_confidence = 0.0 if not result.confirmed else result.updated_confidence
            updated.append(replace(finding, confidence=new_confidence))
        return updated

    def _run_ast_check(self, finding: TaintFinding, lang_name: str) -> ConfirmResult:
        """Parse source file AST and check if the tainted symbol reaches the sink.

        Current heuristic: verify the symbol appears in function scope at both
        source and sink locations (same function body = higher confidence).
        """
        from pathlib import Path  # pylint: disable=import-outside-toplevel

        source_path = Path(finding.source_file)
        if not source_path.exists():
            return ConfirmResult(
                confirmed=True,
                reason="Source file not readable",
                updated_confidence=finding.confidence,
            )

        language = tree_sitter_languages.get_language(lang_name)
        parser = Parser()
        parser.set_language(language)

        source_code = source_path.read_bytes()
        tree = parser.parse(source_code)

        sink_path = Path(finding.sink_file)
        if finding.source_file != finding.sink_file and sink_path.exists():
            sink_code = sink_path.read_bytes()
            sink_tree = parser.parse(sink_code)
            _fn_at_sink = self._find_enclosing_function(sink_tree, finding.sink_line)
            return ConfirmResult(
                confirmed=True,
                reason=(
                    f"Cross-file taint path from {source_path.name} "
                    f"to {sink_path.name}"
                ),
                updated_confidence=max(0.7, finding.confidence),
            )

        # Simple heuristic for same-file taint: both within same top-level function or module
        fn_at_source = self._find_enclosing_function(tree, finding.source_line)
        fn_at_sink = self._find_enclosing_function(tree, finding.sink_line)

        if fn_at_source is not None and fn_at_source == fn_at_sink:
            return ConfirmResult(
                confirmed=True,
                reason=f"Same function scope: {fn_at_source}",
                updated_confidence=0.9,
            )
        if fn_at_source is None and fn_at_sink is None:
            # Both at module level - still a valid taint path
            return ConfirmResult(
                confirmed=True,
                reason="Module-level taint path",
                updated_confidence=0.7,
            )
        return ConfirmResult(
            confirmed=False,
            reason="Source and sink in different scopes - likely false positive",
            updated_confidence=0.0,
        )

    @staticmethod
    def _find_enclosing_function(tree: Any, line_number: int) -> str | None:
        """Walk the AST to find the name of the function enclosing line_number.

        Returns the function name string, or None if at module level.
        """
        target_byte_line = line_number - 1  # tree-sitter uses 0-indexed rows

        def walk(node: Any) -> str | None:
            if node.type in (
                "function_definition",
                "method_declaration",
                "function_dec",
            ):
                start = node.start_point[0]
                end = node.end_point[0]
                if start <= target_byte_line <= end:
                    # Try to get function name from first named child
                    for child in node.children:
                        if child.type == "identifier":
                            res: str = child.text.decode("utf-8", errors="ignore")
                            return res
                    return "<anonymous>"
            for child in node.children:
                result = walk(child)
                if result is not None:
                    return result
            return None

        res_fn: str | None = walk(tree.root_node)
        return res_fn
