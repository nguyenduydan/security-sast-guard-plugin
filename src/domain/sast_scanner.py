"""SAST Scanner domain component."""

import json
import re
from pathlib import Path
from typing import Any

from .context_extractor import extract_context


class SASTScanner:
    """SAST rule scanner implementation."""

    def __init__(
        self,
        profile_path: str = "profile.json",
        rules_path: str = "rules/sast_rules.json",
    ):
        self.profile_path = profile_path
        self.rules_path = rules_path
        self.mode = "strict"
        self._rules_cache: list[dict[str, Any]] | None = None
        self._load_profile()

    def _load_profile(self) -> None:
        try:
            with open(self.profile_path, encoding="utf-8") as f:
                profile = json.load(f)
                self.mode = profile.get("mode", "strict")
        except FileNotFoundError:
            pass

    def _get_rules_path(self) -> Path:
        p = Path(self.rules_path)
        if not p.exists():
            repo_root = Path(__file__).parents[2]
            p = repo_root / self.rules_path
        return p

    def _load_rules(self) -> list[dict[str, Any]]:
        if self._rules_cache is not None:
            return self._rules_cache

        rules_file = self._get_rules_path()
        if not rules_file.exists():
            self._rules_cache = []
            return self._rules_cache

        try:
            with open(rules_file, encoding="utf-8") as f:
                self._rules_cache = json.load(f)
        except (json.JSONDecodeError, OSError):
            self._rules_cache = []

        return self._rules_cache or []

    def _is_valid_pattern(self, pattern: str) -> bool:
        """Check if a regex pattern is valid and not a markdown junk pattern."""
        if not pattern:
            return False
        stripped = pattern.strip()
        if not stripped:
            return False

        # Trivial single-character or punctuation junk patterns
        if stripped in (
            r"\ ",
            r"\)",
            r"\(",
            r"\\",
            r"\/",
            r" ",
            ")",
            "(",
            "\\",
            "/",
            "-",
            "--",
            "---",
            r"\|",
            ">",
            "<",
            "=",
            '"',
            "'",
            ":",
            ";",
            ",",
            ".",
            "!",
            "?",
        ):
            return False

        # Markdown blockquotes, documentation, HTTP examples, table borders
        return not (
            stripped.startswith(">")
            or stripped.startswith(r"\*")
            or stripped.startswith(r"\-")
            or stripped.startswith(r"\\*")
            or stripped.startswith(r"\\-")
            or stripped.startswith("→")
            or stripped.startswith("- [")
            or stripped.startswith("* [")
            or stripped.startswith("GET ")
            or stripped.startswith("POST ")
            or stripped.startswith("PUT ")
            or stripped.startswith("DELETE ")
            or stripped.startswith("PATCH ")
            or stripped.startswith("|")
            or stripped.startswith(r"\|")
        )

    def _detect_matches(self, path: str) -> list[dict[str, Any]]:
        """Match target file content against loaded SAST rules."""
        file_path = Path(path)
        if not file_path.exists():
            return []

        rules = self._load_rules()
        findings: list[dict[str, Any]] = []

        try:
            with open(file_path, encoding="utf-8", errors="replace") as f:
                lines = f.readlines()
        except OSError:
            return []

        for line_idx, raw_line in enumerate(lines, 1):
            line_content = raw_line.rstrip("\r\n")
            stripped = line_content.strip()

            # Skip single-line comment lines
            if stripped.startswith("#") or stripped.startswith("//"):
                continue

            for rule in rules:
                patterns = rule.get("patterns", [])
                if not patterns:
                    continue

                matched = False
                for pattern in patterns:
                    if not self._is_valid_pattern(pattern):
                        continue
                    try:
                        if re.search(pattern, line_content):
                            matched = True
                            break
                    except re.error:
                        continue

                if matched:
                    ctx = extract_context(path, line_idx)
                    if ctx.get("is_safe_context"):
                        continue

                    finding = {
                        "rule_id": rule.get("id", "UNKNOWN"),
                        "rule_name": rule.get("name", "Unknown Rule"),
                        "path": path,
                        "line": line_idx,
                        "line_content": ctx.get("line_content", line_content),
                        "severity": rule.get("severity", "MEDIUM"),
                        "scope": ctx.get("scope", "global"),
                    }
                    findings.append(finding)

        return findings

    def scan(self, path: str, interactive: bool = False) -> list[dict[str, Any]]:
        """Scan specified file path for SAST rule matches."""
        matches = self._detect_matches(path)
        if not interactive:
            return matches

        violations: list[dict[str, Any]] = []
        for match in matches:
            rule_name = (
                match.get("rule_name")
                or match.get("rule_id")
                or match.get("rule", "Unknown")
            )
            line_no = match.get("line", 0)
            severity = match.get("severity", "MEDIUM")
            line_content = match.get("line_content", "")
            scope = match.get("scope", "global")

            print(f"[SAST WARNING] Potential {rule_name} at `{path}:{line_no}`.")
            print(f"- Severity: {severity}")
            print(f"- Line: `{str(line_content).strip()}`")
            print(f"- Scope: `{scope}`")

            if self.mode == "draft" and str(severity).upper() in ("MEDIUM", "LOW"):
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
