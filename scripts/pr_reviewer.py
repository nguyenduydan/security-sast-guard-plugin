"""GitHub Pull Request Automated Reviewer script.

Extracts PR diff, executes incremental SAST scan, orchestrates
Antigravity AI PR Review Advisor, and posts review comments to GitHub PR.
"""

from __future__ import annotations

import json
import os
import subprocess
import sys
import urllib.error
import urllib.request
from pathlib import Path
from typing import Any

from src.application.audit_service import AuditService
from src.domain.pr_review_advisor import PRReviewAdvisor, PRReviewResult

BOT_MARKER = "<!-- antigravity-pr-reviewer -->"


def _get_git_diff(base_branch: str = "main") -> str:
    """Extract git diff against base branch."""
    # Try git diff origin/{base}...HEAD first
    for diff_cmd in [
        ["git", "diff", f"origin/{base_branch}...HEAD"],
        ["git", "diff", f"{base_branch}...HEAD"],
        ["git", "diff", "HEAD~1"],
        ["git", "diff", "--staged"],
        ["git", "diff"],
    ]:
        try:
            res = subprocess.run(  # noqa: S603
                diff_cmd,
                capture_output=True,
                text=True,
                check=False,
            )
            if res.returncode == 0 and res.stdout.strip():
                return res.stdout
        except (subprocess.SubprocessError, OSError):
            continue

    return ""


def _load_github_event() -> dict[str, Any]:
    """Load GitHub Actions event payload if present."""
    event_path = os.environ.get("GITHUB_EVENT_PATH")
    if event_path and Path(event_path).exists():
        try:
            with open(event_path, encoding="utf-8") as f:
                data: dict[str, Any] = json.load(f)
                return data
        except (json.JSONDecodeError, OSError):
            return {}
    return {}


def _post_github_comment(
    repo_full_name: str,
    pr_number: int,
    body: str,
    token: str,
) -> bool:
    """Post or update sticky review comment on GitHub Pull Request."""
    headers = {
        "Authorization": f"Bearer {token}",
        "Accept": "application/vnd.github.v3+json",
        "Content-Type": "application/json",
        "User-Agent": "Security-SAST-Guard-PR-Reviewer",
    }
    comment_body = f"{BOT_MARKER}\n{body}"

    # 1. Check for existing comment to update (sticky comment)
    comments_url = (
        f"https://api.github.com/repos/{repo_full_name}/issues/{pr_number}/comments"
    )
    existing_comment_id: int | None = None

    try:
        req = urllib.request.Request(comments_url, headers=headers, method="GET")
        with urllib.request.urlopen(req, timeout=15) as resp:  # noqa: S310
            comments = json.loads(resp.read().decode("utf-8"))
            if isinstance(comments, list):
                for c in comments:
                    if isinstance(c, dict) and BOT_MARKER in c.get("body", ""):
                        existing_comment_id = c.get("id")
                        break
    except (urllib.error.URLError, json.JSONDecodeError, OSError):
        pass

    # 2. Update existing or create new comment
    if existing_comment_id:
        update_url = (
            f"https://api.github.com/repos/{repo_full_name}/issues/comments/"
            f"{existing_comment_id}"
        )
        req = urllib.request.Request(
            update_url,
            data=json.dumps({"body": comment_body}).encode("utf-8"),
            headers=headers,
            method="PATCH",
        )
    else:
        req = urllib.request.Request(
            comments_url,
            data=json.dumps({"body": comment_body}).encode("utf-8"),
            headers=headers,
            method="POST",
        )

    try:
        with urllib.request.urlopen(req, timeout=15) as resp:  # noqa: S310
            return resp.status in (200, 201)
    except urllib.error.URLError as err:
        print(f"Error posting GitHub comment: {err}", file=sys.stderr)
        return False


# pylint: disable=too-many-locals
def run_pr_review(
    target_path: str = ".",
    base_branch: str = "main",
    dry_run: bool = False,
) -> tuple[int, PRReviewResult]:
    """Execute full PR review pipeline."""
    # 1. Load PR info from environment or git
    event_data = _load_github_event()
    pr_data = event_data.get("pull_request", {})
    pr_title = str(pr_data.get("title", os.environ.get("PR_TITLE", "")))
    pr_body = str(pr_data.get("body", os.environ.get("PR_BODY", "")))
    pr_number = pr_data.get("number") or os.environ.get("PR_NUMBER")
    repo_name = event_data.get("repository", {}).get("full_name") or os.environ.get(
        "GITHUB_REPOSITORY"
    )
    token = os.environ.get("GITHUB_TOKEN") or os.environ.get("GH_TOKEN")

    if pr_data.get("base", {}).get("ref"):
        base_branch = str(pr_data["base"]["ref"])

    # 2. Extract Git Diff
    git_diff = _get_git_diff(base_branch=base_branch)

    # 3. Run Incremental SAST Scan on PR diff
    audit_service = AuditService()
    findings, _, _ = audit_service.run_audit(
        target_path=target_path,
        incremental=True,
        generate_report=False,
    )

    # 4. Run Antigravity PR Review Advisor
    advisor = PRReviewAdvisor()
    review_result = advisor.review_pr(
        git_diff=git_diff,
        sast_findings=findings,
        pr_title=pr_title,
        pr_body=pr_body,
    )

    # 5. Output to reports directory
    reports_dir = Path("reports")
    reports_dir.mkdir(exist_ok=True)
    report_file = reports_dir / "pr_review_report.md"
    markdown_output = review_result.to_markdown()
    report_file.write_text(markdown_output, encoding="utf-8")

    print(markdown_output)
    print(f"\nReview report written to: {report_file}")

    # 6. Post to GitHub if configured
    if not dry_run and token and repo_name and pr_number:
        try:
            num_val = int(pr_number)
            posted = _post_github_comment(
                repo_full_name=repo_name,
                pr_number=num_val,
                body=markdown_output,
                token=token,
            )
            if posted:
                print(f"Successfully posted review comment to PR #{num_val}!")
            else:
                print("Failed to post review comment to GitHub PR.", file=sys.stderr)
        except ValueError:
            pass

    # Exit code: 1 if REQUEST_CHANGES, 0 otherwise
    exit_code = 1 if review_result.verdict == "REQUEST_CHANGES" else 0
    return exit_code, review_result


def main() -> int:
    """CLI entrypoint for PR reviewer."""
    dry_run = "--dry-run" in sys.argv
    exit_code, _ = run_pr_review(dry_run=dry_run)
    return exit_code


if __name__ == "__main__":
    sys.exit(main())
