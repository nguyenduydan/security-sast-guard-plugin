# Agent Work Breakdown — Security SAST Guard v2.0.0
## Tier 3: Developer Experience (4 Agent Specs làm việc song song trên 1 branch)

---

## Agent Breakdown

### Agent T3-1 — Pure ANSI TUI Renderer
**Owns exclusively:**
- `src/infrastructure/tui_renderer.py` [NEW]
- `tests/test_tui_renderer.py` [NEW]

**Task:**
Implement `TUIRenderer` in Python (pure ANSI codes, no external dependencies like `rich` or `curses`):
- `render_scan_progress(scanned, total, current_file)`
- `render_scan_summary(target_path, duration, files_count, severity_counts, fp_filtered, fp_reduction, report_path)`
- `render_finding(severity, rule_id, line_no, file_path, code_snippet)`
- `render_firewall_verdict(verdict, intent, risk_score, reason)`
- Dynamic version header: Must call `get_plugin_version()`.

---

### Agent T3-2 — SARIF 2.1.0 Report Generator Upgrade
**Owns exclusively:**
- `tests/test_sarif_v2.py` [NEW]
- `src/infrastructure/report_generator.py` [UPGRADE — SARIF 2.1.0 schema enhancements]

**Task:**
Enhance SARIF 2.1.0 export with CWE tags, OWASP tags, fingerprint hashes, and evidence graph locations.

---

### Agent T3-3 — Refactor UI Landing Page Layout & Content
**Owns exclusively:**
- `docs/index.html` [REFACTOR layout & content]

**Task:**
Maintain existing visual styling (CSS tokens, dark mode, vibrant accents), refactor structure to showcase v2.0.0 13 Modules, AI Agent Symbiotic Security Architecture diagram, and v1.x vs v2.0.0 comparison table.

---

### Agent T3-4 — Documentation & Agent Directives Ecosystem v2
**Owns exclusively:**
- `README.md` [UPGRADE]
- `GEMINI.md` [UPGRADE]
- `docs/RELEASE_GUIDE.md` [NEW]

**Task:**
Update documentation ecosystem for v2.0.0: architecture overview, MCP tools list (`sast_scan_file`, `sast_scan_diff`, `sast_check_command`, etc.), CI/CD workflow, migration guide, and agent directives.
