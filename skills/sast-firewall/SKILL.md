---
name: sast-firewall
description: Check shell command safety — ALLOW | CONFIRM | DENY
---

1. Call Native MCP tool `sast_check_command(command="...")` when available.
2. If MCP tools are unavailable, fallback to `sast firewall <command>` or `python "${PLUGIN_ROOT}/control_plane.py" firewall <command>`.
3. Report the verdict clearly: ALLOW (safe to proceed), CONFIRM (dangerous — ask user first), or DENY (blocked — do not run). If DENY or CONFIRM, explain which pattern matched and why it is dangerous.

