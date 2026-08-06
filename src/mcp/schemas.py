"""MCP tool input and output schemas."""

from __future__ import annotations

from typing import Any

TOOLS_SCHEMAS: list[dict[str, Any]] = [
    {
        "name": "sast_scan_file",
        "description": "Run static security audit on a single source file.",
        "inputSchema": {
            "type": "object",
            "properties": {
                "file_path": {
                    "type": "string",
                    "description": "Absolute or relative path to target file.",
                }
            },
            "required": ["file_path"],
        },
    },
    {
        "name": "sast_scan_diff",
        "description": "Run static security audit on modified git files.",
        "inputSchema": {
            "type": "object",
            "properties": {},
        },
    },
    {
        "name": "sast_check_command",
        "description": "Test command safety against Firewall overlay rules.",
        "inputSchema": {
            "type": "object",
            "properties": {
                "command": {
                    "type": "string",
                    "description": "Shell command string to evaluate.",
                }
            },
            "required": ["command"],
        },
    },
    {
        "name": "sast_get_status",
        "description": "Get current security profile status and rule counts.",
        "inputSchema": {
            "type": "object",
            "properties": {},
        },
    },
    {
        "name": "sast_set_level",
        "description": "Set active SAST audit strictness level (lite | full | ultra).",
        "inputSchema": {
            "type": "object",
            "properties": {
                "level": {
                    "type": "string",
                    "enum": ["lite", "full", "ultra"],
                    "description": "Desired strictness level.",
                }
            },
            "required": ["level"],
        },
    },
]
