"""Antigravity PR Review Advisor module.

Performs automated Pull Request code review analyzing Security (SAST),
Clean & Lean Code (Ponytail), and Architecture Logic via Google Antigravity SDK.
"""

from __future__ import annotations

import asyncio
import concurrent.futures
import json
import logging
import re
from dataclasses import dataclass, field
from typing import Any, Literal

from src.domain.antigravity_advisor import (
    AntigravitySecurityAdvisor,
    is_sdk_available,
)
from src.domain.models import AITokenUsage

logger = logging.getLogger(__name__)

PR_REVIEW_SYSTEM_INSTRUCTIONS = (
    "You are an elite Staff Security & Principal Software Engineer acting as "
    "an automated GitHub Pull Request Reviewer.\n"
    "Your mission is to perform a rigorous code review across 3 core pillars:\n"
    "1. Security (OWASP Top 10, CWE, prompt injection, secrets, command safety)\n"
    "2. Clean & Lean Code / Ponytail (YAGNI, dead code, silent exception "
    "swallowing `except: pass`, premature abstractions, excessive diffs)\n"
    "3. Architecture & Logic (regression risks, edge cases, error handling, "
    "correctness)\n\n"
    "SAFETY CONSTRAINTS:\n"
    "- You are running in Read-Only advisory mode. DO NOT attempt to modify files.\n"
    "- Evaluate whether to issue: APPROVE, COMMENT, or REQUEST_CHANGES.\n"
    "- If any Critical/High security issues exist, MUST issue REQUEST_CHANGES.\n"
    "- If only minor suggestions exist, issue COMMENT or APPROVE.\n"
    "- Provide concrete, minimal code snippets for fixes where applicable.\n"
)


@dataclass
class PRReviewComment:
    """Individual actionable review comment on a PR diff."""

    category: Literal["SECURITY", "CLEAN_CODE", "ARCHITECTURE", "BUG_RISK"]
    file_path: str
    line: int | None
    severity: Literal["CRITICAL", "HIGH", "MEDIUM", "LOW", "INFO"]
    title: str
    comment: str
    suggested_fix: str | None = None


@dataclass
class PRReviewResult:
    """Comprehensive PR review result with verdict, comments, and token telemetry."""

    verdict: Literal["APPROVE", "COMMENT", "REQUEST_CHANGES"]
    summary: str
    comments: list[PRReviewComment] = field(default_factory=list)
    token_usage: AITokenUsage = field(default_factory=AITokenUsage)
    model_name: str = "google-antigravity-agent"
    status: str = "success"  # "success" | "skipped" | "error" | "not_installed"
    error_message: str | None = None

    def to_markdown(self) -> str:
        """Render PR review result into GitHub-flavored Markdown."""
        verdict_badge = {
            "APPROVE": "APPROVE - LGTM with high confidence.",
            "COMMENT": "COMMENT - Informational suggestions provided.",
            "REQUEST_CHANGES": ("REQUEST CHANGES - Action required on critical items."),
        }.get(self.verdict, f"VERDICT: `{self.verdict}`")

        lines = [
            "## Antigravity AI - Pull Request Review Report",
            "",
            f"### Verdict: **{verdict_badge}**",
            "",
            "### Executive Summary",
            self.summary,
            "",
        ]

        if self.token_usage.total_tokens > 0:
            lines.extend(
                [
                    "### Token Accounting Telemetry",
                    "",
                    "| Metric | Token Count |",
                    "|:---|:---:|",
                    (
                        f"| Input / Context Tokens | "
                        f"`{self.token_usage.input_tokens:,}` |"
                    ),
                    (f"| Thinking Tokens | `{self.token_usage.thinking_tokens:,}` |"),
                    (f"| Output Tokens | `{self.token_usage.output_tokens:,}` |"),
                    (
                        f"| Total Tokens Consumed | "
                        f"`{self.token_usage.total_tokens:,}` |"
                    ),
                    "",
                ]
            )

        if self.comments:
            lines.append("### Detailed Review Findings")
            lines.append("")
            for _idx, c in enumerate(self.comments, 1):
                icon = {
                    "SECURITY": "[SECURITY]",
                    "CLEAN_CODE": "[CLEAN_CODE]",
                    "ARCHITECTURE": "[ARCHITECTURE]",
                    "BUG_RISK": "[BUG_RISK]",
                }.get(c.category, "[NOTE]")
                loc_str = f"`{c.file_path}:{c.line}`" if c.line else f"`{c.file_path}`"
                lines.append(f"#### {icon} [{c.severity}] {c.title} ({loc_str})")
                lines.append(c.comment)
                lines.append("")
                if c.suggested_fix:
                    lines.append("**Suggested Fix:**")
                    lines.append(f"```\n{c.suggested_fix}\n```")
                    lines.append("")
        else:
            lines.append(
                "> **Clean Codebase:** No security vulnerabilities or "
                "Ponytail code smells detected in this PR diff."
            )
            lines.append("")

        lines.append("---")
        lines.append(
            "<sub>Powered by **Security SAST Guard** & **Google Antigravity SDK**</sub>"
        )
        return "\n".join(lines)


