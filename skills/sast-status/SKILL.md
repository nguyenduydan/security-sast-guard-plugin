---
name: sast-status
description: View security profile, rule counts, deny/confirm patterns, and plugin status
---

1. Call Native MCP tool `sast_get_status` (or `call_mcp_tool`) when available.
2. If MCP tools are unavailable, fallback to running `sast status` or `python control_plane.py status`.
3. Present a clean, concise summary of profile status, rule counts, and firewall overlay patterns to the user.

