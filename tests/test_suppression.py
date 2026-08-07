"""Tests for SAST rule suppression and RCE false positive fixes."""

from src.domain.sast_scanner import SASTScanner


def test_rce_false_positive_browser_exec():
    """Verify regex.exec(...) in client-side JS does NOT trigger RCE_RISK."""
    scanner = SASTScanner()
    js_code = """
    var matches = filenameRegex.exec(disposition);
    a.download = filename;
    a.click();
    """
    findings = scanner.scan_code(js_code, "download.js")
    rce_findings = [f for f in findings if f.rule_id == "RCE_RISK"]
    assert len(rce_findings) == 0


def test_rce_real_vulnerabilities_detected():
    """Verify real RCE code IS detected by RCE_RISK."""
    scanner = SASTScanner()
    code = """
    eval("doSomethingDangerous()");
    os.system("whoami");
    child_process.exec("cat /etc/passwd");
    """
    findings = scanner.scan_code(code, "vulnerable.py")
    rce_findings = [f for f in findings if f.rule_id == "RCE_RISK"]
    assert len(rce_findings) >= 3


def test_inline_comment_suppression():
    """Verify inline comments like // sast-ignore RCE_RISK suppress findings."""
    scanner = SASTScanner()
    code = """
    eval("safe_eval_context()"); // sast-ignore RCE_RISK
    os.system("safe_cmd"); # sast-ignore
    """
    findings = scanner.scan_code(code, "test.py")
    assert len(findings) == 0


def test_preceding_comment_suppression():
    """Verify comment on preceding line suppresses finding on next line."""
    scanner = SASTScanner()
    code = """
    // sast-ignore RCE_RISK
    eval("context_is_validated()");
    """
    findings = scanner.scan_code(code, "test.js")
    assert len(findings) == 0
