"""Firewall intent classification module for Security SAST Guard v2.

Infers high-level threat intent labels and confidence levels based on
the detected capabilities and command candidates.
"""

from __future__ import annotations

import re
from collections.abc import Sequence

DEFAULT_INTENT_RULES: list[tuple[set[str], set[str], str, float]] = [
    ({"NETWORK", "DATA_TRANSFER", "FILE_READ"}, set(), "EXFILTRATION", 0.85),
    ({"FILE_WRITE", "PROCESS_EXEC"}, set(), "DESTRUCTIVE", 0.70),
    ({"PERSISTENCE"}, set(), "PERSISTENCE", 0.90),
    ({"PRIVILEGE_CHANGE"}, set(), "PRIVILEGE_ESCALATION", 0.80),
    ({"NETWORK", "PROCESS_EXEC"}, set(), "SUPPLY_CHAIN", 0.75),
    ({"LATERAL_MOVEMENT"}, set(), "LATERAL_MOVEMENT", 0.90),
]

ANTI_FORENSICS_PATTERNS: list[str] = [
    r"\b(?:Clear-EventLog|wevtutil(?:\.exe)?\s+cl|history\s+-c)\b",
    r"\brm\s+-(?:rf?|fr?)\s+/var/log\b",
    r"\bRemove-EventLog\b",
]


class FirewallIntentClassifier:
    """Classifies security intent from capabilities and candidate strings."""

    def __init__(
        self,
        intent_rules: Sequence[tuple[set[str], set[str], str, float]] | None = None,
        anti_forensics_patterns: Sequence[str] | None = None,
    ) -> None:
        """Initialize intent classifier with rules and patterns."""
        target_rules = (
            intent_rules if intent_rules is not None else DEFAULT_INTENT_RULES
        )
        self.rules = list(target_rules)
        af_patterns = (
            anti_forensics_patterns
            if anti_forensics_patterns is not None
            else ANTI_FORENSICS_PATTERNS
        )
        self._anti_forensics_compiled = [
            re.compile(p, re.IGNORECASE) for p in af_patterns
        ]

    def classify(
        self,
        candidates: list[str],
        capabilities: set[str],
    ) -> tuple[str | None, float]:
        """Classify intent from candidate strings and matched capabilities.

        Args:
            candidates: List of candidate command strings.
            capabilities: Set of matched capability labels.

        Returns:
            Tuple of (intent_label, confidence). Returns (None, 0.0) if no match.
        """
        # 1. Check Anti-Forensics pattern match on candidate strings
        for candidate in candidates:
            for pattern in self._anti_forensics_compiled:
                if pattern.search(candidate):
                    return ("ANTI_FORENSICS", 0.85)

        # 2. Match intent rules against capabilities set
        best_match: tuple[str | None, float] = (None, 0.0)
        highest_confidence = 0.0

        for req_caps, forbidden_caps, intent_label, confidence in self.rules:
            is_matched = req_caps.issubset(capabilities) and forbidden_caps.isdisjoint(
                capabilities
            )
            if is_matched and confidence > highest_confidence:
                highest_confidence = confidence
                best_match = (intent_label, confidence)

        return best_match
