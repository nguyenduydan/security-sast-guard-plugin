# 🛡️ Security SAST Guard — Production Readiness Design Spec

**Date:** 2026-08-06  
**Repo:** [nguyenduydan/security-sast-guard-plugin](https://github.com/nguyenduydan/security-sast-guard-plugin)

---

## 🎯 Goal

Nâng cấp plugin từ **prototype functional** lên **production-grade** — hoạt động đầy đủ trên cả **Antigravity 2.0 (IDE)** và **CLI (agy)** trên Windows, Linux, macOS.

---

## 📌 Gap Analysis

| ID | Gap | Severity |
|----|-----|----------|
| G1 | `gemini-extension.json` version `0.0.1` không đồng bộ `plugin.json` `0.10.0` | 🔴 Critical |
| G2 | CLI dispatcher thiếu handler `firewall` command | 🔴 Critical |
| G3 | `run_audit_hook.py` là stub rỗng | 🔴 Critical |
| G4 | Không có `PostToolCallExecute` hook tự động scan sau agent write | 🟠 High |
| G5 | `firewall_hook.ps1` chỉ chạy Windows, CLI Linux/macOS không được bảo vệ | 🟠 High |
| G6 | Không có MCP Server — Antigravity 2.0 không dùng được như tool | 🟠 High |
| G7 | Một `profile.json` toàn cục, không hỗ trợ per-project | 🟡 Medium |
| G8 | Không có `/sast-init` để khởi tạo project | 🟡 Medium |
| G9 | `AIVerifier` chỉ là heuristic/regex, không phải AI thực sự | 🟡 Medium |
| G10 | Không có JSON output cho report | 🟡 Medium |
| G11 | Không có `version` command | 🟢 Low |
| G12 | `commands/` thiếu `sast-audit-level.toml` | 🟢 Low |
| G13 | `tests/test_plugin.py` chỉ có `assert True` | 🟢 Low |

---

## 📦 Sub-project Decomposition

### SP-1: Critical Bug Fixes ⚡
**Branch:** `fix/critical-blockers`

| Task ID | File | Mô tả |
|---------|------|-------|
| T1.1 | `gemini-extension.json` | Sync version về `0.10.0`. Thêm CI step kiểm tra version đồng bộ |
| T1.2 | `src/cli/dispatcher.py` | Thêm handler `firewall <cmd>`: gọi firewall check, in `ALLOW/CONFIRM/DENY` + lý do |
| T1.3 | `src/cli/dispatcher.py` | Thêm handler `version`: in plugin version + Python version + platform |
| T1.4 | `hooks/run_audit_hook.py` | Implement thực sự: đọc `SAST_TARGET` env var, chạy `AuditService().run_audit()`, in summary |
| T1.5 | `hooks.json` | Kết nối `PostToolCallExecute` → `run_audit_hook.py` |
| T1.6 | `commands/sast-audit-level.toml` | Tạo file còn thiếu |
| T1.7 | `tests/test_plugin.py` | Thay `assert True` bằng test thực kiểm tra `plugin.json` fields + version hợp lệ |
| T1.8 | `.github/workflows/ci.yml` | Thêm step kiểm tra version sync giữa `plugin.json` và `gemini-extension.json` |

---

### SP-2: Cross-platform Firewall + PostToolCall Hook 🌐
**Branch:** `feat/cross-platform-firewall`

**Thiết kế:** Tách logic firewall từ PowerShell sang Python module `FirewallEngine`. PS1 và SH script chỉ là thin wrappers.

| Task ID | File | Mô tả |
|---------|------|-------|
| T2.1 | `src/domain/firewall_engine.py` | **[NEW]** `FirewallEngine(profile).check(cmd) -> Literal["ALLOW","CONFIRM","DENY"]` — port logic PS1 sang Python |
| T2.2 | `src/domain/firewall_engine.py` | Implement: de-obfuscation (caret strip, backtick strip), Base64 decode, regex matching |
| T2.3 | `src/cli/dispatcher.py` | Update handler `firewall` (T1.2) gọi `FirewallEngine` — cross-platform |
| T2.4 | `hooks/firewall_hook.ps1` | Refactor thành thin wrapper: `python control_plane.py firewall "$CommandText"` |
| T2.5 | `hooks/firewall_hook.sh` | **[NEW]** Bash wrapper cho Linux/macOS, exit code POSIX |
| T2.6 | `hooks/firewall_hook.py` | **[NEW]** Python launcher cross-platform: detect OS → call `.ps1` hoặc `.sh` hoặc gọi `FirewallEngine` trực tiếp |
| T2.7 | `hooks.json` | Update command dùng `firewall_hook.py` thay vì hardcode `.ps1` |
| T2.8 | `hooks/post_write_hook.py` | **[NEW]** PostToolCallExecute: nhận `file_path` từ env, scan nếu là code file, in findings ngắn |
| T2.9 | `hooks.json` | Đăng ký `PostToolCallExecute` → `post_write_hook.py` |
| T2.10 | `tests/test_firewall_engine.py` | **[NEW]** Test `FirewallEngine`: deny, confirm, allow, base64, caret bypass |

---

### SP-3: MCP Server 🔌
**Branch:** `feat/mcp-server`  
**Độc lập, song song với SP-2.**

**Thiết kế:** Python stdio MCP server expose 5 tools cho Antigravity 2.0. Transport: stdio JSON-RPC.

**MCP Tools:**
- `sast_scan_file(path)` → findings + summary
- `sast_scan_diff()` → scan git changed files
- `sast_check_command(command)` → ALLOW/CONFIRM/DENY + reason
- `sast_get_status()` → profile + rule count + integrity
- `sast_set_level(level)` → success bool

| Task ID | File | Mô tả |
|---------|------|-------|
| T3.1 | `pyproject.toml` | Thêm optional dependency `mcp>=1.0` hoặc dùng stdlib JSON-RPC |
| T3.2 | `src/mcp/__init__.py` | **[NEW]** Package init |
| T3.3 | `src/mcp/server.py` | **[NEW]** MCP server chính: stdio JSON-RPC loop, route requests |
| T3.4 | `src/mcp/tools.py` | **[NEW]** 5 tool handlers, mỗi tool async function gọi `AuditService` |
| T3.5 | `src/mcp/schemas.py` | **[NEW]** JSON schema definitions cho inputs/outputs của mỗi tool |
| T3.6 | `control_plane.py` | Thêm subcommand `mcp-server`: `python control_plane.py mcp-server` |
| T3.7 | `mcp_config.json` | **[NEW]** Khai báo MCP server cho Antigravity 2.0 load |
| T3.8 | `plugin.json` | Thêm field `mcp` reference nếu AGY 2.0 cần |
| T3.9 | `tests/test_mcp_tools.py` | **[NEW]** Unit test gọi tool handlers trực tiếp |
| T3.10 | `docs/MCP_INTEGRATION.md` | **[NEW]** Hướng dẫn setup MCP server trong Antigravity 2.0 |

---

### SP-4: Multi-project Profile + `/sast-init` 🗂️
**Branch:** `feat/multi-project-profile`  
**Độc lập, song song với SP-2 & SP-3.**

**Profile resolution order:** `.sast/profile.json` (CWD) → `.sast/profile.json` (git root) → `~/.sast/profile.json` (global)

| Task ID | File | Mô tả |
|---------|------|-------|
| T4.1 | `src/infrastructure/profile_resolver.py` | **[NEW]** `ProfileResolver`: traverse CWD → git root → global, return `(Path, scope)` |
| T4.2 | `src/application/audit_service.py` | Update `__init__` dùng `ProfileResolver` thay vì hardcode `"profile.json"` |
| T4.3 | `src/infrastructure/integrity_checker.py` | Update paths để tương thích với `.sast/profile.json` |
| T4.4 | `src/cli/dispatcher.py` | Thêm command `init`: tạo `.sast/` dir, copy template profile, hỏi project_id + stack |
| T4.5 | `templates/profile_template.json` | **[NEW]** Template profile với defaults và comments |
| T4.6 | `skills/sast-init/SKILL.md` | **[NEW]** Skill cho `/sast-init` |
| T4.7 | `commands/sast-init.toml` | **[NEW]** Command definition |
| T4.8 | `plugin.json` | Thêm `sast-init` vào skills list |
| T4.9 | `hooks/firewall_hook.ps1` & `.sh` | Update dùng `ProfileResolver` order |
| T4.10 | `tests/test_profile_resolver.py` | **[NEW]** Test resolution order với tmp_path fixtures |
| T4.11 | `tests/test_cli.py` | Thêm test cho `init` command |

---

### SP-5: AI Verifier (LLM + Cache) + JSON Output + Misc 🤖
**Branch:** `feat/ai-verifier-and-polish`  
**Sau SP-2 và SP-4.**

**AI Verifier design:**
- Chỉ kích hoạt ở `ultra` level
- Batch **toàn bộ findings thành 1 LLM call** (tiết kiệm quota free tier)
- Cache kết quả bằng hash `SHA256(rule_id + line_content + file_ext)` → `~/.sast/ai_cache.json`
- Model: `gemini-1.5-flash` (free tier)

| Task ID | File | Mô tả |
|---------|------|-------|
| T5.1 | `src/domain/ai_verifier.py` | Tách thành `HeuristicVerifier` (giữ logic cũ) + `LLMVerifier` mới |
| T5.2 | `src/domain/ai_cache.py` | **[NEW]** Cache layer: hash-based lookup/store, TTL 24h |
| T5.3 | `src/domain/ai_verifier.py` | `LLMVerifier`: batch findings → 1 Gemini API call → parse JSON → cache kết quả |
| T5.4 | `src/application/audit_service.py` | Route: `ultra` → `LLMVerifier`, `lite/full` → `HeuristicVerifier` |
| T5.5 | `src/infrastructure/report_generator.py` | Thêm `output_format: Literal["markdown","json"]` — JSON trả dict thay vì render file |
| T5.6 | `src/cli/dispatcher.py` | Thêm `--format json` flag cho `scan`/`audit` command |
| T5.7 | `src/domain/rule_versioning.py` | **[NEW]** `RuleRegistry`: mỗi rule có `version` + `updated_at`. `check_remote_updates()` |
| T5.8 | `src/cli/dispatcher.py` | Command `rules update`: fetch updates từ remote rule registry |
| T5.9 | `skills/sast-rules/SKILL.md` | Thêm hướng dẫn `/sast-rules update` |
| T5.10 | `tests/test_ai_verifier.py` | **[NEW]** Mock Gemini API, test caching, test fallback |
| T5.11 | `tests/test_report_json.py` | **[NEW]** Test JSON output format |

---

## 🔗 Dependency Graph

```
SP-1 (Critical Fixes) ──────────────────────────── unblock ──▶ SP-2, SP-3, SP-4
   T1.1, T1.6, T1.7     ← parallel group A
   T1.2 → T1.3, T1.4    ← sequential
   T1.4 → T1.5          ← sequential

SP-2 ←─────────┐
SP-3 ←──(all)──┤  parallel sau SP-1
SP-4 ←─────────┘

SP-5 ← sau SP-2, SP-4 (dùng FirewallEngine & ProfileResolver)
```

---

## ✅ Definition of Done (mỗi SP)

1. `python -m pytest` — 100% pass, 0 failures
2. `python -m pylint $(git ls-files '*.py')` — 10.00/10
3. `python -m mypy --config-file=pyproject.toml control_plane.py src/` — 0 errors
4. `/sast-audit file <modified_files>` — 0 security findings
5. PR tạo trên GitHub, báo cáo User để merge

---

## 📊 Effort Estimate

| Sub-project | Tasks | Ước tính đơn agent | Song song (4 agents) |
|-------------|-------|-------------------|----------------------|
| SP-1 | 8 | ~2h | ~2h |
| SP-2 | 10 | ~4h | ~1h |
| SP-3 | 10 | ~5h | ~1.5h |
| SP-4 | 11 | ~3h | ~1h |
| SP-5 | 11 | ~4h | ~1.5h |
| **Total** | **50** | **~18h** | **~7h** |
