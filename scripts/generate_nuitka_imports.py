#!/usr/bin/env python
# -*- coding: utf-8 -*-

import os
import re
from pathlib import Path

# Thư mục cần quét
DIRS_TO_SCAN = ["./"]
EXCLUED_DIR_NAMES = ['examples', 'ccr', 'samples', 'scripts', 'tests', 'tests_core']
EXCLUED_FILES = ['nuitka_hook.py', 'generate_nuitka_imports.py', 'setup.py', 'main.py']
# Đường dẫn tới thư mục gốc của dự án - thay đổi nếu cần
PROJECT_ROOT = "./"
def is_excluded_dir(dir_path):
    for name in EXCLUED_DIR_NAMES:
        if str(dir_path).endswith(name):
            return True
    return False
def is_valid_module_file(filepath):
    """Kiểm tra xem file có phải là Python module hay không"""
    # Bỏ qua __pycache__ và các file ẩn (bắt đầu bằng .)
    if "__pycache__" in filepath or os.path.basename(filepath).startswith('.'):
        return False
    if is_excluded_dir(dir_path=filepath):
        return False
    for excluded_file in EXCLUED_FILES:
        if excluded_file in filepath:
            return False
    if "examples" in filepath:
        return False
    if "old" in filepath.lower():
        return False
    if "packages" in filepath and "ccr" in filepath:
        return False
    # Chỉ lấy file .py
    if filepath.endswith('.py'):
        return True
    
    return False

def parse_pycache_filename(filename):
    """Parse tên module từ file trong __pycache__"""
    # Ví dụ: CheckerController.cpython-310.pyc -> CheckerController
    match = re.match(r'(.+)\.cpython-\d+.*\.pyc', filename)
    if match:
        modulename = match.group(1)
        if is_valid_module_file(modulename):
            return modulename
    return None

def find_modules_from_pycache(dir_path):
    """Tìm các module dựa vào __pycache__"""
    modules = set()
    pycache_dir = os.path.join(dir_path, "__pycache__")
    
    if os.path.exists(pycache_dir) and os.path.isdir(pycache_dir):
        for filename in os.listdir(pycache_dir):
            module_name = parse_pycache_filename(filename)
            if module_name:
                # Tạo tên module đầy đủ
                rel_path = os.path.relpath(dir_path, PROJECT_ROOT)
                if rel_path == ".":
                    modules.add(module_name)
                else:
                    module_path = rel_path.replace(os.sep, ".")
                    modules.add(f"{module_path}.{module_name}")
    
    return modules

def find_modules_from_py_files(dir_path):
    """Tìm các module dựa vào file .py"""
    for name in EXCLUED_DIR_NAMES:
        if str(dir_path).endswith(name):
            print('dir_path', dir_path)
            return set()

    modules = set()
    
    for item in os.listdir(dir_path):
        item_path = os.path.join(dir_path, item)
        
        # Nếu là thư mục, kiểm tra xem có phải là package không
        if os.path.isdir(item_path):
            if os.path.exists(os.path.join(item_path, "__init__.py")):
                # Đây là package, thêm vào danh sách
                rel_path = os.path.relpath(item_path, PROJECT_ROOT)
                module_path = rel_path.replace(os.sep, ".")
                modules.add(module_path)
                
                # Tiếp tục quét đệ quy
                sub_modules = find_modules_from_py_files(item_path)
                modules.update(sub_modules)
        
        # Nếu là file .py
        elif is_valid_module_file(item_path):
            module_name = os.path.splitext(item)[0]
            if module_name != "__init__":  # Bỏ qua file __init__.py
                rel_path = os.path.relpath(dir_path, PROJECT_ROOT)
                if rel_path == ".":
                    modules.add(module_name)
                else:
                    module_path = rel_path.replace(os.sep, ".")
                    modules.add(f"{module_path}.{module_name}")
    
    return modules

