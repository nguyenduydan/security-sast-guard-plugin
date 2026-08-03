# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [1.1.0-rc.1] - 2026-08-03

### Added
- Integrated 53 new security rules covering OWASP Top 10, OWASP API 2023, CWE-SANS Top 25, and NIST 800-53.
- Implemented enterprise-grade 14-step Pre-Commit pipeline configuration (`.pre-commit-config.yaml`, `pyproject.toml`).
- Added secret detection baseline via `detect-secrets`.
- Added Conventional Commits validation for commit messages.

### Changed
- Refactored `sast-audit-level` skill to operate seamlessly in AI memory context without altering local config files.
- Refactored `sast-audit` skill to automatically run codebase/large audits as silent background tasks.
- Refactored `sast-rules` skill for token-efficient background execution.

### Fixed
- Fixed command prompt transparency by suppressing raw Python command execution in chat UI.
