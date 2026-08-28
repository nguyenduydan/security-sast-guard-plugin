# Security & SAST Guard — Agent Directives

This system autonomously operates a dual-layer Zero-Trust security defense architecture: a background **Command Interception Firewall** (`PreCommandExecute` hook) and a **Stdio SAST Intelligence Server** for AI Agents (Antigravity 2.0 / Gemini CLI).

After modifying source code or before committing/pushing, the Agent **MUST** run `/sast-audit` (or interact via the `ask_question` modal) to confirm zero OWASP/CWE security vulnerabilities according to the level configured in `.sast/profile.json`.

---

## 1. Agentic Code Discovery & MCP Usage

- **Prioritize codebase-memory-mcp:** The Agent **MUST** prioritize tools from the `codebase-memory-mcp` server (such as `search_graph`, `query_graph`, `get_code_snippet`, `get_architecture`) to explore codebase architecture, dependency relationships, and dataflows before using blind search commands (`grep` or raw file reading).
- **Integrate sast-guard MCP Server (13 Tools):** The Agent **MUST** invoke the Stdio MCP tools provided by `sast-guard` when performing security tasks:
  - `sast_scan_file`: Check security for a specific file and extract taint traces.
  - `sast_scan_diff`: Scan security on modified lines based on Git diff.
  - `sast_check_command`: Check shell command safety before proposing execution.
  - `sast_get_dataflow_path`: Trace dataflow paths from Source to Sink.
  - `sast_get_taint_context`: Inspect taint context snippets at specified lines.
  - `sast_get_taint_evidence`: Extract concise program slice and evidence graph for a finding.
  - `sast_get_status` / `sast_set_mode` / `sast_set_level` / `sast_init` / `sast_sync_rules` / `sast_get_help` / `sast_generate_report`.

---

## 2. Command Execution Firewall Rules (Zero-Trust)

All terminal commands executed by the Agent or User must pass through the **Command Execution Firewall (`PreCommandExecute` hook)**:

1. **10-Stage De-obfuscation Normalizer:** Any complex, obfuscated, or encoded commands (Base64, Hex, Unicode, CharCode, Subcommands, Env expansion, String interpolation, Caret/Backtick stripping) are decoded prior to analysis.
2. **Capability & Intent Classification:** Evaluates command intent across 7 capability groups (`NETWORK`, `FILE_READ`, `FILE_WRITE`, `PROCESS_EXEC`, `PRIVILEGE_CHANGE`, `PERSISTENCE`, `DATA_TRANSFER`) to detect malicious behaviors such as `EXFILTRATION`, `DESTRUCTIVE`, `PRIVILEGE_ESCALATION`.
3. **Multi-Command Threat Chains:** Automatically blocks or requires confirmation for high-risk command sequences (`Download+Execute`, `Set-ExecutionPolicy Bypass`, unverified script execution).
4. **Verdict Policy:**
   - **`DENY`:** Strictly **FORBIDDEN** to execute or bypass. Never retry a DENIED command.
   - **`CONFIRM`:** Requires explicit user confirmation via the `ask_question` modal prior to execution.
   - **`ALLOW`:** Allowed to execute normally.
5. **Append-Only Audit Log:** All verdicts and evaluated commands are cryptographically recorded in `.sast/firewall_audit.jsonl`.

---

## 3. Release Process & Git Flow (Conventional Commits)

- **Scoped Conventional Commits:** All commit messages **MUST** adhere to the standard format `<type>(<scope>): <description>`. Commit types:
  - `feat`: **ONLY** used when adding new features to the core codebase (triggers Minor Version bump). Do not use `feat` for minor fixes or documentation.
  - `fix`: When fixing bugs in the source code or scripts (triggers Patch Version bump).
  - `chore`: Maintenance tasks, cleanup, library updates, CI/CD configuration (triggers Patch Version bump).
  - `refactor`: Rewriting code without changing existing behavior (triggers Patch Version bump).
  - `docs`: Adding or updating documentation (`.md`, docstrings). Does not trigger a release.
  - `style`: Formatting changes (whitespace, lint formatting).
  - `test`: Adding or updating unit tests.
- **No Manual Tagging or Version Edits:** The repository uses `release-please` v4 to automate version management. Never run `git tag` manually or manually edit version fields in `plugin.json` or `pyproject.toml` to avoid downgrading versions. The `release-please` bot will automatically create Release PRs to bump versions and update `CHANGELOG.md`.
- **Atomic Commits per Issue:** Never bundle multiple issues into a single commit. Each issue **MUST** be resolved in its own distinct commit (1 issue = 1 commit) with explicit linking keywords such as `Fixes #<id>` (e.g., `fix(firewall): strip shell wrapper prefixes (Fixes #176)`).
- **Git Branching Flow:**
  1. Never commit directly to `main`.
  2. Always create a new branch: `git checkout -b <type>/<branch-name>` (e.g., `git checkout -b fix/taint-tracker` or `git checkout -b feat/firewall-rules`).
  3. Push code to the remote repository and notify the user to open a Pull Request into `main`.

---

## 4. Mandatory Quality Inspection & CI Quality Gate

Before committing, pushing code, or declaring task completion, the Agent **MUST** run the complete quality suite and ensure a 100% green score (zero errors):

```bash
python -m ruff check .
python -m ruff format --check .
python -m pylint control_plane.py src/
python -m mypy --config-file=pyproject.toml control_plane.py src/
python -m pytest
```

If any linter, formatter, mypy, or test failure occurs, the Agent must resolve it completely before finishing the task.

---

## 5. Response & Language Policy

- **Language:** Respond in Vietnamese when the user interacts in Vietnamese. All codebase artifacts, comments, docstrings, and documentation remain strictly in English.
- **Conciseness:** Report file edits in 1–2 lines. Summarize tool outputs in 2–3 sentences. Avoid lengthy intermediate thinking narration.
