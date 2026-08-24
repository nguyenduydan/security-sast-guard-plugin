# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [2.7.2](https://github.com/nguyenduydan/security-sast-guard-plugin/compare/v2.7.1...v2.7.2) (2026-08-24)


### 📝 Documentation

* **wiki:** add enterprise project wiki and auto-sync workflow ([10d32e4](https://github.com/nguyenduydan/security-sast-guard-plugin/commit/10d32e49431c0b1ff6b8bd4f1983063b1536fd80))
* **wiki:** remove _Sidebar.md from wiki docs ([43f4ffb](https://github.com/nguyenduydan/security-sast-guard-plugin/commit/43f4ffbd6b3dc392483ed2b95b0d15aca9a5578c))

## [2.7.1](https://github.com/nguyenduydan/security-sast-guard-plugin/compare/v2.7.0...v2.7.1) (2026-08-24)


### Maintenance & Tooling

* update banner ([e522d9d](https://github.com/nguyenduydan/security-sast-guard-plugin/commit/e522d9d6b30c871cbe7b70e5313ed13deda48d72))

## [2.7.0](https://github.com/nguyenduydan/security-sast-guard-plugin/compare/v2.6.0...v2.7.0) (2026-08-24)


### 🚀 Features & SAST Security Rules

* **scanner:** integrate Shannon entropy and token signature secret detector into SAST audit ([42c5adf](https://github.com/nguyenduydan/security-sast-guard-plugin/commit/42c5adf7b9faadc7871cab99ca6a1060640a6100))


### 🐛 Bug Fixes

* **tests:** add detect-secrets allowlist pragma and resolve line length in entropy tests ([adce59c](https://github.com/nguyenduydan/security-sast-guard-plugin/commit/adce59cdadd7279c2a74c9924f35f2dc1578ac98))
* **tests:** chunk mock token fixtures to resolve detect-secrets false alarms ([e74be76](https://github.com/nguyenduydan/security-sast-guard-plugin/commit/e74be76e931fef8bea3ac706ab9ea33f31938c8b))

## [2.6.0](https://github.com/nguyenduydan/security-sast-guard-plugin/compare/v2.5.0...v2.6.0) (2026-08-24)


### 🚀 Features & SAST Security Rules

* **audit:** support folder scanning in sast-audit and CLI dispatcher ([9b2a1a0](https://github.com/nguyenduydan/security-sast-guard-plugin/commit/9b2a1a02b52d1085f6fe412b67a1d4136685344e))


### 🐛 Bug Fixes

* **ci:** update labeler configuration to actions/labeler v5 schema ([8e05ee6](https://github.com/nguyenduydan/security-sast-guard-plugin/commit/8e05ee65ade9e2dc90ea9d454f51def2fb4faf9e))

## [2.5.0](https://github.com/nguyenduydan/security-sast-guard-plugin/compare/v2.4.2...v2.5.0) (2026-08-24)


### 🚀 Features & SAST Security Rules

* **ast:** modernize tree-sitter Parser API and add mock AST unit tests for ASTConfirmEngine (Fixes [#193](https://github.com/nguyenduydan/security-sast-guard-plugin/issues/193)) ([4c7d167](https://github.com/nguyenduydan/security-sast-guard-plugin/commit/4c7d167b14f19e1d70b39085ce6455990c99255b))
* **ci:** add multi-OS CI matrix and cross-platform tests for firewall hooks (Fixes [#185](https://github.com/nguyenduydan/security-sast-guard-plugin/issues/185)) ([ee64c4f](https://github.com/nguyenduydan/security-sast-guard-plugin/commit/ee64c4f505400e396f33504266acfb4ebab93cb3))
* **devex:** enhance repository with Makefile, Code of Conduct, Architecture & Threat Model docs, examples, and GitHub automations ([bc0252e](https://github.com/nguyenduydan/security-sast-guard-plugin/commit/bc0252e8ac01909b6939cf542e647cadfc0de268))
* **ignore:** add AI agent directories (.agents, .gemini, .antigravity, .cursor, .claude, etc.) to blacklist and default ignore list ([70c45d7](https://github.com/nguyenduydan/security-sast-guard-plugin/commit/70c45d7735c553bf7f43e154a2345df068795673))
* **install:** add POSIX shell installation and management scripts (install.sh, update.sh, remove.sh) (Fixes [#197](https://github.com/nguyenduydan/security-sast-guard-plugin/issues/197)) ([8a4d279](https://github.com/nguyenduydan/security-sast-guard-plugin/commit/8a4d279fb07dc71dd4c6b94a9c5287e9a6e07efd))
* **mcp:** implement real rule synchronization in sast_sync_rules MCP tool handler (Fixes [#200](https://github.com/nguyenduydan/security-sast-guard-plugin/issues/200)) ([d0913f8](https://github.com/nguyenduydan/security-sast-guard-plugin/commit/d0913f81879e464c967512ffb71f0038de8d8e31))
* **mcp:** support optional output_file parameter in handle_sast_sync_rules ([985776b](https://github.com/nguyenduydan/security-sast-guard-plugin/commit/985776b22f35fed8d47abe2566320a7c7ecea4dc))
* **reports:** add JSON report format support in CLI and unit tests for generate_json_report (Fixes [#202](https://github.com/nguyenduydan/security-sast-guard-plugin/issues/202)) ([8ca7540](https://github.com/nguyenduydan/security-sast-guard-plugin/commit/8ca7540fd93871c5c47e881b39f6e253f23d54e1))
* **scanner:** support standalone blacklist.json for custom scan exclusions ([b8f9e73](https://github.com/nguyenduydan/security-sast-guard-plugin/commit/b8f9e7321a4d1c2d9529561cac4419d5f312d0c8))


### 🐛 Bug Fixes

* **ci:** align CI matrix python version with pyproject requires-python 3.12+ ([a31aa0e](https://github.com/nguyenduydan/security-sast-guard-plugin/commit/a31aa0e9c7c0ddb6f747d6282fe10f6cfd641d26))
* **cli:** fix unconditional verbose mode in CLI dispatcher (Fixes [#189](https://github.com/nguyenduydan/security-sast-guard-plugin/issues/189)) ([d790cc4](https://github.com/nguyenduydan/security-sast-guard-plugin/commit/d790cc4eef79ad6f87f4c3255d65be6d7b29b1af))
* **firewall:** support Linux POSIX octal escape sequences in FirewallNormalizer (Fixes [#186](https://github.com/nguyenduydan/security-sast-guard-plugin/issues/186)) ([3e200a2](https://github.com/nguyenduydan/security-sast-guard-plugin/commit/3e200a24f4d2d12a8d66f642a4ba3d01ee1c70e1))
* **metrics:** resolve Windows and POSIX path format mismatch in SecurityMetricsEngine (Fixes [#190](https://github.com/nguyenduydan/security-sast-guard-plugin/issues/190)) ([9645b6b](https://github.com/nguyenduydan/security-sast-guard-plugin/commit/9645b6ba30d2b0b2763214b1e25f045e89d4d500))
* **rules:** correct copy-pasted SQL sinks in PROMPT_INJECTION_VULNERABLE rule (Fixes [#188](https://github.com/nguyenduydan/security-sast-guard-plugin/issues/188)) ([2634907](https://github.com/nguyenduydan/security-sast-guard-plugin/commit/26349075517e1e5b5d6df99f1f227f186777fcc9))
* **scanner:** add explanatory comment to empty except clause in IgnoreFilter ([28640fa](https://github.com/nguyenduydan/security-sast-guard-plugin/commit/28640fa2b596eb63c6c3262f132b6fef4c353a8e))
* **scanner:** integrate ContextExtractor and AIVerifier into SASTScanner.scan_code (Fixes [#192](https://github.com/nguyenduydan/security-sast-guard-plugin/issues/192)) ([ddb152a](https://github.com/nguyenduydan/security-sast-guard-plugin/commit/ddb152ac0c75e7f5ee78ddca89af61d418e91879))
* **scanner:** prevent workspace path pollution in run_audit_v2 writing logs to plugin directory (Fixes [#191](https://github.com/nguyenduydan/security-sast-guard-plugin/issues/191)) ([026c670](https://github.com/nguyenduydan/security-sast-guard-plugin/commit/026c67072e2e0288606d9577e2cd09ec482616a7))
* **scripts:** remove hardcoded local machine Windows path in scripts/md_to_json.py (Fixes [#184](https://github.com/nguyenduydan/security-sast-guard-plugin/issues/184)) ([6346cf7](https://github.com/nguyenduydan/security-sast-guard-plugin/commit/6346cf735d35b53fe284518fae22b9b8b37a5825))
* **taint:** enhance SymbolIndexer regex to support typed and multi-language variable declarations (Fixes [#187](https://github.com/nguyenduydan/security-sast-guard-plugin/issues/187)) ([0602e41](https://github.com/nguyenduydan/security-sast-guard-plugin/commit/0602e41bb21b4ca07441d7bae607b3a2016b21d3))


### ♻️ Refactoring & Code Hygiene

* **ci:** adopt setup-env composite action across GitHub Actions workflows (Fixes [#196](https://github.com/nguyenduydan/security-sast-guard-plugin/issues/196)) ([5d19931](https://github.com/nguyenduydan/security-sast-guard-plugin/commit/5d199315eecc5c177216b10a0e8291bccf574885))
* **ci:** streamline CI/CD pipeline and consolidate redundant runner jobs ([ee03497](https://github.com/nguyenduydan/security-sast-guard-plugin/commit/ee0349790e7b7b24d15916ec3f0af02b3466e09c))
* **hooks:** standardize output formatting and exit codes between firewall_hook.ps1 and firewall_hook.py (Fixes [#198](https://github.com/nguyenduydan/security-sast-guard-plugin/issues/198)) ([ff96b66](https://github.com/nguyenduydan/security-sast-guard-plugin/commit/ff96b6615024fe17a56dfbcfe7c01c416421fbc1))
* **rules:** filter out empty pattern stubs in sast_rules.json during rule sync (Fixes [#199](https://github.com/nguyenduydan/security-sast-guard-plugin/issues/199)) ([011c07c](https://github.com/nguyenduydan/security-sast-guard-plugin/commit/011c07c645aa5821aa51484905cb3f57e37d85e5))


### 📝 Documentation

* **plugin:** synchronize complete list of 8 skills in plugin.json (Fixes [#194](https://github.com/nguyenduydan/security-sast-guard-plugin/issues/194)) ([b1b1e1a](https://github.com/nguyenduydan/security-sast-guard-plugin/commit/b1b1e1aff25e93d3c022029b23a7915b0acdead7))
* remove hardcoded version and synchronize documentation for POSIX scripts, blacklist.json, and CLI options ([914b271](https://github.com/nguyenduydan/security-sast-guard-plugin/commit/914b27127ea37ace7c282c28c10956652585dca7))


### Maintenance & Tooling

* **release:** replace hardcoded personal git author identity in release SBOM workflow (Fixes [#195](https://github.com/nguyenduydan/security-sast-guard-plugin/issues/195)) ([c715953](https://github.com/nguyenduydan/security-sast-guard-plugin/commit/c715953d7693b8a8b5225c630498ecf8b489b987))

## [2.4.2](https://github.com/nguyenduydan/security-sast-guard-plugin/compare/v2.4.1...v2.4.2) (2026-08-21)


### 📝 Documentation

* synchronize README and MCP integration guide with 95 SAST rules and 12 MCP tools ([3181cb4](https://github.com/nguyenduydan/security-sast-guard-plugin/commit/3181cb47dac313e57a14d94dc4917b3478484eb6))

## [2.4.1](https://github.com/nguyenduydan/security-sast-guard-plugin/compare/v2.4.0...v2.4.1) (2026-08-21)


### 🐛 Bug Fixes

* **rules:** prevent false positive prompt injection findings on internal f-strings ([9e1b5de](https://github.com/nguyenduydan/security-sast-guard-plugin/commit/9e1b5de1c81446c96df58b58d5360821cf6d0228))
* **rules:** prevent false positive prompt injection findings on internal f-strings ([2a6dc8a](https://github.com/nguyenduydan/security-sast-guard-plugin/commit/2a6dc8ad100da448017861a6a334c5c13a7536c8))

## [2.4.0](https://github.com/nguyenduydan/security-sast-guard-plugin/compare/v2.3.2...v2.4.0) (2026-08-21)


### 🚀 Features & SAST Security Rules

* **build:** add CLI entry points [project.scripts] and optional dev extras in pyproject.toml (Fixes [#182](https://github.com/nguyenduydan/security-sast-guard-plugin/issues/182)) ([0587a67](https://github.com/nguyenduydan/security-sast-guard-plugin/commit/0587a676eb19ff1c8638a2bc60ceaf575e9a48bd))
* **sast:** harden rule engine for prompt injection, deserialization, and ReDoS prevention ([daaa02b](https://github.com/nguyenduydan/security-sast-guard-plugin/commit/daaa02ba4d4c3b1b6d1cedcfbb118565636ebc46))


### 🐛 Bug Fixes

* **ci:** enforce baseline verification for hardcoded secrets scanning in security gate (Fixes [#171](https://github.com/nguyenduydan/security-sast-guard-plugin/issues/171)) ([1c51cd9](https://github.com/nguyenduydan/security-sast-guard-plugin/commit/1c51cd9a8b5864a5f24808ad47847be0d1f3bcd5))
* **ci:** fix non-existent major versions in GitHub Actions workflows (Fixes [#164](https://github.com/nguyenduydan/security-sast-guard-plugin/issues/164)) ([ea03d81](https://github.com/nguyenduydan/security-sast-guard-plugin/commit/ea03d8188d2e77cd5ef372927dc58b1081dc04ca))
* **cli:** route CLI firewall command evaluation through FirewallEngine to prevent normalizer bypass (Fixes [#178](https://github.com/nguyenduydan/security-sast-guard-plugin/issues/178)) ([259c49c](https://github.com/nguyenduydan/security-sast-guard-plugin/commit/259c49c18c53941c60c216c65ef49f433d615819))
* **engine:** fix Darwin macOS 1024x process memory over-reporting in BoundedVerificationHarness (Fixes [#179](https://github.com/nguyenduydan/security-sast-guard-plugin/issues/179)) ([d1022aa](https://github.com/nguyenduydan/security-sast-guard-plugin/commit/d1022aac0dd50e28b238b90f443bcad3771bde41))
* **engine:** resolve mathematical dead code in SecurityDecisionEngine for confirmed true positives (Fixes [#173](https://github.com/nguyenduydan/security-sast-guard-plugin/issues/173)) ([ae595be](https://github.com/nguyenduydan/security-sast-guard-plugin/commit/ae595be774f6b72050208cb75c73dc8d54634fa1))
* **firewall:** fix unreachable DESTRUCTIVE intent rule and add LATERAL_MOVEMENT capability group (Fixes [#177](https://github.com/nguyenduydan/security-sast-guard-plugin/issues/177)) ([0be76ba](https://github.com/nguyenduydan/security-sast-guard-plugin/commit/0be76ba4c9b832c353dbf73da9cb7e1d5b57938d))
* **firewall:** strip shell wrapper prefixes and normalize compound flags in FirewallNormalizer (Fixes [#176](https://github.com/nguyenduydan/security-sast-guard-plugin/issues/176)) ([ca035e4](https://github.com/nguyenduydan/security-sast-guard-plugin/commit/ca035e4c185de30048272ee710ea18208db4d6d9))
* **git-hook:** resolve relative control_plane.py path in GitHookInstaller for external repositories (Fixes [#180](https://github.com/nguyenduydan/security-sast-guard-plugin/issues/180)) ([80dcf48](https://github.com/nguyenduydan/security-sast-guard-plugin/commit/80dcf487f49f25775a391cdd819af3e37ff8a71b))
* **hooks:** fix runtime crash in post_write_hook.py on PostToolCallExecute (Fixes [#170](https://github.com/nguyenduydan/security-sast-guard-plugin/issues/170)) ([5a603d9](https://github.com/nguyenduydan/security-sast-guard-plugin/commit/5a603d94e1d8890e0d71715b3bf60e6cb8f30190))
* **scanner:** fix multi-file incremental git diff scanning ([12560bb](https://github.com/nguyenduydan/security-sast-guard-plugin/commit/12560bb27c2a5b9eef50c53cfa69b87c31562b60))
* **security:** eliminate overly broad substring sanitizer match in AIVerifier (Fixes [#169](https://github.com/nguyenduydan/security-sast-guard-plugin/issues/169)) ([1b36867](https://github.com/nguyenduydan/security-sast-guard-plugin/commit/1b368675453da84c3781bab2ad511cfc6e802487))
* **security:** fix global variable scope flattening in ASTPrecisionAnalyzer (Fixes [#167](https://github.com/nguyenduydan/security-sast-guard-plugin/issues/167)) ([21c261b](https://github.com/nguyenduydan/security-sast-guard-plugin/commit/21c261b4ecf764dd005ccad65134737ee494b8a8))
* **security:** fix PowerShell Base64 colon parameter and prefix abbreviation bypass in Command Firewall (Fixes [#166](https://github.com/nguyenduydan/security-sast-guard-plugin/issues/166)) ([db7f0ac](https://github.com/nguyenduydan/security-sast-guard-plugin/commit/db7f0acd92849e2103a707fc3a08dba98a283ee4))
* **security:** prevent remote download-and-execute LOLBIN chain bypasses in Command Firewall (Fixes [#172](https://github.com/nguyenduydan/security-sast-guard-plugin/issues/172)) ([bdceee0](https://github.com/nguyenduydan/security-sast-guard-plugin/commit/bdceee0f0e57a5220b54fea7a1b6e50306e51d04))
* **security:** prevent stored XSS in interactive HTML report generator (Fixes [#165](https://github.com/nguyenduydan/security-sast-guard-plugin/issues/165)) ([62fa217](https://github.com/nguyenduydan/security-sast-guard-plugin/commit/62fa217fdd43d8d03d7ab06fb948573751432244))
* **taint:** fix cross-file taint confirmation failure in ASTConfirmEngine (Fixes [#174](https://github.com/nguyenduydan/security-sast-guard-plugin/issues/174)) ([76d6fe7](https://github.com/nguyenduydan/security-sast-guard-plugin/commit/76d6fe7f2b62a5fd4e0828d469bd95dce9595d60))
* **taint:** replace naive substring grepping and improve CallGraphBuilder import chain precision (Fixes [#175](https://github.com/nguyenduydan/security-sast-guard-plugin/issues/175)) ([0ecc176](https://github.com/nguyenduydan/security-sast-guard-plugin/commit/0ecc1761f6d520865a1edf5d6b03cd3e0209bd49))
* **taint:** utilize sink function scope and replace mock tokens with low-entropy fixtures ([5753ce5](https://github.com/nguyenduydan/security-sast-guard-plugin/commit/5753ce50ca0d3fccfb3a01a5765c85c233381011))


### ♻️ Refactoring & Code Hygiene

* **engine:** wire AdaptiveKnowledgeBase and TrustedSanitizerRegistry into core scan pipeline (Fixes [#181](https://github.com/nguyenduydan/security-sast-guard-plugin/issues/181)) ([75e0231](https://github.com/nguyenduydan/security-sast-guard-plugin/commit/75e023173e3546b998f166a058c491f63ac0febb))
* **tests:** stabilize cross-subsystem test assertions and typing overrides ([03cfeca](https://github.com/nguyenduydan/security-sast-guard-plugin/commit/03cfecad227f4bf3101c12bc4d70a371cf5d2a23))
* **types:** clean stale tree-sitter overrides and enable mypy validation for hooks and tests (Fixes [#183](https://github.com/nguyenduydan/security-sast-guard-plugin/issues/183)) ([7010727](https://github.com/nguyenduydan/security-sast-guard-plugin/commit/7010727c5065da7364c64d7c2bf975e7e8c2e0bd))


### 📦 Build System & Dependencies

* **deps:** bump actions/upload-artifact from 4 to 7 ([7a8a0b2](https://github.com/nguyenduydan/security-sast-guard-plugin/commit/7a8a0b2d6c8add6011b1f71048f97a8c41d628ab))
* **deps:** bump astral-sh/setup-uv from 5 to 7 ([fc886fd](https://github.com/nguyenduydan/security-sast-guard-plugin/commit/fc886fdbe5c7eb976609e14a4b9101869379b2a5))
* **deps:** bump github/codeql-action from 3 to 4 ([0dff0fa](https://github.com/nguyenduydan/security-sast-guard-plugin/commit/0dff0fa1ffbba7dcfa3bd5234fb48f3b3e6eec17))


### 📝 Documentation

* **rules:** add atomic commit per issue policy to GEMINI.md ([aac6012](https://github.com/nguyenduydan/security-sast-guard-plugin/commit/aac60124a567402277821d89470c67e83e4788a2))


### Maintenance & Tooling

* **ci:** remove missing dependencies label from dependabot config ([86bf7a8](https://github.com/nguyenduydan/security-sast-guard-plugin/commit/86bf7a887d13fcfd2813365b5dff9d2bdf173dc1))

## [2.3.2](https://github.com/nguyenduydan/security-sast-guard-plugin/compare/v2.3.1...v2.3.2) (2026-08-17)


### 🐛 Bug Fixes

* **security:** resolve 5 false-positive security patterns across core modules ([ed1cdbb](https://github.com/nguyenduydan/security-sast-guard-plugin/commit/ed1cdbb0bf37ae7aa84de88f624fa84817ac997c))


### 🎨 Code Style & Formatting

* **domain:** fix ruff E501 line length in evidence_engine ([1803ea1](https://github.com/nguyenduydan/security-sast-guard-plugin/commit/1803ea159777086c1370145afcbcf7d207094c6e))

## [2.3.1](https://github.com/nguyenduydan/security-sast-guard-plugin/compare/v2.3.0...v2.3.1) (2026-08-14)


### 🐛 Bug Fixes

* **docs:** resolve Vietnamese diacritics font rendering using Plus Jakarta Sans and Be Vietnam Pro ([8a629ad](https://github.com/nguyenduydan/security-sast-guard-plugin/commit/8a629add4dbf8f16cf6068793cffc7e11dc6d0c1))


### 📝 Documentation

* translate all SAST rules and documentation to English and enable dynamic version rendering ([5595a78](https://github.com/nguyenduydan/security-sast-guard-plugin/commit/5595a7853370da8022c08efe9169a68673d34215))

## [2.3.0](https://github.com/nguyenduydan/security-sast-guard-plugin/compare/v2.2.0...v2.3.0) (2026-08-14)


### 🚀 Features & SAST Security Rules

* **scanner:** add OWASP LLM rules, parallel scanner, HTML dashboard, and git hook installer ([a5e4d53](https://github.com/nguyenduydan/security-sast-guard-plugin/commit/a5e4d53098905b53fbcaa3cf78b17a27137f6a11))


### 📝 Documentation

* update landing page and rules explorer with 95 security rules ([7b8dc5b](https://github.com/nguyenduydan/security-sast-guard-plugin/commit/7b8dc5bd3aba2d14d5232d1dffcecbe194a05544))

## [2.2.0](https://github.com/nguyenduydan/security-sast-guard-plugin/compare/v2.1.0...v2.2.0) (2026-08-14)


### 🚀 Features & SAST Security Rules

* **scanner:** add rules ignore filter, sarif cli export, and optimize ci with uv ([5aff348](https://github.com/nguyenduydan/security-sast-guard-plugin/commit/5aff348207745ba014d90472789837cc28844f5e))


### 🐛 Bug Fixes

* **ci:** grant security-events and actions permissions to workflow callers ([89df682](https://github.com/nguyenduydan/security-sast-guard-plugin/commit/89df682d3492c9737892b7c258761a5bbaaca2c6))
* **harness:** preserve explicit memory value in set_memory_mb and stabilize test ([c2a48e2](https://github.com/nguyenduydan/security-sast-guard-plugin/commit/c2a48e2212035f200bda289ced1ad45a7200de30))

## [2.1.0](https://github.com/nguyenduydan/security-sast-guard-plugin/compare/v2.0.1...v2.1.0) (2026-08-14)


### 🚀 Features & SAST Security Rules

* **ast:** add ASTPrecisionAnalyzer for Python constant propagation ([49c5e25](https://github.com/nguyenduydan/security-sast-guard-plugin/commit/49c5e251cec6f6e5119b62e672c465872f56ff08))
* **context:** add multi-line block comment tracking and context window extraction ([b32d8c6](https://github.com/nguyenduydan/security-sast-guard-plugin/commit/b32d8c606b1ec8f96c5fb4e553cda9f194002311))
* **scanner:** integrate AST analyzer and context window into scanning pipeline ([9662e06](https://github.com/nguyenduydan/security-sast-guard-plugin/commit/9662e060ed70c3a5b3401e890f1235c73fa3371d))
* **verifier:** add context window sanitizer inspection to AIVerifier ([8d81d64](https://github.com/nguyenduydan/security-sast-guard-plugin/commit/8d81d64f9b6f663a6348a4e0887d3ddd5f06972c))


### 🐛 Bug Fixes

* **tests:** move AICache import to top-level to satisfy pylint C0415 ([0be2a73](https://github.com/nguyenduydan/security-sast-guard-plugin/commit/0be2a73e31e10693053aded0bd268108d5ba1b4c))


### 📝 Documentation

* **specs:** add design, plan, and task reports for semantic precision engine ([4e955b7](https://github.com/nguyenduydan/security-sast-guard-plugin/commit/4e955b7482ca55a24da8a9fe7fd30f72a293f6ad))

## [2.0.1](https://github.com/nguyenduydan/security-sast-guard-plugin/compare/v2.0.0...v2.0.1) (2026-08-13)


### ♻️ Refactoring & Code Hygiene

* **rules:** reduce false positives for ASP.NET, UI events and minified JS ([79eafd0](https://github.com/nguyenduydan/security-sast-guard-plugin/commit/79eafd001aff1f7d0c0dbae52709f3796180e4e0))


### 🎨 Code Style & Formatting

* **scripts:** split long line in md_to_json.py for pylint line-too-long compliance ([4c69dd2](https://github.com/nguyenduydan/security-sast-guard-plugin/commit/4c69dd2296bb7e13f21ef681552914d0a6d9d8d8))
* **tests:** split long line in test_sast.py for ruff compliance ([dd054b5](https://github.com/nguyenduydan/security-sast-guard-plugin/commit/dd054b5a12c35423ad63bbb13893c4555f813dda))

## [2.0.0](https://github.com/nguyenduydan/security-sast-guard-plugin/compare/v1.9.0...v2.0.0) (2026-08-12)


### ⚠ BREAKING CHANGES

* **dx:** Major release upgrade to Security SAST Guard v2.0.0 Architecture.

### 🚀 Features & SAST Security Rules

* **dx:** implement v2.0.0 Tier 3 developer experience modules ([8a5d863](https://github.com/nguyenduydan/security-sast-guard-plugin/commit/8a5d863103186fd36de278c71df5fb7408d48b2e))
* **sast-intelligence:** implement v2.0.0 Tier 2 SAST intelligence modules ([66ad017](https://github.com/nguyenduydan/security-sast-guard-plugin/commit/66ad017d22fde6ebd36b3fa878d5bd99971ceb88))
* **security-core:** implement v2.0.0 Tier 1 security core modules ([e3673d7](https://github.com/nguyenduydan/security-sast-guard-plugin/commit/e3673d74ff03cac1e9a10e055d8797b12f94be2c))


### 🐛 Bug Fixes

* **harness:** add explanatory comments to empty except blocks for CodeQL ([ee1a3fd](https://github.com/nguyenduydan/security-sast-guard-plugin/commit/ee1a3fd4e8913ce76c4201deb32695a29367e653))
* **harness:** resolve cross-platform mypy type checking errors in loop_harness ([c00c208](https://github.com/nguyenduydan/security-sast-guard-plugin/commit/c00c208d68c6115424dd09317563657db695f211))

## [1.9.0](https://github.com/nguyenduydan/security-sast-guard-plugin/compare/v1.8.11...v1.9.0) (2026-08-12)


### 🚀 Features & SAST Security Rules

* **installer:** add automatic Python Embeddable fallback when system Python is missing ([02b32c0](https://github.com/nguyenduydan/security-sast-guard-plugin/commit/02b32c0b27ce25be20ac2eaaedb6764380ff71a0))


### 🐛 Bug Fixes

* **docs:** remove duplicate inline script block and declare autoPlayTimer in app.js ([2378d5b](https://github.com/nguyenduydan/security-sast-guard-plugin/commit/2378d5b5fc6636d6272fcb7a56fcce962d10f3cb))
* **docs:** update version badges to v1.8.11 and resolve version sync logic ([d73ce64](https://github.com/nguyenduydan/security-sast-guard-plugin/commit/d73ce64d2a35854b909e85668a737313f1e0a618))

## [1.8.11](https://github.com/nguyenduydan/security-sast-guard-plugin/compare/v1.8.10...v1.8.11) (2026-08-12)


### ♻️ Refactoring & Code Hygiene

* **config:** add macOS diskutil erase/repartition pattern to deny list ([5bf64eb](https://github.com/nguyenduydan/security-sast-guard-plugin/commit/5bf64ebffe04eee9017d22e068ed739b36e27926))
* **docs:** improve landing page ui components, copy buttons and focus ring removal ([9402493](https://github.com/nguyenduydan/security-sast-guard-plugin/commit/9402493f658b70b620b57f66b752ffa4282afcb2))
* **docs:** update architecture topology SVG and landing page UI ([ff805d9](https://github.com/nguyenduydan/security-sast-guard-plugin/commit/ff805d9469ba4d1e3615d779208229d8524b05ba))

## [1.8.10](https://github.com/nguyenduydan/security-sast-guard-plugin/compare/v1.8.9...v1.8.10) (2026-08-12)


### 🐛 Bug Fixes

* **config:** update dependabot labels to existing dependencies label ([d6e9955](https://github.com/nguyenduydan/security-sast-guard-plugin/commit/d6e99553e5b970bc2686b06f285ae4745b44000a))
* **hooks:** remove duplicate import json in firewall_hook.py ([d28c25d](https://github.com/nguyenduydan/security-sast-guard-plugin/commit/d28c25d8dcdeea9148428e7bee064596eb4463a7))
* resolve false positives for web.config tokens, csproj, and plugins directory ([f028c07](https://github.com/nguyenduydan/security-sast-guard-plugin/commit/f028c07154a8d6fd520400e7368f9bacc780e902))

## [1.8.9](https://github.com/nguyenduydan/security-sast-guard-plugin/compare/v1.8.8...v1.8.9) (2026-08-12)


### 📦 Build System & Dependencies

* **deps:** bump actions/attest-build-provenance from 2 to 4 ([f3ccfde](https://github.com/nguyenduydan/security-sast-guard-plugin/commit/f3ccfdea3e7b35cf7519b0afb26fe78e112f041d))
* **deps:** bump actions/dependency-review-action from 4 to 5 ([a3875d2](https://github.com/nguyenduydan/security-sast-guard-plugin/commit/a3875d268e7b58c50f43451460cfca6b15f8c91c))
* **deps:** bump actions/setup-python from 5 to 7 ([4a8fbc3](https://github.com/nguyenduydan/security-sast-guard-plugin/commit/4a8fbc38ed7b1fe66a7ccf1f76963a6a05f29905))
* **deps:** bump googleapis/release-please-action from 4 to 5 ([3accaaa](https://github.com/nguyenduydan/security-sast-guard-plugin/commit/3accaaa69b30ab9fd70104dc4c541a9d3cb328f6))
* **deps:** bump softprops/action-gh-release from 2 to 3 ([d2b0a71](https://github.com/nguyenduydan/security-sast-guard-plugin/commit/d2b0a71f0557cbeb075a875ec0e004020693e095))

## [1.8.8](https://github.com/nguyenduydan/security-sast-guard-plugin/compare/v1.8.7...v1.8.8) (2026-08-11)


### 🐛 Bug Fixes

* **hooks:** remove duplicate import json in firewall_hook.py ([bc7ff1d](https://github.com/nguyenduydan/security-sast-guard-plugin/commit/bc7ff1dd32eed02b5cc67de527d6e81794f91d4c))
* resolve false positives for web.config tokens, csproj, and plugins directory ([6e817d9](https://github.com/nguyenduydan/security-sast-guard-plugin/commit/6e817d9a58e1686e0abe271c5f52412ce898747b))

## [1.8.7](https://github.com/nguyenduydan/security-sast-guard-plugin/compare/v1.8.6...v1.8.7) (2026-08-11)


### 🐛 Bug Fixes

* **hooks:** update firewall hook to output JSON for Gemini compatibility ([344b28c](https://github.com/nguyenduydan/security-sast-guard-plugin/commit/344b28c1c1cc78f1945a579f45e71128e78be3b6))


### Maintenance & Tooling

* **rules:** enforce ruff checks and fix hook formatting ([55a7da5](https://github.com/nguyenduydan/security-sast-guard-plugin/commit/55a7da5b12cafd8b71f3cd9ade14bf6ccafbb386))

## [1.8.6](https://github.com/nguyenduydan/security-sast-guard-plugin/compare/v1.8.5...v1.8.6) (2026-08-11)


### ♻️ Refactoring & Code Hygiene

* **core:** decouple report generation to allow AI analysis injection ([1fee309](https://github.com/nguyenduydan/security-sast-guard-plugin/commit/1fee309fe6e4c0d1b703e5ec233bf1378de8608a))


### Maintenance & Tooling

* **ignore:** add missing ASP.NET directories, designer.cs, static configs, and htm files to default ignore rules ([01c9522](https://github.com/nguyenduydan/security-sast-guard-plugin/commit/01c95221ed923cec5f0e064daa9ea05c9d934683))
* **ignore:** add web.config, app.config, and environment transformation files to default ignore rules ([f1981e9](https://github.com/nguyenduydan/security-sast-guard-plugin/commit/f1981e9a9be8979a62e7a482d32c63ead5124e52))

## [1.8.5](https://github.com/nguyenduydan/security-sast-guard-plugin/compare/v1.8.4...v1.8.5) (2026-08-11)


### 🐛 Bug Fixes

* **ignore:** refine temp folder ignore matching to prevent ignoring Linux runner /tmp/ root directory ([879ae06](https://github.com/nguyenduydan/security-sast-guard-plugin/commit/879ae06a66e26933d0dba7897963560eb5837dff))


### 🎨 Code Style & Formatting

* **format:** format comment spacing in ignore_filter.py for ruff formatter ([5300a39](https://github.com/nguyenduydan/security-sast-guard-plugin/commit/5300a39aa48bb27b287fd6382a23282e2090323f))
* **format:** resolve ruff E501 line length warnings in test_ignore_filter.py ([0da7a6c](https://github.com/nguyenduydan/security-sast-guard-plugin/commit/0da7a6c6bfa25ba7f8fe0a92ac3c879cc9d565d4))
* **format:** shorten test assertion lines to comply with strict ruff line-length ([2a0fb25](https://github.com/nguyenduydan/security-sast-guard-plugin/commit/2a0fb25e80f5b07f45284d091242b9a39cbab997))


### Maintenance & Tooling

* **ignore:** add aspnet build, cache, symbol, and lock file ignore rules ([8709e6f](https://github.com/nguyenduydan/security-sast-guard-plugin/commit/8709e6f74f24b93d3c115fba8630c8deb0f13b6b))
* **ignore:** add temp, cache, and library directories across ecosystems to default ignore rules ([4331cbe](https://github.com/nguyenduydan/security-sast-guard-plugin/commit/4331cbe2f51b5092949f6e5492bd1d6feb827258))
* **ignore:** add template and log files/directories to zero-config ignore defaults ([9759ab5](https://github.com/nguyenduydan/security-sast-guard-plugin/commit/9759ab500a480237b48aba43a4f35b4062f21420))

## [1.8.4](https://github.com/nguyenduydan/security-sast-guard-plugin/compare/v1.8.3...v1.8.4) (2026-08-11)


### ♻️ Refactoring & Code Hygiene

* **tui:** restore full cyber neo-brutalist TUI installer and updater ([e78c0d8](https://github.com/nguyenduydan/security-sast-guard-plugin/commit/e78c0d86bbe358bfc773470f086a7507ee0ad7d4))

## [1.8.3](https://github.com/nguyenduydan/security-sast-guard-plugin/compare/v1.8.2...v1.8.3) (2026-08-11)


### 🐛 Bug Fixes

* **install:** fix bug expect ([16a6d91](https://github.com/nguyenduydan/security-sast-guard-plugin/commit/16a6d91ce3b193f4b11d73d7e9335c3ee92ea581))

## [1.8.2](https://github.com/nguyenduydan/security-sast-guard-plugin/compare/v1.8.1...v1.8.2) (2026-08-11)


### 🐛 Bug Fixes

* **scripts:** convert powershell scripts to utf-8 bom encoding ([7ff4af0](https://github.com/nguyenduydan/security-sast-guard-plugin/commit/7ff4af037d1ee3216fde6a2669d3f339177aadb6))

## [1.8.1](https://github.com/nguyenduydan/security-sast-guard-plugin/compare/v1.8.0...v1.8.1) (2026-08-11)


### ♻️ Refactoring & Code Hygiene

* **cli:** add verbose real-time progress logging for sast scan ([5a30dc4](https://github.com/nguyenduydan/security-sast-guard-plugin/commit/5a30dc4bcbf36f9c536d4cb96b1ea0329892f907))

## [1.8.0](https://github.com/nguyenduydan/security-sast-guard-plugin/compare/v1.7.0...v1.8.0) (2026-08-11)


### 🚀 Features & SAST Security Rules

* merge remaining feature branches - AST context engine, installer auto-reg, landing page docs, skill files update ([ac476d9](https://github.com/nguyenduydan/security-sast-guard-plugin/commit/ac476d949d5a946411ac4a3855209949611a85fc))
* **taint:** merge full taint analysis engine - CallGraphBuilder, TaintTracker, SymbolIndexer, ASTConfirmEngine, MCP dataflow tools ([b5b6724](https://github.com/nguyenduydan/security-sast-guard-plugin/commit/b5b67243415240768a549e52d8dc8b383352b6ec))


### 🐛 Bug Fixes

* **ci:** allow skipped dependency-review on push events, add gate-result job to security gate ([9b68d31](https://github.com/nguyenduydan/security-sast-guard-plugin/commit/9b68d316c815400746422dd5ad7440e646a0ec45))
* **security:** resolve 10 CodeQL alerts - remove unused globals, clarify empty except blocks ([607c57e](https://github.com/nguyenduydan/security-sast-guard-plugin/commit/607c57e455d4122b923de19c374fbf45ff2a0162))
* **types:** add explicit type annotations for mypy - dict generics, Iterator return types, no-any-return ([437db8c](https://github.com/nguyenduydan/security-sast-guard-plugin/commit/437db8cabc94cdf4f2635efc6fa6ab771e54ee8b))


### 🎨 Code Style & Formatting

* **format:** auto-format 14 files with ruff format ([b97b493](https://github.com/nguyenduydan/security-sast-guard-plugin/commit/b97b49375b118fcd2a11a67fcc0b9a81d6737150))
* **lint:** fix pylint C1803, C0415, W0621, W0404 and trailing newline ([271aa55](https://github.com/nguyenduydan/security-sast-guard-plugin/commit/271aa550b02452e9ccb2558760b0bb84452bb890))
* **lint:** fix ruff I001, E501, RUF015, F401, E401, SIM117 across audit_service and tests ([33063c2](https://github.com/nguyenduydan/security-sast-guard-plugin/commit/33063c28c326fe0ad4d78278c5be1ffd71bf9067))

## [1.7.0](https://github.com/nguyenduydan/security-sast-guard-plugin/compare/v1.6.1...v1.7.0) (2026-08-11)


### 🚀 Features & SAST Security Rules

* **ci:** implement enterprise security github actions architecture with sha pinning sbom and attestations ([60f4f42](https://github.com/nguyenduydan/security-sast-guard-plugin/commit/60f4f4206091b2f562cf964719c2e1934e4f565a))
* **security:** complete 100% public repository security hardening with dependabot codeql and dependency review ([b3a60d9](https://github.com/nguyenduydan/security-sast-guard-plugin/commit/b3a60d9208342fe1426648fd4ec9b06e83fb07fa))


### 🐛 Bug Fixes

* **ci:** grant explicit caller permissions in ci and release workflows for reusable workflows ([877ad3a](https://github.com/nguyenduydan/security-sast-guard-plugin/commit/877ad3a00262f05cd572d0c241a6d9b1a61c502c))
* **ci:** inline setup-python steps in reusable workflows for reliable resolution ([2f02e3b](https://github.com/nguyenduydan/security-sast-guard-plugin/commit/2f02e3bb5571de326b427fda476575ce78e967b9))
* **ci:** update all action references to official version tags for instant runner resolution ([989c6e2](https://github.com/nguyenduydan/security-sast-guard-plugin/commit/989c6e23118da936c903295d243a6f20d02e697f))
* **ci:** update codeql-action tag to v3 for valid runner resolution ([4679df8](https://github.com/nguyenduydan/security-sast-guard-plugin/commit/4679df8f3bc6e0dd1552cc5a9b6811b42d0981cb))
* **cli:** support codebase keyword alias in audit command ([87aa369](https://github.com/nguyenduydan/security-sast-guard-plugin/commit/87aa36934e159b6ff09ca32963670b0b5c0cd71f))


### 📦 Build System & Dependencies

* **deps:** bump actions/checkout from v4 to v7 ([e63afb3](https://github.com/nguyenduydan/security-sast-guard-plugin/commit/e63afb31d2ee512b063a6ca8db3367288acd232b))
* **deps:** bump github/codeql-action from 3 to 4 ([e672ecb](https://github.com/nguyenduydan/security-sast-guard-plugin/commit/e672ecb80a9f997df8c8999f4bcbed3db0196487))


### 🎨 Code Style & Formatting

* **ci:** shorten workflow and job display names for clean github UI ([9e097d9](https://github.com/nguyenduydan/security-sast-guard-plugin/commit/9e097d9ae4e99e3726331ccc794969787c17a7be))

## [1.6.1](https://github.com/nguyenduydan/security-sast-guard-plugin/compare/v1.6.0...v1.6.1) (2026-08-11)


### ♻️ Refactoring & Code Hygiene

* **ci:** restructure github actions workflows with composite action and parallel jobs ([8fdb0ac](https://github.com/nguyenduydan/security-sast-guard-plugin/commit/8fdb0ac160c31f1b6c35856b5c5242fc62fc50f3))

## [1.6.0](https://github.com/nguyenduydan/security-sast-guard-plugin/compare/v1.5.6...v1.6.0) (2026-08-11)


### 🚀 Features & SAST Security Rules

* **detection:** implement Smarter Detection Engine with taint analysis, AST confirmation, and cross-file call graph ([a8fbc89](https://github.com/nguyenduydan/security-sast-guard-plugin/commit/a8fbc89d7b6e6937a3b003cdf83e033b474b1796))


### 🐛 Bug Fixes

* **cache:** add pure-python OrderedDict LRUCache fallback and install dependencies in CI workflow ([7b2045b](https://github.com/nguyenduydan/security-sast-guard-plugin/commit/7b2045b5e59a58d54dee443e1ff59c42ccc1a558))
* **mypy:** configure mypy overrides for untyped third-party packages in pyproject.toml ([ba04246](https://github.com/nguyenduydan/security-sast-guard-plugin/commit/ba04246d6e3f7a62ecc9f110807472820c7610c0))
* **pytest:** add pythonpath to pyproject.toml to resolve test collection module imports ([8bd7cee](https://github.com/nguyenduydan/security-sast-guard-plugin/commit/8bd7cee306b568030d6867e9281511f7e9d22997))
* **types:** resolve all 20 mypy type annotations and ignore warnings ([0c8b11b](https://github.com/nguyenduydan/security-sast-guard-plugin/commit/0c8b11b6534841a596189098ecb330f8e652e223))
* **types:** resolve SymbolCache.get no-any-return mypy error ([1684949](https://github.com/nguyenduydan/security-sast-guard-plugin/commit/1684949417b25186ec32257c90bfca3f3700cdea))


### 📝 Documentation

* **plans:** add 4-sprint implementation plans for smarter detection engine ([23ed127](https://github.com/nguyenduydan/security-sast-guard-plugin/commit/23ed127a4408db368ff9a58ca861ce99dd99e3bd))
* **spec:** add smarter detection engine design spec with taint analysis and cross-file dataflow ([330011a](https://github.com/nguyenduydan/security-sast-guard-plugin/commit/330011a3c466f98a7d53abef8b7ab18a8f52ab46))


### 🎨 Code Style & Formatting

* **linter:** import Generator from collections.abc (UP035) ([5a01771](https://github.com/nguyenduydan/security-sast-guard-plugin/commit/5a01771d42c2b48fe39cff4683ee80a2ac7bd2ec))

## [1.5.6](https://github.com/nguyenduydan/security-sast-guard-plugin/compare/v1.5.5...v1.5.6) (2026-08-10)


### ♻️ Refactoring & Code Hygiene

* **report:** skip markdown report file generation when no findings detected ([71403c8](https://github.com/nguyenduydan/security-sast-guard-plugin/commit/71403c8589bbcc52b0bc5640b74ae0c632a72751))

## [1.5.5](https://github.com/nguyenduydan/security-sast-guard-plugin/compare/v1.5.4...v1.5.5) (2026-08-10)


### ♻️ Refactoring & Code Hygiene

* **firewall:** optimize command firewall anti-bypass and update rules ([196c0b7](https://github.com/nguyenduydan/security-sast-guard-plugin/commit/196c0b701cedfd7d3dd72b310c035a38cdcbac48))


### 🎨 Code Style & Formatting

* **firewall:** apply ruff formatting ([bd60e56](https://github.com/nguyenduydan/security-sast-guard-plugin/commit/bd60e56b28f319dddcc30d02ff43b9f4657edc9e))
* **firewall:** fix ruff E501 line length limit ([cee951f](https://github.com/nguyenduydan/security-sast-guard-plugin/commit/cee951ff3fd5fa96f410bf91d212ea0b7b55315f))

## [1.5.4](https://github.com/nguyenduydan/security-sast-guard-plugin/compare/v1.5.3...v1.5.4) (2026-08-10)


### 🐛 Bug Fixes

* **scan:** optimize large file scanning performance with in-memory context extraction and pre-compiled rules ([166d745](https://github.com/nguyenduydan/security-sast-guard-plugin/commit/166d7459a0039ef0bdf8cc37f9d0709d6f0ccaa3))


### ⚡ Performance Improvements

* **engine:** apply LRU cache and pre-compiled regex arrays for firewall and scope resolution ([69a0ceb](https://github.com/nguyenduydan/security-sast-guard-plugin/commit/69a0ceba8c1d5c12227f33bbda4b875b7f6dad6a))


### 🎨 Code Style & Formatting

* **linter:** fix ruff import sorting, line length, SIM105 and SIM110 rules ([df1a482](https://github.com/nguyenduydan/security-sast-guard-plugin/commit/df1a4823256a5d7c6fd053d4d0f089e6066c469a))

## [1.5.3](https://github.com/nguyenduydan/security-sast-guard-plugin/compare/v1.5.2...v1.5.3) (2026-08-10)


### 📝 Documentation

* **skill:** add post-audit AI false positive verification workflow to sast-audit ([6ec3bd3](https://github.com/nguyenduydan/security-sast-guard-plugin/commit/6ec3bd3138df723913ae3e0c2a27a5e07e3870c2))

## [1.5.2](https://github.com/nguyenduydan/security-sast-guard-plugin/compare/v1.5.1...v1.5.2) (2026-08-10)


### 📝 Documentation

* **readme:** streamline overview documentation and sync rule counts to 88 ([c404be3](https://github.com/nguyenduydan/security-sast-guard-plugin/commit/c404be3de13927842d0baf128c2d5162f385eb81))

## [1.5.1](https://github.com/nguyenduydan/security-sast-guard-plugin/compare/v1.5.0...v1.5.1) (2026-08-10)


### 🐛 Bug Fixes

* **scanner:** support explicit single file scan for aspx and dot-net webforms ([74d2ea2](https://github.com/nguyenduydan/security-sast-guard-plugin/commit/74d2ea299f7473f3847a8f51f8e6f0f45b3cbfd6))

## [1.5.0](https://github.com/nguyenduydan/security-sast-guard-plugin/compare/v1.4.2...v1.5.0) (2026-08-10)


### 🚀 Features & SAST Security Rules

* **git-helper:** implement smart git diff base resolver ([14164c9](https://github.com/nguyenduydan/security-sast-guard-plugin/commit/14164c9ce903bd469e4f74b4ca9efff81b0cd6cd))
* **report:** implement SARIF 2.1.0 report exporter ([569988a](https://github.com/nguyenduydan/security-sast-guard-plugin/commit/569988aff535404a92e73fa0526c076030f74cda))
* **rules:** add remediation snippets to rules and markdown report ([572305d](https://github.com/nguyenduydan/security-sast-guard-plugin/commit/572305db31a64924373fe82c092c66495231bccb))


### 🎨 Code Style & Formatting

* **lint:** format python files with ruff ([b25d6aa](https://github.com/nguyenduydan/security-sast-guard-plugin/commit/b25d6aa11cb8a735f8bac7b733e604444db483e4))

## [1.4.2](https://github.com/nguyenduydan/security-sast-guard-plugin/compare/v1.4.1...v1.4.2) (2026-08-10)


### 📝 Documentation

* **plan:** add implementation plan for sast enhancements ([5adeb4f](https://github.com/nguyenduydan/security-sast-guard-plugin/commit/5adeb4fa0676be4e3ab11b3bb21c0fbe84223079))
* **spec:** add design specification for sast enhancements ([fbc95e0](https://github.com/nguyenduydan/security-sast-guard-plugin/commit/fbc95e02d63ae13abad82ed84bb15e72c6708c6c))

## [1.4.1](https://github.com/nguyenduydan/security-sast-guard-plugin/compare/v1.4.0...v1.4.1) (2026-08-10)


### 🐛 Bug Fixes

* **scanner:** resolve report relative url and aspnet false positives ([#87](https://github.com/nguyenduydan/security-sast-guard-plugin/issues/87), [#88](https://github.com/nguyenduydan/security-sast-guard-plugin/issues/88)) ([700b204](https://github.com/nguyenduydan/security-sast-guard-plugin/commit/700b204a65067e16c6e7f1fcba59866a5513e2ec))


### 🎨 Code Style & Formatting

* **lint:** format ai_verifier.py with ruff ([a182efc](https://github.com/nguyenduydan/security-sast-guard-plugin/commit/a182efc64345121c09b2d3ba7ba27dacae2341c2))

## [1.4.0](https://github.com/nguyenduydan/security-sast-guard-plugin/compare/v1.3.2...v1.4.0) (2026-08-07)


### 🚀 Features & SAST Security Rules

* **ast:** add ASTContextEngine for node scope classification ([06b454b](https://github.com/nguyenduydan/security-sast-guard-plugin/commit/06b454b3c84c653003ae9f96b486dbbee1fbf51f))
* **rules:** add target_scopes and excluded_scopes metadata to sast_rules.json ([129c6aa](https://github.com/nguyenduydan/security-sast-guard-plugin/commit/129c6aa1a0b82af63526e2c86553f669dc174e75))
* **scanner:** integrate ASTContextEngine scope filtering into SASTScanner ([ba20719](https://github.com/nguyenduydan/security-sast-guard-plugin/commit/ba20719e0abe8ff196ec9506ba6ea6824ede9496))


### 🐛 Bug Fixes

* **lint:** fix mixed line endings and trailing newlines in test_suppression.py ([19a356a](https://github.com/nguyenduydan/security-sast-guard-plugin/commit/19a356a3b7af0c3e478663cda98ce15678fa26c6))
* **lint:** resolve ruff I001, SIM102, and E501 linter issues ([0c161da](https://github.com/nguyenduydan/security-sast-guard-plugin/commit/0c161da023dfd6e0ae3c4edea7e6d73971718620))


### 📝 Documentation

* **plan:** update implementation plan with docs/index.html landing page task ([6bcffac](https://github.com/nguyenduydan/security-sast-guard-plugin/commit/6bcffacfadfd6c54eeec104c4344e3a4888d961c))
* update README.md and docs/index.html landing page with Realtime AST Engine & Comment Suppression features ([0086f6d](https://github.com/nguyenduydan/security-sast-guard-plugin/commit/0086f6d4556d4427e67296748e41fa2b484c3165))
* update stats to 88 rules, v1.3.2 release tag, 70 pytests in index.html ([401e70c](https://github.com/nguyenduydan/security-sast-guard-plugin/commit/401e70c9c6738f2a5bbea37b59f8479e257417b1))


### 🎨 Code Style & Formatting

* **lint:** format python files with ruff ([58e08b4](https://github.com/nguyenduydan/security-sast-guard-plugin/commit/58e08b44ae6e76298e86d67c1673aba62d02a3f7))

## [1.3.2](https://github.com/nguyenduydan/security-sast-guard-plugin/compare/v1.3.1...v1.3.2) (2026-08-07)


### 🐛 Bug Fixes

* **sast:** refine RCE regex pattern and add inline comment suppression logic ([764d7c0](https://github.com/nguyenduydan/security-sast-guard-plugin/commit/764d7c09f1ac76ebd767b8e9d62b47b3e54f439d))
* **scanner:** simplify inline suppression return condition to fix ruff SIM103 ([39b9ad7](https://github.com/nguyenduydan/security-sast-guard-plugin/commit/39b9ad7623b925c91d78d6412268b4a91dbfda91))

## [1.3.1](https://github.com/nguyenduydan/security-sast-guard-plugin/compare/v1.3.0...v1.3.1) (2026-08-07)


### 🐛 Bug Fixes

* **tui:** suppress powershell native progress banner during archive extraction ([305d213](https://github.com/nguyenduydan/security-sast-guard-plugin/commit/305d213c3c96ff6da798d741d6b491e31efd7b8a))

## [1.3.0](https://github.com/nguyenduydan/security-sast-guard-plugin/compare/v1.2.7...v1.3.0) (2026-08-07)


### 🚀 Features & SAST Security Rules

* **tui:** integrate responsive console theme, ascii fallback, and duration timer ([d25c7ee](https://github.com/nguyenduydan/security-sast-guard-plugin/commit/d25c7eed8d57a67e26652b27bac214158990ba07))


### 🐛 Bug Fixes

* **tui:** resolve Windows PowerShell string interpolation parser error ([c512d52](https://github.com/nguyenduydan/security-sast-guard-plugin/commit/c512d52522895c0c6ac4848b0d477a14e41d4904))

## [1.2.7](https://github.com/nguyenduydan/security-sast-guard-plugin/compare/v1.2.6...v1.2.7) (2026-08-07)


### ♻️ Refactoring & Code Hygiene

* **tui:** redesign installer and updater scripts with real-time TUI ([7fc63db](https://github.com/nguyenduydan/security-sast-guard-plugin/commit/7fc63dbf270213add2e1c4828997ab4137d92af5))

## [1.2.6](https://github.com/nguyenduydan/security-sast-guard-plugin/compare/v1.2.5...v1.2.6) (2026-08-07)


### ♻️ Refactoring & Code Hygiene

* **skills:** optimize slash commands to use ask_question grill modal UI ([79a147a](https://github.com/nguyenduydan/security-sast-guard-plugin/commit/79a147a2e3837fbd4ac1794d398b2ba21da54bb8))

## [1.2.5](https://github.com/nguyenduydan/security-sast-guard-plugin/compare/v1.2.4...v1.2.5) (2026-08-07)


### 🐛 Bug Fixes

* **scanner:** fix mypy operator precedence in audit_service.py ([22f35d3](https://github.com/nguyenduydan/security-sast-guard-plugin/commit/22f35d3656c42ba4936a2eabd0ceb0e4c6818756))
* **scanner:** resolve false positive findings and ignore test fixtures ([129b30a](https://github.com/nguyenduydan/security-sast-guard-plugin/commit/129b30a8eb4907921489445c2012f10711282322))

## [1.2.4](https://github.com/nguyenduydan/security-sast-guard-plugin/compare/v1.2.3...v1.2.4) (2026-08-07)


### 🐛 Bug Fixes

* **mcp:** write mcp_config.json as utf8 without bom to prevent json parse errors ([d08a912](https://github.com/nguyenduydan/security-sast-guard-plugin/commit/d08a912c4ba0a63613b689a4c3a1ad682a2b6573))

## [1.2.3](https://github.com/nguyenduydan/security-sast-guard-plugin/compare/v1.2.2...v1.2.3) (2026-08-07)


### 🐛 Bug Fixes

* **updater:** stop active mcp process and use overlay copy to prevent file locks ([643a99d](https://github.com/nguyenduydan/security-sast-guard-plugin/commit/643a99d6edba8ca69bfb08233da384eb28f630cf))

## [1.2.2](https://github.com/nguyenduydan/security-sast-guard-plugin/compare/v1.2.1...v1.2.2) (2026-08-07)


### 🐛 Bug Fixes

* **mcp:** resolve absolute python executable path in mcp_config ([757aa3d](https://github.com/nguyenduydan/security-sast-guard-plugin/commit/757aa3d8a8182aa4c8b0705e0ad295df36d703d3))

## [1.2.1](https://github.com/nguyenduydan/security-sast-guard-plugin/compare/v1.2.0...v1.2.1) (2026-08-07)


### 🐛 Bug Fixes

* **installer:** resolve powershell parser errors in ps1 scripts ([d08577a](https://github.com/nguyenduydan/security-sast-guard-plugin/commit/d08577aa0b384508bfa574d38179b24085752283))

## [1.2.0](https://github.com/nguyenduydan/security-sast-guard-plugin/compare/v1.1.1...v1.2.0) (2026-08-07)


### 🚀 Features & SAST Security Rules

* **mcp:** auto register MCP server in installer scripts and improve skill fallback UI labels ([0022252](https://github.com/nguyenduydan/security-sast-guard-plugin/commit/00222523d9e80b7df7bee835cd3f43b22bc449e8))


### 🐛 Bug Fixes

* **mcp:** add PYTHONPATH env var to MCP server config to resolve src module not found error ([7fc2c65](https://github.com/nguyenduydan/security-sast-guard-plugin/commit/7fc2c65b987ee20a77f7a11c486665132c40c7a9))
* **mcp:** silently ignore JSON-RPC notifications to fix tools/list invalid request error ([5911838](https://github.com/nguyenduydan/security-sast-guard-plugin/commit/5911838a5dd4f5d1f30cb025552d6eba3dadd969))
* **scanner:** exclude doc/text extensions and system dirs from SAST scan to eliminate false positives ([6a2b120](https://github.com/nguyenduydan/security-sast-guard-plugin/commit/6a2b120a53fa0bad5e23bfe12025b20565564226))


### 🎨 Code Style & Formatting

* **tests:** fix ruff E501 line-too-long in test_ignore_filter.py ([4d12905](https://github.com/nguyenduydan/security-sast-guard-plugin/commit/4d1290594ed40ef84fa4c536ca496f4ec684e9f2))

## [1.1.1](https://github.com/nguyenduydan/security-sast-guard-plugin/compare/v1.1.0...v1.1.1) (2026-08-07)


### 📝 Documentation

* **web:** remove deprecated /sast-firewall slash command to align with plugin.json ([c985a1d](https://github.com/nguyenduydan/security-sast-guard-plugin/commit/c985a1d69ffb935cca0b21bc0cada95416f98af6))
* **web:** update landing page with /sast-status command and 9 native mcp tools ([0629bbc](https://github.com/nguyenduydan/security-sast-guard-plugin/commit/0629bbcbd24cf2e2da9524996d54b29c6cd141ef))

## [1.1.0](https://github.com/nguyenduydan/security-sast-guard-plugin/compare/v1.0.0...v1.1.0) (2026-08-07)


### 🚀 Features & SAST Security Rules

* **mcp:** add native mcp tools, sast-mode command, and clean cli runners ([b82d8c7](https://github.com/nguyenduydan/security-sast-guard-plugin/commit/b82d8c731ec0e7e046653ea353538d1c29e087c6))
* **ui:** streamline slash commands array in plugin.json to 5 essential user-facing skills ([d1b494f](https://github.com/nguyenduydan/security-sast-guard-plugin/commit/d1b494f767e5b36e5da21674a58eae60ca7ce3e0))


### 🐛 Bug Fixes

* **linter:** resolve all ruff check linter formatting and line length errors ([d9aba9b](https://github.com/nguyenduydan/security-sast-guard-plugin/commit/d9aba9b45fb05f3df974af40d9335c40825d1813))
* **test:** remove trailing newlines in test_mcp_tools.py to reach 10.00/10 pylint score ([e2ccfe9](https://github.com/nguyenduydan/security-sast-guard-plugin/commit/e2ccfe9f758ccadac21d732bbdeaee8631e040eb))


### 📝 Documentation

* **mcp:** update documentation for native mcp tools, sast-mode command, and clean cli runners ([491ad9e](https://github.com/nguyenduydan/security-sast-guard-plugin/commit/491ad9edf496d9a79eaf96188e69f34334d3b7a0))
* **readme:** strip version-specific release notes and hardcoded version strings ([ad57661](https://github.com/nguyenduydan/security-sast-guard-plugin/commit/ad576612bcc92e11ef141fdff6e437a9649838af))
* **web:** update interactive landing page and mcp integration guide for native mcp tools and sast-mode ([1f5ca32](https://github.com/nguyenduydan/security-sast-guard-plugin/commit/1f5ca3215f2ee5046afa8311c6bed60abc78f352))


### 🎨 Code Style & Formatting

* **ruff:** format python files to pass ruff format --check ([c7090a0](https://github.com/nguyenduydan/security-sast-guard-plugin/commit/c7090a06b633b869c1a2199310567a984fd96c38))

## [1.0.0](https://github.com/nguyenduydan/security-sast-guard-plugin/compare/v0.10.1...v1.0.0) (2026-08-06)


### ⚠ BREAKING CHANGES

* **core:** Complete architectural upgrade to v1.0.0 including cross-platform FirewallEngine, Stdio MCP Server for Antigravity 2.0, Multi-project profile resolution, and AI response caching.

### 🚀 Features & SAST Security Rules

* **core:** major release v1.0.0 with cross-platform firewall, mcp server, and multi-project support ([8049ee5](https://github.com/nguyenduydan/security-sast-guard-plugin/commit/8049ee5df8299ae185daeb147dc6b40ee73016b4))
* **dock:** implement proximity hover zone wrapper so dock expands when cursor approaches ([7993aac](https://github.com/nguyenduydan/security-sast-guard-plugin/commit/7993aac680a42b6ddc08cc07a71665ce440d51d6))
* **dock:** implement smart HUD dock collapse on idle and expand on hover ([3e573ce](https://github.com/nguyenduydan/security-sast-guard-plugin/commit/3e573ce82fb1ba91f06a9f0fe3094b3060429e6e))
* **ui:** add high-tech cyber grid patterns and ambient glow orbs to enrich page background ([2e2c75d](https://github.com/nguyenduydan/security-sast-guard-plugin/commit/2e2c75db00b95dbe8b18f7039ec60cb88bac7804))
* **ui:** add scroll-to-top button with smooth scrolling and dynamic visibility ([674231b](https://github.com/nguyenduydan/security-sast-guard-plugin/commit/674231bc809c743b01ed656369ea60fdd9421a6f))
* **ui:** redesign Hero section with high-impact headline, fresh slogan, animated badges, and terminal demo CTA ([5affc93](https://github.com/nguyenduydan/security-sast-guard-plugin/commit/5affc9385ad8c9832a45c3a62be6a3fd4d5ee7a8))


### 🐛 Bug Fixes

* **cli:** add firewall and version command handlers to CLI dispatcher ([359548f](https://github.com/nguyenduydan/security-sast-guard-plugin/commit/359548f754cee6a4a3c05ab86c8050f5ab740566))
* **cli:** add firewall and version command handlers to CLI dispatcher ([c821399](https://github.com/nguyenduydan/security-sast-guard-plugin/commit/c82139936d45914dc2df794ee28fd1e6f390d973))
* **dock:** detach collapsed items from flex flow using position absolute to eliminate asymmetrical whitespace ([bf2bf66](https://github.com/nguyenduydan/security-sast-guard-plugin/commit/bf2bf66a3d5a4735644dcadef9c11a87ca238690))
* **hooks:** implement functional audit hook and add missing sast-audit-level command definition ([706c60a](https://github.com/nguyenduydan/security-sast-guard-plugin/commit/706c60aba23c71b1c9d32b8f4fad1c99ea07c785))
* **hooks:** implement functional audit hook and add missing sast-audit-level command definition ([b8cf0e7](https://github.com/nguyenduydan/security-sast-guard-plugin/commit/b8cf0e7a741d816e74e953f3027023d2b581db6d))
* **js:** bind all interactive event handlers to window object ([f9b0091](https://github.com/nguyenduydan/security-sast-guard-plugin/commit/f9b0091ff38ec6e58c732bbd39f66c3af9017f30))
* **linter:** achieve 10.00/10 pylint score and 0 mypy errors ([d10d12e](https://github.com/nguyenduydan/security-sast-guard-plugin/commit/d10d12e1ffbe126e1ca8ee6dbb730a9369d8221b))
* **manifest:** synchronize version to 0.10.0 and add CI version check ([cab0919](https://github.com/nguyenduydan/security-sast-guard-plugin/commit/cab0919d22437f8ce171e178e699440e1cff5fc9))
* **manifest:** synchronize version to 0.10.0 and add CI version check ([1cb6ad1](https://github.com/nguyenduydan/security-sast-guard-plugin/commit/1cb6ad1c8d9430f2f86870133c6f9026246419d6))
* **nav:** add scroll-margin-top and refine Capabilities heading to prevent overscrolling ([8f650eb](https://github.com/nguyenduydan/security-sast-guard-plugin/commit/8f650ebe17de4a7fac4b8df89c35d920ed8db5de))
* **ui:** reorder workflow section to match dock sequence and pre-populate step 1 HTML ([c5a0031](https://github.com/nguyenduydan/security-sast-guard-plugin/commit/c5a00314f053ff6fa66e0984a498f664ea55dd4e))


### ⚡ Performance Improvements

* **dock:** implement 60fps hardware-accelerated cubic-bezier transition engine for silk-smooth dock expansion ([24dbf7c](https://github.com/nguyenduydan/security-sast-guard-plugin/commit/24dbf7c9df188dd0d8541911a31d16b0fb8905c3))


### 📦 Build System & Dependencies

* **ci:** add gemini-extension.json to release-please extra-files ([684dd4d](https://github.com/nguyenduydan/security-sast-guard-plugin/commit/684dd4ddd0b3cab651db7cdcdd420162479e43cd))


### 📝 Documentation

* **plans:** add SP-1 critical fixes implementation plan ([e174150](https://github.com/nguyenduydan/security-sast-guard-plugin/commit/e174150275d4641786aa3df2048685e91af785de))
* **specs:** add production readiness design spec for 5 sub-projects ([03c0c88](https://github.com/nguyenduydan/security-sast-guard-plugin/commit/03c0c88264d9268323726e5f84ef4f1419b86082))
* synchronize version badges and CLI references across README and landing page ([be1e177](https://github.com/nguyenduydan/security-sast-guard-plugin/commit/be1e177e2863492199562a1ec353180a3e7ad34f))
* **ui:** enhance landing page hero with quick install widget and 4 pillars badges ([3473707](https://github.com/nguyenduydan/security-sast-guard-plugin/commit/3473707b30506b74d12278e71c7813b6f7c2d69a))
* **ui:** extract CSS and JS into docs/style and add animated workflow step demonstrator ([03084b8](https://github.com/nguyenduydan/security-sast-guard-plugin/commit/03084b82cb57bd5cc7dcb2df0436ba25a0cb2da8))
* **ui:** overhaul usage section with v1.0.0 commands, larger typography, and MCP server reference ([771537a](https://github.com/nguyenduydan/security-sast-guard-plugin/commit/771537a7632e6117539bbe6be607eef19e8e73e4))
* update README and landing page with v1.0.0 features, MCP integration, and architecture ([06b5f7f](https://github.com/nguyenduydan/security-sast-guard-plugin/commit/06b5f7fe89ba517cd290e3e1a1b93bcac113d447))


### 🎨 Code Style & Formatting

* **dock:** fix cyber-dock border class to valid Tailwind border-2 class ([d611e84](https://github.com/nguyenduydan/security-sast-guard-plugin/commit/d611e84aba0b63139a4bf416f1f28eef649d2777))
* **dock:** increase flex gap and item padding so Audit and Capabilities have distinct separation ([7bd2635](https://github.com/nguyenduydan/security-sast-guard-plugin/commit/7bd2635574b07da05346b2302d4e44b753f61f01))
* **dock:** keep dock shadow constant at 4px without size expansion on hover ([dd1075f](https://github.com/nguyenduydan/security-sast-guard-plugin/commit/dd1075fc9eb7c2673496f1d7b3bfdbcc85c7f885))
* **dock:** optimize Cyber Dock layout flex-nowrap to prevent Install button overflow ([5e27e71](https://github.com/nguyenduydan/security-sast-guard-plugin/commit/5e27e7150a41789d098da2ff45acfb9204aa5c9e))
* **dock:** redesign INSTALL button with high-contrast emerald CTA styling and icon ([ddcb5e3](https://github.com/nguyenduydan/security-sast-guard-plugin/commit/ddcb5e3e57ac4e9d4f1bafc752490618d7ff945d))
* **dock:** replace display:none with smooth max-width and opacity spring transition for dock expansion ([2d482e4](https://github.com/nguyenduydan/security-sast-guard-plugin/commit/2d482e4aed5c676528fb866d7294763a6395c895))
* **hero:** center-align hero badges, headline, subtext slogan, and CTA buttons ([7598485](https://github.com/nguyenduydan/security-sast-guard-plugin/commit/75984858351f66957413770547015b8b85bf197e))
* **layout:** add min-h-[85vh] and vertical centering across main sections to prevent next section overlap ([9320dcf](https://github.com/nguyenduydan/security-sast-guard-plugin/commit/9320dcf2315308c733887ac368afa1762f9ca16f))
* **linter:** fix ruff check and formatting warnings ([9234e11](https://github.com/nguyenduydan/security-sast-guard-plugin/commit/9234e1147aca6dd905893af96f5551f4370d635e))
* **linter:** fix ruff check and formatting warnings ([2dc9999](https://github.com/nguyenduydan/security-sast-guard-plugin/commit/2dc9999c2e7ead6ce1255ca547e117264fd28d45))
* **theme:** add smooth cubic-bezier fluid dark mode transition engine and icon spin animation ([e525d10](https://github.com/nguyenduydan/security-sast-guard-plugin/commit/e525d104baa9850c12db45cd0134d7d9e284f626))
* **theme:** replace green dark shadows with crisp solid white shadows and dark backgrounds ([861d6b9](https://github.com/nguyenduydan/security-sast-guard-plugin/commit/861d6b9ee12c43ebf6ba7ff24b201cab96a9a60c))
* **tui:** optimize ASCII character padding and encoding compatibility for PowerShell scripts ([6369f16](https://github.com/nguyenduydan/security-sast-guard-plugin/commit/6369f16a813e7c294db12d54e094e3e2780255b7))
* **tui:** optimize ASCII character padding and encoding compatibility for PowerShell scripts ([40d08d5](https://github.com/nguyenduydan/security-sast-guard-plugin/commit/40d08d5bf95062efbb5f8c4b0c2bbf99b0747da6))
* **tui:** restore Cyber/Neo-Brutalist TUI with UTF-8 BOM encoding ([62003e0](https://github.com/nguyenduydan/security-sast-guard-plugin/commit/62003e0fc95a2749a5949a3d16d9940c5709943f))
* **tui:** restore Cyber/Neo-Brutalist TUI with UTF-8 BOM encoding ([6d99cbe](https://github.com/nguyenduydan/security-sast-guard-plugin/commit/6d99cbe95e4a09775efd1027e8ff6aaaffe150d2))
* **tui:** upgrade install, update, and remove scripts with Cyber/Neo-Brutalist TUI ([236f52d](https://github.com/nguyenduydan/security-sast-guard-plugin/commit/236f52d46c4be9b4a29e51c1aaafdca726e5a090))
* **tui:** upgrade install, update, and remove scripts with Cyber/Neo-Brutalist TUI ([d5e2569](https://github.com/nguyenduydan/security-sast-guard-plugin/commit/d5e2569034eb227dabfe3fe2dd7bdb5ac4c06ab7))
* **ui:** enforce pure white text color on all green background elements ([a0aafae](https://github.com/nguyenduydan/security-sast-guard-plugin/commit/a0aafae3fc970c9f32617b5b6b90446ac81d85bc))
* **ui:** reduce padding on cyber-dock, metrics, bento grid, and workflow cards for a sleek layout ([8249275](https://github.com/nguyenduydan/security-sast-guard-plugin/commit/82492755482f129c38a00395bcf3a372a47ce454))
* **ui:** refine scroll-to-top button styling with harmonious colors and reduced 2px shadow ([b02210a](https://github.com/nguyenduydan/security-sast-guard-plugin/commit/b02210aa94c5880f60da6ab4da3d77aec95956a2))

## [0.10.1](https://github.com/nguyenduydan/security-sast-guard-plugin/compare/v0.10.0...v0.10.1) (2026-08-06)


### 🐛 Bug Fixes

* **status:** reload profile dynamically and include sast rule counts in status ([cfdf89d](https://github.com/nguyenduydan/security-sast-guard-plugin/commit/cfdf89d906164093fb74b9f79c266be921d0d547))


### 📝 Documentation

* **rules:** enforce mandatory local CI/CD and linter checks before push ([bd208b0](https://github.com/nguyenduydan/security-sast-guard-plugin/commit/bd208b09bc61e3430d576654845dc2d31eb7e600))


### 🎨 Code Style & Formatting

* **linter:** resolve pylint warnings and achieve 10.00/10 rating ([2fd4ea7](https://github.com/nguyenduydan/security-sast-guard-plugin/commit/2fd4ea79b210536c2af5b33435383d33ceb49de4))

## [0.10.0](https://github.com/nguyenduydan/security-sast-guard-plugin/compare/v0.9.0...v0.10.0) (2026-08-05)


### 🚀 Features & SAST Security Rules

* **security:** comprehensive firewall deny rules, unified audit level, and interactive docs ([59f4eee](https://github.com/nguyenduydan/security-sast-guard-plugin/commit/59f4eee06015f287ad91f13d7787d321e41a599d))

## [0.9.0](https://github.com/nguyenduydan/security-sast-guard-plugin/compare/v0.8.0...v0.9.0) (2026-08-05)


### 🚀 Features & SAST Security Rules

* **domain:** add action field to Finding domain model ([f33f3fa](https://github.com/nguyenduydan/security-sast-guard-plugin/commit/f33f3fa9b34f78d70375cb3ccc56f1f26eac231e))
* **rules:** add destructive git command firewall and SAST rules ([2034352](https://github.com/nguyenduydan/security-sast-guard-plugin/commit/20343528c46f9bf0c9306843b7ccb92fabf35629))
* **sast:** extract action metadata from markdown rules ([5b411d5](https://github.com/nguyenduydan/security-sast-guard-plugin/commit/5b411d558f9e9d03cdc9efbb447958c190f266b1))
* **sast:** map rule action to finding dataclass in SASTScanner ([89d006a](https://github.com/nguyenduydan/security-sast-guard-plugin/commit/89d006a7f40659a4898a4290b7c4af733323d0da))


### 🐛 Bug Fixes

* **mypy:** add mypy_path to pyproject.toml to resolve module imports ([9d04fa9](https://github.com/nguyenduydan/security-sast-guard-plugin/commit/9d04fa981fa3a197fb5da71f6aedc3cf622f0f4e))


### 🎨 Code Style & Formatting

* **lint:** resolve pylint warnings and trailing whitespace ([4dda628](https://github.com/nguyenduydan/security-sast-guard-plugin/commit/4dda62808b59d68f5e005da06bb21c9790ecb21b))
* **lint:** resolve pylint warnings in git_helper, report_generator, and tests ([5b3806b](https://github.com/nguyenduydan/security-sast-guard-plugin/commit/5b3806b7635f102f4be542e7db4e72ef47689fdc))
* **ruff:** format git_helper.py and report_generator.py ([c506245](https://github.com/nguyenduydan/security-sast-guard-plugin/commit/c50624573aa893717e011216aa19f887ba0e7840))
* **ruff:** format models.py to fix formatting CI check ([1032490](https://github.com/nguyenduydan/security-sast-guard-plugin/commit/1032490a6d71f67a3ef1498baa98002d97f13679))


### Maintenance & Tooling

* **sast:** commit plans, specs, and helper modules ([e79b983](https://github.com/nguyenduydan/security-sast-guard-plugin/commit/e79b9833f980249aa65e30fdfab0b452286dd646))

## [0.8.0](https://github.com/nguyenduydan/security-sast-guard-plugin/compare/v0.7.0...v0.8.0) (2026-08-05)


### 🚀 Features & SAST Security Rules

* **security:** implement anti-bypass firewall, integrity checker, and clean architecture ([8433a83](https://github.com/nguyenduydan/security-sast-guard-plugin/commit/8433a83db59b4f3ba14cf6c6bc508fb572afa1af))


### 🐛 Bug Fixes

* **ci:** satisfy ruff linter UP042, W291, and S603 rules ([3466046](https://github.com/nguyenduydan/security-sast-guard-plugin/commit/346604617dd3be4097b245cb2c9236f6177e2d2e))
* **firewall:** strongly type tokens and errors arrays for pwsh 7 AST parser compatibility ([3f5fd1b](https://github.com/nguyenduydan/security-sast-guard-plugin/commit/3f5fd1b6f677c04d20fac4ffd1effcdebc2bcfbf))
* **firewall:** type AST parser reference arrays ([52d239a](https://github.com/nguyenduydan/security-sast-guard-plugin/commit/52d239a72a6ed6ef1270b636348577c9f7c1c0b9))
* **firewall:** use Split-Path -Parent for cross-platform profile path resolution in pwsh ([83774e5](https://github.com/nguyenduydan/security-sast-guard-plugin/commit/83774e5be391398c87be092057a0cc6bd245cbaa))
* **quality:** polish CI quality checks, ruff formatting, and report generator ([9ebd063](https://github.com/nguyenduydan/security-sast-guard-plugin/commit/9ebd063b9b7f4cdab310d28d3f91da1c2aea8d35))
* **quality:** polish line length and format for CI quality gate ([a104ea4](https://github.com/nguyenduydan/security-sast-guard-plugin/commit/a104ea4fa63869be29f178b1aeca8e88e394bb8d))
* stop tracking .profile.sha256, normalize profile.json to LF ([dcdad30](https://github.com/nguyenduydan/security-sast-guard-plugin/commit/dcdad30c696e8400c40c4d9ceebe1f5cd5601277))


### ♻️ Refactoring & Code Hygiene

* **quality:** resolve R0914 too-many-locals in report_generator to reach 10.00/10 pylint rating ([1c218fc](https://github.com/nguyenduydan/security-sast-guard-plugin/commit/1c218fc3ce42f3a0f60970bb78579f862079f002))


### 📝 Documentation

* **index:** redesign navigation to 100% opaque floating cyber-hud dock ([501144a](https://github.com/nguyenduydan/security-sast-guard-plugin/commit/501144ac71258bf43846bb637b400e21ead0139a))

## [0.7.0](https://github.com/nguyenduydan/security-sast-guard-plugin/compare/v0.6.0...v0.7.0) (2026-08-04)


### 🚀 Features & SAST Security Rules

* **report:** export SAST audit findings to Markdown report ([72f7e01](https://github.com/nguyenduydan/security-sast-guard-plugin/commit/72f7e01a456cf8b9534d6b786ec220c9eee2dcf6))
* **rules:** implement rule sync engine for Markdown security rules ([3d935f0](https://github.com/nguyenduydan/security-sast-guard-plugin/commit/3d935f02cdfcc7d1e61044d65cb22ff518c606c7))
* **scanner:** enhance SAST scanning engine, sync markdown rules, and generate Markdown reports ([b9db0ec](https://github.com/nguyenduydan/security-sast-guard-plugin/commit/b9db0ec167f6b348d7fa64581b1d7772764a3731))
* **scanner:** implement real regex pattern matching engine ([a18af7a](https://github.com/nguyenduydan/security-sast-guard-plugin/commit/a18af7ab59a5c3eeb449b9b0b2df7fe9c19bfcef))


### 🐛 Bug Fixes

* **ci:** fix ruff formatting and linter issues for CI quality gate ([8878acb](https://github.com/nguyenduydan/security-sast-guard-plugin/commit/8878acb988452569b542a672ab9597dc7d74ec34))
* **report:** ensure safe ASCII formatting for Windows stdout report summaries ([a00e171](https://github.com/nguyenduydan/security-sast-guard-plugin/commit/a00e171d9435a4b82a318e7855b33d16aaad46ac))
* resolve Ruff E501 line length violations ([14f1216](https://github.com/nguyenduydan/security-sast-guard-plugin/commit/14f121675c5f0f67106c55ac07b887283aea2334))
* satisfy Ruff formatting ([61b58e1](https://github.com/nguyenduydan/security-sast-guard-plugin/commit/61b58e12759094257d65690d3fa33cb2295750a0))


### ♻️ Refactoring & Code Hygiene

* **quality:** resolve R0914 too-many-locals warnings to reach 10.00/10 pylint rating ([bdf515e](https://github.com/nguyenduydan/security-sast-guard-plugin/commit/bdf515e7450150dac30910d13dd68b6f0fcbc9ee))

## [0.6.0](https://github.com/nguyenduydan/security-sast-guard-plugin/compare/v0.5.10...v0.6.0) (2026-08-04)


### 🚀 Features & SAST Security Rules

* **cli:** add status command to display security profile ([aaeb59f](https://github.com/nguyenduydan/security-sast-guard-plugin/commit/aaeb59fffdf55b8736693da40cd34a54c1051f7a))
* **cli:** add status command to display security profile ([06b7a80](https://github.com/nguyenduydan/security-sast-guard-plugin/commit/06b7a8037c5cfebdb77f34d7402765eec9946def))


### 🐛 Bug Fixes

* **ci:** add pytest dependency to pylint workflow and disable import-error ([f2f857e](https://github.com/nguyenduydan/security-sast-guard-plugin/commit/f2f857e0fe1fab6c82e547ff1ae29e7706739500))


### 🎨 Code Style & Formatting

* **cli:** fix code formatting and trailing newlines for CI quality gate ([fa09c96](https://github.com/nguyenduydan/security-sast-guard-plugin/commit/fa09c96b1ca609b424ddc847f7559ae954f41889))


### Maintenance & Tooling

* **ui:** update ui ([f1b03be](https://github.com/nguyenduydan/security-sast-guard-plugin/commit/f1b03beb5e630c80fca357c55e531dd3e50d03a2))

## [0.5.10](https://github.com/nguyenduydan/security-sast-guard-plugin/compare/v0.5.9...v0.5.10) (2026-08-04)


### ♻️ Refactoring & Code Hygiene

* **tui:** improve installer progress bar visuals ([ea75048](https://github.com/nguyenduydan/security-sast-guard-plugin/commit/ea75048e21492ab2991120e5cb3e6cd279e1f578))

## [0.5.9](https://github.com/nguyenduydan/security-sast-guard-plugin/compare/v0.5.8...v0.5.9) (2026-08-04)


### 🐛 Bug Fixes

* **remove:** avoid deleting plugin from active directory ([e96fea7](https://github.com/nguyenduydan/security-sast-guard-plugin/commit/e96fea7f3775d8b005e38de31b93a669a2fcdf37))

## [0.5.8](https://github.com/nguyenduydan/security-sast-guard-plugin/compare/v0.5.7...v0.5.8) (2026-08-04)


### 🐛 Bug Fixes

* **tui:** stabilize ANSI Shadow logo rendering in PowerShell ([d65ab2c](https://github.com/nguyenduydan/security-sast-guard-plugin/commit/d65ab2ca147f474036a82aa0a85a3f4d3022cf9e))

## [0.5.7](https://github.com/nguyenduydan/security-sast-guard-plugin/compare/v0.5.6...v0.5.7) (2026-08-04)


### 🐛 Bug Fixes

* **installer:** fallback to GitHub source archive when ZIP is missing ([b090c70](https://github.com/nguyenduydan/security-sast-guard-plugin/commit/b090c70d1eef83da0d7a2581ff65d83efefd044d))

## [0.5.6](https://github.com/nguyenduydan/security-sast-guard-plugin/compare/v0.5.5...v0.5.6) (2026-08-04)


### 🐛 Bug Fixes

* **installer:** handle missing release assets and stabilize terminal logo ([562e1b1](https://github.com/nguyenduydan/security-sast-guard-plugin/commit/562e1b181ee22bd9f7c6fe8ad4358677d6e5fcac))

## [0.5.5](https://github.com/nguyenduydan/security-sast-guard-plugin/compare/v0.5.4...v0.5.5) (2026-08-04)


### 🐛 Bug Fixes

* **install:** fix bug dont install ([f9ae85c](https://github.com/nguyenduydan/security-sast-guard-plugin/commit/f9ae85c3149809e76d24eb0f2bad34ddf10570dc))
* **release:** fix release ([bc6d5cf](https://github.com/nguyenduydan/security-sast-guard-plugin/commit/bc6d5cf480178be29439eabebf122246ba169ca0))

## [0.5.4](https://github.com/nguyenduydan/security-sast-guard-plugin/compare/v0.5.3...v0.5.4) (2026-08-04)


### 🐛 Bug Fixes

* **installer:** remove GitHub CLI dependency from downloads ([#38](https://github.com/nguyenduydan/security-sast-guard-plugin/issues/38)) ([876c5ea](https://github.com/nguyenduydan/security-sast-guard-plugin/commit/876c5ea506ada66d5e450c1cb9d09217e3c44bb0))

## [0.5.3](https://github.com/nguyenduydan/security-sast-guard-plugin/compare/v0.5.2...v0.5.3) (2026-08-04)


### ♻️ Refactoring & Code Hygiene

* **release:** streamline runtime package and installer TUI ([0ecae6e](https://github.com/nguyenduydan/security-sast-guard-plugin/commit/0ecae6e804f42462579e67015c859e31c3d22797))
* **release:** streamline runtime package and installer TUI ([feee0db](https://github.com/nguyenduydan/security-sast-guard-plugin/commit/feee0db3915efdca942822510f4760c1d4f1ad47))

## [0.5.2](https://github.com/nguyenduydan/security-sast-guard-plugin/compare/v0.5.1...v0.5.2) (2026-08-04)


### 🐛 Bug Fixes

* **update:** release plugin directory before replacement ([4957fea](https://github.com/nguyenduydan/security-sast-guard-plugin/commit/4957fea212cb89a5e7d43e39b7bc0759642b6645))
* **update:** release plugin directory before replacement ([288fe2c](https://github.com/nguyenduydan/security-sast-guard-plugin/commit/288fe2ce1d56db188a9c8fded601a2ad476b048c))

## [0.5.1](https://github.com/nguyenduydan/security-sast-guard-plugin/compare/v0.5.0...v0.5.1) (2026-08-04)


### 🐛 Bug Fixes

* **docs:** resolve GitHub Pages asset paths ([9fea842](https://github.com/nguyenduydan/security-sast-guard-plugin/commit/9fea84210c29ac19a0098f9051d81e515e243756))
* **docs:** resolve GitHub Pages asset paths ([c05851f](https://github.com/nguyenduydan/security-sast-guard-plugin/commit/c05851f15f5d0702c3f4202e841364e5b225747d))


### Maintenance & Tooling

* **avt:** add branding assets, site metadata and update readme ([2d69612](https://github.com/nguyenduydan/security-sast-guard-plugin/commit/2d6961276aaaba2d94dd79b5d4849620c3df2a1b))
* **avt:** add branding assets, site metadata and update readme ([5ebd337](https://github.com/nguyenduydan/security-sast-guard-plugin/commit/5ebd3373d885c5d1088b26008a8698393949513a))
* move index.html ([5d51b3e](https://github.com/nguyenduydan/security-sast-guard-plugin/commit/5d51b3ed37acc7d6b7af1c998cc033377736ef58))
* move index.html ([4feadd5](https://github.com/nguyenduydan/security-sast-guard-plugin/commit/4feadd579ca7eee0163e6fc4634ef57972acadd2))

## [0.5.0](https://github.com/nguyenduydan/security-sast-guard-plugin/compare/v0.4.3...v0.5.0) (2026-08-04)


### 🚀 Features & SAST Security Rules

* **landing:** add GitHub Releases API live version sync and dual-theme neo-brutalist UI ([12a06fb](https://github.com/nguyenduydan/security-sast-guard-plugin/commit/12a06fb2b0665762be0881f23e1022fbe9d90f50))
* **landing:** GitHub Releases API live version sync & dual-theme neo-brutalist UI ([9b48fab](https://github.com/nguyenduydan/security-sast-guard-plugin/commit/9b48fabb4fbcaa028610a00d3e60dcc7fa2984a2))

## [0.4.3](https://github.com/nguyenduydan/security-sast-guard-plugin/compare/v0.4.2...v0.4.3) (2026-08-04)


### 🐛 Bug Fixes

* **ci:** disable auto-merge for release-please PRs ([e109169](https://github.com/nguyenduydan/security-sast-guard-plugin/commit/e109169639cba35b725ab618053d11bf9173dfeb))
* **ci:** skip release-please when commit is a release to prevent double version bump ([#27](https://github.com/nguyenduydan/security-sast-guard-plugin/issues/27)) ([d4a51b6](https://github.com/nguyenduydan/security-sast-guard-plugin/commit/d4a51b69effaa44d08d17a67dba75be16980506a))

## [0.4.2](https://github.com/nguyenduydan/security-sast-guard-plugin/compare/v0.4.1...v0.4.2) (2026-08-04)


### 📝 Documentation

* **gemini:** treat chore and refactor as patch triggers ([#23](https://github.com/nguyenduydan/security-sast-guard-plugin/issues/23)) ([888f35a](https://github.com/nguyenduydan/security-sast-guard-plugin/commit/888f35a5f68cacfbe0a16de5040c908a3603072c))

## [0.4.1](https://github.com/nguyenduydan/security-sast-guard-plugin/compare/v0.4.0...v0.4.1) (2026-08-04)


### 📝 Documentation

* **gemini:** define strict rules for conventional commits usage ([#21](https://github.com/nguyenduydan/security-sast-guard-plugin/issues/21)) ([37210c7](https://github.com/nguyenduydan/security-sast-guard-plugin/commit/37210c7dc30e193534cd2261df72b47adbba1049))

## [0.4.0](https://github.com/nguyenduydan/security-sast-guard-plugin/compare/v0.3.0...v0.4.0) (2026-08-04)


### 🚀 Features & SAST Security Rules

* **skill:** add proactive auditor design and script fixes ([#19](https://github.com/nguyenduydan/security-sast-guard-plugin/issues/19)) ([7abd1ef](https://github.com/nguyenduydan/security-sast-guard-plugin/commit/7abd1ef54249edfe4cef350ce683a7f26cfe54fb))

## [0.3.0](https://github.com/nguyenduydan/security-sast-guard-plugin/compare/v0.2.0...v0.3.0) (2026-08-04)


### 🚀 Features & SAST Security Rules

* **ci:** automate merging for release-please PRs ([7ea92ec](https://github.com/nguyenduydan/security-sast-guard-plugin/commit/7ea92ecb25cba78b4496efd7932e7de29362510d))
* **ci:** automate merging for release-please PRs ([4b96b28](https://github.com/nguyenduydan/security-sast-guard-plugin/commit/4b96b2843c990f17dbacdd1e2b506ad7635118a5))


### 🐛 Bug Fixes

* **ci:** provide repo flag to gh pr merge ([f426a72](https://github.com/nguyenduydan/security-sast-guard-plugin/commit/f426a72e83a55942f4b0cf27b39998ee5a639e78))
* **ci:** provide repo flag to gh pr merge ([67dd77f](https://github.com/nguyenduydan/security-sast-guard-plugin/commit/67dd77f657130258c37634f51f6ffa9403006e94))

## [0.2.0](https://github.com/nguyenduydan/security-sast-guard-plugin/compare/v0.1.0...v0.2.0) (2026-08-04)


### 🚀 Features & SAST Security Rules

* tuning improvements for firewall, sast scanner, and delivery ([#8](https://github.com/nguyenduydan/security-sast-guard-plugin/issues/8)) ([1fa4862](https://github.com/nguyenduydan/security-sast-guard-plugin/commit/1fa4862dab24586405f013194bd61ff6fa5c9dd7))


### 🐛 Bug Fixes

* **ci:** comprehensively resolve pylint and mypy errors across codebase ([#12](https://github.com/nguyenduydan/security-sast-guard-plugin/issues/12)) ([d39597f](https://github.com/nguyenduydan/security-sast-guard-plugin/commit/d39597f1349b9d43e4fbc861e960736cf3bf89b2))
* force version bump for release-please ([c39a442](https://github.com/nguyenduydan/security-sast-guard-plugin/commit/c39a4421362d93d1793223e790522d68ae9160f5))
* **release-please:** migrate config to v4 schema ([5a9a60a](https://github.com/nguyenduydan/security-sast-guard-plugin/commit/5a9a60a26cff0392199de27288f2f8e335b29e11))
* **release-please:** migrate config to v4 schema ([4bb5944](https://github.com/nguyenduydan/security-sast-guard-plugin/commit/4bb59448f651dc7b2ce7ba5a42cc5e6924e10b37))
* **release:** force trigger release-please to bump version ([4b65a27](https://github.com/nguyenduydan/security-sast-guard-plugin/commit/4b65a2794edfdc24438f2e29e6b08cb46c0d9e80))
* **release:** sync plugin version and setup release-please config ([d102df6](https://github.com/nguyenduydan/security-sast-guard-plugin/commit/d102df64a6775dd9da16d2376dd5ef7068feedf7))
* reset release-please branch state ([dfebbfe](https://github.com/nguyenduydan/security-sast-guard-plugin/commit/dfebbfef5d7be7405026ef4af506165c1b71daba))
* **sast-status:** optimize skill and update gemini workflows ([b03d917](https://github.com/nguyenduydan/security-sast-guard-plugin/commit/b03d91709557f08d9fa6add39a2ace4cb57cc7dd))
* **sast-status:** optimize skill to prevent unnecessary file reading ([25b022b](https://github.com/nguyenduydan/security-sast-guard-plugin/commit/25b022be785a3d6c2fc0fa71ac66d538294c39f5))


### 📝 Documentation

* add release and git flow rules to GEMINI.md ([a003292](https://github.com/nguyenduydan/security-sast-guard-plugin/commit/a0032928cbbd3a1ccc2cc301bb35f8e75810abe5))
* consolidate SECURITY.md into .github folder ([#7](https://github.com/nguyenduydan/security-sast-guard-plugin/issues/7)) ([68d9b70](https://github.com/nguyenduydan/security-sast-guard-plugin/commit/68d9b70a98ae4ef39d652e1b2b44a9aca46dce22))
* **gemini:** detail agent git workflow ([4970317](https://github.com/nguyenduydan/security-sast-guard-plugin/commit/497031766f922ad4176d2ed675d5e2bd778f22d6))
* **gemini:** enforce testing and linting before commit ([72baaba](https://github.com/nguyenduydan/security-sast-guard-plugin/commit/72baabab96b2a153cce131424104c3d46f2020ef))
* **gemini:** require scope in conventional commits ([1be0e22](https://github.com/nguyenduydan/security-sast-guard-plugin/commit/1be0e22c3caeff09b01183643b6e91f12b02ca06))
* modernize and redesign README with security aesthetic and packaging guide ([#5](https://github.com/nguyenduydan/security-sast-guard-plugin/issues/5)) ([2c9ec29](https://github.com/nguyenduydan/security-sast-guard-plugin/commit/2c9ec29fcac8c9ccef5f78f750f1915fc2bd6a1f))
* rewrite security policy and ignore .superpowers ([#6](https://github.com/nguyenduydan/security-sast-guard-plugin/issues/6)) ([00954e7](https://github.com/nguyenduydan/security-sast-guard-plugin/commit/00954e794e3f9abd59a04de4224cb1596daa293e))
* **superpowers:** add release-please v4 migration design ([9d7d0ef](https://github.com/nguyenduydan/security-sast-guard-plugin/commit/9d7d0ef687c3c6e8ae211b81a24a5eb2a7870df9))
* **superpowers:** add release-please v4 migration plan ([b59cc89](https://github.com/nguyenduydan/security-sast-guard-plugin/commit/b59cc89168c6c3621e5d4f1854a0b5d2730feabc))


### 🎨 Code Style & Formatting

* fix ruff linter line length issues in domain modules ([32686a0](https://github.com/nguyenduydan/security-sast-guard-plugin/commit/32686a0b01760e45b642930b56b6ef24ae6dd5fc))

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
