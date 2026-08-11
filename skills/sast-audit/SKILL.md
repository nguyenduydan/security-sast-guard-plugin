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
- `file` / `diff` type: Call Native MCP tool `sast_scan_file` or `sast_scan_diff` when available. 
- `codebase` / large audit: Run silently as background task (`run_command` async with `toolAction="Auditing Codebase Security"` and `toolSummary="Codebase SAST Audit"`).
- **CRITICAL - AI Analysis Step**: After receiving the raw JSON findings from the scan tools, you (the AI Agent) MUST:
  1. Analyze the JSON findings intelligently.
  2. Write a concise, Markdown-formatted analysis (e.g., summarizing key risks, filtering obvious false positives, and proposing architectural mitigations).
  3. Call the `sast_generate_report` MCP tool, passing the original `findings`, `target_path`, and your `ai_analysis`. This will embed your analysis directly into the final Markdown report.
  4. Return the path of the generated report to the user.

