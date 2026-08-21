"""Unit tests for GitHookInstaller."""

from src.infrastructure.git_hook_installer import GitHookInstaller


def test_git_hook_installer_success(tmp_path) -> None:
    """Verify GitHookInstaller correctly installs and uninstalls pre-commit hooks."""
    git_dir = tmp_path / ".git"
    git_dir.mkdir()

    installer = GitHookInstaller(repo_dir=str(tmp_path))

    # Test install
    install_res = installer.install()
    assert install_res["status"] == "success"

    hook_shell = git_dir / "hooks" / "pre-commit"
    hook_cmd = git_dir / "hooks" / "pre-commit.cmd"
    assert hook_shell.exists()
    assert hook_cmd.exists()
    assert "control_plane.py" in hook_shell.read_text(encoding="utf-8")
    assert "control_plane.py" in hook_cmd.read_text(encoding="utf-8")

    # Test uninstall
    uninstall_res = installer.uninstall()
    assert uninstall_res["status"] == "success"
    assert not hook_shell.exists()
    assert not hook_cmd.exists()


def test_git_hook_installer_not_a_git_repo(tmp_path) -> None:
    """Verify GitHookInstaller fails gracefully when not a git repository."""
    installer = GitHookInstaller(repo_dir=str(tmp_path))
    res = installer.install()
    assert res["status"] == "error"
    assert "Not a git repository" in res["message"]
