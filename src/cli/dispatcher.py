"""Dispatcher CLI module."""

import sys
from collections.abc import Sequence

from src.application.audit_service import AuditService


def _print_status() -> int:
    service = AuditService()
    status = service.get_status()

    print("SAST Security & Firewall Guard Status")
    print("=====================================")
    print(f"Project ID     : {status['project_id']}")
    print(f"Stack          : {status['stack']}")
    print(f"Mode           : {status['mode']}")
    print(f"Audit Level    : {status['audit_level']}")
    print(f"SAST Level     : {status['sast_level']}")
    print("Command Firewall Overlay:")
    print(f"  - Deny Rules   : {status['deny_count']}")
    print(f"  - Confirm Rules: {status['confirm_count']}")
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
        service = AuditService()
        _, _, summary = service.run_audit(target_path)
        print(summary)
        return 0

    print(f"Unknown command: {command}")
    return 1


if __name__ == "__main__":
    sys.exit(main())
