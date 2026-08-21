#!/usr/bin/env python3
"""PostToolCallExecute Hook script for Security SAST Guard.

Triggers automatic SAST scanning when a file is created or modified by an AI agent.
"""

from __future__ import annotations

import os
import sys

PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if PROJECT_ROOT not in sys.path:
    sys.path.insert(0, PROJECT_ROOT)

# pylint: disable=wrong-import-position
from src.application.audit_service import (  # noqa: E402
    AuditService,
)


def main() -> int:
    """Run SAST audit on modified target file."""
    target = ""
    if len(sys.argv) > 1:
        target = sys.argv[1]
    else:
        target = os.environ.get("TOOL_FILE_PATH", os.environ.get("SAST_TARGET", ""))

    if not target or not os.path.exists(target):
        return 0

    findings, _, _summary = service.run_audit(
        target_path=target, generate_report=False
    )

    if findings:
        msg = f"[SAST Guard] Auto-scan detected {len(findings)} findings in {target}:"
        print(msg)
        for f in findings[:3]:
            sev = f.get("severity", "UNKNOWN")
            name = f.get("rule_name", f.get("rule_id", "Security Issue"))
            line = f.get("line", f.get("line_number", 1))
            print(f" - [{sev}] {name} (Line {line})")
        if len(findings) > 3:
            print(f" ... and {len(findings) - 3} more findings.")
    else:
        print(f"[SAST Guard] Auto-scan passed cleanly for {target}.")

    return 0


if __name__ == "__main__":
    sys.exit(main())
