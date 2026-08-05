# Specification: Anti-Bypass, Tamper Resistance & Command Firewall Upgrade

**Date:** 2026-08-05  
**Project:** Security SAST Guard Plugin  
**Status:** Approved  
**Author:** AI Security Supervisor Architect  

---

## 1. Overview & Objectives

Targeting the core weaknesses identified in Section 5, 6, 7 & 19 of `new-updated.md`, this specification defines the design for **Anti-Bypass Protection**, **Tamper Resistance**, and **Fail-Closed Command Firewall Engine** in the Security SAST Guard Plugin.

### Core Objectives:
1. **Deobfuscation & Normalization:** Detect and strip encoding (Base64), escaping (`^`, `` ` ``), and nested execution parameters in commands before rule evaluation.
2. **Tamper Resistance:** Detect any unauthorized modification or deletion of `profile.json` or hook files, instantly dropping into Fail-Closed (`DENY`) mode.
3. **Fail-Closed Guarantee:** Ensure that parser errors, missing config files, or script crashes result in strict `DENY` verdicts rather than silent `ALLOW`.
4. **Adversarial Test Suite:** Add tests designed to actively attempt bypasses.

---

## 2. Architecture & Components

```
+-------------------------------------------------------------------------+
|                           Agent Execution Layer                         |
|                             (PreCommandExecute)                         |
+-------------------------------------------------------------------------+
                                    |
                                    v
+-------------------------------------------------------------------------+
|                         firewall_hook.ps1                               |
|                                                                         |
|  1. Integrity Check (SHA-256 Checksum Verification of profile.json)    |
|       └─► Failed / Tampered? ──► Output "DENY" & Exit 1 (Fail-Closed)   |
|                                                                         |
|  2. Command Normalization Engine                                        |
|       ├─► Strip CMD Caret Escape (`^`) & PS Backtick (`` ` ``)         |
|       ├─► Base64 Automatic Decoder (-EncodedCommand, -enc, [Convert])   |
|       └─► Environment Variable Expansion & Quote Normalization          |
|                                                                         |
|  3. Multi-Layer Rule Evaluation (Raw Text + Normalized Text + AST Nodes)|
|       ├─► Check Deny Rules    ──► Match? ──► Output "DENY"              |
|       ├─► Check Confirm Rules ──► Match? ──► Output "CONFIRM"           |
|       └─► Default             ───────────► Output "ALLOW"               |
+-------------------------------------------------------------------------+
```

---

## 3. Component Details

### 3.1. Profile Integrity Guard (Tamper Resistance)
- **Mechanisms:**
  - A hidden/locked checksum file `.profile.sha256` or an internal signature secret.
  - Prior to parsing `profile.json`, `firewall_hook.ps1` calculates the SHA-256 hash of `profile.json`.
  - If `profile.json` does not exist, is empty, is corrupted, or hash verification fails:
    - Log security breach attempt.
    - Immediately output `DENY` and exit with non-zero code.

### 3.2. Command Normalization Engine (Deobfuscation)
- **Base64 Decoding:**
  - Detect regex patterns for `-enc`, `-encodedcommand`, `-e`, `[System.Convert]::FromBase64String`.
  - Extract the Base64 payload, decode UTF-16LE / UTF-8 text, and recursively pass the decoded string back through the normalization engine.
- **Escape Character Stripping:**
  - Remove CMD caret escapes (e.g. `p^o^w^e^r^s^h^e^l^l` ➔ `powershell`).
  - Remove PowerShell backtick escapes (e.g. `i` `e` `x` ➔ `iex`).
- **Nested Interpreter Unrolling:**
  - Extract commands wrapped inside `cmd.exe /c "..."`, `powershell.exe -Command "..."`, `wmic`, `mshta`, `cscript/wscript`.

### 3.3. Fail-Closed Error Handling
- Default `$ErrorActionPreference = "Stop"`.
- Wrap main hook logic in `try { ... } catch { Write-Output "DENY"; exit 1 }`.
- Guarantees zero `ALLOW` fallbacks on script execution failures.

---

## 4. Verification & Testing Strategy

1. **Unit Tests:**
   - Test Base64 deobfuscation (`powershell -enc ...`).
   - Test caret escaping (`r^m^ -r^f`).
   - Test missing `profile.json` triggers `DENY`.
   - Test corrupted `profile.json` triggers `DENY`.
2. **Adversarial Security Tests:**
   - Attempt bypass using nested `powershell.exe -c "cmd.exe /c powershell -enc ..."`.
   - Attempt modifying `profile.json` during runtime and verify `DENY` trigger.

---

## 5. Decision Record

- **Fail-Closed Policy:** Hardened from default `ALLOW` (on missing config) to strict `DENY`.
- **Scope:** PowerShell Hook & Python SAST Integration.
