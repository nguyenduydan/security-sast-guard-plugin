"""Bounded Verification Harness module for Security SAST Guard v2.0.0."""

import ctypes
import logging
import time
from collections.abc import Callable
from dataclasses import dataclass
from typing import Any

from src.domain.models import VerdictState

logger = logging.getLogger(__name__)


def _get_process_memory_mb() -> float:
    """Get current process RSS memory usage in MB."""
    try:
        import resource  # pylint: disable=import-outside-toplevel

        if hasattr(resource, "getrusage") and hasattr(resource, "RUSAGE_SELF"):
            getrusage = getattr(resource, "getrusage")  # noqa: B009
            rusage_self = getattr(resource, "RUSAGE_SELF")  # noqa: B009
            rusage = getrusage(rusage_self)
            return float(getattr(rusage, "ru_maxrss", 0)) / 1024.0
    except (ImportError, AttributeError):
        # resource module is unavailable on non-POSIX OS (e.g. Windows);
        # fall back to ctypes memory query
        pass

    if hasattr(ctypes, "windll"):
        try:

            class PROCESS_MEMORY_COUNTERS(ctypes.Structure):
                _fields_ = [
                    ("cb", ctypes.c_ulong),
                    ("PageFaultCount", ctypes.c_ulong),
                    ("PeakWorkingSetSize", ctypes.c_size_t),
                    ("WorkingSetSize", ctypes.c_size_t),
                    ("QuotaPeakPeakPagedPoolUsage", ctypes.c_size_t),
                    ("QuotaPagedPoolUsage", ctypes.c_size_t),
                    ("QuotaPeakNonPagedPoolUsage", ctypes.c_size_t),
                    ("QuotaNonPagedPoolUsage", ctypes.c_size_t),
                    ("PagefileUsage", ctypes.c_size_t),
                    ("PeakPagefileUsage", ctypes.c_size_t),
                ]

            counters = PROCESS_MEMORY_COUNTERS()
            # pylint: disable=attribute-defined-outside-init
            counters.cb = ctypes.sizeof(PROCESS_MEMORY_COUNTERS)
            windll = getattr(ctypes, "windll")  # noqa: B009
            handle = windll.kernel32.GetCurrentProcess()
            if windll.psapi.GetProcessMemoryInfo(
                handle, ctypes.byref(counters), counters.cb
            ):
                return float(counters.WorkingSetSize) / (1024 * 1024)
        except Exception:  # noqa: S110 # pylint: disable=broad-exception-caught
            # Windows API query failed or permission denied; return fallback 0.0
            pass

    return 0.0


@dataclass
class HarnessConstraints:
    """Resource constraints for verification loop."""

    max_iterations: int = 5
    max_tool_calls: int = 10
    max_execution_seconds: float = 30.0
    max_output_bytes: int = 1048576  # 1 MB
    max_files_read: int = 20
    max_memory_mb: int = 128


HarnessConstraintConfig = HarnessConstraints


# pylint: disable=too-many-instance-attributes
@dataclass
class HarnessResult:
    """Result returned by BoundedVerificationHarness."""

    status: VerdictState | str
    iterations_used: int = 0
    tool_calls_used: int = 0
    execution_seconds: float = 0.0
    output_bytes_used: int = 0
    files_read_used: int = 0
    memory_mb_used: float = 0.0
    violated_constraint: str | None = None
    reason: str = ""
    payload: Any = None


