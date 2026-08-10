"""Unit tests for GitHelper component."""

from pathlib import Path
from unittest.mock import MagicMock, patch

from src.domain.git_helper import GitHelper


def test_is_git_repo_true(tmp_path: Path) -> None:
    """Test is_git_repo when target path is inside a git work tree."""
    mock_res = MagicMock(returncode=0, stdout="true\n")
    with patch("subprocess.run", return_value=mock_res):
        assert GitHelper.is_git_repo(tmp_path) is True


def test_is_git_repo_false(tmp_path: Path) -> None:
    """Test is_git_repo when target path is not inside a git work tree."""
    mock_res = MagicMock(returncode=128, stdout="false\n")
    with patch("subprocess.run", return_value=mock_res):
        assert GitHelper.is_git_repo(tmp_path) is False


def test_is_git_repo_exception(tmp_path: Path) -> None:
    """Test is_git_repo handling OSError or ValueError."""
    with patch("subprocess.run", side_effect=OSError("Git not found")):
        assert GitHelper.is_git_repo(tmp_path) is False


def test_get_changed_files_not_git_repo(tmp_path: Path) -> None:
    """Test get_changed_files returns empty list when not in git repo."""
    with patch.object(GitHelper, "is_git_repo", return_value=False):
        assert not GitHelper.get_changed_files(tmp_path)



def test_get_changed_files_success(tmp_path: Path) -> None:
    """Test get_changed_files collecting modified files."""
    test_file = tmp_path / "modified.py"
    test_file.write_text("print('hello')", encoding="utf-8")

    mock_diff_head = MagicMock(returncode=0, stdout="modified.py\n")
    mock_diff_cached = MagicMock(returncode=0, stdout="")
    mock_ls_files = MagicMock(returncode=0, stdout="")

    with patch.object(GitHelper, "is_git_repo", return_value=True):
        with patch("subprocess.run", side_effect=[mock_diff_head, mock_diff_cached, mock_ls_files]):
            changed = GitHelper.get_changed_files(tmp_path)
            assert test_file in changed


def test_get_diff_base_not_git_repo(tmp_path: Path) -> None:
    """Test get_diff_base returns HEAD when path is not a git repo."""
    with patch.object(GitHelper, "is_git_repo", return_value=False):
        assert GitHelper.get_diff_base(tmp_path) == "HEAD"


def test_get_diff_base_symbolic_ref_success(tmp_path: Path) -> None:
    """Test get_diff_base resolves remote tracking branch via symbolic-ref."""
    mock_res = MagicMock(returncode=0, stdout="origin/main\n")
    with patch.object(GitHelper, "is_git_repo", return_value=True):
        with patch("subprocess.run", return_value=mock_res) as mock_run:
            result = GitHelper.get_diff_base(tmp_path)
            assert result == "origin/main"
            mock_run.assert_called_once()
            cmd_args = mock_run.call_args[0][0]
            assert "symbolic-ref" in cmd_args


def test_get_diff_base_fallback_branches(tmp_path: Path) -> None:
    """Test get_diff_base checks fallback branches if symbolic-ref fails."""
    mock_symbolic_fail = MagicMock(returncode=1, stdout="")
    mock_rev_parse_main_fail = MagicMock(returncode=1, stdout="")
    mock_rev_parse_master_success = MagicMock(returncode=0, stdout="abc1234\n")

    with patch.object(GitHelper, "is_git_repo", return_value=True):
        with patch(
            "subprocess.run",
            side_effect=[
                mock_symbolic_fail,
                mock_rev_parse_main_fail,
                mock_rev_parse_master_success,
            ],
        ):
            result = GitHelper.get_diff_base(tmp_path)
            assert result == "origin/master"


def test_get_diff_base_fallback_head(tmp_path: Path) -> None:
    """Test get_diff_base returns HEAD if no remote branches resolve."""
    mock_fail = MagicMock(returncode=1, stdout="")
    with patch.object(GitHelper, "is_git_repo", return_value=True):
        with patch("subprocess.run", return_value=mock_fail):
            result = GitHelper.get_diff_base(tmp_path)
            assert result == "HEAD"


def test_get_diff_base_exception_handling(tmp_path: Path) -> None:
    """Test get_diff_base handles subprocess exception gracefully."""
    with patch.object(GitHelper, "is_git_repo", return_value=True):
        with patch("subprocess.run", side_effect=OSError("Git failure")):
            result = GitHelper.get_diff_base(tmp_path)
            assert result == "HEAD"
