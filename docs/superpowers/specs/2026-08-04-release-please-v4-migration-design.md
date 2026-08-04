# Release Please v4 Migration Design

## Purpose
Khắc phục lỗi GitHub Action `release-please` chạy thành công (Success) nhưng không sinh ra Pull Request mới. 
Nguyên nhân gốc là dự án đang sử dụng `release-please-action@v4` kết hợp với chuẩn cấu hình cũ (v3) không có wrapper `"packages"`.

## Scope
Chỉ tập trung vào 2 file:
1. `release-please-config.json`: Cấu trúc lại dữ liệu sang schema v4.
2. `.github/workflows/release.yml`: Khắc phục cảnh báo "Node.js 20 is deprecated" bằng cách nâng cấp version Node.js của action nếu cần (hoặc update các setup actions).

## Architecture / Config Design

### `release-please-config.json`
Đưa tất cả cấu hình (`release-type`, `extra-files`, `changelog-sections`) vào trong một key `packages` với key con là `.` (đại diện cho thư mục root của dự án - simple repo mode).

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

### `.github/workflows/release.yml`
Sử dụng node20 chuẩn hoặc nâng cấp action (thực tế `googleapis/release-please-action@v4` mặc định chạy trên node20, việc GitHub ép lên node24 chỉ là warning, không gây lỗi hệ thống. Ta sẽ cập nhật action lên bản mới nhất nếu có để hạn chế warning).

## Testing Strategy
- Sau khi áp dụng thay đổi, push trực tiếp một commit kiểu `fix: migrate release-please to v4` lên `main`.
- Quan sát luồng `Release Please PR Automation` trong GitHub Actions.
- Kết quả mong đợi (Success Criteria): Bot sẽ tự động tạo một Pull Request có tiêu đề `chore(main): release 0.1.1`.