def get_modules_from_dir(dir_path):
    all_modules = set()
    
    if not os.path.exists(dir_path):
        print(f"Warning: Directory {dir_path} does not exist, skipping...")
        return all_modules
    # Quét các module từ file .py
    py_modules = find_modules_from_py_files(dir_path)
    all_modules.update(py_modules)
    
    # Quét các module từ __pycache__ nếu có
    pycache_modules = find_modules_from_pycache(dir_path)
    all_modules.update(pycache_modules)
    
    return all_modules

def generate_nuitka_hook():
    """Tạo file nuitka_hook.py với các import được phát hiện"""
    all_modules = set()
    
    for dir_name in DIRS_TO_SCAN:
        dir_path = os.path.join(PROJECT_ROOT, dir_name)
        if not os.path.exists(dir_path):
            print(f"Warning: Directory {dir_path} does not exist, skipping...")
            continue
            
        # Quét các module từ file .py
        py_modules = find_modules_from_py_files(dir_path)
        all_modules.update(py_modules)
        
        # Quét các module từ __pycache__ nếu có
        pycache_modules = find_modules_from_pycache(dir_path)
        all_modules.update(pycache_modules)
    
    # Thêm các package gốc
    for dir_name in DIRS_TO_SCAN:
        curDir = os.path.join(PROJECT_ROOT, dir_name)
        for o in os.listdir(curDir):
            if os.path.isdir(os.path.join(curDir, o)):
                all_modules.update(get_modules_from_dir(os.path.join(curDir, o)))
        if os.path.exists(os.path.join(curDir, "__init__.py")) and not is_excluded_dir(curDir):
            all_modules.add(dir_name)
    
    # Sắp xếp để dễ đọc
    sorted_modules = sorted(all_modules)
    
    # Tạo nội dung file hook
    from datetime import datetime
    hook_content = [
        "# nuitka_hook.py - Auto-generated file",
        "# This file helps Nuitka identify modules to include in the build",
        "# Generated: " + datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        "",
    ]
    
    for module in sorted_modules:
        if "(" in module or ")" in module:
            continue
        hook_content.append(f"import {module}")
    
    # Tạo file nuitka_hook.py
    with open("nuitka_hook.py", "w", encoding="utf-8") as f:
        f.write("\n".join(hook_content))
    
    # Tạo nội dung cho include-package arguments
    include_packages = []
    for dir_name in DIRS_TO_SCAN:
        include_packages.append(f"--include-package={dir_name}")
    
    # Tạo file .bat để build
    bat_content = [
        "@echo off",
        "python -m nuitka --standalone ^",
        "    --show-progress ^",
        "    --follow-imports ^",
        "    --enable-plugin=pyside6 ^",
        "    --include-data-dir=data=data ^",
        "    --include-data-dir=vendor=vendor ^",
        "    --include-data-dir=assets=assets ^"
    ]
    
    # Thêm các package cần include
    for package in include_packages:
        bat_content.append(f"    {package} ^")
    
    # Tiếp tục với các tham số khác
    bat_content.extend([
        "    --nofollow-import-to=tkinter,matplotlib ^",
        "    --windows-disable-console ^",
        "    --windows-icon-from-ico=assets/icon.png ^",
        "    --output-dir=dist ^",
        "    --include-module=nuitka_hook ^",
        "    main.py"
    ])
    
    # Tạo file build.bat
    with open("build_full.bat", "w", encoding="utf-8") as f:
        f.write("\n".join(bat_content))
    
    print(f"Generated nuitka_hook.py with {len(sorted_modules)} modules")
    print(f"Generated build_full.bat with {len(include_packages)} include-package arguments")
    print("\nTo build your application, run: build_full.bat")

if __name__ == "__main__":
    # e = input('e')
    # if e != 'e':
    #     generate_nuitka_hook()
    # e = input('e')
    # if e != 'e':
    generate_nuitka_hook()
