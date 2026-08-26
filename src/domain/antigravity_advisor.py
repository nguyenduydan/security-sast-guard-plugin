"""Antigravity SDK AI Security Advisor module.

Provides deep AI security triage, false-positive evaluation,
actionable remediation suggestions, token usage accounting,
and SHA-256 local response caching via Google Antigravity Python SDK.
"""

from __future__ import annotations

import asyncio
import concurrent.futures
import importlib.util
import json
import logging
import re
from typing import Any

from src.domain.ai_cache import AICache
from src.domain.models import AIFindingAdvice, AITokenUsage, AntigravityAuditReport

logger = logging.getLogger(__name__)

SECURITY_SYSTEM_INSTRUCTIONS = (
    "You are an elite Static Application Security Testing (SAST) and "
    "AppSec Intelligence Agent.\n"
    "Your task is to analyze static code security findings, determine if they "
    "are true or false positives in the given code context, provide a root-cause "
    "explanation, and suggest concrete secure code remediation.\n\n"
    "IMPORTANT SAFETY CONSTRAINTS:\n"
    "1. You are running in Read-Only advisory mode. DO NOT execute commands or "
    "attempt to modify files directly.\n"
    "2. Provide your analysis in structured format.\n"
    "3. Be concise and precise. Avoid unnecessary fluff.\n\n"
    "FEW-SHOT EXAMPLES:\n"
    "- SQL_INJECTION: Unsanitized string formatting into SQL query -> "
    "Suggested Fix: `cursor.execute('SELECT * FROM t WHERE id = %s', (uid,))`\n"
    "- COMMAND_INJECTION: Passing raw string to os.system() -> "
    "Suggested Fix: Use `subprocess.run(['prog', arg], check=True)`\n"
    "- XSS_VULNERABILITY: Raw template insertion -> "
    "Suggested Fix: Use `html.escape(user_str)` or modern framework escaping\n"
    "- HARDCODED_SECRET: API key literal -> "
    "Suggested Fix: Use `os.environ.get('SECRET_KEY')`\n\n"
    "For each finding, evaluate:\n"
    "- Is it a likely false positive? (e.g. sanitized, mock, test data)\n"
    "- Exploitability assessment (High / Medium / Low / None)\n"
    "- Root-cause analysis\n"
    "- Concrete, minimal secure code replacement snippet (Suggested Fix)\n"
)


def is_sdk_available() -> bool:
    """Check if google-antigravity SDK is installed and available for import."""
    try:
        return importlib.util.find_spec("google.antigravity") is not None
    except (ModuleNotFoundError, ImportError, ValueError, AttributeError):
        return False



