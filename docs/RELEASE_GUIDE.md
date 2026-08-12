# Hướng Dẫn Quy Trình Xuất Bản Release & Migration Guide (Security SAST Guard v2.0.0)

Tài liệu này quy định tiêu chuẩn phát hành phiên bản, quy trình commit, hướng dẫn nâng cấp từ v1.x lên v2.0.0 (Zero Breaking Changes) và tự động hóa xuất bản GitHub Release cho dự án **security-sast-guard-plugin**.

---

## 1. Migration Guide: Nâng Cấp Từ v1.x Lên v2.0.0 (Zero Breaking Changes)

Security SAST Guard v2.0.0 được thiết kế với nguyên tắc **100% Backward Compatibility (Tương thích ngược hoàn toàn)**. Người dùng và AI Agent nâng cấp từ v1.x lên v2.0.0 không cần thay đổi bất kỳ cấu hình hiện có nào.

### 1.1. Cam Kết Zero Breaking Changes
- **Cấu hình `.sast/profile.json` hiện tại:** Giữ nguyên toàn bộ key/value từ v1.x. Engine v2.0.0 tự động load và bổ sung các giá trị mặc định cho 13 module mới.
- **Tập lệnh CLI & Slash Commands:** Tất cả lệnh CLI (`sast scan`, `sast status`, `sast init`, `sast mode`, `sast level`, `sast rules`) và Slash Commands (`/sast-audit`, `/sast-status`, `/sast-init`, `/sast-mode`, `/sast-audit-level`, `/sast-rules`) giữ nguyên cú pháp 100%.
- **MCP Server Stdio Interface:** 9 Stdio tools từ v1.x (`sast_scan_file`, `sast_scan_diff`, `sast_check_command`, `sast_get_status`, `sast_set_level`, `sast_init`, `sast_sync_rules`, `sast_get_help`, `sast_set_mode`) giữ nguyên signature. v2.0.0 bổ sung 3 tools mới (`sast_get_dataflow_path`, `sast_get_taint_context`, `sast_generate_report`).

### 1.2. Các Tính Năng & Kiến Trúc Mới Trong v2.0.0
Phiên bản v2.0.0 bổ sung **13 Modular Subsystems** chia làm 3 Tier:
1. **Tier 1 (Security Core):** 10-Stage Firewall Normalizer, Capability Classifier, Intent Classifier, Multi-Command Chain Analyzer, 4-State Decision Engine, Semantic Fingerprint Tracker, Rule Integrity Validator, Append-Only Audit Log.
2. **Tier 2 (SAST Intelligence):** Evidence Engine & Program Slicer, Bounded Verification Harness, Adaptive Knowledge Base (Sanitizer Registry), CWE/OWASP Mapper & Metrics Engine, Framework Semantics Registry (ASP.NET WebForms, React, Generic).
3. **Tier 3 (Developer Experience):** Pure ANSI TUI Renderer (`TUIRenderer`), Enhanced ISO SARIF 2.1.0 Exporter, 12 MCP Tools Suite.

---

## 2. Quy Trình SemVer & Release-Please Automated Release

Dự án áp dụng công cụ tự động **`release-please` v4** kết hợp với quy tắc Semantic Versioning (SemVer):

### 2.1. Quy Tắc Đặt Tên Phiên Bản (SemVer)
- **MAJOR (`v2.0.0`):** Tăng khi có thay đổi lớn về kiến trúc hoặc breaking changes (v2.0.0 nâng cấp toàn bộ hệ thống SAST & Firewall).
- **MINOR (`v2.1.0`):** Tăng khi bổ sung tính năng mới, quy tắc SAST mới hoặc công cụ MCP mới mà vẫn tương thích ngược.
- **PATCH (`v2.0.1`):** Tăng khi sửa lỗi bug fix, cập nhật bảo trì, tái cấu trúc hoặc cập nhật dependency.

