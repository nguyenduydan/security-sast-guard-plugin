/* ==========================================================================
   Security SAST Guard - Main JavaScript Application & Step Visualizer Engine
   ========================================================================== */

const GITHUB_REPO = "nguyenduydan/security-sast-guard-plugin";
const FALLBACK_VERSION = "v2.8.0";
let activeCategory = "ALL";

let autoPlayTimer = null;
let isAutoPlaying = false;

// 53 SAST Vector Rules Database
const SAST_RULES = [
  {
    "id": "RCE_RISK",
    "name": "Remote Code Execution (RCE Risk - OWASP ASI05)",
    "category": "OWASP Web 2021",
    "severity": "CRITICAL",
    "desc": "Matches arbitrary shell command execution or dynamic code evaluation (eval, exec, subprocess, os.system)."
  },
  {
    "id": "WILDCARD_PATH",
    "name": "Excessive File Access / Wildcard Path Traversal (OWASP ASI03)",
    "category": "OWASP API 2023",
    "severity": "HIGH",
    "desc": "Matches wildcard (*) patterns or root directory path traversals causing excessive file system access."
  },
  {
    "id": "PLAINTEXT_SECRET",
    "name": "Plaintext Credentials & Secret Exposure (OWASP LLM02)",
    "category": "OWASP Web 2021",
    "severity": "CRITICAL",
    "desc": "Detects API keys, passwords, and private tokens exposed in configurations or source code."
  },
  {
    "id": "DESERIALIZATION_RCE",
    "name": "Unsafe Deserialization Risk (CWE-502)",
    "category": "OWASP Web 2021",
    "severity": "HIGH",
    "desc": "Detects parsing of untrusted input using unsafe deserializers like pickle, marshal, or PyYAML unsafe_load."
  },
  {
    "id": "XXE_RISK",
    "name": "XML External Entity (XXE) Injection (CWE-611)",
    "category": "CWE Top 25",
    "severity": "HIGH",
    "desc": "Detects insecure XML parsers configured with external entity resolution enabled."
  },
  {
    "id": "PROMPT_INJECTION_VULNERABLE",
    "name": "Prompt Injection Vulnerability (OWASP LLM01)",
    "category": "OWASP API 2023",
    "severity": "MEDIUM",
    "desc": "Detects unescaped user inputs directly interpolated into LLM prompts without boundary delimiters."
  },
  {
    "id": "SSRF_LAN_ACCESS",
    "name": "Server-Side Request Forgery & Internal LAN Access (CWE-918)",
    "category": "OWASP API 2023",
    "severity": "HIGH",
    "desc": "Detects outbound HTTP requests targeting localhost, internal RFC1918 IPs, or cloud metadata endpoints."
  },
  {
    "id": "SKILL_EXFILTRATION",
    "name": "Skill & Agent Tool Data Exfiltration (OWASP LLM06)",
    "category": "OWASP API 2023",
    "severity": "HIGH",
    "desc": "Detects agent tools sending local workspace files or environment variables to external endpoints."
  },
  {
    "id": "SQL_INJECTION",
    "name": "SQL Injection Vulnerability (CWE-89)",
    "category": "OWASP Web 2021",
    "severity": "CRITICAL",
    "desc": "Detects unparameterized SQL queries built via string concatenation or raw formatting."
  },
  {
    "id": "XSS_VULNERABILITY",
    "name": "Cross-Site Scripting (XSS - CWE-79)",
    "category": "OWASP Web 2021",
    "severity": "HIGH",
    "desc": "Detects unescaped user input rendered into HTML markup, DOM sinks, or inline script event handlers."
  },
  {
    "id": "CSRF_CLICKJACKING",
    "name": "Cross-Site Request Forgery & Clickjacking (CWE-352)",
    "category": "OWASP Web 2021",
    "severity": "HIGH",
    "desc": "Detects state-changing endpoints lacking CSRF tokens or missing X-Frame-Options protection."
  },
  {
    "id": "UNRESTRICTED_FILE_UPLOAD",
    "name": "Unrestricted File Upload (CWE-434)",
    "category": "OWASP Web 2021",
    "severity": "CRITICAL",
    "desc": "Detects file upload handlers missing extension whitelists, MIME validation, or path sanitization."
  },
  {
    "id": "VERBOSE_ERROR_DISCLOSURE",
    "name": "Verbose Error & Stack Trace Disclosure (CWE-209)",
    "category": "OWASP Web 2021",
    "severity": "MEDIUM",
    "desc": "Detects sensitive debug information, exception details, or stack traces returned to client responses."
  },
  {
    "id": "ASP_NET_WEBMETHOD_EXPOSURE",
    "name": "Exposed ASP.NET WebMethod Endpoint (CWE-306)",
    "category": "OWASP Web 2021",
    "severity": "HIGH",
    "desc": "Detects public ASP.NET WebMethod / ScriptMethod endpoints missing authentication and authorization gates."
  },
  {
    "id": "CORS_MISCONFIGURATION",
    "name": "Permissive Cross-Origin Resource Sharing (CORS Misconfiguration)",
    "category": "OWASP Web 2021",
    "severity": "MEDIUM",
    "desc": "Detects wildcard (*) Access-Control-Allow-Origin headers combined with credentials allowance."
  },
  {
    "id": "API_SECURITY_CHECKLIST",
    "name": "API Security Architecture Checklist",
    "category": "OWASP API 2023",
    "severity": "HIGH",
    "desc": "Comprehensive security validation for API endpoints, schemas, and transport encryption."
  },
  {
    "id": "DISCOVERY_GUIDE",
    "name": "API Discovery & Endpoint Enumeration Guard",
    "category": "OWASP API 2023",
    "severity": "HIGH",
    "desc": "Ensures undocumented or internal debug API routes are not publicly exposed."
  },
  {
    "id": "FULL_AUDIT",
    "name": "Full Codebase Security Audit Baseline",
    "category": "OWASP Web 2021",
    "severity": "HIGH",
    "desc": "Comprehensive multi-tier static security assessment across all source files."
  },
  {
    "id": "GOVERNMENT",
    "name": "Public Sector & Government Compliance Standards",
    "category": "OWASP Web 2021",
    "severity": "CRITICAL",
    "desc": "Enforces strict access control, auditing, and encryption compliance according to standards."
  },
  {
    "id": "QUICK_API",
    "name": "Quick API Security Health Check",
    "category": "OWASP API 2023",
    "severity": "CRITICAL",
    "desc": "Fast heuristic verification of API authorization, input validation, and headers."
  },
  {
    "id": "WEB_APP",
    "name": "Web Application Security Baseline",
    "category": "OWASP Web 2021",
    "severity": "CRITICAL",
    "desc": "Core security policy enforcement for modern web application frontends and backends."
  },
  {
    "id": "README",
    "name": "Security Policy & Governance Guide",
    "category": "OWASP API 2023",
    "severity": "CRITICAL",
    "desc": "Baseline guidelines for secure development lifecycle and threat vector management."
  },
  {
    "id": "CWE_TOP25_RULES",
    "name": "CWE Top 25 Most Dangerous Software Weaknesses",
    "category": "CWE Top 25",
    "severity": "CRITICAL",
    "desc": "Enforces static detection rules covering the MITRE CWE Top 25 vulnerability standards."
  },
  {
    "id": "GETCURRENTUSERID",
    "name": "Broken Object Level Authorization (BOLA / IDOR - CWE-284)",
    "category": "OWASP Web 2021",
    "severity": "MEDIUM",
    "desc": "Detects resource queries relying on user-supplied IDs instead of authenticated session identity."
  },
  {
    "id": "DTO",
    "name": "Mass Assignment & Broken Object Property Authorization",
    "category": "OWASP API 2023",
    "severity": "MEDIUM",
    "desc": "Detects automatic binding of request payloads to database models exposing private fields."
  },
  {
    "id": "OTHER_USER_ID",
    "name": "Horizontal Privilege Escalation (IDOR)",
    "category": "OWASP API 2023",
    "severity": "CRITICAL",
    "desc": "Detects accessing records belonging to other users without tenancy or ownership verification."
  },
  {
    "id": "USER",
    "name": "Broken Authentication & Credential Verification",
    "category": "OWASP API 2023",
    "severity": "MEDIUM",
    "desc": "Detects weak password handling, plaintext authentication, or missing session validation."
  },
  {
    "id": "SESSION",
    "name": "Insecure Session Management & Token Storage",
    "category": "OWASP API 2023",
    "severity": "CRITICAL",
    "desc": "Detects session tokens stored in insecure storage or lacking HttpOnly / Secure flags."
  },
  {
    "id": "API6_BUSINESSFLOW",
    "name": "Unrestricted Access to Sensitive Business Flows",
    "category": "OWASP API 2023",
    "severity": "CRITICAL",
    "desc": "Flags critical business logic endpoints vulnerable to automated abuse and lacking rate limiting."
  },
  {
    "id": "API7_SSRF",
    "name": "Server-Side Request Forgery in API Consumers",
    "category": "OWASP API 2023",
    "severity": "CRITICAL",
    "desc": "Detects user-controlled URLs passed to backend HTTP clients without host whitelisting."
  },
  {
    "id": "API8_MISCONFIGURATION",
    "name": "Security Misconfiguration & Verbose Headers",
    "category": "OWASP API 2023",
    "severity": "CRITICAL",
    "desc": "Identifies missing security headers, default passwords, and unnecessary HTTP methods."
  },
  {
    "id": "API9_INVENTORY",
    "name": "Improper API Inventory & Zombie Endpoints",
    "category": "OWASP API 2023",
    "severity": "LOW",
    "desc": "Detects unversioned deprecated APIs or shadow debug endpoints exposed to clients."
  },
  {
    "id": "REQUEST",
    "name": "Unsafe Consumption of Third-Party APIs",
    "category": "OWASP Web 2021",
    "severity": "CRITICAL",
    "desc": "Detects unvalidated ingestion of external API response payloads into critical sinks."
  },
  {
    "id": "BCRYPT",
    "name": "Weak Cryptographic Algorithms & Insecure Hashing",
    "category": "OWASP Web 2021",
    "severity": "CRITICAL",
    "desc": "Detects outdated hashing algorithms (MD5, SHA1) used for password storage or signatures."
  },
  {
    "id": "A03_INJECTION",
    "name": "OWASP A03:2021 - Injection Vulnerabilities",
    "category": "OWASP Web 2021",
    "severity": "CRITICAL",
    "desc": "Covers SQL, Command, LDAP, and Expression injection vulnerabilities."
  },
  {
    "id": "A05_SECURITYMISCONFIGURATION",
    "name": "OWASP A05:2021 - Security Misconfiguration",
    "category": "OWASP Web 2021",
    "severity": "CRITICAL",
    "desc": "Detects default settings, verbose debug modes, and misconfigured access permissions."
  },
  {
    "id": "A06_VULNERABLECOMPONENTS",
    "name": "OWASP A06:2021 - Vulnerable and Outdated Components",
    "category": "OWASP Web 2021",
    "severity": "CRITICAL",
    "desc": "Flags known vulnerable dependencies and unsupported software libraries."
  },
  {
    "id": "A07_AUTHFAILURES",
    "name": "OWASP A07:2021 - Identification & Authentication Failures",
    "category": "OWASP Web 2021",
    "severity": "CRITICAL",
    "desc": "Detects missing authentication, weak session timeouts, and brute force exposure."
  },
  {
    "id": "A08_DATAINTEGRITYFAILURES",
    "name": "OWASP A08:2021 - Software and Data Integrity Failures",
    "category": "OWASP Web 2021",
    "severity": "MEDIUM",
    "desc": "Detects unverified code execution, auto-updates without signatures, and unsafe deserialization."
  },
  {
    "id": "A09_LOGGINGFAILURES",
    "name": "OWASP A09:2021 - Security Logging and Monitoring Failures",
    "category": "OWASP Web 2021",
    "severity": "MEDIUM",
    "desc": "Identifies critical state-changing actions missing structured audit logging."
  },
  {
    "id": "A10_SSRF",
    "name": "OWASP A10:2021 - Server-Side Request Forgery (SSRF)",
    "category": "OWASP Web 2021",
    "severity": "CRITICAL",
    "desc": "Detects arbitrary URL fetching without strict protocol and host whitelisting."
  },
  {
    "id": "WEB10_RACECONDITION",
    "name": "Race Condition & Concurrency Flaws (TOCTOU)",
    "category": "OWASP Web 2021",
    "severity": "MEDIUM",
    "desc": "Detects time-of-check to time-of-use race conditions in file and transaction operations."
  },
  {
    "id": "WEB11_SOURCEFILEEXPOSURE",
    "name": "Source Code & Backup File Exposure",
    "category": "OWASP Web 2021",
    "severity": "CRITICAL",
    "desc": "Detects exposed .git, .env, backup, or source files accessible via web routes."
  },
  {
    "id": "WEB1_HTTPSECURITYHEADERS",
    "name": "Missing HTTP Security Headers",
    "category": "OWASP Web 2021",
    "severity": "MEDIUM",
    "desc": "Detects web responses missing HSTS, CSP, X-Content-Type-Options, or Referrer-Policy."
  },
  {
    "id": "WEB2_CSRF_CLICKJACKING",
    "name": "Cross-Site Request Forgery Protection Gate",
    "category": "OWASP Web 2021",
    "severity": "MEDIUM",
    "desc": "Enforces anti-CSRF token verification on state-changing POST/PUT/DELETE requests."
  },
  {
    "id": "WEB3_FRONTENDSECURITY",
    "name": "Frontend DOM Security & Inline Script Sanitization",
    "category": "OWASP Web 2021",
    "severity": "MEDIUM",
    "desc": "Enforces DOMPurify or safe templating on user-controlled HTML string bindings."
  },
  {
    "id": "NEWFILENAME",
    "name": "Path Traversal & Insecure File Name Handling",
    "category": "OWASP Web 2021",
    "severity": "CRITICAL",
    "desc": "Detects file creations or downloads using unvalidated user-supplied file names."
  },
  {
    "id": "WEB5_ERRORHANDLING",
    "name": "Custom Error Pages & Exception Sanitization",
    "category": "OWASP Web 2021",
    "severity": "MEDIUM",
    "desc": "Ensures generic error handlers are configured without leaking internal system state."
  },
  {
    "id": "WEB6_WEBFORMSASPNET",
    "name": "ASP.NET ViewState & EventValidation Protection",
    "category": "OWASP Web 2021",
    "severity": "MEDIUM",
    "desc": "Detects disabled ViewState encryption or disabled EventValidation in ASP.NET WebForms."
  },
  {
    "id": "WEB7_THIRDPARTYDASHBOARDS",
    "name": "Unprotected Admin Dashboards & Endpoints",
    "category": "OWASP Web 2021",
    "severity": "CRITICAL",
    "desc": "Detects third-party admin or telemetry dashboards exposed without authentication."
  },
  {
    "id": "WEB8_SENSITIVEACTIONREAUTH",
    "name": "Sensitive Action Re-authentication Gate",
    "category": "OWASP Web 2021",
    "severity": "CRITICAL",
    "desc": "Enforces password re-prompting or MFA before password changes, email updates, or financial actions."
  },
  {
    "id": "WEB9_CORSMISCONFIGURATION",
    "name": "CORS Origin Reflection Vulnerability",
    "category": "OWASP Web 2021",
    "severity": "CRITICAL",
    "desc": "Detects reflecting incoming Origin header into Access-Control-Allow-Origin response."
  },
  {
    "id": "SKILL",
    "name": "AI Agent Skill Permission & Tool Isolation",
    "category": "OWASP API 2023",
    "severity": "CRITICAL",
    "desc": "Enforces sandboxing and least privilege permissions for custom AI Agent tools."
  },
  {
    "id": "XSS_INLINE_EVENT",
    "name": "Cross-Site Scripting Inline Event Attributes (CWE-79)",
    "category": "OWASP Web 2021",
    "severity": "HIGH",
    "desc": "Detects inline JavaScript event attributes like onfocus=, onerror="
  },
  {
    "id": "BROKEN_ACCESS_CONTROL",
    "name": "Unvalidated Privilege Parameter Tampering (CWE-639 / CWE-269)",
    "category": "OWASP Web 2021",
    "severity": "CRITICAL",
    "desc": "Detects unvalidated role or privilege parameter assignments"
  },
  {
    "id": "cwe_top25_rules",
    "name": "cwe_top25_rules",
    "category": "CWE Top 25",
    "severity": "CRITICAL",
    "desc": "Imported rule from cwe_top25_rules.md"
  },
  {
    "id": "nist_key_controls",
    "name": "nist_key_controls",
    "category": "NIST 800-53",
    "severity": "CRITICAL",
    "desc": "Imported rule from nist_key_controls.md"
  },
  {
    "id": "API10_2023",
    "name": "Unsafe Consumption of APIs",
    "category": "OWASP API 2023",
    "severity": "MEDIUM",
    "desc": "Imported rule from API10_ThirdParty.md"
  },
  {
    "id": "API1_2023",
    "name": "Broken Object Level Authorization (BOLA)",
    "category": "OWASP API 2023",
    "severity": "CRITICAL",
    "desc": "Imported rule from API1_BOLA.md"
  },
  {
    "id": "API2_2023",
    "name": "Broken Authentication",
    "category": "OWASP API 2023",
    "severity": "CRITICAL",
    "desc": "Imported rule from API2_BrokenAuth.md"
  },
  {
    "id": "API3_2023",
    "name": "Broken Object Property Level Authorization",
    "category": "OWASP API 2023",
    "severity": "MEDIUM",
    "desc": "Imported rule from API3_MassAssignment.md"
  },
  {
    "id": "API4_2023",
    "name": "Unrestricted Resource Consumption",
    "category": "OWASP API 2023",
    "severity": "CRITICAL",
    "desc": "Imported rule from API4_RateLimit.md"
  },
  {
    "id": "API5_2023",
    "name": "Broken Function Level Authorization",
    "category": "OWASP API 2023",
    "severity": "CRITICAL",
    "desc": "Imported rule from API5_FunctionAuth.md"
  },
  {
    "id": "API6_2023",
    "name": "Unrestricted Access to Sensitive Business Flows",
    "category": "OWASP API 2023",
    "severity": "CRITICAL",
    "desc": "Imported rule from API6_BusinessFlow.md"
  },
  {
    "id": "API7_2023",
    "name": "Server Side Request Forgery (SSRF)",
    "category": "OWASP API 2023",
    "severity": "CRITICAL",
    "desc": "Imported rule from API7_SSRF.md"
  },
  {
    "id": "API8_2023",
    "name": "Security Misconfiguration",
    "category": "OWASP API 2023",
    "severity": "CRITICAL",
    "desc": "Imported rule from API8_Misconfiguration.md"
  },
  {
    "id": "API9_2023",
    "name": "Improper Inventory Management",
    "category": "OWASP API 2023",
    "severity": "LOW",
    "desc": "Imported rule from API9_Inventory.md"
  },
  {
    "id": "A01_2021",
    "name": "Broken Access Control",
    "category": "OWASP Web 2021",
    "severity": "CRITICAL",
    "desc": "Imported rule from A01_BrokenAccessControl.md"
  },
  {
    "id": "A02_2021",
    "name": "Cryptographic Failures",
    "category": "OWASP Web 2021",
    "severity": "CRITICAL",
    "desc": "Imported rule from A02_CryptoFailures.md"
  },
  {
    "id": "A03_2021",
    "name": "Injection (SQL, NoSQL, OS Command, LDAP, XSS)",
    "category": "OWASP Web 2021",
    "severity": "CRITICAL",
    "desc": "Imported rule from A03_Injection.md"
  },
  {
    "id": "A04_2021",
    "name": "Insecure Design",
    "category": "OWASP Web 2021",
    "severity": "MEDIUM",
    "desc": "Imported rule from A04_InsecureDesign.md"
  },
  {
    "id": "A05_2021",
    "name": "Security Misconfiguration",
    "category": "OWASP Web 2021",
    "severity": "CRITICAL",
    "desc": "Imported rule from A05_SecurityMisconfiguration.md"
  },
  {
    "id": "A06_2021",
    "name": "Vulnerable and Outdated Components",
    "category": "OWASP Web 2021",
    "severity": "CRITICAL",
    "desc": "Imported rule from A06_VulnerableComponents.md"
  },
  {
    "id": "A07_2021",
    "name": "Identification and Authentication Failures",
    "category": "OWASP Web 2021",
    "severity": "CRITICAL",
    "desc": "Imported rule from A07_AuthFailures.md"
  },
  {
    "id": "A08_2021",
    "name": "Software and Data Integrity Failures",
    "category": "OWASP Web 2021",
    "severity": "MEDIUM",
    "desc": "Imported rule from A08_DataIntegrityFailures.md"
  },
  {
    "id": "A09_2021",
    "name": "Security Logging and Monitoring Failures",
    "category": "OWASP Web 2021",
    "severity": "MEDIUM",
    "desc": "Imported rule from A09_LoggingFailures.md"
  },
  {
    "id": "A10_2021",
    "name": "Server-Side Request Forgery (SSRF)",
    "category": "OWASP Web 2021",
    "severity": "CRITICAL",
    "desc": "Imported rule from A10_SSRF.md"
  },
  {
    "id": "WEB10",
    "name": "Race Condition / TOCTOU",
    "category": "OWASP Web 2021",
    "severity": "MEDIUM",
    "desc": "Imported rule from WEB10_RaceCondition.md"
  },
  {
    "id": "WEB11",
    "name": "Source File & Sensitive Data Exposure",
    "category": "OWASP Web 2021",
    "severity": "MEDIUM",
    "desc": "Imported rule from WEB11_SourceFileExposure.md"
  },
  {
    "id": "WEB1",
    "name": "HTTP Security Headers",
    "category": "OWASP Web 2021",
    "severity": "MEDIUM",
    "desc": "Imported rule from WEB1_HTTPSecurityHeaders.md"
  },
  {
    "id": "WEB2",
    "name": "CSRF & Clickjacking Protection",
    "category": "OWASP Web 2021",
    "severity": "MEDIUM",
    "desc": "Imported rule from WEB2_CSRF_Clickjacking.md"
  },
  {
    "id": "WEB3",
    "name": "Frontend Security",
    "category": "OWASP Web 2021",
    "severity": "MEDIUM",
    "desc": "Imported rule from WEB3_FrontendSecurity.md"
  },
  {
    "id": "WEB4",
    "name": "File Upload Security",
    "category": "OWASP Web 2021",
    "severity": "CRITICAL",
    "desc": "Imported rule from WEB4_FileUploadSecurity.md"
  },
  {
    "id": "WEB5",
    "name": "Error Handling & Information Disclosure",
    "category": "OWASP Web 2021",
    "severity": "MEDIUM",
    "desc": "Imported rule from WEB5_ErrorHandling.md"
  },
  {
    "id": "WEB6",
    "name": "ASP.NET Specific Security (WebForms, MVC, Core)",
    "category": "OWASP Web 2021",
    "severity": "MEDIUM",
    "desc": "Imported rule from WEB6_WebFormsASPNET.md"
  },
  {
    "id": "WEB7",
    "name": "Third-party Admin Dashboards & Management Endpoints",
    "category": "OWASP Web 2021",
    "severity": "CRITICAL",
    "desc": "Imported rule from WEB7_ThirdPartyDashboards.md"
  },
  {
    "id": "WEB8",
    "name": "Sensitive Action Re-authentication",
    "category": "OWASP Web 2021",
    "severity": "CRITICAL",
    "desc": "Imported rule from WEB8_SensitiveActionReauth.md"
  },
  {
    "id": "WEB9",
    "name": "CORS Misconfiguration",
    "category": "OWASP Web 2021",
    "severity": "CRITICAL",
    "desc": "Imported rule from WEB9_CORSMisconfiguration.md"
  },
  {
    "id": "LLM01_PROMPT_INJECTION",
    "name": "LLM Prompt Injection Vulnerability (OWASP LLM01)",
    "category": "OWASP LLM 2025",
    "severity": "CRITICAL",
    "desc": "Detects unescaped user input directly interpolated into System Prompts or LLM prompt templates."
  },
  {
    "id": "LLM02_SENSITIVE_DATA_EXPOSURE",
    "name": "Sensitive Data Exposure in LLM Context (OWASP LLM02)",
    "category": "OWASP LLM 2025",
    "severity": "HIGH",
    "desc": "Detects API keys, passwords, connection strings, or private tokens embedded into LLM prompt context."
  },
  {
    "id": "LLM06_EXCESSIVE_AGENCY",
    "name": "Excessive Agency & Unconstrained Tool Execution (OWASP LLM06)",
    "category": "OWASP LLM 2025",
    "severity": "CRITICAL",
    "desc": "Detects AI agent tools configured with shell or dangerous execution permissions without verification gates."
  },
  {
    "id": "GHA_EXPRESSION_INJECTION",
    "name": "GitHub Actions Script Expression Injection (GHA Injection)",
    "category": "CI/CD & GitHub Actions",
    "severity": "CRITICAL",
    "desc": "Detects untrusted GitHub context expressions interpolated directly inside run: steps."
  },
  {
    "id": "GHA_UNSAFE_CHECKOUT",
    "name": "GitHub Actions Unsafe PR Target Checkout (PWN Request)",
    "category": "CI/CD & GitHub Actions",
    "severity": "HIGH",
    "desc": "Flags pull_request_target workflows checking out untrusted PR head commit references."
  },
  {
    "id": "DOCKER_ROOT_USER",
    "name": "Container Execution as Root User (Dockerfile Security)",
    "category": "Container Security",
    "severity": "MEDIUM",
    "desc": "Detects Dockerfiles running container processes under root without switching to a non-root USER."
  },
  {
    "id": "DOCKER_CURL_BASH",
    "name": "Unverified Remote Script Execution (Curl Pipe Bash)",
    "category": "Container Security",
    "severity": "HIGH",
    "desc": "Detects downloading and piping unverified shell scripts directly to bash/sh during container builds."
  }
];


