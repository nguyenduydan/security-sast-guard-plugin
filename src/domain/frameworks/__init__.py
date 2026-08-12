"""Multi-language framework semantics engine package."""

from src.domain.frameworks.base import (
    EventHandler,
    FrameworkSemanticsResult,
    FrameworkSemanticsStrategy,
    OutputExpression,
    ServerControl,
)
from src.domain.frameworks.dotnet_webforms import DotNetWebFormsStrategy
from src.domain.frameworks.generic import GenericStrategy
from src.domain.frameworks.registry import FrameworkRegistry

__all__ = [
    "DotNetWebFormsStrategy",
    "EventHandler",
    "FrameworkRegistry",
    "FrameworkSemanticsResult",
    "FrameworkSemanticsStrategy",
    "GenericStrategy",
    "OutputExpression",
    "ServerControl",
]
