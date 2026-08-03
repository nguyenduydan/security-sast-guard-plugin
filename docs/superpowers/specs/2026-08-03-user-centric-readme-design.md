# User-Centric README & Developer Documentation Separation Design

**Date:** 2026-08-03  
**Status:** Approved  
**Topic:** User-Centric README & Developer Documentation Separation  

---

## 1. Problem Statement

The current `README.md` file mixes end-user installation instructions with developer-only environment setup commands (`pip install pre-commit ruff mypy pytest detect-secrets pylint`, `pre-commit install`). 

End users who install and use **Security SAST Guard** as an AI extension/plugin do not need developer linting/formatting tools. Including dev dependencies in the user Quick Start section creates unnecessary cognitive friction and confusion.

---

## 2. Target Design

### 2.1. `README.md` (End-User Focused)
- **Scope:** 100% focused on plugin value proposition, safety guarantees, end-user plugin installation, and slash command usage.
- **Key Sections:**
  1. **Banner & Header Badges:** Plugin status, License, Python 3.12+ badge.
  2. **📖 About Security SAST Guard:** Executive summary.
  3. **❓ What Makes It Essential For You?:** 3 Core user benefits (100% Command Firewall Safety, 53 Vulnerability Scan Depth, Core Value proposition).
  4. **🚀 Quick Start (Plugin Installation):** Clean 2-step installation into Antigravity / Gemini CLI (`C:\Users\<User>\.gemini\config\plugins\security-sast-guard`).
  5. **🎮 Slash Commands Reference Table:** `/sast-audit`, `/sast-audit-level`, `/sast-rules`, `/sast-firewall`, `/sast-status`, `/sast-help`.
  6. **📊 SAST Rules Coverage Table:** Summary of OWASP Top 10, OWASP API 2023, CWE Top 25, NIST 800-53 rules.
  7. **🤝 Contributing & Developer Guide:** Redirect link to `CONTRIBUTING.md`.

### 2.2. `CONTRIBUTING.md` (Developer & Contributor Focused)
- **Scope:** Complete guide for developers maintaining or contributing to the codebase.
- **Key Sections:**
  1. **Development Environment Setup:** `pip install pre-commit ruff mypy pytest detect-secrets pylint`.
  2. **Git Pre-Commit Hook Activation:** `pre-commit install` & `pre-commit install --hook-type commit-msg`.
  3. **Local CI Quality Gate Verification:** `ruff check .`, `mypy --config-file=pyproject.toml control_plane.py src/`, `pytest`.
  4. **Conventional Commits Guidelines.**

---

## 3. Implementation Checklist

- [x] Create design doc in `docs/superpowers/specs/2026-08-03-user-centric-readme-design.md`.
- [ ] Update `README.md` with clean end-user installation guide.
- [ ] Update `CONTRIBUTING.md` with complete developer pip & pre-commit setup instructions.
- [ ] Verify `ruff check .` passes with zero errors.
- [ ] Commit and push to GitHub `main`.
