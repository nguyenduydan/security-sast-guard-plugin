"""SAST ignore filter with zero-config defaults and custom .sastignore support."""

import fnmatch
import json
from pathlib import Path

DEFAULT_IGNORE_DIRS: set[str] = {
    # VCS
    ".git",
    ".hg",
    ".svn",
    # Dependencies / Libraries (cross-ecosystem)
    "node_modules",
    "vendor",
    "bower_components",  # Frontend legacy package manager
    "jspm_packages",  # JS package manager
    ".venv",
    "venv",
    "env",
    ".env",
    "packages",  # NuGet legacy packages directory
    "OtherDLL",  # Legacy external compiled DLLs directory
    "OtherDll",
    "otherdll",
    ".nuget",  # NuGet cache directory
    ".gradle",  # Gradle cache directory
    ".m2",  # Maven local repository cache
    ".cargo",  # Rust cargo cache
    ".bundle",  # Ruby bundler cache
    # Temp / Cache / build artefacts & .NET / ASP.NET build output
    ".tmp",  # Hidden temp directory
    ".temp",  # Hidden temp directory
    "cache",  # General cache directory
    ".cache",  # Hidden system/build cache directory
    "__pycache__",
    ".pytest_cache",
    ".mypy_cache",
    ".ruff_cache",
    "dist",
    "build",
    "out",
    "target",
    "bin",  # ASP.NET / .NET compiled binaries
    "obj",  # ASP.NET / .NET intermediate build output
    "publish",  # ASP.NET publish output directory
    "App_Data",  # ASP.NET local data / mdf files directory
    "Uploads",  # User uploaded files directory
    "Upload",
    "uploads",
    "upload",
    "Images",  # Static image assets directory
    "images",
    "Template",  # HTML / email / doc templates directory
    "template",
    "plugins",  # Frontend / 3rd party plugins directory
    "TestResults",  # .NET / MSTest test execution results
    ".next",
    ".nuxt",
    "coverage",
    "site",
    # IDE / VS
    ".idea",
    ".vscode",
    ".vs",  # Visual Studio local cache directory
    # Logs & telemetry
    "logs",
    "log",
    "Log",
    "reports",
    "docs",
    ".aiops",
    ".sast",
    ".superpowers",
    ".system_generated",
    ".github",
    ".gemini",
    ".agents",
    "skills",
    "templates",
    "tests",
    "rules",
}

DEFAULT_IGNORE_EXTS: set[str] = {
    # Images / media
    ".png",
    ".jpg",
    ".jpeg",
    ".gif",
    ".ico",
    ".svg",
    ".mp3",
    ".mp4",
    # Fonts
    ".woff",
    ".woff2",
    ".ttf",
    ".eot",
    # Archives / binaries & .NET assemblies / symbols
    ".pdf",
    ".zip",
    ".tar",
    ".gz",
    ".7z",
    ".rar",
    ".exe",
    ".dll",
    ".pdb",  # .NET debug symbols
    ".nupkg",  # NuGet package file
    ".snupkg",  # NuGet symbol package
    ".so",
    ".dylib",
    # Compiled / generated / Visual Studio user options
    ".pyc",
    ".pyo",
    ".map",
    ".suo",  # Visual Studio Solution User Options
    ".user",  # Visual Studio project user settings
    ".userossc",
    ".sln.docstates",
    ".csproj",  # Visual Studio C# Project File
    # XML Schema / static configs
    ".xsd",
    # Databases & ASP.NET data files
    ".db",
    ".sqlite",
    ".mdf",  # SQL Server Express database file
    ".ldf",  # SQL Server Express log file
    # Templates & Static HTML files (scaffold / static error pages)
    ".template",
    ".tpl",
    ".tmpl",
    ".mustache",
    ".handlebars",
    ".hbs",
    ".htm",
    ".html",
    # Documentation, plain text, temp, and log files
    ".md",
    ".markdown",
    ".rst",
    ".txt",
    ".log",
    ".out",
    ".err",
    ".bak",
    ".tmp",
    ".temp",
    ".swp",
    ".swo",
    ".ds_store",
}

DEFAULT_IGNORE_FILES: set[str] = {
    ".ds_store",
    "package-lock.json",
    "yarn.lock",
    "pnpm-lock.yaml",
    "Cargo.lock",
    "poetry.lock",
    "packages.lock.json",  # NuGet package lock file
    # ASP.NET / .NET environment config transformation files & static configs
    "web.config",
    "web.debug.config",
    "web.release.config",
    "app.config",
    "nlog.config",
    "applicationinsights.config",
    "loader.js",
    # Rule definitions and security profiles (meta-rules)
    "sast_rules.json",
    "profiles.json",
    "profile.json",
    "blacklist.json",
}


