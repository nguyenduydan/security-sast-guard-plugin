"""CallGraphBuilder: grep-based cross-file call graph for taint analysis."""

import re
from collections import deque
from pathlib import Path

from .models import CallChain, TraceStep

# Patterns to detect import statements by language
_IMPORT_PATTERNS = [
    # Python: from X import Y  /  import X
    re.compile(r"^\s*from\s+([\w./]+)\s+import"),
    re.compile(r"^\s*import\s+([\w./]+)"),
    # JS/TS: import X from 'Y'  /  require('Y')
    re.compile(r"""(?:import|require)\s*\(?\s*['"]([^'"]+)['"]"""),
    # C#: using Namespace.Sub;
    re.compile(r"^\s*using\s+([\w.]+)\s*;"),
    # Java: import a.b.c;
    re.compile(r"^\s*import\s+([\w.]+)\s*;"),
]

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


class CallGraphBuilder:
    """Builds a cross-file import graph and traces call chains to sinks."""

    def __init__(self, repo_path: str) -> None:
        self.repo_path = Path(repo_path).resolve()

    def build_import_graph(self, entry_files: list[str]) -> dict[str, list[str]]:
        """BFS from entry_files, following import declarations.

        Returns dict: { relative_file_path: [list of imported relative paths] }
        """
        graph: dict[str, list[str]] = {}
        visited: set[str] = set()
        queue: deque[str] = deque()

        for ef in entry_files:
            rel = self._normalize(ef)
            queue.append(rel)

        while queue:
            current = queue.popleft()
            if current in visited:
                continue
            visited.add(current)
            deps = self._extract_imports(current)
            graph[current] = deps
            for dep in deps:
                if dep not in visited:
                    queue.append(dep)

        return graph

    # pylint: disable=too-many-locals
    def trace_to_sinks(
        self, entry_file: str, entry_symbol: str, sinks: list[str]
    ) -> list[CallChain]:
        """BFS from entry_file following imports, searching for sink calls
        that contain the entry_symbol.

        Returns a list of CallChain objects for each sink hit found.
        """
        entry_rel = self._normalize(entry_file)
        import_graph = self.build_import_graph([entry_rel])
        chains: list[CallChain] = []

        visited: set[str] = set()
        queue: deque[tuple[str, list[TraceStep]]] = deque()
        queue.append((entry_rel, []))

        while queue:
            current_file, path_so_far = queue.popleft()
            if current_file in visited:
                continue
            visited.add(current_file)

            abs_path = self.repo_path / current_file
            if not abs_path.exists():
                continue

            try:
                lines = abs_path.read_text(
                    encoding="utf-8", errors="ignore"
                ).splitlines()
            except OSError:
                continue

            for lineno, line in enumerate(lines, start=1):
                for sink in sinks:
                    if sink in line and (
                        entry_symbol in line or current_file != entry_rel
                    ):
                        steps = [
                            *path_so_far,
                            TraceStep(
                                file=current_file,
                                line=lineno,
                                symbol=f"{sink}({entry_symbol})",
                                step_type="sink",
                            ),
                        ]
                        chains.append(
                            CallChain(
                                entry_fn=entry_file,
                                steps=steps,
                                terminal_sink=sink,
                            )
                        )

            # Follow imports
            for dep in import_graph.get(current_file, []):
                if dep not in visited:
                    hop = TraceStep(
                        file=current_file,
                        line=0,
                        symbol=f"import {dep}",
                        step_type="intermediate_usage",
                    )
                    queue.append((dep, [*path_so_far, hop]))

        return chains

    def _normalize(self, file_path: str) -> str:
        """Return file_path relative to repo_path."""
        p = Path(file_path)
        if p.is_absolute():
            try:
                return str(p.relative_to(self.repo_path))
            except ValueError:
                return str(p)
        return file_path

    def _extract_imports(self, rel_path: str) -> list[str]:
        """Grep file for import statements and resolve to relative repo paths."""
        abs_path = self.repo_path / rel_path
        if not abs_path.exists():
            return []
        try:
            content = abs_path.read_text(encoding="utf-8", errors="ignore")
        except OSError:
            return []

        results: list[str] = []
        for line in content.splitlines():
            for pattern in _IMPORT_PATTERNS:
                m = pattern.search(line)
                if m:
                    module_ref = m.group(1)
                    resolved = self._resolve_module(rel_path, module_ref)
                    if resolved:
                        results.append(resolved)
                    break  # one pattern per line
        return results

    def _resolve_module(self, from_file: str, module_ref: str) -> str | None:
        """Try to resolve a module reference to a repo-relative file path."""
        # Convert dotted Python paths to slashes
        candidate_base = module_ref.replace(".", "/").replace("-", "_")
        from_dir = Path(from_file).parent

        for ext in _SCAN_EXTENSIONS:
            # Relative to the importing file's directory
            rel_candidate = str(from_dir / (candidate_base + ext))
            if (self.repo_path / rel_candidate).exists():
                return rel_candidate
            # Relative to repo root
            root_candidate = candidate_base + ext
            if (self.repo_path / root_candidate).exists():
                return root_candidate
        return None
