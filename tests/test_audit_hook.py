"""Unit tests for the SAST audit hook."""

import sys
from pathlib import Path

import pytest
from pytest import CaptureFixture

from hooks.run_audit_hook import main


def test_run_audit_hook_no_target(
    capsys: CaptureFixture[str], monkeypatch: pytest.MonkeyPatch
) -> None:
    """Test hook output when no target is specified via environment or argument."""
    monkeypatch.delenv("SAST_TARGET", raising=False)
    monkeypatch.setattr(sys, "argv", ["run_audit_hook.py"])

    exit_code = main()

    assert exit_code == 0
    captured = capsys.readouterr()
    assert (
        "Audit hook: No target specified via SAST_TARGET env or argument."
        in captured.out
    )


def test_run_audit_hook_with_target(
    capsys: CaptureFixture[str],
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    """Test hook execution when SAST_TARGET is provided."""
    test_file = tmp_path / "vulnerable.py"
    test_file.write_text("eval('import os')", encoding="utf-8")

    monkeypatch.setenv("SAST_TARGET", str(test_file))
    monkeypatch.setattr(sys, "argv", ["run_audit_hook.py"])

    exit_code = main()

    assert exit_code == 0
    captured = capsys.readouterr()
    assert "SAST Audit completed." in captured.out
