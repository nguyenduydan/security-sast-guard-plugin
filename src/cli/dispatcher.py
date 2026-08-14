"""Dispatcher CLI module."""

import platform
import re
import sys
from collections.abc import Sequence
from pathlib import Path
from typing import Any

from src.application.audit_service import AuditService
from src.infrastructure.git_hook_installer import GitHookInstaller
from src.infrastructure.profile_loader import ProfileLoader
from src.infrastructure.version_loader import get_plugin_version
from src.mcp.server import MCPServer


def _print_status() -> int:
    service = AuditService()
    status = service.get_status()

    print("SAST Security & Firewall Guard Status")
    print("=====================================")
    print(f"Version        : v{status.get('version', '1.0.0')}")
    print(f"Project ID     : {status['project_id']}")
    print(f"Stack          : {status['stack']}")
    print(f"Mode           : {status['mode']}")
    print(f"Audit Level    : {status['audit_level']}")
    print(f"SAST Scan Rules: {status.get('sast_rules_count', 0)} active rules")
    print("Command Firewall Overlay:")
    print(f"  - Deny Rules   : {status['deny_count']}")
    print(f"  - Confirm Rules: {status['confirm_count']}")
    return 0


def _handle_version() -> int:
    """Display plugin version, Python runtime version, and platform information."""
    version = get_plugin_version()
    py_version = platform.python_version()
    plat_info = platform.platform()

    print(f"Security SAST Guard v{version}")
    print(f"Python: {py_version}")
    print(f"Platform: {plat_info}")
    return 0


def _handle_firewall(args: list[str]) -> int:
    """Evaluate command string against security firewall overlay rules."""
    loader = ProfileLoader()
    profile_path = Path("profile.json")
    if not profile_path.exists():
        profile_path = Path(__file__).parents[2] / "profile.json"

    profile = loader.load(str(profile_path))
    if not profile:
        print("DENY: Missing or corrupted profile configuration.")
        return 1

    if not args:
        print("Usage: control_plane.py firewall <command_string>")
        return 1

    cmd_text = " ".join(args).strip()
    if not cmd_text:
        print("Usage: control_plane.py firewall <command_string>")
        return 1

    overlay: dict[str, Any] = profile.get("command_firewall_overlay", {})
    deny_rules: list[str] = overlay.get("deny", [])
    confirm_rules: list[str] = overlay.get("confirm", [])

    for pattern in deny_rules:
        try:
            if re.search(pattern, cmd_text, re.IGNORECASE):
                print(f"DENY: Dangerous pattern matched: '{pattern}'")
                return 0
        except re.error:
            continue

    for pattern in confirm_rules:
        try:
            if re.search(pattern, cmd_text, re.IGNORECASE):
                print(f"CONFIRM: Potentially risky pattern matched: '{pattern}'")
                return 0
        except re.error:
            continue

    print("ALLOW: Command verified safe by firewall.")
    return 0


def _handle_level(args: list[str]) -> int:
    """Handle level / set-level subcommand."""
    service = AuditService()
    if args:
        target_level = args[0]
        if service.set_audit_level(target_level):
            print(f"Audit level successfully set to '{target_level.lower()}'.")
            return 0
        print(
            f"Error: Invalid level '{target_level}'. Valid options: lite, full, ultra."
        )
        return 1
    status = service.get_status()
    print(f"Current Audit Level: {status['audit_level']}")
    return 0


def _handle_mode(args: list[str]) -> int:
    """Handle mode / set-mode subcommand."""
    service = AuditService()
    if args:
        target_mode = args[0]
        if service.set_mode(target_mode):
            print(f"Operation mode successfully set to '{target_mode.lower()}'.")
            return 0
        print(f"Error: Invalid mode '{target_mode}'. Valid options: strict, draft.")
        return 1
    status = service.get_status()
    print(f"Current Operation Mode: {status['mode']}")
    return 0


