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

import ast
import ctypes
import fnmatch
import os
import subprocess
from pathlib import Path

# ================= CONFIGURATION =================
# Needle keywords (Không cần quan tâm khoảng trắng, script sẽ tự loại bỏ khi scan)
NEEDLE_KEYWORD = 'MMMMMMMMMMM-*-CreatedbyZuko-*-'
COMMENT_KEYWORD = '#'  # Đặt thành biến để dễ tái sử dụng cho ngôn ngữ khác (VD: '//')
TARGET_EXT = '.py'

# Hỗ trợ wildcard standard: '*' (mọi ký tự), '?' (1 ký tự), '[seq]'
SKIP_DIR_NAMES = ['.*', 'data', 'assets', 'nghien_cuu_i9', '.pixi', '.env', '.cache']
# =================================================


def enable_win_vt100():
    if os.name != 'nt':
        return
    # Lấy handle của STDOUT (-11)
    kernel32 = ctypes.windll.kernel32
    handle = kernel32.GetStdHandle(-11)
    # Lấy Mode hiện tại
    mode = ctypes.c_ulong()
    kernel32.GetConsoleMode(handle, ctypes.byref(mode))
    # Set cờ ENABLE_VIRTUAL_TERMINAL_PROCESSING (0x0004)
    kernel32.SetConsoleMode(handle, mode.value | 0x0004)


enable_win_vt100()


def get_ruff_target_files():
    try:
        result = subprocess.check_output(['ruff', 'check', '--show-files'], text=True, stderr=subprocess.DEVNULL)
        return [f.strip() for f in result.splitlines() if f.strip().endswith(TARGET_EXT)]
    except (subprocess.CalledProcessError, FileNotFoundError) as e:
        print(f'Error: Could not invoke Ruff to get file list. {e}')
        return []


def remove_empty_lines_in_scope(file_path):
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
    function_ranges = []
    for node in ast.walk(tree):
        if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)):
            function_ranges.append((node.lineno, node.end_lineno))
    if not function_ranges:
        return
    optimized_lines = []
    for idx, line in enumerate(lines, start=1):
        is_inside_fn = any(start <= idx <= end for start, end in function_ranges)
        # --- Bắt Junk Lines ---
        stripped_nospace = ''.join(line.split())
        is_junk = set(stripped_nospace).issubset({COMMENT_KEYWORD})
        # Nếu nằm trong Function và là dòng rác (trống hoặc chỉ có #) -> Bỏ qua
        if is_inside_fn and is_junk:
            continue
        optimized_lines.append(line)
    if len(optimized_lines) != len(lines):
        with open(path, 'w', encoding='utf-8') as f:
            f.writelines(optimized_lines)
        print(f'\033[32m[AST CLEANED]\033[0m {file_path}')


