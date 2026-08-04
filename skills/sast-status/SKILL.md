---
name: sast-status
description: View security profile, rule counts, deny/confirm patterns, and plugin status
---

Execute EXACTLY ONE tool call: `run_command` with `python "${PLUGIN_ROOT}/control_plane.py" status` (or `python -m src.cli.dispatcher status` if appropriate).
Directly print the exact output of this command to the user.
CRITICAL: Do NOT use `list_dir`, `view_file`, or any other tools to explore files. Do NOT attempt to read `profile.json` or any python files. One-shot execution only!
