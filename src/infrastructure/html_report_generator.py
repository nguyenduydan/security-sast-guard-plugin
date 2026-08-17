"""Interactive HTML Report Generator for Security SAST Guard."""

from __future__ import annotations

import html
import json
from datetime import datetime
from pathlib import Path
from typing import Any


# pylint: disable=too-many-locals,too-many-statements
def generate_html_report(
    findings: list[dict[str, Any]],
    output_dir: str = "reports",
    target_path: str = ".",
    metadata: dict[str, Any] | None = None,
    audit_level: str = "full",
) -> tuple[str, str]:
    """Generate a self-contained interactive Dark Mode HTML report."""
    target_dir = Path(output_dir)
    target_dir.mkdir(parents=True, exist_ok=True)

    timestamp_str = datetime.now().strftime("%Y%m%d_%H%M%S")
    report_file = target_dir / f"sast_audit_report_{timestamp_str}.html"

    counts = {"critical": 0, "high": 0, "medium": 0, "low": 0}
    for f in findings:
        sev = str(f.get("severity", "medium")).lower()
        if sev in counts:
            counts[sev] += 1

    meta = metadata or {}
    scanned_count = meta.get("scanned_files", len(findings))
    lines_count = meta.get("total_lines", "N/A")
    duration_val = meta.get("duration_seconds", 0.0)

    findings_json = json.dumps(findings, default=str)

    html_template = f"""<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <title>SAST Security Audit Dashboard</title>
  <style>
    :root {{
      --bg-primary: #0d1117;
      --bg-secondary: #161b22;
      --bg-tertiary: #21262d;
      --border-color: #30363d;
      --text-primary: #c9d1d9;
      --text-secondary: #8b949e;
      --accent-blue: #58a6ff;
      --color-critical: #f85149;
      --color-high: #db6d28;
      --color-medium: #d29922;
      --color-low: #3fb950;
    }}
    * {{ box-sizing: border-box; margin: 0; padding: 0; }}
    body {{
      font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Helvetica, Arial;
      background-color: var(--bg-primary);
      color: var(--text-primary);
      line-height: 1.5;
      padding: 24px;
    }}
    .header {{
      display: flex;
      justify-content: space-between;
      align-items: center;
      padding-bottom: 20px;
      border-bottom: 1px solid var(--border-color);
      margin-bottom: 24px;
    }}
    .title-group {{ display: flex; align-items: center; gap: 12px; }}
    .title-group h1 {{ font-size: 24px; color: #fff; }}
    .badge-level {{
      background-color: var(--bg-tertiary);
      color: var(--accent-blue);
      padding: 4px 10px;
      border-radius: 12px;
      font-size: 12px;
      font-weight: 600;
      border: 1px solid var(--border-color);
    }}
    .stats-grid {{
      display: grid;
      grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
      gap: 16px;
      margin-bottom: 24px;
    }}
    .stat-card {{
      background: var(--bg-secondary);
      border: 1px solid var(--border-color);
      border-radius: 8px;
      padding: 16px;
    }}
    .stat-card .label {{
      font-size: 12px;
      color: var(--text-secondary);
      text-transform: uppercase;
      font-weight: 600;
    }}
    .stat-card .value {{ font-size: 28px; font-weight: 700; margin-top: 4px; }}
    .val-critical {{ color: var(--color-critical); }}
    .val-high {{ color: var(--color-high); }}
    .val-medium {{ color: var(--color-medium); }}
    .val-low {{ color: var(--color-low); }}
    .controls {{
      display: flex;
      gap: 12px;
      margin-bottom: 20px;
      flex-wrap: wrap;
    }}
    .search-input {{
      flex: 1;
      min-width: 250px;
      background: var(--bg-secondary);
      border: 1px solid var(--border-color);
      color: var(--text-primary);
      padding: 8px 14px;
      border-radius: 6px;
      font-size: 14px;
    }}
    .filter-btn {{
      background: var(--bg-secondary);
      border: 1px solid var(--border-color);
      color: var(--text-primary);
      padding: 8px 16px;
      border-radius: 6px;
      cursor: pointer;
      font-size: 13px;
      font-weight: 500;
      transition: all 0.15s ease;
    }}
    .filter-btn.active {{
      background: var(--bg-tertiary);
      border-color: var(--accent-blue);
      color: #fff;
    }}
    .finding-list {{ display: flex; flex-direction: column; gap: 12px; }}
    .finding-card {{
      background: var(--bg-secondary);
      border: 1px solid var(--border-color);
      border-radius: 8px;
      padding: 16px;
      transition: border-color 0.15s ease;
    }}
    .finding-card:hover {{ border-color: #58a6ff55; }}
    .finding-header {{
      display: flex;
      justify-content: space-between;
      align-items: center;
      margin-bottom: 8px;
    }}
    .finding-title {{
      display: flex;
      align-items: center;
      gap: 8px;
      font-size: 15px;
      font-weight: 600;
    }}
    .sev-tag {{
      padding: 2px 8px;
      border-radius: 4px;
      font-size: 11px;
      font-weight: 700;
      text-transform: uppercase;
    }}
    .sev-critical {{
      background: #f8514922;
      color: var(--color-critical);
      border: 1px solid var(--color-critical);
    }}
    .sev-high {{
      background: #db6d2822;
      color: var(--color-high);
      border: 1px solid var(--color-high);
    }}
    .sev-medium {{
      background: #d2992222;
      color: var(--color-medium);
      border: 1px solid var(--color-medium);
    }}
    .sev-low {{
      background: #3fb95022;
      color: var(--color-low);
      border: 1px solid var(--color-low);
    }}
    .location {{
      font-size: 13px;
      color: var(--text-secondary);
      font-family: monospace;
    }}
    .snippet {{
      background: var(--bg-primary);
      border: 1px solid var(--border-color);
      border-radius: 6px;
      padding: 10px;
      font-family: monospace;
      font-size: 13px;
      overflow-x: auto;
      margin-top: 8px;
      color: #e6edf3;
    }}
    .empty-state {{
      text-align: center;
      padding: 48px;
      background: var(--bg-secondary);
      border-radius: 8px;
      border: 1px dashed var(--border-color);
      color: var(--text-secondary);
    }}
  </style>
</head>
<body>
  <div class="header">
    <div class="title-group">
      <h1>🛡️ SAST Security Audit Dashboard</h1>
      <span class="badge-level">Level: {html.escape(str(audit_level).upper())}</span>
    </div>
    <div style="font-size: 13px; color: var(--text-secondary);">
      Target: <code>{html.escape(target_path)}</code> |
      Date: {datetime.now().strftime("%Y-%m-%d %H:%M:%S")}
    </div>
  </div>

  <div class="stats-grid">
    <div class="stat-card">
      <div class="label">Total Findings</div>
      <div class="value">{len(findings)}</div>
    </div>
    <div class="stat-card">
      <div class="label">Critical</div>
      <div class="value val-critical">{counts["critical"]}</div>
    </div>
    <div class="stat-card">
      <div class="label">High</div>
      <div class="value val-high">{counts["high"]}</div>
    </div>
    <div class="stat-card">
      <div class="label">Medium</div>
      <div class="value val-medium">{counts["medium"]}</div>
    </div>
    <div class="stat-card">
      <div class="label">Low</div>
      <div class="value val-low">{counts["low"]}</div>
    </div>
  </div>

  <div class="controls">
    <input type="text" id="search-box" class="search-input"
           placeholder="Search Rule ID, Path, or Content...">
    <button class="filter-btn active" data-filter="all">All ({len(findings)})</button>
    <button class="filter-btn" data-filter="critical">
      Critical ({counts["critical"]})
    </button>
    <button class="filter-btn" data-filter="high">High ({counts["high"]})</button>
    <button class="filter-btn" data-filter="medium">Medium ({counts["medium"]})</button>
    <button class="filter-btn" data-filter="low">Low ({counts["low"]})</button>
  </div>

  <div id="findings-container" class="finding-list"></div>

  <script>
    const findingsData = {findings_json};
    let currentFilter = 'all';
    let searchQuery = '';

    function renderFindings() {{
      const container = document.getElementById('findings-container');
      container.innerHTML = '';

      const filtered = findingsData.filter(f => {{
        const sev = (f.severity || 'medium').toLowerCase();
        const matchesFilter = (currentFilter === 'all' || sev === currentFilter);
        const term = [
          f.rule_id,
          f.rule_name,
          f.path || f.file_path,
          f.line_content
        ].filter(Boolean).join(' ').toLowerCase();
        const matchesSearch = !searchQuery || term.includes(searchQuery.toLowerCase());
        return matchesFilter && matchesSearch;
      }});

      if (filtered.length === 0) {{
        container.textContent = '';
        const emptyDiv = document.createElement('div');
        emptyDiv.className = 'empty-state';
        emptyDiv.textContent = '✅ No security vulnerabilities matched.';
        container.appendChild(emptyDiv);
        return;
      }}

      filtered.forEach(f => {{
        const card = document.createElement('div');
        card.className = 'finding-card';
        const sev = (f.severity || 'medium').toLowerCase();
        const path = f.path || f.file_path || 'unknown';
        const line = f.line || f.line_number || 1;
        const snippet = f.line_content || '';
        const ruleName = f.rule_name || f.rule_id || 'Unknown';

        card.innerHTML = `
          <div class="finding-header">
            <div class="finding-title">
              <span class="sev-tag sev-${{sev}}">${{sev}}</span>
              <span><code>${{escapeHtml(f.rule_id)}}</code>
                - ${{escapeHtml(ruleName)}}</span>
            </div>
            <span class="location">${{escapeHtml(path)}}:${{line}}</span>
          </div>
          <pre class="snippet">${{escapeHtml(snippet)}}</pre>
        `;
        container.appendChild(card);
      }});
    }}

    function escapeHtml(str) {{
      return String(str)
        .replace(/&/g, '&amp;')
        .replace(/</g, '&lt;')
        .replace(/>/g, '&gt;')
        .replace(/"/g, '&quot;');
    }}

    document.getElementById('search-box').addEventListener('input', (e) => {{
      searchQuery = e.target.value;
      renderFindings();
    }});

    document.querySelectorAll('.filter-btn').forEach(btn => {{
      btn.addEventListener('click', () => {{
        document.querySelectorAll('.filter-btn').forEach(
          b => b.classList.remove('active')
        );
        btn.classList.add('active');
        currentFilter = btn.getAttribute('data-filter');
        renderFindings();
      }});
    }});

    renderFindings();
  </script>
</body>
</html>"""

    report_file.write_text(html_template, encoding="utf-8")
    file_uri = report_file.resolve().as_uri()
    try:
        rel_path = report_file.resolve().relative_to(Path.cwd()).as_posix()
    except ValueError:
        rel_path = report_file.name

    counts_str = (
        f"Critical: {counts['critical']}, High: {counts['high']}, "
        f"Medium: {counts['medium']}, Low: {counts['low']}"
    )
    summary = (
        f"SAST Audit completed. [Scanned {scanned_count} files, "
        f"{lines_count} lines in {duration_val}s] "
        f"Total: {len(findings)} findings ({counts_str}).\n"
        f"HTML report saved to: [{rel_path}]({file_uri})"
    )
    return str(report_file), summary
