"""Unit tests for Shannon Entropy and Token Signature Detector."""

from pathlib import Path

from src.domain.entropy_detector import ShannonEntropyDetector
from src.domain.sast_scanner import SASTScanner


def _join_parts(*parts: str) -> str:
    """Helper to construct test fixture strings without triggering secret scanners."""
    return "".join(parts)


def test_calculate_entropy_math() -> None:
    """Verify mathematical properties of Shannon Entropy."""
    detector = ShannonEntropyDetector()
    assert detector.calculate_entropy("") == 0.0
    assert detector.calculate_entropy("aaaaaaa") == 0.0

    # Low entropy string
    low_ent = detector.calculate_entropy("abcabcabcabc")
    assert low_ent < 2.0

    # High entropy base64 string
    test_str = _join_parts(
        "vR8x", "L4nK", "9qP2", "mS7z", "B1wX", "6jD3", "fH5t", "Y0aC"
    )
    high_ent = detector.calculate_entropy(test_str)
    assert high_ent > 4.5


def test_openai_token_detection() -> None:
    """Verify detection of OpenAI API secret keys."""
    detector = ShannonEntropyDetector()
    dummy_key = _join_parts(
        "sk-",
        "a1b2",
        "c3d4",
        "e5f6",
        "g7h8",
        "i9j0",
        "k1l2",
        "m3n4",
        "o5p6",
        "q7r8",
        "s9t0",
        "u1v2",
        "w3x4",
    )
    line = f'openai_key = "{dummy_key}"'
    findings = detector.scan_line(line, 1, "test.py")
    rule_ids = {f["rule_id"] for f in findings}
    assert "TOKEN_OPENAI" in rule_ids


def test_github_pat_detection() -> None:
    """Verify detection of GitHub Personal Access Tokens."""
    detector = ShannonEntropyDetector()
    dummy_pat = _join_parts(
        "ghp_", "a1b2", "c3d4", "e5f6", "g7h8", "i9j0", "k1l2", "m3n4", "o5p6", "q7r8"
    )
    line = f'token = "{dummy_pat}"'
    findings = detector.scan_line(line, 1, "test.py")
    rule_ids = {f["rule_id"] for f in findings}
    assert "TOKEN_GITHUB" in rule_ids


def test_aws_key_detection() -> None:
    """Verify detection of AWS Access Key IDs."""
    detector = ShannonEntropyDetector()
    dummy_aws = _join_parts("AKIA", "0123", "4567", "89AB", "CDEF")
    line = f'AWS_ACCESS_KEY_ID = "{dummy_aws}"'
    findings = detector.scan_line(line, 1, "test.py")
    rule_ids = {f["rule_id"] for f in findings}
    assert "TOKEN_AWS" in rule_ids


def test_stripe_token_detection() -> None:
    """Verify detection of Stripe Live API secret keys."""
    detector = ShannonEntropyDetector()
    dummy_stripe = _join_parts(
        "sk_live_", "0123", "4567", "89ab", "cdef", "ABCD", "EF01"
    )
    line = f'stripe.api_key = "{dummy_stripe}"'
    findings = detector.scan_line(line, 1, "test.py")
    rule_ids = {f["rule_id"] for f in findings}
    assert "TOKEN_STRIPE" in rule_ids


def test_slack_token_detection() -> None:
    """Verify detection of Slack Bot/User tokens."""
    detector = ShannonEntropyDetector()
    dummy_slack = _join_parts(
        "xoxb-",
        "123456789012-",
        "123456789012-",
        "abcdef",
        "ghijkl",
        "mnopqr",
        "stuvwx",
    )
    line = f'SLACK_TOKEN = "{dummy_slack}"'
    findings = detector.scan_line(line, 1, "test.py")
    rule_ids = {f["rule_id"] for f in findings}
    assert "TOKEN_SLACK" in rule_ids


def test_private_key_detection() -> None:
    """Verify detection of unencrypted RSA/EC private keys."""
    detector = ShannonEntropyDetector()
    line = _join_parts("-----BEGIN ", "RSA PRIVATE ", "KEY-----")
    findings = detector.scan_line(line, 1, "test.py")
    rule_ids = {f["rule_id"] for f in findings}
    assert "TOKEN_PRIVATE_KEY" in rule_ids


def test_high_entropy_secret_with_security_context() -> None:
    """Verify high-entropy random string detection when assigned to secret keyword."""
    detector = ShannonEntropyDetector()
    # High entropy base64 string (32 chars)
    rand_val = _join_parts(
        "vR8x", "L4nK", "9qP2", "mS7z", "B1wX", "6jD3", "fH5t", "Y0aC"
    )
    line = f'api_secret_key = "{rand_val}"'
    findings = detector.scan_line(line, 10, "app.py")
    rule_ids = {f["rule_id"] for f in findings}
    assert "HIGH_ENTROPY_SECRET" in rule_ids


def test_false_positive_filtering() -> None:
    """Verify false positive filters ignore UUIDs, placeholders, and data URIs."""
    detector = ShannonEntropyDetector()

    # UUID/GUID must be ignored
    uuid_line = 'session_id = "123e4567-e89b-12d3-a456-426614174000"'
    assert not detector.scan_line(uuid_line, 1, "test.py")

    # Placeholder keys must be ignored
    placeholder_line = 'api_key = "YOUR_API_KEY_HERE_1234567890"'
    assert not detector.scan_line(placeholder_line, 1, "test.py")

    # Image base64 data URIs must be ignored
    data_uri_line = (
        'img_src = "data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFc'
        'SJAAAADUlEQVR42mNk+M9QDwADhgGAWjR9awAAAABJRU5ErkJggg=="'
    )
    assert not detector.scan_line(data_uri_line, 1, "test.py")


