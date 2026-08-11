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
    def get_changed_files(path: Path | str) -> list[Path]:
        """Get list of modified, staged, or untracked files in git repository."""
        p = Path(path).resolve()
        target_dir = p if p.is_dir() else p.parent
        if not GitHelper.is_git_repo(target_dir):
            return []

        changed_files: set[Path] = set()

        # 1. Get modified & staged files via git diff
        for cmd in [
            ["git", "diff", "--name-only", "HEAD"],
            ["git", "diff", "--name-only", "--cached"],
            ["git", "ls-files", "--others", "--exclude-standard"],
        ]:
            try:
                res = subprocess.run(  # noqa: S603
                    cmd,
                    cwd=str(target_dir),
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
                    full_path = (target_dir / rel_path).resolve()
                    if full_path.is_file():
                        changed_files.add(full_path)
            except (OSError, ValueError):
                continue

        return list(changed_files)

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
