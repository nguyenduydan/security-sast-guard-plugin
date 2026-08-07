---
name: sast-help
description: Quick reference for security-sast-guard levels, commands, and options
---

Show the security-sast-guard quick reference. Running slash commands without arguments triggers the interactive Grill UI modal (`ask_question`). Commands:
- `/sast-audit [type] [path]`: Triggers static vulnerability audit. If parameters are omitted, presents Grill UI modal to select type (diff, file, codebase, api, web). Uses active audit level from profile.json.
- `/sast-status`: Displays active profile, tool version, tech stack, operation mode, and rule counts.
- `/sast-init`: Initializes project-local `.sast/profile.json` configuration.
- `/sast-mode [strict|draft]`: Switches operation mode. If parameter is omitted, presents Grill UI modal.
- `/sast-audit-level [lite|full|ultra]`: Sets active audit strictness level. If parameter is omitted, presents Grill UI modal.
- `/sast-rules [sync|add|status]`: Manages SAST rules. If parameter is omitted, presents Grill UI modal.
- `/sast-help`: Displays this reference card.


