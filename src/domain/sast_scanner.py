"""SAST Scanner domain component."""

import json
from typing import Any

from .context_extractor import extract_context


class SASTScanner:
    """SAST rule scanner implementation."""

    def __init__(self, profile_path: str = "profile.json"):
        self.profile_path = profile_path
        self.mode = "strict"
        self._load_profile()

    def _load_profile(self):
        try:
            with open(self.profile_path, encoding="utf-8") as f:
                profile = json.load(f)
                self.mode = profile.get("mode", "strict")
        except FileNotFoundError:
            pass

    def _detect_matches(self, path: str) -> list[dict[str, Any]]:
        """Placeholder for actual regex engine execution."""
        _ = path
        return []

    def scan(self, path: str) -> list[dict[str, Any]]:
        """Scan specified file path for SAST rule matches with lazy interactive loop."""
        matches = self._detect_matches(path)
        violations: list[dict[str, Any]] = []

        for match in matches:
            ctx = extract_context(path, match["line"])
            rule = match["rule"]
            line_no = match["line"]
            severity = match.get("severity", "MEDIUM")

            # Reduce alert fatigue: check if match is purely inside a comment or string
            if ctx.get("is_safe_context"):
                continue

            print(f"[SAST WARNING] Potential {rule} at `{path}:{line_no}`.")
            print(f"- Severity: {severity}")
            print(f"- Line: `{ctx['line_content'].strip()}`")
            print(f"- Scope: `{ctx['scope']}`")

            if self.mode == "draft" and severity in ("MEDIUM", "LOW"):
                print(
                    ">> [DRAFT MODE] Auto-allowing low/medium severity finding "
                    "to preserve vibe."
                )
                continue

            prompt_msg = "? Is this context safe? (Reply Y to allow, N to block): "
            answer = input(prompt_msg).strip().upper()
            if answer != "Y":
                violations.append(match)

        return violations
