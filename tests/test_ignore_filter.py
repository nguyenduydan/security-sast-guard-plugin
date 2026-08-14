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

    gemini_path = tmp_path / ".gemini" / "rules.json"
    agent_path = tmp_path / ".agents" / "task.py"

    assert filter_inst.should_ignore(node_path) is True
    assert filter_inst.should_ignore(venv_path) is True
    assert filter_inst.should_ignore(git_path) is True
    assert filter_inst.should_ignore(gemini_path) is True
    assert filter_inst.should_ignore(agent_path) is True
    assert filter_inst.should_ignore(src_path) is False


def test_ignore_filter_default_extensions(tmp_path: Path) -> None:
    filter_inst = IgnoreFilter(root_dir=tmp_path)
    assert filter_inst.should_ignore(tmp_path / "assets" / "logo.png") is True
    assert filter_inst.should_ignore(tmp_path / "docs" / "manual.pdf") is True
    assert filter_inst.should_ignore(tmp_path / "build" / "app.exe") is True
    assert filter_inst.should_ignore(tmp_path / "assets" / "loader.js") is True
    assert filter_inst.should_ignore(tmp_path / "dist" / "app.min.js") is True
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
    assert filter_inst.should_ignore_dir("plugins") is True
    assert filter_inst.should_ignore_dir("src") is False


def test_ignore_filter_aspnet_rules(tmp_path: Path) -> None:
    """ASP.NET build outputs, symbols, and databases must be ignored."""
    filter_inst = IgnoreFilter(root_dir=tmp_path)

    # Directories
    bin_dll = tmp_path / "bin" / "Debug" / "app.dll"
    assert filter_inst.should_ignore(bin_dll) is True

    obj_cache = tmp_path / "obj" / "Release" / "app.csproj.assemblyInputs.cache"
    assert filter_inst.should_ignore(obj_cache) is True

    pkg_dll = tmp_path / "packages" / "Newtonsoft.Json" / "lib.dll"
    assert filter_inst.should_ignore(pkg_dll) is True

    vs_suo = tmp_path / ".vs" / "solution" / "v17" / ".suo"
    assert filter_inst.should_ignore(vs_suo) is True

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
    assert filter_inst.should_ignore(tmp_path / "project.csproj") is True

    # Lock and Config files
    assert filter_inst.should_ignore(tmp_path / "packages.lock.json") is True
    assert filter_inst.should_ignore(tmp_path / "Web.config") is True
    assert filter_inst.should_ignore(tmp_path / "Web.Debug.config") is True
    assert filter_inst.should_ignore(tmp_path / "Web.Release.config") is True
    assert filter_inst.should_ignore(tmp_path / "App.config") is True

    # ASP.NET C# source code must NOT be ignored
    ctrl_cs = tmp_path / "Controllers" / "HomeController.cs"
    assert filter_inst.should_ignore(ctrl_cs) is False
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
    assert filter_inst.should_ignore(tmp_path / ".temp" / "file.txt") is True
    assert filter_inst.should_ignore(tmp_path / ".tmp" / "file.txt") is True
    assert filter_inst.should_ignore(tmp_path / "cache" / "data.bin") is True
    assert filter_inst.should_ignore(tmp_path / ".cache" / "build.json") is True

    # Library directories across ecosystems
    bower_file = tmp_path / "bower_components" / "jquery.js"
    assert filter_inst.should_ignore(bower_file) is True

    jspm_file = tmp_path / "jspm_packages" / "npm" / "lib.js"
    assert filter_inst.should_ignore(jspm_file) is True

    assert filter_inst.should_ignore(tmp_path / ".nuget" / "packages.config") is True

    gradle_file = tmp_path / ".gradle" / "caches" / "test.jar"
    assert filter_inst.should_ignore(gradle_file) is True

    m2_file = tmp_path / ".m2" / "repository" / "lib.jar"
    assert filter_inst.should_ignore(m2_file) is True

    cargo_file = tmp_path / ".cargo" / "registry" / "lib.rlib"
    assert filter_inst.should_ignore(cargo_file) is True

    bundle_file = tmp_path / ".bundle" / "gems" / "ruby.rb"
    assert filter_inst.should_ignore(bundle_file) is True

    # Temp extensions
    assert filter_inst.should_ignore(tmp_path / "cache.tmp") is True
    assert filter_inst.should_ignore(tmp_path / "scratch.temp") is True
    assert filter_inst.should_ignore(tmp_path / ".main.py.swp") is True
    assert filter_inst.should_ignore(tmp_path / ".main.py.swo") is True
    assert filter_inst.should_ignore(tmp_path / ".DS_Store") is True


def test_ignore_filter_aspnet_extended_rules(tmp_path: Path) -> None:
    """OtherDLL, Uploads, Template, .designer.cs and static configs must be ignored."""
    filter_inst = IgnoreFilter(root_dir=tmp_path)

    # Directories
    assert filter_inst.should_ignore(tmp_path / "OtherDLL" / "lib.dll") is True
    assert filter_inst.should_ignore(tmp_path / "Uploads" / "doc.pdf") is True
    assert filter_inst.should_ignore(tmp_path / "Template" / "mail.htm") is True
    assert filter_inst.should_ignore(tmp_path / "Log" / "trace.log") is True

    # Auto-generated designer files
    designer_file = tmp_path / "WebMethod.aspx.designer.cs"
    assert filter_inst.should_ignore(designer_file) is True

    # Static HTML & Schema configs
    assert filter_inst.should_ignore(tmp_path / "_index.htm") is True
    assert filter_inst.should_ignore(tmp_path / "auth-error.html") is True
    assert filter_inst.should_ignore(tmp_path / "NLog.xsd") is True

    # Static config files
    assert filter_inst.should_ignore(tmp_path / "Nlog.config") is True
    app_insights = tmp_path / "ApplicationInsights.config"
    assert filter_inst.should_ignore(app_insights) is True


def test_ignore_filter_rules_and_meta_files(tmp_path: Path) -> None:
    """Rule definition directories and meta-rule database files must be ignored."""
    filter_inst = IgnoreFilter(root_dir=tmp_path)

    # Rules directory and files inside it
    assert filter_inst.should_ignore_dir("rules") is True
    assert filter_inst.should_ignore(tmp_path / "rules" / "sast_rules.json") is True
    assert filter_inst.should_ignore(tmp_path / "rules" / "profiles.json") is True

    # Standalone meta-rule files
    assert filter_inst.should_ignore(tmp_path / "sast_rules.json") is True
    assert filter_inst.should_ignore(tmp_path / "profiles.json") is True
    assert filter_inst.should_ignore(tmp_path / "profile.json") is True
