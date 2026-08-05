from src.domain.models import Finding


def test_finding_action_default_and_custom():
    f1 = Finding(
        rule_id="TEST_01",
        rule_name="Test Rule",
        path="src/main.py",
        line=10,
        line_content="eval(x)",
        severity="HIGH",
    )
    assert f1.action == "Block"

    f2 = Finding(
        rule_id="TEST_02",
        rule_name="Warn Rule",
        path="src/main.py",
        line=20,
        line_content="print(x)",
        severity="MEDIUM",
        action="Warn",
    )
    assert f2.action == "Warn"
