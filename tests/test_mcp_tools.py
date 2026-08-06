"""Unit tests for MCP server tools and request handlers."""

from __future__ import annotations

from src.mcp.server import MCPServer
from src.mcp.tools import MCPToolHandlers


def test_mcp_tool_handlers_status() -> None:
    handlers = MCPToolHandlers()
    res = handlers.handle_sast_get_status()
    assert res["status"] == "success"
    assert "audit_level" in res


def test_mcp_tool_handlers_check_command() -> None:
    handlers = MCPToolHandlers()
    res = handlers.handle_sast_check_command("git status")
    assert res["verdict"] in ["ALLOW", "CONFIRM", "DENY"]


def test_mcp_server_initialize() -> None:
    server = MCPServer()
    req = {"jsonrpc": "2.0", "id": 1, "method": "initialize"}
    resp = server.handle_request(req)
    assert resp is not None
    assert resp["result"]["serverInfo"]["name"] == "security-sast-guard"


def test_mcp_server_tools_list() -> None:
    server = MCPServer()
    req = {"jsonrpc": "2.0", "id": 2, "method": "tools/list"}
    resp = server.handle_request(req)
    assert resp is not None
    tools = resp["result"]["tools"]
    assert len(tools) >= 5
