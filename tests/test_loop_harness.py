"""Unit tests for BoundedVerificationHarness in loop_harness.py."""

import time

from src.domain.loop_harness import (
    BoundedVerificationHarness,
    HarnessConstraintConfig,
    HarnessConstraints,
    HarnessResult,
)
from src.domain.models import DecisionResult, VerdictState


def test_harness_default_constraints() -> None:
    """Verify default constraint values match v2.0 spec."""
    constraints = HarnessConstraints()
    assert constraints.max_iterations == 5
    assert constraints.max_tool_calls == 10
    assert constraints.max_execution_seconds == 30.0
    assert constraints.max_output_bytes == 1048576  # 1 MB
    assert constraints.max_files_read == 20
    assert constraints.max_memory_mb == 128

    # Alias check
    config = HarnessConstraintConfig()
    assert config.max_iterations == 5


def test_harness_successful_execution() -> None:
    """Verify successful verification loop execution returning DecisionResult."""
    harness = BoundedVerificationHarness()

    def step(iteration: int, h: BoundedVerificationHarness) -> DecisionResult | None:
        h.record_tool_call(1)
        h.record_file_read(2)
        h.record_output(512)
        if iteration == 2:
            return DecisionResult(
                state=VerdictState.TRUE_POSITIVE,
                risk_score=0.9,
                confidence=0.95,
                reason="High risk vulnerability confirmed",
            )
        return None

    res = harness.run(step)

    assert res.status == VerdictState.TRUE_POSITIVE
    assert res.iterations_used == 2
    assert res.tool_calls_used == 2
    assert res.files_read_used == 4
    assert res.output_bytes_used == 1024
    assert res.violated_constraint is None


def test_constraint_exceeded_max_iterations() -> None:
    """Verify loop aborts with NOT_ENOUGH_CONTEXT when max_iterations is exceeded."""
    harness = BoundedVerificationHarness()

    def step(_iteration: int, _h: BoundedVerificationHarness) -> None:
        # Never returns a definitive decision
        pass

    res = harness.run(step)

    assert res.status == VerdictState.NOT_ENOUGH_CONTEXT
    assert res.iterations_used == 5
    assert res.violated_constraint == "max_iterations"
    assert "max_iterations" in res.reason


def test_constraint_exceeded_max_tool_calls() -> None:
    """Verify loop aborts immediately when max_tool_calls (10) is exceeded."""
    harness = BoundedVerificationHarness()

    def step(iteration: int, h: BoundedVerificationHarness) -> None:
        if iteration == 1:
            h.record_tool_call(11)  # Exceeds max 10

    res = harness.run(step)

    assert res.status == VerdictState.NOT_ENOUGH_CONTEXT
    assert res.tool_calls_used == 11
    assert res.violated_constraint == "max_tool_calls"


def test_constraint_exceeded_max_execution_seconds() -> None:
    """Verify loop aborts when execution time exceeds 30 seconds."""
    constraints = HarnessConstraints(max_execution_seconds=0.1)
    harness = BoundedVerificationHarness(constraints=constraints)

    def step(_iteration: int, _h: BoundedVerificationHarness) -> None:
        time.sleep(0.15)

    res = harness.run(step)

    assert res.status == VerdictState.NOT_ENOUGH_CONTEXT
    assert res.violated_constraint == "max_execution_seconds"


def test_constraint_exceeded_max_output_bytes() -> None:
    """Verify loop aborts when max_output_bytes (1 MB) is exceeded."""
    harness = BoundedVerificationHarness()

    def step(_iteration: int, h: BoundedVerificationHarness) -> None:
        h.record_output(1048577)  # 1 byte over 1 MB limit

    res = harness.run(step)

    assert res.status == VerdictState.NOT_ENOUGH_CONTEXT
    assert res.output_bytes_used == 1048577
    assert res.violated_constraint == "max_output_bytes"


def test_constraint_exceeded_max_files_read() -> None:
    """Verify loop aborts when max_files_read (20) is exceeded."""
    harness = BoundedVerificationHarness()

    def step(_iteration: int, h: BoundedVerificationHarness) -> None:
        h.record_file_read(21)  # Exceeds limit of 20

    res = harness.run(step)

    assert res.status == VerdictState.NOT_ENOUGH_CONTEXT
    assert res.files_read_used == 21
    assert res.violated_constraint == "max_files_read"


def test_constraint_exceeded_max_memory_mb() -> None:
    """Verify loop aborts when max_memory_mb (128) is exceeded."""
    fake_memory = 100.0

    def memory_provider() -> float:
        return fake_memory

    harness = BoundedVerificationHarness(memory_fn=memory_provider)

    def step(_iteration: int, h: BoundedVerificationHarness) -> None:
        nonlocal fake_memory
        fake_memory = 150.0  # Exceeds 128 MB limit
        h.update_memory()

    res = harness.run(step)

    assert res.status == VerdictState.NOT_ENOUGH_CONTEXT
    assert res.memory_mb_used == 150.0
    assert res.violated_constraint == "max_memory_mb"


def test_harness_reset_and_manual_recording() -> None:
    """Test manual recording methods and reset functionality."""
    harness = BoundedVerificationHarness()
    harness.reset()

    assert harness.record_tool_call(5) is None
    assert harness.tool_calls_used == 5

    assert harness.record_file_read(3) is None
    assert harness.files_read_used == 3

    assert harness.record_output(100) is None
    assert harness.output_bytes_used == 100

    assert harness.set_memory_mb(50.0) is None
    assert harness.memory_mb_used == 50.0

    # Trigger memory violation manually
    violation = harness.set_memory_mb(200.0)
    assert violation == "max_memory_mb"
    assert harness.violated_constraint == "max_memory_mb"


def test_harness_step_exception_handling() -> None:
    """Verify harness catches exception inside step and returns NOT_ENOUGH_CONTEXT."""
    harness = BoundedVerificationHarness()

    def step(_iteration: int, _h: BoundedVerificationHarness) -> None:
        raise ValueError("Unexpected error during step execution")

    res = harness.run(step)

    assert res.status == VerdictState.NOT_ENOUGH_CONTEXT
    assert "Unexpected error" in res.reason


def test_harness_result_with_harness_result_return() -> None:
    """Verify harness returns HarnessResult when step directly returns HarnessResult."""
    harness = BoundedVerificationHarness()

    expected_result = HarnessResult(
        status=VerdictState.FALSE_POSITIVE,
        iterations_used=1,
        reason="Explicitly marked false positive",
    )

    def step(_iteration: int, _h: BoundedVerificationHarness) -> HarnessResult:
        return expected_result

    res = harness.run(step)
    assert res.status == VerdictState.FALSE_POSITIVE
    assert res.reason == "Explicitly marked false positive"
