#!/usr/bin/env python
"""
Wrapper script to run pytest with pyreadline fix for Windows.

This script should be run from the project root, not from scripts/ directory.

Usage:
    python scripts/run_pytest.py [pytest arguments]

Example:
    python scripts/run_pytest.py tests_core/task_system/
    python scripts/run_pytest.py --version
    python scripts/run_pytest.py tests_core/task_system/ -v --cov=core.taskSystem
"""

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
import collections.abc
import os
import sys
from pathlib import Path

# Fix pyreadline compatibility issue on Windows with Python 3.10+
if not hasattr(collections, 'Callable'):
    collections.Callable = collections.abc.Callable

# Ensure we're running from project root
script_dir = Path(__file__).parent
project_root = script_dir.parent

# Change to project root if we're in scripts directory
if os.getcwd() != str(project_root):
    os.chdir(project_root)
    print(f'Changed working directory to: {project_root}')

# Add project root to Python path
if str(project_root) not in sys.path:
    sys.path.insert(0, str(project_root))


def run_test(iniPath=None, args=None):
    # Now import and run pytest
    import pytest
    if args is None:
        args = sys.argv[1:]
    if iniPath is None:
        iniPath = project_root / 'tests' / 'pytest.ini'
    if iniPath.exists() and '-c' not in args:
        args.extend(['-c', str(iniPath)])
    return sys.exit(pytest.main(args))


if __name__ == '__main__':
    # Default to tests/pytest.ini if it exists and no config is specified
    run_test()
