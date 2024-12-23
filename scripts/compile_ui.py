#!/usr/bin/env python3

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
#              * -  Copyright © 2024 (Z) Programing  - *
#              *    -  -  All Rights Reserved  -  -    *
#              * * * * * * * * * * * * * * * * * * * * *

import glob
import os


def compile_ui_file(ui_file):
    """Compile a .ui file to Python code"""
    py_file = ui_file.replace('.ui', '.py')
    os.system(f'pyside6-uic {ui_file} -o {py_file}')
    print(f'Compiled {ui_file} -> {py_file}')


def compile_qrc_file(qrc_file):
    """Compile a .qrc file to Python code"""
    py_file = qrc_file.replace('.qrc', '_rc.py')
    os.system(f'pyside6-rcc {qrc_file} -o {py_file}')
    print(f'Compiled {qrc_file} -> {py_file}')


def find_files(pattern):
    """Find all files matching pattern"""
    base_path = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    return glob.glob(os.path.join(base_path, '**', pattern), recursive=True)


def main():
    # Compile UI files
    ui_files = find_files('*.ui')
    for ui_file in ui_files:
        compile_ui_file(ui_file)
    
    # Compile QRC files
    qrc_files = find_files('*.qrc')
    for qrc_file in qrc_files:
        compile_qrc_file(qrc_file)


if __name__ == '__main__':
    main()
