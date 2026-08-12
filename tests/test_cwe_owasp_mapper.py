"""Unit tests for CWEOWASPMapper."""

from src.domain.cwe_owasp_mapper import (
    FALLBACK_MAPPING,
    CWEOWASPMapper,
    MappingInfo,
)


def test_mapper_known_rules() -> None:
    """Test mapping standard SAST rule IDs to CWE and OWASP."""
    mapper = CWEOWASPMapper()

    mapping_xss = mapper.get_mapping("XSS_INLINE_OUTPUT")
    assert mapping_xss.cwe_id == "CWE-79"
    assert mapping_xss.owasp_category == "A03:2021-Injection"
    assert mapper.get_cwe("XSS_INLINE_OUTPUT") == "CWE-79"
    assert mapper.get_owasp("XSS_INLINE_OUTPUT") == "A03:2021-Injection"

    mapping_sqli = mapper.get_mapping("SQL_INJECTION")
    assert mapping_sqli.cwe_id == "CWE-89"
    assert mapping_sqli.owasp_category == "A03:2021-Injection"

    mapping_rce = mapper.get_mapping("RCE_EXEC")
    assert mapping_rce.cwe_id == "CWE-78"
    assert mapping_rce.owasp_category == "A03:2021-Injection"

    mapping_secret = mapper.get_mapping("HARDCODED_SECRET")
    assert mapping_secret.cwe_id == "CWE-798"
    owasp_auth = "A07:2021-Identification and Authentication Failures"
    assert mapping_secret.owasp_category == owasp_auth


def test_mapper_case_and_whitespace_insensitivity() -> None:
    """Test that rule matching handles lowercase and whitespace."""
    mapper = CWEOWASPMapper()
    mapping = mapper.get_mapping("  xss_inline_output  ")
    assert mapping.cwe_id == "CWE-79"


def test_mapper_unknown_rule_fallback() -> None:
    """Test fallback mapping for unrecognized rule IDs."""
    mapper = CWEOWASPMapper()
    mapping = mapper.get_mapping("UNKNOWN_CUSTOM_RULE_123")
    assert mapping == FALLBACK_MAPPING
    assert mapping.cwe_id == "CWE-699"
    assert mapping.to_dict()["cwe_id"] == "CWE-699"


def test_mapper_dynamic_registration() -> None:
    """Test dynamically registering a new rule mapping."""
    mapper = CWEOWASPMapper()
    ssti_cwe_name = (
        "Improper Neutralization of Special Elements Used in a Template Engine"
    )
    mapper.register_mapping(
        rule_id="CUSTOM_SSTI",
        cwe_id="CWE-1336",
        cwe_name=ssti_cwe_name,
        owasp_category="A03:2021-Injection",
        owasp_name="Injection",
    )

    mapping = mapper.get_mapping("CUSTOM_SSTI")
    assert mapping.cwe_id == "CWE-1336"
    assert mapping.owasp_category == "A03:2021-Injection"
    assert "CUSTOM_SSTI" in mapper.list_supported_rules()


def test_mapper_custom_initial_mappings() -> None:
    """Test initializing mapper with custom overrides."""
    custom = {
        "SPECIAL_RULE": MappingInfo(
            cwe_id="CWE-999",
            cwe_name="Custom Vulnerability",
            owasp_category="A00:2021-Custom",
            owasp_name="Custom",
        )
    }
    mapper = CWEOWASPMapper(custom_mappings=custom)
    assert mapper.get_cwe("SPECIAL_RULE") == "CWE-999"
    assert mapper.get_cwe("SQL_INJECTION") == "CWE-89"
