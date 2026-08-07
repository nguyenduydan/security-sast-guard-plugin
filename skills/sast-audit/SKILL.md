---
name: sast-audit
description: SAST security audit — file | codebase | api | web, with level lite | full | ultra
---

Run SAST security audit on demand using active audit level from memory.

Syntax: `/sast-audit <type> <path>`
Types:
- `file`: Single file audit.
- `diff`: Incremental scan (only git changed/staged files).
- `codebase`: Full recursive scan of every file in the codebase (excluding built-in ignored dirs).
- `api`: OWASP API 2023 rules.
- `web`: Web App security rules.

Execution:
- `file` / `diff` type: Call Native MCP tool `sast_scan_file` when available. If fallback to `run_command` is required, MUST specify descriptive `toolAction="Scanning File Security"` and `toolSummary="SAST Security Audit"` for clean UI rendering.
- `codebase` / large audit: Run silently as background task (`run_command` async with descriptive `toolAction="Auditing Codebase Security"` and `toolSummary="Codebase SAST Audit"`), inform task ID, monitor status, and output concise report upon completion.