document.addEventListener("DOMContentLoaded", () => {
  initTheme();
  initDockObserver();
  initWorkflowVisualizer();
  initScrollToTop();
  fetchLatestRelease();
});

/* --------------------------------------------------------------------------
   8. Scroll To Top Engine
   -------------------------------------------------------------------------- */
function initScrollToTop() {
  const btn = document.getElementById("scroll-to-top-btn");
  if (!btn) return;

  window.addEventListener("scroll", () => {
    if (window.scrollY > 300) {
      btn.classList.remove("opacity-0", "translate-y-4", "pointer-events-none");
      btn.classList.add("opacity-100", "translate-y-0", "pointer-events-auto");
    } else {
      btn.classList.remove("opacity-100", "translate-y-0", "pointer-events-auto");
      btn.classList.add("opacity-0", "translate-y-4", "pointer-events-none");
    }
  });
}

function scrollToTop() {
  window.scrollTo({ top: 0, behavior: "smooth" });
}

/* --------------------------------------------------------------------------
   9. Global Window Event Handler Expositions
   -------------------------------------------------------------------------- */
window.toggleTheme = toggleTheme;
window.selectStep = selectStep;
window.toggleWorkflowAutoPlay = toggleWorkflowAutoPlay;
window.simulateCommand = simulateCommand;
window.handleCustomCommand = handleCustomCommand;
window.openRulesModal = openRulesModal;
window.closeRulesModal = closeRulesModal;
window.setCategory = setCategory;
window.filterRules = filterRules;
window.switchTab = switchTab;
window.copySnippet = copySnippet;
window.showCopyToast = showCopyToast;
window.scrollToTop = scrollToTop;

