"""Unit tests for CLI dispatcher and profile loader."""

from pytest import CaptureFixture

from src.cli.dispatcher import main
from src.infrastructure.profile_loader import ProfileLoader


def test_profile_loader_nonexistent_file() -> None:
    loader = ProfileLoader()
    result = loader.load("non_existent_file.json")
    assert result == {}


def test_dispatcher_status_command(capsys: CaptureFixture[str]) -> None:
    code = main(["status"])
    assert code == 0
    captured = capsys.readouterr()
    assert "SAST Security & Firewall Guard Status" in captured.out
    assert "Project ID" in captured.out
    assert "Command Firewall Overlay:" in captured.out


def test_dispatcher_unknown_command(capsys: CaptureFixture[str]) -> None:
    code = main(["unknown_action"])
    assert code == 1
    captured = capsys.readouterr()
    assert "Unknown command: unknown_action" in captured.out


def test_dispatcher_scan_command(capsys: CaptureFixture[str], tmp_path) -> None:
    test_file = tmp_path / "test.html"
    test_file.write_text('<input onfocus="alert(1)">', encoding="utf-8")
    code = main(["scan", str(test_file)])
    assert code == 0
    captured = capsys.readouterr()
    assert "SAST Audit completed." in captured.out
    assert "Detailed report saved to:" in captured.out


def test_dispatcher_level_command(capsys: CaptureFixture[str]) -> None:
    code = main(["level"])
    assert code == 0
    captured = capsys.readouterr()
    assert "Current Audit Level:" in captured.out

    code_set = main(["level", "lite"])
    assert code_set == 0
    captured_set = capsys.readouterr()
    assert "Audit level successfully set to 'lite'." in captured_set.out

    code_status = main(["status"])
    assert code_status == 0
    captured_status = capsys.readouterr()
    assert "Audit Level    : lite" in captured_status.out
    assert "SAST Scan Rules:" in captured_status.out
    assert "Integrity      :" in captured_status.out

    # Reset back to full for consistency
    main(["level", "full"])


def test_audit_service_status_dynamic_reload() -> None:
    from src.application.audit_service import AuditService

    service = AuditService()
    service.set_audit_level("ultra")
    status = service.get_status()
    assert status["audit_level"] == "ultra"
    assert "sast_rules_count" in status
    assert "checksum_valid" in status

    # Reset back to full
    service.set_audit_level("full")

