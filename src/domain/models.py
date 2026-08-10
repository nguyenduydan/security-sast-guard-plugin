"""Domain models for Security SAST Guard."""

from dataclasses import dataclass
from enum import StrEnum


class FirewallDecision(StrEnum):
    """Firewall verdict enum."""

    ALLOW = "ALLOW"
    CONFIRM = "CONFIRM"
    DENY = "DENY"


class Severity(StrEnum):
    """Finding severity enum."""

    LOW = "LOW"
    MEDIUM = "MEDIUM"
    HIGH = "HIGH"
    CRITICAL = "CRITICAL"


# pylint: disable=too-many-instance-attributes
@dataclass(frozen=True)
class Finding:
    """Represents a SAST rule violation finding."""

    rule_id: str
    rule_name: str
    path: str
    line: int
    line_content: str
    severity: str
    scope: str = "global"
    action: str = "Block"
    remediation: dict[str, str] | None = None


@dataclass(frozen=True)
class SecurityProfile:
    """Security profile domain model."""

    project_id: str
    stack: str
    mode: str
    audit_level: str
    deny_rules: tuple[str, ...]
    confirm_rules: tuple[str, ...]


# ── Taint Analysis Models ──────────────────────────────────────────────────

# SymbolMap: symbol_name → list of (file_path, line_number) where it appears
SymbolMap = dict[str, list[tuple[str, int]]]


@dataclass(frozen=True)
class TraceStep:
    """One hop in a taint flow trace."""

    file: str
    line: int
    symbol: str
    step_type: str  # "source_assignment" | "intermediate_usage" | "sink"


@dataclass
class TaintFinding:
    """A confirmed source-to-sink taint flow."""

    rule_id: str
    source_file: str
    source_line: int
    source_pattern: str
    sink_file: str
    sink_line: int
    sink_pattern: str
    trace_path: list[TraceStep]
    confidence: float  # 0.0 - 1.0
