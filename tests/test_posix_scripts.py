"""Unit tests for POSIX shell scripts (install.sh, update.sh, remove.sh)."""

from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[1]


def test_install_sh_structure() -> None:
    install_file = REPO_ROOT / "install.sh"
    assert install_file.exists()
    content = install_file.read_text(encoding="utf-8")
    assert content.startswith("#!/bin/sh")
    assert "set -e" in content
    assert "INSTALL_DIR=" in content
    assert "MCP_CONFIG=" in content
    assert "mcpServers" in content
    assert "control_plane.py" in content


def test_update_sh_structure() -> None:
    update_file = REPO_ROOT / "update.sh"
    assert update_file.exists()
    content = update_file.read_text(encoding="utf-8")
    assert content.startswith("#!/bin/sh")
    assert "set -e" in content
    assert "INSTALL_DIR=" in content
    assert "pip install" in content


def test_remove_sh_structure() -> None:
    remove_file = REPO_ROOT / "remove.sh"
    assert remove_file.exists()
    content = remove_file.read_text(encoding="utf-8")
    assert content.startswith("#!/bin/sh")
    assert "set -e" in content
    assert "rm -rf" in content
    assert "security-sast-guard" in content
