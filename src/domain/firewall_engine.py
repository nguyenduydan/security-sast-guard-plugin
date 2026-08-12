"""Firewall Engine Module for Security SAST Guard.

Provides cross-platform command safety evaluation, de-obfuscation,
intent classification, chain threat analysis, and rule checking.
"""

from __future__ import annotations

import base64
import re
from dataclasses import dataclass
from functools import lru_cache
from typing import Literal

from src.domain.firewall_capability import FirewallCapabilityClassifier
from src.domain.firewall_chain import FirewallChainAnalyzer
from src.domain.firewall_intent import FirewallIntentClassifier
from src.domain.firewall_normalizer import FirewallNormalizer
from src.domain.models import FirewallVerdictV2

VerdictType = Literal["ALLOW", "CONFIRM", "DENY"]


@dataclass(frozen=True)
class FirewallVerdict:
    """Represents the verdict of a firewall command evaluation (v1 legacy model)."""

    verdict: VerdictType
    reason: str
    matched_pattern: str | None = None


# pylint: disable=too-many-instance-attributes,too-many-locals,too-many-branches
class FirewallEngine:
    """Cross-platform command evaluation engine with multi-stage normalization."""

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
        self.normalizer = FirewallNormalizer()
        self.capability_classifier = FirewallCapabilityClassifier()
        self.intent_classifier = FirewallIntentClassifier()
        self.chain_analyzer = FirewallChainAnalyzer()

    @staticmethod
    def split_commands(cmd: str) -> list[str]:
        """Split chained or piped commands into individual statements."""
        if not cmd or not cmd.strip():
            return []

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

        ps_match = re.search(
            r"(?:powershell|pwsh)(?:\.exe)?\s+.*-(?:c|command)\s+[\"']?(.*?)[\"']?$",
            cmd,
            re.IGNORECASE,
        )
        if ps_match and ps_match.group(1):
            candidates.append(ps_match.group(1))

        cmd_match = re.search(
            r"cmd(?:\.exe)?\s+/(?:c|k)\s+[\"']?(.*?)[\"']?$",
            cmd,
            re.IGNORECASE,
        )
        if cmd_match and cmd_match.group(1):
            candidates.append(cmd_match.group(1))

        sh_match = re.search(
            r"(?:bash|sh|zsh)\s+-c\s+[\"']?(.*?)[\"']?$",
            cmd,
            re.IGNORECASE,
        )
        if sh_match and sh_match.group(1):
            candidates.append(sh_match.group(1))

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

        normalizer = FirewallNormalizer()
        return normalizer.normalize(cmd)

    @staticmethod
    @lru_cache(maxsize=2048)
    def deobfuscate(cmd: str) -> str:
        """Strip de-obfuscation artifacts such as carets and backticks."""
        if not cmd:
            return ""

        cleaned = cmd.replace("^", "").replace("`", "")

        base64_match = re.search(
            r"(?:-e|-enc|-encodedcommand)\s+([A-Za-z0-9+/=]+)",
            cleaned,
            re.IGNORECASE,
        )
        if base64_match:
            try:
                encoded_str = base64_match.group(1)
                decoded_bytes = base64.b64decode(encoded_str)
                try:
                    decoded_str = decoded_bytes.decode("utf-16le")
                except UnicodeDecodeError:
                    decoded_str = decoded_bytes.decode("utf-8", errors="ignore")
                cleaned += f" {decoded_str}"
            except Exception:  # noqa: S110 # pylint: disable=broad-exception-caught
                pass

        return cleaned

    def _collect_all_candidates(self, cmd_text: str) -> list[str]:
        """Extract subcommands and normalized candidates from input command string."""
        return self.normalizer.normalize(cmd_text)

    def evaluate_v2(self, cmd_text: str) -> FirewallVerdictV2:
        """Evaluate shell command with full v2 pipeline."""
        if not cmd_text or not cmd_text.strip():
            return FirewallVerdictV2(
                verdict="ALLOW",
                intent_label=None,
                capability_set=[],
                risk_score=0.0,
                confidence=1.0,
                matched_patterns=[],
                deobfuscated_form="",
                chain_threat=False,
                reason="Empty command text",
                recommended_action="Allow execution",
            )

        all_candidates = self.normalizer.normalize(cmd_text)
        deobf_form = all_candidates[1] if len(all_candidates) > 1 else all_candidates[0]
        sub_cmds = self.split_commands(cmd_text)

        # 1. Chain Threat Analysis
        chain_res = self.chain_analyzer.analyze(sub_cmds)

        # 2. Capability & Intent Classification
        capabilities = self.capability_classifier.classify(all_candidates)
        cap_list = sorted(capabilities)
        intent_label, intent_conf = self.intent_classifier.classify(
            all_candidates, capabilities
        )

        matched_deny_pattern: str | None = None
        matched_confirm_pattern: str | None = None

        # 3. Rule Matching (Fail-Closed DENY first)
        for candidate in all_candidates:
            for i, pat_obj in enumerate(self._compiled_deny):
                if pat_obj.search(candidate):
                    matched_deny_pattern = self.deny_rules[i]
                    break
            if matched_deny_pattern:
                break

        if not matched_deny_pattern:
            for candidate in all_candidates:
                for i, pat_obj in enumerate(self._compiled_confirm):
                    if pat_obj.search(candidate):
                        matched_confirm_pattern = self.confirm_rules[i]
                        break
                if matched_confirm_pattern:
                    break

        # Compute Verdict & Risk Score
        if matched_deny_pattern or (
            chain_res.threat_detected and chain_res.verdict == "DENY"
        ):
            reason = (
                chain_res.reason
                if (chain_res.threat_detected and chain_res.verdict == "DENY")
                else f"Dangerous pattern matched: '{matched_deny_pattern}'"
            )
            matched_pats = (
                [matched_deny_pattern] if matched_deny_pattern else [chain_res.reason]
            )
            return FirewallVerdictV2(
                verdict="DENY",
                intent_label=intent_label or "DESTRUCTIVE",
                capability_set=cap_list,
                risk_score=0.95,
                confidence=intent_conf,
                matched_patterns=matched_pats,
                deobfuscated_form=deobf_form,
                chain_threat=chain_res.threat_detected,
                reason=reason,
                recommended_action="Block execution immediately",
            )

        if matched_confirm_pattern or (
            chain_res.threat_detected and chain_res.verdict == "CONFIRM"
        ):
            reason = (
                chain_res.reason
                if (chain_res.threat_detected and chain_res.verdict == "CONFIRM")
                else f"Potentially risky pattern matched: '{matched_confirm_pattern}'"
            )
            matched_pats = (
                [matched_confirm_pattern]
                if matched_confirm_pattern
                else [chain_res.reason]
            )
            return FirewallVerdictV2(
                verdict="CONFIRM",
                intent_label=intent_label,
                capability_set=cap_list,
                risk_score=0.65,
                confidence=intent_conf,
                matched_patterns=matched_pats,
                deobfuscated_form=deobf_form,
                chain_threat=chain_res.threat_detected,
                reason=reason,
                recommended_action="Prompt user for explicit approval",
            )

        if (
            intent_label in ("DESTRUCTIVE", "EXFILTRATION", "ANTI_FORENSICS")
            and intent_conf >= 0.85
        ):
            return FirewallVerdictV2(
                verdict="DENY",
                intent_label=intent_label,
                capability_set=cap_list,
                risk_score=0.90,
                confidence=intent_conf,
                matched_patterns=[f"Intent:{intent_label}"],
                deobfuscated_form=deobf_form,
                chain_threat=False,
                reason=f"High risk intent detected: {intent_label}",
                recommended_action="Block execution immediately",
            )

        return FirewallVerdictV2(
            verdict="ALLOW",
            intent_label=intent_label,
            capability_set=cap_list,
            risk_score=0.10,
            confidence=intent_conf,
            matched_patterns=[],
            deobfuscated_form=deobf_form,
            chain_threat=False,
            reason="Command verified safe by firewall",
            recommended_action="Allow execution",
        )

    def evaluate(self, cmd_text: str) -> FirewallVerdict:
        """Evaluate shell command (v1 interface for backward compatibility)."""
        v2_res = self.evaluate_v2(cmd_text)
        pattern = v2_res.matched_patterns[0] if v2_res.matched_patterns else None
        return FirewallVerdict(
            verdict=v2_res.verdict,
            reason=v2_res.reason,
            matched_pattern=pattern,
        )