# pylint: disable=too-many-branches,too-many-statements
def _handle_scan(args: list[str]) -> int:
    """Handle scan / audit subcommand with format, threads, and level options."""
    verbose = "-v" in args or "--verbose" in args

    sarif_output_path: str | None = None
    html_output_path: str | None = None
    output_format = "markdown"
    target_level: str | None = None
    threads: int | None = None
    positional_args: list[str] = []

    idx = 0
    while idx < len(args):
        arg = args[idx]
        if arg in ("-v", "--verbose"):
            verbose = True
            idx += 1
        elif arg == "--sarif":
            output_format = "sarif"
            if idx + 1 < len(args) and not args[idx + 1].startswith("-"):
                sarif_output_path = args[idx + 1]
                idx += 2
            else:
                idx += 1
        elif arg == "--html":
            output_format = "html"
            if idx + 1 < len(args) and not args[idx + 1].startswith("-"):
                html_output_path = args[idx + 1]
                idx += 2
            else:
                idx += 1
        elif arg in ("--format", "-f"):
            if idx + 1 < len(args):
                output_format = args[idx + 1].lower()
                idx += 2
            else:
                idx += 1
        elif arg in ("--threads", "-t"):
            if idx + 1 < len(args):
                try:
                    threads = int(args[idx + 1])
                except ValueError:
                    threads = None
                idx += 2
            else:
                idx += 1
        elif arg in ("--level", "-l"):
            if idx + 1 < len(args):
                target_level = args[idx + 1].lower()
                idx += 2
            else:
                idx += 1
        else:
            positional_args.append(arg)
            idx += 1

    target_path = positional_args[0] if positional_args else "."
    if target_path.lower() == "codebase":
        target_path = "."

    service = AuditService()
    if target_level:
        service.set_audit_level(target_level)

    _, _, summary = service.run_audit(
        target_path,
        verbose=verbose or True,
        output_format=output_format,
        sarif_output_path=sarif_output_path,
        html_output_path=html_output_path,
        threads=threads,
    )
    print(summary)
    return 0


def _handle_init() -> int:
    """Initialize project-local .sast/profile.json configuration."""
    sast_dir = Path(".sast")
    sast_dir.mkdir(exist_ok=True)
    profile_file = sast_dir / "profile.json"

    if profile_file.exists():
        print(f"Project profile already exists at {profile_file}")
        return 0

    tmpl_file = Path(__file__).parents[2] / "templates" / "profile_template.json"
    if tmpl_file.exists():
        content = tmpl_file.read_text(encoding="utf-8")
    else:
        content = '{\n  "profile_name": "project_local"\n}\n'

    profile_file.write_text(content, encoding="utf-8")
    print(f"Successfully initialized project profile at {profile_file}")
    return 0


def _handle_install_hook(args: list[str]) -> int:
    """Install git pre-commit security hook."""
    target_repo = args[0] if args else "."
    installer = GitHookInstaller(repo_dir=target_repo)
    result = installer.install()
    print(result.get("message", "Hook installation finished."))
    return 0 if result.get("status") == "success" else 1


def _handle_uninstall_hook(args: list[str]) -> int:
    """Uninstall git pre-commit security hook."""
    target_repo = args[0] if args else "."
    installer = GitHookInstaller(repo_dir=target_repo)
    result = installer.uninstall()
    print(result.get("message", "Hook uninstallation finished."))
    return 0 if result.get("status") == "success" else 1


def _handle_mcp_server() -> int:
    """Run Stdio JSON-RPC MCP Server."""
    server = MCPServer()
    server.run()
    return 0


# pylint: disable=too-many-return-statements
def dispatch(args: list[str]) -> int:
    """Dispatch command line arguments to appropriate handler."""
    command = args[0].lower() if args else "status"

    if command == "status":
        return _print_status()

    if command == "version":
        return _handle_version()

    if command == "firewall":
        return _handle_firewall(args[1:])

    if command in ("level", "set-level"):
        return _handle_level(args[1:])

    if command in ("mode", "set-mode"):
        return _handle_mode(args[1:])

    if command in ("scan", "audit"):
        return _handle_scan(args[1:])

    if command == "init":
        return _handle_init()

    if command in ("install-hook", "install-git-hook", "hook-install"):
        return _handle_install_hook(args[1:])

    if command in ("uninstall-hook", "uninstall-git-hook", "hook-uninstall"):
        return _handle_uninstall_hook(args[1:])

    if command in ("mcp-server", "mcp"):
        return _handle_mcp_server()

    print(f"Unknown command: {command}")
    return 1


def main(args: Sequence[str] | None = None) -> int:
    """Main CLI entrypoint."""
    if args is None:
        args = sys.argv[1:]
    return dispatch(list(args))


if __name__ == "__main__":
    sys.exit(main())