# pylint: disable=too-many-instance-attributes
class BoundedVerificationHarness:
    """Enforces execution resource bounds during SAST verification loop."""

    def __init__(
        self,
        constraints: HarnessConstraints | None = None,
        memory_fn: Callable[[], float] | None = None,
    ) -> None:
        self.constraints = constraints or HarnessConstraints()
        self.memory_fn = memory_fn or _get_process_memory_mb

        self.iterations_used: int = 0
        self.tool_calls_used: int = 0
        self.start_time: float = 0.0
        self.execution_seconds: float = 0.0
        self.output_bytes_used: int = 0
        self.files_read_used: int = 0
        self.memory_mb_used: float = 0.0
        self.violated_constraint: str | None = None

    def reset(self) -> None:
        """Reset internal metrics to start a new verification run."""
        self.iterations_used = 0
        self.tool_calls_used = 0
        self.start_time = time.monotonic()
        self.execution_seconds = 0.0
        self.output_bytes_used = 0
        self.files_read_used = 0
        self.memory_mb_used = self.update_memory()
        self.violated_constraint = None

    def update_memory(self) -> float:
        """Fetch current process memory and update recorded memory usage."""
        try:
            val = self.memory_fn()
            self.memory_mb_used = max(self.memory_mb_used, val)
        except Exception:  # noqa: S110 # pylint: disable=broad-exception-caught
            pass
        return self.memory_mb_used

    # pylint: disable=too-many-return-statements
    def check_constraints(self, update_memory: bool = True) -> str | None:
        """Check current resource metrics against constraints.

        Returns constraint violation name if any limit is exceeded, else None.
        """
        if self.start_time > 0.0:
            self.execution_seconds = round(time.monotonic() - self.start_time, 4)

        if update_memory:
            self.update_memory()

        if self.iterations_used > self.constraints.max_iterations:
            return "max_iterations"

        if self.tool_calls_used > self.constraints.max_tool_calls:
            return "max_tool_calls"

        if self.execution_seconds > self.constraints.max_execution_seconds:
            return "max_execution_seconds"

        if self.output_bytes_used > self.constraints.max_output_bytes:
            return "max_output_bytes"

        if self.files_read_used > self.constraints.max_files_read:
            return "max_files_read"

        if self.memory_mb_used > float(self.constraints.max_memory_mb):
            return "max_memory_mb"

        return None

    def record_iteration(self) -> str | None:
        """Increment iteration count and return constraint violation if any."""
        self.iterations_used += 1
        violation = self.check_constraints()
        if violation is not None:
            self._log_violation(violation)
        return violation

    def record_tool_call(self, count: int = 1) -> str | None:
        """Record tool call(s) and return constraint violation if any."""
        self.tool_calls_used += count
        violation = self.check_constraints()
        if violation is not None:
            self._log_violation(violation)
        return violation

    def record_output(self, byte_count: int) -> str | None:
        """Record output bytes and return constraint violation if any."""
        self.output_bytes_used += byte_count
        violation = self.check_constraints()
        if violation is not None:
            self._log_violation(violation)
        return violation

    def record_file_read(self, count: int = 1) -> str | None:
        """Record file read operations and return constraint violation if any."""
        self.files_read_used += count
        violation = self.check_constraints()
        if violation is not None:
            self._log_violation(violation)
        return violation

    def set_memory_mb(self, memory_mb: float) -> str | None:
        """Explicitly set memory usage (useful for testing) and return violation."""
        self.memory_mb_used = memory_mb
        violation = self.check_constraints(update_memory=False)
        if violation is not None:
            self._log_violation(violation)
        return violation

    def _log_violation(self, violation: str) -> None:
        """Log constraint violation name."""
        self.violated_constraint = violation
        logger.warning(
            "Constraint violation: %s (iterations=%d, tool_calls=%d, "
            "exec_time=%.2fs, output_bytes=%d, files_read=%d, memory_mb=%.2f)",
            violation,
            self.iterations_used,
            self.tool_calls_used,
            self.execution_seconds,
            self.output_bytes_used,
            self.files_read_used,
            self.memory_mb_used,
        )

    # pylint: disable=too-many-return-statements
    def run(
        self,
        step_fn: Callable[[int, "BoundedVerificationHarness"], Any],
    ) -> HarnessResult:
        """Execute verification loop with strict bound enforcement."""
        self.reset()

        while True:
            if self.iterations_used >= self.constraints.max_iterations:
                violation = "max_iterations"
                self._log_violation(violation)
                return HarnessResult(
                    status=VerdictState.NOT_ENOUGH_CONTEXT,
                    iterations_used=self.iterations_used,
                    tool_calls_used=self.tool_calls_used,
                    execution_seconds=self.execution_seconds,
                    output_bytes_used=self.output_bytes_used,
                    files_read_used=self.files_read_used,
                    memory_mb_used=self.memory_mb_used,
                    violated_constraint=violation,
                    reason=f"Constraint violated: {violation}",
                )

            violation_iter = self.record_iteration()
            if violation_iter is not None:
                return HarnessResult(
                    status=VerdictState.NOT_ENOUGH_CONTEXT,
                    iterations_used=self.iterations_used,
                    tool_calls_used=self.tool_calls_used,
                    execution_seconds=self.execution_seconds,
                    output_bytes_used=self.output_bytes_used,
                    files_read_used=self.files_read_used,
                    memory_mb_used=self.memory_mb_used,
                    violated_constraint=violation_iter,
                    reason=f"Constraint violated: {violation_iter}",
                )

            try:
                res = step_fn(self.iterations_used, self)
            except Exception as exc:  # pylint: disable=broad-exception-caught
                logger.error("Error in verification loop step: %s", exc)
                return HarnessResult(
                    status=VerdictState.NOT_ENOUGH_CONTEXT,
                    iterations_used=self.iterations_used,
                    tool_calls_used=self.tool_calls_used,
                    execution_seconds=self.execution_seconds,
                    output_bytes_used=self.output_bytes_used,
                    files_read_used=self.files_read_used,
                    memory_mb_used=self.memory_mb_used,
                    reason=f"Step execution exception: {exc}",
                )

            post_violation = self.check_constraints()
            if post_violation is not None:
                self._log_violation(post_violation)
                return HarnessResult(
                    status=VerdictState.NOT_ENOUGH_CONTEXT,
                    iterations_used=self.iterations_used,
                    tool_calls_used=self.tool_calls_used,
                    execution_seconds=self.execution_seconds,
                    output_bytes_used=self.output_bytes_used,
                    files_read_used=self.files_read_used,
                    memory_mb_used=self.memory_mb_used,
                    violated_constraint=post_violation,
                    reason=f"Constraint violated: {post_violation}",
                )

            if res is not None:
                if isinstance(res, HarnessResult):
                    return res

                if isinstance(res, VerdictState):
                    return HarnessResult(
                        status=res,
                        iterations_used=self.iterations_used,
                        tool_calls_used=self.tool_calls_used,
                        execution_seconds=self.execution_seconds,
                        output_bytes_used=self.output_bytes_used,
                        files_read_used=self.files_read_used,
                        memory_mb_used=self.memory_mb_used,
                        payload=res,
                    )

                if hasattr(res, "state"):
                    return HarnessResult(
                        status=res.state,
                        iterations_used=self.iterations_used,
                        tool_calls_used=self.tool_calls_used,
                        execution_seconds=self.execution_seconds,
                        output_bytes_used=self.output_bytes_used,
                        files_read_used=self.files_read_used,
                        memory_mb_used=self.memory_mb_used,
                        payload=res,
                    )

                if isinstance(res, dict) and "status" in res:
                    return HarnessResult(
                        status=res["status"],
                        iterations_used=self.iterations_used,
                        tool_calls_used=self.tool_calls_used,
                        execution_seconds=self.execution_seconds,
                        output_bytes_used=self.output_bytes_used,
                        files_read_used=self.files_read_used,
                        memory_mb_used=self.memory_mb_used,
                        payload=res,
                    )

                if isinstance(res, str) and res != VerdictState.NOT_ENOUGH_CONTEXT:
                    return HarnessResult(
                        status=res,
                        iterations_used=self.iterations_used,
                        tool_calls_used=self.tool_calls_used,
                        execution_seconds=self.execution_seconds,
                        output_bytes_used=self.output_bytes_used,
                        files_read_used=self.files_read_used,
                        memory_mb_used=self.memory_mb_used,
                        payload=res,
                    )
