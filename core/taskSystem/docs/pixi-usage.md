# Pixi Package Manager - Complete Guide

Hướng dẫn đầy đủ về việc sử dụng Pixi package manager trong dự án MyLink GMEOY.

## Table of Contents

- [Quick Start](#quick-start)
- [Installation](#installation)
- [Migration Guide](#migration-guide)
- [Daily Usage](#daily-usage)
- [Tasks Reference](#tasks-reference)
- [Troubleshooting](#troubleshooting)
- [Best Practices](#best-practices)

---

## Quick Start

### 📋 Yêu cầu

- Windows 10/11, Linux, hoặc macOS
- [Pixi](https://pixi.sh) package manager

### 🚀 Setup trong 3 bước

#### 1️⃣ Cài đặt Pixi

**Windows (PowerShell - admin):**
```powershell
iwr -useb https://pixi.sh/install.ps1 | iex
```

**Linux/macOS:**
```bash
curl -fsSL https://pixi.sh/install.sh | bash
```

Restart terminal sau khi cài đặt.

#### 2️⃣ Clone và Install

```bash
cd D:\MyLink\git_repositories\mylink_gmeoy
pixi install
```

⏱️ Lần đầu tiên sẽ mất 2-5 phút để tải dependencies.

#### 3️⃣ Chạy ứng dụng

```bash
pixi run start
```

🎉 Xong! Ứng dụng đang chạy.

### 📚 Commands cơ bản

```bash
# Application
pixi run start        # Chạy app chính
pixi run dev          # Development mode (compile UI + run)
pixi run start-v1     # Chạy phiên bản v1

# Development
pixi run compile-ui   # Compile UI files
pixi run generate     # Generate components
pixi run test         # Run tests

# Code Quality
pixi run lint         # Check code quality
pixi run format       # Format code
pixi run check        # Run all checks

# Cleanup
pixi run clean-all    # Clean everything
```

---

## Installation

### Tại sao Pixi?

#### Ưu điểm của Pixi

1. **Tốc độ cực nhanh**: Pixi sử dụng conda-forge và được viết bằng Rust, cài đặt dependencies nhanh hơn nhiều so với pip
2. **Cross-platform**: Hỗ trợ tốt cho Windows, Linux, và macOS
3. **Reproducible environments**: Lock file đảm bảo môi trường giống nhau trên mọi máy
4. **Task runner tích hợp**: Không cần Makefile hay scripts riêng
5. **Quản lý nhiều environments**: Dev, test, prod trong cùng một project
6. **Tích hợp PyPI**: Vẫn có thể sử dụng packages từ PyPI khi cần

#### So sánh với các công cụ khác

| Tính năng | Pixi | Poetry | PDM | pip + venv |
|-----------|------|--------|-----|------------|
| Tốc độ | ⭐⭐⭐⭐⭐ | ⭐⭐⭐ | ⭐⭐⭐ | ⭐⭐ |
| Cross-platform | ⭐⭐⭐⭐⭐ | ⭐⭐⭐⭐ | ⭐⭐⭐⭐ | ⭐⭐⭐ |
| Task runner | ⭐⭐⭐⭐⭐ | ⭐⭐⭐ | ⭐⭐ | ❌ |
| Lock file | ⭐⭐⭐⭐⭐ | ⭐⭐⭐⭐⭐ | ⭐⭐⭐⭐⭐ | ❌ |
| PyPI support | ⭐⭐⭐⭐⭐ | ⭐⭐⭐⭐⭐ | ⭐⭐⭐⭐⭐ | ⭐⭐⭐⭐⭐ |
| Conda packages | ⭐⭐⭐⭐⭐ | ❌ | ❌ | ❌ |

### Cài đặt Pixi

**Windows (PowerShell - chạy với quyền admin):**
```powershell
iwr -useb https://pixi.sh/install.ps1 | iex
```

**Linux/macOS:**
```bash
curl -fsSL https://pixi.sh/install.sh | bash
```

Sau khi cài đặt, restart terminal và kiểm tra:
```bash
pixi --version
```

### Cấu trúc project

```
mylink_gmeoy/
├── pixi.toml          # Pixi configuration & tasks
├── pyproject.toml     # Python project metadata
├── pixi.lock          # Lock file (commit to git)
├── .pixi/             # Environment folder (ignored by git)
├── core/              # Core modules
├── services/          # Service layer
├── windows/           # UI windows & controllers
├── scripts/           # CLI tools
└── data/              # Application data
```

---

## Migration Guide

### Từ pip + requirements.txt sang Pixi

#### Bước 1: Backup môi trường cũ (tùy chọn)

```bash
# Backup requirements hiện tại
cp requirements.txt requirements.txt.backup

# Lưu danh sách packages đang cài
pip freeze > installed_packages.txt
```

#### Bước 2: Cài đặt dependencies với Pixi

```bash
cd D:\MyLink\git_repositories\mylink_gmeoy
pixi install
```

Lệnh này sẽ:
- Đọc `pixi.toml` và `pyproject.toml`
- Tải và cài đặt tất cả dependencies
- Tạo file `pixi.lock` để lock versions
- Tạo thư mục `.pixi/` chứa environment

**Lưu ý**: Quá trình này có thể mất 2-5 phút lần đầu tiên, nhưng các lần sau sẽ rất nhanh nhờ cache.

#### Bước 3: Kích hoạt environment

**Cách 1: Kích hoạt shell (khuyến nghị cho development)**
```bash
pixi shell
```

Sau khi vào shell, bạn có thể chạy các lệnh Python như bình thường:
```bash
python main.py
python scripts/compile_ui.py
pytest
```

**Cách 2: Chạy trực tiếp với `pixi run` (khuyến nghị cho CI/CD)**
```bash
pixi run start
pixi run test
pixi run lint
```

#### Bước 4: Xóa môi trường cũ (tùy chọn)

Sau khi đã test và chắc chắn mọi thứ hoạt động tốt:

```bash
# Xóa virtual environment cũ (nếu có)
rm -rf venv/
rm -rf .venv/

# Xóa cache pip
rm -rf __pycache__/
find . -type d -name "__pycache__" -exec rm -rf {} +
```

### So sánh Workflows

#### Trước (pip + venv)

```bash
# Setup
python -m venv venv
.\venv\Scripts\activate  # Windows
source venv/bin/activate  # Linux/Mac
pip install -r requirements.txt

# Chạy app
python main.py

# Test
pytest

# Thêm package
pip install new-package
pip freeze > requirements.txt
```

#### Sau (Pixi)

```bash
# Setup
pixi install

# Chạy app
pixi run start

# Test
pixi run test

# Thêm package
pixi add new-package
```

---

## Daily Usage

### 🛠️ Quản lý Dependencies

#### Thêm dependencies mới

**Thêm từ conda-forge (khuyến nghị):**
```bash
pixi add numpy pandas matplotlib
```

**Thêm từ PyPI:**
```bash
pixi add --pypi package-name
```

**Thêm dev dependencies:**
```bash
pixi add --feature dev pytest ruff mypy
```

#### Update dependencies

```bash
# Update tất cả packages
pixi update

# Update package cụ thể
pixi update package-name

# Xem outdated packages
pixi list
```

#### Xóa dependencies

```bash
pixi remove package-name
```

#### Xem danh sách packages

```bash
# Xem tất cả packages đã cài
pixi list

# Xem cây dependencies
pixi tree
```

### 🐚 Shell Environment

```bash
# Activate Pixi shell
pixi shell

# Trong shell, bạn có thể chạy Python trực tiếp
python main.py
pytest
```

### 🎯 Task System

Pixi có task runner tích hợp, được định nghĩa trong `pixi.toml`:

```toml
[tasks]
start = "python main.py"
test = "pytest tests/ -v"
lint = "ruff check ."
```

Bạn có thể:
- Chạy task: `pixi run start`
- Tạo task phụ thuộc: `dev = { depends_on = ["compile-ui", "start"] }`
- Chạy nhiều tasks: `pixi run check` (lint + type-check + test)

### 🌍 Environments

Pixi hỗ trợ nhiều environments trong cùng 1 project:

```bash
# Environment mặc định (có dev tools)
pixi install

# Production environment (không có dev tools)
pixi install --environment prod

# Switch environment
pixi shell --environment prod
```

---

## Tasks Reference

### 📝 Xem danh sách tasks

```bash
pixi task list
```

### 🔧 Setup & Check Tasks

#### `check-pixi`
Kiểm tra xem Pixi đã được cài đặt và cấu hình đúng chưa.

```bash
pixi run check-pixi
```

**Output:**
- ✅ Pixi version
- ✅ Project files status (pixi.toml, pixi.lock)
- ✅ Environment status (.pixi/)
- 📋 Next steps suggestions

#### `info`
Hiển thị thông tin về project và environment.

```bash
pixi run info
```

### 🚀 Application Tasks

#### `start`
Chạy ứng dụng chính (main.py).

```bash
pixi run start
```

#### `start-v1`
Chạy phiên bản v1 của ứng dụng (main_v1.py).

```bash
pixi run start-v1
```

#### `dev`
Development mode - tự động compile UI files và chạy ứng dụng.

```bash
pixi run dev
```

**Dependencies:**
- Chạy `compile-ui` trước
- Sau đó chạy `start`

### 🎨 UI Compilation Tasks

#### `compile-ui`
Compile tất cả .ui files thành Python code.

```bash
pixi run compile-ui
```

**Chức năng:**
- Tìm tất cả .ui files trong project
- Convert thành .py files
- Compile .qrc resources (nếu có)

### 🏗️ Code Generation Tasks

#### `generate`
Generate controllers, services, hoặc components mới.

```bash
# Generate Controller
pixi run generate controller MyController

# Generate Service
pixi run generate service MyService

# Generate Component
pixi run generate component MyComponent
```

#### `set-app-info`
Set thông tin ứng dụng (name, version).

```bash
pixi run set-app-info --name "My App" --version "1.0.0"
```

### 🧪 Testing Tasks

#### `test`
Chạy test suite với pytest.

```bash
pixi run test
```

#### `test-cov`
Chạy tests với coverage report.

```bash
pixi run test-cov
```

**Output:**
- Terminal coverage report
- HTML coverage report trong `htmlcov/`

### 🔍 Code Quality Tasks

#### `lint`
Check code quality với Ruff.

```bash
pixi run lint
```

#### `lint-fix`
Tự động fix linting issues.

```bash
pixi run lint-fix
```

#### `format`
Format code với Ruff formatter.

```bash
pixi run format
```

#### `format-check`
Check formatting without modifying files.

```bash
pixi run format-check
```

#### `type-check`
Static type checking với mypy.

```bash
pixi run type-check
```

#### `check`
Chạy tất cả quality checks (lint + type-check + test).

```bash
pixi run check
```

#### `build`
Prepare code for production (lint + type-check + compile-ui).

```bash
pixi run build
```

### 🔧 RPA Server Tasks

#### `install-rpa-server`
Cài đặt Fire RPA server lên thiết bị Android.

```bash
pixi run install-rpa-server
```

#### `rpa-server`
Quản lý RPA server.

```bash
pixi run rpa-server
```

### 🧹 Cleanup Tasks

#### `clean-logs`
Xóa tất cả log files.

```bash
pixi run clean-logs
```

#### `clean-cache`
Xóa Python cache files.

```bash
pixi run clean-cache
```

#### `clean-all`
Xóa logs và cache.

```bash
pixi run clean-all
```

### 🔄 Workflows thường dùng

#### Development Workflow

```bash
# 1. Activate shell
pixi shell

# 2. Make changes to code...

# 3. If UI changed
pixi run compile-ui

# 4. Test changes
pixi run test

# 5. Check code quality
pixi run check

# 6. Run app
pixi run start
```

#### Quick Development

```bash
# Compile UI + Run in one command
pixi run dev
```

#### Pre-commit Workflow

```bash
# Format code
pixi run format

# Run all checks
pixi run check

# If all pass, commit
git add .
git commit -m "Your message"
```

#### Build & Release Workflow

```bash
# 1. Run all checks
pixi run check

# 2. Build production
pixi run build

# 3. Clean up
pixi run clean-all

# 4. Final test
pixi run test-cov

# 5. Tag and release
git tag v1.0.0
git push --tags
```

### 🎯 Task Dependencies

Một số tasks phụ thuộc vào tasks khác:

```
dev
├── compile-ui
└── start

check
├── lint
├── type-check
└── test

build
├── lint
├── type-check
└── compile-ui

clean-all
├── clean-logs
└── clean-cache
```

---

## Troubleshooting

### "pixi: command not found"
- Restart terminal sau khi cài Pixi
- Kiểm tra PATH: `echo $env:PATH` (Windows) hoặc `echo $PATH` (Linux/Mac)

### "Lock file out of date"
```bash
pixi install --locked=false
```

### Environment bị lỗi
```bash
rm -rf .pixi/
pixi install
```

### Package không tìm thấy
```bash
# Thử tìm trên PyPI
pixi add --pypi package-name
```

### Lỗi "Package not found"

Nếu package không có trên conda-forge:
```bash
pixi add --pypi package-name
```

### Xung đột dependencies

```bash
# Xem cây dependencies
pixi tree

# Update để resolve conflicts
pixi update
```

### Pixi chậm trên Windows

- Thêm `.pixi/` vào Windows Defender exclusions
- Sử dụng SSD thay vì HDD

### Task không chạy

```bash
# Check if Pixi is working
pixi run check-pixi

# Reinstall environment
rm -rf .pixi/
pixi install
```

### Task chạy sai version Python

```bash
# Check Python version in environment
pixi shell
python --version

# Should be Python 3.9+
```

### Task không tìm thấy module

```bash
# Ensure all dependencies installed
pixi install

# Update dependencies
pixi update
```

---

## Best Practices

1. **Commit `pixi.lock`**: Đảm bảo reproducible builds
2. **Sử dụng conda-forge trước**: Ưu tiên conda-forge packages vì nhanh hơn và có binary wheels
3. **Tách dev dependencies**: Sử dụng features cho dev, test, docs
4. **Định nghĩa tasks**: Tạo tasks cho các workflows thường dùng
5. **Sử dụng `pixi shell`**: Khi development, `pixi run` cho CI/CD
6. **Update thường xuyên**: Chạy `pixi update` định kỳ để có security patches

---

## CI/CD Integration

### GitHub Actions

```yaml
name: CI

on: [push, pull_request]

jobs:
  test:
    runs-on: windows-latest
    steps:
      - uses: actions/checkout@v3
      
      - name: Setup Pixi
        uses: prefix-dev/setup-pixi@v0.4.1
        with:
          pixi-version: latest
      
      - name: Run tests
        run: pixi run test
      
      - name: Run lint
        run: pixi run lint
```

### GitLab CI

```yaml
image: ghcr.io/prefix-dev/pixi:latest

test:
  script:
    - pixi install
    - pixi run test
    - pixi run lint
```

---

## FAQ

**Q: Tôi có thể dùng cả pip và pixi không?**  
A: Có, nhưng không khuyến nghị. Nếu cần package từ PyPI, dùng `pixi add --pypi`.

**Q: Pixi có hỗ trợ Python 2.7 không?**  
A: Không, Pixi chỉ hỗ trợ Python 3.7+.

**Q: Kích thước `.pixi/` folder?**  
A: Thường 200-500MB, tùy vào số lượng packages.

**Q: Có thể share environment giữa các projects không?**  
A: Không, mỗi project có environment riêng. Nhưng Pixi có cache nên không tốn dung lượng.

**Q: Làm sao để uninstall Pixi?**  
A: 
```bash
# Windows
rm $env:USERPROFILE\.pixi
rm $env:USERPROFILE\.pixi-bin

# Linux/Mac
rm -rf ~/.pixi
rm -rf ~/.pixi-bin
```

---

## Resources

- [Pixi Documentation](https://pixi.sh/latest/)
- [Pixi GitHub](https://github.com/prefix-dev/pixi)
- [conda-forge packages](https://conda-forge.org/packages/)
- [PyPI packages](https://pypi.org/)
- [Pixi Tasks Documentation](https://pixi.sh/latest/features/tasks/)
- [Task Dependencies](https://pixi.sh/latest/features/tasks/#task-dependencies)

---

## Pro Tips

1. **Sử dụng `pixi shell`** khi develop để tránh phải gõ `pixi run` liên tục
2. **Commit `pixi.lock`** để đảm bảo môi trường giống nhau trên mọi máy
3. **Xem tất cả tasks**: `pixi task list`
4. **Xem dependencies tree**: `pixi tree`
5. **Tạo tasks mới** trong `pixi.toml` cho workflows thường dùng
6. **Chạy nhiều tasks liên tiếp**: `pixi run format && pixi run lint && pixi run test`

---

**Câu hỏi?** Mở issue hoặc xem [README.md](../README.md) để biết thêm chi tiết.

**Happy Coding! 🚀**

