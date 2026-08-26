"""Unit tests for Antigravity AI PR Review Bot and script runner."""

import json
from types import ModuleType
from typing import Any
from unittest.mock import AsyncMock, MagicMock, patch

from scripts.pr_reviewer import (
    BOT_MARKER,
    _get_git_diff,
    _load_github_event,
    _post_github_comment,
    run_pr_review,
)
from src.domain.models import AITokenUsage
from src.domain.pr_review_advisor import (
    PRReviewAdvisor,
    PRReviewComment,
    PRReviewResult,
)


def test_pr_review_result_to_markdown_approve() -> None:
    """Test rendering markdown report for APPROVE verdict."""
    res = PRReviewResult(
        verdict="APPROVE",
        summary="Changes look great and secure.",
        comments=[],
        token_usage=AITokenUsage(
            input_tokens=1000,
            thinking_tokens=300,
            output_tokens=200,
            total_tokens=1500,
        ),
    )
    md = res.to_markdown()
    assert "Antigravity AI - Pull Request Review Report" in md
    assert "APPROVE" in md
    assert "1,500" in md
    assert "Clean Codebase" in md


def test_pr_review_result_to_markdown_request_changes() -> None:
    """Test rendering markdown report for REQUEST_CHANGES verdict with comments."""
    res = PRReviewResult(
        verdict="REQUEST_CHANGES",
        summary="Critical vulnerability found in PR diff.",
        comments=[
            PRReviewComment(
                category="SECURITY",
                file_path="src/api.py",
                line=25,
                severity="CRITICAL",
                title="SQL Injection Vulnerability",
                comment="Raw query concatenation allows arbitrary DB execution.",
                suggested_fix=(
                    "cursor.execute('SELECT * FROM users WHERE id = %s', (uid,))"
                ),
            ),
            PRReviewComment(
                category="CLEAN_CODE",
                file_path="src/utils.py",
                line=10,
                severity="LOW",
                title="Dead Function Detected",
                comment="Unused helper function should be deleted (Ponytail YAGNI).",
            ),
        ],
    )
    md = res.to_markdown()
    assert "REQUEST CHANGES" in md
    assert "SQL Injection Vulnerability" in md
    assert "cursor.execute" in md
    assert "Dead Function Detected" in md


def test_pr_review_advisor_build_prompt() -> None:
    """Test constructing prompt with diff and findings."""
    advisor = PRReviewAdvisor()
    diff = "+ def new_func():\n+     pass\n"
    findings = [{"rule_id": "EMPTY_PASS", "line": 2, "path": "test.py"}]
    prompt = advisor._build_pr_review_prompt(
        git_diff=diff,
        sast_findings=findings,
        pr_title="feat: add new func",
        pr_body="Adds helper function",
    )
    assert "feat: add new func" in prompt
    assert "EMPTY_PASS" in prompt
    assert "def new_func()" in prompt


def test_pr_review_advisor_parse_response_json() -> None:
    """Test parsing structured JSON response."""
    advisor = PRReviewAdvisor()
    agent_output = """```json
{
  "verdict": "REQUEST_CHANGES",
  "summary": "1 Critical Security issue detected.",
  "comments": [
    {
      "category": "SECURITY",
      "file_path": "auth.py",
      "line": 15,
      "severity": "HIGH",
      "title": "Hardcoded JWT Secret",
      "comment": "Move secret to environment variable.",
      "suggested_fix": "JWT_SECRET = os.environ['JWT_SECRET']"
    }
  ]
}
```"""
    verdict, summary, comments = advisor._parse_pr_response(agent_output)
    assert verdict == "REQUEST_CHANGES"
    assert summary == "1 Critical Security issue detected."
    assert len(comments) == 1
    assert comments[0].category == "SECURITY"
    assert comments[0].suggested_fix == "JWT_SECRET = os.environ['JWT_SECRET']"


def test_pr_review_advisor_mocked_sdk() -> None:
    """Test review_pr workflow with mocked Antigravity SDK."""
    advisor = PRReviewAdvisor()

    mock_response = MagicMock()
    mock_response.text = """```json
{
  "verdict": "APPROVE",
  "summary": "Diff is clean and passes all checks.",
  "comments": []
}
```"""
    mock_usage = MagicMock()
    mock_usage.input_tokens = 400
    mock_usage.thinking_tokens = 100
    mock_usage.output_tokens = 100
    mock_usage.total_tokens = 600
    mock_response.usage = mock_usage

    mock_agent = MagicMock()
    mock_agent.chat = AsyncMock(return_value=mock_response)
    mock_agent.__aenter__ = AsyncMock(return_value=mock_agent)
    mock_agent.__aexit__ = AsyncMock(return_value=None)

    mock_module = ModuleType("google.antigravity")
    mock_module.Agent = MagicMock(return_value=mock_agent)  # type: ignore[attr-defined]
    mock_module.LocalAgentConfig = MagicMock()  # type: ignore[attr-defined]
    mock_module.CapabilitiesConfig = MagicMock()  # type: ignore[attr-defined]

    with (
        patch.dict("sys.modules", {"google.antigravity": mock_module}),
        patch.object(advisor, "is_available", return_value=True),
    ):
        result = advisor.review_pr(
            git_diff="+ print('hello')",
            sast_findings=[],
            pr_title="feat: test",
        )
        assert result.status == "success"
        assert result.verdict == "APPROVE"
        assert result.token_usage.total_tokens == 600


def test_get_git_diff() -> None:
    """Test _get_git_diff returns string from subprocess."""
    with patch("subprocess.run") as mock_run:
        mock_run.return_value = MagicMock(returncode=0, stdout="diff --git a/b")
        diff = _get_git_diff("main")
        assert diff == "diff --git a/b"


def test_load_github_event(tmp_path: Any) -> None:
    """Test loading event payload from GITHUB_EVENT_PATH."""
    event_file = tmp_path / "event.json"
    event_file.write_text(
        json.dumps({"pull_request": {"number": 42}}), encoding="utf-8"
    )

    with patch.dict("os.environ", {"GITHUB_EVENT_PATH": str(event_file)}):
        data = _load_github_event()
        assert data.get("pull_request", {}).get("number") == 42


def test_post_github_comment_mocked() -> None:
    """Test _post_github_comment making HTTP request with sticky marker."""
    mock_read = json.dumps([{"id": 123, "body": f"{BOT_MARKER}\nOld review"}]).encode(
        "utf-8"
    )
    mock_resp = MagicMock()
    mock_resp.read.return_value = mock_read
    mock_resp.status = 200
    mock_resp.__enter__ = MagicMock(return_value=mock_resp)
    mock_resp.__exit__ = MagicMock(return_value=None)

    with patch("urllib.request.urlopen", return_value=mock_resp):
        success = _post_github_comment(
            repo_full_name="owner/repo",
            pr_number=42,
            body="New review content",
            token="ghp_test123",  # noqa: S106
        )
        assert success is True


def test_run_pr_review_dry_run(tmp_path: Any) -> None:
    """Test run_pr_review pipeline execution in dry-run mode."""
    with (
        patch("scripts.pr_reviewer._get_git_diff", return_value="+ x = 1\n"),
        patch.dict("os.environ", {"GITHUB_EVENT_PATH": ""}),
    ):
        code, result = run_pr_review(target_path=str(tmp_path), dry_run=True)
        assert code in (0, 1)
        assert result.verdict in ("APPROVE", "COMMENT", "REQUEST_CHANGES")
