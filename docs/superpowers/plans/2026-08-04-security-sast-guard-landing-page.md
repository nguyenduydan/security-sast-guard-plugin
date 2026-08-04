# Implementation Plan - Security SAST Guard Landing Page

## Overview
Build an AWWWARDS-level, cinematic landing page for **Security SAST Guard** inside `docs/landing/index.html`. 
The page incorporates real-time interactive terminal simulation, gapless bento grid for 53 security vectors, installation guides, interactive comparison matrix, and GSAP scroll animations.

## Technical Stack & Libraries
- **HTML5 & Vanilla JS:** Clean, modular single-file web application.
- **Tailwind CSS (CDN):** Custom dark-mode theme, glassmorphism, ambient mesh blurs.
- **Typography:** `Outfit` (Headings) and `JetBrains Mono` (Code/Terminals) via Google Fonts.
- **Animations:** GSAP 3 + ScrollTrigger for pinned sections, scrubbing text reveals, and physics-driven card entry.
- **Icons:** Phosphor Icons / Lucide Icons SVG icons.

## Page Architecture (AIDA Framework)
1. **Header / Glass Floating Nav:** Sleek glassmorphic navbar with logo, status badge, nav links, and quick install CTA.
2. **Attention (Hero Section):**
   - H1 container `max-w-6xl` (2-line rule enforced: font size clamp `clamp(2.5rem, 5vw, 4.5rem)`).
   - Dynamic taglines: "Zero-Trust SAST & Real-Time Command Firewall for Google Antigravity & Gemini CLI".
   - Dual high-contrast CTAs: "Install via PowerShell" and "Explore Security Rules".
   - Live Interactive Command Firewall Sandbox (Simulates ALLOW / CONFIRM / DENY in real-time).
3. **Interest (Bento Grid):**
   - Gapless `grid-flow-dense` Bento layout (Zero dead space).
   - Card 1: 53 Security Vectors (OWASP, CWE, NIST).
   - Card 2: 14-Stage Pre-Commit Gate (Ruff, Mypy, Pytest 100% Coverage).
   - Card 3: Token-Saving Minified Context Extractor.
   - Card 4: Silent Skill Integration & Slash Commands.
4. **Desire (Interactive Features & Comparison):**
   - **How It Works:** Interactive pipeline diagram (Command Input -> Firewall Interceptor -> SAST Engine -> Action).
   - **Comparison Table:** Security SAST Guard vs. Legacy Static Code Analyzers (SonarQube, Snyk, Semgrep).
   - **Slash Commands Showcases:** Dynamic tab view for `/sast-audit`, `/sast-firewall`, `/sast-status`, etc.
5. **Action (Installation & Footer):**
   - 1-Click Copy PowerShell installation snippet (`install.ps1`, `update.ps1`, `remove.ps1`).
   - Enterprise security badge & MIT License footer.

## Verification Checklist
- Zero horizontal scrollbar (`overflow-x-hidden`).
- High-contrast buttons and readable fonts.
- Tested responsive behavior on desktop and mobile viewports.
- Validated GSAP animations work without JS console errors.
