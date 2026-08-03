# Technical Spec: Plugin Packaging Scripts (Release Download Version)

## 1. Overview
Triển khai bộ 3 script (`install.ps1`, `update.ps1`, `remove.ps1`) bằng PowerShell để người dùng cuối (end-users) cài đặt và quản lý plugin mà **không cần dùng Git**. Các script này sẽ tự động tải file `.zip` từ Github Release mới nhất và giải nén.

## 2. Nguồn dữ liệu (Repository)
- **Repo:** `nguyenduydan/security-sast-guard-plugin`
- **Cách lấy bản mới nhất:** Sử dụng GitHub API để lấy Release mới nhất (`https://api.github.com/repos/nguyenduydan/security-sast-guard-plugin/releases/latest`), hoặc mặc định tải nhánh `main` nếu chưa có Release.

## 3. Các lệnh (Scripts)

### 3.1. `install.ps1`
- **Mục đích:** Cài đặt mới plugin cho người dùng cuối.
- **Hành động:**
  1. Yêu cầu tải script này về chạy cục bộ hoặc chạy qua lệnh one-liner (VD: `Invoke-WebRequest ... | Invoke-Expression`).
  2. Xác định thư mục đích: `$HOME/.gemini/config/plugins/security-sast-guard`.
  3. Kiểm tra xem đã cài đặt chưa. Nếu có rồi, cảnh báo và yêu cầu dùng `update.ps1`.
  4. Tải file ZIP từ GitHub (ưu tiên Release mới nhất).
  5. Giải nén vào thư mục đích.
  6. Xóa file ZIP rác.
  7. Thông báo cài đặt thành công.

### 3.2. `update.ps1`
- **Mục đích:** Cập nhật phiên bản mới nhất cho plugin đã cài đặt.
- **Hành động:**
  1. Xác định thư mục đích: `$HOME/.gemini/config/plugins/security-sast-guard`.
  2. Sao lưu file cấu hình của người dùng (ví dụ: `profile.json`) ra một nơi tạm thời.
  3. Tải file ZIP Release mới nhất từ GitHub.
  4. Xóa các file cũ trong thư mục (ngoại trừ file cấu hình nếu cần).
  5. Giải nén bản mới đè lên thư mục.
  6. Khôi phục lại file cấu hình của người dùng.
  7. Xóa file ZIP rác và thông báo hoàn tất.

### 3.3. `remove.ps1`
- **Mục đích:** Gỡ cài đặt plugin.
- **Hành động:**
  1. Hỏi xác nhận người dùng (tùy chọn).
  2. Xóa toàn bộ thư mục `$HOME/.gemini/config/plugins/security-sast-guard`.
  3. Thông báo hoàn tất.

## 4. Kiến trúc Files
Thêm 3 file script tại thư mục gốc của repository (và sẽ được đính kèm trong các bản Release):
```
security-sast-guard/
├── install.ps1
├── update.ps1
└── remove.ps1
```