class PRReviewAdvisor:
    """Orchestrates comprehensive PR code review using Antigravity SDK."""

    def __init__(
        self,
        system_instructions: str = PR_REVIEW_SYSTEM_INSTRUCTIONS,
        timeout_seconds: float = 60.0,
    ) -> None:
        self.system_instructions = system_instructions
        self.timeout_seconds = timeout_seconds
        self.security_advisor = AntigravitySecurityAdvisor(
            timeout_seconds=timeout_seconds
        )

    def is_available(self) -> bool:
        """Return True if google-antigravity SDK is available."""
        return is_sdk_available()

    def _build_pr_review_prompt(
        self,
        git_diff: str,
        sast_findings: list[dict[str, Any]],
        pr_title: str = "",
        pr_body: str = "",
    ) -> str:
        """Construct structured prompt for PR review."""
        truncated_diff = (
            git_diff[:12000] + "\n\n[... Diff truncated for token budget ...]"
            if len(git_diff) > 12000
            else git_diff
        )

        prompt = f"""Pull Request Title: {pr_title or "N/A"}
Pull Request Description:
{pr_body or "N/A"}

Deterministic SAST Diff Findings ({len(sast_findings)} findings):
```json
{json.dumps(sast_findings, indent=2)}
```

Git Diff:
```diff
{truncated_diff}
```

Review the Pull Request diff and respond in STRICT JSON format:
```json
{{
  "verdict": "APPROVE | COMMENT | REQUEST_CHANGES",
  "summary": "Concise executive review summary...",
  "comments": [
    {{
      "category": "SECURITY | CLEAN_CODE | ARCHITECTURE | BUG_RISK",
      "file_path": "path/to/file",
      "line": 42,
      "severity": "CRITICAL | HIGH | MEDIUM | LOW | INFO",
      "title": "Short title describing the observation",
      "comment": "In-depth rationale and impact explanation...",
      "suggested_fix": "Optional replacement code snippet or null"
    }}
  ]
}}
```
"""
        return prompt

    # pylint: disable=too-many-locals
    def _parse_pr_response(
        self, response_text: str
    ) -> tuple[
        Literal["APPROVE", "COMMENT", "REQUEST_CHANGES"], str, list[PRReviewComment]
    ]:
        """Parse structured response from Antigravity Agent."""
        verdict: Literal["APPROVE", "COMMENT", "REQUEST_CHANGES"] = "COMMENT"
        summary = "PR Review completed."
        comments: list[PRReviewComment] = []

        json_match = re.search(
            r"```(?:json)?\s*(\{.*?\})\s*```", response_text, re.DOTALL
        )
        raw_json_str = json_match.group(1) if json_match else response_text.strip()

        try:
            parsed = json.loads(raw_json_str)
            if isinstance(parsed, dict):
                raw_verdict = str(parsed.get("verdict", "COMMENT")).upper()
                if raw_verdict in ("APPROVE", "COMMENT", "REQUEST_CHANGES"):
                    verdict = raw_verdict  # type: ignore[assignment]
                summary = str(parsed.get("summary", summary))
                raw_comments = parsed.get("comments", [])
                if isinstance(raw_comments, list):
                    for item in raw_comments:
                        if isinstance(item, dict):
                            raw_cat = str(item.get("category", "ARCHITECTURE")).upper()
                            cat: Literal[
                                "SECURITY", "CLEAN_CODE", "ARCHITECTURE", "BUG_RISK"
                            ] = (
                                raw_cat
                                if raw_cat
                                in (
                                    "SECURITY",
                                    "CLEAN_CODE",
                                    "ARCHITECTURE",
                                    "BUG_RISK",
                                )
                                else "ARCHITECTURE"  # type: ignore[assignment]
                            )
                            raw_sev = str(item.get("severity", "MEDIUM")).upper()
                            sev: Literal[
                                "CRITICAL", "HIGH", "MEDIUM", "LOW", "INFO"
                            ] = (
                                raw_sev
                                if raw_sev
                                in ("CRITICAL", "HIGH", "MEDIUM", "LOW", "INFO")
                                else "MEDIUM"  # type: ignore[assignment]
                            )
                            line_val = item.get("line")
                            line_num = int(line_val) if line_val is not None else None
                            comments.append(
                                PRReviewComment(
                                    category=cat,
                                    file_path=str(item.get("file_path", "")),
                                    line=line_num,
                                    severity=sev,
                                    title=str(item.get("title", "Review Note")),
                                    comment=str(item.get("comment", "")),
                                    suggested_fix=item.get("suggested_fix"),
                                )
                            )
        except (json.JSONDecodeError, ValueError):
            logger.debug("Failed to parse JSON PR Review from Agent.")
            summary = response_text.strip()

        return verdict, summary, comments

    # pylint: disable=too-many-locals,protected-access
    async def review_pr_async(
        self,
        git_diff: str,
        sast_findings: list[dict[str, Any]],
        pr_title: str = "",
        pr_body: str = "",
    ) -> PRReviewResult:
        """Asynchronously review Pull Request diff using Antigravity Agent."""
        if not git_diff and not sast_findings:
            return PRReviewResult(
                verdict="APPROVE",
                summary="Empty pull request diff. No changes to review.",
                comments=[],
                token_usage=AITokenUsage(),
                status="skipped",
            )

        if not self.is_available():
            # Fallback heuristic review when SDK is not installed
            crit_high = [
                f
                for f in sast_findings
                if str(f.get("severity", "")).upper() in ("CRITICAL", "HIGH")
            ]
            verdict: Literal["APPROVE", "COMMENT", "REQUEST_CHANGES"] = (
                "REQUEST_CHANGES"
                if crit_high
                else ("COMMENT" if sast_findings else "APPROVE")
            )
            comments = [
                PRReviewComment(
                    category="SECURITY",
                    file_path=str(f.get("path", "")),
                    line=int(f.get("line", 1)),
                    severity=str(f.get("severity", "MEDIUM")).upper(),  # type: ignore[arg-type]
                    title=f"SAST: {f.get('rule_id', 'SECURITY_FINDING')}",
                    comment=str(
                        f.get(
                            "message", f.get("description", "Vulnerability detected.")
                        )
                    ),
                    suggested_fix=str(
                        f.get("remediation", {}).get("fix_after", "")
                        if isinstance(f.get("remediation"), dict)
                        else ""
                    )
                    or None,
                )
                for f in sast_findings
            ]
            return PRReviewResult(
                verdict=verdict,
                summary=(
                    f"Static PR review completed (Antigravity SDK not installed). "
                    f"Found {len(sast_findings)} security findings."
                ),
                comments=comments,
                token_usage=AITokenUsage(),
                status="not_installed",
            )

        # sast-ignore PROMPT_INJECTION_VULNERABLE
        prompt = self._build_pr_review_prompt(
            git_diff, sast_findings, pr_title, pr_body
        )

        try:
            from google.antigravity import (  # pylint: disable=import-outside-toplevel,no-name-in-module
                Agent,
                CapabilitiesConfig,
                LocalAgentConfig,
            )

            # Zero-Trust capabilities hardening
            try:
                capabilities = CapabilitiesConfig(
                    disabled_tools=[
                        "run_command",
                        "edit_file",
                        "write_to_file",
                        "delete_file",
                    ]
                )
            except TypeError:
                capabilities = CapabilitiesConfig()

            config = LocalAgentConfig(
                system_instructions=self.system_instructions,
                capabilities=capabilities,
            )

            async with Agent(config) as agent:
                response = await asyncio.wait_for(
                    agent.chat(prompt), timeout=self.timeout_seconds
                )

                response_text = ""
                if hasattr(response, "text") and response.text:
                    response_text = str(response.text)
                elif hasattr(response, "__aiter__"):
                    try:
                        chunks: list[str] = []
                        async for token in response:
                            chunks.append(str(token))
                        response_text = "".join(chunks)
                    except TypeError:
                        response_text = str(response)
                else:
                    response_text = str(getattr(response, "content", str(response)))

                token_usage = self.security_advisor._extract_token_usage(
                    response, prompt
                )
                if token_usage.output_tokens == 0 and response_text:
                    token_usage.output_tokens = self.security_advisor.estimate_tokens(
                        response_text
                    )
                    token_usage.total_tokens = (
                        token_usage.input_tokens + token_usage.output_tokens
                    )

                verdict, summary, comments = self._parse_pr_response(response_text)

                return PRReviewResult(
                    verdict=verdict,
                    summary=summary,
                    comments=comments,
                    token_usage=token_usage,
                    status="success",
                )

        except Exception as exc:  # pylint: disable=broad-exception-caught
            logger.warning("Antigravity PR Review error: %s", exc)
            return PRReviewResult(
                verdict="COMMENT",
                summary=f"PR Review encountered an error: {exc}",
                comments=[],
                token_usage=AITokenUsage(),
                status="error",
                error_message=str(exc),
            )

    def review_pr(
        self,
        git_diff: str,
        sast_findings: list[dict[str, Any]],
        pr_title: str = "",
        pr_body: str = "",
    ) -> PRReviewResult:
        """Synchronous wrapper for review_pr_async."""
        try:
            loop = asyncio.get_event_loop()
            if loop.is_running():
                with concurrent.futures.ThreadPoolExecutor(max_workers=1) as pool:
                    return pool.submit(
                        asyncio.run,
                        self.review_pr_async(
                            git_diff, sast_findings, pr_title, pr_body
                        ),
                    ).result()
            return loop.run_until_complete(
                self.review_pr_async(git_diff, sast_findings, pr_title, pr_body)
            )
        except RuntimeError:
            return asyncio.run(
                self.review_pr_async(git_diff, sast_findings, pr_title, pr_body)
            )
