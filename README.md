# Security SAST Guard Plugin

[![CI Quality Gate](https://github.com/nguyenduydan/security-sast-guard-plugin/actions/workflows/ci.yml/badge.svg)](https://github.com/nguyenduydan/security-sast-guard-plugin/actions/workflows/ci.yml)
[![Release Please](https://github.com/nguyenduydan/security-sast-guard-plugin/actions/workflows/release.yml/badge.svg)](https://github.com/nguyenduydan/security-sast-guard-plugin/actions/workflows/release.yml)
[![Python Version](https://img.shields.io/badge/python-3.12%2B-blue.svg)](https://www.python.org/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)
[![Ruff](https://img.shields.io/endpoint?url=https://raw.githubusercontent.com/astral-sh/ruff/main/assets/badge/v2.json)](https://github.com/astral-sh/ruff)
[![code style: mypy](https://img.shields.io/badge/type_checker-mypy-blue)](https://mypy-lang.org/)

SAST Security & Command Firewall Guard Plugin for Antigravity & Gemini CLI.

---

## Cấu trúc Dự Án (Repository Architecture)

```
security-sast-guard/
├── .github/
│   ├── ISSUE_TEMPLATE/     # Templates cho Bug report & Feature request
│   ├── workflows/          # Workflows CI Quality Gate & Automated Release
│   ├── CODEOWNERS          # Khai báo chủ sở hữu mã nguồn
│   ├── PULL_REQUEST_TEMPLATE.md
│   └── SECURITY.md         # Chính sách báo cáo lỗ hổng an toàn thông tin
├── docs/
│   ├── releases/           # Báo cáo phát hành chi tiết cho các phiên bản
│   ├── RELEASE_GUIDE.md    # Quy trình deploy & xuất bản Release chuẩn
│   └── RULE_TEMPLATE.md    # Mẫu định nghĩa quy tắc SAST mới
├── rules/
│   ├── sast_rules.json     # 53 quy tắc SAST chuẩn OWASP/CWE/NIST
│   └── profiles.json
├── skills/                 # AI Skill Prompt Directives (chạy ngầm ngầm)
├── src/
│   ├── cli/                # Dispatcher CLI entrypoint
│   ├── domain/             # SAST Scanner & Command Firewall core domain
│   └── infrastructure/     # Logger & Profile loader
├── tests/                  # Pytest test suite
├── .editorconfig           # Cấu hình chuẩn định dạng IDE
├── .pre-commit-config.yaml # Pipeline 14 bước Pre-commit
├── pyproject.toml          # Cấu hình Ruff, Mypy & Pytest
├── LICENSE                 # Giấy phép mã nguồn mở MIT
└── README.md
```

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
