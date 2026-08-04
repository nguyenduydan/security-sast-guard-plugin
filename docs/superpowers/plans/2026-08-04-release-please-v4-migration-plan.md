# Release Please v4 Migration Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Khắc phục lỗi `release-please` không tạo Pull Request bằng cách bọc toàn bộ file cấu hình vào trong block `"packages": { ".": { ... } }` theo chuẩn schema v4.

**Architecture:** Nâng cấp cấu hình từ cấu trúc v3 sang v4, khai báo explicitly đường dẫn root `.` bên trong object `packages` để `release-please-action@v4` nhận diện chính xác ứng dụng cần release.

**Tech Stack:** JSON, GitHub Actions.

## Global Constraints

- File `release-please-config.json` phải hợp lệ định dạng JSON.
- Cấu hình phải tuân thủ chuẩn schema `https://raw.githubusercontent.com/googleapis/release-please/main/schemas/config.json`.
- Commit thông báo phải chuẩn Conventional Commits có dạng `fix: migrate release-please to v4`.

---

### Task 1: Update release-please-config.json

**Files:**
- Modify: `release-please-config.json`

**Interfaces:**
- Consumes: N/A
- Produces: Cấu hình chuẩn v4 để bot sinh PR thành công.

- [ ] **Step 1: Write the updated configuration to `release-please-config.json`**

Thay thế toàn bộ nội dung file `release-please-config.json` bằng đoạn JSON sau:
```json
{
  "$schema": "https://raw.githubusercontent.com/googleapis/release-please/main/schemas/config.json",
  "packages": {
    ".": {
      "release-type": "python",
      "extra-files": [
        {
          "type": "json",
          "path": "plugin.json",
          "jsonpath": "$.version"
        }
      ],
      "changelog-sections": [
        { "type": "feat", "section": "🚀 Features & SAST Security Rules", "hidden": false },
        { "type": "fix", "section": "🐛 Bug Fixes", "hidden": false },
        { "type": "perf", "section": "⚡ Performance Improvements", "hidden": false },
        { "type": "refactor", "section": "♻️ Refactoring & Code Hygiene", "hidden": false },
        { "type": "build", "section": "📦 Build System & Dependencies", "hidden": false },
        { "type": "ci", "section": "🤖 CI/CD Workflows", "hidden": false },
        { "type": "docs", "section": "📝 Documentation", "hidden": false },
        { "type": "style", "section": "🎨 Code Style & Formatting", "hidden": false }
      ]
    }
  }
}
```

- [ ] **Step 2: Check JSON validity**

Run: `node -e "require('./release-please-config.json')"` (hoặc dùng jq `jq . release-please-config.json`)
Expected: Không hiện ra lỗi (Valid JSON).

- [ ] **Step 3: Commit**

```bash
git add release-please-config.json
git commit -m "fix: migrate release-please config to v4 schema"
```
