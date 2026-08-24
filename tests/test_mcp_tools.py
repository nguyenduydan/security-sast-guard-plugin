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
    assert len(tools) >= 8


def test_mcp_tool_handlers_new_tools(tmp_path) -> None:
    handlers = MCPToolHandlers()
    res_init = handlers.handle_sast_init()
    assert res_init["status"] == "success"

    out_file = str(tmp_path / "synced_rules.json")
    res_sync = handlers.handle_sast_sync_rules(output_file=out_file)
    assert res_sync["status"] == "success"
    assert res_sync["rule_count"] >= 1
    assert "target_file" in res_sync

    res_sync_invalid = handlers.handle_sast_sync_rules("nonexistent_rules_dir_xyz")
    assert res_sync_invalid["status"] == "error"

    res_help = handlers.handle_sast_get_help()
    assert res_help["status"] == "success"
    assert len(res_help["skills"]) > 0

    res_mode = handlers.handle_sast_set_mode("draft")
    assert res_mode["status"] == "success"
    assert res_mode["active_mode"] == "draft"

    handlers.handle_sast_set_mode("strict")
