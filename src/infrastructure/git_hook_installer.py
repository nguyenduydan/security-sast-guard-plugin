"""Git Pre-Commit Hook Installer for Security SAST Guard."""

from __future__ import annotations

import os
from pathlib import Path
from typing import Any

PRE_COMMIT_SHELL_SCRIPT = """#!/usr/bin/env bash
# Security SAST Guard Git Pre-Commit Hook
# Automatically blocks commits containing critical vulnerabilities or unvetted scripts

echo "🛡️  Running Security SAST Guard Pre-Commit Verification..."

if command -v python3 >/dev/null 2>&1; then
    PYTHON_BIN="python3"
elif command -v python >/dev/null 2>&1; then
    PYTHON_BIN="python"
else
    echo "⚠️  Python not found in PATH. Skipping SAST pre-commit hook."
    exit 0
fi

# Run incremental SAST audit on staged files
$PYTHON_BIN control_plane.py scan .
EXIT_CODE=$?

if [ $EXIT_CODE -ne 0 ]; then
    echo "❌ Security SAST Guard detected blocking security issues. Commit rejected."
    exit $EXIT_CODE
fi

echo "✅ Security SAST Guard pre-commit check passed."
exit 0
"""

PRE_COMMIT_CMD_SCRIPT = """@echo off
REM Security SAST Guard Git Pre-Commit Hook (Windows)
echo [SAST Guard] Running Security SAST Guard Pre-Commit Verification...
python control_plane.py scan .
if %ERRORLEVEL% NEQ 0 (
    echo [SAST Guard] Critical security issues detected. Commit blocked.
    exit /b %ERRORLEVEL%
)
echo [SAST Guard] Pre-commit security check passed.
exit /b 0
"""


class GitHookInstaller:
    """Installs and uninstalls native git pre-commit hooks for Security SAST Guard."""

    def __init__(self, repo_dir: str | Path = ".") -> None:
        self.repo_dir = Path(repo_dir).resolve()
        self.git_dir = self.repo_dir / ".git"
        self.hooks_dir = self.git_dir / "hooks"

    def install(self) -> dict[str, Any]:
        """Install pre-commit hook scripts into .git/hooks directory."""
        if not self.git_dir.exists():
            return {
                "status": "error",
                "message": f"Not a git repository: {self.repo_dir}",
            }

        self.hooks_dir.mkdir(parents=True, exist_ok=True)

        plugin_root = Path(__file__).parents[2].resolve()
        cp_path = (plugin_root / "control_plane.py").as_posix()

        shell_script = PRE_COMMIT_SHELL_SCRIPT.replace(
            "control_plane.py", f'"{cp_path}"'
        )
        cmd_script = PRE_COMMIT_CMD_SCRIPT.replace("control_plane.py", f'"{cp_path}"')

        hook_shell = self.hooks_dir / "pre-commit"
        hook_cmd = self.hooks_dir / "pre-commit.cmd"

        hook_shell.write_text(shell_script, encoding="utf-8")
        hook_cmd.write_text(cmd_script, encoding="utf-8")

        # Make shell hook executable on POSIX environments
        if os.name != "nt":
            import contextlib  # pylint: disable=import-outside-toplevel

            with contextlib.suppress(OSError):
                hook_shell.chmod(0o755)

        return {
            "status": "success",
            "message": (
                f"Security SAST Guard pre-commit hook installed at {hook_shell}"
            ),
            "installed_files": [str(hook_shell), str(hook_cmd)],
        }

    def uninstall(self) -> dict[str, Any]:
        """Remove installed pre-commit hook scripts."""
        if not self.hooks_dir.exists():
            return {
                "status": "success",
                "message": "No hooks directory found. Nothing to uninstall.",
            }

        removed: list[str] = []
        for name in ("pre-commit", "pre-commit.cmd"):
            hook_file = self.hooks_dir / name
            if hook_file.exists():
                try:
                    hook_file.unlink()
                    removed.append(str(hook_file))
                except OSError as exc:
                    return {
                        "status": "error",
                        "message": f"Failed to remove {hook_file}: {exc}",
                    }

        return {
            "status": "success",
            "message": f"Successfully uninstalled {len(removed)} pre-commit hook(s).",
            "removed_files": removed,
        }