/* --------------------------------------------------------------------------
   1. Theme Management (Light / Dark Neo-Brutalist Toggle)
   -------------------------------------------------------------------------- */
function initTheme() {
  const savedTheme = localStorage.getItem("sast-theme");
  const prefersDark = window.matchMedia("(prefers-color-scheme: dark)").matches;

  if (savedTheme === "dark" || (!savedTheme && prefersDark)) {
    document.documentElement.classList.add("dark");
  } else {
    document.documentElement.classList.remove("dark");
  }
  updateThemeIcon();
}

function toggleTheme() {
  document.documentElement.classList.toggle("dark");
  const isDark = document.documentElement.classList.contains("dark");
  localStorage.setItem("sast-theme", isDark ? "dark" : "light");
  updateThemeIcon();
}

function updateThemeIcon() {
  const btn = document.getElementById("theme-toggle-btn");
  if (!btn) return;
  const isDark = document.documentElement.classList.contains("dark");
  btn.innerHTML = isDark
    ? '<i class="ph-bold ph-sun text-amber-400 text-lg inline-block theme-icon-spin"></i>'
    : '<i class="ph-bold ph-moon-stars text-slate-800 text-lg inline-block theme-icon-spin"></i>';
}

/* --------------------------------------------------------------------------
   2. Floating Cyber-HUD Dock Section Observer
   -------------------------------------------------------------------------- */
