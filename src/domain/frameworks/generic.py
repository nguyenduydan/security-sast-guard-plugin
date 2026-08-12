"""Generic fallback framework semantics strategy."""

from src.domain.frameworks.base import (
    FrameworkSemanticsResult,
    FrameworkSemanticsStrategy,
)

# Common sanitization functions across languages (JS, Python, C#, Java, etc.)
GENERIC_SANITIZERS: tuple[str, ...] = (
    "encodeuricomponent",
    "encodeuri",
    "html.escape",
    "htmlescape",
    "httputility.htmlencode",
    "antixss",
    "sanitize",
    "sanitise",
    "escapehtml",
    "encodehtml",
    "securityelement.escape",
    "dompurify",
    "bleach.clean",
    "xss_clean",
)


class GenericStrategy(FrameworkSemanticsStrategy):
    """Fallback framework semantics strategy for generic files."""

    @property
    def framework_name(self) -> str:
        """Return framework strategy name."""
        return "generic"

    def supports_file(self, file_path: str, content_probe: str | None = None) -> bool:
        """Generic strategy supports all files as a fallback."""
        return True

    def analyze_semantics(
        self, file_path: str, content: str
    ) -> FrameworkSemanticsResult:
        """Analyze generic source code file for sanitization semantics."""
        sanitized_expressions: list[str] = []
        lines = content.splitlines()

        for line in lines:
            line_str = line.strip()
            if not line_str:
                continue

            for sanitizer in GENERIC_SANITIZERS:
                if sanitizer in line_str.lower():
                    sanitized_expressions.append(line_str)
                    break

        return FrameworkSemanticsResult(
            framework_name=self.framework_name,
            file_path=file_path,
            sanitized_expressions=tuple(sanitized_expressions),
            metadata={"total_lines": len(lines)},
        )

    def is_sanitized_expression(
        self, expression: str, line_content: str | None = None
    ) -> bool:
        """Check if expression or line_content contains standard sanitizer functions."""
        target = f"{expression} {line_content or ''}".lower()
        return any(sanitizer in target for sanitizer in GENERIC_SANITIZERS)
