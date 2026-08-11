"""Tests for IgnoreFilter and zero-config SAST scan metadata."""

from pathlib import Path

from src.domain.ignore_filter import IgnoreFilter
from src.domain.sast_scanner import SASTScanner


def test_ignore_filter_default_dirs(tmp_path: Path) -> None:
    filter_inst = IgnoreFilter(root_dir=tmp_path)
    node_path = tmp_path / "node_modules" / "express" / "index.js"
    venv_path = tmp_path / ".venv" / "lib" / "site-packages" / "foo.py"
    git_path = tmp_path / ".git" / "config"
    src_path = tmp_path / "src" / "index.ts"

    assert filter_inst.should_ignore(node_path) is True
    assert filter_inst.should_ignore(venv_path) is True
    assert filter_inst.should_ignore(git_path) is True
    assert filter_inst.should_ignore(src_path) is False


def test_ignore_filter_default_extensions(tmp_path: Path) -> None:
    filter_inst = IgnoreFilter(root_dir=tmp_path)
    assert filter_inst.should_ignore(tmp_path / "assets" / "logo.png") is True
    assert filter_inst.should_ignore(tmp_path / "docs" / "manual.pdf") is True
    assert filter_inst.should_ignore(tmp_path / "build" / "app.exe") is True
    assert filter_inst.should_ignore(tmp_path / "main.py") is False


def test_ignore_filter_custom_sastignore(tmp_path: Path) -> None:
    sastignore = tmp_path / ".sastignore"
    sastignore.write_text("*.tmp\nsecret_folder/\n", encoding="utf-8")

    filter_inst = IgnoreFilter(root_dir=tmp_path)
    assert filter_inst.should_ignore(tmp_path / "test.tmp") is True
    assert filter_inst.should_ignore(tmp_path / "secret_folder" / "data.py") is True
    assert filter_inst.should_ignore(tmp_path / "normal.py") is False


def test_scanner_with_metadata_and_recursive_directory(tmp_path: Path) -> None:
    # Create test directory structure
    src_dir = tmp_path / "src"
    src_dir.mkdir()
    (src_dir / "app.py").write_text("print('hello world')\n", encoding="utf-8")

    ignored_dir = tmp_path / "node_modules"
    ignored_dir.mkdir()
    (ignored_dir / "lib.js").write_text("console.log('ignored')\n", encoding="utf-8")

    scanner = SASTScanner()
    res = scanner.scan_with_metadata(str(tmp_path))

    assert "findings" in res
    assert "metadata" in res
    meta = res["metadata"]
    assert meta["scanned_files"] == 1
    assert meta["ignored_files"] == 1
    assert meta["total_lines"] == 1
    assert meta["duration_seconds"] >= 0


def test_ignore_filter_doc_extensions(tmp_path: Path) -> None:
    """Documentation and plain-text files must be ignored to prevent false positives."""
    filter_inst = IgnoreFilter(root_dir=tmp_path)

    assert filter_inst.should_ignore(tmp_path / "README.md") is True
    assert filter_inst.should_ignore(tmp_path / "CHANGELOG.md") is True
    assert filter_inst.should_ignore(tmp_path / "guide.markdown") is True
    assert filter_inst.should_ignore(tmp_path / "spec.rst") is True
    assert filter_inst.should_ignore(tmp_path / "notes" / "todo.txt") is True
    assert filter_inst.should_ignore(tmp_path / "logs" / "server.log") is True
    assert filter_inst.should_ignore(tmp_path / "dist" / "bundle.map") is True
    # Python source must NOT be ignored
    assert filter_inst.should_ignore(tmp_path / "src" / "app.py") is False


def test_ignore_filter_system_dirs(tmp_path: Path) -> None:
    """Internal plugin/tool directories must be ignored to prevent false positives."""
    filter_inst = IgnoreFilter(root_dir=tmp_path)

    assert filter_inst.should_ignore(tmp_path / "reports" / "sast_audit.md") is True
    assert filter_inst.should_ignore(tmp_path / ".aiops" / "decisions.jsonl") is True
    assert filter_inst.should_ignore(tmp_path / ".sast" / "profile.json") is True
    assert filter_inst.should_ignore(tmp_path / ".superpowers" / "config.yaml") is True
    github_ci = tmp_path / ".github" / "workflows" / "ci.yml"
    assert filter_inst.should_ignore(github_ci) is True
    skills_md = tmp_path / "skills" / "sast-audit" / "SKILL.md"
    assert filter_inst.should_ignore(skills_md) is True
    assert filter_inst.should_ignore(tmp_path / "coverage" / "report.html") is True
    # Source code must NOT be ignored
    assert filter_inst.should_ignore(tmp_path / "src" / "engine.py") is False


def test_ignore_filter_should_ignore_dir_new_entries(tmp_path: Path) -> None:
    """should_ignore_dir must prune new system directories during tree traversal."""
    filter_inst = IgnoreFilter(root_dir=tmp_path)

    assert filter_inst.should_ignore_dir("reports") is True
    assert filter_inst.should_ignore_dir("docs") is True
    assert filter_inst.should_ignore_dir(".aiops") is True
    assert filter_inst.should_ignore_dir(".sast") is True
    assert filter_inst.should_ignore_dir(".superpowers") is True
    assert filter_inst.should_ignore_dir(".github") is True
    assert filter_inst.should_ignore_dir("coverage") is True
    assert filter_inst.should_ignore_dir("skills") is True
    assert filter_inst.should_ignore_dir("templates") is True
    assert filter_inst.should_ignore_dir("tests") is True
    assert filter_inst.should_ignore_dir("bin") is True
    assert filter_inst.should_ignore_dir("obj") is True
    assert filter_inst.should_ignore_dir("packages") is True
    assert filter_inst.should_ignore_dir(".vs") is True
    assert filter_inst.should_ignore_dir("src") is False