function initDockObserver() {
  const sections = document.querySelectorAll("section[id]");
  const navItems = document.querySelectorAll(".dock-item");

  const activeExists = Array.from(navItems).some((item) => item.classList.contains("nav-link-active"));
  if (!activeExists && navItems.length > 0) {
    const firstItem = document.querySelector('.dock-item[data-nav-section="firewall"]');
    if (firstItem) firstItem.classList.add("nav-link-active");
  }

  const observer = new IntersectionObserver(
    (entries) => {
      entries.forEach((entry) => {
        if (entry.isIntersecting) {
          const id = entry.target.getAttribute("id");
          navItems.forEach((item) => {
            if (item.getAttribute("data-nav-section") === id) {
              item.classList.add("nav-link-active");
            } else {
              item.classList.remove("nav-link-active");
            }
          });
        }
      });
    },
    { threshold: 0.3 }
  );

  sections.forEach((section) => observer.observe(section));
}

/* --------------------------------------------------------------------------
   3. Interactive Step-by-Step Workflow Visualizer Engine
   -------------------------------------------------------------------------- */
const WORKFLOW_STEPS = [
  {
    step: 1,
    title: "Node 01-A: Intake & Requirements Gate (PreCommand Hook)",
    icon: "ph-clipboard-text",
    tag: "CLIENT & HOOK LAYER",
    badgeColor: "bg-emerald-500 text-black",
    description: "Intercepts shell execution before terminal run. Evaluates request intent and enforces profile constraints.",
    codeSnippet: `[Intake Service] Analyzing request context...\n[✓] Confidence Score: 98%\n[✓] Target Scope: src/domain/firewall_engine.py\n[✓] Profile Loaded: CWD .sast/profile.json (Level: FULL)\n[✓] Action Plan: Proceeding with zero ambiguity.`
  },
  {
    step: "1b",
    title: "Node 01-B: AI File Modifications Guard (PostToolCallExecute)",
    icon: "ph-code-simple",
    tag: "CLIENT & HOOK LAYER",
    badgeColor: "bg-emerald-500 text-black",
    description: "Triggers automatically after AI code modifications. Immediately runs SAST scan on generated diffs before saving to disk.",
    codeSnippet: `[PostToolCallExecute] File modified: src/domain/scanner.py\n[✓] Diff Extracted: +42 lines, -12 lines\n[✓] Auto-Scan Initiated against OWASP Vector Rules\n[✓] Zero vulnerabilities detected in generated diff.`
  },
  {
    step: "1c",
    title: "Node 01-C: Antigravity Slash Commands Suite",
    icon: "ph-terminal-window",
    tag: "CLIENT & HOOK LAYER",
    badgeColor: "bg-emerald-500 text-black",
    description: "Slash commands integrated into AI session (/sast-audit, /sast-init, /sast-mode, /sast-rules) for on-demand security auditing.",
    codeSnippet: `[Slash Commands] Executing /sast-audit file=src/app.py --level=ultra\n[✓] Scanning against 53 OWASP Vector Rules...\n[✓] Taint Dataflow Traces Extracted\n[✓] Zero critical vulnerabilities found.`
  },
  {
    step: 2,
    title: "Node 02-A: Command Firewall & Anti-Bypass Deobfuscator",
    icon: "ph-shield-warning",
    tag: "FIREWALL ENGINE",
    badgeColor: "bg-rose-500 text-white",
    description: "Executes PreCommandExecute hook. Strips obfuscation carets (^, \`) and decodes Base64 shell payloads before terminal execution.",
    codeSnippet: `[FirewallEngine] Evaluating command: "powershell -enc cm0gLXJmIC8="\n[!] Anti-Bypass Deobfuscation Triggered!\n[!] Decoded Payload: "rm -rf /"\n[✗] VERDICT: DENY (Dangerous pattern matched)\n[✓] Command Execution Blocked Safely.`
  },
  {
    step: "2b",
    title: "Node 02-B: PowerShell AST Parser & Pattern Matcher",
    icon: "ph-terminal-window",
    tag: "FIREWALL ENGINE",
    badgeColor: "bg-rose-500 text-white",
    description: "Parses PowerShell AST tokens and evaluates commands against ALLOW, CONFIRM, and DENY security rules.",
    codeSnippet: `[AST Parser] Analyzing command tokens: "Remove-Item -Path C:\\Windows -Recurse"\n[!] Match Found: Remove-Item (Destructive file deletion)\n[!] Action Required: User confirmation modal triggered\n[✓] VERDICT: CONFIRM.`
  },
  {
    step: "2c",
    title: "Node 02-C: Firewall Verdict Engine (DENY / CONFIRM / ALLOW)",
    icon: "ph-gavel",
    tag: "FIREWALL ENGINE",
    badgeColor: "bg-rose-500 text-white",
    description: "Enforces zero-trust command verdicts. DENY blocks destructive calls automatically; CONFIRM requests explicit user approval.",
    codeSnippet: `[Verdict Engine] Final Evaluation:\n  - DENY: Blocked "rm -rf /", "Format-Volume", "Disable-Defender"\n  - CONFIRM: Prompted user for "Remove-Item", "git push --force"\n  - ALLOW: Permitted clean read-only status commands.`
  },
  {
    step: "3a",
    title: "Node 03-A: Profile Cascade Resolver (.sast/profile.json)",
    icon: "ph-gear-six",
    tag: "CONTROL PLANE",
    badgeColor: "bg-cyan-500 text-black",
    description: "Resolves project configuration cascading from CWD (.sast/profile.json) -> Git Root -> Global Fallback (~/.gemini/config).",
    codeSnippet: `[Profile Cascade] Resolving settings...\n[✓] Local Profile Found: .sast/profile.json\n[✓] Audit Level: FULL (53 Rules Active)\n[✓] Operation Mode: STRICT (Fail-Closed Enforcement).`
  },
  {
    step: "core",
    title: "Node CORE: Stdio MCP Server (9 Stdio JSON-RPC Tools)",
    icon: "ph-cpu",
    tag: "CONTROL PLANE & MCP",
    badgeColor: "bg-brand-emerald text-black",
    description: "Central Stdio MCP Server exposing 9 specialized security tools (sast_scan_file, sast_scan_diff, sast_check_command, sast_init, etc.) to AI agent.",
    codeSnippet: `[MCP Server] Stdio JSON-RPC Transport Connected\n[✓] Available Tools: 9 Eager & Lazy Tools Registered\n[✓] Real-time JSON-RPC Query Processing Active\n[✓] Zero-Latency Subprocess IPC Communication.`
  },
  {
    step: "3c",
    title: "Node 03-C: Operation Mode & Audit Level Controls",
    icon: "ph-sliders-horizontal",
    tag: "CONTROL PLANE",
    badgeColor: "bg-cyan-500 text-black",
    description: "Controls strictness levels (lite, full, ultra) and operation modes (strict, draft). Parses inline # sast-ignore suppressions.",
    codeSnippet: `[Mode Engine] Active Settings:\n  - Mode: strict (Blocks execution on any Critical/High finding)\n  - Level: ultra (Includes dataflow taint tracking)\n  - Comment Suppression: # sast-ignore parsed on Line 88.`
  },
  {
    step: 3,
    title: "Node 03: 53 SAST Vector Audit Engine",
    icon: "ph-magnifying-glass-plus",
    tag: "SAST SCAN ENGINE",
    badgeColor: "bg-brand-cyan text-black",
    description: "Scans modified files against 53 OWASP Top 10, CWE Top 25, NIST 800-53, and ASP.NET security rules.",
    codeSnippet: `[SAST Audit] Scanning file: src/api/routes.py\n[!] Rule Triggered: OWASP-A03-SQLi (Critical)\n    Line 42: query = f"SELECT * FROM users WHERE id = '{user_id}'"\n[✓] AST Scope Extracted: Class UserHandler -> Method get_user()\n[✓] 1 Finding Registered.`
  },
  {
    step: 4,
    title: "Node 04: SHA-256 AI Response Cache",
    icon: "ph-brain",
    tag: "AI CACHE ENGINE",
    badgeColor: "bg-violet-500 text-white",
    description: "Queries LLM AI Verifier to filter false positives. Results cached locally with SHA-256 keys (24h TTL) for 0ms latency verification.",
    codeSnippet: `[AICache] Checking key: 8f9a2b4c1e7d...\n[✓] CACHE HIT! SHA-256 verification retrieved (Latency: 0ms)\n[✓] Verification Result: Valid Vulnerability Confirmed\n[✓] Suggested Remediation: Use Parameterized Queries.`
  },
  {
    step: 5,
    title: "Node 05: Report Generator & Audit Trail Logger",
    icon: "ph-file-text",
    tag: "EXPORTERS & LOGS",
    badgeColor: "bg-amber-500 text-black",
    description: "Generates ISO SARIF 2.1.0, Markdown, and JSON reports while logging audit decisions to .aiops/decisions.jsonl.",
    codeSnippet: `[Report Generator] SARIF report created: reports/sast_audit.sarif\n[Report Generator] Markdown report created: reports/sast_audit.md\n[Decision Log] Appended entry to .aiops/decisions.jsonl\n[✓] SAST Guard Workflow Execution Complete.`
  }
];

