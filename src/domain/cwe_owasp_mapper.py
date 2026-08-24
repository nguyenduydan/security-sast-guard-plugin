"""CWE and OWASP mapping domain service for SAST rules."""

from dataclasses import dataclass

XSS_CWE_NAME = (
    "Improper Neutralization of Input During Web Page Generation "
    "('Cross-site Scripting')"
)
SQLI_CWE_NAME = (
    "Improper Neutralization of Special Elements used in an SQL Command "
    "('SQL Injection')"
)
RCE_CWE_NAME = (
    "Improper Neutralization of Special Elements used in an OS Command "
    "('OS Command Injection')"
)
PATH_TRAVERSAL_CWE_NAME = (
    "Improper Limitation of a Pathname to a Restricted Directory ('Path Traversal')"
)


@dataclass(frozen=True)
class MappingInfo:
    """Dataclass holding CWE and OWASP metadata for a SAST rule."""

    cwe_id: str
    cwe_name: str
    owasp_category: str
    owasp_name: str

    def to_dict(self) -> dict[str, str]:
        """Convert mapping info to dictionary representation."""
        return {
            "cwe_id": self.cwe_id,
            "cwe_name": self.cwe_name,
            "owasp_category": self.owasp_category,
            "owasp_name": self.owasp_name,
        }


