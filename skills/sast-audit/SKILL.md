---
name: sast-audit
description: SAST security audit — file | codebase | api | web, with level lite | full | ultra
---

Run SAST security audit on demand using the active audit level stored in profile configuration (`profile.json`).

Syntax: `/sast-audit [type] [path]`

Interactive Grill UI Workflow:
- If executed without arguments, immediately prompt the user using the interactive `ask_question` modal tool ("Grill UI") with options:
  1. `(Recommended) diff`: Incremental scan (only git changed/staged files)
  2. `file`: Single file scan (prompt user to select or provide target file path)
  3. `codebase`: Full recursive scan of every file in the codebase
  4. `api`: OWASP API 2023 security rules
  5. `web`: Web App security rules

Execution:
- The active audit level (`lite`, `full`, `ultra`) MUST be retrieved from `profile.json` / `sast_get_status` rather than asking the user again.
- `file` / `diff` type: Call Native MCP tool `sast_scan_file` or `sast_scan_diff` when available. If fallback to `run_command` is required, specify `toolAction="Scanning File Security"` and `toolSummary="SAST Security Audit"`.
- `codebase` / large audit: Run silently as background task (`run_command` async with `toolAction="Auditing Codebase Security"` and `toolSummary="Codebase SAST Audit"`), inform task ID, monitor status, and output concise report upon completion.

