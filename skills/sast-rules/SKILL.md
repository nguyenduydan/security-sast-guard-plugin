---
name: sast-rules
description: Manage SAST rules — add a single .md file or sync an entire rules directory
---

Convert Markdown rules to `sast_rules.json`.

Syntax: `/sast-rules add <file.md>` | `/sast-rules sync <dir>`

Execution: Run `md_to_json.py` (`--input` or `--dir`) silently via tool call. Do not display python command string or create async background task. Directly report summary (rules added/updated/skipped, total count). Warn if missing ```regex``` blocks.
