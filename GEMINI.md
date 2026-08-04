# Security & SAST Guard — Plugin Directives

Plugin này tự động chạy Command Firewall ở background (PreCommandExecute hook).

Sau mỗi lần sửa code, gọi `/sast-audit file <path>` để xác nhận zero lỗ hổng OWASP/CWE.

## Release & Git Flow (Conventional Commits)

- **Sử dụng Conventional Commits có Scope:** Mọi commit message phải tuân thủ chuẩn Conventional Commits và **BẮT BUỘC phải có scope (phạm vi)** để làm rõ module nào đang được sửa (VD: `fix(sast-status): ...`, `feat(firewall): ...`, `chore(release): ...`, `docs(gemini): ...`).
- **Không đánh Tag thủ công:** Repository sử dụng `release-please` để quản lý phiên bản tự động. Tuyệt đối **KHÔNG** tự ý chạy `git tag` hoặc tạo nhánh `release/vX.Y.Z` thủ công trừ khi có yêu cầu đặc biệt từ user.
- **Không tự ý sửa file version (plugin.json, package.json):** `release-please` sẽ tự động tạo Pull Request nâng version và cập nhật Changelog dựa trên lịch sử commit. Không tự tiện sửa version trong file config để tránh hạ cấp version (downgrade) so với tag mới nhất trên GitHub.
## Quy Trình Làm Việc Bắt Buộc (Agent Git Workflow)

Khi được yêu cầu fix bug hoặc thêm tính năng, Agent BẮT BUỘC tuân thủ luồng sau:
1. **Tuyệt đối không commit trực tiếp lên `main`**: Trước khi sửa đổi bất kỳ code nào, phải tạo và chuyển sang nhánh mới bằng lệnh `git checkout -b <loại>/<tên-nhánh>` (VD: `git checkout -b fix/sast-status` hoặc `git checkout -b feat/firewall-rules`).
2. **Thực thi và Kiểm thử**: Sửa code và chạy `/sast-audit file <path>` để kiểm tra bảo mật.
3. **Commit đúng chuẩn**: Bắt buộc sử dụng Conventional Commits có Scope (như đã quy định ở trên).
4. **Không Merge/Tag thủ công**: Báo cáo lại cho User để họ tự tạo Pull Request và Merge vào `main`. Không được tự ý `git merge` vào `main` hay đánh tag phiên bản. Bot `release-please` sẽ lo phần còn lại.
