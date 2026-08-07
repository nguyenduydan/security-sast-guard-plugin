---
name: sast-init
description: Initialize project-local SAST Security profile configuration (.sast/profile.json)
---

# 🗂️ SAST Init Skill

Initializes project-level security profile configuration in the current working directory.

## Usage
1. Call Native MCP tool `sast_init` when available.
2. If MCP tools are unavailable, fallback to running `sast init` or `python control_plane.py init` (MUST specify descriptive `toolAction="Initializing SAST Profile"` and `toolSummary="SAST Profile Initialization"` for clean UI rendering).
3. Report the result clearly to the user.

