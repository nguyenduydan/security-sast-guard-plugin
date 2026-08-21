"""Git helper component for incremental SAST scans."""

import subprocess
from pathlib import Path


class GitHelper:
    """Helper for detecting git repository status and modified files."""

    @staticmethod
    def is_git_repo(path: Path | str) -> bool:
        """Check if path is inside a git working tree."""
        p = Path(path)
        target_dir = p if p.is_dir() else p.parent
        try:
            res = subprocess.run(
                ["git", "rev-parse", "--is-inside-work-tree"],  # noqa: S607
                cwd=str(target_dir),
                capture_output=True,
                text=True,
                check=False,
            )
            return res.returncode == 0 and "true" in res.stdout.strip().lower()
        except (OSError, ValueError):
            return False

    @staticmethod
    def get_repo_root(path: Path | str) -> Path | None:
        """Get repository root directory Path."""
        p = Path(path).resolve()
        target_dir = p if p.is_dir() else p.parent
        try:
            res = subprocess.run(
                ["git", "rev-parse", "--show-toplevel"],  # noqa: S607
                cwd=str(target_dir),
                capture_output=True,
                text=True,
                check=False,
            )
            if res.returncode == 0 and res.stdout.strip():
                return Path(res.stdout.strip()).resolve()
            return None
        except (OSError, ValueError):
            return None

    @staticmethod
    def _is_file_in_target(target: Path, candidate: Path) -> bool:
        """Check if candidate file matches or resides inside target path."""
        if not candidate.is_file():
            return False
        if target.is_file():
            return candidate == target
        if target.is_dir():
            return candidate == target or target in candidate.parents
        return True

    @staticmethod
    def get_changed_files(path: Path | str, base_ref: str | None = None) -> list[Path]:
        """Get list of modified, staged, or untracked files in git repository."""
        p = Path(path).resolve()
        target_dir = p if p.is_dir() else p.parent
        if not GitHelper.is_git_repo(target_dir):
            return []

        repo_root = GitHelper.get_repo_root(target_dir) or target_dir
        diff_base = base_ref or GitHelper.get_diff_base(target_dir)

        changed_files: set[Path] = set()

        diff_commands = [
            ["git", "diff", "--name-only", diff_base],
            ["git", "diff", "--name-only", "HEAD"],
            ["git", "diff", "--name-only", "--cached"],
            ["git", "ls-files", "--others", "--exclude-standard"],
        ]

        for cmd in diff_commands:
            try:
                res = subprocess.run(  # noqa: S603
                    cmd,
                    cwd=str(repo_root),
                    capture_output=True,
                    text=True,
                    check=False,
                )
                if res.returncode != 0:
                    continue
                for line in res.stdout.splitlines():
                    rel_path = line.strip()
                    if not rel_path:
                        continue
                    full_path = (repo_root / rel_path).resolve()
                    if GitHelper._is_file_in_target(p, full_path):
                        changed_files.add(full_path)
            except (OSError, ValueError):
                continue

        return sorted(changed_files, key=str)

    @staticmethod
    def get_diff_base(path: Path | str) -> str:
        """Determine base reference for diff comparison (remote branch or HEAD)."""
        p = Path(path)
        target_dir = p if p.is_dir() else p.parent
        if not GitHelper.is_git_repo(target_dir):
            return "HEAD"

        # 1. Resolve remote tracking branch via refs/remotes/origin/HEAD
        try:
            cmd_sym = ["git", "symbolic-ref", "--short", "refs/remotes/origin/HEAD"]
            res = subprocess.run(  # noqa: S603
                cmd_sym,
                cwd=str(target_dir),
                capture_output=True,
                text=True,
                check=False,
            )
            if res.returncode == 0 and res.stdout.strip():
                return res.stdout.strip()
        except (OSError, ValueError):
            pass  # git not available: fall through to branch fallbacks

        # 2. Fallback check for common default remote branches
        for branch in ["origin/main", "origin/master", "origin/develop"]:
            try:
                cmd_rev = ["git", "rev-parse", "--verify", "--quiet", branch]
                res = subprocess.run(  # noqa: S603
                    cmd_rev,
                    cwd=str(target_dir),
                    capture_output=True,
                    text=True,
                    check=False,
                )
                if res.returncode == 0 and res.stdout.strip():
                    return branch
            except (OSError, ValueError):
                continue

        # 3. Default fallback to HEAD
        return "HEAD"
