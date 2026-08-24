"""Unit tests for new OWASP LLM, GitHub Actions, and Docker security rules."""

# pylint: disable=redefined-outer-name

import pytest

from src.domain.cwe_owasp_mapper import CWEOWASPMapper
from src.domain.sast_scanner import SASTScanner


@pytest.fixture
def scanner() -> SASTScanner:
    """Fixture returning initialized SASTScanner instance."""
    return SASTScanner()


def test_llm01_prompt_injection_detection(scanner: SASTScanner, tmp_path) -> None:
    """Verify LLM01_PROMPT_INJECTION detects unescaped user input."""
    vuln_file = tmp_path / "llm_vuln.py"
    vuln_file.write_text(
        'system_prompt = f"Answer query: {user_input}"\n'
        'response = client.chat.completions.create(prompt=f"{user_query}")\n',
        encoding="utf-8",
    )

    findings = scanner.scan(str(vuln_file))
    rule_ids = {f.get("rule_id") for f in findings}
    assert "LLM01_PROMPT_INJECTION" in rule_ids


def test_prompt_injection_sinks_are_llm_apis(scanner: SASTScanner) -> None:
    """Verify PROMPT_INJECTION_VULNERABLE has genuine LLM sinks, not SQL sinks."""
    rules = scanner.get_rules()
    prompt_rule = next(
        (r for r in rules if r.get("id") == "PROMPT_INJECTION_VULNERABLE"),
        None,
    )
    assert prompt_rule is not None
    sinks = prompt_rule.get("sinks", [])
    assert "openai.ChatCompletion" in sinks
    assert "cursor.execute" not in sinks
    assert "SqlCommand" not in sinks


def test_llm02_sensitive_data_exposure(scanner: SASTScanner, tmp_path) -> None:
    """Verify LLM02_SENSITIVE_DATA_EXPOSURE detects secrets in prompt context."""
    vuln_file = tmp_path / "llm_secret.py"
    vuln_file.write_text(
        'messages = [{"role": "system", "content": "Secret: " + api_key}]\n',
        encoding="utf-8",
    )

    findings = scanner.scan(str(vuln_file))
    rule_ids = {f.get("rule_id") for f in findings}
    assert "LLM02_SENSITIVE_DATA_EXPOSURE" in rule_ids


def test_llm06_excessive_agency(scanner: SASTScanner, tmp_path) -> None:
    """Verify LLM06_EXCESSIVE_AGENCY detects unconstrained agent tools."""
    vuln_file = tmp_path / "agent_config.py"
    vuln_file.write_text(
        "agent = initialize_agent(\n"
        "    tools=[ShellTool(dangerous=True)],\n"
        "    allow_dangerous_tools=True,\n"
        ")\n",
        encoding="utf-8",
    )

    findings = scanner.scan(str(vuln_file))
    rule_ids = {f.get("rule_id") for f in findings}
    assert "LLM06_EXCESSIVE_AGENCY" in rule_ids


def test_gha_expression_injection(scanner: SASTScanner, tmp_path) -> None:
    """Verify GHA_EXPRESSION_INJECTION detects untrusted expressions in run:."""
    workflow_file = tmp_path / "ci_workflow.yml"
    workflow_file.write_text(
        "jobs:\n"
        "  test:\n"
        "    runs-on: ubuntu-latest\n"
        "    steps:\n"
        "      - name: Print Title\n"
        '        run: echo "PR: ${{ github.event.pull_request.title }}"\n',
        encoding="utf-8",
    )

    findings = scanner.scan(str(workflow_file))
    rule_ids = {f.get("rule_id") for f in findings}
    assert "GHA_EXPRESSION_INJECTION" in rule_ids


def test_gha_unsafe_checkout(scanner: SASTScanner, tmp_path) -> None:
    """Verify GHA_UNSAFE_CHECKOUT detects untrusted checkout on pull_request_target."""
    workflow_file = tmp_path / "pwn_workflow.yml"
    workflow_file.write_text(
        "on: pull_request_target\n"
        "jobs:\n"
        "  build:\n"
        "    steps:\n"
        "      - uses: actions/checkout@v4\n"
        "        with:\n"
        "          ref: ${{ github.event.pull_request.head.sha }}\n",
        encoding="utf-8",
    )

    findings = scanner.scan(str(workflow_file))
    rule_ids = {f.get("rule_id") for f in findings}
    assert "GHA_UNSAFE_CHECKOUT" in rule_ids


def test_docker_security_rules(scanner: SASTScanner, tmp_path) -> None:
    """Verify DOCKER_ROOT_USER and DOCKER_CURL_BASH detection."""
    dockerfile = tmp_path / "Dockerfile"
    dockerfile.write_text(
        "FROM alpine:3.19\n"
        "USER root\n"
        "RUN curl -sSL https://example.com/install.sh | bash\n",
        encoding="utf-8",
    )

    findings = scanner.scan(str(dockerfile))
    rule_ids = {f.get("rule_id") for f in findings}
    assert "DOCKER_ROOT_USER" in rule_ids
    assert "DOCKER_CURL_BASH" in rule_ids


def test_cwe_owasp_mappings_for_new_rules() -> None:
    """Verify CWEOWASPMapper maps all new rules to appropriate standards."""
    mapper = CWEOWASPMapper()

    mapping_llm01 = mapper.get_mapping("LLM01_PROMPT_INJECTION")
    assert mapping_llm01.cwe_id == "CWE-77"
    assert "Prompt-Injection" in mapping_llm01.owasp_category

    mapping_llm02 = mapper.get_mapping("LLM02_SENSITIVE_DATA_EXPOSURE")
    assert mapping_llm02.cwe_id == "CWE-200"

    mapping_llm06 = mapper.get_mapping("LLM06_EXCESSIVE_AGENCY")
    assert mapping_llm06.cwe_id == "CWE-250"

    mapping_gha = mapper.get_mapping("GHA_EXPRESSION_INJECTION")
    assert mapping_gha.cwe_id == "CWE-94"
    assert "A03:2021" in mapping_gha.owasp_category

    mapping_docker_curl = mapper.get_mapping("DOCKER_CURL_BASH")
    assert mapping_docker_curl.cwe_id == "CWE-494"
