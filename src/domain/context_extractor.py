import io
import tokenize
from abc import ABC, abstractmethod
from typing import Any


class ISafeContextStrategy(ABC):
    """Abstract Strategy for safe context evaluation."""

    @abstractmethod
    def is_safe_context(
        self, line_content: str, line_number: int, lines: list[str]
    ) -> bool:
        """Check whether target line is safe context."""


class PythonSafeContextStrategy(ISafeContextStrategy):
    """Tokenization-based safe context checker for Python code."""

    def is_safe_context(
        self, line_content: str, line_number: int, lines: list[str]
    ) -> bool:
        _ = line_content
        try:
            # Tokenize only up to the target line to avoid unnecessary processing
            content = "".join(lines[:line_number])
            tokens = tokenize.tokenize(io.BytesIO(content.encode("utf-8")).readline)
            is_safe = False
            for t in tokens:
                if t.start[0] == line_number:
                    if t.type in (tokenize.COMMENT, tokenize.STRING):
                        is_safe = True
                        break
                    if t.type not in (
                        tokenize.NL,
                        tokenize.NEWLINE,
                        tokenize.INDENT,
                        tokenize.DEDENT,
                    ):
                        is_safe = False
                        break
            return is_safe
        except (tokenize.TokenError, UnicodeEncodeError, IndentationError):
            return False


class GenericSafeContextStrategy(ISafeContextStrategy):
    """Fast in-memory safe context checker for non-Python files."""

    def is_safe_context(
        self, line_content: str, line_number: int, lines: list[str]
    ) -> bool:
        _ = (line_number, lines)
        stripped = line_content.strip()
        if not stripped:
            return True

        # Fast O(1) comment checks for common languages
        return (
            stripped.startswith("#")
            or stripped.startswith("//")
            or stripped.startswith("/*")
            or stripped.startswith("<!--")
            or stripped.startswith("*")
        )


class ContextExtractor:
    """In-memory Context Extractor evaluating scope and safe context in O(1) file IO."""

    def __init__(self) -> None:
        self._python_strategy = PythonSafeContextStrategy()
        self._generic_strategy = GenericSafeContextStrategy()

    def _get_strategy(self, file_path: str) -> ISafeContextStrategy:
        if file_path.lower().endswith(".py"):
            return self._python_strategy
        return self._generic_strategy

    def extract_context_from_lines(
        self, lines: list[str], line_number: int, file_path: str
    ) -> dict[str, Any]:
        """Extract line context and safety status directly from memory."""
        imports: list[str] = []
        scope = "global"
        line_content = lines[line_number - 1] if 0 < line_number <= len(lines) else ""

        if file_path.lower().endswith(".py"):
            max_idx = min(line_number, len(lines))
            for i in range(max_idx):
                line = lines[i]
                stripped = line.strip()
                if stripped.startswith("import ") or stripped.startswith("from "):
                    imports.append(stripped)
                if stripped:
                    if stripped.startswith("def ") or stripped.startswith("class "):
                        scope = stripped
                    elif not (
                        line.startswith(" ") or line.startswith("\t")
                    ) and not stripped.startswith("@"):
                        scope = "global"

        strategy = self._get_strategy(file_path)
        is_safe = strategy.is_safe_context(line_content, line_number, lines)

        return {
            "line_content": line_content.rstrip("\r\n"),
            "imports": "\n".join(imports),
            "scope": scope,
            "is_safe_context": is_safe,
        }


# Global instance for backward compatibility
_DEFAULT_EXTRACTOR = ContextExtractor()


def extract_context(file_path: str, line_number: int) -> dict[str, str | bool]:
    """Legacy backward-compatible wrapper loading file content on demand."""
    try:
        with open(file_path, encoding="utf-8", errors="replace") as f:
            lines = f.readlines()
    except OSError:
        return {
            "line_content": "",
            "imports": "",
            "scope": "global",
            "is_safe_context": False,
        }
    return _DEFAULT_EXTRACTOR.extract_context_from_lines(lines, line_number, file_path)
