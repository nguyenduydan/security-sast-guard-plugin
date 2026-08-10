"""SAST Scanner domain component."""

import json
import os
import re
import time
from pathlib import Path
from typing import Any

from .ai_verifier import AIVerifier
from .ast_context_engine import ASTContextEngine
from .context_extractor import ContextExtractor
from .git_helper import GitHelper
from .ignore_filter import IgnoreFilter
from .models import Finding


class SASTScanner:
    """SAST rule scanner implementation."""

    def __init__(
        self,
        profile_path: str = "profile.json",
        rules_path: str = "rules/sast_rules.json",
        rules: list[dict[str, Any]] | None = None,
    ):
        self.profile_path = profile_path
        self.rules_path = rules_path
        self.mode = "strict"
        self._rules_cache: list[dict[str, Any]] | None = rules
        self.ai_verifier = AIVerifier()
        self.ast_engine = ASTContextEngine()
        self.context_extractor = ContextExtractor()
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
                loaded = json.load(f)
                for r in loaded:
                    compiled = []
                    for pat in r.get("patterns", []):
                        if self._is_valid_pattern(pat):
                            try:
                                compiled.append(re.compile(pat))
                            except re.error:
                                pass
                    r["_compiled_patterns"] = compiled
                self._rules_cache = loaded
        except (json.JSONDecodeError, OSError):
            self._rules_cache = []

        return self._rules_cache or []

    def get_rules(self, force_reload: bool = False) -> list[dict[str, Any]]:
        """Return loaded SAST rules, optionally forcing a reload from disk."""
        if force_reload:
            self._rules_cache = None
        return self._load_rules()

    def _is_valid_pattern(self, pattern: str) -> bool:
        """Check if a regex pattern is valid and not a markdown junk pattern."""
        if not pattern:
            return False
        stripped = pattern.strip()
        if not stripped:
            return False

        # Trivial single-character or punctuation junk patterns
        if len(stripped.replace("\\", "")) <= 1:
            return False

        if stripped in (
            "-",
            "--",
            "---",
            r"\|",
            ">",
            "<",
            "=",
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

    def _rule_matches_line(self, line_content: str, rule: dict[str, Any]) -> bool:
        compiled = rule.get("_compiled_patterns")
        if compiled is not None:
            for pat_obj in compiled:
                if pat_obj.search(line_content):
                    return True
            return False

        for pattern in rule.get("patterns", []):
            if not self._is_valid_pattern(pattern):
                continue
            try:
                if re.search(pattern, line_content):
                    return True
            except re.error:
                continue
        return False

    @staticmethod
    def _is_suppressed(
        line_content: str,
        prev_line_content: str | None,
        rule_id: str,
    ) -> bool:
        """Check if finding for rule_id is suppressed on current or prev line."""
        suppression_pattern = re.compile(
            r"(?:#|//|/\*|<!--)\s*sast-(?:ignore|disable|allow)(?:\s*([a-zA-Z0-9_,\s-]*))?",
            re.IGNORECASE,
        )

        def line_suppresses(text: str) -> bool:
            for match in suppression_pattern.finditer(text):
                targets_str = match.group(1)
                if not targets_str or not targets_str.strip():
                    return True
                targets = [
                    t.strip().upper()
                    for t in re.split(r"[,;|\s]+", targets_str)
                    if t.strip()
                ]
                if rule_id.upper() in targets or "ALL" in targets:
                    return True
            return False

        return line_suppresses(line_content) or bool(
            prev_line_content and line_suppresses(prev_line_content)
        )

    # pylint: disable=too-many-locals
    def _detect_matches_file(
        self, file_path: Path, rules: list[dict[str, Any]]
    ) -> tuple[list[dict[str, Any]], int]:
        """Match single file content against loaded SAST rules.

        Returns (findings, line_count).
        """
        findings: list[dict[str, Any]] = []

        try:
            with open(file_path, encoding="utf-8", errors="replace") as f:
                lines = f.readlines()
        except OSError:
            return [], 0

        line_count = len(lines)
        str_path = str(file_path)
        prev_line: str | None = None

        for line_idx, raw_line in enumerate(lines, 1):
            line_content = raw_line.rstrip("\r\n")
            stripped = line_content.strip()

            is_comment_only = (
                stripped.startswith("#")
                or stripped.startswith("//")
                or stripped.startswith("/*")  # sast-ignore WILDCARD_PATH
                or stripped.startswith("<!--")
            )

            if not is_comment_only:
                scope = self.ast_engine.resolve_scope(str_path, line_idx, line_content)
                for rule in rules:
                    target_scopes = rule.get("target_scopes")
                    if (
                        target_scopes
                        and scope not in target_scopes
                        and scope != "global"
                    ):
                        continue

                    excluded_scopes = rule.get("excluded_scopes")
                    if excluded_scopes and scope in excluded_scopes:
                        continue

                    rule_id = rule.get("id", "UNKNOWN")
                    if self._rule_matches_line(line_content, rule):
                        if self._is_suppressed(line_content, prev_line, rule_id):
                            continue
                        ctx = self.context_extractor.extract_context_from_lines(
                            lines, line_idx, str_path
                        )
                        if ctx.get("is_safe_context"):
                            continue

                        findings.append(
                            {
                                "rule_id": rule_id,
                                "rule_name": rule.get("name", "Unknown Rule"),
                                "path": str_path,
                                "line": line_idx,
                                "line_content": ctx.get("line_content", line_content),
                                "severity": rule.get("severity", "MEDIUM"),
                                "scope": (
                                    scope
                                    if scope != "global"
                                    else ctx.get("scope", "global")
                                ),
                                "action": rule.get("action", "Block"),
                                "remediation": rule.get("remediation"),
                            }
                        )

            prev_line = line_content

        return findings, line_count

    # pylint: disable=too-many-locals,too-many-branches,too-many-statements
    def scan_with_metadata(
        self,
        path: str,
        interactive: bool = False,
        incremental: bool = False,
    ) -> dict[str, Any]:
        """Scan file or directory with full metadata tracking."""
        start_time = time.perf_counter()
        target_path = Path(path).resolve()

        rules = self._load_rules()
        raw_findings: list[dict[str, Any]] = []

        scanned_files = 0
        ignored_files = 0
        total_lines = 0

        root_dir = target_path if target_path.is_dir() else target_path.parent
        ignore_filter = IgnoreFilter(root_dir=root_dir)

        if not target_path.exists():
            duration = time.perf_counter() - start_time
            return {
                "findings": [],
                "metadata": {
                    "scanned_files": 0,
                    "ignored_files": 0,
                    "total_lines": 0,
                    "rules_applied": len(rules),
                    "false_positives_filtered": 0,
                    "incremental_mode": False,
                    "duration_seconds": round(duration, 3),
                },
            }

        files_to_scan: list[Path] = []
        is_incremental = False

        if target_path.is_file():
            files_to_scan = [target_path]
        elif incremental and GitHelper.is_git_repo(target_path):
            git_files = GitHelper.get_changed_files(target_path)
            if git_files:
                is_incremental = True
                files_to_scan = git_files

        if not files_to_scan and target_path.is_dir():
            # Perform top-down os.walk with early directory pruning
            for root, dirs, files in os.walk(target_path):
                pruned_dirs = [d for d in dirs if ignore_filter.should_ignore_dir(d)]
                ignored_files += len(pruned_dirs)
                dirs[:] = [d for d in dirs if not ignore_filter.should_ignore_dir(d)]
                for file_name in files:
                    file_p = Path(root) / file_name
                    if ignore_filter.should_ignore(file_p):
                        ignored_files += 1
                    else:
                        files_to_scan.append(file_p)

        for file_path in files_to_scan:
            # Explicit single file targets bypass default extension/path ignore rules
            if (
                target_path.is_file()
                and target_path != file_path
                and ignore_filter.should_ignore(file_path)
            ):
                ignored_files += 1
                continue

            matches = self._detect_matches(str(file_path))
            try:
                with open(file_path, encoding="utf-8", errors="replace") as f:
                    lines_count = len(f.readlines())
            except OSError:
                lines_count = 0

            scanned_files += 1
            total_lines += lines_count

            if interactive and matches:
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

                    msg = (
                        f"[SAST WARNING] Potential {rule_name} at "
                        f"`{file_path}:{line_no}`."
                    )
                    print(msg)
                    print(f"- Severity: {severity}")
                    print(f"- Line: `{str(line_content).strip()}`")
                    print(f"- Scope: `{scope}`")

                    if self.mode == "draft" and str(severity).upper() in (
                        "MEDIUM",
                        "LOW",
                    ):
                        print(
                            ">> [DRAFT MODE] Auto-allowing low/medium severity finding "
                            "to preserve vibe."
                        )
                        continue

                    prompt_msg = (
                        "? Is this context safe? (Reply Y to allow, N to block): "
                    )
                    answer = input(prompt_msg).strip().upper()
                    if answer != "Y":
                        raw_findings.append(match)
            else:
                raw_findings.extend(matches)

        # Stage 2: AI Context Verification Gate (Filter False Positives)
        verified_findings, fp_count = self.ai_verifier.filter_false_positives(
            raw_findings
        )

        duration = time.perf_counter() - start_time
        metadata = {
            "scanned_files": scanned_files,
            "ignored_files": ignored_files,
            "total_lines": total_lines,
            "rules_applied": len(rules),
            "false_positives_filtered": fp_count,
            "incremental_mode": is_incremental,
            "duration_seconds": round(duration, 3),
        }

        return {
            "findings": verified_findings,
            "metadata": metadata,
        }

    def _detect_matches(self, path: str) -> list[dict[str, Any]]:
        """Match target file content against loaded SAST rules (legacy helper)."""
        file_path = Path(path)
        if not file_path.exists() or file_path.is_dir():
            return []
        rules = self._load_rules()
        findings, _ = self._detect_matches_file(file_path, rules)
        return findings

    def scan(self, path: str, interactive: bool = False) -> list[dict[str, Any]]:
        """Scan specified file or directory path for SAST rule matches."""
        result = self.scan_with_metadata(path, interactive=interactive)
        findings: list[dict[str, Any]] = result["findings"]
        return findings

    # pylint: disable=too-many-locals
    def scan_code(self, code: str, filename: str = "sample.py") -> list[Finding]:
        """Scan code string directly and return list of Finding domain objects."""
        rules = self._load_rules()
        findings: list[Finding] = []
        lines = code.splitlines()

        prev_line: str | None = None
        for line_idx, raw_line in enumerate(lines, 1):
            line_content = raw_line.rstrip("\r\n")
            stripped = line_content.strip()

            is_comment_only = (
                stripped.startswith("#")
                or stripped.startswith("//")
                or stripped.startswith("/*")  # sast-ignore WILDCARD_PATH
                or stripped.startswith("<!--")
            )

            if not is_comment_only:
                scope = self.ast_engine.resolve_scope(filename, line_idx, line_content)
                for rule in rules:
                    excluded_scopes = rule.get("excluded_scopes", [])
                    if excluded_scopes and scope in excluded_scopes:
                        continue
                    target_scopes = rule.get("target_scopes", [])
                    if (
                        target_scopes
                        and scope not in target_scopes
                        and scope != "global"
                    ):
                        continue

                    rule_id = rule.get("id", "UNKNOWN")
                    if self._rule_matches_line(line_content, rule):
                        if self._is_suppressed(line_content, prev_line, rule_id):
                            continue
                        findings.append(
                            Finding(
                                rule_id=rule_id,
                                rule_name=rule.get("name", "Unknown Rule"),
                                path=filename,
                                line=line_idx,
                                line_content=line_content,
                                severity=rule.get("severity", "MEDIUM"),
                                scope=scope,
                                action=rule.get("action", "Block"),
                                remediation=rule.get("remediation"),
                            )
                        )
            prev_line = line_content
        return findings
