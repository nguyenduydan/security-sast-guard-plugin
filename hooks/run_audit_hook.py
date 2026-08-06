"""Audit hook entrypoint."""

import os
import sys
from pathlib import Path

# Add project root to sys.path if not present
PROJECT_ROOT = Path(__file__).resolve().parents[1]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from src.application.audit_service import AuditService  # pylint: disable=wrong-import-position


def main() -> int:
    """Execute audit hook."""
    target = os.environ.get("SAST_TARGET", "")
    if not target and len(sys.argv) > 1:
        target = sys.argv[1]

    if not target:
        print("Audit hook: No target specified via SAST_TARGET env or argument.")
        return 0

    service = AuditService()
    _findings, _report_file, summary = service.run_audit(target_path=target)
    print(summary)
    return 0


if __name__ == "__main__":
    sys.exit(main())