class AntigravitySecurityAdvisor:
    """Orchestrates AI security analysis and token tracking via Antigravity SDK."""

    def __init__(
        self,
        system_instructions: str = SECURITY_SYSTEM_INSTRUCTIONS,
        timeout_seconds: float = 30.0,
        cache: AICache | None = None,
        batch_size: int = 10,
    ) -> None:
        self.system_instructions = system_instructions
        self.timeout_seconds = timeout_seconds
        self.cache = cache or AICache()
        self.batch_size = max(1, batch_size)

    def is_available(self) -> bool:
        """Return True if SDK is available in the environment."""
        return is_sdk_available()

    def estimate_tokens(self, text: str) -> int:
        """Rough token estimation fallback (approx 4 chars per token)."""
        if not text:
            return 0
        return max(1, len(text) // 4)

    def _compute_finding_cache_key(self, finding: dict[str, Any]) -> str:
        """Compute deterministic cache key for a single finding."""
        rule_id = str(finding.get("rule_id", "UNKNOWN"))
        line_content = str(finding.get("line_content", "")).strip()
        path = str(finding.get("path", ""))
        file_ext = path.rsplit(".", 1)[-1] if "." in path else ""
        context_window = finding.get("context_window", [])
        if isinstance(context_window, list):
            ctx_str = "|".join(str(x).strip() for x in context_window)
        else:
            ctx_str = str(context_window).strip()
        combined = f"{line_content}:{ctx_str}" if ctx_str else line_content
        return self.cache.compute_key(rule_id, combined, file_ext)

    def _build_triage_prompt(
        self,
        findings: list[dict[str, Any]],
        project_context: dict[str, Any] | None = None,
    ) -> str:
        """Construct structured prompt with findings and context windows."""
        context_info = project_context or {}
        stack = context_info.get("stack", "general")
        mode = context_info.get("mode", "strict")

        findings_payload: list[dict[str, Any]] = []
        for idx, f in enumerate(findings, 1):
            context_window = f.get("context_window", [])
            if isinstance(context_window, list):
                ctx_lines = context_window
            elif isinstance(context_window, str):
                ctx_lines = context_window.splitlines()
            else:
                ctx_lines = []

            findings_payload.append(
                {
                    "index": idx,
                    "rule_id": f.get("rule_id", "UNKNOWN"),
                    "rule_name": f.get("rule_name", ""),
                    "file_path": str(f.get("path", "")),
                    "line_number": f.get("line", 1),
                    "line_content": str(f.get("line_content", "")),
                    "severity": str(f.get("severity", "MEDIUM")),
                    "context_window": ctx_lines,
                }
            )

        prompt = f"""Target Project Stack: {stack} (Mode: {mode})
Total Findings to analyze in this batch: {len(findings)}

Findings Data (JSON):
```json
{json.dumps(findings_payload, indent=2)}
```

Analyze each finding and respond in the following STRICT JSON format:
```json
{{
  "executive_summary": "Summary of overall posture and risk assessment.",
  "findings_advice": [
    {{
      "index": 1,
      "rule_id": "RULE_ID",
      "file_path": "path/to/file",
      "line": 10,
      "is_likely_false_positive": false,
      "exploitability": "High | Medium | Low | None",
      "analysis": "Root cause and impact analysis...",
      "suggested_fix": "Secure code replacement snippet..."
    }}
  ]
}}
```
"""
        return prompt

    def _extract_token_usage(self, response: Any, prompt_text: str) -> AITokenUsage:
        """Extract token usage from response object or fallback to estimation."""
        usage_obj = getattr(response, "usage", None)
        if usage_obj is not None:
            input_tok = int(
                getattr(usage_obj, "input_tokens", 0)
                or getattr(usage_obj, "prompt_tokens", 0)
                or 0
            )
            thinking_tok = int(
                getattr(usage_obj, "thinking_tokens", 0)
                or getattr(usage_obj, "reasoning_tokens", 0)
                or 0
            )
            output_tok = int(
                getattr(usage_obj, "output_tokens", 0)
                or getattr(usage_obj, "completion_tokens", 0)
                or 0
            )
            total_tok = int(
                getattr(usage_obj, "total_tokens", 0)
                or (input_tok + thinking_tok + output_tok)
            )
            if total_tok > 0:
                return AITokenUsage(
                    input_tokens=input_tok,
                    thinking_tokens=thinking_tok,
                    output_tokens=output_tok,
                    total_tokens=total_tok,
                )

        # Fallback token estimation
        est_input = self.estimate_tokens(prompt_text)
        return AITokenUsage(
            input_tokens=est_input,
            thinking_tokens=0,
            output_tokens=0,
            total_tokens=est_input,
        )

    def _parse_agent_response(
        self, response_text: str, findings: list[dict[str, Any]]
    ) -> tuple[str, list[AIFindingAdvice]]:
        """Parse structured response into summary and list of AIFindingAdvice."""
        summary = "AI analysis completed."
        advice_list: list[AIFindingAdvice] = []

        # Try extracting JSON code block
        json_match = re.search(
            r"```(?:json)?\s*(\{.*?\})\s*```", response_text, re.DOTALL
        )
        raw_json_str = json_match.group(1) if json_match else response_text.strip()

        try:
            parsed = json.loads(raw_json_str)
            if isinstance(parsed, dict):
                summary = str(parsed.get("executive_summary", summary))
                raw_advice = parsed.get("findings_advice", [])
                if isinstance(raw_advice, list):
                    for item in raw_advice:
                        if isinstance(item, dict):
                            advice_list.append(
                                AIFindingAdvice(
                                    rule_id=str(item.get("rule_id", "UNKNOWN")),
                                    file_path=str(item.get("file_path", "")),
                                    line=int(item.get("line", 1)),
                                    analysis=str(item.get("analysis", "")),
                                    exploitability=str(
                                        item.get("exploitability", "Medium")
                                    ),
                                    suggested_fix=str(item.get("suggested_fix", "")),
                                    is_likely_false_positive=bool(
                                        item.get("is_likely_false_positive", False)
                                    ),
                                )
                            )
        except (json.JSONDecodeError, ValueError):
            logger.debug(
                "Failed to parse structured JSON from Agent, falling back to raw text."
            )
            summary = response_text.strip()
            for f in findings:
                advice_list.append(
                    AIFindingAdvice(
                        rule_id=str(f.get("rule_id", "UNKNOWN")),
                        file_path=str(f.get("path", "")),
                        line=int(f.get("line", 1)),
                        analysis="Detailed analysis available in raw output.",
                        exploitability="Medium",
                        suggested_fix=str(
                            f.get("remediation", {}).get("fix_after", "")
                            if isinstance(f.get("remediation"), dict)
                            else ""
                        ),
                        is_likely_false_positive=False,
                    )
                )

        return summary, advice_list

    # pylint: disable=too-many-locals
    async def _analyze_batch(
        self,
        batch_findings: list[dict[str, Any]],
        project_context: dict[str, Any] | None = None,
    ) -> tuple[str, list[AIFindingAdvice], AITokenUsage]:
        """Process a single batch of findings through Antigravity Agent."""
        # Dynamic import of google.antigravity
        from google.antigravity import (  # pylint: disable=import-outside-toplevel,no-name-in-module
            Agent,
            CapabilitiesConfig,
            LocalAgentConfig,
        )

        # Zero-Trust capabilities hardening: disable command and file modification tools
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

        # sast-ignore PROMPT_INJECTION_VULNERABLE
        prompt = self._build_triage_prompt(batch_findings, project_context)

        async with Agent(config) as agent:
            # Pre-count prompt tokens if supported
            count_fn = getattr(agent, "count_tokens", None)
            if callable(count_fn):
                try:
                    counted = count_fn(prompt)
                    if asyncio.iscoroutine(counted):
                        counted = await counted
                    logger.debug("Estimated token count: %s", counted)
                except Exception as count_err:  # pylint: disable=broad-exception-caught
                    logger.debug("Token count error: %s", count_err)

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

            token_usage = self._extract_token_usage(response, prompt)
            summary, advice_list = self._parse_agent_response(
                response_text, batch_findings
            )

            if token_usage.output_tokens == 0 and response_text:
                token_usage.output_tokens = self.estimate_tokens(response_text)
                token_usage.total_tokens = (
                    token_usage.input_tokens + token_usage.output_tokens
                )

            return summary, advice_list, token_usage

    # pylint: disable=too-many-locals,too-many-branches
    async def analyze_findings_async(
        self,
        findings: list[dict[str, Any]],
        project_context: dict[str, Any] | None = None,
    ) -> AntigravityAuditReport:
        """Asynchronously analyze findings with caching and adaptive batching."""
        if not findings:
            return AntigravityAuditReport(
                executive_summary="No vulnerabilities detected to analyze.",
                findings_advice=[],
                token_usage=AITokenUsage(),
                status="skipped",
            )

        if not self.is_available():
            return AntigravityAuditReport(
                executive_summary=(
                    "Antigravity Python SDK (`google-antigravity`) is not installed. "
                    "AI triage skipped."
                ),
                findings_advice=[],
                token_usage=AITokenUsage(),
                status="not_installed",
                error_message="Package 'google-antigravity' not found in environment.",
            )

        # Stage 1: Check SHA-256 Cache for previously triaged findings
        cached_advices: list[AIFindingAdvice] = []
        uncached_findings: list[dict[str, Any]] = []
        finding_key_map: dict[int, str] = {}

        for idx, f in enumerate(findings):
            key = self._compute_finding_cache_key(f)
            finding_key_map[idx] = key
            cached_data = self.cache.get_advice(key)
            if cached_data is not None:
                cached_advices.append(
                    AIFindingAdvice(
                        rule_id=str(
                            cached_data.get("rule_id", f.get("rule_id", "UNKNOWN"))
                        ),
                        file_path=str(cached_data.get("file_path", f.get("path", ""))),
                        line=int(cached_data.get("line", f.get("line", 1))),
                        analysis=str(cached_data.get("analysis", "")),
                        exploitability=str(cached_data.get("exploitability", "Medium")),
                        suggested_fix=str(cached_data.get("suggested_fix", "")),
                        is_likely_false_positive=bool(
                            cached_data.get("is_likely_false_positive", False)
                        ),
                    )
                )
            else:
                uncached_findings.append(f)

        # If all findings were served from cache, return immediately (0 tokens)
        if not uncached_findings:
            return AntigravityAuditReport(
                executive_summary=(
                    "All findings triaged from local SHA-256 cache (0 tokens consumed)."
                ),
                findings_advice=cached_advices,
                token_usage=AITokenUsage(),
                status="success",
            )

        # Stage 2: Process uncached findings via Adaptive Batching
        combined_advice: list[AIFindingAdvice] = list(cached_advices)
        total_tokens = AITokenUsage()
        summaries: list[str] = []

        try:
            for i in range(0, len(uncached_findings), self.batch_size):
                batch = uncached_findings[i : i + self.batch_size]
                summary, batch_advices, b_tokens = await self._analyze_batch(
                    batch, project_context
                )
                summaries.append(summary)
                total_tokens.input_tokens += b_tokens.input_tokens
                total_tokens.thinking_tokens += b_tokens.thinking_tokens
                total_tokens.output_tokens += b_tokens.output_tokens
                total_tokens.total_tokens += b_tokens.total_tokens

                # Writeback advice to SHA-256 cache
                for adv in batch_advices:
                    combined_advice.append(adv)
                    matched_f = next(
                        (
                            f
                            for f in batch
                            if str(f.get("rule_id")) == adv.rule_id
                            and str(f.get("path")) == adv.file_path
                        ),
                        None,
                    )
                    if matched_f:
                        k = self._compute_finding_cache_key(matched_f)
                        self.cache.set_advice(
                            k,
                            {
                                "rule_id": adv.rule_id,
                                "file_path": adv.file_path,
                                "line": adv.line,
                                "analysis": adv.analysis,
                                "exploitability": adv.exploitability,
                                "suggested_fix": adv.suggested_fix,
                                "is_likely_false_positive": (
                                    adv.is_likely_false_positive
                                ),
                            },
                        )

            exec_summary = summaries[0] if summaries else "AI analysis completed."
            return AntigravityAuditReport(
                executive_summary=exec_summary,
                findings_advice=combined_advice,
                token_usage=total_tokens,
                status="success",
            )

        except Exception as exc:  # pylint: disable=broad-exception-caught
            logger.warning("Antigravity Agent execution error: %s", exc)
            return AntigravityAuditReport(
                executive_summary=f"AI triage encountered an error: {exc}",
                findings_advice=combined_advice,
                token_usage=total_tokens,
                status="error",
                error_message=str(exc),
            )

    def analyze_findings(
        self,
        findings: list[dict[str, Any]],
        project_context: dict[str, Any] | None = None,
    ) -> AntigravityAuditReport:
        """Synchronous wrapper for analyze_findings_async."""
        try:
            loop = asyncio.get_event_loop()
            if loop.is_running():
                # Running inside existing loop (e.g. jupyter or async framework)
                with concurrent.futures.ThreadPoolExecutor(max_workers=1) as pool:
                    return pool.submit(
                        asyncio.run,
                        self.analyze_findings_async(findings, project_context),
                    ).result()
            return loop.run_until_complete(
                self.analyze_findings_async(findings, project_context)
            )
        except RuntimeError:
            return asyncio.run(self.analyze_findings_async(findings, project_context))
