"""Unit tests for multithreaded parallel scanning in SASTScanner."""

from src.domain.sast_scanner import SASTScanner


def test_parallel_scanner_vs_sequential(tmp_path) -> None:
    """Verify parallel scanning and sequential scanning yield identical findings."""
    scanner = SASTScanner()

    # Create multiple test files with mixed vulnerabilities
    for i in range(10):
        f = tmp_path / f"test_file_{i}.js"
        if i % 2 == 0:
            f.write_text(f"document.write(user_input_{i});\n", encoding="utf-8")
        else:
            f.write_text(f"function safe_{i}() {{ return {i}; }}\n", encoding="utf-8")

    # Run sequential scan (threads=1)
    seq_res = scanner.scan_with_metadata(str(tmp_path), threads=1)

    # Run parallel scan (threads=4)
    par_res = scanner.scan_with_metadata(str(tmp_path), threads=4)

    assert seq_res["metadata"]["scanned_files"] == 10
    assert par_res["metadata"]["scanned_files"] == 10
    assert len(seq_res["findings"]) == len(par_res["findings"])
    assert len(par_res["findings"]) == 5


def test_parallel_scanner_single_file(tmp_path) -> None:
    """Verify single file scan handles threads parameter cleanly."""
    scanner = SASTScanner()
    single_file = tmp_path / "single.js"
    single_file.write_text("document.write(userInput);\n", encoding="utf-8")

    res = scanner.scan_with_metadata(str(single_file), threads=2)
    assert res["metadata"]["scanned_files"] == 1
    assert len(res["findings"]) == 1
