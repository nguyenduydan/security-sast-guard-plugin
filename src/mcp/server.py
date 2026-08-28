"""Stdio JSON-RPC MCP Server implementation."""

from __future__ import annotations

import json
import sys
from typing import Any

from src.infrastructure.version_loader import get_plugin_version
from src.mcp.schemas import TOOLS_SCHEMAS
from src.mcp.tools import MCPToolHandlers


class MCPServer:
    """Stdio JSON-RPC MCP Server for Antigravity 2.0."""

    def __init__(self) -> None:
        self.handlers = MCPToolHandlers()

    def run(self) -> None:
        """Run standard I/O JSON-RPC loop."""
        for line in sys.stdin:
            line = line.strip()
            if not line:
                continue

            try:
                request = json.loads(line)
                response = self.handle_request(request)
                if response is not None:
                    sys.stdout.write(json.dumps(response) + "\n")
                    sys.stdout.flush()
            except Exception as err:  # pylint: disable=broad-exception-caught
                err_resp = {
                    "jsonrpc": "2.0",
                    "id": None,
                    "error": {"code": -32603, "message": str(err)},
                }
                sys.stdout.write(json.dumps(err_resp) + "\n")
                sys.stdout.flush()

    def _get_version(self) -> str:
        """Get plugin version dynamically from version loader."""
        return get_plugin_version()

    def handle_request(self, req: dict[str, Any]) -> dict[str, Any] | None:
        """Process incoming JSON-RPC request.

        JSON-RPC 2.0 distinguishes requests (have 'id') from notifications
        (no 'id' key at all). Notifications MUST NOT receive a response —
        sending one corrupts the stdio stream and breaks subsequent calls
        such as tools/list.
        """
        # Notifications have no 'id' key (absent, not null) — silently ignore
        if "id" not in req:
            return None

        req_id = req.get("id")
        method = req.get("method")
        params = req.get("params", {})

        if method == "initialize":
            return {
                "jsonrpc": "2.0",
                "id": req_id,
                "result": {
                    "protocolVersion": "2024-11-05",
                    "capabilities": {"tools": {}},
                    "serverInfo": {
                        "name": "security-sast-guard",
                        "version": self._get_version(),
                    },
                },
            }

        if method == "tools/list":
            return {
                "jsonrpc": "2.0",
                "id": req_id,
                "result": {"tools": TOOLS_SCHEMAS},
            }

        if method == "tools/call":
            tool_name = params.get("name")
            arguments = params.get("arguments", {})
            result = self.execute_tool(tool_name, arguments)
            return {
                "jsonrpc": "2.0",
                "id": req_id,
                "result": {
                    "content": [{"type": "text", "text": json.dumps(result, indent=2)}]
                },
            }

        return {
            "jsonrpc": "2.0",
            "id": req_id,
            "error": {"code": -32601, "message": f"Method '{method}' not found"},
        }

    # pylint: disable=too-many-return-statements,too-many-branches
    def execute_tool(
        self, tool_name: str | None, args: dict[str, Any]
    ) -> dict[str, Any]:
        """Dispatch tool name to handler function."""
        if tool_name == "sast_scan_file":
            return self.handlers.handle_sast_scan_file(args.get("file_path", "."))
        if tool_name == "sast_scan_diff":
            return self.handlers.handle_sast_scan_diff()
        if tool_name == "sast_check_command":
            return self.handlers.handle_sast_check_command(args.get("command", ""))
        if tool_name == "sast_get_status":
            return self.handlers.handle_sast_get_status()
        if tool_name == "sast_set_level":
            return self.handlers.handle_sast_set_level(args.get("level", "full"))
        if tool_name == "sast_init":
            return self.handlers.handle_sast_init()
        if tool_name == "sast_sync_rules":
            return self.handlers.handle_sast_sync_rules(args.get("rules_dir", ""))
        if tool_name == "sast_get_help":
            return self.handlers.handle_sast_get_help()
        if tool_name == "sast_get_dataflow_path":
            return self.handlers.handle_sast_get_dataflow_path(
                args.get("source_pattern", ""),
                args.get("sink_pattern", ""),
                args.get("repo_path", "."),
            )
        if tool_name == "sast_get_taint_context":
            return self.handlers.handle_sast_get_taint_context(
                args.get("file_path", ""),
                args.get("line_number", 0),
                args.get("context_lines", 10),
            )
        if tool_name == "sast_set_mode":
            return self.handlers.handle_sast_set_mode(args.get("mode", "strict"))
        if tool_name == "sast_generate_report":
            return self.handlers.handle_sast_generate_report(
                args.get("findings", []),
                args.get("target_path", "."),
                args.get("ai_analysis", ""),
            )
        if tool_name == "sast_get_taint_evidence":
            return self.handlers.handle_sast_get_taint_evidence(
                args.get("file_path", ""),
                args.get("line_number", 0),
                args.get("slice_window", 7),
            )

        return {"error": f"Unknown tool name: {tool_name}"}


if __name__ == "__main__":
    server = MCPServer()
    server.run()
