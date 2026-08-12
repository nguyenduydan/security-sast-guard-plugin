"""Unit tests for SecurityDecisionEngine domain module."""

# pylint: disable=redefined-outer-name

import pytest

from src.domain.decision_engine import (
    SecurityDecisionEngine,
    VerdictState,
)


@pytest.fixture
def engine() -> SecurityDecisionEngine:
    """Fixture providing SecurityDecisionEngine instance."""
    return SecurityDecisionEngine()


def test_verdict_state_enum_values() -> None:
    """Verify VerdictState enum string values."""
    assert VerdictState.TRUE_POSITIVE == "TRUE_POSITIVE"
    assert VerdictState.FALSE_POSITIVE == "FALSE_POSITIVE"
    assert VerdictState.CONFIRM_REQUIRED == "CONFIRM_REQUIRED"
    assert VerdictState.NOT_ENOUGH_CONTEXT == "NOT_ENOUGH_CONTEXT"


def test_risk_formula_calculation(engine: SecurityDecisionEngine) -> None:
    """Verify exact risk score calculation using specified weights."""
    # Critical (1.0), Taint confirmed (1.0), No sanitizer (0.0) -> 0.70
    score = engine.calculate_risk_score("critical", 1.0, 0.0)
    assert score == pytest.approx(0.70)

    # High (0.75), Taint confirmed (1.0), No sanitizer (0.0) -> 0.625
    score_high = engine.calculate_risk_score("high", 1.0, 0.0)
    assert score_high == pytest.approx(0.625)

    # Medium (0.5), Taint confirmed (1.0), High Sanitizer (1.0) -> 0.25
    score_sanitized = engine.calculate_risk_score("medium", 1.0, 1.0)
    assert score_sanitized == pytest.approx(0.25)


def test_evidence_none_and_iterations_remaining(
    engine: SecurityDecisionEngine,
) -> None:
    """Partial/missing evidence + iterations < max -> NOT_ENOUGH_CONTEXT."""
    finding = {"rule_id": "CWE-89", "severity": "high"}
    res = engine.decide(
        finding=finding,
        evidence=None,
        framework_context=None,
        harness_iterations_used=1,
        max_iterations=5,
    )
    assert res.state == VerdictState.NOT_ENOUGH_CONTEXT
    assert res.risk_score == 0.0
    assert res.confidence == 0.0
    assert not res.policy_override


def test_evidence_none_and_iterations_exhausted(
    engine: SecurityDecisionEngine,
) -> None:
    """Iterations exhausted + incomplete evidence -> CONFIRM_REQUIRED."""
    finding = {"rule_id": "CWE-79", "severity": "medium"}
    res = engine.decide(
        finding=finding,
        evidence=None,
        framework_context=None,
        harness_iterations_used=5,
        max_iterations=5,
    )
    assert res.state == VerdictState.CONFIRM_REQUIRED
    assert not res.policy_override


def test_policy_deny_sql_injection_without_sanitizer(
    engine: SecurityDecisionEngine,
) -> None:
    """SQL injection without sanitizer -> TRUE_POSITIVE (policy deny override)."""
    finding = {
        "rule_id": "CWE-89-SQL-INJECTION",
        "rule_name": "SQL Injection",
        "severity": "critical",
        "line_content": "db.Execute(param)",
    }
    evidence = {
        "user_input": True,
        "sanitizer_confidence": 0.0,
    }
    res = engine.decide(
        finding=finding,
        evidence=evidence,
        framework_context=None,
        harness_iterations_used=2,
        max_iterations=5,
    )
    assert res.state == VerdictState.TRUE_POSITIVE
    assert res.policy_override
    assert res.risk_score == 1.0
    assert res.confidence == 1.0


def test_policy_allow_webforms_onclick(engine: SecurityDecisionEngine) -> None:
    """WebForms OnClick server event -> FALSE_POSITIVE (policy allow override)."""
    finding = {
        "rule_id": "CWE-79",
        "severity": "medium",
        "line_content": (
            "protected void btnSubmit_OnClick(object sender, EventArgs e)"
        ),
    }
    framework_context = {
        "framework": "webforms",
        "is_webforms_event": True,
        "event_name": "btnSubmit_OnClick",
    }
    evidence = {"sanitizer_confidence": 0.0}
    res = engine.decide(
        finding=finding,
        evidence=evidence,
        framework_context=framework_context,
        harness_iterations_used=1,
        max_iterations=5,
    )
    assert res.state == VerdictState.FALSE_POSITIVE
    assert res.policy_override
    assert res.risk_score == 0.0


def test_full_taint_path_high_risk_true_positive(
    engine: SecurityDecisionEngine,
) -> None:
    """Full taint path + high risk -> TRUE_POSITIVE."""
    finding = {"rule_id": "CWE-78", "severity": "critical"}
    evidence_high = {
        "taint_path_confirmed": 1.0,
        "sanitizer_confidence": 0.0,
        "policy_deny": True,
    }
    res = engine.decide(
        finding=finding,
        evidence=evidence_high,
        framework_context=None,
        harness_iterations_used=3,
        max_iterations=5,
    )
    assert res.state == VerdictState.TRUE_POSITIVE


def test_sanitizer_confirmed_false_positive(
    engine: SecurityDecisionEngine,
) -> None:
    """Confirmed sanitizer -> FALSE_POSITIVE."""
    finding = {"rule_id": "CWE-79", "severity": "high"}
    evidence = {
        "taint_path_confirmed": 1.0,
        "sanitizer_confidence": 0.9,
        "sanitizer_confirmed": True,
    }
    res = engine.decide(
        finding=finding,
        evidence=evidence,
        framework_context=None,
        harness_iterations_used=2,
        max_iterations=5,
    )
    assert res.state == VerdictState.FALSE_POSITIVE
    assert not res.policy_override


def test_confirm_required_intermediate_risk(
    engine: SecurityDecisionEngine,
) -> None:
    """Intermediate risk score without policy override -> CONFIRM_REQUIRED."""
    finding = {"rule_id": "CWE-20", "severity": "medium"}
    evidence = {
        "taint_path_confirmed": 0.5,
        "sanitizer_confidence": 0.2,
    }
    res = engine.decide(
        finding=finding,
        evidence=evidence,
        framework_context=None,
        harness_iterations_used=3,
        max_iterations=5,
    )
    assert res.state == VerdictState.CONFIRM_REQUIRED
    assert not res.policy_override
