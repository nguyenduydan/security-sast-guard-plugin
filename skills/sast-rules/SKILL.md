---
name: sast-rules
description: Manage SAST rules — add a single .md file or sync an entire rules directory
---

Convert Markdown rules to `sast_rules.json` or manage active SAST rule definitions.

Syntax: `/sast-rules [add <file.md> | sync <dir> | status]`

Interactive Grill UI Workflow:
- If executed without arguments, immediately prompt the user using the interactive `ask_question` modal tool ("Grill UI") with options:
  1. `(Recommended) sync`: Sync and convert all Markdown rules in the rules directory
  2. `add`: Convert and add a specific `.md` rule file (prompt for file path)
  3. `status`: Check rule count and active rule status

Execution:
- `add <file.md>`: Run `run_command` with `python "${PLUGIN_ROOT}/scripts/md_to_json.py" --input "<file.md>"`.
- `sync <dir>`: Run `run_command` with `python "${PLUGIN_ROOT}/scripts/md_to_json.py" --dir "<dir>"`.
- Default sync: Run `run_command` with `python "${PLUGIN_ROOT}/scripts/md_to_json.py"`.
Directly report summary output. Warn if missing ```regex``` blocks.

