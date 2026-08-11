# SAST False Positives Fix

This plan details the implementation to fix the false positives in the SAST scanner as requested.

## Goal Description
Fix three major sources of false positives in the SAST scanner (which currently account for about 86% of noise in Ultra mode):
1. **Assembly Token Misidentification**: `publicKeyToken` in `Web.config` is being flagged as `PLAINTEXT_SECRET`.
2. **Project File False Positives**: `packages.config` and `<DependentUpon>` inside `.csproj` and `.config` files are being flagged incorrectly.
3. **Third-Party Libraries**: Open-source libraries in `Styles/plugins/` (like `d3v3.js`, `flatpickr.js`) are being scanned.

## Proposed Changes

### `rules/sast_rules.json`
Update the regex pattern for `PLAINTEXT_SECRET` to ignore `publicKeyToken`.
- **Action**: Modify the pattern `(?i)(api_key|secret|token|password|passwd|private_key|auth_token)\s*[:=]\s*['"][a-zA-Z0-9_\-]{8,}['"]` to explicitly exclude `publicKeyToken` using a negative lookbehind `(?<!publicKey)` or by enforcing word boundaries for `token`.

### `src/domain/ignore_filter.py`
Exclude `.csproj` and `.config` files, and ignore the `plugins` directory.
- **Action**: Add `.csproj` to `DEFAULT_IGNORE_EXTS`.
- **Action**: Add `plugins` to `DEFAULT_IGNORE_DIRS`. 

## Verification Plan

### Automated Tests
- Run `pytest` to ensure all existing tests pass.
- Write or update tests in `tests/test_ignore_filter.py` to verify `.csproj` and `plugins` are ignored.
- Write or update tests in `tests/test_sast.py` to verify `publicKeyToken` doesn't trigger `PLAINTEXT_SECRET`.

### Linter & Security Check
- Run `python -m pylint src tests`
- Run `python -m ruff check .`
- Run `python -m ruff format --check .`
- Run `/sast-audit file <modified files>`
