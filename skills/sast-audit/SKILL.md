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
- `file` / `diff` type: Run synchronously via tool call, hide python command, report finding summary.
- `codebase` / large audit: Run silently as background task (`run_command` async), inform task ID, monitor status, and output concise report upon completion.
