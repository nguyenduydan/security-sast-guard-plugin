"""Dispatcher CLI module."""

import sys
from collections.abc import Sequence

from src.domain.sast_scanner import SASTScanner
from src.infrastructure.profile_loader import ProfileLoader
from src.infrastructure.report_generator import generate_markdown_report


def _print_status() -> int:
    profile = ProfileLoader().load("profile.json")
    firewall = profile.get("command_firewall_overlay", {})
    deny_rules = firewall.get("deny", [])
    confirm_rules = firewall.get("confirm", [])

    print("SAST Security & Firewall Guard Status")
    print("=====================================")
    print(f"Project ID     : {profile.get('project_id', 'unknown')}")
    print(f"Stack          : {profile.get('stack', 'unknown')}")
    print(f"Mode           : {profile.get('mode', 'strict')}")
    print(f"Audit Level    : {profile.get('audit_level', 'full')}")
    print(f"SAST Level     : {profile.get('sast_level', 'ultra')}")
    print("Command Firewall Overlay:")
    print(f"  - Deny Rules   : {len(deny_rules)}")
    print(f"  - Confirm Rules: {len(confirm_rules)}")
    return 0


def main(args: Sequence[str] | None = None) -> int:
    """Main CLI entrypoint."""
    if args is None:
        args = sys.argv[1:]

    command = args[0].lower() if args else "status"

    if command == "status":
        return _print_status()

    if command in ("scan", "audit"):
        target_path = args[1] if len(args) > 1 else "."
        scanner = SASTScanner()
        findings = scanner.scan(target_path)
        _, summary = generate_markdown_report(findings)
        print(summary)
        return 0

    print(f"Unknown command: {command}")
    return 1


if __name__ == "__main__":
    sys.exit(main())
