import re
from typing import Any

from src.domain.ai_cache import AICache

CSHARP_METHOD_REGEX = re.compile(
    r"""on[a-z]+\s*=\s*["'](?!\s*javascript:)[a-zA-Z0-9_]+["']"""
)
SHELL_SANITIZERS: set[str] = {
    "shlex.quote",
    "escapeshellarg",
    "escapeshellcmd",
    "quote_plus",
}

HTML_XSS_SANITIZERS: set[str] = {
    "dompurify",
    "sanitize",
    "htmlspecialchars",
    "htmlentities",
    "escapehtml",
    "validator.escape",
    "encodeuricomponent",
    "encodeuri",
    "bleach.clean",
    "urlencode",
}

PATH_SANITIZERS: set[str] = {
    "path.resolve",
    "os.path.basename",
    "path.basename",
    "os.path.abspath",
    "pathlib.path",
}

SAFE_TYPECASTS: set[str] = {
    "int(",
    "float(",
    "bool(",
    "uuid(",
}

KNOWN_SANITIZERS: set[str] = (
    SHELL_SANITIZERS
    | HTML_XSS_SANITIZERS
    | PATH_SANITIZERS
    | SAFE_TYPECASTS
    | {
        "parameterized",
        "preparedstatement",
    }
)

TEST_INDICATORS: set[str] = {
    "test_",
    "_test.",
    "spec.",
    "mock",
    "dummy",
    "fixture",
    "fake",
    "stub",
}

SQL_MARKERS: list[str] = [
    "?",
    "%s",
    "$1",
    ":1",
    ":param",
    "params=",
    "parameters=",
    "bindparam",
    "preparestatement",
    "preparedstatement",
    "execute(",
]


def _is_aspnet_false_positive(rule_id: str, line_content: str) -> bool:
    if "getresourcetext(" in line_content or "getglobalresourceobject(" in line_content:
        return True

    if rule_id == "XSS_INLINE_EVENT":
        is_server_tag = (
            'runat="server"' in line_content
            or "runat='server'" in line_content
            or "<asp:" in line_content
            or "<sweetsoft:" in line_content
        )
        has_simple_csharp = bool(CSHARP_METHOD_REGEX.search(line_content))
        if is_server_tag or has_simple_csharp:
            return True

    return False


def _extract_combined_text(finding: dict[str, Any]) -> str:
    """Combine context window lines and target line content."""
    line_content = str(finding.get("line_content", "")).lower()
    context_window = finding.get("context_window")
    if isinstance(context_window, list):
        context_text = "\n".join(str(item) for item in context_window).lower()
    elif isinstance(context_window, str):
        context_text = context_window.lower()
    else:
        context_text = ""
    return f"{context_text}\n{line_content}" if context_text else line_content


class AIVerifier:
    """Evaluates candidate findings and eliminates false positives based on context."""

    def __init__(self, cache: AICache | None = None) -> None:
        self.cache = cache or AICache()

    def filter_false_positives(
        self, findings: list[dict[str, Any]]
    ) -> tuple[list[dict[str, Any]], int]:
        """Filter list of findings.

        Returns (verified_findings, false_positives_count).
        """
        verified: list[dict[str, Any]] = []
        fp_count = 0

        for f in findings:
            rule_id = str(f.get("rule_id", ""))
            line_content = str(f.get("line_content", ""))
            path = str(f.get("path", ""))
            file_ext = path.rsplit(".", maxsplit=1)[-1] if "." in path else ""
            context_window = f.get("context_window")
            if isinstance(context_window, list):
                context_str = "|".join(str(x) for x in context_window)
            elif isinstance(context_window, str):
                context_str = context_window
            else:
                context_str = ""

            cache_input = (
                f"{line_content}:{context_str}" if context_str else line_content
            )
            key = self.cache.compute_key(rule_id, cache_input, file_ext)
            cached_res = self.cache.get(key)

            if cached_res is not None:
                if not cached_res:
                    fp_count += 1
                else:
                    verified.append(f)
                continue

            if self.is_false_positive(f):
                fp_count += 1
                self.cache.set(key, False)
            else:
                verified.append(f)
                self.cache.set(key, True)

        return verified, fp_count

    def is_false_positive(self, finding: dict[str, Any]) -> bool:
        """Analyze line content and context for false positive indicators."""
        line_content = str(finding.get("line_content", "")).lower()
        file_path = str(finding.get("path", "")).lower()
        rule_id = str(finding.get("rule_id", "")).upper()
        combined_text = _extract_combined_text(finding)

        # 1. Skip test files / mocks for low & medium severity findings
        severity = str(finding.get("severity", "")).upper()
        if severity in ("LOW", "MEDIUM") and any(
            ind in file_path for ind in TEST_INDICATORS
        ):
            return True

        # 2. Check for sanitizers or safe typecasts in line or context
        if any(s in combined_text for s in KNOWN_SANITIZERS):
            return True

        # 3. SQLi false positive check: Parameterized queries (params=, ?, %s, etc.)
        is_sqli_rule = "SQL" in rule_id or "INJECTION" in rule_id
        if (
            is_sqli_rule
            and "+" not in line_content
            and any(p in combined_text for p in SQL_MARKERS)
        ):
            return True

        # 4. ASP.NET WebForms False Positives
        if _is_aspnet_false_positive(rule_id, line_content):
            return True

        stripped = line_content.strip()
        comment_prefixes = ("#", "//", "/" + "*", "*", "'''", '"""')
        return stripped.startswith(comment_prefixes)
