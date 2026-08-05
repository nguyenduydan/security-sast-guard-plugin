"""SAST ignore filter with zero-config defaults and custom .sastignore support."""

import fnmatch
from pathlib import Path

DEFAULT_IGNORE_DIRS: set[str] = {
    ".git",
    ".hg",
    ".svn",
    "node_modules",
    "vendor",
    ".venv",
    "venv",
    "env",
    "__pycache__",
    ".pytest_cache",
    ".mypy_cache",
    ".ruff_cache",
    ".idea",
    ".vscode",
    "dist",
    "build",
    "out",
    "target",
    ".next",
    ".nuxt",
}

DEFAULT_IGNORE_EXTS: set[str] = {
    ".png",
    ".jpg",
    ".jpeg",
    ".gif",
    ".ico",
    ".svg",
    ".pdf",
    ".zip",
    ".tar",
    ".gz",
    ".7z",
    ".rar",
    ".exe",
    ".dll",
    ".so",
    ".dylib",
    ".woff",
    ".woff2",
    ".ttf",
    ".eot",
    ".mp3",
    ".mp4",
    ".pyc",
    ".pyo",
    ".db",
    ".sqlite",
}

DEFAULT_IGNORE_FILES: set[str] = {
    "package-lock.json",
    "yarn.lock",
    "pnpm-lock.yaml",
    "Cargo.lock",
    "poetry.lock",
}


class IgnoreFilter:
    """Filters paths based on built-in defaults and custom .sastignore file."""

    def __init__(self, root_dir: str | Path | None = None) -> None:
        self.custom_patterns: list[str] = []
        if root_dir:
            self._load_custom_sastignore(Path(root_dir))

    def _load_custom_sastignore(self, root_dir: Path) -> None:
        self.root_dir = root_dir.resolve()
        ignore_file = self.root_dir / ".sastignore"
        if not ignore_file.exists() or not ignore_file.is_file():
            return

        try:
            with open(ignore_file, encoding="utf-8", errors="replace") as f:
                for line in f:
                    stripped = line.strip()
                    if stripped and not stripped.startswith("#"):
                        self.custom_patterns.append(stripped.rstrip("/"))
        except OSError:
            pass

    def should_ignore(self, path: Path | str) -> bool:
        """Check if path should be ignored by built-in defaults or custom patterns."""
        p = Path(path)
        parts = p.parts

        # Check default ignored directory names anywhere in path
        for part in parts:
            if part in DEFAULT_IGNORE_DIRS:
                return True

        # Check extension
        if p.suffix.lower() in DEFAULT_IGNORE_EXTS:
            return True

        # Check exact filename
        if p.name in DEFAULT_IGNORE_FILES:
            return True

        # Check custom fnmatch patterns from .sastignore
        str_path = str(p).replace("\\", "/")
        file_name = p.name
        for pattern in self.custom_patterns:
            clean_pattern = pattern.replace("\\", "/")
            if fnmatch.fnmatch(str_path, clean_pattern) or fnmatch.fnmatch(
                file_name, clean_pattern
            ):
                return True
            for part in parts:
                if fnmatch.fnmatch(part, clean_pattern):
                    return True

        return False

    def should_ignore_dir(self, dir_name: str) -> bool:
        """Check if a directory name should be pruned during top-down tree traversal."""
        if dir_name in DEFAULT_IGNORE_DIRS:
            return True
        for pattern in self.custom_patterns:
            clean_pattern = pattern.replace("\\", "/")
            if fnmatch.fnmatch(dir_name, clean_pattern):
                return True
        return False
