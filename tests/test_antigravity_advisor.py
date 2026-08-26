"""Unit tests for Antigravity Python SDK Advisor and AI Triage integration."""

import sys
from types import ModuleType
from typing import Any
from unittest.mock import AsyncMock, MagicMock, patch

from src.application.audit_service import AuditService
from src.cli.dispatcher import main
from src.domain.antigravity_advisor import (
    AntigravitySecurityAdvisor,
    is_sdk_available,
)
from src.domain.models import AIFindingAdvice, AITokenUsage, AntigravityAuditReport
from src.infrastructure.report_generator import (
    _format_ai_report_block,
    generate_markdown_report,
)


def test_is_sdk_available_not_installed() -> None:
    """Test is_sdk_available when google.antigravity is not in sys.modules."""
    with patch("importlib.util.find_spec", return_value=None):
        assert is_sdk_available() is False


def test_is_sdk_available_when_parent_module_not_found() -> None:
    """Test is_sdk_available when parent google module raises ModuleNotFoundError."""
    with patch(
        "importlib.util.find_spec",
        side_effect=ModuleNotFoundError("No module named 'google'"),
    ):
        assert is_sdk_available() is False


def test_estimate_tokens() -> None:
    """Test token estimation fallback."""
    advisor = AntigravitySecurityAdvisor()
    assert advisor.estimate_tokens("") == 0
    assert advisor.estimate_tokens("Hello world") >= 1
    assert advisor.estimate_tokens("A" * 400) == 100


def test_build_triage_prompt() -> None:
    """Test building structured prompt with findings."""
    advisor = AntigravitySecurityAdvisor()
    findings = [
        {
            "rule_id": "SQL_INJECTION",
            "rule_name": "SQL Injection in Query",
            "path": "app/db.py",
            "line": 42,
            "line_content": "cursor.execute('SELECT * FROM users WHERE id=' + uid)",
            "severity": "CRITICAL",
            "context_window": ["uid = req.get('id')", "cursor.execute('SELECT * ...')"],
        }
    ]
    prompt = advisor._build_triage_prompt(
        findings, {"stack": "python", "mode": "strict"}
    )
    assert "SQL_INJECTION" in prompt
    assert "app/db.py" in prompt
    assert "python" in prompt
    assert "Target Project Stack" in prompt


def test_extract_token_usage_with_usage_object() -> None:
    """Test extracting token usage from an object with usage attributes."""
    advisor = AntigravitySecurityAdvisor()

    class MockUsage:
        input_tokens = 150
        thinking_tokens = 50
        output_tokens = 100
        total_tokens = 300

    class MockResponse:
        usage = MockUsage()

    usage = advisor._extract_token_usage(MockResponse(), "prompt")
    assert usage.input_tokens == 150
    assert usage.thinking_tokens == 50
    assert usage.output_tokens == 100
    assert usage.total_tokens == 300


def test_extract_token_usage_fallback() -> None:
    """Test token extraction fallback when response lacks usage."""
    advisor = AntigravitySecurityAdvisor()

    class MockResponse:
        usage = None

    prompt = "A" * 400
    usage = advisor._extract_token_usage(MockResponse(), prompt)
    assert usage.input_tokens == 100
    assert usage.total_tokens == 100


def test_parse_agent_response_json() -> None:
    """Test parsing structured JSON from agent response."""
    advisor = AntigravitySecurityAdvisor()
    json_text = """```json
{
  "executive_summary": "1 Critical SQL injection identified.",
  "findings_advice": [
    {
      "index": 1,
      "rule_id": "SQL_INJECTION",
      "file_path": "app/db.py",
      "line": 42,
      "is_likely_false_positive": false,
      "exploitability": "High",
      "analysis": "Unsanitized user input concatenation into SQL query string.",
      "suggested_fix": "cursor.execute('SELECT * FROM users WHERE id = %s', (uid,))"
    }
  ]
}
```"""
    summary, advice = advisor._parse_agent_response(json_text, [])
    assert summary == "1 Critical SQL injection identified."
    assert len(advice) == 1
    assert advice[0].rule_id == "SQL_INJECTION"
    assert advice[0].exploitability == "High"
    assert "cursor.execute" in advice[0].suggested_fix
    assert advice[0].is_likely_false_positive is False


def test_parse_agent_response_fallback_unstructured() -> None:
    """Test parsing fallback when response is unstructured text."""
    advisor = AntigravitySecurityAdvisor()
    findings = [{"rule_id": "XSS", "path": "views.py", "line": 12}]
    summary, advice = advisor._parse_agent_response(
        "Plain text response from agent", findings
    )
    assert "Plain text response" in summary
    assert len(advice) == 1
    assert advice[0].rule_id == "XSS"


def test_analyze_findings_when_not_installed() -> None:
    """Test analyze_findings graceful return when SDK is not installed."""
    advisor = AntigravitySecurityAdvisor()
    findings = [{"rule_id": "SQL_INJECTION", "path": "db.py", "line": 10}]
    with patch.object(advisor, "is_available", return_value=False):
        report = advisor.analyze_findings(findings)
        assert report.status == "not_installed"
        assert report.findings_advice == []
        assert "not installed" in report.executive_summary


