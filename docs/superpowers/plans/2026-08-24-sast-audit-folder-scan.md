# Implementation Plan - Folder Scanning Support for SAST Audit

**Date:** 2026-08-24
**Author:** Antigravity / DeepMind

## Goal
Add dedicated folder/directory scanning logic to `/sast-audit` skill and the CLI dispatcher `sast audit folder <path>`.

## Proposed Changes
1. `src/cli/dispatcher.py`: Parse `folder`, `dir`, `directory` sub-arguments gracefully in `sast audit [folder] [path]`.
2. `skills/sast-audit/SKILL.md` (and plugin installation): Add `folder` option to Grill UI modal and description.
3. `tests/test_cli.py`: Add unit test covering `sast audit folder <path>` invocation.
4. `README.md`: Update documentation table to reflect `folder` support in `/sast-audit`.

## Verification
- `pytest tests/test_cli.py`
- Full CI Quality Gate (`ruff`, `pylint`, `mypy`, `pytest`).