const WORKFLOW_MODES = {
  firewall: {
    activeNodes: ['1', '2', 'core', '2c', '5'],
    defaultStep: '2',
    btnId: 'mode-btn-firewall',
    btnClass: 'bg-rose-500 text-white'
  },
  autoscan: {
    activeNodes: ['1b', '2b', 'core', '4'],
    defaultStep: '1b',
    btnId: 'mode-btn-autoscan',
    btnClass: 'bg-emerald-500 text-black'
  },
  slash: {
    activeNodes: ['1c', '3a', 'core', '3c', '3'],
    defaultStep: '1c',
    btnId: 'mode-btn-slash',
    btnClass: 'bg-cyan-500 text-black'
  },
  all: {
    activeNodes: ['1', '1b', '1c', '2', '2b', '2c', '3a', 'core', '3c', '3', '4', '5'],
    defaultStep: 1,
    btnId: 'mode-btn-all',
    btnClass: 'bg-brand-emerald text-black'
  }
};

let currentWorkflowMode = 'firewall';

function initWorkflowVisualizer() {
  renderStepNodes();
  switchWorkflowMode('firewall');
  startAutoPlay();
}

function switchWorkflowMode(modeKey) {
  currentWorkflowMode = modeKey;
  const mode = WORKFLOW_MODES[modeKey];
  if (!mode) return;

  // 1. Update Mode Tab Buttons styling
  Object.keys(WORKFLOW_MODES).forEach((key) => {
    const btn = document.getElementById(WORKFLOW_MODES[key].btnId);
    if (btn) {
      if (key === modeKey) {
        btn.className = `mode-tab-btn px-3 py-1.5 rounded-lg text-xs font-mono font-black transition-all border-2 border-black shadow-brutal-sm ${WORKFLOW_MODES[key].btnClass}`;
      } else {
        btn.className = `mode-tab-btn px-3 py-1.5 rounded-lg text-xs font-mono font-black transition-all border-2 border-black bg-white dark:bg-obsidian-950 text-slate-700 dark:text-slate-300 hover:bg-slate-200 dark:hover:bg-obsidian-850`;
      }
    }
  });

  // 2. Filter Packet Streams
  const firewallPackets = document.querySelector('.stream-packet-firewall');
  const autoscanPackets = document.querySelector('.stream-packet-autoscan');
  const slashPackets = document.querySelector('.stream-packet-slash');

  if (firewallPackets) firewallPackets.style.display = (modeKey === 'firewall' || modeKey === 'all') ? 'inline' : 'none';
  if (autoscanPackets) autoscanPackets.style.display = (modeKey === 'autoscan' || modeKey === 'all') ? 'inline' : 'none';
  if (slashPackets) slashPackets.style.display = (modeKey === 'slash' || modeKey === 'all') ? 'inline' : 'none';

  // 3. Filter Node Opacity
  WORKFLOW_STEPS.forEach((s) => {
    const node = document.getElementById(`step-node-${s.step}`);
    if (node) {
      if (mode.activeNodes.includes(String(s.step))) {
        node.style.opacity = "1";
      } else {
        node.style.opacity = "0.35";
      }
    }
  });

  // 4. Select default step for active workflow mode
  selectStep(mode.defaultStep);
}