def test_sast_scanner_integration(tmp_path: Path) -> None:
    """Verify integration of ShannonEntropyDetector inside SASTScanner."""
    dummy_key = _join_parts(
        "sk-",
        "a1b2",
        "c3d4",
        "e5f6",
        "g7h8",
        "i9j0",
        "k1l2",
        "m3n4",
        "o5p6",
        "q7r8",
        "s9t0",
        "u1v2",
        "w3x4",
    )
    auth_val = _join_parts(
        "vR8x", "L4nK", "9qP2", "mS7z", "B1wX", "6jD3", "fH5t", "Y0aC"
    )
    vuln_file = tmp_path / "secret_leak.py"
    vuln_file.write_text(
        f'# Secret file\nopenai_secret = "{dummy_key}"\nauth_token = "{auth_val}"\n',
        encoding="utf-8",
    )

    scanner = SASTScanner()
    findings = scanner.scan(str(vuln_file))
    rule_ids = {f["rule_id"] for f in findings}

    assert "TOKEN_OPENAI" in rule_ids
    assert "HIGH_ENTROPY_SECRET" in rule_ids


def test_expanded_provider_tokens_detection() -> None:
    """Verify detection of Google, Azure SAS, Slack Webhook, Twilio, SendGrid,
    Docker Hub, and Vault.
    """
    detector = ShannonEntropyDetector()

    # 1. Google / Gemini API key
    dummy_google = _join_parts(
        "AIza", "SyD1", "2345", "6789", "0abc", "defg", "hijk", "LMNO", "PQRS", "TUV"
    )  # pragma: allowlist secret
    f_google = detector.scan_line(f'GEMINI_KEY = "{dummy_google}"', 1, "test.py")
    assert any(f["rule_id"] == "TOKEN_GOOGLE" for f in f_google)

    # 2. Azure SAS token
    dummy_sas = _join_parts(
        "sig=",
        "a1b2",
        "c3d4",
        "e5f6",
        "g7h8",
        "i9j0",
        "k1l2",
        "m3n4",
        "o5p6",
        "q7r8",
        "s9t0",
        "1234",
        "5678",
        "90A",
    )  # pragma: allowlist secret
    f_azure = detector.scan_line(
        f'blob_url = "https://myacct.blob.core.windows.net/cnt?{dummy_sas}"',
        2,
        "test.py",
    )
    assert any(f["rule_id"] == "TOKEN_AZURE_SAS" for f in f_azure)

    # 3. Slack Webhook URL
    dummy_webhook = _join_parts(
        "https://",
        "hooks.",
        "slack.com/",
        "services/",
        "T12345678/",
        "B87654321/",
        "a1b2",
        "c3d4",
        "e5f6",
        "g7h8",
        "i9j0",
        "k1l2",
    )  # pragma: allowlist secret
    f_slack_hook = detector.scan_line(f'webhook = "{dummy_webhook}"', 3, "test.py")
    assert any(f["rule_id"] == "TOKEN_SLACK_WEBHOOK" for f in f_slack_hook)

    # 4. Twilio API key
    dummy_twilio = _join_parts(
        "SK", "0123", "4567", "89ab", "cdef", "0123", "4567", "89ab", "cdef"
    )  # pragma: allowlist secret
    f_twilio = detector.scan_line(f'twilio_key = "{dummy_twilio}"', 4, "test.py")
    assert any(f["rule_id"] == "TOKEN_TWILIO" for f in f_twilio)

    # 5. SendGrid API key
    dummy_sendgrid = _join_parts(
        "SG.",
        "abcd",
        "efgh",
        "ijkl",
        "mnop",
        "qrst",
        "uv",
        ".",
        "1234",
        "5678",
        "90ab",
        "cdef",
        "ghij",
        "klmn",
        "opqr",
        "stuv",
        "wxyz",
        "1234",
        "567",
    )  # pragma: allowlist secret
    f_sendgrid = detector.scan_line(f'sendgrid_key = "{dummy_sendgrid}"', 5, "test.py")
    assert any(f["rule_id"] == "TOKEN_SENDGRID" for f in f_sendgrid)

    # 6. Docker Hub PAT
    dummy_docker = _join_parts(
        "dckr_", "pat_", "abcd", "efgh", "ijkl", "mnop", "qrst", "uvwx", "yz1"
    )  # pragma: allowlist secret
    f_docker = detector.scan_line(f'docker_pat = "{dummy_docker}"', 6, "test.py")
    assert any(f["rule_id"] == "TOKEN_DOCKER_HUB" for f in f_docker)

    # 7. Vault Token
    dummy_vault = _join_parts(
        "hvs.", "abcd", "efgh", "ijkl", "mnop", "qrst", "uvwx", "yz12"
    )  # pragma: allowlist secret
    f_vault = detector.scan_line(f'vault_token = "{dummy_vault}"', 7, "test.py")
    assert any(f["rule_id"] == "TOKEN_VAULT" for f in f_vault)
