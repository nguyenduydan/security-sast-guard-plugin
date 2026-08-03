# User-Centric README & Developer Documentation Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Separate user-facing plugin usage/installation instructions in `README.md` from developer environment setup in `CONTRIBUTING.md`.

**Architecture:** Refactor `README.md` to focus strictly on end-user value, safety guarantees, plugin installation into Antigravity/Gemini CLI, and slash command usage. Move all developer-only dependencies (`pip install pre-commit ruff mypy pytest detect-secrets pylint`) and pre-commit hook setup instructions to `CONTRIBUTING.md`.

**Tech Stack:** Markdown, Git, Python 3.12+, Ruff.

## Global Constraints

- Do not include developer `pip` or `pre-commit` setup steps in `README.md`.
- Keep all user-centric sections: About, What Makes It Essential (Safety, Scan Depth, Value), Slash Commands, Rules Coverage.
- Keep `CONTRIBUTING.md` fully detailed for developers wanting to set up linter, type checks, pytest, and git hooks.
- All linter checks (`ruff check .`) must pass cleanly.

---

### Task 1: Refactor README.md for End Users

**Files:**
- Modify: `README.md`

**Interfaces:**
- Consumes: Design spec from `docs/superpowers/specs/2026-08-03-user-centric-readme-design.md`
- Produces: Clean user-facing `README.md`

- [ ] **Step 1: Update README.md Quick Start section**

Replace the developer setup steps in `README.md` with simple 2-step plugin installation instructions into `C:\Users\<User>\.gemini\config\plugins\security-sast-guard`.

- [ ] **Step 2: Verify Ruff linter passes**

Run: `python -m ruff check .`
Expected: `All checks passed!`

- [ ] **Step 3: Commit README.md changes**

```bash
git add README.md
git commit -m "docs(readme): simplify Quick Start section for end users without dev pip dependencies"
```

---

### Task 2: Enhance CONTRIBUTING.md for Developers

**Files:**
- Modify: `CONTRIBUTING.md`

**Interfaces:**
- Consumes: Complete developer environment setup commands
- Produces: Enhanced `CONTRIBUTING.md`

- [ ] **Step 1: Add full developer setup instructions to CONTRIBUTING.md**

Include `pip install pre-commit ruff mypy pytest detect-secrets pylint`, `pre-commit install`, `pre-commit run --all-files`, and quality gate verification commands in `CONTRIBUTING.md`.

- [ ] **Step 2: Verify Ruff linter passes**

Run: `python -m ruff check .`
Expected: `All checks passed!`

- [ ] **Step 3: Commit CONTRIBUTING.md changes and push to GitHub**

```bash
git add CONTRIBUTING.md
git commit -m "docs(contributing): add complete developer environment setup guide"
git push origin main
```
