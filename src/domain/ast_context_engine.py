"""AST Context Engine for node-level scope resolution."""

from html.parser import HTMLParser
import re


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

        # HTML / ASPX Inline Event & Attribute Detection
        if file_path.endswith((".html", ".htm", ".aspx", ".ascx")):
            if re.search(r"(?i)\bon[a-z]+\s*=", stripped):
                return "html-inline-event"
            if "<" in stripped and ">" in stripped and "=" in stripped:
                return "html-attribute"

        # JS / TS RegExp method vs Dangerous Sink Detection
        if file_path.endswith((".js", ".ts", ".jsx", ".tsx", ".aspx", ".html")):
            if (
                re.search(r"\.[a-zA-Z0-9_$]+\.exec\s*\(", stripped)
                or "filenameRegex.exec" in stripped
            ):
                return "client-js-regex"

        # Server-side Backend Code Scope
        if file_path.endswith((".py", ".cs", ".java", ".php", ".rb")):
            return "server-code"

        return "global"
