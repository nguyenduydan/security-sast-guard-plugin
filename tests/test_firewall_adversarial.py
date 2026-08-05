"""Adversarial unit tests for Anti-Bypass & Tamper Resistance in Command Firewall."""

import base64
import shutil
import subprocess
from pathlib import Path

import pytest

HOOK_PATH = Path(__file__).parent.parent / "hooks" / "firewall_hook.ps1"
REPO_ROOT = Path(__file__).parent.parent


def find_powershell() -> str | None:
    """Dynamically locate PowerShell executable across Windows and Linux CI runners."""
    for exe in ["powershell.exe", "pwsh", "powershell"]:
        found = shutil.which(exe)
        if found:
            return found
    return None


POWERSHELL_EXE = find_powershell()

pytestmark = pytest.mark.skipif(
    POWERSHELL_EXE is None,
    reason="PowerShell executable (powershell.exe or pwsh) not found on system",
)


def run_firewall_hook(
    command_text: str, cwd: Path = REPO_ROOT, hook_path: Path = HOOK_PATH
) -> tuple[str, int]:
    """Run firewall_hook.ps1 with specified command string."""
    cmd = [
        POWERSHELL_EXE or "powershell.exe",
        "-NoProfile",
        "-ExecutionPolicy",
        "Bypass",
        "-File",
        str(hook_path),
        "-CommandText",
        command_text,
    ]
    result = subprocess.run(  # noqa: S603
        cmd, capture_output=True, text=True, cwd=cwd, check=False
    )
    output = result.stdout.strip()
    return output, result.returncode


def test_firewall_standard_commands() -> None:
    """Test standard allow, confirm, deny verdicts."""
    out_allow, code_allow = run_firewall_hook("git status")
    assert code_allow == 0
    assert out_allow == "ALLOW"

    out_confirm, code_confirm = run_firewall_hook("Remove-Item test.txt")
    assert code_confirm == 0
    assert out_confirm == "CONFIRM"

    out_deny, code_deny = run_firewall_hook("rm -rf /")
    assert code_deny == 0
    assert out_deny == "DENY"


def test_firewall_disk_format_commands() -> None:
    """Test DENY verdict on disk format and partition removal commands."""
    out_cmd_format, _ = run_firewall_hook("format D: /fs:NTFS /q /v:Data")
    assert out_cmd_format == "DENY"

    cmd_fmt = (
        "Format-Volume -DriveLetter D -FileSystem NTFS "
        '-NewFileSystemLabel "Data" -Confirm:$false'
    )
    out_format_vol, _ = run_firewall_hook(cmd_fmt)
    assert out_format_vol == "DENY"

    out_clear_disk, _ = run_firewall_hook("Clear-Disk -Number 1 -RemoveData")
    assert out_clear_disk == "DENY"


def test_firewall_advanced_security_deny_rules() -> None:
    """Test DENY verdict on defender bypass and remote execution."""
    out_mp, _ = run_firewall_hook("Set-MpPreference -DisableRealtimeMonitoring $true")
    assert out_mp == "DENY"

    out_fw, _ = run_firewall_hook("Disable-NetFirewallRule -DisplayName RuleName")
    assert out_fw == "DENY"

    out_icmd, _ = run_firewall_hook(
        "Invoke-Command -ComputerName Server -ScriptBlock { Get-Process }"
    )
    assert out_icmd == "DENY"

    out_rm_rec, _ = run_firewall_hook("Remove-Item -Path C:\\Windows -Recurse -Force")
    assert out_rm_rec == "DENY"


def test_firewall_deobfuscation_carets_backticks() -> None:
    """Test deobfuscation of CMD carets and PowerShell backticks."""

    out_caret, _ = run_firewall_hook("r^m^ -r^f /")
    assert out_caret == "DENY"

    out_backtick, _ = run_firewall_hook("Invoke-Ex`pression ('rm -rf')")
    assert out_backtick == "DENY"


def test_firewall_base64_encoded_commands() -> None:
    """Test automatic detection and decoding of Base64 commands."""

    raw_payload = "rm -rf /"
    b64_utf16 = base64.b64encode(raw_payload.encode("utf-16le")).decode("ascii")
    cmd_enc = f"powershell.exe -enc {b64_utf16}"
    out_enc, _ = run_firewall_hook(cmd_enc)
    assert out_enc == "DENY"

    b64_utf8 = base64.b64encode(raw_payload.encode("utf-8")).decode("ascii")
    cmd_b64 = f"[System.Convert]::FromBase64String('{b64_utf8}')"
    out_b64, _ = run_firewall_hook(cmd_b64)
    assert out_b64 == "DENY"


def test_firewall_tamper_detection(tmp_path: Path) -> None:
    """Test tamper detection when profile.json checksum mismatches."""
    temp_hooks = tmp_path / "hooks"
    temp_hooks.mkdir()
    temp_hook_file = temp_hooks / "firewall_hook.ps1"
    temp_hook_file.write_text(HOOK_PATH.read_text(encoding="utf-8"), encoding="utf-8")

    profile_file = tmp_path / "profile.json"
    profile_content = '{"command_firewall_overlay": {"deny": ["forbidden"]}}'
    profile_file.write_text(profile_content, encoding="utf-8")

    sha_file = tmp_path / ".profile.sha256"
    fake_sha = "0000000000000000000000000000000000000000000000000000000000000000"
    sha_file.write_text(fake_sha, encoding="ascii")

    out, code = run_firewall_hook("git status", cwd=tmp_path, hook_path=temp_hook_file)
    assert code == 1
    assert out == "DENY"


def test_firewall_fail_closed_missing_or_corrupted(tmp_path: Path) -> None:
    """Test fail-closed behavior when profile.json is missing or corrupted."""
    temp_hooks = tmp_path / "hooks"
    temp_hooks.mkdir()
    temp_hook_file = temp_hooks / "firewall_hook.ps1"
    temp_hook_file.write_text(HOOK_PATH.read_text(encoding="utf-8"), encoding="utf-8")

    out_missing, code_missing = run_firewall_hook(
        "git status", cwd=tmp_path, hook_path=temp_hook_file
    )
    assert code_missing == 1
    assert out_missing == "DENY"

    (tmp_path / "profile.json").write_text("INVALID JSON {{{", encoding="utf-8")
    out_corrupt, code_corrupt = run_firewall_hook(
        "git status", cwd=tmp_path, hook_path=temp_hook_file
    )
    assert code_corrupt == 1
    assert out_corrupt == "DENY"