def test_analyze_findings_empty_findings() -> None:
    """Test analyze_findings when findings list is empty."""
    advisor = AntigravitySecurityAdvisor()
    report = advisor.analyze_findings([])
    assert report.status == "skipped"
    assert report.findings_advice == []


def test_analyze_findings_with_mocked_sdk(tmp_path: Any) -> None:
    """Test full analyze_findings workflow with mocked google.antigravity SDK."""
    from src.domain.ai_cache import AICache

    cache = AICache(cache_file=tmp_path / "test_mock_cache.json")
    advisor = AntigravitySecurityAdvisor(cache=cache)
    findings = [
        {
            "rule_id": "COMMAND_INJECTION",
            "path": "cmd.py",
            "line": 15,
            "line_content": "os.system(user_cmd)",
            "severity": "CRITICAL",
        }
    ]

    mock_response = MagicMock()
    mock_response.text = """```json
{
  "executive_summary": "High risk command injection.",
  "findings_advice": [
    {
      "rule_id": "COMMAND_INJECTION",
      "file_path": "cmd.py",
      "line": 15,
      "is_likely_false_positive": false,
      "exploitability": "High",
      "analysis": "Direct shell execution of untrusted input.",
      "suggested_fix": "subprocess.run(['sh', '-c', ...])"
    }
  ]
}
```"""
    mock_usage = MagicMock()
    mock_usage.input_tokens = 500
    mock_usage.thinking_tokens = 200
    mock_usage.output_tokens = 300
    mock_usage.total_tokens = 1000
    mock_response.usage = mock_usage

    mock_agent_instance = MagicMock()
    mock_agent_instance.chat = AsyncMock(return_value=mock_response)
    mock_agent_instance.__aenter__ = AsyncMock(return_value=mock_agent_instance)
    mock_agent_instance.__aexit__ = AsyncMock(return_value=None)

    mock_module = ModuleType("google.antigravity")
    mock_module.Agent = MagicMock(return_value=mock_agent_instance)  # type: ignore[attr-defined]
    mock_module.LocalAgentConfig = MagicMock()  # type: ignore[attr-defined]
    mock_module.CapabilitiesConfig = MagicMock()  # type: ignore[attr-defined]

    with (
        patch.dict(sys.modules, {"google.antigravity": mock_module}),
        patch.object(advisor, "is_available", return_value=True),
    ):
        report = advisor.analyze_findings(findings, {"stack": "python"})
        assert report.status == "success"
        assert report.executive_summary == "High risk command injection."
        assert report.token_usage.total_tokens == 1000
        assert len(report.findings_advice) == 1
        assert report.findings_advice[0].rule_id == "COMMAND_INJECTION"


def test_format_ai_report_block() -> None:
    """Test markdown formatting of AI report and token telemetry."""
    ai_data: dict[str, Any] = {
        "status": "success",
        "summary": "Overall posture requires attention.",
        "token_usage": {
            "input_tokens": 1200,
            "thinking_tokens": 400,
            "output_tokens": 600,
            "total_tokens": 2200,
        },
        "findings_advice": [
            {
                "rule_id": "HARDCODED_SECRET",
                "file_path": "config.py",
                "line": 5,
                "analysis": "Secret key committed directly in code.",
                "exploitability": "High",
                "suggested_fix": "SECRET_KEY = os.environ.get('SECRET_KEY')",
                "is_likely_false_positive": False,
            }
        ],
    }

    block = _format_ai_report_block(ai_data)
    assert "🤖 Antigravity AI Security Intelligence & Token Telemetry" in block
    assert "1,200" in block
    assert "2,200" in block
    assert "HARDCODED_SECRET" in block
    assert "SECRET_KEY = os.environ" in block


def test_generate_markdown_report_with_ai_report(tmp_path: Any) -> None:
    """Test generate_markdown_report with AI metadata."""
    findings = [
        {
            "rule_id": "EVAL_INJECTION",
            "path": "eval.py",
            "line": 8,
            "line_content": "eval(code)",
            "severity": "CRITICAL",
        }
    ]
    metadata = {
        "scanned_files": 1,
        "total_lines": 20,
        "duration_seconds": 0.05,
        "ai_report": {
            "status": "success",
            "summary": "Direct eval() is dangerous.",
            "token_usage": {
                "input_tokens": 100,
                "output_tokens": 50,
                "total_tokens": 150,
            },
            "findings_advice": [
                {
                    "rule_id": "EVAL_INJECTION",
                    "file_path": "eval.py",
                    "line": 8,
                    "analysis": "Arbitrary code execution risk.",
                    "exploitability": "Critical",
                    "suggested_fix": "ast.literal_eval(code)",
                }
            ],
        },
    }

    report_path, summary = generate_markdown_report(
        findings=findings,
        output_dir=str(tmp_path),
        metadata=metadata,
    )
    assert report_path != ""
    assert "Total: 1 findings" in summary
    with open(report_path, encoding="utf-8") as f:
        content = f.read()
    assert "Antigravity AI Security Intelligence" in content
    assert "ast.literal_eval" in content


