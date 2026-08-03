# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [0.1.0](https://github.com/nguyenduydan/security-sast-guard-plugin/compare/security-sast-guard-v0.0.1...security-sast-guard-v0.1.0) (2026-08-03)


### 🚀 Features & SAST Security Rules

* add packaging scripts (install, update, remove) ([#4](https://github.com/nguyenduydan/security-sast-guard-plugin/issues/4)) ([ea2307d](https://github.com/nguyenduydan/security-sast-guard-plugin/commit/ea2307dfb016bea84823054e8689eca63ebb0030))
* Add SAST Guard plugin source, refactored skills, and 53 OWASP/CWE rules ([28f363b](https://github.com/nguyenduydan/security-sast-guard-plugin/commit/28f363b55ad1950694c853cd2d99de55ebc921e8))
* Create SECURITY.md for security policy ([4aafac5](https://github.com/nguyenduydan/security-sast-guard-plugin/commit/4aafac5eae40ab978b54e3f4bc8af3a3deddbd8d))
* Lazy SAST Audit Architecture ([#3](https://github.com/nguyenduydan/security-sast-guard-plugin/issues/3)) ([1d6cf70](https://github.com/nguyenduydan/security-sast-guard-plugin/commit/1d6cf707ce6030b334ad010009694f7a01aefc5e))
* **lint:** Add Pylint CI workflow for Python code quality ([ec50152](https://github.com/nguyenduydan/security-sast-guard-plugin/commit/ec5015213928b97fbc0e2e3a07c62c767ac9a71d))
* **release:** set initial project version to v0.0.1 ([45c5898](https://github.com/nguyenduydan/security-sast-guard-plugin/commit/45c58980875d6c4084cd9d72dc24a5df09b0d42a))


### 🐛 Bug Fixes

* **ci:** optimize python module calls in ci.yml and release.yml ([1851a33](https://github.com/nguyenduydan/security-sast-guard-plugin/commit/1851a33e1962e3da7737e16a1cbd6ca703ddb00c))
* **ci:** resolve pylint workflow failure and code quality issues ([e601449](https://github.com/nguyenduydan/security-sast-guard-plugin/commit/e60144950686d99aa0aa5d7e43d98b82003ecb03))
* **types:** resolve mypy type annotation errors and ruff imports ([4e71f43](https://github.com/nguyenduydan/security-sast-guard-plugin/commit/4e71f43efcc4667119d10e70b942737590675d06))


### ⚙️ Build System & Dependencies

* **ci:** add pre-commit pipeline configuration and tools setup ([04cc5e5](https://github.com/nguyenduydan/security-sast-guard-plugin/commit/04cc5e5bf90f84cb695434f3be0f241b3e770bf3))


### ⚙️ CI/CD Workflows

* **release:** add automated GitHub Release workflow on tag push ([9a7431d](https://github.com/nguyenduydan/security-sast-guard-plugin/commit/9a7431ddff73d19d01e487cb6a46150e55bae1d4))
* **release:** add bot author config and secret token fallback ([08cc30d](https://github.com/nguyenduydan/security-sast-guard-plugin/commit/08cc30d1d61e1db74e06472d66de2a7bfaf7a5e0))
* **release:** add release-please config and manifest for GitHub Release standards ([ab52714](https://github.com/nguyenduydan/security-sast-guard-plugin/commit/ab527140b246f0f9ac7d7443bc50fb39e229ecf9))
* **release:** adopt Release Please action and CI Quality Gate pipeline ([ec98c0f](https://github.com/nguyenduydan/security-sast-guard-plugin/commit/ec98c0f36e5d22a6d54415992ef532c30d906356))
* **release:** improve release notes resolution logic in release workflow ([6709ff7](https://github.com/nguyenduydan/security-sast-guard-plugin/commit/6709ff70d989d3bf7762330a0bce28b26ebef285))
* **release:** integrate gh-release action to auto-publish release notes on tag push ([b260985](https://github.com/nguyenduydan/security-sast-guard-plugin/commit/b2609859b3b394964f909ef8fb72862109d4151b))
* **release:** remove invalid package-name input from release workflow ([b78b2df](https://github.com/nguyenduydan/security-sast-guard-plugin/commit/b78b2df3b799d71ea701af0073c46e431c126fdb))
* **release:** set git author identity to fogvn &lt;dn135897@gmail.com&gt; ([acbb634](https://github.com/nguyenduydan/security-sast-guard-plugin/commit/acbb634d365d126ee65d0fe54e5c9c26745b7792))


### 📚 Documentation

* **readme:** add About Security SAST Guard section ([405bab6](https://github.com/nguyenduydan/security-sast-guard-plugin/commit/405bab6dcb432fdfe190a470ae8e752c3590c6dc))
* **readme:** add value proposition comparison table between native permissions and SAST guard ([074e560](https://github.com/nguyenduydan/security-sast-guard-plugin/commit/074e560414086a31acbc6a5924bfd40fb2a3e32d))
* **readme:** rewrite README.md with modern enterprise design, mermaid diagram, badges, and slash commands reference ([3e30f25](https://github.com/nguyenduydan/security-sast-guard-plugin/commit/3e30f255a5f86fc3c90d70e7cfcf4d6c12ca2db1))
* **readme:** structure user-centric value proposition answering safety, scan depth, and core benefits ([bdbaa30](https://github.com/nguyenduydan/security-sast-guard-plugin/commit/bdbaa300fa3ada3814ec554d8274bd9af51f653c))
* **release:** add release notes for v1.1.0-beta.1 ([15347b5](https://github.com/nguyenduydan/security-sast-guard-plugin/commit/15347b5d8d9f217995c2fd7a696a49a76e5e8087))
* **release:** add release report v1.1.0-rc.1 and changelog ([6f7568f](https://github.com/nguyenduydan/security-sast-guard-plugin/commit/6f7568fe666021e7b845977d209271cc138219d9))
* **release:** add RELEASE_GUIDE.md and simplify release title format to v0.0.1 ([278f4a8](https://github.com/nguyenduydan/security-sast-guard-plugin/commit/278f4a83461ded3a1fefdd4cbaf73543e01387cd))
* separate end-user plugin installation in README from developer setup in CONTRIBUTING.md ([9538f1a](https://github.com/nguyenduydan/security-sast-guard-plugin/commit/9538f1a88b0bb87772a30255759416240254a218))
* **spec:** add design spec for user-centric README separation ([954e214](https://github.com/nguyenduydan/security-sast-guard-plugin/commit/954e21413a60ee1724af1fcbe9ca8cde2f1e15e5))
* **workflow:** mandate feature branch and pull request merge workflow ([#2](https://github.com/nguyenduydan/security-sast-guard-plugin/issues/2)) ([66034a1](https://github.com/nguyenduydan/security-sast-guard-plugin/commit/66034a11681316a7b6c0071632af748bd132cd66))


### 🎨 Code Style & Formatting

* **imports:** fix import sorting and code formatting via ruff ([0c7040b](https://github.com/nguyenduydan/security-sast-guard-plugin/commit/0c7040b0b045ac33daa141b773bd712dc00eb312))

## [1.1.0-beta.1] - 2026-08-03

### Added
- Integrated 53 new security rules covering OWASP Top 10, OWASP API 2023, CWE-SANS Top 25, and NIST 800-53.
- Implemented enterprise-grade 14-step Pre-Commit pipeline configuration (`.pre-commit-config.yaml`, `pyproject.toml`).
- Added secret detection baseline via `detect-secrets`.
- Added Conventional Commits validation for commit messages.
- Automated GitHub Release generation on tag push (`v*`).

### Changed
- Refactored `sast-audit-level` skill to operate seamlessly in AI memory context without altering local config files.
- Refactored `sast-audit` skill to automatically run codebase/large audits as silent background tasks.
- Refactored `sast-rules` skill for token-efficient background execution.

### Fixed
- Fixed command prompt transparency by suppressing raw Python command execution in chat UI.
- Resolved Mypy type annotations and Ruff import sorting errors for 100% CI Quality Gate pass.
