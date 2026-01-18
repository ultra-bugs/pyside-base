#              M""""""""`M            dP
#              Mmmmmm   .M            88
#              MMMMP  .MMM  dP    dP  88  .dP   .d8888b.
#              MMP  .MMMMM  88    88  88888"    88'  `88
#              M' .MMMMMMM  88.  .88  88  `8b.  88.  .88
#              M         M  `88888P'  dP   `YP  `88888P'
#              MMMMMMMMMMM    -*-  Created by Zuko  -*-
#
#              * * * * * * * * * * * * * * * * * * * * *
#              * -    - -   F.R.E.E.M.I.N.D   - -    - *
#              * -  Copyright © 2025 (Z) Programing  - *
#              *    -  -  All Rights Reserved  -  -    *
#              * * * * * * * * * * * * * * * * * * * * *
import os
import re
import sys
from pathlib import Path

# Define what to exclude
EXCLUDES = [
    'venv',
    '.venv',
    '.pixi',
    '__pycache__',
    '.git',
    'node_modules',
    'vendor',
    'build',
    'dist',
    'tests',
    'tests_core',
    # "core",
    'assets',
    '.run',
    '.vscode',
    '.idea',
    '.ruff_cache',
    'data',
    'packages',
]

# Regex pattern to match snake_case after task_manager. or taskManager.
# PATTERN = re.compile(r'\b(task_?manager\.)([a-z_]+_[a-z0-9_]+)\b')
PATTERN = re.compile(r'(?<!\w)(task_?manager|taskManager)\.([a-z_]+_[a-z0-9_]+)\b')


def to_camel_case(snake_str):
    parts = snake_str.split('_')
    return parts[0] + ''.join(word.capitalize() for word in parts[1:])


def should_exclude(path):
    return any(part in EXCLUDES for part in path.split(os.sep))


def process_file(filepath):
    with open(filepath, 'r', encoding='utf-8') as f:
        lines = f.readlines()
    replacements = []
    for idx, line in enumerate(lines, 1):
        for match in re.finditer(PATTERN, line):
            full_match = match.group(0)  # taskManager.runTask
            prefix = match.group(1)  # taskManager or task_manager
            snake = match.group(2)  # run_task
            camel = to_camel_case(snake)
            replacement = f'{prefix}.{camel}'  # taskManager.runTask
            print(f'\nFile: {filepath}')
            print(f'Line {idx}:')
            print(f'Before: {line.strip()}')
            print(f'Would replace: {full_match} → {replacement}')
            confirm = input('Apply change? [Y/n]: ').strip().lower()
            if confirm != 'n':
                new_line = line.replace(full_match, replacement)
                lines[idx - 1] = new_line  # update line
                print(f'After: {new_line.strip()}')
                replacements.append((full_match, replacement))
            else:
                print('Skipped.')
    if replacements:
        with open(filepath, 'w', encoding='utf-8') as f:
            f.writelines(lines)


def walk_and_process(base_dir='.'):
    for root, dirs, files in os.walk(base_dir):
        print(f'Processing directory: {root}')
        # Modify dirs in-place to skip EXCLUDES
        dirs[:] = [d for d in dirs if d not in EXCLUDES]
        for file in files:
            if should_exclude(os.path.join(root, file)):
                continue
            if file.endswith('.bak.bak'):
                print('removing', file)
                os.remove(os.path.join(root, file))
                continue
            if not file.endswith(('.bak', '.log', '.txt')):
                print('running file', file)
                process_file(os.path.join(root, file))


if __name__ == '__main__':
    project_root = Path(__file__).parent.parent
    sys.path.append(str(project_root))
    walk_and_process(project_root)
