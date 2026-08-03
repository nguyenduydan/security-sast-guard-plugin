# Implementation Plan: Tuning Improvements

## 1. Native PowerShell Firewall
- **File:** `hooks/firewall_hook.ps1`
- **Task:** Re-implement firewall in PowerShell utilizing `[System.Management.Automation.Language.Parser]` to eliminate python boot overhead.
- **Status:** DONE

## 2. Reduce SAST Alert Fatigue
- **File:** `src/domain/context_extractor.py`
- **Task:** Integrate python `tokenize` module to check if SAST rule matches are inside safe contexts (comments/strings).
- **Status:** DONE

## 3. Draft Mode (Vibe Preservation)
- **File:** `profile.json`, `src/domain/sast_scanner.py`
- **Task:** Introduce `mode: draft`. Auto-allow MEDIUM/LOW alerts to preserve user workflow.
- **Status:** DONE

## 4. Secure Distribution
- **File:** `.github/workflows/release.yml`, `update.ps1`, `install.ps1`
- **Task:** Package zip cleanly via `git archive`, generate SHA256 checksum, and verify checksum on installation.
- **Status:** DONE
