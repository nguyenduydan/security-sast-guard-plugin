# 🔌 Antigravity 2.0 MCP Integration Guide

Security SAST Guard provides a native **Model Context Protocol (MCP)** server over stdio, enabling Antigravity 2.0 (IDE) and Gemini CLI to invoke security auditing and command verification as native agent tools.

---

## 🛠️ Registered MCP Tools

| MCP Tool Name | Arguments | Description |
| :--- | :--- | :--- |
| 🛡️ `sast_scan_file` | `file_path: string` | Scans a single target file for OWASP/CWE vulnerabilities with taint tracing. |
| 🔍 `sast_scan_diff` | *None* | Scans modified git files according to git diff in current workspace. |
| 🧱 `sast_check_command` | `command: string` | Tests command safety against 10-stage Firewall overlay rules (`ALLOW`, `CONFIRM`, `DENY`). |
| 📊 `sast_get_status` | *None* | Returns plugin version, project ID, tech stack, operation mode, and active rules. |
| 🎚️ `sast_set_level` | `level: string` | Sets active strictness level (`lite`, `full`, or `ultra`). |
| 🎛️ `sast_set_mode` | `mode: string` | Sets active operation mode (`strict` or `draft`). |
| 🚀 `sast_init` | *None* | Initializes project-local `.sast/profile.json` security profile. |
| ⚙️ `sast_sync_rules` | `rules_dir?: string` | Syncs custom Markdown rule definitions into project profile. |
| 🆘 `sast_get_help` | *None* | Returns quick reference documentation card. |
| 🌐 `sast_get_dataflow_path` | `source_pattern: string, sink_pattern: string, repo_path?: string` | Traces source-to-sink dataflow paths across AST and call graph. |
| 🔬 `sast_get_taint_context` | `file_path: string, line_number: int, context_lines?: int` | Retrieves code snippet context for target taint line. |
| 📑 `sast_generate_report` | `findings: list, target_path?: string, ai_analysis?: bool` | Generates comprehensive SARIF 2.1.0 and Markdown security audit reports. |


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
