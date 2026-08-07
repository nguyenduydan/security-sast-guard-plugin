---
name: sast-audit-level
description: Set or view SAST audit level (lite | full | ultra)
---

Set or view the active SAST audit level in profile configuration.

Syntax: `/sast-audit-level [lite|full|ultra]`
Levels: `lite` (Critical only), `full` (OWASP Top10/API/Web), `ultra` (All + CWE Top25/NIST).

Execution:
- If executed with argument (`lite`, `full`, or `ultra`), call Native MCP tool `sast_set_level(level="...")` when available (or fallback to `sast level <level>`), then confirm in 1 concise line.
- If executed without args, call Native MCP tool `sast_get_status` (or fallback to `sast level`) to display the current active level.

