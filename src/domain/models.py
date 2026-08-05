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



@dataclass(frozen=True)
class SecurityProfile:
    """Security profile domain model."""

    project_id: str
    stack: str
    mode: str
    audit_level: str
    sast_level: str
    deny_rules: tuple[str, ...]
    confirm_rules: tuple[str, ...]
