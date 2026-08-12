"""Unit tests for pure ANSI TUIRenderer."""

from __future__ import annotations

from unittest.mock import patch

from src.infrastructure.tui_renderer import TUIRenderer
from src.infrastructure.version_loader import get_plugin_version


class TestTUIRenderer:
    """Test suite for TUIRenderer class."""

    def test_render_scan_progress_unicode(self) -> None:
        """Test progress rendering with Unicode and ANSI color enabled."""
        renderer = TUIRenderer(use_unicode=True, use_color=True, width=68)
        output = renderer.render_scan_progress(
            scanned=38,
            total=53,
            current_file="src/main.py",
            iteration=1,
            max_iterations=5,
        )

        version = get_plugin_version()
        assert f"v{version}" in output
        assert "71%" in output or "72%" in output
        assert "38 / 53 files" in output
        assert "src/main.py" in output
        assert "╭" in output
        assert "╰" in output
        assert "\033[" in output

    def test_render_scan_progress_ascii_no_color(self) -> None:
        """Test progress rendering with ASCII fallback and no ANSI color."""
        renderer = TUIRenderer(use_unicode=False, use_color=False, width=68)
        output = renderer.render_scan_progress(
            scanned=10, total=20, current_file="test.py"
        )

        assert "\033[" not in output
        assert "+" in output
        assert "10 / 20 files" in output
        assert "50%" in output

    def test_render_scan_summary(self) -> None:
        """Test scan summary box rendering."""
        renderer = TUIRenderer(use_unicode=True, use_color=True, width=70)
        sev_counts = {"CRITICAL": 2, "HIGH": 5, "MEDIUM": 3, "LOW": 1}
        output = renderer.render_scan_summary(
            target_path="src/",
            duration=1.24,
            files_count=53,
            severity_counts=sev_counts,
            fp_filtered=14,
            fp_reduction=73.6,
            report_path="reports/sast-2026-08-12.md",
        )

        assert "SAST Audit Complete" in output
        assert "1.24s" in output
        assert "53 files" in output
        assert "2 findings" in output
        assert "5 findings" in output
        assert "3 findings" in output
        assert "1 finding" in output
        assert "14 false positives removed" in output
        assert "73.6%" in output
        assert "reports/sast-2026-08-12.md" in output

    def test_render_finding(self) -> None:
        """Test finding card box rendering."""
        renderer = TUIRenderer(use_unicode=True, use_color=False, width=68)
        code = "query = f'SELECT * FROM users WHERE id = {user_id}'"
        output = renderer.render_finding(
            severity="CRITICAL",
            rule_id="SQL-INJECTION",
            line_no=42,
            file_path="src/db.py",
            code_snippet=code,
        )

        assert "CRITICAL" in output
        assert "SQL-INJECTION (line 42)" in output
        assert "File: src/db.py:42" in output
        assert ">   42 | query = f'SELECT * FROM users WHERE id = {user_id}'" in output

    def test_render_firewall_verdict(self) -> None:
        """Test Command Firewall verdict box rendering."""
        renderer = TUIRenderer(use_unicode=True, use_color=True, width=68)
        output = renderer.render_firewall_verdict(
            verdict="DENY",
            intent="Remote Shell Execution",
            risk_score=0.95,
            reason="Detected curl piped into bash execution",
        )

        assert "[DENY]" in output
        assert "Remote Shell Execution" in output
        assert "0.95 / 1.00" in output
        assert "Detected curl piped into bash execution" in output

    def test_dynamic_version_loader(self) -> None:
        """Verify get_plugin_version is dynamically invoked."""
        renderer = TUIRenderer()
        with patch(
            "src.infrastructure.tui_renderer.get_plugin_version",
            return_value="9.9.9-test",
        ):
            out = renderer.render_scan_progress(1, 10, "foo.py")
            assert "v9.9.9-test" in out

            summary = renderer.render_scan_summary(
                "src/", 0.5, 10, {}, 0, 0.0, "out.md"
            )
            assert "v9.9.9-test" in summary

    def test_edge_cases(self) -> None:
        """Test zero total, empty snippet, and high scanned values."""
        renderer = TUIRenderer(use_unicode=False, use_color=False)
        out1 = renderer.render_scan_progress(0, 0, "")
        assert "[  0%]" in out1 or "[0%]" in out1

        out2 = renderer.render_finding(
            severity="LOW",
            rule_id="SEC-001",
            line_no=1,
            file_path="empty.py",
            code_snippet="",
        )
        assert "<no snippet available>" in out2
