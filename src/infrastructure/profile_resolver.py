"""Profile Resolver Module for Multi-project SAST Guard support."""

from __future__ import annotations

import os
from pathlib import Path


class ProfileResolver:
    """Resolves active profile path: CWD .sast -> Git Root .sast -> Global profile."""

    @staticmethod
    def resolve_profile_path(cwd: str | None = None) -> Path:
        """Resolve highest priority profile.json path."""
        base_dir = Path(cwd or os.getcwd()).resolve()

        # 1. Local workspace .sast/profile.json
        local_sast = base_dir / ".sast" / "profile.json"
        if local_sast.is_file():
            return local_sast

        # 2. Check parent directories up to git root
        curr = base_dir
        while curr != curr.parent:
            git_dir = curr / ".git"
            if git_dir.exists():
                git_sast = curr / ".sast" / "profile.json"
                if git_sast.is_file():
                    return git_sast
                break
            curr = curr.parent

        # 3. Fallback to default plugin root profile.json
        plugin_root = Path(__file__).parent.parent.parent
        return plugin_root / "profile.json"
