---
name: sast-help
description: Quick reference for security-sast-guard levels, commands, and options
---

Show the security-sast-guard quick reference. One shot, change nothing. Commands: /sast-firewall <command> (check if a terminal command is safe — ALLOW/CONFIRM/DENY). /sast-audit <type> <path> [--level lite|full|ultra] where type is file|codebase|api|web — lite scans Critical only, full scans OWASP Top10+API+Web (default), ultra scans all including CWE-SANS Top25 and NIST 800-53; api type filters OWASP API 2023 rules only, web type filters Web App Specific rules only. /sast-rules add <file.md> to convert and merge one Markdown rule file, or /sast-rules sync <dir> to sync an entire rules directory (e.g., from mcp-agent-audit). /sast-status to view active profile, rule counts, deny/confirm pattern totals. /sast-help to show this card. If nothing found: 'Clean. No vulnerabilities detected.'