def test_audit_service_with_enable_ai(tmp_path: Any) -> None:
    """Test AuditService.run_audit with enable_ai flag."""
    test_file = tmp_path / "vulnerable.py"
    test_file.write_text("import os\nos.system('ls')\n", encoding="utf-8")

    mock_report = AntigravityAuditReport(
        executive_summary="Found os.system call.",
        findings_advice=[
            AIFindingAdvice(
                rule_id="COMMAND_INJECTION",
                file_path=str(test_file),
                line=2,
                analysis="os.system is deprecated and insecure.",
                exploitability="Medium",
                suggested_fix="subprocess.run(['ls'])",
            )
        ],
        token_usage=AITokenUsage(
            input_tokens=300,
            thinking_tokens=100,
            output_tokens=200,
            total_tokens=600,
        ),
        status="success",
    )

    service = AuditService()
    with patch(
        "src.application.audit_service.AntigravitySecurityAdvisor.analyze_findings",
        return_value=mock_report,
    ):
        findings, _, summary = service.run_audit(
            str(test_file),
            enable_ai=True,
        )
        assert len(findings) >= 0
        if findings:
            assert "🤖 Antigravity AI Telemetry" in summary
            assert "600 tokens" in summary


def test_dispatcher_ai_flag(tmp_path: Any, capsys: Any) -> None:
    """Test CLI dispatcher with --ai flag."""
    test_file = tmp_path / "clean.py"
    test_file.write_text("print('Hello')", encoding="utf-8")

    code = main(["scan", str(test_file), "--ai"])
    captured = capsys.readouterr()
    assert code == 0
    assert "SAST Audit completed" in captured.out


def test_dispatcher_ai_triage_subcommand(tmp_path: Any, capsys: Any) -> None:
    """Test CLI dispatcher with ai-triage subcommand."""
    test_file = tmp_path / "clean.py"
    test_file.write_text("print('Clean code')", encoding="utf-8")

    code = main(["ai-triage", str(test_file)])
    captured = capsys.readouterr()
    assert code == 0
    assert "SAST Audit completed" in captured.out


def test_analyze_findings_cache_hit(tmp_path: Any) -> None:
    """Test that cached findings consume 0 tokens and return cached advice."""
    from src.domain.ai_cache import AICache

    cache_file = tmp_path / "test_cache.json"
    cache = AICache(cache_file=cache_file)
    advisor = AntigravitySecurityAdvisor(cache=cache)

    finding = {
        "rule_id": "HARDCODED_API_KEY",
        "path": "secret.py",
        "line": 1,
        "line_content": "API_KEY = 'AIzaSy12345'",
    }
    key = advisor._compute_finding_cache_key(finding)
    cache.set_advice(
        key,
        {
            "rule_id": "HARDCODED_API_KEY",
            "file_path": "secret.py",
            "line": 1,
            "analysis": "Cached secret analysis",
            "exploitability": "High",
            "suggested_fix": "os.environ['API_KEY']",
            "is_likely_false_positive": False,
        },
    )

    with patch.object(advisor, "is_available", return_value=True):
        report = advisor.analyze_findings([finding])
        assert report.status == "success"
        assert report.token_usage.total_tokens == 0
        assert len(report.findings_advice) == 1
        assert report.findings_advice[0].suggested_fix == "os.environ['API_KEY']"
        assert "local SHA-256 cache" in report.executive_summary


def test_adaptive_batching_multiple_batches(tmp_path: Any) -> None:
    """Test adaptive batching splits findings and aggregates tokens."""
    from src.domain.ai_cache import AICache

    cache_file = tmp_path / "test_cache.json"
    cache = AICache(cache_file=cache_file)
    advisor = AntigravitySecurityAdvisor(cache=cache, batch_size=2)

    findings = [
        {
            "rule_id": f"RULE_{i}",
            "path": f"file_{i}.py",
            "line": i,
            "line_content": f"code_{i}",
        }
        for i in range(5)
    ]

    mock_batch_result = (
        "Batch summary",
        [
            AIFindingAdvice(
                rule_id="RULE_X",
                file_path="file_X.py",
                line=1,
                analysis="Analysis",
                exploitability="Medium",
                suggested_fix="Fix",
            )
        ],
        AITokenUsage(input_tokens=100, output_tokens=50, total_tokens=150),
    )

    with (
        patch.object(advisor, "is_available", return_value=True),
        patch.object(
            advisor, "_analyze_batch", AsyncMock(return_value=mock_batch_result)
        ) as mock_batch,
    ):
        report = advisor.analyze_findings(findings)
        assert report.status == "success"
        # 5 items with batch_size=2 => 3 batches (2, 2, 1)
        assert mock_batch.call_count == 3
        # 3 batches * 150 tokens = 450 tokens
        assert report.token_usage.total_tokens == 450
