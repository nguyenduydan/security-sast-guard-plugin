"""Unit tests for AppendOnlyAuditLog and domain models v2."""

import json
from pathlib import Path

import pytest

from src.domain.audit_log import AppendOnlyAuditLog
from src.domain.models import FirewallVerdictV2, VerdictState


def test_append_and_verify_100_entries(tmp_path: Path) -> None:
    """Test appending 100 entries into audit log and verifying hash chain integrity."""
    log_path = tmp_path / "firewall_audit.jsonl"
    audit_log = AppendOnlyAuditLog(log_path)

    for i in range(100):
        audit_log.append(
            entry_type="FIREWALL_VERDICT",
            payload={"index": i, "command": f"echo test_{i}", "verdict": "ALLOW"},
        )

    assert audit_log.verify_chain_integrity() is True
    entries = audit_log.get_entries()
    assert len(entries) == 100


def test_tamper_entry_50_payload_breaks_integrity(tmp_path: Path) -> None:
    """Modifying line 50 payload in audit log must fail chain integrity check."""
    log_path = tmp_path / "firewall_audit.jsonl"
    audit_log = AppendOnlyAuditLog(log_path)

    for i in range(100):
        audit_log.append(
            entry_type="DECISION",
            payload={"index": i, "score": i * 0.01},
        )

    assert audit_log.verify_chain_integrity() is True

    # Tamper with entry 50's payload in file
    lines = log_path.read_text(encoding="utf-8").splitlines()
    entry_50_data = json.loads(lines[49])
    entry_50_data["payload"]["tampered"] = True
    lines[49] = json.dumps(entry_50_data)
    log_path.write_text("\n".join(lines) + "\n", encoding="utf-8")

    assert audit_log.verify_chain_integrity() is False


def test_tamper_entry_50_hash_breaks_integrity(tmp_path: Path) -> None:
    """Modifying line 50 hash in audit log must fail chain integrity check."""
    log_path = tmp_path / "firewall_audit.jsonl"
    audit_log = AppendOnlyAuditLog(log_path)

    for i in range(100):
        audit_log.append(
            entry_type="SAST_FINDING",
            payload={"rule": f"RULE_{i}"},
        )

    lines = log_path.read_text(encoding="utf-8").splitlines()
    entry_50_data = json.loads(lines[49])
    entry_50_data["entry_hash"] = "0" * 64
    lines[49] = json.dumps(entry_50_data)
    log_path.write_text("\n".join(lines) + "\n", encoding="utf-8")

    assert audit_log.verify_chain_integrity() is False


def test_empty_or_nonexistent_log(tmp_path: Path) -> None:
    """Non-existent or empty log files should verify as valid."""
    log_path = tmp_path / "non_existent.jsonl"
    audit_log = AppendOnlyAuditLog(log_path)
    assert audit_log.verify_chain_integrity() is True
    assert not audit_log.get_entries()


def test_firewall_verdict_v2_frozen_and_hashable() -> None:
    """FirewallVerdictV2 must be frozen and hashable."""
    verdict = FirewallVerdictV2(
        verdict="DENY",
        intent_label="DESTRUCTIVE",
        capability_set=["FILE_WRITE", "PROCESS_EXEC"],
        risk_score=0.9,
        confidence=0.95,
        matched_patterns=["rm -rf"],
        deobfuscated_form="rm -rf /",
        chain_threat=True,
        reason="Destructive command chain",
        recommended_action="Block execution",
    )

    # Must be hashable without raising TypeError
    h = hash(verdict)
    assert isinstance(h, int)

    # Must be frozen
    with pytest.raises(AttributeError):
        verdict.verdict = "ALLOW"  # type: ignore[misc]


def test_verdict_state_enum() -> None:
    """VerdictState enum must contain exact required values."""
    assert VerdictState.TRUE_POSITIVE == "TRUE_POSITIVE"
    assert VerdictState.FALSE_POSITIVE == "FALSE_POSITIVE"
    assert VerdictState.CONFIRM_REQUIRED == "CONFIRM_REQUIRED"
    assert VerdictState.NOT_ENOUGH_CONTEXT == "NOT_ENOUGH_CONTEXT"
    assert len(VerdictState) == 4
