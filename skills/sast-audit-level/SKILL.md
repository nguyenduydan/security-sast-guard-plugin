---
name: sast-audit-level
description: Set or view SAST audit level (lite | full | ultra)
---

Set or view the active SAST audit level in AI memory context without file edits.

Syntax: `/sast-audit-level [lite|full|ultra]`
Levels: `lite` (Critical only), `full` (OWASP Top10/API/Web), `ultra` (All + CWE Top25/NIST).

Execution: Switch level directly in AI memory context and confirm in 1 concise line. If executed without args, display current level.