class IgnoreFilter:
    """Filters paths based on built-in defaults, .sastignore, and blacklist.json."""

    def __init__(self, root_dir: str | Path | None = None) -> None:
        self.custom_patterns: list[str] = []
        self.root_dir: Path | None = Path(root_dir).resolve() if root_dir else None
        if self.root_dir:
            self._load_custom_sastignore(self.root_dir)
            self._load_custom_blacklist_json(self.root_dir)

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
            pass  # Custom ignore file absent or unreadable: use defaults only

    @staticmethod
    def _parse_json_patterns(content: object) -> list[str]:
        """Extract string pattern list from parsed JSON array or object."""
        patterns: list[str] = []
        if isinstance(content, list):
            for item in content:
                if isinstance(item, str) and item.strip():
                    patterns.append(item.strip().rstrip("/"))
            return patterns

        if isinstance(content, dict):
            keys = ("blacklist", "ignore", "patterns", "dirs", "files", "paths")
            for key in keys:
                val = content.get(key)
                if isinstance(val, list):
                    for item in val:
                        if isinstance(item, str) and item.strip():
                            patterns.append(item.strip().rstrip("/"))
        return patterns

    def _load_custom_blacklist_json(self, root_dir: Path) -> None:
        """Load exclusion patterns from .sast/blacklist.json or blacklist.json."""
        target_files = [
            root_dir / ".sast" / "blacklist.json",
            root_dir / "blacklist.json",
        ]
        for b_file in target_files:
            if not b_file.is_file():
                continue
            try:
                content = json.loads(b_file.read_text(encoding="utf-8"))
                for pat in self._parse_json_patterns(content):
                    if pat not in self.custom_patterns:
                        self.custom_patterns.append(pat)
            except (json.JSONDecodeError, OSError):
                pass

    @staticmethod
    def _matches_default_rules(p: Path) -> bool:
        """Check if file matches default ignored extensions or filenames."""
        name_lower = p.name.lower()
        if p.suffix.lower() in DEFAULT_IGNORE_EXTS:
            return True
        if name_lower in DEFAULT_IGNORE_FILES:
            return True
        return (
            name_lower.endswith(".designer.cs")
            or name_lower.endswith(".min.js")
            or name_lower.endswith(".bundle.js")
        )

    def _matches_custom_pattern(
        self,
        clean_pat: str,
        str_path: str,
        file_name: str,
        rel_str: str | None,
        parts: tuple[str, ...],
    ) -> bool:
        """Check if path matches a specific custom ignore pattern."""
        if fnmatch.fnmatch(str_path, clean_pat) or fnmatch.fnmatch(
            file_name, clean_pat
        ):
            return True
        if rel_str is not None and (
            fnmatch.fnmatch(rel_str, clean_pat)
            or fnmatch.fnmatch(rel_str, f"{clean_pat}/*")
        ):
            return True
        return any(fnmatch.fnmatch(part, clean_pat) for part in parts)

    def should_ignore(self, path: Path | str) -> bool:
        """Check if path should be ignored by built-in defaults or custom patterns."""
        p = Path(path)
        parts = p.parts
        rel_str: str | None = None
        if self.root_dir:
            try:
                rel_p = p.resolve().relative_to(self.root_dir)
                dir_parts = rel_p.parts[:-1]
                rel_str = str(rel_p).replace("\\", "/")
            except ValueError:
                dir_parts = p.parts[:-1]
        else:
            dir_parts = p.parts[:-1]

        # Check default ignored directory names anywhere in relative directory path
        for part in dir_parts:
            if part in DEFAULT_IGNORE_DIRS:
                return True

        if self._matches_default_rules(p):
            return True

        # Check custom fnmatch patterns from .sastignore and blacklist.json
        str_path = str(p).replace("\\", "/")
        file_name = p.name
        for pattern in self.custom_patterns:
            clean_pattern = pattern.replace("\\", "/")
            if self._matches_custom_pattern(
                clean_pattern, str_path, file_name, rel_str, parts
            ):
                return True

        return False

    def should_ignore_dir(self, dir_name: str) -> bool:
        """Check if a directory name should be pruned during top-down tree traversal."""
        if dir_name in DEFAULT_IGNORE_DIRS:
            return True
        for pattern in self.custom_patterns:
            clean_pattern = pattern.replace("\\", "/")
            if fnmatch.fnmatch(dir_name, clean_pattern) or fnmatch.fnmatch(
                f"{dir_name}/*", clean_pattern
            ):
                return True
        return False