def clean_file(filepath):
    try:
        with open(filepath, 'r', encoding='utf-8') as f:
            lines = f.readlines()
        # 1. Quét tìm tất cả các block bản quyền (bằng cách xoá sạch khoảng trắng để so sánh)
        needle_indices = []
        for i, line in enumerate(lines):
            stripped_nospace = ''.join(line.split())
            if stripped_nospace.startswith(COMMENT_KEYWORD) and NEEDLE_KEYWORD in stripped_nospace:
                needle_indices.append(i)
        if not needle_indices:
            return
        modified = False
        # --- Helper: Tìm biên Trên/Dưới của 1 block bản quyền để không ăn nhầm comment code ---
        def get_block_bounds(n_idx):
            start_idx = n_idx
            # Dò ngược lên trên tối đa 15 lines để tìm biên trên M""""""""`M
            for i in range(n_idx, max(-1, n_idx - 15), -1):
                s = ''.join(lines[i].split())
                if s.startswith(COMMENT_KEYWORD) and 'M""""""""`M' in s:
                    start_idx = i
                    break
            else:  # Fallback
                while start_idx > 0 and lines[start_idx - 1].lstrip().startswith(COMMENT_KEYWORD):
                    start_idx -= 1
            end_idx = n_idx
            borders_seen = 0
            # Dò xuống dưới tối đa 15 lines. Biên dưới chuẩn sẽ đi qua 2 lines chứa rất nhiều dấu *
            for i in range(n_idx, min(len(lines), n_idx + 15)):
                s = lines[i].strip()
                if s.startswith(COMMENT_KEYWORD) and s.count('*') > 10:
                    borders_seen += 1
                    end_idx = i
                    if borders_seen == 2:  # Border chốt sổ dưới cùng
                        break
            else:  # Fallback
                while end_idx < len(lines) - 1 and lines[end_idx + 1].lstrip().startswith(COMMENT_KEYWORD):
                    end_idx += 1
            return start_idx, end_idx
        # 2. Xử lý Remove Duplicate Blocks (Xoá từ dưới lên để không làm lệch Index)
        if len(needle_indices) > 1:
            for idx in reversed(needle_indices[1:]):
                start_idx, end_idx = get_block_bounds(idx)
                del lines[start_idx : end_idx + 1]
                modified = True
                print(f'\033[33m[DUPLICATE CLEANED]\033[0m {filepath} - Removed duplicate block (lines {start_idx + 1}-{end_idx + 1}).')
        # 3. Clean Junk Lines (chỉ áp dụng sát đít Primary Block đầu tiên)
        first_needle_idx = needle_indices[0]
        _, first_end_idx = get_block_bounds(first_needle_idx)
        new_content = lines[: first_end_idx + 1]
        scan_content = lines[first_end_idx + 1 :]
        skip_count = 0
        final_part_idx = 0
        found_code = False
        for i, line in enumerate(scan_content):
            # --- [MẠNH TAY] Bắt Junk Lines ---
            stripped_nospace = ''.join(line.split())
            is_junk = set(stripped_nospace).issubset({COMMENT_KEYWORD})
            if is_junk:
                skip_count += 1
            else:
                final_part_idx = i
                found_code = True
                break
        if found_code:
            new_content.extend(scan_content[final_part_idx:])
        if skip_count > 0:
            lines = new_content
            modified = True
            print(f'\033[32m[JUNK CLEANED]\033[0m {filepath} - Removed {skip_count} junk lines after header.')
        # 4. Ghi file nếu có bất kỳ sự thay đổi nào
        if modified:
            with open(filepath, 'w', encoding='utf-8') as f:
                f.writelines(lines)
    except Exception as e:
        print(f'[\033[32m[ERROR]\033[0m  {filepath}: {e}')


def is_skipped_dir(dirname):
    for pattern in SKIP_DIR_NAMES:
        if fnmatch.fnmatch(dirname, pattern):
            return True
    return False


def main2():
    root_dir = '.'
    print(f'-- Scanning for {TARGET_EXT} files (Skipping: {SKIP_DIR_NAMES})...')
    for root, dirs, files in os.walk(root_dir, topdown=True):
        dirs[:] = [d for d in dirs if not is_skipped_dir(d)]
        for file in files:
            if file.endswith(TARGET_EXT):
                if file == os.path.basename(__file__):
                    continue
                full_path = os.path.join(root, file)
                clean_file(full_path)


def main():
    enable_win_vt100()
    print('\n\nStep 1: Running Ruff Format...')
    subprocess.run(['ruff', 'format', '.'], check=False)
    print('\n\nStep 2: Syncing with Ruff file list...')
    target_files = get_ruff_target_files()
    if not target_files:
        print('No files to process via Ruff.')
    else:
        print(f'\n\nStep 3: Processing {len(target_files)} files (AST Empty lines scope)...')
        for file_path in target_files:
            remove_empty_lines_in_scope(file_path)
    print('\n\nStep 4: Running Copyright Header & Junk line cleaner...')
    main2()
    print('\n\nPipeline finished successfully.')


if __name__ == '__main__':
    main()
