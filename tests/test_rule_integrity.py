"""Unit tests for RuleIntegrityValidator."""

# pylint: disable=redefined-outer-name

import hashlib
from pathlib import Path

import pytest

from src.domain.rule_integrity import RuleIntegrityValidator


@pytest.fixture
def validator() -> RuleIntegrityValidator:
    """Fixture providing RuleIntegrityValidator instance."""
    return RuleIntegrityValidator()


def test_verify_rules_single_file_success(
    tmp_path: Path, validator: RuleIntegrityValidator
) -> None:
    """Verify single rule file checksum verification succeeds on valid hash."""
    rule_file = tmp_path / "cwe_89.md"
    checksum_file = tmp_path / "cwe_89.sha256"

    rule_file.write_text("# CWE-89 SQL Injection Rule\n", encoding="utf-8")
    actual_hash = hashlib.sha256(rule_file.read_bytes()).hexdigest()
    checksum_file.write_text(f"{actual_hash}\n", encoding="utf-8")

    assert validator.verify_rules(rule_file, checksum_file) is True


def test_verify_rules_tamper_detected(
    tmp_path: Path, validator: RuleIntegrityValidator
) -> None:
    """Verify rule file tamper alters hash and fails verification (T5)."""
    rule_file = tmp_path / "cwe_89.md"
    checksum_file = tmp_path / "cwe_89.sha256"

    rule_file.write_text("# Original Rule\n", encoding="utf-8")
    actual_hash = hashlib.sha256(rule_file.read_bytes()).hexdigest()
    checksum_file.write_text(f"{actual_hash}\n", encoding="utf-8")

    # Tamper with rule content
    rule_file.write_text("# Tampered Rule (Disabled check)\n", encoding="utf-8")

    assert validator.verify_rules(rule_file, checksum_file) is False


def test_verify_rules_missing_files(
    tmp_path: Path, validator: RuleIntegrityValidator
) -> None:
    """Verify verification returns False when files do not exist."""
    rule_file = tmp_path / "missing.md"
    checksum_file = tmp_path / "missing.sha256"

    assert validator.verify_rules(rule_file, checksum_file) is False


def test_validate_no_redos_detects_catastrophic_backtracking(
    validator: RuleIntegrityValidator,
) -> None:
    """Verify ReDoS patterns are flagged as unsafe (returns False)."""
    unsafe_patterns = [
        "(a+)+",
        "(a*)*",
        "(a|a)*",
        "(.*)*",
        "([a-z]+)+",
    ]
    for pattern in unsafe_patterns:
        assert validator.validate_no_redos(pattern) is False, (
            f"Pattern {pattern} should be marked unsafe"
        )


def test_validate_no_redos_accepts_safe_patterns(
    validator: RuleIntegrityValidator,
) -> None:
    """Verify safe regex patterns pass ReDoS validation."""
    safe_patterns = [
        r"^[a-zA-Z0-9_]+$",
        r"SELECT\s+\*\s+FROM\s+\w+",
        r"^[0-9]{3}-[0-9]{2}-[0-9]{4}$",
        r"\bexec\s*\(",
    ]
    for pattern in safe_patterns:
        assert validator.validate_no_redos(pattern) is True, (
            f"Pattern {pattern} should be marked safe"
        )


def test_validate_no_redos_flags_invalid_regex(
    validator: RuleIntegrityValidator,
) -> None:
    """Verify invalid regex syntax returns False."""
    assert validator.validate_no_redos("[a-z") is False
