# Security Policy

At **Security SAST Guard**, security is our highest priority. We take all security vulnerabilities seriously and appreciate the efforts of the security community and our users in helping us maintain the highest standards of safety for the Google Antigravity & Gemini CLI ecosystems.

## Supported Versions

We provide security updates and patches for the versions listed below. We highly recommend that all users stay on the latest stable release to ensure maximum protection against emerging threats.

| Version | Supported          | Security Patch Guarantee |
| ------- | ------------------ | ------------------------ |
| `0.x` (Latest) | :white_check_mark: | Immediate patch & release |
| Pre-release / Beta | :warning: | Best effort (patched in next stable) |
| `< 0.1` | :x:                | Unsupported              |

> **Note:** As we are currently in the early `0.x` lifecycle, we urge all users to use the auto-update scripts (`update.ps1`) to ensure they receive critical vulnerability mitigations instantly.

---

## 🛡️ Scope of Security SAST Guard

The **Security SAST Guard** plugin acts as a **Local Firewall & Static Analysis Engine**. Its primary functions are:
1. Blocking malicious or destructive commands on your local terminal (`rm -rf`, format, registry mutation).
2. Detecting software vulnerabilities (OWASP/CWE) in AI-generated code.
3. Preventing local secrets and API keys from leaking into version control.

### What is considered a vulnerability in this plugin?
- **Firewall Bypass:** Any method where a destructive shell command can bypass the `PreCommandExecute` regex overlay without triggering a `DENY` or `CONFIRM` prompt.
- **Rule Evasion:** A known malicious payload (e.g., severe SQL Injection or RCE) that circumvents our shipped 53 SAST Rules.
- **Local Sandbox Escape:** The plugin inadvertently granting the AI agent elevated permissions that were not explicitly authorized by the host system.
- **Data Exfiltration:** The plugin logic accidentally leaking user context, secrets, or API keys outside of the local environment.

### What is NOT considered a vulnerability?
- The AI hallucinating safe but logically incorrect commands.
- Vulnerabilities in the native Google Antigravity or Gemini CLI frameworks (these should be reported to the respective framework maintainers).
- Missing SAST rules for highly specific or obscure third-party libraries (we consider these **Feature Requests** rather than security incidents).

---

## 🚨 Reporting a Vulnerability

If you believe you have discovered a security vulnerability in the **Security SAST Guard** plugin, please do **NOT** open a public issue. We adhere to responsible disclosure practices to protect our users.

### Reporting Process
1. **Email us directly:** Send a detailed report to `dn135897@gmail.com`.
2. **Subject Line:** Please use the prefix `[SECURITY VULNERABILITY]` in your email subject.
3. **Include Details:** 
   - A description of the vulnerability.
   - The version of the plugin you are using.
   - Step-by-step instructions to reproduce the issue (Proof of Concept).
   - Any suggested mitigations or patches (optional but appreciated).

### Response Timeline
- **Acknowledgement:** We will acknowledge receipt of your vulnerability report within **48 hours**.
- **Triage & Assessment:** We aim to triage and confirm the severity of the issue within **3 business days**.
- **Patch Development:** Critical firewall bypasses or data exfiltration bugs will be patched and released within **7 days**.
- **Public Disclosure:** Once the patch is released and users have had a reasonable window to update (via `update.ps1`), we will publicly acknowledge your contribution in our Release Notes and Security Advisory.

---

## 🔒 Safe Harbor Policy

We strongly support security research. We will not take legal action against you or ask law enforcement to investigate you if you comply with the following:
- You conduct your research without harming our users, systems, or data.
- You do not exploit the vulnerability further than necessary to establish its existence.
- You do not publicly disclose the vulnerability until we have had a reasonable timeframe to release a patch.
- You do not attempt Denial of Service (DoS) attacks or social engineering against our maintainers.

Thank you for helping keep the open-source AI ecosystem safe and secure!