def test_ignore_filter_aspnet_rules(tmp_path: Path) -> None:
    """ASP.NET build outputs, cache directories, symbols, and databases must be ignored."""
    filter_inst = IgnoreFilter(root_dir=tmp_path)

    # Directories
    assert filter_inst.should_ignore(tmp_path / "bin" / "Debug" / "app.dll") is True
    assert (
        filter_inst.should_ignore(
            tmp_path
            / "obj"
            / "Release"
            / "app.csproj.assemblyInputs.cache"
        )
        is True
    )
    assert filter_inst.should_ignore(tmp_path / "packages" / "Newtonsoft.Json" / "lib.dll") is True
    assert filter_inst.should_ignore(tmp_path / ".vs" / "solution" / "v17" / ".suo") is True
    assert filter_inst.should_ignore(tmp_path / "publish" / "web.config") is True
    assert filter_inst.should_ignore(tmp_path / "App_Data" / "aspnet.mdf") is True
    assert filter_inst.should_ignore(tmp_path / "TestResults" / "test.trx") is True

    # File extensions
    assert filter_inst.should_ignore(tmp_path / "app.pdb") is True
    assert filter_inst.should_ignore(tmp_path / "package.nupkg") is True
    assert filter_inst.should_ignore(tmp_path / "app.suo") is True
    assert filter_inst.should_ignore(tmp_path / "app.user") is True
    assert filter_inst.should_ignore(tmp_path / "data.mdf") is True
    assert filter_inst.should_ignore(tmp_path / "data_log.ldf") is True

    # Lock files
    assert filter_inst.should_ignore(tmp_path / "packages.lock.json") is True

    # ASP.NET C# source code must NOT be ignored
    assert filter_inst.should_ignore(tmp_path / "Controllers" / "HomeController.cs") is False
    assert filter_inst.should_ignore(tmp_path / "Program.cs") is False


def test_ignore_filter_templates_and_logs(tmp_path: Path) -> None:
    """Template files and log directories/files must be ignored."""
    filter_inst = IgnoreFilter(root_dir=tmp_path)

    # Log directories and extensions
    assert filter_inst.should_ignore(tmp_path / "logs" / "app.log") is True
    assert filter_inst.should_ignore(tmp_path / "log" / "server.out") is True
    assert filter_inst.should_ignore(tmp_path / "app.err") is True
    assert filter_inst.should_ignore(tmp_path / "app.bak") is True

    # Template extensions
    assert filter_inst.should_ignore(tmp_path / "page.template") is True
    assert filter_inst.should_ignore(tmp_path / "layout.tpl") is True
    assert filter_inst.should_ignore(tmp_path / "card.tmpl") is True
    assert filter_inst.should_ignore(tmp_path / "email.mustache") is True
    assert filter_inst.should_ignore(tmp_path / "view.handlebars") is True
    assert filter_inst.should_ignore(tmp_path / "item.hbs") is True


def test_ignore_filter_temp_and_libraries(tmp_path: Path) -> None:
    """Temp directories, library caches, and swap files must be ignored."""
    filter_inst = IgnoreFilter(root_dir=tmp_path)

    # Temp and Cache directories
    assert filter_inst.should_ignore(tmp_path / "temp" / "file.txt") is True
    assert filter_inst.should_ignore(tmp_path / "tmp" / "file.txt") is True
    assert filter_inst.should_ignore(tmp_path / ".tmp" / "file.txt") is True
    assert filter_inst.should_ignore(tmp_path / "cache" / "data.bin") is True
    assert filter_inst.should_ignore(tmp_path / ".cache" / "build.json") is True

    # Library directories across ecosystems
    assert filter_inst.should_ignore(tmp_path / "bower_components" / "jquery.js") is True
    assert filter_inst.should_ignore(tmp_path / "jspm_packages" / "npm" / "lib.js") is True
    assert filter_inst.should_ignore(tmp_path / ".nuget" / "packages.config") is True
    assert filter_inst.should_ignore(tmp_path / ".gradle" / "caches" / "test.jar") is True
    assert filter_inst.should_ignore(tmp_path / ".m2" / "repository" / "lib.jar") is True
    assert filter_inst.should_ignore(tmp_path / ".cargo" / "registry" / "lib.rlib") is True
    assert filter_inst.should_ignore(tmp_path / ".bundle" / "gems" / "ruby.rb") is True

    # Temp extensions
    assert filter_inst.should_ignore(tmp_path / "cache.tmp") is True
    assert filter_inst.should_ignore(tmp_path / "scratch.temp") is True
    assert filter_inst.should_ignore(tmp_path / ".main.py.swp") is True
    assert filter_inst.should_ignore(tmp_path / ".main.py.swo") is True
    assert filter_inst.should_ignore(tmp_path / ".DS_Store") is True
