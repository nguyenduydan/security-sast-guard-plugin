---
name: sast-mode
description: Set or view SAST operation mode (strict | draft)
---

Set or view the active SAST Guard operation mode in profile configuration.

Syntax: `/sast-mode [strict|draft]`
Modes:
- `strict`: Enforce all security rules strictly (default).
- `draft`: Auto-allow low/medium severity findings during rapid development.

Execution:
- If executed with argument (`strict` or `draft`), call Native MCP tool `sast_set_mode(mode="...")` when available (or fallback to `sast mode <mode>`), then confirm in 1 concise line.
- If executed without args, call Native MCP tool `sast_get_status` (or fallback to `sast mode`) to display the current active mode.
