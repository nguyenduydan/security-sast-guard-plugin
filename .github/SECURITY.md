# Security Policy

At **Security SAST Guard**, security is our highest priority. We take all security vulnerabilities seriously and appreciate the efforts of the security community and our users in helping us maintain the highest standards of safety for the Google Antigravity & Gemini CLI ecosystems.

## Supported Versions

We provide security updates and patches for the versions listed below. We highly recommend that all users stay on the latest stable release to ensure maximum protection against emerging threats.

| Version | Supported          | Security Patch Guarantee |
| ------- | ------------------ | ------------------------ |
| `2.x` (Latest) | :white_check_mark: | Immediate patch & release |
| `1.x` | :warning: | Critical security patches only |
| `< 1.0` | :x:                | Unsupported              |

> **Note:** We urge all users to use the auto-update scripts (`update.sh` on Linux/macOS or `update.ps1` on Windows) to ensure they receive critical vulnerability mitigations instantly.

---

## 🛡️ Scope of Security SAST Guard

The **Security SAST Guard** plugin acts as a **Local Firewall & Static Analysis Engine**. Its primary functions are:
1. Blocking malicious, destructive, or exfiltration shell commands on your local terminal (`rm -rf`, disk format, registry mutation, reverse shells, download-and-execute chains).
2. Detecting software vulnerabilities (OWASP Top 10, CWE Top 25, OWASP LLM Top 10) in AI-generated and human-written code across 95 vector rules.
3. Preventing local secrets and API keys from leaking into version control.

### What is considered a vulnerability in this plugin?
- **Firewall Bypass:** Any method where a destructive or exfiltrating shell command can bypass the 10-stage `FirewallNormalizer` without triggering a `DENY` or `CONFIRM` prompt.
- **Rule Evasion:** A known malicious payload (e.g., SQL Injection, Deserialization RCE, Prompt Injection) that circumvents our 95 SAST rules.
- **Local Sandbox Escape:** The plugin inadvertently granting the AI agent elevated permissions that were not explicitly authorized by the host system.
- **Data Exfiltration:** The plugin logic accidentally leaking user context, secrets, or API keys outside of the local environment.

### What is NOT considered a vulnerability?
- The AI hallucinating safe but logically incorrect code.
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
   - The version of the plugin you are using (`sast status` or `get_plugin_version()`).
   - Step-by-step instructions to reproduce the issue (Proof of Concept).
   - Any suggested mitigations or patches (optional but appreciated).

### Response Timeline
- **Acknowledgement:** We will acknowledge receipt of your vulnerability report within **24 hours**.
- **Triage & Assessment:** We aim to triage and confirm the severity of the issue within **48 hours**.
- **Patch Development:** Critical firewall bypasses or data exfiltration bugs will be patched and released within **5 days**.
- **Public Disclosure:** Once the patch is released and users have had a reasonable window to update, we will publicly acknowledge your contribution in our Release Notes and Security Advisory.

---

## 🔒 Safe Harbor Policy

We strongly support security research. We will not take legal action against you or ask law enforcement to investigate you if you comply with the following:
- You conduct your research without harming our users, systems, or data.
- You do not exploit the vulnerability further than necessary to establish its existence.
- You do not publicly disclose the vulnerability until we have had a reasonable timeframe to release a patch.
- You do not attempt Denial of Service (DoS) attacks or social engineering against our maintainers.

Thank you for helping keep the open-source AI ecosystem safe and secure!