function renderStepNodes() {
  // Static SVG Node Graph structure is defined in HTML docs/index.html
}

function selectStep(stepKey) {
  currentStep = stepKey;
  const stepData = WORKFLOW_STEPS.find((s) => String(s.step) === String(stepKey));
  if (!stepData) return;

  const modeObj = WORKFLOW_MODES[currentWorkflowMode] || WORKFLOW_MODES.all;

  WORKFLOW_STEPS.forEach((s) => {
    const node = document.getElementById(`step-node-${s.step}`);
    if (node) {
      const rect = node.querySelector('.node-rect');
      const isActiveInMode = modeObj.activeNodes.includes(String(s.step));

      if (String(s.step) === String(stepKey)) {
        node.classList.add("step-node-active");
        node.style.opacity = "1";
        if (rect) {
          rect.setAttribute("stroke-width", "3.5");
          rect.setAttribute("filter", "url(#neon-glow)");
        }
      } else {
        node.classList.remove("step-node-active");
        node.style.opacity = isActiveInMode ? "1" : "0.35";
        if (rect) {
          rect.setAttribute("stroke-width", "1.5");
          rect.removeAttribute("filter");
        }
      }
    }
  });

  const displayBox = document.getElementById("workflow-display-box");
  if (displayBox) {
    displayBox.innerHTML = `
      <div class="flex flex-wrap items-center justify-between gap-3 border-b-2 border-black dark:border-white/20 pb-4 mb-4">
        <div class="flex items-center gap-3">
          <div class="w-10 h-10 rounded-xl bg-black dark:bg-brand-emerald text-white dark:text-obsidian-950 flex items-center justify-center font-bold text-xl border-2 border-black shadow-brutal-sm">
            <i class="ph-bold ${stepData.icon}"></i>
          </div>
          <div>
            <span class="px-2.5 py-0.5 rounded text-[10px] font-mono font-bold uppercase tracking-wider ${stepData.badgeColor}">
              ${stepData.tag}
            </span>
            <h4 class="font-display font-black text-lg text-black dark:text-white leading-tight mt-0.5">
              ${stepData.title}
            </h4>
          </div>
        </div>
        <span class="font-mono text-xs text-slate-700 dark:text-slate-400 font-bold">
          Step ${stepData.step} of 5
        </span>
      </div>
      <p class="text-sm text-slate-800 dark:text-slate-300 font-semibold mb-4">
        ${stepData.description}
      </p>
      <div class="rounded-xl border-2 border-black dark:border-white/20 bg-obsidian-950 p-4 font-mono text-xs text-emerald-400 leading-relaxed overflow-x-auto terminal-scrollbar shadow-inner">
        <pre><code>${escapeHtml(stepData.codeSnippet)}</code></pre>
      </div>
    `;
  }
}

