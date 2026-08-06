---
name: sast-rules
description: Manage SAST rules — add a single .md file or sync an entire rules directory
---

Convert Markdown rules to `sast_rules.json`.

Syntax: `/sast-rules add <file.md>` | `/sast-rules sync <dir>`

Execution:
- If executed with `add <file.md>`, run `run_command` with `python "${PLUGIN_ROOT}/scripts/md_to_json.py" --input "<file.md>"`.
- If executed with `sync <dir>`, run `run_command` with `python "${PLUGIN_ROOT}/scripts/md_to_json.py" --dir "<dir>"`.
- If executed without arguments, run `run_command` with `python "${PLUGIN_ROOT}/scripts/md_to_json.py"`.
Directly report summary output. Warn if missing ```regex``` blocks.
