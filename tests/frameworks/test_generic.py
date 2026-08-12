"""Unit tests for GenericStrategy and FrameworkRegistry."""

from src.domain.frameworks.base import (
    FrameworkSemanticsResult,
    FrameworkSemanticsStrategy,
)
from src.domain.frameworks.dotnet_webforms import DotNetWebFormsStrategy
from src.domain.frameworks.generic import GenericStrategy
from src.domain.frameworks.registry import FrameworkRegistry


def test_generic_strategy_supports_all_files() -> None:
    """Test GenericStrategy supports_file fallback behavior."""
    strategy = GenericStrategy()
    assert strategy.framework_name == "generic"
    assert strategy.supports_file("any_file.py") is True
    assert strategy.supports_file("index.js") is True
    assert strategy.supports_file("unknown.xyz") is True


def test_generic_strategy_sanitizer_detection() -> None:
    """Test GenericStrategy detection of standard sanitizer functions."""
    strategy = GenericStrategy()
    content = """
const safeInput = encodeURIComponent(req.query.input);
const escaped = html.escape(user_text);
const raw = req.body.data;
"""
    result = strategy.analyze_semantics("server.js", content)
    assert result.framework_name == "generic"
    assert len(result.sanitized_expressions) == 2
    assert "encodeURIComponent" in result.sanitized_expressions[0]
    assert "html.escape" in result.sanitized_expressions[1]


def test_generic_strategy_is_sanitized_expression() -> None:
    """Test GenericStrategy is_sanitized_expression method."""
    strategy = GenericStrategy()
    assert strategy.is_sanitized_expression("encodeURIComponent(x)") is True
    assert strategy.is_sanitized_expression("DOMPurify.sanitize(x)") is True
    assert strategy.is_sanitized_expression("html.escape(x)") is True
    assert strategy.is_sanitized_expression("user_input") is False


def test_framework_registry_resolution() -> None:
    """Test FrameworkRegistry resolves strategies accurately."""
    registry = FrameworkRegistry()

    # WebForms file -> DotNetWebFormsStrategy
    aspx_strategy = registry.get_strategy("Default.aspx")
    assert isinstance(aspx_strategy, DotNetWebFormsStrategy)

    # Generic file -> GenericStrategy
    py_strategy = registry.get_strategy("main.py")
    assert isinstance(py_strategy, GenericStrategy)

    # Content probe fallback resolution
    probe_strategy = registry.get_strategy(
        "custom.file", content_probe="<asp:TextBox runat='server'>"
    )
    assert isinstance(probe_strategy, DotNetWebFormsStrategy)


def test_framework_registry_analyze() -> None:
    """Test FrameworkRegistry analyze method dispatch."""
    registry = FrameworkRegistry()

    content = '<asp:Label ID="lblMsg" runat="server" Text="Hello"></asp:Label>'
    result = registry.analyze("Page.aspx", content)

    assert result.framework_name == "dotnet_webforms"
    assert len(result.server_controls) == 1
    assert result.server_controls[0].control_id == "lblMsg"


class MockCustomStrategy(FrameworkSemanticsStrategy):
    """Mock strategy for custom registry testing."""

    @property
    def framework_name(self) -> str:
        return "mock_custom"

    def supports_file(self, file_path: str, content_probe: str | None = None) -> bool:
        return file_path.endswith(".mock")

    def analyze_semantics(
        self, file_path: str, content: str
    ) -> FrameworkSemanticsResult:
        return FrameworkSemanticsResult(
            framework_name=self.framework_name, file_path=file_path
        )

    def is_sanitized_expression(
        self, expression: str, line_content: str | None = None
    ) -> bool:
        return True


def test_framework_registry_custom_strategy_registration() -> None:
    """Test registering custom strategy into FrameworkRegistry."""
    registry = FrameworkRegistry()
    mock_strat = MockCustomStrategy()

    registry.register_strategy(mock_strat)

    resolved = registry.get_strategy("test.mock")
    assert resolved.framework_name == "mock_custom"
