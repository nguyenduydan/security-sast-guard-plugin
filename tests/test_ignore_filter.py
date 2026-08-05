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
    assert filter_inst.should_ignore(tmp_path / "secret_folder" / "data.txt") is True
    assert filter_inst.should_ignore(tmp_path / "normal.txt") is False


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
