<div align="center">

<img src="banner.png" alt="Security SAST Guard banner" width="100%">

# 🛡️ SECURITY SAST GUARD PLUGIN
**Zero-Trust Enterprise SAST & Real-time Command Firewall**
*Engineered for Google Antigravity 2.0 & Gemini CLI Ecosystems*

[![CI Quality Gate](https://github.com/nguyenduydan/security-sast-guard-plugin/actions/workflows/ci.yml/badge.svg)](https://github.com/nguyenduydan/security-sast-guard-plugin/actions/workflows/ci.yml)
[![Release Status](https://github.com/nguyenduydan/security-sast-guard-plugin/actions/workflows/release.yml/badge.svg)](https://github.com/nguyenduydan/security-sast-guard-plugin/actions/workflows/release.yml)
[![Latest Release](https://img.shields.io/github/v/release/nguyenduydan/security-sast-guard-plugin?color=10b981)](https://github.com/nguyenduydan/security-sast-guard-plugin/releases)
[![Python Version](https://img.shields.io/badge/python-3.12%2B-blue.svg)](https://www.python.org/)
[![MCP Server](https://img.shields.io/badge/MCP-Stdio%20Server-violet.svg)](#-stdio-mcp-server-integration)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)

[⚡ Quick Start](#-quick-start) • [🧠 Architecture](#-architecture-overview) • [🔌 MCP Server](#-stdio-mcp-server-integration) • [🎮 Reference](#-slash-commands--cli-reference) • [🛡️ Security Vectors](#-security-vectors--rule-coverage)

</div>

---

## ⚡ Quick Start

```powershell
# Install Security SAST Guard
Invoke-WebRequest -Uri "https://raw.githubusercontent.com/nguyenduydan/security-sast-guard-plugin/main/install.ps1" -OutFile "install.ps1"
.\install.ps1

# Update (Preserves local .sast/profile.json)
cd $HOME\.gemini\config\plugins\security-sast-guard; .\update.ps1

# Uninstall
cd $HOME\.gemini\config\plugins\security-sast-guard; .\remove.ps1
```

---

## 🧠 Architecture Overview

Security SAST Guard provides a two-tier zero-trust defense line: **Command Execution Firewall** (pre-execution shell interception) and **Static Application Security Testing (SAST) Scanning Engine** (file audit & MCP integration).

```mermaid
flowchart TD
    subgraph Client["Client Environment"]
        CmdInput["Shell Command"]
        FileEdit["AI Code Modification"]
        MCPClient["Stdio MCP Client"]
    end

    subgraph CoreEngine["Security SAST Guard Engine"]
        Firewall["PreCommand Interceptor (De-obfuscation + AST)"]
        HookScan["PostToolCall Auto-Scan"]
        MCPServer["Stdio MCP Server (9 Tools)"]
        Resolver["Profile Cascade (.sast/profile.json)"]
        SASTScan["SAST Multi-Vector Scanner"]
        AICache["SHA-256 AI Cache (24h TTL)"]
      end

    subgraph Exporters["Exporters & Logs"]
        SARIF["ISO SARIF 2.1.0 (.sarif)"]
        MDJSON["Markdown / JSON Reports"]
        AuditLog[".aiops/decisions.jsonl"]
    end

    CmdInput -->|"Intercept"| Firewall
    FileEdit -->|"Trigger"| HookScan
    Firewall -->|"Load Profile"| Resolver
    HookScan --> SASTScan
    MCPClient <-->|"JSON-RPC"| MCPServer
    MCPServer --> SASTScan
    SASTScan --> AICache
    SASTScan --> SARIF
    SASTScan --> MDJSON
    Firewall --> AuditLog
```

---

## 🔌 Stdio MCP Server Integration

Add `sast-guard` to your `mcp_config.json`:

```json
{
  "mcpServers": {
    "sast-guard": {
      "command": "python",
      "args": ["-m", "src.mcp.server"],
      "cwd": "${workspaceFolder}"
    }
  }
}
```

### Stdio Tools Provided
- `sast_scan_file`: Audits single source code file against active SAST rules.
- `sast_scan_diff`: Performs incremental scan against Git diff tracking branch.
- `sast_check_command`: Validates shell command against Firewall safety rules.
- `sast_get_status` / `sast_set_mode` / `sast_set_level` / `sast_init` / `sast_sync_rules` / `sast_get_help`.

---

## 🎮 Slash Commands & CLI Reference

| AI Slash Command | CLI Command | Function |
| :--- | :--- | :--- |
| 🛡️ `/sast-audit [type] [path]` | `sast scan [path]` | Triggers SAST audit (`diff`, `file`, `codebase`, `api`, `web`). |
| 📊 `/sast-status` | `sast status` | Displays profile configuration, active mode, and rule count. |
| 🚀 `/sast-init` | `sast init` | Initializes project-level `.sast/profile.json` config. |
| 🎛️ `/sast-mode [strict\|draft]` | `sast mode [mode]` | Sets operation strictness (`strict` blocks warnings, `draft` logs only). |
| 🎚️ `/sast-audit-level [lite\|full\|ultra]` | `sast level [level]` | Updates inspection depth (`lite`, `full`, `ultra`). |
| 🛠️ `/sast-rules [sync\|add]` | `sast rules` | Syncs or definition-updates SAST security vector rules. |

---

## 🛡️ Security Vectors & Rule Coverage

Security SAST Guard implements **53 core SAST vector rules** mapped across global standard frameworks:

| Framework / Category | Rule Count | High-Impact Vector Examples |
| :--- | :---: | :--- |
| **OWASP API Security 2023** | 10 | BOLA (API1), Broken Authentication (API2), Mass Assignment (API3), SSRF (API7) |
| **OWASP Web Application Top 10** | 10 | Broken Access Control (A01), Cryptographic Failure (A02), Injection (A03) |
| **CWE-SANS Top 25** | 12 | SQLi (CWE-89), XSS (CWE-79), OS Command Injection (CWE-78), Path Traversal (CWE-22) |
| **NIST 800-53 Security Controls** | 10 | AC-2 Account Management, SC-8 Transmission Integrity, AU-2 Audit Events |
| **Secret & Credential Guard** | 11 | Hardcoded RSA/SSH Keys, API Tokens, Plaintext Password Assignment |

### Inline Suppression
To suppress specific rule alerts in source code, append `# sast-ignore [RULE_ID]` to the target line:
```python
query = f"SELECT * FROM users WHERE id = {user_id}"  # sast-ignore [OWASP-A03-SQLI]
```

---

## 🤝 Contributing & License

Distributed under the [MIT License](LICENSE). Read [CONTRIBUTING.md](CONTRIBUTING.md) for details on submitting security rule additions.

