# Implementation Plan: SAST Markdown Report Template & Export Engine

**Date:** 2026-08-05  
**Spec:** [docs/superpowers/specs/2026-08-05-sast-report-template-design.md](file:///D:/AI/tools/security-sast-guard/docs/superpowers/specs/2026-08-05-sast-report-template-design.md)  
**Target Branch:** `feat/sast-report-template`  

---

## Proposed Tasks

### Task 1: Create Branch & Default Report Template File
- Switch to/create branch `feat/sast-report-template`.
- Create `templates/report_template.md` with rich placeholders (`{{DATE}}`, `{{TOTAL_COUNT}}`, `{{FINDINGS_TABLE}}`, `{{REMEDIATION_SUMMARY}}`, etc.).

### Task 2: Implement Template Rendering Engine
- Update `src/infrastructure/report_generator.py`:
  - Load `templates/report_template.md` (or fallback).
  - Substitute placeholders.
  - Return concise 2-3 line summary string with clickable file link.

### Task 3: Update Unit Tests
- Update `tests/test_report_generator.py` to test template loading and placeholder rendering.

### Task 4: Verification & Security Audit
- Run `pytest` to confirm 100% pass rate.
- Run `/sast-audit file src/infrastructure/report_generator.py`.
- Record decision in `.aiops/decisions.jsonl`.
