#!/usr/bin/env python3
"""Cross-platform Firewall Hook script.

Invoked by PreCommandExecute hook to validate command safety.
"""

from __future__ import annotations

import os
import sys

# Ensure project root is in python path
PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if PROJECT_ROOT not in sys.path:
    sys.path.insert(0, PROJECT_ROOT)

# pylint: disable=wrong-import-position
from src.domain.firewall_engine import (  # noqa: E402
    FirewallEngine,
)
from src.infrastructure.profile_loader import (  # noqa: E402
    ProfileLoader,  # pylint: disable=wrong-import-position
)


def main() -> int:
    """Run firewall evaluation on input command."""
    cmd_text = ""
    if len(sys.argv) > 1:
        cmd_text = " ".join(sys.argv[1:])
    else:
        cmd_text = os.environ.get("COMMAND_TEXT", os.environ.get("PRE_COMMAND", ""))

    if not cmd_text:
        print("ALLOW: No command provided to firewall.")
        return 0

    loader = ProfileLoader()
    profile = loader.load()
    if not profile:
        print("DENY: Missing or corrupted profile configuration.")
        return 1

    overlay = profile.get("command_firewall_overlay", {})
    deny_rules = overlay.get("deny", [])
    confirm_rules = overlay.get("confirm", [])

    engine = FirewallEngine(deny_rules=deny_rules, confirm_rules=confirm_rules)
    verdict = engine.evaluate(cmd_text)

    print(f"{verdict.verdict}: {verdict.reason}")

    if verdict.verdict == "DENY":
        return 1
    return 0


if __name__ == "__main__":
    sys.exit(main())
