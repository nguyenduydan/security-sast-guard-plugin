# Implementation Plan: Plugin Packaging Scripts

## 1. Overview
This plan outlines the implementation of `install.ps1`, `update.ps1`, and `remove.ps1` for the `security-sast-guard` plugin. The scripts download and extract the latest GitHub Release ZIP.

## 2. Global Constraints
- Target platform: Windows (PowerShell).
- Default install path: `$HOME/.gemini/config/plugins/security-sast-guard`.
- Safe operations: Use `try/catch` and appropriate error handling.
- `Invoke-RestMethod` and `Expand-Archive` are standard in PowerShell 5.1+.

## 3. Tasks

### Task 1: Create `install.ps1`
- Define `$InstallDir = "$HOME\.gemini\config\plugins\security-sast-guard"`.
- Check if it exists; if yes, abort and suggest `update.ps1`.
- Call GitHub API `https://api.github.com/repos/nguyenduydan/security-sast-guard-plugin/releases/latest` to get `zipball_url`.
- Download zip to temporary path.
- Expand zip to temporary folder.
- Move the extracted subfolder (which GitHub prefixes with repo name and commit hash) to `$InstallDir`.
- Clean up zip and temporary folder.

### Task 2: Create `update.ps1`
- Check if `$InstallDir` exists; if not, abort and suggest `install.ps1`.
- Backup `$InstallDir\profile.json` if it exists.
- Download and extract the latest ZIP (same as Task 1).
- Remove the old `$InstallDir` entirely (except if blocked, use `Remove-Item -Recurse -Force`).
- Move the newly extracted folder to `$InstallDir`.
- Restore the backed-up `profile.json`.
- Clean up temporary files.

### Task 3: Create `remove.ps1`
- Define `$InstallDir`.
- Prompt for confirmation (e.g. `Read-Host`).
- If confirmed, run `Remove-Item -Path $InstallDir -Recurse -Force`.
- Output success message.

## 4. Execution Strategy
This plan can be executed sequentially by a single implementer subagent or directly by the orchestrator.
