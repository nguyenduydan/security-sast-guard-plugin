"""Unit tests for FirewallEngine domain logic."""

from __future__ import annotations

from src.domain.firewall_engine import FirewallEngine


def test_firewall_engine_allow() -> None:
    engine = FirewallEngine(deny_rules=[r"rm\s+-rf"], confirm_rules=[r"pip\s+install"])
    verdict = engine.evaluate("git status")
    assert verdict.verdict == "ALLOW"
    assert verdict.matched_pattern is None


def test_firewall_engine_deny() -> None:
    engine = FirewallEngine(deny_rules=[r"Remove-Item.*-Recurse"])
    verdict = engine.evaluate("Remove-Item -Recurse -Force C:\\Windows")
    assert verdict.verdict == "DENY"
    assert verdict.matched_pattern is not None


def test_firewall_engine_confirm() -> None:
    engine = FirewallEngine(confirm_rules=[r"pip\s+install"])
    verdict = engine.evaluate("pip install requests")
    assert verdict.verdict == "CONFIRM"


def test_firewall_engine_deobfuscation() -> None:
    engine = FirewallEngine(deny_rules=[r"Remove-Item"])
    # Caret obfuscated command: R^e^m^o^v^e^-I^t^e^m
    verdict = engine.evaluate("R^e^m^o^v^e^-I^t^e^m C:\\Windows")
    assert verdict.verdict == "DENY"


def test_firewall_engine_compound_and_unpacking() -> None:
    engine = FirewallEngine(
        deny_rules=[r"Remove-Item.*-Recurse", r"git\s+push\s+.*(--force|-f\b)"],
        confirm_rules=[r"\brd\s+"],
    )
    # Chained command with git push -f
    verdict1 = engine.evaluate("cd src && git push -f origin main")
    assert verdict1.verdict == "DENY"

    # Unpack powershell -c subcommand payload
    verdict2 = engine.evaluate('powershell -c "Remove-Item -Recurse C:\\temp"')
    assert verdict2.verdict == "DENY"

    # PowerShell rm -rf alias/flag expansion
    verdict3 = engine.evaluate("rm -rf C:\\temp")
    assert verdict3.verdict == "DENY"

    # False positive prevention on 'third'
    verdict4 = engine.evaluate("echo third item")
    assert verdict4.verdict == "ALLOW"