### 2.2. Tự Động Hóa Qua Bot Release-Please
- **Không Đánh Tag Thủ Công:** Tuyệt đối **KHÔNG** tự ý chạy `git tag` hoặc tạo release thủ công trên GitHub UI.
- **Không Sửa Manual Version:** Không chỉnh sửa thủ công số version trong `plugin.json` hay `pyproject.toml`.
- Bot `release-please` sẽ tự động phân tích các commit được merge vào nhánh `main`, tự tạo Release PR (cập nhật version và `CHANGELOG.md`), và phát hành GitHub Release chính thức kèm theo Git Tag khi Release PR được merge.

---

## 3. Chuẩn Commit Message (Conventional Commits)

Tất cả commit message **BẮT BUỘC** tuân thủ định dạng chuẩn Conventional Commits có Scope:
`<type>(<scope>): <description>`

### Các Loại Commit (`type`):
- `feat`: Thêm tính năng mới hoặc quy tắc SAST mới. *(Kích hoạt tăng MINOR version)*.
- `fix`: Sửa lỗi mã nguồn, bug linter hoặc CI. *(Kích hoạt tăng PATCH version)*.
- `chore`: Tác vụ bảo trì, dọn dẹp, update dependency. *(Kích hoạt tăng PATCH version)*.
- `refactor`: Viết lại code nhưng không thay đổi hành vi. *(Kích hoạt tăng PATCH version)*.
- `docs`: Cập nhật tài liệu (`.md`, comments). *(Không tăng version)*.
- `style`: Sửa định dạng code (Ruff formatting).
- `test`: Thêm hoặc sửa bài kiểm thử pytest.

*Ví dụ:* `feat(firewall): add 10-stage deobfuscation normalizer`

---

## 4. Quy Trình Git Branching & Pull Request (GitHub Flow)

1. **Không commit trực tiếp lên `main`:** Tất cả tác vụ phát triển, fix bug hay cập nhật tài liệu phải thực thi trên branch riêng biệt (`feat/<tên>`, `fix/<tên>`, `docs/<tên>`).
2. **Tạo Branch mới:**
   ```bash
   git checkout -b feat/v2-firewall-rules
   ```
3. **Thực Thi & Kiểm Trợ Chất Lượng (Pre-Commit Gate):**
   Chạy bộ công cụ kiểm tra chất lượng trước khi push:
   ```bash
   python -m ruff check .
   python -m ruff format --check .
   python -m pylint control_plane.py src/
   python -m mypy --config-file=pyproject.toml control_plane.py src/
   python -m pytest
   ```
4. **Push Branch & Tạo Pull Request:**
   ```bash
   git push origin feat/v2-firewall-rules
   ```
   Sau đó mở Pull Request trên GitHub hướng vào nhánh `main`.

---

## 5. CI Quality Gate & Automated Testing

Mọi PR đẩy vào `main` bắt buộc phải pass 100% CI Quality Gate Workflow (`.github/workflows/ci.yml`):
- **Linter & Formatting:** Ruff check & format validation.
- **Static Code Analysis:** Pylint 0 errors score.
- **Type Inspection:** MyPy zero typing errors.
- **Automated Test Suite:** 100% Pytest suite passing.

---

## 6. Kịch Bản Hủy Release & Rollback Emergency

Trong trường hợp phát hiện lỗi nghiêm trọng trên phiên bản vừa release:
1. Tạo branch hotfix ngay lập tức từ commit ổn định gần nhất:
   ```bash
   git checkout -b fix/rollback-patch
   ```
2. Revert commit gây lỗi hoặc áp dụng patch sửa lỗi.
3. Chạy lại bộ kiểm tra Quality Gate và đẩy PR vào `main` với commit `fix(core): emergency fix for issue ...`.
4. Bot `release-please` sẽ tự động tạo Release PR PATCH mới (VD: `v2.0.1`) để ghi đè bản lỗi một cách an toàn.
