# Pixi Package Manager cho pyside_base

Tài liệu hướng dẫn sử dụng Pixi cho base này (không phụ thuộc dự án cụ thể). Nếu bạn mới dùng Pixi, xem thêm docs chính thức: https://pixi.sh/latest/

---

## 1) Quick Start

Yêu cầu:
- Windows 10/11, Linux, hoặc macOS
- Đã cài Pixi

Cài Pixi nhanh:
- Windows (PowerShell - admin):
  iwr -useb https://pixi.sh/install.ps1 | iex
- Linux/macOS:
  curl -fsSL https://pixi.sh/install.sh | bash

Bước chạy dự án base:
1. Mở terminal tại thư mục project
2. Cài deps: pixi install
3. Chạy app: pixi run start

Các lệnh hay dùng:
- pixi run dev          # Compile UI trước rồi chạy app
- pixi run compile-ui   # Biên dịch .ui/.qrc
- pixi run generate     # CLI scaffold (controller/service/...)
- pixi run test         # Chạy tests (nếu có)
- pixi run lint         # Kiểm tra code style (ruff)
- pixi run format       # Format code (ruff)
- pixi run type-check   # Kiểm tra kiểu (mypy)
- pixi run check        # Lint + type-check + test

---

## 2) Migration từ pip/requirements.txt sang Pixi

Nếu bạn đang dùng venv + pip + requirements.txt:

1) Tạm lưu lại môi trường cũ (tùy chọn)
- pip freeze > old_installed_packages.txt

2) Cài bằng Pixi
- pixi install
  Lệnh này đọc file pixi.toml, tạo environment trong ./.pixi và tạo lock file pixi.lock.

3) Kích hoạt môi trường
- Cách 1: pixi shell rồi dùng python/pytest… như bình thường
- Cách 2: dùng trực tiếp tasks: pixi run start, pixi run test, …

4) Dọn môi trường cũ (tùy chọn)
- Xóa venv/.venv nếu không cần nữa

Ghi chú:
- File requirements.txt trong repo chỉ còn mục đích tham chiếu lịch sử. Quản lý deps chính thức dùng pixi.toml.

---

## 3) Quản lý Dependencies

- Thêm package từ conda-forge (khuyến nghị):
  pixi add package-name

- Thêm package từ PyPI:
  pixi add --pypi package-name

- Dev tools (đã cấu hình sẵn feature dev): pytest, ruff, mypy sẽ tự có trong môi trường mặc định.

- Update deps:
  - pixi update              # Update tất cả
  - pixi update <package>    # Update một gói

- Xem danh sách/tình trạng:
  - pixi list
  - pixi tree

---

## 4) Tasks trong base này

Các tasks đã được khai báo trong pixi.toml để làm việc với bộ base này:

- Ứng dụng
  - start: python main.py
  - dev: depends_on = [compile-ui, start]

- Scripts dự án
  - compile-ui: python scripts/compile_ui.py
  - generate: python scripts/generate.py (truyền tiếp tham số sau "--")
    - Ví dụ: pixi run generate -- controller MyController
  - set-app-info: python scripts/set_app_info.py

- Chất lượng mã & kiểm thử
  - test: pytest -q
  - lint: ruff check .
  - lint-fix: ruff check . --fix
  - format: ruff format .
  - format-check: ruff format --check .
  - type-check: mypy .
  - check: depends_on = [lint, type-check, test]

- Tiện ích
  - clean-logs: dọn thư mục data/logs
  - check-pixi: in thông tin Python/Platform đang chạy trong env của Pixi

Mẹo:
- Xem danh sách tasks: pixi task list
- Truyền thêm tham số cho task: pixi run <task> -- <args>

---

## 5) Quy trình làm việc gợi ý

Phát triển nhanh:
1) pixi shell
2) Sửa mã nguồn
3) Nếu chỉnh UI: pixi run compile-ui
4) Kiểm tra: pixi run check
5) Chạy app: pixi run start (hoặc pixi run dev)

Trước khi commit:
- pixi run format
- pixi run check

CI/CD (tham khảo):
- Cài Pixi runner và chạy các task: test, lint, check

---

## 6) Troubleshooting

- "pixi: command not found": Khởi động lại terminal sau khi cài Pixi; kiểm tra PATH.
- "lock out of date": pixi install --locked=false
- Env lỗi: xóa thư mục .pixi/ rồi pixi install
- Package không có trên conda-forge: dùng pixi add --pypi <name>
- Windows chậm: thêm .pixi/ vào antivirus exclusion

---

## 7) Best Practices

1) Commit file pixi.lock để đảm bảo reproducible build.
2) Ưu tiên gói từ conda-forge; chỉ dùng PyPI khi cần.
3) Đặt các workflows thường dùng vào [tasks] trong pixi.toml.
4) Dùng pixi shell khi develop; dùng pixi run trong CI.

---

## 8) Liên quan và tài nguyên

- Tài liệu chính thức Pixi: https://pixi.sh/latest/
- Danh sách packages conda-forge: https://conda-forge.org/packages/
- PyPI: https://pypi.org/

Nếu bạn dùng base này để tạo dự án mới, có thể mở rộng pixi.toml (tasks/features) theo nhu cầu riêng của dự án.
