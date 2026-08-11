"""SymbolIndexer: grep-based source assignment finder."""

import re
from collections.abc import Generator
from pathlib import Path

from .models import SymbolMap

# Matches: <identifier> = <anything containing source_keyword>
# Also matches: <identifier>: <type> = <...> (typed annotations)
_ASSIGN_RE = re.compile(
    r"^[ \t]*([a-zA-Z_]\w*)(?:\s*:\s*\S+)?\s*[:=]=?\s*.*?({SOURCE})"
)

# File extensions to scan (text-based code files)
_SCAN_EXTENSIONS = {
    ".py",
    ".js",
    ".ts",
    ".jsx",
    ".tsx",
    ".cs",
    ".java",
    ".php",
    ".rb",
    ".go",
    ".rs",
    ".cpp",
    ".c",
    ".h",
    ".vue",
    ".svelte",
    ".kt",
    ".swift",
}

# Directories to skip
_SKIP_DIRS = {
    ".git",
    ".venv",
    "venv",
    "node_modules",
    "__pycache__",
    ".mypy_cache",
    ".ruff_cache",
    "dist",
    "build",
    ".sast",
}


class SymbolIndexer:
    """Scans a repository to find variable assignments from taint sources."""

    def __init__(self, repo_path: str) -> None:
        self.repo_path = Path(repo_path).resolve()

    def index(self, sources: list[str]) -> SymbolMap:
        """Grep repo files for assignments from any of the source patterns.

        Returns SymbolMap: { symbol_name: [(relative_file_path, line_number)] }
        """
        result: SymbolMap = {}
        for file_path in self._iter_code_files():
            rel = str(file_path.relative_to(self.repo_path))
            try:
                lines = file_path.read_text(
                    encoding="utf-8", errors="ignore"
                ).splitlines()
            except OSError:
                continue
            for lineno, line in enumerate(lines, start=1):
                for source in sources:
                    if source not in line:
                        continue
                    symbol = self.extract_symbol_name(line, source)
                    if symbol:
                        result.setdefault(symbol, []).append((rel, lineno))
        return result

    def extract_symbol_name(self, line: str, source: str) -> str | None:
        """Return the LHS variable name if line is a simple assignment from source."""
        escaped = re.escape(source)
        pattern = re.compile(
            r"^[ \t]*([a-zA-Z_]\w*)(?:\s*:\s*\S+)?\s*=\s*.*?" + escaped
        )
        m = pattern.match(line)
        if m:
            return m.group(1)
        return None

    def _iter_code_files(self) -> Generator[Path, None, None]:
        """Yield Path objects for all code files in repo, skipping ignored dirs."""
        for path in self.repo_path.rglob("*"):
            if (
                path.is_file()
                and path.suffix in _SCAN_EXTENSIONS
                and not any(part in _SKIP_DIRS for part in path.parts)
            ):
                yield path
