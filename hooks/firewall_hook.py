#!/usr/bin/env python3
"""Cross-platform Firewall Hook script.

Invoked by PreCommandExecute hook to validate command safety.
"""

from __future__ import annotations

import json
import os
import sys

# Ensure project root is in python path
PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if PROJECT_ROOT not in sys.path:
    sys.path.insert(0, PROJECT_ROOT)

# pylint: disable=wrong-import-position
import json

from src.domain.firewall_engine import (  # noqa: E402
    FirewallEngine,
)
from src.infrastructure.profile_loader import (  # noqa: E402
    ProfileLoader,  # pylint: disable=wrong-import-position
)


def main() -> int:
    """Run firewall evaluation on input command."""
    cmd_text = ""

    # Try reading from stdin first (Gemini Hook standard)
    if not sys.stdin.isatty():
        try:
            stdin_data = sys.stdin.read()
            if stdin_data:
                payload = json.loads(stdin_data)
                tool_call = payload.get("toolCall", {})
                if tool_call.get("name") == "run_command":
                    cmd_text = tool_call.get("args", {}).get("CommandLine", "")
        except json.JSONDecodeError:
            # Ignore stdin parsing errors; fallback to argv or env vars later
            pass

    # Fallback to sys.argv or environment variables
    if not cmd_text:
        if len(sys.argv) > 1:
            cmd_text = " ".join(sys.argv[1:])
        else:
            cmd_text = os.environ.get("COMMAND_TEXT", os.environ.get("PRE_COMMAND", ""))

    if not cmd_text:
        print(
            json.dumps(
                {"decision": "allow", "reason": "No command provided to firewall."}
            )
        )
        return 0

    loader = ProfileLoader()
    profile = loader.load()
    if not profile:
        print(
            json.dumps(
                {
                    "decision": "deny",
                    "reason": "Missing or corrupted profile configuration.",
                }
            )
        )
        return 0

    overlay = profile.get("command_firewall_overlay", {})
    deny_rules = overlay.get("deny", [])
    confirm_rules = overlay.get("confirm", [])

    engine = FirewallEngine(deny_rules=deny_rules, confirm_rules=confirm_rules)
    verdict = engine.evaluate(cmd_text)

    decision_map = {"DENY": "deny", "CONFIRM": "force_ask", "ALLOW": "allow"}

    decision = decision_map.get(verdict.verdict, "allow")

    print(json.dumps({"decision": decision, "reason": verdict.reason}))

    return 0


if __name__ == "__main__":
    sys.exit(main())
