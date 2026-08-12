"""Pure ANSI TUI Renderer for Security SAST Guard."""

from __future__ import annotations

import re
from typing import ClassVar

from src.infrastructure.version_loader import get_plugin_version


class TUIRenderer:
    """Renders formatted ANSI text and ASCII fallback components for CLI output."""

    # ANSI Escape Sequences
    RESET: ClassVar[str] = "\033[0m"
    BOLD: ClassVar[str] = "\033[1m"
    DIM: ClassVar[str] = "\033[2m"

    RED: ClassVar[str] = "\033[31m"
    GREEN: ClassVar[str] = "\033[32m"
    YELLOW: ClassVar[str] = "\033[33m"
    BLUE: ClassVar[str] = "\033[34m"
    MAGENTA: ClassVar[str] = "\033[35m"
    CYAN: ClassVar[str] = "\033[36m"
    WHITE: ClassVar[str] = "\033[37m"

    BRIGHT_RED: ClassVar[str] = "\033[91m"
    BRIGHT_GREEN: ClassVar[str] = "\033[92m"
    BRIGHT_YELLOW: ClassVar[str] = "\033[93m"
    BRIGHT_BLUE: ClassVar[str] = "\033[94m"
    BRIGHT_CYAN: ClassVar[str] = "\033[96m"

    def __init__(
        self,
        use_unicode: bool = True,
        use_color: bool = True,
        width: int = 68,
    ) -> None:
        """Initialize the TUIRenderer.

        :param use_unicode: Whether to render Unicode characters/box borders.
        :param use_color: Whether to include ANSI color escape codes.
        :param width: Total character width of rendered boxes (minimum 40).
        """
        self.use_unicode = use_unicode
        self.use_color = use_color
        self.width = max(width, 40)

    @property
    def box_chars(self) -> dict[str, str]:
        """Return dictionary of box-drawing characters and icons."""
        if self.use_unicode:
            return {
                "top_left": "╭",
                "top_right": "╮",
                "bottom_left": "╰",
                "bottom_right": "╯",
                "horizontal": "─",
                "vertical": "│",
                "divider_left": "├",
                "divider_right": "┤",
                "divider_top": "┬",
                "divider_bottom": "┴",
                "filled_bar": "▰",
                "empty_bar": "▱",
                "shield": "⛨",
                "critical": "🔴",
                "high": "🟠",
                "medium": "🟡",
                "low": "🔵",
                "progress_icon": "⏳",
                "ai_icon": "🤖",
                "chart_icon": "📊",
                "file_icon": "📄",
                "firewall_icon": "🛡",
                "dot": "·",
            }
        return {
            "top_left": "+",
            "top_right": "+",
            "bottom_left": "+",
            "bottom_right": "+",
            "horizontal": "-",
            "vertical": "|",
            "divider_left": "+",
            "divider_right": "+",
            "divider_top": "+",
            "divider_bottom": "+",
            "filled_bar": "=",
            "empty_bar": "-",
            "shield": "[SAST]",
            "critical": "[CRITICAL]",
            "high": "[HIGH]",
            "medium": "[MEDIUM]",
            "low": "[LOW]",
            "progress_icon": "[PROG]",
            "ai_icon": "[AI]",
            "chart_icon": "[STAT]",
            "file_icon": "[FILE]",
            "firewall_icon": "[FW]",
            "dot": "-",
        }

    def _color(self, text: str, ansi_code: str) -> str:
        """Wrap text in ANSI color escape codes if color is enabled."""
        if not self.use_color:
            return text
        return f"{ansi_code}{text}{self.RESET}"

    @staticmethod
    def _strip_ansi(text: str) -> str:
        """Strip ANSI escape sequences from text."""
        return re.sub(r"\x1b\[[0-9;]*m", "", text)

    def _visible_len(self, text: str) -> int:
        """Calculate printable display character length."""
        return len(self._strip_ansi(text))

    def _pad_line(self, content: str, target_width: int | None = None) -> str:
        """Format line inside vertical borders padded with spaces."""
        w = target_width if target_width is not None else self.width
        chars = self.box_chars
        v = chars["vertical"]
        inner_width = w - 4
        content_len = self._visible_len(content)
        padding = max(0, inner_width - content_len)
        return f"{v}  {content}{' ' * padding}  {v}"

    def _top_border(self, target_width: int | None = None) -> str:
        w = target_width if target_width is not None else self.width
        chars = self.box_chars
        horiz = chars["horizontal"] * (w - 2)
        return f"{chars['top_left']}{horiz}{chars['top_right']}"

    def _bottom_border(self, target_width: int | None = None) -> str:
        w = target_width if target_width is not None else self.width
        chars = self.box_chars
        horiz = chars["horizontal"] * (w - 2)
        return f"{chars['bottom_left']}{horiz}{chars['bottom_right']}"

    def _divider(self, target_width: int | None = None) -> str:
        w = target_width if target_width is not None else self.width
        chars = self.box_chars
        horiz = chars["horizontal"] * (w - 2)
        return f"{chars['divider_left']}{horiz}{chars['divider_right']}"

    def render_scan_progress(
        self,
        scanned: int,
        total: int,
        current_file: str = "",
        iteration: int = 1,
        max_iterations: int = 5,
    ) -> str:
        """Render scanning progress bar inside a box."""
        # pylint: disable=too-many-locals
        version = get_plugin_version()
        chars = self.box_chars

        dot = chars["dot"]
        header_text = (
            f"{self._color(chars['shield'], self.BRIGHT_CYAN)} "
            f"{self._color(f'Security SAST Guard v{version}', self.BOLD)}"
        )
        if current_file:
            header_text += f"  {dot}  Scanning: {current_file}"

        pct = int((scanned / total) * 100) if total > 0 else 0
        pct = min(100, max(0, pct))

        bar_len = 28
        filled_count = int(bar_len * (pct / 100))
        empty_count = bar_len - filled_count

        filled_str = self._color(chars["filled_bar"] * filled_count, self.GREEN)
        empty_str = self._color(chars["empty_bar"] * empty_count, self.DIM)
        progress_bar = f"{filled_str}{empty_str}"

        prog_line = f"{progress_bar}  [{pct:>3}%]  {scanned} / {total} files"
        ai_line = (
            f"{chars['progress_icon']} AI Verification in progress...  "
            f"(Iteration {iteration}/{max_iterations})"
        )

        lines = [
            self._top_border(),
            self._pad_line(header_text),
            self._divider(),
            self._pad_line(prog_line),
            self._pad_line(ai_line),
            self._bottom_border(),
        ]
        return "\n".join(lines)

    # pylint: disable=too-many-arguments,too-many-positional-arguments,too-many-locals
    def render_scan_summary(
        self,
        target_path: str,
        duration: float,
        files_count: int,
        severity_counts: dict[str, int],
        fp_filtered: int,
        fp_reduction: float,
        report_path: str,
    ) -> str:
        """Render complete SAST scan summary card."""
        chars = self.box_chars
        version = get_plugin_version()

        dot = chars["dot"]
        header = (
            f"{self._color(chars['shield'], self.BRIGHT_GREEN)} "
            f"{self._color('SAST Audit Complete', self.BOLD)} v{version}  {dot}  "
            f"{target_path}  {dot}  {duration:.2f}s  {dot}  {files_count} files"
        )

        norm_counts: dict[str, int] = {}
        for k, v in severity_counts.items():
            norm_counts[k.upper()] = v

        critical_cnt = norm_counts.get("CRITICAL", 0)
        high_cnt = norm_counts.get("HIGH", 0)
        medium_cnt = norm_counts.get("MEDIUM", 0)
        low_cnt = norm_counts.get("LOW", 0)

        c_label = f"{chars['critical']} " + self._color("CRITICAL", self.BRIGHT_RED)
        h_label = f"{chars['high']} " + self._color("HIGH", self.BRIGHT_YELLOW)
        m_label = f"{chars['medium']} " + self._color("MEDIUM", self.YELLOW)
        l_label = f"{chars['low']} " + self._color("LOW", self.BRIGHT_CYAN)

        def _plural(cnt: int) -> str:
            return "finding" if cnt == 1 else "findings"

        c_val = f"{critical_cnt} {_plural(critical_cnt)}"
        h_val = f"{high_cnt} {_plural(high_cnt)}"
        m_val = f"{medium_cnt} {_plural(medium_cnt)}"
        l_val = f"{low_cnt} {_plural(low_cnt)}"

        col1_w = 24
        col2_w = self.width - 3 - col1_w

        top_div = (
            f"{chars['divider_left']}{chars['horizontal'] * (col1_w - 1)}"
            f"{chars['divider_top']}{chars['horizontal'] * (col2_w - 1)}"
            f"{chars['divider_right']}"
        )
        mid_div = (
            f"{chars['divider_left']}{chars['horizontal'] * (col1_w - 1)}"
            f"{chars['divider_bottom']}{chars['horizontal'] * (col2_w - 1)}"
            f"{chars['divider_right']}"
        )

        def _row_2col(left: str, right: str) -> str:
            v = chars["vertical"]
            l_pad = max(0, col1_w - 3 - self._visible_len(left))
            r_pad = max(0, col2_w - 3 - self._visible_len(right))
            return f"{v}  {left}{' ' * l_pad}{v}  {right}{' ' * r_pad}{v}"

        ai_fp_line = (
            f"{chars['ai_icon']} AI Filtered FP     : "
            f"{fp_filtered} false positives removed"
        )
        fpr_line = f"{chars['chart_icon']} FPR Reduction      : {fp_reduction:.1f}%"
        report_line = f"{chars['file_icon']} Report             : {report_path}"

        lines = [
            self._top_border(),
            self._pad_line(header),
            top_div,
            _row_2col(c_label, c_val),
            _row_2col(h_label, h_val),
            _row_2col(m_label, m_val),
            _row_2col(l_label, l_val),
            mid_div,
            self._pad_line(ai_fp_line),
            self._pad_line(fpr_line),
            self._pad_line(report_line),
            self._bottom_border(),
        ]
        return "\n".join(lines)

    # pylint: disable=too-many-locals
    def render_finding(
        self,
        severity: str,
        rule_id: str,
        line_no: int,
        file_path: str,
        code_snippet: str,
    ) -> str:
        """Render a single security finding box."""
        chars = self.box_chars
        sev_upper = severity.upper()

        icon = chars.get(sev_upper.lower(), chars["shield"])
        color_code = self.WHITE
        if sev_upper == "CRITICAL":
            color_code = self.BRIGHT_RED
        elif sev_upper == "HIGH":
            color_code = self.BRIGHT_YELLOW
        elif sev_upper == "MEDIUM":
            color_code = self.YELLOW
        elif sev_upper == "LOW":
            color_code = self.BRIGHT_CYAN

        dot = chars["dot"]
        sev_colored = self._color(sev_upper, color_code)
        header = f"{icon} {sev_colored}  {dot}  {rule_id} (line {line_no})"
        file_line = f"File: {file_path}:{line_no}"

        lines = [
            self._top_border(),
            self._pad_line(header),
            self._pad_line(file_line),
            self._divider(),
        ]

        snippet_lines = code_snippet.strip().splitlines()
        if not snippet_lines:
            snippet_lines = ["<no snippet available>"]

        for idx, s_line in enumerate(snippet_lines):
            curr_line_no = line_no + idx
            code_line = f"> {curr_line_no:>4} | {s_line}"
            lines.append(self._pad_line(code_line))

        lines.append(self._bottom_border())
        return "\n".join(lines)

    def render_firewall_verdict(
        self,
        verdict: str,
        intent: str,
        risk_score: float,
        reason: str,
    ) -> str:
        """Render Command Firewall verdict summary box."""
        chars = self.box_chars
        verdict_upper = verdict.upper()

        v_color = self.WHITE
        if verdict_upper == "ALLOW":
            v_color = self.BRIGHT_GREEN
        elif verdict_upper == "CONFIRM":
            v_color = self.BRIGHT_YELLOW
        elif verdict_upper == "DENY":
            v_color = self.BRIGHT_RED

        v_badge = self._color(f"[{verdict_upper}]", v_color)
        header = (
            f"{chars['firewall_icon']} "
            f"{self._color('Command Firewall Verdict:', self.BOLD)} {v_badge}"
        )

        intent_line = f"Intent    : {intent}"
        risk_line = f"Risk Score: {risk_score:.2f} / 1.00"
        reason_line = f"Reason    : {reason}"

        lines = [
            self._top_border(),
            self._pad_line(header),
            self._divider(),
            self._pad_line(intent_line),
            self._pad_line(risk_line),
            self._pad_line(reason_line),
            self._bottom_border(),
        ]
        return "\n".join(lines)