DEFAULT_MAPPINGS: dict[str, MappingInfo] = {
    "XSS_INLINE_OUTPUT": MappingInfo(
        cwe_id="CWE-79",
        cwe_name=XSS_CWE_NAME,
        owasp_category="A03:2021-Injection",
        owasp_name="Injection",
    ),
    "XSS": MappingInfo(
        cwe_id="CWE-79",
        cwe_name=XSS_CWE_NAME,
        owasp_category="A03:2021-Injection",
        owasp_name="Injection",
    ),
    "REFLECTED_XSS": MappingInfo(
        cwe_id="CWE-79",
        cwe_name=XSS_CWE_NAME,
        owasp_category="A03:2021-Injection",
        owasp_name="Injection",
    ),
    "STORED_XSS": MappingInfo(
        cwe_id="CWE-79",
        cwe_name=XSS_CWE_NAME,
        owasp_category="A03:2021-Injection",
        owasp_name="Injection",
    ),
    "SQL_INJECTION": MappingInfo(
        cwe_id="CWE-89",
        cwe_name=SQLI_CWE_NAME,
        owasp_category="A03:2021-Injection",
        owasp_name="Injection",
    ),
    "SQLI": MappingInfo(
        cwe_id="CWE-89",
        cwe_name=SQLI_CWE_NAME,
        owasp_category="A03:2021-Injection",
        owasp_name="Injection",
    ),
    "RCE_EXEC": MappingInfo(
        cwe_id="CWE-78",
        cwe_name=RCE_CWE_NAME,
        owasp_category="A03:2021-Injection",
        owasp_name="Injection",
    ),
    "RCE": MappingInfo(
        cwe_id="CWE-78",
        cwe_name=RCE_CWE_NAME,
        owasp_category="A03:2021-Injection",
        owasp_name="Injection",
    ),
    "COMMAND_INJECTION": MappingInfo(
        cwe_id="CWE-78",
        cwe_name=RCE_CWE_NAME,
        owasp_category="A03:2021-Injection",
        owasp_name="Injection",
    ),
    "PATH_TRAVERSAL": MappingInfo(
        cwe_id="CWE-22",
        cwe_name=PATH_TRAVERSAL_CWE_NAME,
        owasp_category="A01:2021-Broken Access Control",
        owasp_name="Broken Access Control",
    ),
    "DIR_TRAVERSAL": MappingInfo(
        cwe_id="CWE-22",
        cwe_name=PATH_TRAVERSAL_CWE_NAME,
        owasp_category="A01:2021-Broken Access Control",
        owasp_name="Broken Access Control",
    ),
    "HARDCODED_SECRET": MappingInfo(
        cwe_id="CWE-798",
        cwe_name="Use of Hard-coded Credentials",
        owasp_category="A07:2021-Identification and Authentication Failures",
        owasp_name="Identification and Authentication Failures",
    ),
    "HARDCODED_KEY": MappingInfo(
        cwe_id="CWE-798",
        cwe_name="Use of Hard-coded Credentials",
        owasp_category="A07:2021-Identification and Authentication Failures",
        owasp_name="Identification and Authentication Failures",
    ),
    "SECRET_LEAK": MappingInfo(
        cwe_id="CWE-798",
        cwe_name="Use of Hard-coded Credentials",
        owasp_category="A07:2021-Identification and Authentication Failures",
        owasp_name="Identification and Authentication Failures",
    ),
    "DESERIALIZATION": MappingInfo(
        cwe_id="CWE-502",
        cwe_name="Deserialization of Untrusted Data",
        owasp_category="A08:2021-Software and Data Integrity Failures",
        owasp_name="Software and Data Integrity Failures",
    ),
    "DESERIALIZATION_RCE": MappingInfo(
        cwe_id="CWE-502",
        cwe_name="Deserialization of Untrusted Data",
        owasp_category="A08:2021-Software and Data Integrity Failures",
        owasp_name="Software and Data Integrity Failures",
    ),
    "UNSAFE_DESERIALIZATION": MappingInfo(
        cwe_id="CWE-502",
        cwe_name="Deserialization of Untrusted Data",
        owasp_category="A08:2021-Software and Data Integrity Failures",
        owasp_name="Software and Data Integrity Failures",
    ),
    "SSRF": MappingInfo(
        cwe_id="CWE-918",
        cwe_name="Server-Side Request Forgery (SSRF)",
        owasp_category="A10:2021-Server-Side Resource Forgery (SSRF)",
        owasp_name="Server-Side Resource Forgery (SSRF)",
    ),
    "CSRF": MappingInfo(
        cwe_id="CWE-352",
        cwe_name="Cross-Site Request Forgery (CSRF)",
        owasp_category="A01:2021-Broken Access Control",
        owasp_name="Broken Access Control",
    ),
    "BROKEN_AUTH": MappingInfo(
        cwe_id="CWE-287",
        cwe_name="Improper Authentication",
        owasp_category="A07:2021-Identification and Authentication Failures",
        owasp_name="Identification and Authentication Failures",
    ),
    "WEAK_PASSWORD": MappingInfo(
        cwe_id="CWE-521",
        cwe_name="Weak Password Requirements",
        owasp_category="A07:2021-Identification and Authentication Failures",
        owasp_name="Identification and Authentication Failures",
    ),
    "INSECURE_CRYPTO": MappingInfo(
        cwe_id="CWE-327",
        cwe_name="Use of a Broken or Risky Cryptographic Algorithm",
        owasp_category="A02:2021-Cryptographic Failures",
        owasp_name="Cryptographic Failures",
    ),
    "WEAK_HASH": MappingInfo(
        cwe_id="CWE-328",
        cwe_name="Use of Weak Hash",
        owasp_category="A02:2021-Cryptographic Failures",
        owasp_name="Cryptographic Failures",
    ),
    "OPEN_REDIRECT": MappingInfo(
        cwe_id="CWE-601",
        cwe_name="URL Redirection to Untrusted Site ('Open Redirect')",
        owasp_category="A01:2021-Broken Access Control",
        owasp_name="Broken Access Control",
    ),
    "XXE": MappingInfo(
        cwe_id="CWE-611",
        cwe_name="Improper Restriction of XML External Entity Reference",
        owasp_category="A05:2021-Security Misconfiguration",
        owasp_name="Security Misconfiguration",
    ),
    "LLM01_PROMPT_INJECTION": MappingInfo(
        cwe_id="CWE-77",
        cwe_name="Improper Neutralization of Special Elements used in a Command",
        owasp_category="LLM01:2025-Prompt-Injection",
        owasp_name="Prompt Injection",
    ),
    "PROMPT_INJECTION_VULNERABLE": MappingInfo(
        cwe_id="CWE-77",
        cwe_name="Improper Neutralization of Special Elements used in a Command",
        owasp_category="LLM01:2025-Prompt-Injection",
        owasp_name="Prompt Injection",
    ),
    "LLM02_SENSITIVE_DATA_EXPOSURE": MappingInfo(
        cwe_id="CWE-200",
        cwe_name="Exposure of Sensitive Information to an Unauthorized Actor",
        owasp_category="LLM02:2025-Sensitive-Information-Disclosure",
        owasp_name="Sensitive Information Disclosure",
    ),
    "LLM06_EXCESSIVE_AGENCY": MappingInfo(
        cwe_id="CWE-250",
        cwe_name="Execution with Unnecessary Privileges",
        owasp_category="LLM06:2025-Excessive-Agency",
        owasp_name="Excessive Agency",
    ),
    "GHA_EXPRESSION_INJECTION": MappingInfo(
        cwe_id="CWE-94",
        cwe_name="Improper Control of Generation of Code ('Code Injection')",
        owasp_category="A03:2021-Injection",
        owasp_name="CI/CD Script Injection",
    ),
    "GHA_UNSAFE_CHECKOUT": MappingInfo(
        cwe_id="CWE-829",
        cwe_name="Inclusion of Functionality from Untrusted Control Sphere",
        owasp_category="A01:2021-Broken Access Control",
        owasp_name="Untrusted PR Checkout",
    ),
    "DOCKER_ROOT_USER": MappingInfo(
        cwe_id="CWE-250",
        cwe_name="Execution with Unnecessary Privileges",
        owasp_category="A05:2021-Security Misconfiguration",
        owasp_name="Container Root Execution",
    ),
    "DOCKER_CURL_BASH": MappingInfo(
        cwe_id="CWE-494",
        cwe_name="Download of Code Without Integrity Check",
        owasp_category="A08:2021-Software and Data Integrity Failures",
        owasp_name="Unverified Remote Code Execution",
    ),
    "HIGH_ENTROPY_SECRET": MappingInfo(
        cwe_id="CWE-798",
        cwe_name="Use of Hard-coded Credentials",
        owasp_category="A07:2021-Identification and Authentication Failures",
        owasp_name="Hardcoded Secret & Key",
    ),
    "TOKEN_OPENAI": MappingInfo(
        cwe_id="CWE-798",
        cwe_name="Use of Hard-coded Credentials",
        owasp_category="A07:2021-Identification and Authentication Failures",
        owasp_name="OpenAI API Key Leak",
    ),
    "TOKEN_GITHUB": MappingInfo(
        cwe_id="CWE-798",
        cwe_name="Use of Hard-coded Credentials",
        owasp_category="A07:2021-Identification and Authentication Failures",
        owasp_name="GitHub Token Leak",
    ),
    "TOKEN_AWS": MappingInfo(
        cwe_id="CWE-798",
        cwe_name="Use of Hard-coded Credentials",
        owasp_category="A07:2021-Identification and Authentication Failures",
        owasp_name="AWS Access Key Leak",
    ),
    "TOKEN_ANTHROPIC": MappingInfo(
        cwe_id="CWE-798",
        cwe_name="Use of Hard-coded Credentials",
        owasp_category="A07:2021-Identification and Authentication Failures",
        owasp_name="Anthropic API Key Leak",
    ),
    "TOKEN_STRIPE": MappingInfo(
        cwe_id="CWE-798",
        cwe_name="Use of Hard-coded Credentials",
        owasp_category="A07:2021-Identification and Authentication Failures",
        owasp_name="Stripe API Key Leak",
    ),
    "TOKEN_SLACK": MappingInfo(
        cwe_id="CWE-798",
        cwe_name="Use of Hard-coded Credentials",
        owasp_category="A07:2021-Identification and Authentication Failures",
        owasp_name="Slack Token Leak",
    ),
    "TOKEN_PRIVATE_KEY": MappingInfo(
        cwe_id="CWE-312",
        cwe_name="Cleartext Storage of Sensitive Information",
        owasp_category="A02:2021-Cryptographic Failures",
        owasp_name="Private Key Exposure",
    ),
}

