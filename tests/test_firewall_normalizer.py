"""Unit tests for FirewallNormalizer (10-Stage Deobfuscation Engine)."""

from __future__ import annotations

import time
from unittest.mock import patch

from src.domain.firewall_normalizer import FirewallNormalizer


def test_stage1_caret_backtick_stripping() -> None:
    normalizer = FirewallNormalizer()
    res = normalizer.normalize("p^o^w^e^r^s^h^e^l^l")
    assert any("powershell" in c for c in res)

    res_bt = normalizer.normalize("P`o`w`e`r`s`h`e`l`l")
    assert any("Powershell" in c or "PowerShell" in c for c in res_bt)


def test_stage2_base64_decode() -> None:
    normalizer = FirewallNormalizer()
    # "Remove-Item" in base64 UTF-16LE: "UgBlAG0AbwB2AGUALQBJAHQAZQBtAA=="
    b64_cmd = "powershell -enc UgBlAG0AbwB2AGUALQBJAHQAZQBtAA=="
    res = normalizer.normalize(b64_cmd)
    assert any("Remove-Item" in c for c in res)


def test_stage3_hex_decode() -> None:
    normalizer = FirewallNormalizer()
    cmd = r"\x52\x65\x6d\x6f\x76\x65\x2d\x49\x74\x65\x6d"
    res = normalizer.normalize(cmd)
    assert any("Remove-Item" in c for c in res)


def test_stage4_unicode_decode() -> None:
    normalizer = FirewallNormalizer()
    cmd = r"\u0052\u0065\u006d"
    res = normalizer.normalize(cmd)
    assert any("Rem" in c for c in res)


def test_stage5_env_var_expansion() -> None:
    normalizer = FirewallNormalizer()
    cmd = "$env:COMSPEC /c dir"
    res = normalizer.normalize(cmd)
    assert any("cmd.exe" in c.lower() for c in res)

    cmd_ifs = r"cat${IFS}/etc/passwd"
    res_ifs = normalizer.normalize(cmd_ifs)
    assert any("cat /etc/passwd" in c for c in res_ifs)


def test_stage6_string_interpolation() -> None:
    normalizer = FirewallNormalizer()
    cmd = r'"Invoke-$(' + "'Expres'+" + "'sion')" + '"'
    res = normalizer.normalize(cmd)
    assert any("Invoke-Expression" in c for c in res)


def test_stage7_char_code_assembly() -> None:
    normalizer = FirewallNormalizer()
    cmd = "[char]82+[char]101+[char]109"
    res = normalizer.normalize(cmd)
    assert any("Rem" in c for c in res)


def test_stage8_alias_expansion() -> None:
    normalizer = FirewallNormalizer()
    cmd = "rm -Force C:\\Windows"
    res = normalizer.normalize(cmd)
    assert any("Remove-Item" in c for c in res)

    cmd_iex = "iex (New-Object Net.WebClient)"
    res_iex = normalizer.normalize(cmd_iex)
    assert any("Invoke-Expression" in c for c in res_iex)


def test_stage9_subcommand_unpacking() -> None:
    normalizer = FirewallNormalizer()
    cmd = 'powershell -c "Remove-Item -Path C:\\secret"'
    res = normalizer.normalize(cmd)
    assert any(c == "Remove-Item -Path C:\\secret" for c in res)


def test_stage10_command_decomposition() -> None:
    normalizer = FirewallNormalizer()
    cmd = "echo hello && Remove-Item C:\\temp | dir"
    res = normalizer.normalize(cmd)
    assert any("Remove-Item C:\\temp" in c for c in res)
    assert any("echo hello" in c for c in res)


def test_stage_timeout_graceful_fallback() -> None:
    normalizer = FirewallNormalizer()

    def slow_stage(candidates: list[str]) -> list[str]:
        time.sleep(0.7)  # Exceeds 500ms timeout
        return [*candidates, "slow_result"]

    with patch.object(normalizer, "_stage1_strip_carets_backticks", slow_stage):
        res = normalizer.normalize("safe_command")
        # Should complete without error and fall back without slow_result
        assert "slow_result" not in res
        assert "safe_command" in res


def test_catastrophic_failure_fallback() -> None:
    normalizer = FirewallNormalizer()

    with patch.object(
        normalizer, "_run_stage_with_timeout", side_effect=RuntimeError("Fatal")
    ):
        res = normalizer.normalize("critical_command")
        assert res == ["critical_command"]


def test_adversarial_bypass_t2_threat_model() -> None:
    """10 Threat Model T2 Obfuscated Test Cases."""
    normalizer = FirewallNormalizer()
    test_cases = [
        ("r^e^m^o^v^e^-^i^t^e^m", "remove-item"),
        (r"\x52\x65\x6d\x6f\x76\x65\x2d\x49\x74\x65\x6d", "Remove-Item"),
        (r"\u0052\u0065\u006d\u006f\u0076\u0065", "Remove"),
        ("[char]82+[char]101+[char]109", "Rem"),
        ('powershell -c "rm -Recurse C:\\data"', "Remove-Item"),
        ("del /f /q C:\\boot.ini", "Remove-Item"),
        ('Invoke-$("Expres"+"sion") "calc.exe"', "Invoke-Expression"),
        ("cat${IFS}/etc/shadow", "cat /etc/shadow"),
        ("powershell -enc UgBlAG0AbwB2AGUALQBJAHQAZQBtAA==", "Remove-Item"),
        ("cmd /c dir && rm -rf /", "Remove-Item"),
    ]

    for obfuscated, expected_substr in test_cases:
        res = normalizer.normalize(obfuscated)
        assert any(expected_substr.lower() in c.lower() for c in res), (
            f"Failed for obfuscated input: {obfuscated}, candidates: {res}"
        )
