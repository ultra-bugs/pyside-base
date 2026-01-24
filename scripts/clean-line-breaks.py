#                  M""""""""`M            dP
#                  Mmmmmm   .M            88
#                  MMMMP  .MMM  dP    dP  88  .dP   .d8888b.
#                  MMP  .MMMMM  88    88  88888"    88'  `88
#                  M' .MMMMMMM  88.  .88  88  `8b.  88.  .88
#                  M         M  `88888P'  dP   `YP  `88888P'
#                  MMMMMMMMMMM    -*-  Created by Zuko  -*-
#
#                  * * * * * * * * * * * * * * * * * * * * *
#                  * -    - -   F.R.E.E.M.I.N.D   - -    - *
#                  * -  Copyright © 2026 (Z) Programing  - *
#                  *    -  -  All Rights Reserved  -  -    *
#                  * * * * * * * * * * * * * * * * * * * * *

#
import ast
import subprocess
import sys
from pathlib import Path


def get_ruff_target_files():
    """
    Retrieves the list of files Ruff is configured to process.
    Respects include, exclude, and .gitignore settings from pyproject.toml/ruff.toml.
    """
    try:
        # 'ruff check --show-files' returns the resolved list of files
        result = subprocess.check_output(['ruff', 'check', '--show-files'], text=True, stderr=subprocess.DEVNULL)
        return [f.strip() for f in result.splitlines() if f.strip().endswith('.py')]
    except (subprocess.CalledProcessError, FileNotFoundError) as e:
        print(f'Error: Could not invoke Ruff to get file list. {e}')
        return []


def remove_empty_lines_in_scope(file_path):
    """
    Parses the file into an AST, identifies function/method boundaries,
    and removes empty lines only within those ranges.
    """
    path = Path(file_path)
    if not path.exists():
        return
    with open(path, 'r', encoding='utf-8') as f:
        lines = f.readlines()
    source_code = ''.join(lines)
    try:
        tree = ast.parse(source_code)
    except SyntaxError:
        print(f'Syntax Error in {file_path}, skipping...')
        return
    # Extract line ranges (start, end) for all function and method definitions
    function_ranges = []
    for node in ast.walk(tree):
        if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)):
            # lineno points to the first decorator or 'def'
            # end_lineno points to the last line of the body
            function_ranges.append((node.lineno, node.end_lineno))
    if not function_ranges:
        return
    optimized_lines = []
    for idx, line in enumerate(lines, start=1):
        # Check if current line index falls within any function range
        is_inside_fn = any(start <= idx <= end for start, end in function_ranges)
        # Remove line if it's inside a function AND is empty/whitespace only
        if is_inside_fn and not line.strip():
            continue
        optimized_lines.append(line)
    # Write changes back only if the file content was modified
    if len(optimized_lines) != len(lines):
        with open(path, 'w', encoding='utf-8') as f:
            f.writelines(optimized_lines)
        print(f'Modified: {file_path}')


def main():
    # 1. Standardize code via Ruff Format first
    print('Step 1: Running Ruff Format...')
    subprocess.run(['ruff', 'format', '.'], check=False)
    # 2. Get the list of files Ruff actually cares about
    print('Step 2: Syncing with Ruff file list...')
    target_files = get_ruff_target_files()
    if not target_files:
        print('No files to process.')
        return
    # 3. Apply the AST-based empty line removal
    print(f'Step 3: Processing {len(target_files)} files...')
    for file_path in target_files:
        remove_empty_lines_in_scope(file_path)
    print('Pipeline finished successfully.')


import fnmatch
import os

# ================= CONFIGURATION =================
TRIGGER_LINE = '#              * * * * * * * * * * * * * * * * * * * * *'
TARGET_EXT = '.py'

# Hỗ trợ wildcard standard: '*' (mọi ký tự), '?' (1 ký tự), '[seq]'
# '.*' sẽ match các folder ẩn như .git, .idea, .venv, etc.
SKIP_DIR_NAMES = ['.*', 'data', 'assets', 'nghien_cuu_i9']
# =================================================


def clean_file(filepath):
    try:
        with open(filepath, 'r', encoding='utf-8') as f:
            lines = f.readlines()
        trigger_indices = [i for i, line in enumerate(lines) if TRIGGER_LINE in line]
        if not trigger_indices:
            return
        last_trigger_idx = trigger_indices[-1]  # Lấy dòng border dưới cùng
        # Phần giữ lại (Header gốc)
        new_content = lines[: last_trigger_idx + 1]
        # Phần cần scan (từ ngay sau header trở đi)
        scan_content = lines[last_trigger_idx + 1 :]
        skip_count = 0
        final_part_idx = 0
        found_code = False
        for i, line in enumerate(scan_content):
            stripped = line.strip()
            # Logic: Nếu gặp dòng trống hoặc chỉ có dấu # thì coi là rác
            if stripped == '' or stripped == '#':
                skip_count += 1
                continue
            else:
                # Đã va phải code hoặc comment xịn
                final_part_idx = i
                found_code = True
                break
        if found_code:
            new_content.extend(scan_content[final_part_idx:])
        if skip_count > 0:
            with open(filepath, 'w', encoding='utf-8') as f:
                f.writelines(new_content)
            print(f'[CLEANED] {filepath} - Removed {skip_count} junk lines.')
    except Exception as e:
        print(f'[ERROR] {filepath}: {e}')


def is_skipped_dir(dirname):
    """Kiểm tra xem tên thư mục có khớp với pattern nào trong SKIP list không"""
    for pattern in SKIP_DIR_NAMES:
        if fnmatch.fnmatch(dirname, pattern):
            return True
    return False


def main2():
    root_dir = '.'
    print(f'Scanning for {TARGET_EXT} files (Skipping: {SKIP_DIR_NAMES})...')
    # topdown=True là bắt buộc để có thể sửa đổi list 'dirs' in-place
    for root, dirs, files in os.walk(root_dir, topdown=True):
        # --- LOGIC PRUNING FOLDER ---
        # Sửa đổi list 'dirs' ngay lập tức để os.walk không đi vào các thư mục này
        # Dùng kỹ thuật list comprehension slice [:] để thay đổi chính object list đang duyệt
        dirs[:] = [d for d in dirs if not is_skipped_dir(d)]
        for file in files:
            if file.endswith(TARGET_EXT):
                if file == os.path.basename(__file__):
                    continue
                full_path = os.path.join(root, file)
                clean_file(full_path)


if __name__ == '__main__':
    main()
    main2()
