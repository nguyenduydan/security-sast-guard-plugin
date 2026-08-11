# Security & SAST Guard — Plugin Directives

Plugin này tự động chạy Command Firewall ở background (PreCommandExecute hook).

Sau mỗi lần sửa code, gọi `/sast-audit` (hoặc mở Grill UI tương tác qua `ask_question`) để xác nhận zero lỗ hổng OWASP/CWE theo level cài đặt trong profile.json.

## Release & Git Flow (Conventional Commits)

- **Sử dụng Conventional Commits có Scope:** Mọi commit message BẮT BUỘC tuân thủ chuẩn và có scope. Định nghĩa các loại commit phải được áp dụng khắt khe:
  - `feat`: **CHỈ DÙNG** khi thực sự thêm một tính năng mới vào mã nguồn lõi (làm thay đổi logic hoạt động của sản phẩm). Tuyệt đối không dùng `feat` cho các sửa đổi nhỏ, thêm tài liệu, hoặc chỉnh sửa script phụ trợ. (Gây nhảy Minor Version).
  - `fix`: Khi sửa một lỗi (bug) trong mã nguồn hoặc script hiện tại. (Gây nhảy Patch Version).
  - `chore`: Các tác vụ bảo trì, dọn dẹp, update thư viện, chỉnh sửa config CI/CD. (Được tính là tăng Patch Version).
  - `refactor`: Viết lại code nhưng không thay đổi hành vi hiện tại. (Được tính là tăng Patch Version).
  - `docs`: Khi thêm/sửa tài liệu (`.md`, bình luận code, thiết kế spec). KHÔNG kích hoạt Release mới.
  - `style`: Sửa định dạng code (khoảng trắng, dấu phẩy...), không ảnh hưởng logic.
  - `test`: Thêm hoặc sửa các bài kiểm thử (unit test).
- **Không đánh Tag thủ công:** Repository sử dụng `release-please` để quản lý phiên bản tự động. Tuyệt đối **KHÔNG** tự ý chạy `git tag` hoặc tạo nhánh `release/vX.Y.Z` thủ công trừ khi có yêu cầu đặc biệt từ user.
- **Không tự ý sửa file version (plugin.json, package.json):** `release-please` sẽ tự động tạo Pull Request nâng version và cập nhật Changelog dựa trên lịch sử commit. Không tự tiện sửa version trong file config để tránh hạ cấp version (downgrade) so với tag mới nhất trên GitHub.
## Quy Trình Làm Việc Bắt Buộc (Agent Git Workflow)

Khi được yêu cầu fix bug hoặc thêm tính năng, Agent BẮT BUỘC tuân thủ luồng sau:
1. **Tuyệt đối không commit trực tiếp lên `main`**: Trước khi sửa đổi bất kỳ code nào, phải tạo và chuyển sang nhánh mới bằng lệnh `git checkout -b <loại>/<tên-nhánh>` (VD: `git checkout -b fix/sast-status` hoặc `git checkout -b feat/firewall-rules`).
2. **Thực thi và Kiểm thử**: 
   - Sửa code và chạy các bài test/linter (như `pytest`, `mypy`, `pylint` hoặc các script test có sẵn trong dự án) để đảm bảo không phá vỡ tính năng hiện tại.
   - **Kiểm tra CI/CD Bắt Buộc Trước Khi Commit/Push:** BẮT BUỘC phải thực thi kiểm tra toàn bộ linter (`python -m pylint ...`), bộ định dạng (`python -m ruff check .` và `python -m ruff format --check .`), cùng test suite (`pytest`). Phải đảm bảo điểm số linter tối đa và mọi lệnh check (kể cả ruff) đều pass 100% (không còn cảnh báo hay lỗi format) **ngay trước khi commit**, push code hoặc báo cáo hoàn thành. Nếu có bất kỳ chỉnh sửa nào (dù nhỏ nhất), cũng phải chạy lại các lệnh check này VÀ CẢ TEST SUITE trước khi tạo commit mới.
   - Bắt buộc chạy `/sast-audit file <path>` để kiểm tra bảo mật (không có lỗ hổng OWASP/CWE).
3. **Commit đúng chuẩn**: Bắt buộc sử dụng Conventional Commits có Scope (như đã quy định ở trên).
4. **Không Merge/Tag thủ công**: Báo cáo lại cho User để họ tự tạo Pull Request và Merge vào `main`. Không được tự ý `git merge` vào `main` hay đánh tag phiên bản. Bot `release-please` sẽ lo phần còn lại.

## Khám Phá Mã Nguồn (Agentic Code Discovery)

- **Sử dụng MCP (codebase-memory-mcp):** Agent BẮT BUỘC phải ưu tiên sử dụng các công cụ từ MCP `codebase-memory-mcp` (như `search_graph`, `query_graph`, `get_code_snippet`, `get_architecture`) để khám phá và phân tích kiến trúc mã nguồn trước khi dùng các lệnh tìm kiếm mù quáng (`grep` hoặc đọc chay). Điều này giúp Agent hiểu sâu về Dependency và các liên kết trong dự án.
