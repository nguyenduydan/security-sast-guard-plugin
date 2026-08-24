# CUSTOM_01_UNSAFE_INLINE_EVAL

## Rule Metadata
- **ID:** `CUSTOM-01-UNSAFE-EVAL`
- **Severity:** `HIGH`
- **Confidence:** `HIGH`
- **CWE:** `CWE-95`
- **OWASP:** `A03:2021-Injection`
- **Category:** `Code Injection`
- **Message:** `Detected dangerous dynamic code evaluation via eval() or Function constructor.`
- **Remediation:** `Avoid dynamic code evaluation. Use structured JSON parsing (JSON.parse) or static lookups.`

## Patterns
- `eval\s*\(`
- `new\s+Function\s*\(`
- `setTimeout\s*\(\s*["'`]``
- `setInterval\s*\(\s*["'`]``

## Sinks
- `eval`
- `Function`

## Sanitizers
- `JSON.parse`
- `safeEval`
