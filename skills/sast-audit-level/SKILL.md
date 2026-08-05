---
name: sast-audit-level
description: Set or view SAST audit level (lite | full | ultra)
---

Set or view the active SAST audit level in profile configuration.

Syntax: `/sast-audit-level [lite|full|ultra]`
Levels: `lite` (Critical only), `full` (OWASP Top10/API/Web), `ultra` (All + CWE Top25/NIST).

Execution:
If executed with argument (`lite`, `full`, or `ultra`), run `run_command` with `python "${PLUGIN_ROOT}/control_plane.py" level <level>` to update profile.json persistently, then confirm in 1 concise line.
If executed without args, run `run_command` with `python "${PLUGIN_ROOT}/control_plane.py" level` to display the current active level.
