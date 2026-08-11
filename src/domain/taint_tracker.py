"""TaintTracker: traces tainted symbols from source assignments to sink call sites."""

from collections.abc import Generator
from pathlib import Path

from .models import SymbolMap, TaintFinding, TraceStep

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


class TaintTracker:
    """Traces tainted symbols from SymbolMap to sink call sites in the repo."""

    def __init__(self, repo_path: str) -> None:
        self.repo_path = Path(repo_path).resolve()

    def trace(
        self,
        symbol_map: SymbolMap,
        rule_id: str,
        source_pattern: str,
        sinks: list[str],
    ) -> list[TaintFinding]:
        """For each symbol in symbol_map, grep repo for sink usage lines.

        A match requires BOTH the sink keyword AND the tainted symbol to appear
        in the same line (simple heuristic — no scope analysis at this phase).
        """
        findings: list[TaintFinding] = []
        for symbol, source_locs in symbol_map.items():
            for source_file, source_line in source_locs:
                sink_hits = self._find_sink_hits(symbol, sinks)
                for sink_file, sink_line, sink_pattern in sink_hits:
                    trace = [
                        TraceStep(
                            file=source_file,
                            line=source_line,
                            symbol=symbol,
                            step_type="source_assignment",
                        ),
                        TraceStep(
                            file=sink_file,
                            line=sink_line,
                            symbol=f"{sink_pattern}({symbol})",
                            step_type="sink",
                        ),
                    ]
                    findings.append(
                        TaintFinding(
                            rule_id=rule_id,
                            source_file=source_file,
                            source_line=source_line,
                            source_pattern=source_pattern,
                            sink_file=sink_file,
                            sink_line=sink_line,
                            sink_pattern=sink_pattern,
                            trace_path=trace,
                            confidence=0.5,  # Phase 1 baseline; Phase 2 may update
                        )
                    )
        return findings

    def _find_sink_hits(
        self, symbol: str, sinks: list[str]
    ) -> list[tuple[str, int, str]]:
        """Search all code files for lines containing BOTH a sink and the symbol."""
        hits: list[tuple[str, int, str]] = []
        for file_path in self._iter_code_files():
            rel = str(file_path.relative_to(self.repo_path))
            try:
                lines = file_path.read_text(
                    encoding="utf-8", errors="ignore"
                ).splitlines()
            except OSError:
                continue
            for lineno, line in enumerate(lines, start=1):
                for sink in sinks:
                    if sink in line and symbol in line:
                        hits.append((rel, lineno, sink))
        return hits

    def _iter_code_files(self) -> Generator[Path, None, None]:
        for path in self.repo_path.rglob("*"):
            if (
                path.is_file()
                and path.suffix in _SCAN_EXTENSIONS
                and not any(part in _SKIP_DIRS for part in path.parts)
            ):
                yield path
