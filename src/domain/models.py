"""Domain models for Security SAST Guard."""

from dataclasses import dataclass
from enum import StrEnum
from typing import Any, Literal


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


# -- Call Graph Models ------------------------------------------------------


@dataclass(frozen=True)
class CallEdge:
    """A directed edge in the call graph: caller ? callee."""

    caller_file: str
    caller_fn: str
    callee_file: str
    callee_fn: str


@dataclass
class CallChain:
    """A resolved call chain from an entry function to a sink."""

    entry_fn: str
    steps: list[TraceStep]
    terminal_sink: str


# ── Shared v2.0.0 Interface Contracts ──────────────────────────────────────


class VerdictState(StrEnum):
    """Decision verdict state enum."""

    TRUE_POSITIVE = "TRUE_POSITIVE"
    FALSE_POSITIVE = "FALSE_POSITIVE"
    CONFIRM_REQUIRED = "CONFIRM_REQUIRED"
    NOT_ENOUGH_CONTEXT = "NOT_ENOUGH_CONTEXT"


# pylint: disable=too-many-instance-attributes
@dataclass(frozen=True)
class FirewallVerdictV2:
    """Detailed verdict produced by FirewallEngine v2."""

    verdict: Literal["ALLOW", "CONFIRM", "DENY"]
    intent_label: str | None
    capability_set: list[str] | tuple[str, ...]
    risk_score: float
    confidence: float
    matched_patterns: list[str] | tuple[str, ...]
    deobfuscated_form: str
    chain_threat: bool
    reason: str
    recommended_action: str

    def __post_init__(self) -> None:
        """Convert list attributes to tuples to ensure hashability if frozen."""
        if isinstance(self.capability_set, list):
            object.__setattr__(self, "capability_set", tuple(self.capability_set))
        if isinstance(self.matched_patterns, list):
            object.__setattr__(self, "matched_patterns", tuple(self.matched_patterns))


@dataclass(frozen=True)
class DecisionResult:
    """Result of SecurityDecisionEngine processing a finding."""

    state: VerdictState
    risk_score: float
    confidence: float
    reason: str
    policy_override: bool = False


@dataclass(frozen=True)
class SemanticFingerprint:
    """Semantic fingerprint for SAST finding baseline tracking."""

    fingerprint_id: str
    rule_id: str
    normalized_sink: str
    normalized_source: str
    dataflow_signature: str
    symbol: str
    first_seen: str
    status: Literal["open", "resolved", "suppressed"]


@dataclass
class AuditEntry:
    """Single entry in append-only security audit log."""

    timestamp: str
    entry_type: Literal["SAST_FINDING", "FIREWALL_VERDICT", "DECISION", "KB_APPROVAL"]
    payload: dict[str, Any]
    entry_hash: str


# ── Antigravity AI Telemetry & Advice Models ───────────────────────────────


@dataclass
class AITokenUsage:
    """Token consumption telemetry for AI agent calls."""

    input_tokens: int = 0
    thinking_tokens: int = 0
    output_tokens: int = 0
    total_tokens: int = 0


@dataclass
class AIFindingAdvice:
    """AI security analysis and remediation suggestion for a specific finding."""

    rule_id: str
    file_path: str
    line: int
    analysis: str
    exploitability: str
    suggested_fix: str
    is_likely_false_positive: bool = False


@dataclass
class AntigravityAuditReport:
    """Aggregated security triage and telemetry report from Antigravity Agent."""

    executive_summary: str
    findings_advice: list[AIFindingAdvice]
    token_usage: AITokenUsage
    model_name: str = "google-antigravity-agent"
    status: str = "success"  # "success" | "skipped" | "error" | "not_installed"
    error_message: str | None = None
