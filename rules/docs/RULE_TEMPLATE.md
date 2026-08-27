# CUSTOM_RULE_TEMPLATE — My Custom Security Rule

## Description
Brief description of the security vulnerability detected by this rule.
Example: Detects usage of the `eval()` function with untrusted user input, presenting a Remote Code Execution (RCE) risk.

## Severity
High

<!-- Valid severity levels: Critical | High | Medium | Low | Info -->

## Category
Specify an appropriate category: owasp-api-2023 | owasp-web-2021 | web-app-specific | cwe-sans-top25 | nist-800-53

## Patterns

Add regular expression patterns to detect the vulnerability. One pattern per line:

```regex
# Detect eval() with dynamic variables
eval\s*\(\s*[a-zA-Z_$][a-zA-Z0-9_$]*

# Detect exec() with unvalidated input
exec\s*\(\s*request\.(GET|POST|params)
```

## References
- OWASP: https://owasp.org/
- CWE: https://cwe.mitre.org/

---
<!-- After creating your rule, compile it to JSON by running:
     /sast-rules add <path/to/MY_RULE.md>
-->
