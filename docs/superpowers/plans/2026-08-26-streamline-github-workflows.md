# Streamline GitHub Workflows Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Consolidate and streamline GitHub CI/CD workflows into 5 self-contained, minimal files, removing 5 redundant/wrapper workflows.

**Architecture:** Inline reusable quality, security, and release steps directly into `ci.yml` and `release.yml`, remove obsolete wrapper files (`reusable-*.yml`), redundant CodeQL scan (`codeql.yml`), and unnecessary cron stale bot (`stale.yml`).

**Tech Stack:** GitHub Actions, Python 3.12, Pytest, Ruff, Mypy, Pylint, SAST Guard SARIF integration.

**Spec:** `docs/superpowers/specs/2026-08-26-streamline-github-workflows-design.md`

## Global Constraints
- Do not commit directly to `main`.
- Maintain 100% CI Quality Gate score (Ruff, Pylint 10/10, Mypy, 349+ Pytest tests green).
- Maintain conventional commit conventions (`ci(workflows): ...`).

---

### Task 1: Consolidate `ci.yml` with Inlined Quality, Security, and Cross-Platform Jobs

**Files:**
- Modify: `.github/workflows/ci.yml`

**Interfaces:**
- Consumes: `.github/actions/setup-env/action.yml`, `control_plane.py audit codebase`
- Produces: GitHub Action jobs `quality-gate`, `security-gate`, `cross-platform-tests`, and GitHub Code Scanning SARIF alert integration.

- [ ] **Step 1: Write inlined `ci.yml` with parallel quality, security, and cross-platform jobs**
- [ ] **Step 2: Scan `ci.yml` with SAST Guard scanner (`sast_scan_file`)**
- [ ] **Step 3: Run CI Quality Gate locally to confirm compatibility**

---

### Task 2: Consolidate `release.yml` with Inlined Security, Release Please, and SBOM/Release Packaging

**Files:**
- Modify: `.github/workflows/release.yml`

**Interfaces:**
- Consumes: `.github/actions/setup-env/action.yml`, `release-please-config.json`, `.release-please-manifest.json`
- Produces: GitHub Releases, SBOM SPDX assets, signed provenance attestations.

- [ ] **Step 1: Write inlined `release.yml` removing reusable workflow references**
- [ ] **Step 2: Scan `release.yml` with SAST Guard scanner (`sast_scan_file`)**
- [ ] **Step 3: Run CI Quality Gate locally**

---

### Task 3: Remove Redundant Workflows & Run Full Verification

**Files:**
- Delete: `.github/workflows/reusable-quality-gate.yml`
- Delete: `.github/workflows/reusable-security-gate.yml`
- Delete: `.github/workflows/reusable-release-sbom.yml`
- Delete: `.github/workflows/codeql.yml`
- Delete: `.github/workflows/stale.yml`

- [ ] **Step 1: Delete the 5 redundant workflow files**
- [ ] **Step 2: Run full CI test suite and quality gates (Ruff, Pylint, Mypy, Pytest)**
- [ ] **Step 3: Commit and push changes to branch**
