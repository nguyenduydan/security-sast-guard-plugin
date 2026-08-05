from src.domain.models import Finding
from src.domain.sast_scanner import SASTScanner


def test_scanner_assigns_action_from_rules():
    rules = [
        {
            "id": "WARN_RULE",
            "name": "Warning Test",
            "description": "Desc",
            "category": "test",
            "severity": "Medium",
            "action": "Warn",
            "patterns": [r"insecure_call"],
        }
    ]
    scanner = SASTScanner(rules=rules)
    findings = scanner.scan_code("insecure_call()", "app.py")
    assert len(findings) == 1
    assert isinstance(findings[0], Finding)
    assert findings[0].action == "Warn"
