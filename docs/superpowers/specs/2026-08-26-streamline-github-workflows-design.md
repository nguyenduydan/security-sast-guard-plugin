# Streamline & Minimalize GitHub Workflows Design Spec

**Date:** 2026-08-26  
**Status:** Approved (Approach 2: Extreme Minimalist - Ponytail Ultra)  
**Author:** AI Agent (Antigravity 2.0)  

---

## 1. Context & Motivation
The `.github/workflows/` directory currently contains 10 workflow files and 1 composite action. Many workflows are thin wrappers calling `reusable-*.yml` files. This introduces:
- Excess runner scheduling latency and cold starts.
- Log fragmentation across multiple child workflow runs.
- Duplicate SAST analysis between GitHub CodeQL and native `security-sast-guard`.
- Unnecessary cron jobs (`stale.yml`).

## 2. Target Architecture (Extreme Minimalist)
Reduce 10 workflow files to **5 essential, self-contained workflow files**:

| Workflow File | Trigger | Purpose |
| :--- | :--- | :--- |
| `ci.yml` | `push` / `pull_request` (ignoring `*.md`, `docs/**`) | Consolidated parallel jobs: `quality-gate`, `security-gate`, `cross-platform-tests`. |
| `release.yml` | `push` to `main` & `v*` tags | Consolidated `release-please` and `release-package-sbom` without reusable workflow dependencies. |
| `dependabot-auto-merge.yml` | `pull_request` by `dependabot[bot]` | Automatically approves and enables rebase auto-merge for minor & patch updates. |
| `wiki-sync.yml` | `push` to `main` (`docs/wiki/**`) | Syncs markdown files in `docs/wiki/` to GitHub Wiki. |
| `labeler.yml` | `pull_request_target` | Auto-labels PRs based on changed paths. |

### Deleted Redundant Files:
1. `.github/workflows/reusable-quality-gate.yml` (Inlined into `ci.yml`)
2. `.github/workflows/reusable-security-gate.yml` (Inlined into `ci.yml` & `release.yml`)
3. `.github/workflows/reusable-release-sbom.yml` (Inlined into `release.yml`)
4. `.github/workflows/codeql.yml` (Redundant with native SAST Guard SARIF scanning)
5. `.github/workflows/stale.yml` (Eliminates noisy cron job)

---

## 3. Detailed Specifications

### 3.1 `ci.yml`
- **Concurrency:** Cancel in-progress runs for same ref.
- **Paths Ignore:** `**.md`, `docs/**`, `.gitignore`, `LICENSE`.
- **Jobs:**
  - `quality-gate`: Runs on `ubuntu-latest`, executes manifest check, ruff check/format, pylint (10/10 gate), mypy, and pytest.
  - `security-gate`: Runs on `ubuntu-latest`, executes `detect-secrets-hook`, `python control_plane.py audit codebase --level full --sarif results.sarif`, uploads SARIF artifact, and uploads to GitHub Code Scanning via `github/codeql-action/upload-sarif@v4`.
  - `cross-platform-tests`: Runs pytest on `windows-latest` and `macos-latest`.

### 3.2 `release.yml`
- **Triggers:** `push` on `main` and `v*` tags.
- **Jobs:**
  - `security-gate`: Full SAST codebase audit before releasing.
  - `release-please`: Evaluates conventional commits and manages release PRs.
  - `release-package-sbom`: Runs on `v*` tags, packages `.zip`, generates SHA-256 checksums, anchore SBOM (SPDX), attestation provenance, and creates GitHub Release via `softprops/action-gh-release@v2`.

---

## 4. Verification & Quality Gates
1. Run local Quality Gate:
   ```bash
   python -m ruff check .
   python -m ruff format --check .
   python -m pylint control_plane.py src/
   python -m mypy --config-file=pyproject.toml control_plane.py src/
   python -m pytest
   ```
2. Scan modified workflows via SAST Guard (`sast_scan_file`).
3. Verify YAML syntax and consistency of remaining workflow files.
