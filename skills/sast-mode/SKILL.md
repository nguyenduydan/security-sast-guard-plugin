---
name: sast-mode
description: Set or view SAST operation mode (strict | draft)
---

Set or view the active SAST Guard operation mode in profile configuration (`profile.json`).

Syntax: `/sast-mode [strict|draft]`

Interactive Grill UI Workflow:
- If executed without arguments, immediately prompt the user using the interactive `ask_question` modal tool ("Grill UI") with options:
  1. `(Recommended) strict`: Enforce all security rules & command blocks strictly
  2. `draft`: Auto-allow low/medium severity findings during rapid development

Execution:
- If executed with argument or after user selects via `ask_question` modal, call Native MCP tool `sast_set_mode(mode="...")` when available (or fallback to `sast mode <mode>`), then confirm in 1 concise line.
- If user chooses to only view current status, call Native MCP tool `sast_get_status` (or `sast mode`) to display active mode.

