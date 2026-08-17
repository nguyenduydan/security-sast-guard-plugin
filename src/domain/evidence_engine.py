"""EvidenceEngine: Constructs EvidenceGraph and performs Program Slicing."""

from collections import deque
from dataclasses import dataclass
from typing import Any, Literal

# Type for node classification in evidence graphs
NodeType = Literal["source", "propagation", "sanitizer", "sink"]


_C_BLOCK_START: str = "/" + "*"


@dataclass
class EvidenceNode:
    """Represents a single step or location in an evidence dataflow path."""

    node_id: str
    node_type: NodeType
    file_path: str
    line_number: int
    code_snippet: str
    symbol: str


@dataclass
class EvidenceGraph:
    """Represents the complete evidence graph and program slice for a finding."""

    finding_id: str
    nodes: list[EvidenceNode]
    edges: list[tuple[str, str]]
    program_slice: list[str]
    is_complete_path: bool


class EvidenceEngine:
    """Engine for building evidence graphs and extracting program slices."""

    def is_complete_path(
        self,
        nodes: list[EvidenceNode],
        edges: list[tuple[str, str]],
    ) -> bool:
        """Determine if a directed path exists from any source to any sink.

        Args:
            nodes: List of EvidenceNode items in the graph.
            edges: Directed edges represented as (from_node_id, to_node_id).

        Returns:
            True if at least one source node reaches a sink node via edges.
        """
        source_ids = {node.node_id for node in nodes if node.node_type == "source"}
        sink_ids = {node.node_id for node in nodes if node.node_type == "sink"}

        if not source_ids or not sink_ids:
            return False

        adj: dict[str, list[str]] = {node.node_id: [] for node in nodes}
        for u_node, v_node in edges:
            if u_node in adj:
                adj[u_node].append(v_node)

        queue = deque(source_ids)
        visited = set(source_ids)

        while queue:
            curr = queue.popleft()
            if curr in sink_ids:
                return True
            for neighbor in adj.get(curr, []):
                if neighbor not in visited:
                    visited.add(neighbor)
                    queue.append(neighbor)

        return False

    def slice_program(
        self,
        source_code: str,
        nodes: list[EvidenceNode],
        edges: list[tuple[str, str]] | None = None,
    ) -> list[str]:
        """Perform program slicing by extracting code lines relevant to dataflow.

        Args:
            source_code: Full input source code string.
            nodes: Relevant evidence nodes participating in dataflow.
            edges: Optional graph edges (not strictly required if nodes are present).

        Returns:
            Extracted lines of relevant code statements in format 'L<num>: <code_line>'.
        """
        _ = edges
        if not source_code.strip():
            return [
                f"L{node.line_number}: {node.code_snippet.strip()}" for node in nodes
            ]

        lines = source_code.splitlines()
        target_lines: set[int] = set()

        # Gather line numbers directly associated with nodes
        for node in nodes:
            if 1 <= node.line_number <= len(lines):
                target_lines.add(node.line_number)

        # Collect symbols involved in dataflow
        symbols = {node.symbol.strip() for node in nodes if node.symbol.strip()}

        # Scan lines to pick up intermediate propagation statements referencing symbols
        if symbols:
            for idx, line in enumerate(lines, start=1):
                stripped = line.strip()
                if not stripped or stripped.startswith(("#", "//", _C_BLOCK_START, "*")):
                    continue
                if any(sym in line for sym in symbols):
                    target_lines.add(idx)

        sorted_line_numbers = sorted(target_lines)
        sliced_statements: list[str] = []
        for line_num in sorted_line_numbers:
            if 1 <= line_num <= len(lines):
                sliced_statements.append(f"L{line_num}: {lines[line_num - 1].strip()}")

        return sliced_statements

    def build_graph(
        self,
        finding_id: str,
        nodes: list[EvidenceNode],
        edges: list[tuple[str, str]],
        source_code_map: dict[str, str] | None = None,
    ) -> EvidenceGraph:
        """Construct an EvidenceGraph for a candidate finding.

        Args:
            finding_id: Identifier of the candidate finding.
            nodes: List of EvidenceNode items.
            edges: Directed edges representing dataflow hops.
            source_code_map: Optional map of file_path -> full source code string.

        Returns:
            Constructed EvidenceGraph with slice and path completeness.
        """
        complete = self.is_complete_path(nodes, edges)

        # Build program slice across files or from node code snippets
        if source_code_map and nodes:
            slice_lines: list[str] = []
            for file_path, code_text in source_code_map.items():
                file_nodes = [node for node in nodes if node.file_path == file_path]
                if file_nodes:
                    file_slice = self.slice_program(code_text, file_nodes, edges)
                    slice_lines.extend(file_slice)
            program_slice = (
                slice_lines
                if slice_lines
                else [f"L{n.line_number}: {n.code_snippet.strip()}" for n in nodes]
            )
        else:
            program_slice = [
                f"L{n.line_number}: {n.code_snippet.strip()}" for n in nodes
            ]

        return EvidenceGraph(
            finding_id=finding_id,
            nodes=nodes,
            edges=edges,
            program_slice=program_slice,
            is_complete_path=complete,
        )

    def build_from_trace(
        self,
        finding_id: str,
        trace_steps: list[dict[str, Any]],
        source_code_map: dict[str, str] | None = None,
    ) -> EvidenceGraph:
        """Construct an EvidenceGraph from raw trace step dictionaries.

        Args:
            finding_id: Identifier of the finding.
            trace_steps: List of trace step dicts containing file, line, symbol,
                and step_type.
            source_code_map: Optional source code mapping.

        Returns:
            EvidenceGraph constructed from trace steps.
        """
        nodes: list[EvidenceNode] = []
        edges: list[tuple[str, str]] = []

        for idx, step in enumerate(trace_steps):
            node_id = f"node_{idx + 1}"
            raw_type = step.get("step_type", "propagation")
            if raw_type in ("source_assignment", "source"):
                node_type: NodeType = "source"
            elif raw_type == "sink":
                node_type = "sink"
            elif raw_type == "sanitizer":
                node_type = "sanitizer"
            else:
                node_type = "propagation"

            node = EvidenceNode(
                node_id=node_id,
                node_type=node_type,
                file_path=str(step.get("file", step.get("file_path", ""))),
                line_number=int(step.get("line", step.get("line_number", 0))),
                code_snippet=str(step.get("code_snippet", step.get("symbol", ""))),
                symbol=str(step.get("symbol", "")),
            )
            nodes.append(node)

            if idx > 0:
                prev_id = f"node_{idx}"
                edges.append((prev_id, node_id))

        return self.build_graph(finding_id, nodes, edges, source_code_map)
