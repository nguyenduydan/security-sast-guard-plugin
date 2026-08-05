# Implementation Plan: Anti-Bypass, Tamper Resistance & Command Firewall Upgrade

**Date:** 2026-08-05  
**Spec:** [docs/superpowers/specs/2026-08-05-anti-bypass-tamper-resistance-design.md](file:///D:/AI/tools/security-sast-guard/docs/superpowers/specs/2026-08-05-anti-bypass-tamper-resistance-design.md)  
**Target Branch:** `feat/anti-bypass-firewall`  

---

## Proposed Tasks

### Task 1: Create Development Branch & Harden Fail-Closed Behavior
- Create git branch `feat/anti-bypass-firewall`.
- Update `hooks/firewall_hook.ps1` to output `DENY` (instead of `ALLOW`) if `profile.json` is missing or corrupted.
- Wrap execution in a robust `try { ... } catch { Write-Output "DENY"; exit 1 }` block.

### Task 2: Implement Base64 Deobfuscation & Escape Character Stripping
- Enhance `hooks/firewall_hook.ps1` with normalization helpers:
  - `Remove-Escapes`: Strip CMD caret (`^`) and PowerShell backtick (`` ` ``).
  - `Decode-Base64Command`: Extract and decode UTF-16LE / UTF-8 string from `-enc`, `-encodedcommand`, or `FromBase64String`.
- Feed normalized and decoded strings to both string regex matching and PowerShell AST parser.

### Task 3: Implement Profile Integrity Guard
- Implement checksum validation mechanism for `profile.json` in `firewall_hook.ps1`.
- Verify SHA-256 hash against saved `.profile.sha256`. If hash mismatches, trigger `DENY`.

### Task 4: Add Adversarial Unit Tests
- Create `tests/test_firewall_adversarial.py` to test:
  - Base64 encoded payload detection (`powershell -enc ...`).
  - Obfuscated command detection (`r^m^ -r^f`).
  - Tamper detection (modified `profile.json` triggers `DENY`).
  - Fail-closed fallback (missing config triggers `DENY`).

### Task 5: Verification & SAST Audit
- Run `pytest` test suite to verify 100% pass rate.
- Execute security audit using `/sast-audit file hooks/firewall_hook.ps1`.
- Record decision in `.aiops/decisions.jsonl`.
