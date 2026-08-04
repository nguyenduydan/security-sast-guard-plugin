"""Dispatcher CLI module."""

import sys
from collections.abc import Sequence

from src.domain.sast_scanner import SASTScanner
from src.infrastructure.profile_loader import ProfileLoader
from src.infrastructure.report_generator import generate_markdown_report


def main(args: Sequence[str] | None = None) -> int:
    """Main CLI entrypoint."""
    if args is None:
        args = sys.argv[1:]

    command = args[0].lower() if args else "status"

    if command == "status":
        loader = ProfileLoader()
        profile = loader.load("profile.json")
        project_id = profile.get("project_id", "unknown")
        stack = profile.get("stack", "unknown")
        mode = profile.get("mode", "strict")
        audit_level = profile.get("audit_level", "full")
        sast_level = profile.get("sast_level", "ultra")

        firewall = profile.get("command_firewall_overlay", {})
        deny_rules = firewall.get("deny", [])
        confirm_rules = firewall.get("confirm", [])

        print("SAST Security & Firewall Guard Status")
        print("=====================================")
        print(f"Project ID     : {project_id}")
        print(f"Stack          : {stack}")
        print(f"Mode           : {mode}")
        print(f"Audit Level    : {audit_level}")
        print(f"SAST Level     : {sast_level}")
        print("Command Firewall Overlay:")
        print(f"  - Deny Rules   : {len(deny_rules)}")
        print(f"  - Confirm Rules: {len(confirm_rules)}")
        return 0

    if command in ("scan", "audit"):
        target_path = args[1] if len(args) > 1 else "."
        scanner = SASTScanner()
        findings = scanner._detect_matches(target_path)
        _, summary = generate_markdown_report(findings)
        print(summary)
        return 0

    print(f"Unknown command: {command}")
    return 1


if __name__ == "__main__":
    sys.exit(main())

