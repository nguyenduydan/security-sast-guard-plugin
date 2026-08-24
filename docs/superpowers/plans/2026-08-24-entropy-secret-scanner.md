# Implementation Plan - Shannon Entropy Secret & Token Sniffer (Integrated in Audit)

**Date:** 2026-08-24
**Author:** Antigravity / DeepMind

## Goal
Integrate High-Precision Shannon Entropy and Provider Token Signature detection directly into the core SAST Audit pipeline (`sast scan`, `sast audit`, `/sast-audit`, `sast_scan_file`, `sast_scan_diff`).

## Architecture & Design
1. `src/domain/entropy_detector.py`:
   - Math: \(H(S) = -\sum_{c \in \Sigma} P(c) \log_2 P(c)\).
   - High-Precision Thresholds:
     - Base64: min length >= 24, \(H \ge 4.5\).
     - Hex: min length >= 32, \(H \ge 3.4\).
     - Required security context keywords: `key`, `secret`, `token`, `password`, `auth`, `api`, `credential`, `private`, `bearer`, `access`.
   - Provider Signatures: OpenAI (`sk-...`), GitHub (`ghp_...`), AWS (`AKIA...`), Anthropic (`sk-ant-...`), Stripe (`sk_live_...`), Slack (`xoxb-...`), Private Keys (`-----BEGIN ... PRIVATE KEY-----`).
   - False positive filters: UUIDs, placeholders, image data URIs, common test patterns.
2. `src/domain/sast_scanner.py`:
   - Instantiate `ShannonEntropyDetector` inside `SASTScanner`.
   - In `_detect_matches_file()`, invoke entropy and signature detection seamlessly on non-comment code lines, adding findings with severity `Critical` / `High`.
3. `src/domain/cwe_owasp_mapper.py`:
   - Register `HIGH_ENTROPY_SECRET` (CWE-798, A07:2021) and `TOKEN_SIGNATURE_LEAK` (CWE-312, A02:2021).
4. `tests/test_entropy_detector.py`:
   - Full test coverage for math, token signatures, false positive filtering, and integrated SAST audit scanning.
