---
name: sast-firewall
description: Check shell command safety — ALLOW | CONFIRM | DENY
---

Run the Security SAST Guard firewall check on the command provided in the user's arguments. Execute: python "${PLUGIN_ROOT}/control_plane.py" firewall <command>. Report the verdict clearly: ALLOW (safe to proceed), CONFIRM (dangerous — ask user first), or DENY (blocked — do not run). If DENY or CONFIRM, explain which security pattern matched and why it is dangerous. Never bypass a DENY verdict.
