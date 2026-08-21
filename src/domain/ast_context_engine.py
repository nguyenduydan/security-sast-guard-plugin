"""AST Context Engine for node-level scope resolution."""

import re
from html.parser import HTMLParser


class HTMLASPXParser(HTMLParser):
    """Lightweight HTML and ASPX tag/attribute context parser."""

    def __init__(self) -> None:
        super().__init__()
        self.inline_event_found = False
        self.attribute_found = False

    def handle_starttag(self, tag: str, attrs: list[tuple[str, str | None]]) -> None:
        for attr, _ in attrs:
            if attr.lower().startswith("on"):
                self.inline_event_found = True
            else:
                self.attribute_found = True


class ASTContextEngine:
    """Engine for classifying file lines into AST node scopes."""

    def resolve_scope(self, file_path: str, line_number: int, line_content: str) -> str:
        """Resolve node scope for a given line of code."""
        _ = line_number
        stripped = line_content.strip()

        # Node.js process sinks vs client JS regex detection
        if file_path.endswith(
            (".js", ".ts", ".jsx", ".tsx", ".mjs", ".cjs")
        ) and re.search(
            r"\b(?:child_process|cp)\.(?:exec|execSync|spawn|execFile)\s*\(",
            stripped,
        ):
            return "node-process-sink"

        # HTML / ASPX Inline Event & Attribute Detection
        if re.search(r"(?i)\bon[a-zA-Z]{2,20}\s*=", stripped):
            return "html-inline-event"
        if (
            file_path.endswith(
                (".html", ".htm", ".aspx", ".ascx", ".vue", ".svelte", ".jsp", ".ejs")
            )
            and "<" in stripped
            and ">" in stripped
            and "=" in stripped
        ):
            return "html-attribute"

        # JS / TS RegExp method vs Dangerous Sink Detection
        if file_path.endswith(
            (".js", ".ts", ".jsx", ".tsx", ".aspx", ".html", ".mjs", ".cjs")
        ) and (
            "filenameRegex.exec" in stripped
            or re.search(r"/(?:\\.|[^/\\\n\r])+/[a-z]*\.exec\s*\(", stripped)
            or (
                re.search(r"\b[a-zA-Z0-9_$]+\.exec\s*\(", stripped)
                and not re.search(r"\b(?:child_process|cp|process)\.exec", stripped)
            )
        ):
            return "client-js-regex"

        # Server-side Backend Code Scope
        if file_path.endswith(
            (
                ".py",
                ".cs",
                ".java",
                ".php",
                ".rb",
                ".go",
                ".rs",
                ".cpp",
                ".c",
                ".cc",
                ".cxx",
                ".h",
                ".hpp",
                ".kt",
                ".kts",
                ".scala",
                ".swift",
            )
        ):
            return "server-code"

        return "global"
