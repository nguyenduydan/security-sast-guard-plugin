"""Unit tests for SecurityMetricsEngine."""

import pytest

from src.domain.metrics_engine import SecurityMetricsEngine
from src.domain.models import Finding


def test_calculate_from_counts_basic() -> None:
    """Test metrics computation from explicit counts."""
    # TP=8, FP=2, FN=2, TN=88 -> Precision=0.8, Recall=0.8, F1=0.8, FPR=2/90
    result = SecurityMetricsEngine.calculate_from_counts(
        tp=8,
        fp=2,
        fn=2,
        tn=88,
        critical_tp=4,
        critical_fn=1,
    )

    assert result.tp == 8
    assert result.fp == 2
    assert result.fn == 2
    assert result.tn == 88
    assert pytest.approx(result.precision, 0.001) == 0.8
    assert pytest.approx(result.recall, 0.001) == 0.8
    assert pytest.approx(result.f1_score, 0.001) == 0.8
    assert pytest.approx(result.fpr, 0.001) == 2 / 90
    assert pytest.approx(result.fnr, 0.001) == 0.2
    assert pytest.approx(result.critical_recall, 0.001) == 0.8

    dct = result.to_dict()
    assert dct["precision"] == 0.8
    assert dct["recall"] == 0.8


def test_calculate_from_counts_zero_division() -> None:
    """Test metrics computation with zero counts avoiding ZeroDivisionError."""
    result = SecurityMetricsEngine.calculate_from_counts(tp=0, fp=0, fn=0, tn=0)

    assert result.precision == 0.0
    assert result.recall == 0.0
    assert result.f1_score == 0.0
    assert result.fpr == 0.0
    assert result.fnr == 0.0
    assert result.critical_recall == 0.0


def test_evaluate_findings() -> None:
    """Test evaluation of finding lists (ground truth vs actual)."""
    expected = [
        Finding(
            rule_id="SQL_INJECTION",
            rule_name="SQL Injection",
            path="app/db.py",
            line=42,
            line_content="cursor.execute(query)",
            severity="CRITICAL",
        ),
        Finding(
            rule_id="XSS",
            rule_name="XSS Vulnerability",
            path="app/views.py",
            line=10,
            line_content="html += user_input",
            severity="HIGH",
        ),
        Finding(
            rule_id="RCE",
            rule_name="Command Injection",
            path="app/utils.py",
            line=15,
            line_content="os.system(cmd)",
            severity="CRITICAL",
        ),
    ]

    actual = [
        Finding(
            rule_id="SQL_INJECTION",
            rule_name="SQL Injection",
            path="app/db.py",
            line=42,
            line_content="cursor.execute(query)",
            severity="CRITICAL",
        ),
        Finding(
            rule_id="XSS",
            rule_name="XSS Vulnerability",
            path="app/views.py",
            line=10,
            line_content="html += user_input",
            severity="HIGH",
        ),
        Finding(
            rule_id="FALSE_POSITIVE_RULE",
            rule_name="False Positive",
            path="app/views.py",
            line=99,
            line_content="safe_function()",
            severity="LOW",
        ),
    ]

    engine = SecurityMetricsEngine()
    result = engine.evaluate(
        expected=expected, actual=actual, total_negative_samples=100
    )

    # TP = 2 (SQL_INJECTION, XSS)
    # FP = 1 (FALSE_POSITIVE_RULE)
    # FN = 1 (RCE missing in actual)
    assert result.tp == 2
    assert result.fp == 1
    assert result.fn == 1
    assert pytest.approx(result.precision, 0.001) == 2 / 3
    assert pytest.approx(result.recall, 0.001) == 2 / 3
    assert pytest.approx(result.f1_score, 0.001) == 2 / 3
    assert pytest.approx(result.critical_recall, 0.001) == 0.5


def test_evaluate_dicts() -> None:
    """Test evaluation using dict representations of findings."""
    expected = [
        {"path": "a.py", "line": 1, "rule_id": "R1", "severity": "CRITICAL"},
        {"path": "b.py", "line": 2, "rule_id": "R2", "severity": "MEDIUM"},
    ]
    actual = [
        {"path": "a.py", "line": 1, "rule_id": "R1", "severity": "CRITICAL"},
        {"path": "b.py", "line": 2, "rule_id": "R2", "severity": "MEDIUM"},
    ]

    engine = SecurityMetricsEngine()
    result = engine.evaluate(expected=expected, actual=actual)

    assert result.tp == 2
    assert result.fp == 0
    assert result.fn == 0
    assert result.precision == 1.0
    assert result.recall == 1.0
    assert result.f1_score == 1.0
    assert result.critical_recall == 1.0


def test_evaluate_windows_and_posix_path_normalization() -> None:
    """Test path normalization matches Windows backslashes with POSIX slashes."""
    expected = [
        Finding(
            rule_id="SQL_INJECTION",
            rule_name="SQL Injection",
            path="src/app/views.py",
            line=10,
            line_content="cursor.execute(query)",
            severity="CRITICAL",
        ),
    ]
    actual_windows = [
        Finding(
            rule_id="SQL_INJECTION",
            rule_name="SQL Injection",
            path="src\\app\\views.py",
            line=10,
            line_content="cursor.execute(query)",
            severity="CRITICAL",
        ),
    ]

    engine = SecurityMetricsEngine()
    result = engine.evaluate(expected=expected, actual=actual_windows)
    assert result.tp == 1
    assert result.fp == 0
    assert result.fn == 0
    assert result.precision == 1.0
    assert result.recall == 1.0
