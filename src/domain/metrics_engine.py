"""Security metrics evaluation engine for SAST audit findings."""

from collections.abc import Sequence
from dataclasses import dataclass
from typing import Any

from src.domain.models import Finding


# pylint: disable=too-many-instance-attributes
@dataclass(frozen=True)
class MetricsResult:
    """Calculated performance metrics for benchmark/audit evaluations."""

    tp: int
    fp: int
    tn: int
    fn: int
    precision: float
    recall: float
    f1_score: float
    fpr: float
    fnr: float
    critical_recall: float

    def to_dict(self) -> dict[str, Any]:
        """Convert metrics result to dictionary format."""
        return {
            "tp": self.tp,
            "fp": self.fp,
            "tn": self.tn,
            "fn": self.fn,
            "precision": round(self.precision, 4),
            "recall": round(self.recall, 4),
            "f1_score": round(self.f1_score, 4),
            "fpr": round(self.fpr, 4),
            "fnr": round(self.fnr, 4),
            "critical_recall": round(self.critical_recall, 4),
        }


class SecurityMetricsEngine:
    """Engine computing precision, recall, F1, FPR, FNR, and critical recall."""

    # pylint: disable=too-many-arguments,too-many-positional-arguments
    @staticmethod
    def calculate_from_counts(
        tp: int,
        fp: int,
        fn: int,
        tn: int = 0,
        critical_tp: int = 0,
        critical_fn: int = 0,
    ) -> MetricsResult:
        """Calculate metrics directly from raw counts."""
        precision = tp / (tp + fp) if (tp + fp) > 0 else 0.0
        recall = tp / (tp + fn) if (tp + fn) > 0 else 0.0
        f1_score = (
            2 * (precision * recall) / (precision + recall)
            if (precision + recall) > 0
            else 0.0
        )
        fpr = fp / (fp + tn) if (fp + tn) > 0 else 0.0
        fnr = fn / (tp + fn) if (tp + fn) > 0 else 0.0

        critical_total = critical_tp + critical_fn
        critical_recall = critical_tp / critical_total if critical_total > 0 else 0.0

        return MetricsResult(
            tp=tp,
            fp=fp,
            tn=tn,
            fn=fn,
            precision=precision,
            recall=recall,
            f1_score=f1_score,
            fpr=fpr,
            fnr=fnr,
            critical_recall=critical_recall,
        )

    # pylint: disable=too-many-locals
    def evaluate(
        self,
        expected: Sequence[Finding | dict[str, Any]],
        actual: Sequence[Finding | dict[str, Any]],
        total_negative_samples: int = 0,
    ) -> MetricsResult:
        """Evaluate actual audit findings against expected ground truth findings."""
        expected_keys: set[tuple[str, int, str]] = set()
        critical_expected_keys: set[tuple[str, int, str]] = set()

        for f in expected:
            key = self._extract_key(f)
            expected_keys.add(key)
            if self._is_critical(f):
                critical_expected_keys.add(key)

        actual_keys: set[tuple[str, int, str]] = set()
        for f in actual:
            actual_keys.add(self._extract_key(f))

        tp_keys = expected_keys.intersection(actual_keys)
        fp_keys = actual_keys - expected_keys
        fn_keys = expected_keys - actual_keys

        tp = len(tp_keys)
        fp = len(fp_keys)
        fn = len(fn_keys)
        tn = max(0, total_negative_samples - fp)

        critical_tp = len(critical_expected_keys.intersection(actual_keys))
        critical_fn = len(critical_expected_keys - actual_keys)

        return self.calculate_from_counts(
            tp=tp,
            fp=fp,
            fn=fn,
            tn=tn,
            critical_tp=critical_tp,
            critical_fn=critical_fn,
        )

    @staticmethod
    def _extract_key(finding: Finding | dict[str, Any]) -> tuple[str, int, str]:
        if isinstance(finding, Finding):
            norm_path = str(finding.path).replace("\\", "/")
            return (norm_path, finding.line, finding.rule_id)
        if isinstance(finding, dict):
            raw_path = str(finding.get("path") or finding.get("file") or "")
            norm_path = raw_path.replace("\\", "/")
            line = int(finding.get("line") or 0)
            rule_id = str(finding.get("rule_id") or "")
            return (norm_path, line, rule_id)
        raise TypeError(f"Unsupported finding type: {type(finding)}")

    @staticmethod
    def _is_critical(finding: Finding | dict[str, Any]) -> bool:
        if isinstance(finding, Finding):
            return str(finding.severity).upper() == "CRITICAL"
        return str(finding.get("severity", "")).upper() == "CRITICAL"
