# Proactive AI Auditor Skill Design

## Purpose
Bổ sung một kỹ năng (Skill) mới cho Antigravity tên là `sast-proactive-auditor`. Skill này biến Agent thành một chuyên gia bảo mật tự động, có khả năng vừa bắt trend công nghệ thế giới (tìm kiếm kỹ thuật hack AI mới), vừa review mã nguồn dự án để phát hiện code smell, sau đó tự động tạo Github Issues để đội ngũ phát triển (hoặc các Agent khác) có thể khắc phục.

## Scope
1. **File tạo mới:** `skills/sast-proactive-auditor/SKILL.md` (chứa prompt/hướng dẫn logic của skill).
2. Tích hợp lệnh tạo Issue: Hướng dẫn Agent sử dụng Github MCP (mcp_github_create_issue) hoặc công cụ dòng lệnh `gh issue create`.

## Architecture & Workflow

Khi người dùng gọi `/superpowers:sast-proactive-auditor` (hoặc trực tiếp gọi tên skill), Agent BẮT BUỘC thực thi tuần tự 3 Phase sau mà không cần hỏi thêm:

### Phase 1: Knowledge Gathering (Bắt Trend)
- **Công cụ:** `search_web`
- **Mục tiêu:** Thu thập các mối đe dọa bảo mật mới nhất liên quan đến AI/LLM (ví dụ: Prompt Injection, Jailbreak, Data Exfiltration, OWASP Top 10 for LLM 2026).
- **Hành động:** 
  1. Search web các từ khóa cập nhật.
  2. Đọc thư mục `rules/` bằng `list_dir` và `view_file` để hiểu các luật Firewall/SAST hiện có.
  3. Rút ra kết luận: Những luật nào đang thiếu so với trend thế giới.

### Phase 2: Codebase Auditing (Săn Bug)
- **Công cụ:** `grep_search`, `view_file` (hoặc delegate cho subagent `research`).
- **Mục tiêu:** Rà soát kiến trúc mã nguồn (`src/` và `tests/`) để tìm kiếm:
  - Logic lỏng lẻo hoặc Hardcode secrets.
  - Vấn đề hiệu năng hoặc thiếu Type hints (mypy/pylint issues).
  - Thiếu Unit Test.

### Phase 3: Triage & Issue Creation
- **Hành động:** 
  1. Tổng hợp kết quả từ Phase 1 và Phase 2.
  2. Phân loại thành các nhóm: `bug`, `enhancement`, `security`.
  3. Trình bày một báo cáo nháp (Markdown) cho User xem trước danh sách các Issue dự định tạo.
  4. Yêu cầu User phê duyệt (Dùng `ask_question`).
  5. Nếu được duyệt, dùng `call_mcp_tool` gọi `create_issue` (server `github`) để chính thức đẩy Issue lên kho lưu trữ.

## Global Constraints
- Không tự ý tạo Issue lên Github nếu chưa có sự phê duyệt nháp của người dùng.
- Mỗi Issue phải chứa thông tin chi tiết: Context, Expected Behavior, và Code snippet gợi ý (nếu có).
- Skill phải tuân thủ nghiêm ngặt chuẩn YAML Markdown của Antigravity Skills.
