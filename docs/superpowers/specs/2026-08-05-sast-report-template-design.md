# Specification: SAST Markdown Report Template & Export Engine

**Date:** 2026-08-05  
**Project:** Security SAST Guard Plugin  
**Status:** Approved  
**Author:** AI Security Supervisor Architect  

---

## 1. Overview & Objectives

When a SAST security scan completes and detects vulnerabilities, outputting a long wall of text in the console response is noisy and difficult to read. This specification defines a dedicated **Markdown Report Template System** for the Security SAST Guard Plugin.

### Core Objectives:
1. **Template Engine:** Provide a default, customizable Markdown report template at `templates/report_template.md` with rich placeholders.
2. **Concise CLI Handoff:** Keep terminal/chat output limited to a 2-3 line executive summary with a clickable `file://` link to the generated `.md` report.
3. **Structured Report Layout:** Include OWASP risk mapping, code snippets, file location, remediation guidelines, and severity breakdown table in the template output.

---

## 2. Architecture & Template Format

### Template File Location: `templates/report_template.md`

#### Supported Placeholders:
- `{{DATE}}`: Audit execution timestamp.
- `{{TARGET_PATH}}`: Path of scanned code/file.
- `{{TOTAL_COUNT}}`: Total vulnerability findings.
- `{{CRITICAL_COUNT}}`: Count of Critical severity findings.
- `{{HIGH_COUNT}}`: Count of High severity findings.
- `{{MEDIUM_COUNT}}`: Count of Medium severity findings.
- `{{LOW_COUNT}}`: Count of Low severity findings.
- `{{FINDINGS_TABLE}}`: Formatted Markdown table containing rule ID, location, severity, code snippet, and scope.
- `{{REMEDIATION_SUMMARY}}`: Executive security action items and OWASP remediation guidelines.

---

## 3. Implementation Details

1. **Default Template Creation (`templates/report_template.md`)**:
   - Create a clean, professional security report template featuring visual alerts, severity badges, and structured tables.

2. **Template Loader & Renderer (`src/infrastructure/report_generator.py`)**:
   - Read template file from `templates/report_template.md` (or fallback to built-in template string if template file is missing).
   - Substitute placeholders dynamically.
   - Write output to `reports/sast_audit_report_<timestamp>.md`.
   - Return (report_path, summary_str) where `summary_str` is concise (2-3 lines).

3. **Unit Tests (`tests/test_report_generator.py`)**:
   - Verify template loading, placeholder replacement, and markdown file creation when findings exist vs clean scan.

---

## 4. Verification Plan

1. Run `pytest` test suite to verify 100% pass rate.
2. Run `/sast-audit file templates/report_template.md` to verify security safety.
