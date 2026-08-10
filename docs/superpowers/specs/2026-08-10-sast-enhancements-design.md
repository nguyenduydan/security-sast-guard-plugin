# Security SAST Guard Enhancements - Design Document

## 1. Overview
Enhance the `security-sast-guard` SAST engine inspired by Strix security tools:
- **Remediation Code Snippets (`fix_before` / `fix_after`):** Enrich rules with guidance and render code diff examples in reports.
- **SARIF 2.1.0 Exporter:** Generate standard SARIF reports (`reports/*.sarif`) for GitHub Code Scanning & IDE integrations.
- **Smart Git Diff Base Resolver:** Automatically detect base branch (`origin/main`, `origin/master`, `origin/develop`) for accurate incremental scans.

---

## 2. Architecture & Component Changes

### A. Rule Schema & Markdown Report (`rules/sast_rules.json` & `src/infrastructure/report_generator.py`)
- Add `"remediation"` object to key SAST rules containing `fix_before` and `fix_after` code blocks.
- Update `_build_remediation_summary` in `report_generator.py` to format Remediation Guidance with code snippets.

### B. SARIF 2.1.0 Exporter (`src/infrastructure/report_generator.py`)
- Implement `generate_sarif_report(findings, output_dir, target_path, metadata, audit_level) -> tuple[str, str]`.
- Output schema compliant with OASIS SARIF v2.1.0 specification.

### C. Smart Git Diff Base Resolver (`src/domain/git_helper.py`)
- Implement `GitHelper.get_diff_base(target_dir: Path) -> str`.
- Automatically resolve tracking remote HEAD, `origin/main`, `origin/master`, or fallback to `HEAD`.

---

## 3. Verification Plan
- Unit tests in `tests/test_report_generator.py` for SARIF generation and remediation rendering.
- Unit tests in `tests/test_git_helper.py` for diff base resolution.
- Full quality check: `pylint`, `mypy`, `ruff`, and `pytest`.
