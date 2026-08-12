"""Framework registry for resolving framework semantics strategies."""

from src.domain.frameworks.base import (
    FrameworkSemanticsResult,
    FrameworkSemanticsStrategy,
)
from src.domain.frameworks.dotnet_webforms import DotNetWebFormsStrategy
from src.domain.frameworks.generic import GenericStrategy


class FrameworkRegistry:
    """Registry managing and resolving framework semantics strategies."""

    def __init__(
        self, strategies: list[FrameworkSemanticsStrategy] | None = None
    ) -> None:
        """Initialize registry with given or default strategies."""
        self._generic_strategy: FrameworkSemanticsStrategy = GenericStrategy()
        self._strategies: list[FrameworkSemanticsStrategy] = []

        if strategies:
            for s in strategies:
                self.register_strategy(s)
        else:
            # Register built-in default strategies
            self.register_strategy(DotNetWebFormsStrategy())

    def register_strategy(self, strategy: FrameworkSemanticsStrategy) -> None:
        """Register a framework semantics strategy."""
        if strategy.framework_name == "generic":
            self._generic_strategy = strategy
        else:
            # Override any strategy with matching framework_name
            self._strategies = [
                s
                for s in self._strategies
                if s.framework_name != strategy.framework_name
            ]
            self._strategies.append(strategy)

    def get_strategy(
        self, file_path: str, content_probe: str | None = None
    ) -> FrameworkSemanticsStrategy:
        """Resolve framework semantics strategy for file path or content probe."""
        for strategy in self._strategies:
            if strategy.supports_file(file_path, content_probe):
                return strategy
        return self._generic_strategy

    def analyze(self, file_path: str, content: str) -> FrameworkSemanticsResult:
        """Resolve strategy and execute semantics analysis."""
        strategy = self.get_strategy(file_path, content_probe=content)
        return strategy.analyze_semantics(file_path, content)
