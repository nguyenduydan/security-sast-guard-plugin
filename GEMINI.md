# Security & SAST Guard — Plugin Directives

Plugin này đóng vai trò là "lớp giáp" bảo vệ an toàn cho hệ sinh thái Gemini/Antigravity CLI bằng các cơ chế tự động và chủ động.

## 1. Command Firewall (Bảo vệ thời gian thực)
- Firewall được viết bằng Native PowerShell AST Parse (`hooks/firewall_hook.ps1`), đảm bảo tốc độ cực nhanh (<50ms) và chống được các kỹ thuật Obfuscation/nối chuỗi.
- **Tự động kích hoạt:** Chạy ẩn ở background thông qua hook `PreCommandExecute` mỗi khi hệ thống chuẩn bị thực thi một lệnh Terminal.
- Mọi lệnh nguy hiểm (DENY) sẽ bị chặn đứng tuyệt đối; lệnh nhạy cảm (CONFIRM) sẽ yêu cầu xác nhận.

## 2. SAST Scanner (Quét tĩnh Codebase)
- **Lazy Context Extractor:** Chỉ trích xuất vùng code xung quanh lỗi, tiết kiệm Token.
- **Alert Fatigue Reduction:** Tự động bỏ qua các lỗi (false positives) nếu chúng nằm hoàn toàn trong bình luận (`# comment`) hoặc chuỗi tĩnh (`string`).
- **Draft Mode:** Hỗ trợ "Vibe Coding" mượt mà bằng cách tự động cho qua (auto-allow) các lỗi mức độ MEDIUM/LOW.
- **Chủ động Quét:** 
  > ⚠️ **BẮT BUỘC:** Sau mỗi lần sửa code hoặc hoàn thiện tính năng, BẠN PHẢI gọi lệnh `/sast-audit file <path>` hoặc `/sast-audit codebase` để xác nhận zero lỗ hổng OWASP/CWE trước khi kết thúc tác vụ.

## 3. Quản lý Rules
Sử dụng các Slash Commands sau để điều khiển plugin:
- `/sast-audit-level <lite|full|ultra>`: Đổi mức độ quét.
- `/sast-rules add <file.md>`: Thêm luật bảo mật mới.
- `/sast-status`: Kiểm tra trạng thái Firewall & SAST.
