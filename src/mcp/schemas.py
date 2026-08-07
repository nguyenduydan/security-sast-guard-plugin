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
    {
        "name": "sast_init",
        "description": (
            "Initialize project-local SAST Security profile configuration "
            "(.sast/profile.json)."
        ),
        "inputSchema": {
            "type": "object",
            "properties": {},
        },
    },
    {
        "name": "sast_sync_rules",
        "description": "Sync or add custom SAST rules to project profile.",
        "inputSchema": {
            "type": "object",
            "properties": {
                "rules_dir": {
                    "type": "string",
                    "description": "Optional rules directory path.",
                }
            },
        },
    },
    {
        "name": "sast_get_help",
        "description": "Get SAST Guard help and usage documentation.",
        "inputSchema": {
            "type": "object",
            "properties": {},
        },
    },
    {
        "name": "sast_set_mode",
        "description": "Set active SAST Guard operation mode (strict | draft).",
        "inputSchema": {
            "type": "object",
            "properties": {
                "mode": {
                    "type": "string",
                    "enum": ["strict", "draft"],
                    "description": "Desired operation mode.",
                }
            },
            "required": ["mode"],
        },
    },
]
