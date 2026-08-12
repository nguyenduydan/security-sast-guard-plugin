"""Abstract base class and data models for framework semantics strategies."""

from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from typing import Any, Literal


@dataclass(frozen=True)
class ServerControl:
    """Represents a framework server control (e.g. <asp:TextBox>)."""

    control_id: str
    control_type: str
    line: int
    attributes: dict[str, str] = field(default_factory=dict)
    runat_server: bool = True


@dataclass(frozen=True)
class EventHandler:
    """Represents an event handler binding on a server control or page."""

    control_id: str | None
    event_name: str
    handler_name: str
    line: int


@dataclass(frozen=True)
class OutputExpression:
    """Represents a framework template output expression (e.g. <%: %> vs <%= %>)."""

    expression_type: Literal["encoded", "raw"]
    expression: str
    line: int
    is_sanitized: bool


@dataclass(frozen=True)
class FrameworkSemanticsResult:
    """Consolidated semantics analysis result for a source file."""

    framework_name: str
    file_path: str
    server_controls: tuple[ServerControl, ...] = ()
    event_handlers: tuple[EventHandler, ...] = ()
    output_expressions: tuple[OutputExpression, ...] = ()
    sanitized_expressions: tuple[str, ...] = ()
    metadata: dict[str, Any] = field(default_factory=dict)


class FrameworkSemanticsStrategy(ABC):
    """Abstract base strategy for framework semantics analysis."""

    @property
    @abstractmethod
    def framework_name(self) -> str:
        """Return the name of the framework strategy."""

    @abstractmethod
    def supports_file(self, file_path: str, content_probe: str | None = None) -> bool:
        """Determine if this strategy handles the given file or content probe."""

    @abstractmethod
    def analyze_semantics(
        self, file_path: str, content: str
    ) -> FrameworkSemanticsResult:
        """Analyze framework semantics from file path and content."""

    @abstractmethod
    def is_sanitized_expression(
        self, expression: str, line_content: str | None = None
    ) -> bool:
        """Check if expression or line is sanitized by framework semantics."""
