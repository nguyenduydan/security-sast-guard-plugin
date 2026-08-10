"""
CallGraphBuilder implementation for standalone import graph tracing.
"""

import re
from collections import deque
from dataclasses import dataclass
from pathlib import Path


@dataclass
class CallEdge:
    """Represents a call from a caller function/file to a callee function/file."""

    caller_file: str
    caller_fn: str
    callee_file: str
    callee_fn: str


@dataclass
class CallChain:
    """Represents a trace from an entry point to a terminal sink."""

    entry_fn: str
    steps: list[CallEdge]
    terminal_sink: str


class CallGraphBuilder:
    """Builds an import graph and traces call chains to sinks."""

    def __init__(self, repo_path: str):
        self.repo_path = Path(repo_path)
        # Python: from X import Y, import X
        # JS/TS: import X from 'Y', require('Y')
        # C#: using X;
        # Java: import X;
        self.import_patterns = [
            re.compile(r"^\s*from\s+([a-zA-Z0-9_\.]+)\s+import", re.MULTILINE),
            re.compile(r"^\s*import\s+([a-zA-Z0-9_\.]+)", re.MULTILINE),
            re.compile(r'^\s*import\s+.*from\s+[\'"]([^\'"]+)[\'"]', re.MULTILINE),
            re.compile(r'^\s*require\([\'"]([^\'"]+)[\'"]\)', re.MULTILINE),
            re.compile(r"^\s*using\s+([a-zA-Z0-9_\.]+)\s*;", re.MULTILINE),
            re.compile(r"^\s*import\s+([a-zA-Z0-9_\.]+)\s*;", re.MULTILINE),
        ]

    def _resolve_path(self, current_file: Path, imported_module: str) -> Path:
        """Attempt to resolve an imported module name to a file path."""
        if imported_module.startswith("./") or imported_module.startswith("../"):
            potential = (current_file.parent / imported_module).resolve()
            for ext in [".js", ".ts", ".jsx", ".tsx"]:
                if potential.with_suffix(ext).exists():
                    return potential.with_suffix(ext)
            return potential

        module_path = imported_module.replace(".", "/")

        potential = self.repo_path / module_path
        if potential.is_dir():
            for init_file in ["__init__.py", "index.js", "index.ts"]:
                if (potential / init_file).exists():
                    return potential / init_file

        for ext in [".py", ".java", ".cs", ".js", ".ts"]:
            if potential.with_suffix(ext).exists():
                return potential.with_suffix(ext)

        return self.repo_path / module_path

    def build_import_graph(self, entry_files: list[str]) -> dict[str, list[str]]:
        """Recursively trace and build the import graph starting from entry_files."""
        graph: dict[str, list[str]] = {}
        visited: set[str] = set()
        queue = deque([Path(self.repo_path / f).resolve() for f in entry_files])

        while queue:
            current = queue.popleft()
            try:
                current_str = str(current.relative_to(self.repo_path))
            except ValueError:
                current_str = str(current)

            if current_str in visited:
                continue
            visited.add(current_str)
            graph[current_str] = []

            if not current.exists() or not current.is_file():
                continue

            try:
                content = current.read_text(encoding="utf-8")
            except (OSError, ValueError):
                continue

            for pattern in self.import_patterns:
                for match in pattern.finditer(content):
                    module = match.group(1)
                    resolved = self._resolve_path(current, module)
                    try:
                        resolved_str = str(resolved.relative_to(self.repo_path))
                    except ValueError:
                        resolved_str = str(resolved)

                    if resolved_str not in graph[current_str]:
                        graph[current_str].append(resolved_str)

                    if resolved.exists() and resolved_str not in visited:
                        queue.append(resolved)

        return graph

    def trace_to_sinks(
        self, entry_file: str, entry_symbol: str, sinks: list[str]
    ) -> list[CallChain]:
        """BFS traverse import graph to find paths from entry_file to any sink."""
        graph = self.build_import_graph([entry_file])

        queue: deque[tuple[str, list[CallEdge]]] = deque([(entry_file, [])])
        visited: set[str] = {entry_file}

        chains = []

        while queue:
            current, path = queue.popleft()

            if any(sink in current for sink in sinks):
                chains.append(
                    CallChain(entry_fn=entry_symbol, steps=path, terminal_sink=current)
                )
                continue

            for neighbor in graph.get(current, []):
                if neighbor not in visited:
                    visited.add(neighbor)
                    new_path = list(path)
                    new_path.append(
                        CallEdge(
                            caller_file=current,
                            caller_fn="*",
                            callee_file=neighbor,
                            callee_fn="*",
                        )
                    )
                    queue.append((neighbor, new_path))

        return chains
