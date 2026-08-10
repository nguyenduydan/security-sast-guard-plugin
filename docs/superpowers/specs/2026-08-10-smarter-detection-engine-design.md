# Smarter Detection Engine — Design Spec

**Date:** 2026-08-10  
**Status:** Approved (brainstorming session)  
**Author:** Antigravity AI (pair-programming)

---

## 1. Mục tiêu

Nâng cấp plugin từ **regex-based SAST scanner** thành **semantic-aware detection engine** có khả năng:

1. **Taint analysis** — theo dõi luồng dữ liệu từ `source` đến `sink` bất kể ngôn ngữ
2. **Cross-file dataflow** — kết nối các file khác nhau thông qua symbol/import tracking
3. **MCP tool exposure** — expose kết quả đa góc nhìn để AI agent tự khai thác

Approach: **Incremental — Phase 1 (grep-based) → Phase 3 (AST + call graph)**

---

## 2. Kiến trúc Tổng quan

```
Rule Files (.md)
    │ parse { sources, sinks } keywords
    ▼
[Phase 1] SymbolIndexer  ←──────────── TwoLevelCache (LRU + file-based)
    │ grep toàn repo → biến nhận source
    ▼
[Phase 1] TaintTracker
    │ grep tiếp → biến chạy đến sink
    │ build TaintFinding { source_file, source_line, sink_file, sink_line, trace_path[] }
    ▼
[Phase 2] ASTConfirmEngine  ← tree-sitter (optional, async)
    │ parse AST candidate files
    │ xác nhận scope & variable binding → loại false positives
    ▼
[Phase 3] CallGraphBuilder
    │ extract import/require/using declarations
    │ build directed graph: module A → module B
    │ trace call chains: fn_a() → fn_b() → dangerous_sink()
    ▼
AuditService (mở rộng)
    ├── existing findings (SASTScanner)
    └── taint_traces (TaintFinding list với full call chain)
         ▼
MCP Layer (3 new tools)
    ├── sast_get_dataflow_path(source_pattern, sink_pattern)
    ├── sast_get_taint_context(file_path, line_number)
    └── sast_scan_file / sast_scan_diff (mở rộng với taint_traces field)
```

---

## 3. Phase 1 — Lightweight Symbol Graph (Grep-based)

### 3.1 Rule Parsing — Source/Sink Extraction

Mỗi rule `.md` và `sast_rules.json` được parse để extract:
- **sources**: input entrypoints (request.GET, os.environ, input(), Request.QueryString, ...)
- **sinks**: dangerous call sites (subprocess.call, eval(), cursor.execute(), SqlCommand, ...)

Rule format mở rộng (backward-compatible):
```json
{
  "id": "RULE-001",
  "name": "SQL Injection",
  "sources": ["request.GET", "request.POST", "Request.Form"],
  "sinks": ["cursor.execute", "db.query", "SqlCommand"],
  "taint_enabled": true
}
```

### 3.2 SymbolIndexer

**File:** src/domain/symbol_indexer.py  
**Trách nhiệm:** Grep repo → tìm tất cả assignment từ source patterns

Language-agnostic: dùng grep pattern tổng quát, nhận biết `=`, `:=` và source keyword.

### 3.3 TaintTracker

**File:** src/domain/taint_tracker.py  
**Trách nhiệm:** Với mỗi symbol từ SymbolIndexer, grep tiếp để tìm nơi symbol chạy đến sink

TaintFinding fields: source_file, source_line, source_pattern, sink_file, sink_line, sink_pattern, trace_path (list[TraceStep]), confidence (0.0–1.0)

### 3.4 TwoLevelCache

**File:** src/infrastructure/symbol_cache.py

- **Level 1 (in-process):** LRU cache — key: (repo_path, frozenset(sources), commit_hash) — lifetime: process session
- **Level 2 (file-based):** .sast/symbol_cache.json — key: sha256(repo_path + sources + git_commit_hash) — invalidate khi commit hash thay đổi — TTL: 24h (configurable)

---

## 4. Phase 2 — AST Confirmation (tree-sitter)

