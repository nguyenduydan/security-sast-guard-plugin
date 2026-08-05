"""AI Context Verification Gate for SAST False Positive filtering."""

from typing import Any

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


class AIVerifier:
    """Evaluates candidate findings and eliminates false positives based on context."""

    def filter_false_positives(
        self, findings: list[dict[str, Any]]
    ) -> tuple[list[dict[str, Any]], int]:
        """Filter list of findings.

        Returns (verified_findings, false_positives_count).
        """
        verified: list[dict[str, Any]] = []
        fp_count = 0

        for f in findings:
            if self.is_false_positive(f):
                fp_count += 1
            else:
                verified.append(f)

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

        # 4. Comment / docstring or placeholder string false positive check
        stripped = line_content.strip()
        return stripped.startswith(("#", "//", "/*", "*", "'''", '"""'))
