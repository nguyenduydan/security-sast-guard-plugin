"""SAST ignore filter with zero-config defaults and custom .sastignore support."""

import fnmatch
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
            pass  # Custom ignore file absent or unreadable: use defaults only

    def should_ignore(self, path: Path | str) -> bool:
        """Check if path should be ignored by built-in defaults or custom patterns."""
        p = Path(path)
        parts = p.parts

        # Check default ignored directory names anywhere in path
        for part in parts:
            if part in DEFAULT_IGNORE_DIRS:
                return True

        # Check extension, exact filename, minified JS,
        # or .designer.cs auto-generated files
        name_lower = p.name.lower()
        if (
            p.suffix.lower() in DEFAULT_IGNORE_EXTS
            or name_lower in DEFAULT_IGNORE_FILES
            or name_lower.endswith(".designer.cs")
            or name_lower.endswith(".min.js")
            or name_lower.endswith(".bundle.js")
        ):
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
