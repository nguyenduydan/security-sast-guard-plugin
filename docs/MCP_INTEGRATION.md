# 🔌 Antigravity 2.0 MCP Integration Guide

Security SAST Guard provides a native **Model Context Protocol (MCP)** server over stdio, enabling Antigravity 2.0 (IDE) and Gemini CLI to invoke security auditing and command verification as native agent tools.

---

## 🛠️ Registered MCP Tools

| MCP Tool Name | Arguments | Description |
| :--- | :--- | :--- |
| 🛡️ `sast_scan_file` | `file_path: string` | Scans a single target file for OWASP/CWE vulnerabilities. |
| 🔍 `sast_scan_diff` | *None* | Scans modified git files in current workspace. |
| 🧱 `sast_check_command` | `command: string` | Tests command safety against Firewall overlay rules (`ALLOW`, `CONFIRM`, `DENY`). |
| 📊 `sast_get_status` | *None* | Returns active strictness level, rule category counts, and profile integrity status. |
| 🎚️ `sast_set_level` | `level: string` | Sets active strictness level (`lite`, `full`, or `ultra`). |

---

## 🚀 Setup in Antigravity 2.0

Add the following definition to your workspace `.gemini/mcp_config.json`:

```json
{
  "mcpServers": {
    "security-sast-guard": {
      "command": "python",
      "args": ["control_plane.py", "mcp-server"]
    }
  }
}
```
