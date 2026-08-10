import re
from typing import Any

from src.domain.ai_cache import AICache

CSHARP_METHOD_REGEX = re.compile(
    r"""on[a-z]+\s*=\s*["'](?!\s*javascript:)[a-zA-Z0-9_]+["']"""
)
KNOWN_SANITIZERS: set[str] = {
    "dompurify",
    "sanitize",
    "htmlspecialchars",
    "htmlentities",
    "escapehtml",
    "bleach.clean",
    "parameterized",
    "preparedstatement",
    "encodeuricomponent",
    "urlencode",
}

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

SQL_MARKERS: list[str] = ["?", "%s", "$1", ":1", "bindparam", "execute("]


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

            key = self.cache.compute_key(rule_id, line_content, file_ext)
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

        # 1. Skip test files / mocks for low & medium severity findings
        severity = str(finding.get("severity", "")).upper()
        is_test_file = any(ind in file_path for ind in TEST_INDICATORS)
        if is_test_file and severity in ("LOW", "MEDIUM"):
            return True

        # 2. Check for sanitization functions in same line
        for s in KNOWN_SANITIZERS:
            if s in line_content:
                return True

        # 3. SQLi false positive check: Parameterized queries (?, %s, $1, bindParam)
        is_sqli_rule = "SQL" in rule_id or "INJECTION" in rule_id
        has_sql_marker = any(p in line_content for p in SQL_MARKERS)
        no_concat = "+" not in line_content
        if is_sqli_rule and has_sql_marker and no_concat:
            return True

        # 4. ASP.NET WebForms False Positives
        if _is_aspnet_false_positive(rule_id, line_content):
            return True

        stripped = line_content.strip()
        comment_prefixes = ("#", "//", "/" + "*", "*", "'''", '"""')
        return stripped.startswith(comment_prefixes)
