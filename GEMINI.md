# Security & SAST Guard — Plugin Directives

Plugin này tự động chạy Command Firewall ở background (PreCommandExecute hook).

Sau mỗi lần sửa code, gọi `/sast-audit file <path>` để xác nhận zero lỗ hổng OWASP/CWE.

## Release & Git Flow (Conventional Commits)

- **Sử dụng Conventional Commits có Scope:** Mọi commit message phải tuân thủ chuẩn Conventional Commits và **BẮT BUỘC phải có scope (phạm vi)** để làm rõ module nào đang được sửa (VD: `fix(sast-status): ...`, `feat(firewall): ...`, `chore(release): ...`, `docs(gemini): ...`).
- **Không đánh Tag thủ công:** Repository sử dụng `release-please` để quản lý phiên bản tự động. Tuyệt đối **KHÔNG** tự ý chạy `git tag` hoặc tạo nhánh `release/vX.Y.Z` thủ công trừ khi có yêu cầu đặc biệt từ user.
- **Không tự ý sửa file version (plugin.json, package.json):** `release-please` sẽ tự động tạo Pull Request nâng version và cập nhật Changelog dựa trên lịch sử commit. Không tự tiện sửa version trong file config để tránh hạ cấp version (downgrade) so với tag mới nhất trên GitHub.
- **Workflow:** Tạo nhánh feature/bugfix -> Code -> Commit đúng chuẩn -> Trả về `main`. Bot sẽ lo phần còn lại.
