"""Unit tests for CLI dispatcher and profile loader."""

from pathlib import Path

from pytest import CaptureFixture

from src.application.audit_service import AuditService
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


def test_dispatcher_scan_diff_command(capsys: CaptureFixture[str]) -> None:
    code = main(["scan", "--diff"])
    assert code == 0
    captured = capsys.readouterr()
    assert "SAST Audit completed." in captured.out

    code_diff_pos = main(["scan", "diff"])
    assert code_diff_pos == 0
    captured_diff_pos = capsys.readouterr()
    assert "SAST Audit completed." in captured_diff_pos.out


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
    assert "Version        :" in captured_status.out

    # Reset back to full for consistency
    main(["level", "full"])


def test_audit_service_status_dynamic_reload() -> None:
    service = AuditService()
    service.set_audit_level("ultra")
    status = service.get_status()
    assert status["audit_level"] == "ultra"
    assert "sast_rules_count" in status
    assert "checksum_valid" in status

    # Reset back to full
    service.set_audit_level("full")


def test_cli_version_command(capsys: CaptureFixture[str]) -> None:
    code = main(["version"])
    assert code == 0
    captured = capsys.readouterr()
    assert "Security SAST Guard v" in captured.out
    assert "Python:" in captured.out
    assert "Platform:" in captured.out


def test_cli_firewall_command_deny(capsys: CaptureFixture[str]) -> None:
    code = main(["firewall", "Remove-Item -Recurse -Force C:\\Windows"])
    assert code == 0
    captured = capsys.readouterr()
    assert "DENY" in captured.out or "CONFIRM" in captured.out


def test_cli_firewall_command_allow(capsys: CaptureFixture[str]) -> None:
    code = main(["firewall", "git status"])
    assert code == 0
    captured = capsys.readouterr()
    assert "ALLOW" in captured.out


def test_cli_init_command(capsys: CaptureFixture[str], tmp_path, monkeypatch) -> None:
    monkeypatch.chdir(tmp_path)
    code = main(["init"])
    assert code == 0
    captured = capsys.readouterr()
    assert "Successfully initialized project profile" in captured.out
    assert (tmp_path / ".sast" / "profile.json").exists()


def test_dispatcher_scan_sarif_flag(capsys: CaptureFixture[str], tmp_path) -> None:
    test_file = tmp_path / "test.html"
    test_file.write_text('<input onfocus="alert(1)">', encoding="utf-8")
    sarif_file = tmp_path / "out.sarif"
    code = main(["scan", str(test_file), "--sarif", str(sarif_file)])
    assert code == 0
    captured = capsys.readouterr()
    assert "SARIF report saved to:" in captured.out
    assert sarif_file.exists()
    sarif_content = sarif_file.read_text(encoding="utf-8")
    assert '"version": "2.1.0"' in sarif_content


def test_dispatcher_scan_format_sarif(capsys: CaptureFixture[str], tmp_path) -> None:
    test_file = tmp_path / "clean.py"
    test_file.write_text("x = 1\n", encoding="utf-8")
    code = main(["scan", str(test_file), "--format", "sarif"])
    assert code == 0
    captured = capsys.readouterr()
    assert "SARIF report saved to:" in captured.out


def test_dispatcher_scan_html(capsys: CaptureFixture[str], tmp_path) -> None:
    test_file = tmp_path / "app.py"
    test_file.write_text("os.system('rm -rf /')\n", encoding="utf-8")
    html_file = tmp_path / "audit.html"
    code = main(["scan", str(test_file), "--html", str(html_file), "--threads", "2"])
    assert code == 0
    captured = capsys.readouterr()
    assert "HTML report saved to:" in captured.out
    assert html_file.exists()


def test_dispatcher_hook_commands(capsys: CaptureFixture[str], tmp_path) -> None:
    git_dir = tmp_path / ".git"
    git_dir.mkdir()
    code = main(["install-hook", str(tmp_path)])
    assert code == 0
    captured = capsys.readouterr()
    assert "pre-commit hook installed" in captured.out

    code_un = main(["uninstall-hook", str(tmp_path)])
    assert code_un == 0
    captured_un = capsys.readouterr()
    assert "Successfully uninstalled" in captured_un.out


def test_dispatcher_scan_verbose_flag(capsys: CaptureFixture[str], tmp_path) -> None:
    test_dir = tmp_path / "src"
    test_dir.mkdir()
    (test_dir / "a.py").write_text("x = 1\n", encoding="utf-8")
    (test_dir / "b.py").write_text("y = 2\n", encoding="utf-8")

    code_quiet = main(["scan", str(test_dir)])
    assert code_quiet == 0
    captured_quiet = capsys.readouterr()
    assert "Scanning" not in captured_quiet.out

    code_verbose = main(["scan", str(test_dir), "-v"])
    assert code_verbose == 0
    captured_verbose = capsys.readouterr()
    assert "Scanning" in captured_verbose.out


def test_dispatcher_scan_json_flag(capsys: CaptureFixture[str], tmp_path) -> None:
    test_file = tmp_path / "test.html"
    test_file.write_text('<input onfocus="alert(1)">', encoding="utf-8")
    json_file = tmp_path / "out.json"
    code = main(["scan", str(test_file), "--json", str(json_file)])
    assert code == 0
    captured = capsys.readouterr()
    assert "JSON report saved to:" in captured.out
    assert json_file.exists()
    json_content = json_file.read_text(encoding="utf-8")
    assert '"findings_count": 1' in json_content


def test_dispatcher_scan_format_json(
    capsys: CaptureFixture[str], tmp_path: Path
) -> None:
    test_file = tmp_path / "clean.py"
    test_file.write_text("x = 1\n", encoding="utf-8")
    code = main(["scan", str(test_file), "--format", "json"])
    assert code == 0
    captured = capsys.readouterr()
    assert "JSON report saved to:" in captured.out


def test_dispatcher_audit_folder_and_positional_prefixes(
    capsys: CaptureFixture[str], tmp_path: Path
) -> None:
    target_dir = tmp_path / "my_module"
    target_dir.mkdir()
    target_file = target_dir / "app.py"
    target_file.write_text("x = 1\n", encoding="utf-8")

    # Test 'sast audit folder <path>'
    code_folder = main(["audit", "folder", str(target_dir)])
    assert code_folder == 0
    captured_folder = capsys.readouterr()
    assert (
        "SAST Audit completed" in captured_folder.out
        or "Scan complete" in captured_folder.out
    )

    # Test 'sast audit dir <path>'
    code_dir = main(["audit", "dir", str(target_dir)])
    assert code_dir == 0
    captured_dir = capsys.readouterr()
    assert (
        "SAST Audit completed" in captured_dir.out
        or "Scan complete" in captured_dir.out
    )

    # Test 'sast audit file <path>'
    code_file = main(["audit", "file", str(target_file)])
    assert code_file == 0
    captured_file = capsys.readouterr()
    assert (
        "SAST Audit completed" in captured_file.out
        or "Scan complete" in captured_file.out
    )

    # Test 'sast audit codebase'
    code_cb = main(["audit", "codebase"])
    assert code_cb == 0
    captured_cb = capsys.readouterr()
    assert (
        "SAST Audit completed" in captured_cb.out or "Scan complete" in captured_cb.out
    )
