---
name: sast-status
description: View security profile, rule counts, deny/confirm patterns, and plugin status
---

Run: python "${PLUGIN_ROOT}/control_plane.py" status. Display a clean status card: plugin name & version, default audit level, available audit levels (off/lite/full/ultra), available audit types (file/codebase/api/web), total SAST rules loaded, total deny patterns (firewall blocked), total confirm patterns (require user approval). Also show the rule breakdown by category and severity distribution.
