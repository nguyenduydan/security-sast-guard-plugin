"""Firewall capability classification module for Security SAST Guard v2.

Categorizes normalized command candidates into security capability groups:
NETWORK, FILE_READ, FILE_WRITE, PROCESS_EXEC, PRIVILEGE_CHANGE, PERSISTENCE,
DATA_TRANSFER.
"""

from __future__ import annotations

import re

CAPABILITY_GROUPS: dict[str, list[str]] = {
    "NETWORK": [
        r"\b(?:curl|wget|nc|netcat|nmap|tftp|ping|nslookup|dig|ssh|telnet)\b",
        (
            r"\b(?:Invoke-WebRequest|iwr|Invoke-RestMethod|irm|"
            r"System\.Net\.WebClient|Net\.WebClient|bitsadmin|certutil)\b"
        ),
        r"https?://",
    ],
    "FILE_READ": [
        r"\b(?:Get-Content|gc|cat|type|head|tail|more|less|read|grep|findstr)\b",
        r"(?:-d|--data|--data-binary|--data-raw|-T|--upload-file)\s+@\S+",
        r"<\s*\S+",
    ],
    "FILE_WRITE": [
        r"\b(?:Set-Content|sc|Out-File|Add-Content|ac|tee|touch)\b",
        r"(?:>|>>)\s*\S+",
        r"(?:-o|--output|-O|--remote-name-all)\s+\S+",
    ],
    "PROCESS_EXEC": [
        (
            r"\b(?:Start-Process|saps|Invoke-Expression|iex|bash|sh|zsh|csh|ksh|"
            r"python|python3|cmd|powershell|pwsh|wmic|eval|exec)\b"
        ),
        r"\.(?:py|sh|ps1|bat|exe)\b",
    ],
    "PRIVILEGE_CHANGE": [
        r"\b(?:sudo|runas|Set-ExecutionPolicy|su|chmod|chown|whoami\s+/priv)\b",
        (
            r"(?:Set-ExecutionPolicy|-(?:ep|executionpolicy))\s+"
            r"(?:Bypass|Unrestricted|RemoteSigned)"
        ),
    ],
    "PERSISTENCE": [
        r"\b(?:schtasks|crontab|systemctl\s+enable|launchctl)\b",
        r"\breg(?:\.exe)?\s+add\b",
        r"HKCU\\Software\\Microsoft\\Windows\\CurrentVersion\\Run",
        r"HKLM\\Software\\Microsoft\\Windows\\CurrentVersion\\Run",
    ],
    "DATA_TRANSFER": [
        r"\b(?:ftp|scp|rsync|sftp|tftp|Start-BitsTransfer|bitsadmin)\b",
        r"curl\b.*(?:-X\s*POST|-d|--data|-F|--form|-T|--upload-file)",
        (
            r"(?:Invoke-WebRequest|iwr|Invoke-RestMethod|irm)\b.*"
            r"(?:-Method\s+POST|-InFile|-OutFile|-Body)"
        ),
        r"(?:-X\s*POST|--request\s+POST)\b",
    ],
}


class FirewallCapabilityClassifier:
    """Classifies command candidates into security capabilities."""

    def __init__(
        self,
        groups: dict[str, list[str]] | None = None,
    ) -> None:
        """Initialize classifier with compiled regex patterns."""
        target_groups = groups if groups is not None else CAPABILITY_GROUPS
        self._compiled_groups: dict[str, list[re.Pattern[str]]] = {
            group: [re.compile(p, re.IGNORECASE) for p in patterns]
            for group, patterns in target_groups.items()
        }

    def classify(self, candidates: list[str]) -> set[str]:
        """Returns set of matched capability labels for candidates.

        Args:
            candidates: List of candidate command strings.

        Returns:
            Set of capability names matched across any candidate string.
        """
        matched: set[str] = set()
        if not candidates:
            return matched

        for candidate in candidates:
            for group_name, patterns in self._compiled_groups.items():
                if group_name in matched:
                    continue
                for pattern in patterns:
                    if pattern.search(candidate):
                        matched.add(group_name)
                        break

        return matched
