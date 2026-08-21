"""Command Chain Threat Analyzer for Security SAST Guard Firewall v2.

Detects dangerous combinations of commands (e.g. download followed by execute).
"""

from __future__ import annotations

import re
from dataclasses import dataclass
from typing import Literal

ChainVerdictType = Literal["ALLOW", "CONFIRM", "DENY"]


@dataclass(frozen=True)
class ChainThreatMatch:
    """Represents a threat match found in a command chain."""

    threat_detected: bool
    verdict: ChainVerdictType
    reason: str
    trigger_command: str | None = None
    followup_command: str | None = None


DEFAULT_CHAIN_THREAT_RULES: list[tuple[str, str, ChainVerdictType, str]] = [
    (
        (
            r"(?:Invoke-WebRequest|iwr|Invoke-RestMethod|irm|curl|wget|"
            r"Net\.WebClient|DownloadString|DownloadFile|DownloadData|"
            r"bitsadmin|certutil\s+.*-urlcache|fetch)"
        ),
        (
            r"(?:Start-Process|saps|Invoke-Expression|iex|bash|sh|zsh|"
            r"python|python3|cmd|powershell|pwsh|chmod\s+\+x|\./[a-zA-Z0-9_\-\.]+)"
        ),
        "DENY",
        "Download+Execute chain detected",
    ),
    (
        (
            r"(?:Set-ExecutionPolicy\s+(?:-[a-zA-Z]+\s+)*(?:Bypass|Unrestricted|RemoteSigned)|"
            r"-(?:ep|executionpolicy)\s+(?:Bypass|Unrestricted|RemoteSigned)|"
            r"Set-ExecutionPolicy\s+.*Bypass)"
        ),
        r".+",
        "DENY",
        "Policy bypass followed by execution",
    ),
    (
        (
            r"(?:Set-MpPreference|Add-MpPreference|Disable-NetFirewallRule|"
            r"netsh\s+advfirewall|netsh\s+firewall)"
        ),
        r".+",
        "DENY",
        "Defense evasion chain detected",
    ),
    (
        r"git\s+clone\s+https?://",
        r"(?:Invoke-Expression|iex|\./install|python\s+setup|pip\s+install)",
        "CONFIRM",
        "Unverified external repository clone and execution",
    ),
    (
        r"(?:Get-ChildItem|dir|ls|Get-Content|cat|type|findstr|grep)",
        (
            r"(?:curl\b.*(?:-d|--data|-F|--form|-T)|"
            r"Invoke-WebRequest\b.*(?:-Method\s+POST|-InFile)|"
            r"Invoke-RestMethod\b.*(?:-Method\s+POST|-InFile)|"
            r"iwr\b.*(?:-Body|-InFile))"
        ),
        "CONFIRM",
        "Reconnaissance followed by exfiltration detected",
    ),
]


class FirewallChainAnalyzer:
    """Analyzes a list of chained/piped sub-commands for multi-command threats."""

    def __init__(
        self,
        rules: list[tuple[str, str, ChainVerdictType, str]] | None = None,
    ) -> None:
        self.rules = rules if rules is not None else DEFAULT_CHAIN_THREAT_RULES
        self._compiled_rules = [
            (
                re.compile(trig, re.IGNORECASE),
                re.compile(fol, re.IGNORECASE),
                verdict,
                reason,
            )
            for trig, fol, verdict, reason in self.rules
        ]

    def analyze(self, sub_commands: list[str]) -> ChainThreatMatch:
        """Analyze sequence of sub-commands for dangerous chain patterns.

        Args:
            sub_commands: Ordered list of statements split from chained/piped command.

        Returns:
            ChainThreatMatch indicating if a threat was found.
        """
        if not sub_commands or len(sub_commands) < 2:
            # Single commands or empty chains don't trigger chain threats
            # (unless single statement match)
            if len(sub_commands) == 1:
                cmd = sub_commands[0]
                for (
                    trig_re,
                    fol_re,
                    verdict,
                    reason,
                ) in self._compiled_rules:
                    # Special check if single command contains both trigger and followup
                    if trig_re.search(cmd) and fol_re.search(cmd):
                        return ChainThreatMatch(
                            threat_detected=True,
                            verdict=verdict,
                            reason=reason,
                            trigger_command=cmd,
                            followup_command=cmd,
                        )
            return ChainThreatMatch(
                threat_detected=False,
                verdict="ALLOW",
                reason="No chain threat detected",
            )

        for i, first_cmd in enumerate(sub_commands):
            for second_cmd in sub_commands[i + 1 :]:
                for (
                    trig_re,
                    fol_re,
                    verdict,
                    reason,
                ) in self._compiled_rules:
                    if trig_re.search(first_cmd) and fol_re.search(second_cmd):
                        return ChainThreatMatch(
                            threat_detected=True,
                            verdict=verdict,
                            reason=reason,
                            trigger_command=first_cmd,
                            followup_command=second_cmd,
                        )

        return ChainThreatMatch(
            threat_detected=False,
            verdict="ALLOW",
            reason="No chain threat detected",
        )