function startAutoPlay() {
  if (autoPlayTimer) clearInterval(autoPlayTimer);
  isAutoPlaying = true;
  updatePlayPauseBtn();
  autoPlayTimer = setInterval(() => {
    let next = currentStep + 1;
    if (next > WORKFLOW_STEPS.length) next = 1;
    selectStep(next);
  }, 4000);
}

function stopAutoPlay() {
  if (autoPlayTimer) clearInterval(autoPlayTimer);
  isAutoPlaying = false;
  updatePlayPauseBtn();
}

function toggleWorkflowAutoPlay() {
  if (isAutoPlaying) {
    stopAutoPlay();
  } else {
    startAutoPlay();
  }
}

function updatePlayPauseBtn() {
  const btn = document.getElementById("workflow-autoplay-btn");
  if (!btn) return;
  btn.innerHTML = isAutoPlaying
    ? '<i class="ph-bold ph-pause text-sm"></i> Pause Flow'
    : '<i class="ph-bold ph-play text-sm"></i> Play Flow Animation';
}

/* --------------------------------------------------------------------------
   4. Live Interactive Firewall Terminal Simulator
   -------------------------------------------------------------------------- */
function simulateCommand(cmd) {
  const input = document.getElementById("cmd-input");
  if (input) input.value = cmd;
  runFirewallLogic(cmd);
}

function handleCustomCommand(e) {
  e.preventDefault();
  const input = document.getElementById("cmd-input");
  if (!input) return;
  const cmd = input.value.trim();
  if (cmd) runFirewallLogic(cmd);
}

function runFirewallLogic(cmd) {
  const outputDiv = document.getElementById("terminal-output");
  if (!outputDiv) return;

  const cleanCmd = cmd.replace(/\^/g, "").replace(/`/g, "");
  const lower = cleanCmd.toLowerCase();

  const isBase64Deny =
    cmd.includes("cm0gLXJmIC8=") ||
    (lower.includes("-enc") && lower.includes("cm0g"));

  let status = "ALLOW";
  let statusClass = "bg-black dark:bg-brand-emerald text-white dark:text-obsidian-950";
  let icon = "ph-check-circle";
  let reason = "Verified clean execution trajectory.";

  const isDeny =
    lower.includes("rm -rf") ||
    lower.includes("format") ||
    lower.includes("clear-disk") ||
    lower.includes("initialize-disk") ||
    lower.includes("remove-partition") ||
    lower.includes("diskutil") ||
    lower.includes("set-mppreference") ||
    lower.includes("add-mppreference") ||
    lower.includes("disable-netfirewallrule") ||
    lower.includes("set-netfirewallprofile") ||
    lower.includes("invoke-command") ||
    lower.includes("enter-pssession") ||
    lower.includes("reg delete") ||
    lower.includes("mkfs") ||
    lower.includes("stop-computer") ||
    lower.includes("restart-computer") ||
    lower.includes("git checkout --") ||
    lower.includes("git restore") ||
    lower.includes("git reset --hard") ||
    isBase64Deny;

  if (isDeny) {
    status = "DENY";
    statusClass = "bg-black dark:bg-rose-500 text-white dark:text-obsidian-950";
    icon = "ph-x-circle";
    if (cmd !== cleanCmd || isBase64Deny) {
      reason =
        "ANTI-BYPASS DENY: Obfuscated/Base64 payload decoded and blocked by Deobfuscation Engine!";
    } else {
      reason =
        "CRITICAL: Destructive system operation blocked by PreCommand Interceptor!";
    }
  } else if (
    lower.includes("remove-item") ||
    lower.includes("--force") ||
    lower.includes("rmdir") ||
    lower.includes("del ")
  ) {
    status = "CONFIRM";
    statusClass = "bg-black dark:bg-amber-500 text-white dark:text-obsidian-950";
    icon = "ph-warning-circle";
    reason =
      "HIGH RISK: Operation alters file state/history. Halting for Y/N user prompt.";
  }

  const timestamp = new Date().toLocaleTimeString();
  const newEntry = document.createElement("div");
  newEntry.className =
    "p-3.5 rounded-xl bg-slate-100 dark:bg-obsidian-900 border-2 border-black dark:border-white/20 space-y-2 shadow-brutal-sm";
  newEntry.innerHTML = `
    <div class="flex items-center justify-between text-xs font-mono font-bold">
      <span class="text-black dark:text-white">$ ${escapeHtml(cmd)}</span>
      <span class="text-[10px] text-slate-700 dark:text-slate-400">${timestamp}</span>
    </div>
    <div class="flex items-center gap-2 font-mono text-xs">
      <span class="inline-flex items-center gap-1.5 px-3 py-0.5 rounded font-bold border border-black dark:border-white/20 ${statusClass}">
        <i class="ph-bold ${icon}" aria-hidden="true"></i> ${status}
      </span>
      <span class="text-black dark:text-slate-200 font-semibold text-xs">${reason}</span>
    </div>
  `;

  outputDiv.appendChild(newEntry);
  outputDiv.parentElement.scrollTop = outputDiv.parentElement.scrollHeight;
}

/* --------------------------------------------------------------------------
   5. 53 SAST Rules Modal & Filtering Engine
   -------------------------------------------------------------------------- */
function openRulesModal(categoryFilter = "ALL") {
  activeCategory = categoryFilter;
  renderCategoryPills();
  renderRules();
  const modal = document.getElementById("rules-modal");
  if (modal) modal.classList.remove("hidden");
  const searchInput = document.getElementById("rule-search");
  if (searchInput) searchInput.focus();
}

function closeRulesModal() {
  const modal = document.getElementById("rules-modal");
  if (modal) modal.classList.add("hidden");
}

function renderCategoryPills() {
  const categories = [
    "ALL",
    "OWASP API 2023",
    "OWASP Web 2021",
    "CWE Top 25",
    "NIST 800-53",
    "Secret Protection",
  ];
  const container = document.getElementById("category-pills");
  if (!container) return;

  container.innerHTML = categories
    .map((cat) => {
      const isSelected = activeCategory === cat;
      const count =
        cat === "ALL"
          ? SAST_RULES.length
          : SAST_RULES.filter((r) => r.category === cat).length;
      const activeClass = isSelected
        ? "bg-black dark:bg-brand-emerald text-white dark:text-obsidian-950 font-bold border-2 border-black dark:border-brand-emerald"
        : "bg-white dark:bg-obsidian-950 text-black dark:text-white font-bold border-2 border-black dark:border-white/20 hover:bg-slate-200 dark:hover:border-brand-emerald";
      return `<button onclick="setCategory('${cat}')" class="px-3 py-1 rounded text-xs transition-all ${activeClass}">${cat} (${count})</button>`;
    })
    .join("");
}

function setCategory(cat) {
  activeCategory = cat;
  renderCategoryPills();
  renderRules();
}

function filterRules() {
  renderRules();
}

function renderRules() {
  const searchElem = document.getElementById("rule-search");
  const query = searchElem ? searchElem.value.toLowerCase().trim() : "";
  const container = document.getElementById("rules-list-container");
  if (!container) return;

  const filtered = SAST_RULES.filter((r) => {
    const matchesCat =
      activeCategory === "ALL" || r.category === activeCategory;
    const matchesQuery =
      !query ||
      r.id.toLowerCase().includes(query) ||
      r.name.toLowerCase().includes(query) ||
      r.desc.toLowerCase().includes(query);
    return matchesCat && matchesQuery;
  });

  const countBadge = document.getElementById("rules-count-badge");
  if (countBadge) {
    countBadge.innerText = `Showing ${filtered.length} of ${SAST_RULES.length} rules`;
  }

  if (filtered.length === 0) {
    container.innerHTML = `<div class="p-8 text-center font-mono font-bold text-xs">No matching rules found.</div>`;
    return;
  }

  container.innerHTML = filtered
    .map((r) => {
      let sevBadgeClass = "bg-black dark:bg-brand-cyan text-white dark:text-obsidian-950";
      if (r.severity === "CRITICAL") {
        sevBadgeClass = "bg-rose-600 dark:bg-rose-500 text-white font-black";
      } else if (r.severity === "HIGH") {
        sevBadgeClass = "bg-amber-500 text-black font-black";
      } else if (r.severity === "MEDIUM") {
        sevBadgeClass = "bg-cyan-500 text-black font-bold";
      } else if (r.severity === "LOW") {
        sevBadgeClass = "bg-slate-300 dark:bg-slate-700 text-black dark:text-white font-bold";
      }
      return `
      <div class="p-4 rounded-xl bg-slate-100 dark:bg-obsidian-900 border-2 border-black dark:border-white/10 space-y-2">
        <div class="flex items-center justify-between">
          <div class="flex items-center gap-3">
            <span class="font-mono font-bold text-white dark:text-obsidian-950 bg-black dark:bg-brand-emerald px-2 py-0.5 rounded text-xs">${r.id}</span>
            <span class="font-display font-black text-black dark:text-white text-base">${r.name}</span>
          </div>
          <span class="text-[10px] font-mono px-2.5 py-0.5 rounded ${sevBadgeClass} uppercase tracking-wider">${r.severity}</span>
        </div>
        <p class="text-xs text-black dark:text-slate-300 font-mono font-semibold">${r.desc}</p>
      </div>
    `;
    })
    .join("");
}

/* --------------------------------------------------------------------------
   6. GitHub Latest Release Fetcher
   -------------------------------------------------------------------------- */
function parseVer(v) {
  return (v || "").replace(/^v/, "").split(".").map(Number);
}

function compareVer(v1, v2) {
  const a = parseVer(v1);
  const b = parseVer(v2);
  for (let i = 0; i < Math.max(a.length, b.length); i++) {
    const numA = a[i] || 0;
    const numB = b[i] || 0;
    if (numA > numB) return 1;
    if (numA < numB) return -1;
  }
  return 0;
}

async function fetchLatestRelease() {
  try {
    const res = await fetch(
      `https://api.github.com/repos/${GITHUB_REPO}/releases/latest`,
      { headers: { Accept: "application/vnd.github.v3+json" } }
    );
    if (!res.ok) throw new Error(`GitHub API ${res.status}`);
    const data = await res.json();
    let tag = data.tag_name || FALLBACK_VERSION;
    if (compareVer(FALLBACK_VERSION, tag) > 0) {
      tag = FALLBACK_VERSION;
    }
    applyVersionToPage(
      tag,
      data.html_url || `https://github.com/${GITHUB_REPO}/releases/tag/${tag}`
    );
  } catch (err) {
    applyVersionToPage(
      FALLBACK_VERSION,
      `https://github.com/${GITHUB_REPO}/releases/tag/${FALLBACK_VERSION}`
    );
  }
}