Optional — install: `pip install security-sast-guard[ast]`

**File:** src/domain/ast_confirm_engine.py  
Xác nhận TaintFinding từ Phase 1 bằng AST analysis:
- Cùng scope không?
- Có sanitize trước khi đến sink không?
- Variable binding đúng không?

Returns: ConfirmResult { confirmed: bool, reason: str, updated_confidence: float }

**Graceful degradation:** Nếu tree-sitter không install → bỏ qua, confidence = 0.5, log warning.

**Supported languages:** Python, JavaScript, TypeScript, C#, Java, PHP, Ruby, Go, Rust

---

## 5. Phase 3 — Cross-file Call Graph

**File:** src/domain/call_graph_builder.py  
Xây directed graph: caller → callee từ import/require declarations.  
BFS/DFS từ entry points → tìm path đến sinks.  
Returns: CallChain { entry_fn, steps[], terminal_sink }

Import resolution: grep-based (không dùng language-specific resolver), resolve relative paths → absolute.

---

## 6. MCP Layer — New Tools

### sast_get_dataflow_path
Input: source_pattern, sink_pattern, repo_path  
Output: JSON với paths[], mỗi path có source/sink location, trace_path[], confidence, ast_confirmed

### sast_get_taint_context
Input: file_path, line_number, context_lines (default 10)  
Output: JSON với code_snippet, taint_info { is_source, is_sink, symbol, flows_to[], sanitized }

### Extended sast_scan_file / sast_scan_diff
Thêm field taint_traces[] vào JSON output hiện tại:
```json
{
  "findings": [...],
  "taint_traces": [{ "rule_id": "...", "source": {...}, "sink": {...}, "trace_path": [...], "confidence": 0.85 }],
  "summary": { ... }
}
```

---

## 7. Files Mới & Sửa Đổi

### New Files

| File | Phase | Mô tả |
|------|-------|--------|
| src/domain/symbol_indexer.py | 1 | Grep-based symbol assignment finder |
| src/domain/taint_tracker.py | 1 | Source-to-sink taint flow tracker |
| src/infrastructure/symbol_cache.py | 1 | Two-level cache (LRU + file-based) |
| src/domain/ast_confirm_engine.py | 2 | tree-sitter AST confirmation |
| src/domain/call_graph_builder.py | 3 | Cross-file call graph builder |
| tests/test_symbol_indexer.py | 1 | Unit tests |
| tests/test_taint_tracker.py | 1 | Unit tests |
| tests/test_symbol_cache.py | 1 | Unit tests |
| tests/test_ast_confirm_engine.py | 2 | Unit tests |
| tests/test_call_graph_builder.py | 3 | Unit tests |

### Modified Files

| File | Thay đổi |
|------|----------|
| src/application/audit_service.py | Integrate TaintTracker, expose taint_traces |
| src/mcp/tools.py | Add 2 new tools, extend sast_scan output |
| src/mcp/schemas.py | Add TaintFinding, CallChain, DataflowPath schemas |
| rules/sast_rules.json | Add sources, sinks, taint_enabled fields per rule |
| pyproject.toml | Add optional [ast] dependency group |

---

## 8. Verification Plan

```bash
python -m pytest tests/test_symbol_indexer.py tests/test_taint_tracker.py tests/test_symbol_cache.py -v
python -m pytest  # full suite — zero regressions
python -m pylint src/  # 10.00/10.00
python -m ruff check .
python -m ruff format --check .
```

Manual: verify dataflow path JSON, taint_context JSON, taint_traces in scan output, cache hit performance.

---

## 9. Rollout Sequence

| Sprint | Scope |
|--------|-------|
| Sprint 1 | Phase 1: SymbolIndexer + TaintTracker + TwoLevelCache + tests |
| Sprint 2 | MCP tools: sast_get_dataflow_path, sast_get_taint_context, extend scan output |
| Sprint 3 | Phase 2: ASTConfirmEngine với tree-sitter (optional dependency) |
| Sprint 4 | Phase 3: CallGraphBuilder + cross-file trace integration |
