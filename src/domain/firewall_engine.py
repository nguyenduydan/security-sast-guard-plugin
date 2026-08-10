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
    def split_commands(cmd: str) -> list[str]:
        """Split chained or piped commands into individual statements."""
        if not cmd or not cmd.strip():
            return []

        # Split on &&, ||, ;, |, &, newlines
        sub_cmds = re.split(r"&&|\|\||;|\||&|\n", cmd)
        results: list[str] = []
        for sc in sub_cmds:
            cleaned = sc.strip()
            if cleaned:
                results.append(cleaned)
        return results if results else [cmd.strip()]

    @staticmethod
    def unpack_subcommands(cmd: str) -> list[str]:
        """Recursively unpack subcommands inside shell wrapper executions."""
        candidates = [cmd]
        if not cmd:
            return candidates

        # Match powershell/pwsh -c or -Command "..."
        ps_match = re.search(
            r"(?:powershell|pwsh)(?:\.exe)?\s+.*-(?:c|command)\s+[\"']?(.*?)[\"']?$",
            cmd,
            re.IGNORECASE,
        )
        if ps_match and ps_match.group(1):
            candidates.append(ps_match.group(1))

        # Match cmd.exe /c "..."
        cmd_match = re.search(
            r"cmd(?:\.exe)?\s+/(?:c|k)\s+[\"']?(.*?)[\"']?$",
            cmd,
            re.IGNORECASE,
        )
        if cmd_match and cmd_match.group(1):
            candidates.append(cmd_match.group(1))

        # Match bash/sh/zsh -c "..."
        sh_match = re.search(
            r"(?:bash|sh|zsh)\s+-c\s+[\"']?(.*?)[\"']?$",
            cmd,
            re.IGNORECASE,
        )
        if sh_match and sh_match.group(1):
            candidates.append(sh_match.group(1))

        # Match python -c "..."
        py_match = re.search(
            r"python[3]?\s+-c\s+[\"']?(.*?)[\"']?$",
            cmd,
            re.IGNORECASE,
        )
        if py_match and py_match.group(1):
            candidates.append(py_match.group(1))

        return candidates

    @staticmethod
    def normalize_candidates(cmd: str) -> list[str]:
        """Generate normalized variations of a command string for rule evaluation."""
        if not cmd:
            return []

        candidates: list[str] = [cmd]

        # Deobfuscated caret/backtick/base64
        deobf = FirewallEngine.deobfuscate(cmd)
        if deobf and deobf not in candidates:
            candidates.append(deobf)

        # De-quoted version
        dequoted = re.sub(r"[\"']", "", cmd)
        if dequoted and dequoted not in candidates:
            candidates.append(dequoted)

        # PowerShell Alias & Flag Expansion
        for base_str in list(candidates):
            expanded = base_str
            # Expand PowerShell aliases as standalone words
            expanded = re.sub(r"(?i)\brm\b", "Remove-Item", expanded)
            expanded = re.sub(r"(?i)\bri\b", "Remove-Item", expanded)
            expanded = re.sub(r"(?i)\bdel\b", "Remove-Item", expanded)
            expanded = re.sub(r"(?i)\berase\b", "Remove-Item", expanded)

            # Expand PowerShell flags -r, -rec, -rf, -fr, -f
            expanded = re.sub(
                r"(?i)(^|\s)-rf(\s|$)", r"\1-Recurse -Force\2", expanded
            )
            expanded = re.sub(
                r"(?i)(^|\s)-fr(\s|$)", r"\1-Force -Recurse\2", expanded
            )
            expanded = re.sub(r"(?i)(^|\s)-r(\s|$)", r"\1-Recurse\2", expanded)
            expanded = re.sub(r"(?i)(^|\s)-rec(\s|$)", r"\1-Recurse\2", expanded)
            expanded = re.sub(r"(?i)(^|\s)-f(\s|$)", r"\1-Force\2", expanded)

            # Git push -f -> --force expansion
            if "git" in expanded.lower() and "push" in expanded.lower():
                git_expanded = re.sub(r"(?i)(^|\s)-f(\s|$)", r"\1--force\2", expanded)
                if git_expanded not in candidates:
                    candidates.append(git_expanded)

            if expanded and expanded not in candidates:
                candidates.append(expanded)


        return candidates

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

    def _collect_all_candidates(self, cmd_text: str) -> list[str]:
        """Extract subcommands and normalized candidates from input command string."""
        sub_commands = self.split_commands(cmd_text)
        all_statements: list[str] = []
        for sc in sub_commands:
            all_statements.extend(self.unpack_subcommands(sc))

        all_candidates: list[str] = []
        for stmt in all_statements:
            for cand in self.normalize_candidates(stmt):
                if cand not in all_candidates:
                    all_candidates.append(cand)
        return all_candidates

    def evaluate(self, cmd_text: str) -> FirewallVerdict:
        """Evaluate a shell command against deny and confirm rules."""
        if not cmd_text or not cmd_text.strip():
            return FirewallVerdict(
                verdict="ALLOW",
                reason="Empty command text",
            )

        all_candidates = self._collect_all_candidates(cmd_text)
        matched_confirm_pattern: str | None = None

        # Check DENY rules first across all candidates (Fail-Closed)
        for candidate in all_candidates:
            for i, pat_obj in enumerate(self._compiled_deny):
                if pat_obj.search(candidate):
                    pattern_str = self.deny_rules[i]
                    return FirewallVerdict(
                        verdict="DENY",
                        reason=f"Dangerous pattern matched: '{pattern_str}'",
                        matched_pattern=pattern_str,
                    )

        # Check CONFIRM rules across all candidates
        for candidate in all_candidates:
            for i, pat_obj in enumerate(self._compiled_confirm):
                if pat_obj.search(candidate):
                    matched_confirm_pattern = self.confirm_rules[i]
                    break
            if matched_confirm_pattern:
                break

        if matched_confirm_pattern:
            return FirewallVerdict(
                verdict="CONFIRM",
                reason=f"Potentially risky pattern matched: '{matched_confirm_pattern}'",
                matched_pattern=matched_confirm_pattern,
            )

        return FirewallVerdict(
            verdict="ALLOW",
            reason="Command verified safe by firewall.",
        )
