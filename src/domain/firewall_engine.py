"""Firewall Engine Module for Security SAST Guard.

Provides cross-platform command safety evaluation, de-obfuscation, and rule checking.
"""

from __future__ import annotations

import base64
import re
from dataclasses import dataclass
from functools import lru_cache
from typing import Literal

VerdictType = Literal["ALLOW", "CONFIRM", "DENY"]


@dataclass(frozen=True)
class FirewallVerdict:
    """Represents the verdict of a firewall command evaluation."""

    verdict: VerdictType
    reason: str
    matched_pattern: str | None = None


class FirewallEngine:
    """Cross-platform command evaluation engine with de-obfuscation."""

    def __init__(
        self,
        deny_rules: list[str] | None = None,
        confirm_rules: list[str] | None = None,
    ) -> None:
        self.deny_rules = deny_rules or []
        self.confirm_rules = confirm_rules or []
        self._compiled_deny = [re.compile(p, re.IGNORECASE) for p in self.deny_rules]
        self._compiled_confirm = [
            re.compile(p, re.IGNORECASE) for p in self.confirm_rules
        ]

    @staticmethod
    @lru_cache(maxsize=2048)
    def deobfuscate(cmd: str) -> str:
        """Strip de-obfuscation artifacts such as carets and backticks."""
        if not cmd:
            return ""

        # Strip PowerShell carets and Bash backticks used to break keywords
        cleaned = cmd.replace("^", "").replace("`", "")

        # Check for Base64 encoded payload indicators (e.g. -EncodedCommand / -e / -enc)
        base64_match = re.search(
            r"(?:-e|-enc|-encodedcommand)\s+([A-Za-z0-9+/=]+)",
            cleaned,
            re.IGNORECASE,
        )
        if base64_match:
            try:
                encoded_str = base64_match.group(1)
                decoded_bytes = base64.b64decode(encoded_str)
                # Try UTF-16LE (Windows PowerShell default) then UTF-8
                try:
                    decoded_str = decoded_bytes.decode("utf-16le")
                except UnicodeDecodeError:
                    decoded_str = decoded_bytes.decode("utf-8", errors="ignore")
                cleaned += f" {decoded_str}"
            except Exception:  # noqa: S110  # pylint: disable=broad-exception-caught
                pass

        return cleaned

    def evaluate(self, cmd_text: str) -> FirewallVerdict:
        """Evaluate a shell command against deny and confirm rules."""
        if not cmd_text or not cmd_text.strip():
            return FirewallVerdict(
                verdict="ALLOW",
                reason="Empty command text",
            )

        cleaned_cmd = self.deobfuscate(cmd_text)

        # Check DENY rules first (Fail-Closed)
        for i, pat_obj in enumerate(self._compiled_deny):
            if pat_obj.search(cleaned_cmd):
                pattern_str = self.deny_rules[i]
                return FirewallVerdict(
                    verdict="DENY",
                    reason=f"Dangerous pattern matched: '{pattern_str}'",
                    matched_pattern=pattern_str,
                )

        # Check CONFIRM rules
        for i, pat_obj in enumerate(self._compiled_confirm):
            if pat_obj.search(cleaned_cmd):
                pattern_str = self.confirm_rules[i]
                return FirewallVerdict(
                    verdict="CONFIRM",
                    reason=f"Potentially risky pattern matched: '{pattern_str}'",
                    matched_pattern=pattern_str,
                )

        return FirewallVerdict(
            verdict="ALLOW",
            reason="Command verified safe by firewall.",
        )
