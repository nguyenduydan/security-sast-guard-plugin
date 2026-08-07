---
name: sast-audit-level
description: Set or view SAST audit level (lite | full | ultra)
---

Set or view the active SAST audit level in profile configuration (`profile.json`).

Syntax: `/sast-audit-level [lite|full|ultra]`

Interactive Grill UI Workflow:
- If executed without arguments, immediately prompt the user using the interactive `ask_question` modal tool ("Grill UI") with options:
  1. `(Recommended) full`: OWASP Top 10 + API + Web App rules
  2. `lite`: Critical security vulnerabilities only (Fastest)
  3. `ultra`: All rules + CWE Top 25 + NIST 800-53 controls (Deepest audit)

Execution:
- If executed with argument or after user selects via `ask_question` modal, call Native MCP tool `sast_set_level(level="...")` when available (or fallback to `sast level <level>`), then confirm in 1 concise line.
- If user chooses to only view current status, call Native MCP tool `sast_get_status` (or `sast level`) to display active level.