function applyVersionToPage(tag, releaseUrl) {
  document.querySelectorAll("[data-version-text]").forEach((el) => {
    el.textContent = tag;
  });
  document.querySelectorAll("[data-version-link]").forEach((el) => {
    el.href = releaseUrl;
  });
  document.title = `Security SAST Guard ${tag} — Dual Theme Neo-Brutalist Security Platform`;
}

/* --------------------------------------------------------------------------
   7. Installation Command Tab Switcher & Copy Snippets
   -------------------------------------------------------------------------- */
function switchTab(tab) {
  ["install", "update", "remove"].forEach((t) => {
    const btn = document.getElementById(`tab-${t}`);
    const content = document.getElementById(`content-${t}`);
    if (!btn || !content) return;

    if (t === tab) {
      btn.className =
        "px-4 py-1.5 rounded brutal-btn-alt font-bold uppercase text-xs";
      content.classList.remove("hidden");
    } else {
      btn.className =
        "px-4 py-1.5 rounded text-white hover:underline font-bold text-xs";
      content.classList.add("hidden");
    }
  });
}

function showCopyToast() {
  const toast = document.getElementById("copy-toast");
  if (!toast) return;
  toast.classList.remove("translate-y-4", "opacity-0", "pointer-events-none");
  toast.classList.add("translate-y-0", "opacity-100");

  clearTimeout(window.copyToastTimer);
  window.copyToastTimer = setTimeout(() => {
    toast.classList.remove("translate-y-0", "opacity-100");
    toast.classList.add("translate-y-4", "opacity-0", "pointer-events-none");
  }, 2200);
}

function copySnippet(id) {
  const elem = document.getElementById(id);
  if (!elem) return;
  const button = event.currentTarget;

  navigator.clipboard.writeText(elem.innerText).then(() => {
    const originalLabel = button.innerHTML;
    button.innerHTML = '<i class="ph-bold ph-check"></i> Copied';
    button.classList.add("!bg-brand-emerald", "!text-black");
    showCopyToast();
    setTimeout(() => {
      button.innerHTML = originalLabel;
      button.classList.remove("!bg-brand-emerald", "!text-black");
    }, 1800);
  });
}

function escapeHtml(text) {
  return text
    .replace(/&/g, "&amp;")
    .replace(/</g, "&lt;")
    .replace(/>/g, "&gt;");
}

function initScrollSpy() {
  const sections = [...document.querySelectorAll('[data-nav-section]')]
    .map(link => document.getElementById(link.dataset.navSection))
    .filter(Boolean);
  const links = document.querySelectorAll('[data-nav-section]');
  const observer = new IntersectionObserver((entries) => {
    const visible = entries.filter(entry => entry.isIntersecting)
      .sort((a, b) => b.intersectionRatio - a.intersectionRatio)[0];
    if (!visible) return;
    links.forEach(link => {
      const active = link.dataset.navSection === visible.target.id;
      link.classList.toggle('nav-link-active', active);
      link.setAttribute('aria-current', active ? 'page' : 'false');
    });
  }, { rootMargin: '-18% 0px -62% 0px', threshold: [0.1, 0.35, 0.6] });
  sections.forEach(section => observer.observe(section));
}

/* --------------------------------------------------------------------------
   8. Global Window Event Handler Expositions
   -------------------------------------------------------------------------- */
window.toggleTheme = toggleTheme;
window.selectStep = selectStep;
window.toggleWorkflowAutoPlay = toggleWorkflowAutoPlay;
window.simulateCommand = simulateCommand;
window.handleCustomCommand = handleCustomCommand;
window.openRulesModal = openRulesModal;
window.closeRulesModal = closeRulesModal;
window.setCategory = setCategory;
window.filterRules = filterRules;
window.switchTab = switchTab;
window.copySnippet = copySnippet;
window.showCopyToast = showCopyToast;
window.syncVersionFromGitHub = fetchLatestRelease;
window.initScrollSpy = initScrollSpy;
