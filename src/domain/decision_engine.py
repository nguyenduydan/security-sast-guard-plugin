"""Security Decision Engine domain module."""

from dataclasses import dataclass
from enum import StrEnum
from typing import Any

SEVERITY_WEIGHT: dict[str, float] = {
    "critical": 1.0,
    "high": 0.75,
    "medium": 0.5,
    "low": 0.25,
}

W_SEVERITY: float = 0.30
W_TAINT: float = 0.40
W_SANITIZER: float = 0.30


class VerdictState(StrEnum):
    """Decision verdict state enum."""

    TRUE_POSITIVE = "TRUE_POSITIVE"
    FALSE_POSITIVE = "FALSE_POSITIVE"
    CONFIRM_REQUIRED = "CONFIRM_REQUIRED"
    NOT_ENOUGH_CONTEXT = "NOT_ENOUGH_CONTEXT"


@dataclass(frozen=True)
class DecisionResult:
    """Result of security decision engine evaluation."""

    state: VerdictState
    risk_score: float
    confidence: float
    reason: str
    policy_override: bool = False


class SecurityDecisionEngine:
    """Formal 4-state security decision engine with policy overrides."""

    def calculate_risk_score(
        self,
        severity_str: str,
        taint_path_confirmed: float,
        sanitizer_confidence: float,
    ) -> float:
        """Calculate weighted risk score bounded to [0.0, 1.0]."""
        sev_weight = SEVERITY_WEIGHT.get(severity_str.lower(), 0.5)
        raw_score = (
            W_SEVERITY * sev_weight
            + W_TAINT * taint_path_confirmed
            - W_SANITIZER * sanitizer_confidence
        )
        return max(0.0, min(1.0, raw_score))

    # pylint: disable=too-many-return-statements
    def decide(
        self,
        finding: dict[str, Any],
        evidence: dict[str, Any] | None,
        framework_context: dict[str, Any] | None,
        harness_iterations_used: int,
        max_iterations: int,
    ) -> DecisionResult:
        """Evaluate finding against rules, policy overrides, and risk model."""
        # Step 1: Context availability check
        if evidence is None:
            if harness_iterations_used < max_iterations:
                return DecisionResult(
                    state=VerdictState.NOT_ENOUGH_CONTEXT,
                    risk_score=0.0,
                    confidence=0.0,
                    reason=(
                        "Insufficient evidence collected; context gathering in progress"
                    ),
                    policy_override=False,
                )
            return DecisionResult(
                state=VerdictState.CONFIRM_REQUIRED,
                risk_score=0.0,
                confidence=0.0,
                reason=(
                    "Iterations exhausted with incomplete evidence; "
                    "manual confirmation required"
                ),
                policy_override=False,
            )

        ev = evidence or {}
        fc = framework_context or {}

        taint_confirmed_val = self._extract_taint_confirmed(ev)
        sanitizer_conf_val = float(ev.get("sanitizer_confidence", 0.0))
        if ev.get("sanitizer_confirmed"):
            sanitizer_conf_val = max(sanitizer_conf_val, 1.0)

        # Step 2: Policy DENY override check
        if self._check_policy_deny(finding, ev, fc):
            return DecisionResult(
                state=VerdictState.TRUE_POSITIVE,
                risk_score=1.0,
                confidence=1.0,
                reason=(
                    "Policy DENY override: Direct user input to SQL exec "
                    "without sanitizer"
                ),
                policy_override=True,
            )

        # Step 3: Policy ALLOW override check
        if self._check_policy_allow(finding, ev, fc):
            return DecisionResult(
                state=VerdictState.FALSE_POSITIVE,
                risk_score=0.0,
                confidence=1.0,
                reason=("Policy ALLOW override: Safe WebForms server event handler"),
                policy_override=True,
            )

        # Step 4: Calculate risk score
        severity_str = str(finding.get("severity", "medium"))
        risk_score = self.calculate_risk_score(
            severity_str, taint_confirmed_val, sanitizer_conf_val
        )

        confidence = self._compute_confidence(
            ev, harness_iterations_used, max_iterations
        )

        # Step 5: High risk + confirmed taint -> TRUE_POSITIVE
        is_taint_confirmed = taint_confirmed_val > 0.0 or bool(
            ev.get("taint_confirmed")
        )
        if risk_score >= 0.65 and is_taint_confirmed:
            return DecisionResult(
                state=VerdictState.TRUE_POSITIVE,
                risk_score=risk_score,
                confidence=confidence,
                reason=f"High risk score ({risk_score:.2f}) with confirmed taint path",
                policy_override=False,
            )

        # Step 6: Low risk or confirmed sanitizer -> FALSE_POSITIVE
        is_sanitizer_confirmed = sanitizer_conf_val >= 0.8 or bool(
            ev.get("sanitizer_confirmed")
        )
        if risk_score <= 0.15 or is_sanitizer_confirmed:
            return DecisionResult(
                state=VerdictState.FALSE_POSITIVE,
                risk_score=risk_score,
                confidence=confidence,
                reason=(
                    f"Low risk score ({risk_score:.2f}) or effective sanitizer verified"
                ),
                policy_override=False,
            )

        # Step 7: Ambiguous / intermediate risk -> CONFIRM_REQUIRED
        return DecisionResult(
            state=VerdictState.CONFIRM_REQUIRED,
            risk_score=risk_score,
            confidence=confidence,
            reason=(
                f"Intermediate risk score ({risk_score:.2f}); manual confirmation"
                " required"
            ),
            policy_override=False,
        )

    def _extract_taint_confirmed(self, evidence: dict[str, Any]) -> float:
        """Extract float value (0.0 - 1.0) for taint path confirmation."""
        if "taint_path_confirmed" in evidence:
            val = evidence["taint_path_confirmed"]
            if isinstance(val, (int, float)):
                return float(val)
            if isinstance(val, bool):
                return 1.0 if val else 0.0
        if evidence.get("taint_confirmed") is True:
            return 1.0
        if evidence.get("trace_path"):
            return 1.0
        status = str(evidence.get("taint_status", "")).lower()
        if status in ("confirmed", "full"):
            return 1.0
        if status == "partial":
            return 0.5
        return 0.0

    def _check_policy_deny(
        self,
        finding: dict[str, Any],
        evidence: dict[str, Any],
        framework_context: dict[str, Any],
    ) -> bool:
        """Check if policy explicitly denies."""
        _ = framework_context
        if finding.get("policy_deny") is True or evidence.get("policy_deny") is True:
            return True
        rule_id = str(finding.get("rule_id", "")).lower()
        rule_name = str(finding.get("rule_name", "")).lower()
        line_content = str(finding.get("line_content", "")).lower()

        keywords = ["sql", "sqli", "sql_injection", "sql-injection"]
        is_sqli = any(kw in rule_id or kw in rule_name for kw in keywords)
        has_user_input = (
            bool(evidence.get("user_input"))
            or "request" in line_content
            or "param" in line_content
        )
        has_no_sanitizer = float(
            evidence.get("sanitizer_confidence", 0.0)
        ) == 0.0 and not evidence.get("sanitizer_confirmed")

        return (
            is_sqli
            and (has_user_input or evidence.get("taint_confirmed") is True)
            and has_no_sanitizer
        )

    def _check_policy_allow(
        self,
        finding: dict[str, Any],
        evidence: dict[str, Any],
        framework_context: dict[str, Any],
    ) -> bool:
        """Check if policy explicitly allows."""
        if finding.get("policy_allow") is True or evidence.get("policy_allow") is True:
            return True
        framework = str(framework_context.get("framework", "")).lower()
        is_wf_event = bool(framework_context.get("is_webforms_event"))
        event_name = str(framework_context.get("event_name", "")).lower()
        line_content = str(finding.get("line_content", "")).lower()

        is_wf = framework == "webforms" or "webforms" in line_content or is_wf_event
        is_handler = (
            "onclick" in event_name
            or "onclick" in line_content
            or "page_load" in line_content
            or is_wf_event
        )

        return is_wf and is_handler

    def _compute_confidence(
        self,
        evidence: dict[str, Any],
        harness_iterations_used: int,
        max_iterations: int,
    ) -> float:
        """Compute confidence score for non-override decisions."""
        if evidence.get("confidence") is not None:
            return float(evidence["confidence"])
        if not evidence:
            return 0.5
        iter_ratio = min(1.0, harness_iterations_used / max(1, max_iterations))
        base_confidence = 0.8
        return round(min(1.0, base_confidence + 0.2 * iter_ratio), 2)
