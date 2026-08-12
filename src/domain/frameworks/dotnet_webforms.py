"""ASP.NET WebForms framework semantics strategy."""

import re
from typing import Any, Literal

from src.domain.frameworks.base import (
    EventHandler,
    FrameworkSemanticsResult,
    FrameworkSemanticsStrategy,
    OutputExpression,
    ServerControl,
)

# Known explicit HTML encoders/sanitizers in ASP.NET
DOTNET_SANITIZERS: tuple[str, ...] = (
    "server.htmlencode",
    "httputility.htmlencode",
    "antixssencoder.htmlencode",
    "antixss.htmlencode",
    "encoder.htmlencode",
    "sanitizer.sanitize",
    "sanitize",
)

# Event attribute pattern (e.g. OnClick="btnSubmit_Click")
EVENT_ATTR_RE = re.compile(
    r"\b(On[A-Z]\w+)\s*=\s*(?:\"([^\"]*)\"|'([^']*)'|(\S+))",
    re.IGNORECASE,
)

# Generic XML/HTML attribute pattern
ATTR_RE = re.compile(
    r"\b([a-zA-Z_:][\w:.-]*)\s*=\s*(?:\"([^\"]*)\"|'([^']*)'|(\S+))",
)

# Tag pattern for <asp:ControlName ...>
ASP_CONTROL_RE = re.compile(
    r"<\s*asp:([a-zA-Z0-9_]+)\b([^>]*)/?>",
    re.IGNORECASE | re.DOTALL,
)

# ASP.NET Expression blocks:
# <%: ... %>  (Auto HTML-encoded output, .NET 4.0+)
# <%#: ... %> (Auto HTML-encoded databinding)
# <%= ... %>  (Raw output)
# <%# ... %>  (Raw databinding)
EXPRESSION_BLOCK_RE = re.compile(
    r"<%\s*(?P<tag_type>:|#:|#|=)?\s*(?P<expr>.*?)\s*%>",
    re.DOTALL,
)


def _get_line_number(content: str, char_index: int) -> int:
    """Calculate 1-indexed line number for a character index in content."""
    return content.count("\n", 0, char_index) + 1


def _parse_attributes(attr_str: str) -> dict[str, str]:
    """Parse key=value attributes from tag string."""
    attrs: dict[str, str] = {}
    for match in ATTR_RE.finditer(attr_str):
        key = match.group(1)
        val = (
            match.group(2)
            if match.group(2) is not None
            else (
                match.group(3) if match.group(3) is not None else match.group(4) or ""
            )
        )
        attrs[key] = val
    return attrs


class DotNetWebFormsStrategy(FrameworkSemanticsStrategy):
    """Semantics strategy for ASP.NET WebForms (.aspx, .ascx, .master)."""

    @property
    def framework_name(self) -> str:
        """Return framework strategy name."""
        return "dotnet_webforms"

    def supports_file(self, file_path: str, content_probe: str | None = None) -> bool:
        """Check if file or content probe is ASP.NET WebForms."""
        lower_path = file_path.lower()
        if lower_path.endswith((".aspx", ".ascx", ".master")):
            return True

        if content_probe:
            lower_probe = content_probe.lower()
            if any(
                token in lower_probe
                for token in (
                    'runat="server"',
                    "runat='server'",
                    "<asp:",
                    "<%:",
                    "<%=",  # sast-ignore: XSS_VULNERABILITY
                )
            ):
                return True

        return False

    # pylint: disable=too-many-locals
    def analyze_semantics(
        self, file_path: str, content: str
    ) -> FrameworkSemanticsResult:
        """Analyze ASP.NET WebForms controls, event handlers, and expression blocks."""
        server_controls: list[ServerControl] = []
        event_handlers: list[EventHandler] = []
        output_expressions: list[OutputExpression] = []
        sanitized_expressions: list[str] = []

        # 1. Parse ASP.NET Server Controls <asp:ControlName ...>
        for match in ASP_CONTROL_RE.finditer(content):
            start_idx = match.start()
            line_no = _get_line_number(content, start_idx)
            control_type_name = match.group(1)
            raw_attrs = match.group(2)

            attrs = _parse_attributes(raw_attrs)
            runat_server = attrs.get("runat", "").lower() == "server"
            control_id = attrs.get("ID") or attrs.get("id") or f"control_{start_idx}"

            server_controls.append(
                ServerControl(
                    control_id=control_id,
                    control_type=f"asp:{control_type_name}",
                    line=line_no,
                    attributes=attrs,
                    runat_server=runat_server,
                )
            )

            # Extract event handlers from attributes
            for attr_name, attr_val in attrs.items():
                if attr_name.lower().startswith("on") and len(attr_name) > 2:
                    event_handlers.append(
                        EventHandler(
                            control_id=control_id,
                            event_name=attr_name,
                            handler_name=attr_val,
                            line=line_no,
                        )
                    )

        # 2. Parse Expression Blocks (<% ... %>)
        for match in EXPRESSION_BLOCK_RE.finditer(content):
            start_idx = match.start()
            line_no = _get_line_number(content, start_idx)
            tag_type = match.group("tag_type") or ""
            expr_text = match.group("expr").strip()

            # Ignore code directives/statements like <%@ Page ... %> or <% if (...) { %>
            if not tag_type and (
                expr_text.startswith("@") or expr_text.startswith("import")
            ):
                continue

            is_encoded_tag = tag_type in (":", "#:")
            is_explicit_sanitized = self.is_sanitized_expression(expr_text)
            is_sanitized = is_encoded_tag or is_explicit_sanitized

            expr_kind: Literal["encoded", "raw"] = (
                "encoded" if is_encoded_tag else "raw"
            )

            output_expressions.append(
                OutputExpression(
                    expression_type=expr_kind,
                    expression=expr_text,
                    line=line_no,
                    is_sanitized=is_sanitized,
                )
            )

            if is_sanitized:
                sanitized_expressions.append(expr_text)

        metadata: dict[str, Any] = {
            "total_server_controls": len(server_controls),
            "total_event_handlers": len(event_handlers),
            "total_output_expressions": len(output_expressions),
        }

        return FrameworkSemanticsResult(
            framework_name=self.framework_name,
            file_path=file_path,
            server_controls=tuple(server_controls),
            event_handlers=tuple(event_handlers),
            output_expressions=tuple(output_expressions),
            sanitized_expressions=tuple(sanitized_expressions),
            metadata=metadata,
        )

    def is_sanitized_expression(
        self, expression: str, line_content: str | None = None
    ) -> bool:
        """Check if an expression or line_content is sanitized for HTML output."""
        target = f"{expression} {line_content or ''}".lower()

        # Check encoded ASP.NET expression tag syntax <%: ... %> or <%#: ... %>
        if "<%:" in target or "<%#:" in target:
            return True

        # Check explicit sanitizer functions in ASP.NET / C#
        return any(sanitizer in target for sanitizer in DOTNET_SANITIZERS)
