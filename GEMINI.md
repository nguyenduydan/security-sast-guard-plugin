# Security & SAST Guard — Agent Directives

System này tự động vận hành hai lớp phòng thủ bảo mật Zero-Trust: **Command Interception Firewall** ở background (PreCommandExecute hook) và **Stdio SAST Intelligence Server** dành cho các AI Agent (Antigravity 2.0 / Gemini CLI).

Sau mỗi lần sửa đổi mã nguồn hoặc chuẩn bị commit/push, Agent **BẮT BUỘC** phải gọi `/sast-audit` (hoặc mở tương tác qua `ask_question` modal) để xác nhận zero lỗ hổng OWASP/CWE theo level được cấu hình trong `.sast/profile.json`.

---

## 1. Khám Phá Mã Nguồn & Sử Dụng MCP (Agentic Code Discovery)

- **Ưu tiên codebase-memory-mcp:** Agent **BẮT BUỘC** phải ưu tiên sử dụng các công cụ từ MCP `codebase-memory-mcp` (như `search_graph`, `query_graph`, `get_code_snippet`, `get_architecture`) để phân tích kiến trúc mã nguồn, mối quan hệ phụ thuộc và dataflow trước khi dùng các lệnh tìm kiếm mù quáng (`grep` hoặc đọc file chay).
- **Tích hợp sast-guard MCP Server (12 Tools):** Agent **BẮT BUỘC** gọi các Stdio MCP tool được cung cấp bởi `sast-guard` khi thực hiện tác vụ bảo mật:
  - `sast_scan_file`: Kiểm tra an toàn cho một file cụ thể và trích xuất taint trace.
  - `sast_scan_diff`: Kiểm tra bảo mật các dòng code vừa thay đổi theo Git diff.
  - `sast_check_command`: Kiểm tra mức độ an toàn của lệnh shell trước khi đề xuất thực thi.
  - `sast_get_dataflow_path`: Truy vết đường đi dữ liệu từ Source đến Sink.
  - `sast_get_taint_context`: Xem snippet ngữ cảnh taint tại dòng chỉ định.
  - `sast_get_status` / `sast_set_mode` / `sast_set_level` / `sast_init` / `sast_sync_rules` / `sast_get_help` / `sast_generate_report`.

---

## 2. Lớp Bảo Vệ Command Execution Firewall Rules (Zero-Trust)

Tất cả các lệnh terminal được chạy bởi Agent hoặc User đều phải thông qua **Command Execution Firewall (PreCommandExecute hook)**:

1. **10-Stage De-obfuscation Normalizer:** Mọi câu lệnh phức tạp, mã hóa (Base64, Hex, Unicode, Char Code, Subcommands, Env expansion, String interpolation, Caret/Backtick stripping) đều được giải mã trước khi phân tích.
2. **Capability & Intent Classification:** Đánh giá intent của lệnh dựa trên 7 nhóm capability (`NETWORK`, `FILE_READ`, `FILE_WRITE`, `PROCESS_EXEC`, `PRIVILEGE_CHANGE`, `PERSISTENCE`, `DATA_TRANSFER`) để phát hiện các hành vi độc hại như `EXFILTRATION`, `DESTRUCTIVE`, `PRIVILEGE_ESCALATION`.
3. **Multi-Command Threat Chains:** Tự động chặn hoặc yêu cầu xác nhận các chuỗi lệnh nguy hiểm (`Download+Execute`, `Set-ExecutionPolicy Bypass`, thực thi script không xác minh).
4. **Quy tắc Verdict:**
   - **`DENY`:** Tuyệt đối **KHÔNG** được thực thi hay tìm cách bypass. Không được tự ý thử lại lệnh bị DENY.
   - **`CONFIRM`:** Yêu cầu xác nhận từ người dùng qua `ask_question` modal trước khi thực thi.
   - **`ALLOW`:** Cho phép thực thi bình thường.
5. **Append-Only Audit Log:** Mọi verdict và lệnh kiểm tra đều được ghi lại mã hóa tại `.sast/firewall_audit.jsonl`.

---

## 3. Quy Trình Release & Git Flow (Conventional Commits)

- **Sử dụng Conventional Commits có Scope:** Mọi commit message **BẮT BUỘC** tuân thủ chuẩn `<type>(<scope>): <description>`. Phân loại commit:
  - `feat`: **CHỈ DÙNG** khi thêm tính năng mới vào mã nguồn lõi (làm tăng Minor Version). Không dùng `feat` cho sửa nhỏ hay tài liệu.
  - `fix`: Khi sửa lỗi (bug) trong mã nguồn hoặc script (Tăng Patch Version).
  - `chore`: Tác vụ bảo trì, dọn dẹp, cập nhật thư viện, cấu hình CI/CD (Tăng Patch Version).
  - `refactor`: Viết lại code nhưng không thay đổi hành vi hiện tại (Tăng Patch Version).
  - `docs`: Khi thêm/sửa tài liệu (`.md`, docstrings). Không tạo release mới.
  - `style`: Sửa định dạng code (khoảng trắng, formatting).
  - `test`: Thêm hoặc sửa các bài unit test.
- **Không Đánh Tag / Sửa Version Thủ Công:** Repository sử dụng `release-please` v4 để tự động quản lý phiên bản. Tuyệt đối **KHÔNG** tự ý chạy `git tag`, không sửa thủ công `plugin.json` hay `pyproject.toml` để tránh downgrade version. Bot `release-please` sẽ tự động tạo Pull Request nâng version và cập nhật `CHANGELOG.md`.
- **Cam kết nguyên tử cho từng Issue (Atomic Commits per Issue):** Tuyệt đối **KHÔNG** gom nhiều issues để làm chung rồi commit gộp 1 lần. Mỗi issue **BẮT BUỘC** phải được giải quyết và tạo commit riêng biệt (1 issue = 1 commit) kèm từ khóa liên kết rõ ràng dạng `Fixes #<id>` (VD: `fix(firewall): strip shell wrapper prefixes (Fixes #176)`). Điều này đảm bảo theo dõi chính xác tiến độ Milestone trên GitHub và giúp tự động đóng issue khi PR được merge.
- **Luồng Git Branching:**
  1. Tuyệt đối **KHÔNG** commit trực tiếp lên `main`.
  2. Phải tạo nhánh mới: `git checkout -b <type>/<tên-nhánh>` (VD: `git checkout -b fix/taint-tracker` hoặc `git checkout -b feat/firewall-rules`).
  3. Đẩy code lên remote và báo cáo cho người dùng mở Pull Request vào `main`.

---

## 4. Kiểm Tra Chất Lượng & CI Quality Gate Bắt Bắt Buộc

Trước khi commit, push code hoặc báo cáo hoàn thành nhiệm vụ, Agent **BẮT BUỘC** phải chạy bộ kiểm tra chất lượng và đảm bảo điểm số 100% green (zero errors):

```bash
python -m ruff check .
python -m ruff format --check .
python -m pylint control_plane.py src/
python -m mypy --config-file=pyproject.toml control_plane.py src/
python -m pytest
```

Nếu có bất kỳ lỗi linter, format, mypy hay test failure nào, Agent phải khắc phục triệt để trước khi kết thúc tác vụ.

---

## 5. Chính Sách Phản Hồi & Ngôn Ngữ

- **Ngôn ngữ:** Trả lời bằng Tiếng Việt khi người dùng giao tiếp bằng Tiếng Việt.
- **Tính súc tích:** Báo cáo các thay đổi file trong 1–2 dòng. Tóm tắt kết quả công cụ trong 2–3 câu. Không mô tả suy nghĩ trung gian dài dòng.