FALLBACK_MAPPING = MappingInfo(
    cwe_id="CWE-699",
    cwe_name="Software Development (General Uncategorized Rule)",
    owasp_category="A10:2021-General Security Risk",
    owasp_name="General Security Risk",
)


class CWEOWASPMapper:
    """Mapper connecting SAST rule IDs to CWE numbers and OWASP categories."""

    def __init__(self, custom_mappings: dict[str, MappingInfo] | None = None) -> None:
        """Initialize mapper with optional custom overrides."""
        self._mappings: dict[str, MappingInfo] = dict(DEFAULT_MAPPINGS)
        if custom_mappings:
            self._mappings.update(custom_mappings)

    def get_mapping(self, rule_id: str) -> MappingInfo:
        """Get full CWE and OWASP mapping info for a given rule_id."""
        normalized_rule = rule_id.strip().upper()
        return self._mappings.get(normalized_rule, FALLBACK_MAPPING)

    def get_cwe(self, rule_id: str) -> str:
        """Get CWE ID string (e.g. 'CWE-79') for rule_id."""
        return self.get_mapping(rule_id).cwe_id

    def get_owasp(self, rule_id: str) -> str:
        """Get OWASP category string (e.g. 'A03:2021-Injection') for rule_id."""
        return self.get_mapping(rule_id).owasp_category

    def register_mapping(
        self,
        rule_id: str,
        cwe_id: str,
        cwe_name: str,
        owasp_category: str,
        owasp_name: str,
    ) -> None:
        """Register or update a rule ID mapping dynamically."""
        normalized_rule = rule_id.strip().upper()
        self._mappings[normalized_rule] = MappingInfo(
            cwe_id=cwe_id,
            cwe_name=cwe_name,
            owasp_category=owasp_category,
            owasp_name=owasp_name,
        )

    def list_supported_rules(self) -> list[str]:
        """Return list of all rule IDs currently registered in the mapper."""
        return sorted(self._mappings.keys())
