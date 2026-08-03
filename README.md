# Security SAST Guard Plugin

SAST Security & Command Firewall Guard Plugin for Antigravity & Gemini CLI.

---

## Hướng dẫn cài đặt & sử dụng Pre-Commit System

Dự án sử dụng hệ thống **Pre-Commit** hiện đại cho Python 3.12+ (bao gồm Ruff, mypy, pytest, detect-secrets và Conventional Commits).

### 1. Cài đặt các công cụ cần thiết

```bash
pip install pre-commit ruff mypy pytest detect-secrets
```

### 2. Kích hoạt Pre-Commit Hooks vào Git

```bash
# Kích hoạt pre-commit hook (chạy trước khi commit)
pre-commit install

# Kích hoạt commit-msg hook (kiểm tra chuẩn Conventional Commits)
pre-commit install --hook-type commit-msg
```

### 3. Chạy kiểm tra thủ công trên toàn bộ dự án

```bash
pre-commit run --all-files
```

---

## Chuẩn Commit Message (Conventional Commits)

Format yêu cầu: `<type>(<scope>): <description>`

### Các prefix (type) được phép:
- `feat`: Tính năng mới
- `fix`: Sửa lỗi
- `refactor`: Tái cấu trúc code (không đổi logic/tính năng)
- `docs`: Thêm/sửa tài liệu
- `style`: Định dạng code (khoảng trắng, chấm phẩy...)
- `test`: Thêm hoặc sửa test
- `perf`: Tối ưu hiệu năng
- `ci`: Cấu hình CI/CD
- `build`: Thay đổi hệ thống build hoặc dependencies
- `chore`: Thao tác lặt vặt khác
- `revert`: Revert lại commit trước đó

### Ví dụ hợp lệ:
```bash
git commit -m "feat(auth): add login logic"
git commit -m "fix(api): handle connection timeout"
git commit -m "refactor(sast): simplify rule parser"
```

### Ví dụ KHÔNG hợp lệ (sẽ bị từ chối):
```bash
git commit -m "update"
git commit -m "fix bug"
git commit -m "abc"
```
