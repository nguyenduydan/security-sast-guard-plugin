# Design System: Security SAST Guard (Dual Light/Dark Neo-Brutalist Edition)

## 0. Design Read
Reading this as: Dual-theme (Light Mode + Dark Mode) Neo-Brutalist High-Contrast UI system for Security SAST Guard (v0.4.2), featuring an instant interactive toggle switch in the navbar, theme state persistence via localStorage, and 100% WCAG 2.1 AA contrast compliance in both themes.

## 1. Light Theme (Soft Light Gray Neo-Brutalist)
- **Canvas Base:** Soft Light Gray (`#f1f5f9` / Slate-100) — Eliminates glare while retaining high contrast
- **Card Surfaces:** Pure White (`#ffffff`) with 3px solid black borders (`border-3 border-black`)
- **Drop Shadows:** 4px Solid Black (`shadow-[4px_4px_0px_0px_rgba(0,0,0,1)]`)
- **Primary Text:** Stark Pitch Black (`#000000`)
- **Metric Icon Boxes:** Solid Black container with White icon

## 2. Dark Theme (Cyber Obsidian Neo-Brutalist)
- **Canvas Base:** Deep Obsidian Black (`#040711` / Slate-950)
- **Card Surfaces:** Deep Slate-900 (`#0d1424`) with 2px/3px Emerald/White borders (`border-2 border-emerald-500/40`)
- **Drop Shadows:** Cyber Emerald Shadow (`shadow-[4px_4px_0px_0px_rgba(16,185,129,0.4)]`) or White Shadow (`shadow-[4px_4px_0px_0px_rgba(255,255,255,0.15)]`)
- **Primary Text:** Crisp White (`#ffffff`) & Emerald (`#34d399`)
- **Metric Icon Boxes:** Solid Emerald container (`bg-emerald-500 text-slate-950`)

## 3. Theme Orchestration & Persistence
- **Toggle Switch:** Sun/Moon icon toggle button in header navbar (`#theme-toggle-btn`)
- **State Storage:** `localStorage.setItem('theme', 'dark' | 'light')`
- **System Detection:** `window.matchMedia('(prefers-color-scheme: dark)')` fallback
