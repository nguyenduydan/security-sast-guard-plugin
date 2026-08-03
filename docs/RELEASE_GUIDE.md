# Hướng Dẫn Quy Trình Xuất Bản Release & Deploy Chuẩn (Release Guide)

Tài liệu này quy định tiêu chuẩn phát hành phiên bản, quy trình commit và tự động hóa xuất bản GitHub Release cho dự án **security-sast-guard-plugin**.

---

## 1. Nguyên Tắc Đặt Tên Phiên Bản & Tiêu Đề Release

### 1.1. Định dạng Tiêu đề Release & Tag
- Tiêu đề Release **chỉ bao gồm chuỗi Semantic Version thuần**, tiền tố `v` kết hợp với số phiên bản (Ví dụ: `v0.0.1`, `v0.1.0`, `v1.0.0`).
- **KHÔNG** thêm tên dự án hay văn bản phía trước tiêu đề (Ví dụ **KHÔNG DÙNG**: `Security SAST Guard v0.0.1`).

### 1.2. Quy tắc Semantic Versioning (SemVer)
- **MAJOR (`v1.0.0`):** Tăng khi có Breaking Changes phá vỡ tương thích ngược.
- **MINOR (`v0.1.0`):** Tăng khi bổ sung tính năng mới (Features, Rules mới) mà vẫn tương thích ngược.
### 1.3. Quy Định Nhánh & Pull Request (Bắt buộc GitHub Flow)
- **Cấm commit trực tiếp lên `main`:** Tất cả các thay đổi mã nguồn, tính năng hay tài liệu phải được thực hiện trên một nhánh độc lập (`feat/<feature-name>`, `fix/<bug-name>`, `docs/<topic-name>`).
- **Quy trình Push & PR:**
  1. Tạo nhánh mới: `git checkout -b feat/ten-tinh-nang`
  2. Commit & Push nhánh lên GitHub: `git push origin feat/ten-tinh-nang`
  3. Mở **Pull Request (PR)** hướng vào nhánh `main`.
  4. Đợi GitHub Actions chạy kiểm tra **CI Quality Gate** đạt điểm xanh 100%.
  5. Tiến hành **Merge Pull Request** vào nhánh `main`.

---

## 2. Quy Trình Phát Hành Phiên Bản (Release Workflow)

### Bước 1: Chuẩn hóa Commit Message (Conventional Commits)
Tất cả các commit phải tuân thủ định dạng: `<type>(<scope>): <description>`
- `feat`: Tính năng mới hoặc quy tắc SAST mới.
- `fix`: Sửa lỗi mã nguồn hoặc lỗi CI.
- `refactor`: Tái cấu trúc mã nguồn.
- `docs`: Cập nhật tài liệu.
- `style`: Định dạng code (Ruff).
- `ci` / `build`: Thay đổi workflow CI/CD.

### Bước 2: Chuẩn Bị Tài Liệu Release
Trước khi phát hành một phiên bản mới `vX.Y.Z`:
1. Khởi tạo file báo cáo chi tiết tại: `docs/releases/vX.Y.Z.md`
2. Cập nhật lịch sử thay đổi trong file `CHANGELOG.md` theo chuẩn **Keep a Changelog**.
3. Đồng bộ phiên bản trong `.release-please-manifest.json`, `pyproject.toml`, và `plugin.json`.

### Bước 3: Đẩy Code & Tạo Git Tag
```bash
# 1. Commit các file tài liệu và cấu hình
git add .
git commit -m "docs(release): prepare release documentation for v0.0.1"
git push origin main

# 2. Tạo Git Tag chuẩn phiên bản thuần (v0.0.1)
git tag -a v0.0.1 -m "Release v0.0.1"

# 3. Đẩy Git Tag lên GitHub
git push origin v0.0.1
```

### Bước 4: Tự Động Hóa Xuất Bản Bài Release trên GitHub
Ngay khi Git Tag `vX.Y.Z` được đẩy lên, GitHub Actions Workflow (`.github/workflows/release.yml`) sẽ tự động:
1. Đọc nội dung mô tả chi tiết từ `docs/releases/vX.Y.Z.md` (hoặc `CHANGELOG.md`).
2. Gọi API xuất bản bài **GitHub Release** chính thức.
3. Đặt tiêu đề Release chuẩn thuần `vX.Y.Z`.
4. Gắn badge **`Latest`** hiển thị ở cột **Releases** của Repository.

---

## 3. Kịch Bản Kiểm Tra & Rollback

### 3.1. Kiểm Tra Chất Lượng Trước Khi Release (CI Quality Gate)
Đảm bảo tất cả các lệnh kiểm tra sau đều vượt qua:
```bash
python -m ruff check .
python -m ruff format --check .
python -m pylint control_plane.py src/
python -m mypy --config-file=pyproject.toml control_plane.py src/
python -m pytest
```

### 3.2. Kịch Bản Hủy Release (Rollback Tag)
Trong trường hợp phát hiện lỗi sau khi push tag:
```bash
# Xóa tag local
git tag -d v0.0.1

# Xóa tag trên GitHub Remote
git push origin :refs/tags/v0.0.1
```
