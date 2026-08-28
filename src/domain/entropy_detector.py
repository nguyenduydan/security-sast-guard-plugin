"""High-precision Shannon Entropy and Provider Token Signature Detector."""

from __future__ import annotations

import math
import re
from typing import Any, ClassVar


class ShannonEntropyDetector:
    """Detects high-entropy secrets and provider API token signatures."""

    # Security keywords indicating credential context on the same line
    SECURITY_CONTEXT_KEYWORDS = (
        "key",
        "secret",
        "token",
        "password",
        "passwd",
        "auth",
        "api",
        "credential",
        "private",
        "bearer",
        "access",
    )

    # Provider token signature regex patterns
    SIGNATURE_PATTERNS: ClassVar[list[tuple[str, str, str, re.Pattern[str]]]] = [
        (
            "TOKEN_OPENAI",
            "OpenAI API Secret Key Leak",
            "Critical",
            re.compile(r"\b(sk-[a-zA-Z0-9]{48,}|sk-proj-[a-zA-Z0-9_-]{48,})\b"),
        ),
        (
            "TOKEN_GITHUB",
            "GitHub Personal Access Token Leak",
            "Critical",
            re.compile(
                r"\b(ghp_[A-Za-z0-9]{36}|gho_[A-Za-z0-9]{36}|github_pat_[A-Za-z0-9_]{82})\b"
            ),
        ),
        (
            "TOKEN_AWS",
            "AWS Access Key ID Leak",
            "High",
            re.compile(r"\b(AKIA|ASIA)[0-9A-Z]{16}\b"),
        ),
        (
            "TOKEN_GOOGLE",
            "Google API / Gemini Key Leak",
            "Critical",
            re.compile(r"\bAIza[0-9A-Za-z-_]{35}\b"),
        ),
        (
            "TOKEN_ANTHROPIC",
            "Anthropic Claude API Key Leak",
            "Critical",
            re.compile(r"\b(sk-ant-[a-zA-Z0-9_-]{40,})\b"),
        ),
        (
            "TOKEN_STRIPE",
            "Stripe Live API Key Leak",
            "Critical",
            re.compile(r"\b(sk_live_[0-9a-zA-Z]{24,}|rk_live_[0-9a-zA-Z]{24,})\b"),
        ),
        (
            "TOKEN_SLACK",
            "Slack Bot/User Token Leak",
            "High",
            re.compile(
                r"\b(xoxb-[0-9]{10,}-[0-9]{10,}-[a-zA-Z0-9]{24,}|"
                r"xoxp-[0-9]{10,}-[0-9]{10,}-[a-zA-Z0-9]{24,})\b"
            ),
        ),
        (
            "TOKEN_SLACK_WEBHOOK",
            "Slack Incoming Webhook Leak",
            "Critical",
            re.compile(
                r"https://hooks\.slack\.com/services/T[a-zA-Z0-9_]+/B[a-zA-Z0-9_]+/[a-zA-Z0-9_]+"
            ),
        ),
        (
            "TOKEN_TWILIO",
            "Twilio API Key Leak",
            "High",
            re.compile(r"\bSK[0-9a-fA-F]{32}\b"),
        ),
        (
            "TOKEN_SENDGRID",
            "SendGrid API Key Leak",
            "Critical",
            re.compile(r"\bSG\.[a-zA-Z0-9_-]{22}\.[a-zA-Z0-9_-]{43}\b"),
        ),
        (
            "TOKEN_DOCKER_HUB",
            "Docker Hub Access Token Leak",
            "Critical",
            re.compile(r"\bdckr_pat_[a-zA-Z0-9_-]{27}\b"),
        ),
        (
            "TOKEN_VAULT",
            "HashiCorp Vault Token Leak",
            "High",
            re.compile(r"\b(hvs\.[a-zA-Z0-9_-]{24,}|s\.[a-zA-Z0-9_-]{24,})\b"),
        ),
        (
            "TOKEN_AZURE_SAS",
            "Azure Shared Access Signature Leak",
            "High",
            re.compile(r"(?i)\b(?:sig|signature)=[a-zA-Z0-9%_-]{43,}\b"),
        ),
        (
            "TOKEN_PRIVATE_KEY",
            "Unencrypted Private Key Block",
            "Critical",
            re.compile(r"-----BEGIN (?:RSA|EC|DSA|OPENSSH|PGP)?\s*PRIVATE KEY-----"),
        ),
    ]

    UUID_REGEX = re.compile(
        r"^[0-9a-fA-F]{8}-[0-9a-fA-F]{4}-[0-9a-fA-F]{4}-[0-9a-fA-F]{4}-[0-9a-fA-F]{12}$"
    )

    STRING_LITERAL_REGEX = re.compile(
        r"""(?:"([^"\\]*(?:\\.[^"\\]*)*)"|'([^'\\]*(?:\\.[^'\\]*)*)')"""
    )

    @staticmethod
    def calculate_entropy(text: str) -> float:
        """Calculate Shannon Entropy in bits for a given text string."""
        if not text:
            return 0.0

        length = len(text)
        frequencies: dict[str, int] = {}
        for char in text:
            frequencies[char] = frequencies.get(char, 0) + 1

        entropy = 0.0
        for count in frequencies.values():
            prob = count / length
            entropy -= prob * math.log2(prob)

        return round(entropy, 4)

    @staticmethod
    def is_placeholder(candidate: str) -> bool:
        """Check if candidate string is an obvious template placeholder."""
        upper = candidate.upper()
        return any(
            p in upper
            for p in (
                "YOUR_API_KEY",
                "YOUR_KEY",
                "YOUR_TOKEN",
                "CHANGE_ME",
                "EXAMPLE_KEY",
                "SAMPLE_KEY",
                "DUMMY_KEY",
                "TEST_KEY",
                "XXXXXXXX",
                "00000000",
            )
        )

    def is_false_positive(self, candidate: str, raw_line: str) -> bool:
        """Filter out obvious false positives like UUIDs, placeholders, and URIs."""
        candidate_stripped = candidate.strip()
        if len(candidate_stripped) < 16:
            return True

        # Check unique character diversity
        if len(set(candidate_stripped)) <= 4:
            return True

        # Check for UUID / GUID
        if self.UUID_REGEX.match(candidate_stripped):
            return True

        # Check for placeholder strings
        if self.is_placeholder(candidate_stripped):
            return True

        # Check for inline data URIs
        if "data:image/" in raw_line or ";base64," in raw_line:
            return True

        # Check for public key token metadata (e.g. .NET assembly metadata)
        return "publickeytoken" in raw_line.lower()

    def has_security_context(self, line: str) -> bool:
        """Determine if line contains security or credential keywords."""
        lower_line = line.lower()
        return any(kw in lower_line for kw in self.SECURITY_CONTEXT_KEYWORDS)

    # pylint: disable=too-many-locals
    def scan_line(
        self,
        line: str,
        line_num: int,
        file_path: str,
    ) -> list[dict[str, Any]]:
        """Scan a single line for high-entropy secrets and token signatures."""
        findings: list[dict[str, Any]] = []
        stripped_line = line.strip()

        # 1. Check known signature token formats (High/Critical severity)
        for rule_id, rule_name, severity, pattern in self.SIGNATURE_PATTERNS:
            match = pattern.search(line)
            if match:
                matched_val = match.group(0)
                if not self.is_false_positive(matched_val, line):
                    findings.append(
                        {
                            "rule_id": rule_id,
                            "rule_name": rule_name,
                            "severity": severity,
                            "path": file_path,
                            "line": line_num,
                            "matched_pattern": rule_id,
                            "code_snippet": stripped_line,
                            "entropy": self.calculate_entropy(matched_val),
                            "action": "Block",
                        }
                    )

        # 2. Check high-entropy literals in security context
        if self.has_security_context(line):
            for match in self.STRING_LITERAL_REGEX.finditer(line):
                candidate = match.group(1) or match.group(2)
                if not candidate:
                    continue

                candidate_clean = candidate.strip()
                if self.is_false_positive(candidate_clean, line):
                    continue

                entropy = self.calculate_entropy(candidate_clean)
                cand_len = len(candidate_clean)

                # Hexadecimal string check (MD5/SHA/Hex Token >= 32 chars, H >= 3.4)
                is_hex = bool(re.fullmatch(r"[0-9a-fA-F]+", candidate_clean))
                if is_hex and cand_len >= 32 and entropy >= 3.4:
                    findings.append(
                        {
                            "rule_id": "HIGH_ENTROPY_SECRET",
                            "rule_name": "High-Entropy Hexadecimal Secret/Key Leak",
                            "severity": "High",
                            "path": file_path,
                            "line": line_num,
                            "matched_pattern": "HIGH_ENTROPY_HEX",
                            "code_snippet": stripped_line,
                            "entropy": entropy,
                            "action": "Block",
                        }
                    )
                    continue

                # Base64/Alphanumeric string check (>= 24 chars, H >= 4.5)
                is_base64 = bool(re.fullmatch(r"[A-Za-z0-9+/=_-]+", candidate_clean))
                if is_base64 and cand_len >= 24 and entropy >= 4.5:
                    findings.append(
                        {
                            "rule_id": "HIGH_ENTROPY_SECRET",
                            "rule_name": "High-Entropy Base64/API Key Secret Leak",
                            "severity": "Critical",
                            "path": file_path,
                            "line": line_num,
                            "matched_pattern": "HIGH_ENTROPY_BASE64",
                            "code_snippet": stripped_line,
                            "entropy": entropy,
                            "action": "Block",
                        }
                    )

        return findings
