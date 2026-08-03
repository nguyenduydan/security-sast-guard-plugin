---
name: sast-audit
description: SAST security audit — file | codebase | api | web, with level lite | full | ultra
---

Run SAST security audit on demand using active audit level from memory.

Syntax: `/sast-audit <type> <path>`
Types: `file` (single file), `codebase` (entire tree), `api` (OWASP API 2023), `web` (Web App rules).

Execution:
- `file` type: Run synchronously via tool call, hide python command, report finding summary.
- `codebase` / large audit: Run silently as background task (`run_command` async), inform task ID, monitor status, and output concise report upon completion.
