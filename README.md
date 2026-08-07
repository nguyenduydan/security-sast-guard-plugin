<div align="center">

<img src="banner.png" alt="Security SAST Guard banner" width="100%">

# 🛡️ SECURITY SAST GUARD PLUGIN
**Zero-Trust Enterprise SAST & Real-time Command Firewall**
*Engineered for Google Antigravity 2.0 & Gemini CLI Ecosystems*

[![CI Quality Gate](https://github.com/nguyenduydan/security-sast-guard-plugin/actions/workflows/ci.yml/badge.svg)](https://github.com/nguyenduydan/security-sast-guard-plugin/actions/workflows/ci.yml)
[![Release Status](https://github.com/nguyenduydan/security-sast-guard-plugin/actions/workflows/release.yml/badge.svg)](https://github.com/nguyenduydan/security-sast-guard-plugin/actions/workflows/release.yml)
[![Latest Release](https://img.shields.io/github/v/release/nguyenduydan/security-sast-guard-plugin?color=10b981)](https://github.com/nguyenduydan/security-sast-guard-plugin/releases)
[![Python Version](https://img.shields.io/badge/python-3.12%2B-blue.svg)](https://www.python.org/)
[![MCP Server](https://img.shields.io/badge/MCP-Stdio%20Server-violet.svg)](#-antigravity-20-stdio-mcp-server)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)

[🔥 Features](#-core-security-features) • [🧠 Architecture](#-architecture-overview) • [🔌 MCP Integration](#-antigravity-20-stdio-mcp-server) • [⚡ Installation](#-installation--lifecycle-management) • [🎮 Commands](#-slash-commands--cli-reference) • [🛡️ Rules](#-sast-rules-coverage) • [🤝 Contributing](#-contributing)

</div>

---

## 🕵️‍♂️ About Security SAST Guard

**Security SAST Guard** is your automated, zero-trust security co-pilot for Google Antigravity & Gemini CLI. It works stealthily behind the scenes to keep your local machine safe from destructive shell commands, while auditing AI-generated code against OWASP and CWE standards in real-time.

> *"Empower your AI without compromising your system's integrity."*

---

## 🔥 Core Security Features

### 🌐 1. Real-Time Command Firewall & Anti-Bypass Deobfuscation
- **Anti-Bypass Engine:** Detects and strips caret obfuscation (`c^m^d`), PowerShell backticks (``c`m`d``), and automatically decodes Base64 payloads (`cm0gLXJmIC8=` -> `rm -rf /`).
- **Cross-Platform Protection:** Native POSIX bash (`hooks/firewall_hook.sh`) and Windows PowerShell hooks for Linux, macOS, and Windows environments.
- **PostToolCall Auto-Scan Hook:** `PostToolCallExecute` hook (`hooks/post_write_hook.py`) automatically audits files written or modified by AI agents.

### 🔌 2. Native Stdio MCP Server for Antigravity 2.0
Exposes 8 Stdio JSON-RPC MCP tools for seamless IDE integration:
1. **`sast_scan_file(file_path)`**: Audits target source file for vulnerabilities.
2. **`sast_scan_diff()`**: Scans uncommitted git changes in the workspace.
3. **`sast_check_command(command)`**: Evaluates shell command safety (`ALLOW` | `CONFIRM` | `DENY`).
4. **`sast_get_status()`**: Retrieves plugin version, project ID, tech stack, operation mode, and active rules.
5. **`sast_set_level(level)`**: Updates active audit level (`lite`, `full`, `ultra`).
6. **`sast_set_mode(mode)`**: Updates active operation mode (`strict`, `draft`).
7. **`sast_init()`**: Initializes project-local `.sast/profile.json` security profile.
8. **`sast_get_help()`**: Retrieves quick reference usage documentation.

### 🗂️ 3. Multi-Project Profile Resolver & Custom Rule Sync
- **Priority Cascade Resolution:** Loads profile settings in order: `.sast/profile.json` (CWD) ➔ `.sast/profile.json` (Git Root) ➔ Global Plugin `profile.json`.
- **Project Initialization:** Slash command `/sast-init` (or `sast init`) generates project-specific security rules.

### 🤖 4. AI Response Cache (SHA-256) & Dual Report Formats
- **SHA-256 Cache:** Local cache (`~/.sast/ai_cache.json`) with 24h TTL eliminates redundant LLM verification calls.
- **Dual Output Formats:** Supports both Markdown (`.md`) and JSON (`.json`) report generation (`--format json`).

### 🎨 5. Cyber / Neo-Brutalist TUI & Interactive Documentation
- **PowerShell Cyber TUI:** `install.ps1`, `update.ps1`, and `remove.ps1` feature Cyber/Neo-Brutalist ASCII headers, block progress bars (`[████████░░░]`), and UTF-8 BOM encoding for perfect encoding compatibility.
- **Interactive Landing Page:** Updated [`docs/index.html`](docs/index.html) with separate CSS/JS assets, live workflow animation, and 53 SAST rules explorer.


---

## ⚡ Installation & Lifecycle Management

We provide an automated, Cyber-TUI PowerShell suite to install, update, and remove the plugin smoothly.

> **Note:** Run these scripts directly in your PowerShell terminal.

### 📥 1. Install
Fetches the latest release from GitHub, extracts it, and registers the plugin in your Antigravity environment.
```powershell
Invoke-WebRequest -Uri "https://raw.githubusercontent.com/nguyenduydan/security-sast-guard-plugin/main/install.ps1" -OutFile "install.ps1"
.\install.ps1
```

### 🔄 2. Update
Updates the plugin while **automatically backing up and restoring your user profile** (`profile.json`):
```powershell
cd $HOME\.gemini\config\plugins\security-sast-guard
.\update.ps1
```

### 🗑️ 3. Remove
Safely uninstalls the plugin and restores original configuration states:
```powershell
cd $HOME\.gemini\config\plugins\security-sast-guard
.\remove.ps1
```

---

## 🧠 Architecture Overview

```mermaid
flowchart TD
    subgraph Client["Antigravity 2.0 / Gemini CLI"]
        UserCmd["Shell Command Input"]
        AISkill["AI Skill Directives"]
        MCPClient["MCP Stdio Client"]
    end

    subgraph SecurityGuard["Security SAST Guard Core"]

        Firewall["FirewallEngine (Deobfuscation + Regex)"]
        Scanner["SAST Scanning Engine"]
        MCPServer["Stdio MCP Server"]
        Resolver["ProfileResolver Cascade"]
        AICache["AICache (SHA-256 24h TTL)"]
    end

    subgraph Storage["Knowledge Base"]
        RuleDB[("53 SAST Rules")]
        LocalProfile[(".sast/profile.json")]
    end

    UserCmd -->|"Intercept Cmd"| Firewall
    Firewall -->|"Load Rules"| Resolver
    Resolver -->|".sast -> Git Root -> Global"| LocalProfile
    Firewall -->|"ALLOW/CONFIRM/DENY"| UserCmd

    MCPClient <-->|"JSON-RPC Stdio"| MCPServer
    MCPServer --> Scanner

    AISkill -->|"Trigger /sast-audit"| Scanner
    Scanner -->|"Match Regex"| RuleDB
    Scanner -->|"Check Cache"| AICache
    Scanner -->|"Report (MD / JSON)"| AISkill
```

---

## 🔌 Antigravity 2.0 Stdio MCP Server

To enable Security SAST Guard inside **Antigravity 2.0 (IDE)** or any MCP-compatible environment, add the following configuration to your `mcp_config.json`:

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

For complete integration details and tool schemas, read [`docs/MCP_INTEGRATION.md`](docs/MCP_INTEGRATION.md).

---

## 🎮 Slash Commands & CLI Reference

### 🤖 AI Slash Commands (Chat UI)

| Slash Command | Syntax | Description |
| :--- | :--- | :--- |
| 🛡️ `/sast-audit` | `/sast-audit <file\|codebase\|api\|web> <path>` | Triggers static vulnerability audit. Outputs Markdown and JSON reports. |
| 📊 `/sast-status` | `/sast-status` | Displays plugin version, project ID, tech stack, operation mode, and active rules. |
| 🚀 `/sast-init` | `/sast-init` | Initializes project-local `.sast/profile.json` security profile. |
| 🎛️ `/sast-mode` | `/sast-mode [strict\|draft]` | Toggles operation mode (`strict`: full enforcement, `draft`: auto-allow low/medium). |
| 🎚️ `/sast-audit-level`| `/sast-audit-level [lite\|full\|ultra]` | Sets active audit strictness (`lite`: Critical, `full`: OWASP Top10, `ultra`: All + CWE/NIST). |


### 💻 CLI Subcommands (Terminal Entrypoint & `sast` Runner)

| CLI Subcommand | Syntax | Description |
| :--- | :--- | :--- |
| 📊 `status` | `sast status` *(or `python control_plane.py status`)* | Displays plugin version, project ID, tech stack, operation mode, and rule counts. |
| 🎛️ `mode` | `sast mode [strict\|draft]` | Sets operation mode (`strict` \| `draft`). |
| ℹ️ `version` | `sast version` | Displays plugin version, Python runtime, and platform info. |
| 🧱 `firewall` | `sast firewall <command>` | Evaluates command against firewall rules with de-obfuscation. |
| 🚀 `init` | `sast init` | Creates project-local `.sast/profile.json` template. |
| 🔌 `mcp-server` | `sast mcp-server` | Runs Stdio JSON-RPC MCP Server for IDEs. |
| 🎚️ `level` | `sast level [lite\|full\|ultra]` | Updates active SAST audit strictness level. |
| 🔍 `scan` | `sast scan [path] [--format json]` | Scans target path and generates audit report. |


---

## 🛡️ SAST Rules Coverage

Security SAST Guard ships with 53 battle-tested rules mapping to top international frameworks:

| Threat Category | Count | Coverage Examples |
| :--- | :---: | :--- |
| **OWASP API Security 2023** | 10 | BOLA (API1), Broken Auth (API2), Mass Assignment (API3), SSRF (API7) |
| **OWASP Web Application 2021** | 10 | Access Control (A01), Cryptographic Failures (A02), Injection (A03) |
| **Web App Specific** | 11 | Race Condition (WEB10), Source File Exposure (WEB11), CORS (WEB9) |
| **CWE-SANS Top 25** | 12 | SQLi (CWE-89), XSS (CWE-79), Command Injection (CWE-078), Path Traversal (CWE-022) |
| **NIST 800-53 Controls** | 10 | AC-2 (Account Management), SC-8 (Transmission Integrity), AU-2 (Audit Events) |

---

## 🤝 Contributing

We welcome security researchers and community contributors! Please read our [CONTRIBUTING.md](CONTRIBUTING.md) guide before submitting Pull Requests.

1. Fork the repo and create your feature branch: `git checkout -b feat/my-new-rule`.
2. Follow Conventional Commits format for your commit messages.
3. Ensure all CI quality checks pass: `pytest` and `pylint`.
4. Open a Pull Request using our template.

---

<div align="center">
  <b>Protected by Security SAST Guard</b><br>
  Distributed under the <a href="LICENSE">MIT License</a>.
</div>

