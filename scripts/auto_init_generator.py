"""
Interactive auto generate __init__.py tool
"""

import ast
import os
import sys
from pathlib import Path
from typing import Dict, List, Set


class InitGenerator:
    def __init__(self, root_dir: str):
        self.root_dir = Path(root_dir)

    def extract_symbols(self, file_path: Path) -> Dict[str, Set[str]]:
        """Extract classes, functions and variables from Python file (module level only)"""
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
            tree = ast.parse(content)
            symbols = {'classes': set(), 'functions': set(), 'variables': set()}
            # Only get module-level definitions (not nested in classes/functions)
            for node in tree.body:
                if isinstance(node, ast.ClassDef):
                    if not node.name.startswith('_'):  # Skip private classes
                        symbols['classes'].add(node.name)
                elif isinstance(node, ast.FunctionDef):
                    if not node.name.startswith('_'):  # Skip private functions
                        symbols['functions'].add(node.name)
                elif isinstance(node, ast.Assign):
                    for target in node.targets:
                        if isinstance(target, ast.Name) and not target.id.startswith('_'):
                            symbols['variables'].add(target.id)
            return symbols
        except Exception as e:
            print(f'Error parsing {file_path}: {e}')
            return {'classes': set(), 'functions': set(), 'variables': set()}

    def find_python_files(self, directory: Path) -> List[Path]:
        """Find all Python files in directory (excluding __init__.py and .backup files)"""
        python_files = []
        for item in directory.iterdir():
            if item.is_file() and item.suffix == '.py':
                if item.name != '__init__.py' and not item.name.endswith('.backup'):
                    python_files.append(item)
        return python_files

    def find_subdirectories(self, directory: Path) -> List[Path]:
        """Find all subdirectories that contain Python files"""
        subdirs = []
        for item in directory.iterdir():
            if item.is_dir() and not item.name.startswith('.'):
                # Check if subdirectory has Python files or __init__.py
                if any(f.suffix == '.py' for f in item.iterdir() if f.is_file()):
                    subdirs.append(item)
        return subdirs

    def collect_submodule_exports_recursive(self, directory: Path, visited: Set[Path] = None) -> Set[str]:
        """Recursively collect all exports from submodules including nested ones"""
        if visited is None:
            visited = set()
        if directory in visited:
            return set()
        visited.add(directory)
        exports = set()
        # Get exports from __init__.py if it exists
        init_file = directory / '__init__.py'
        if init_file.exists():
            try:
                with open(init_file, 'r', encoding='utf-8') as f:
                    content = f.read()
                tree = ast.parse(content)
                for node in tree.body:
                    if isinstance(node, ast.Assign):
                        for target in node.targets:
                            if isinstance(target, ast.Name) and target.id == '__all__' and isinstance(node.value, (ast.List, ast.Tuple)):
                                for item in node.value.elts:
                                    if isinstance(item, ast.Constant):
                                        exports.add(item.value)
            except Exception as e:
                print(f'Warning: Could not parse {init_file}: {e}')
        # If no __all__ found in __init__.py, collect from Python files
        if not exports:
            python_files = self.find_python_files(directory)
            for file_path in python_files:
                symbols = self.extract_symbols(file_path)
                exports.update(symbols['classes'] | symbols['functions'] | symbols['variables'])
        # Recursively collect from subdirectories
        subdirs = self.find_subdirectories(directory)
        for subdir in subdirs:
            subdir_exports = self.collect_submodule_exports_recursive(subdir, visited.copy())
            exports.update(subdir_exports)
        return exports

    def get_import_path_for_symbol(self, symbol: str, start_dir: Path, root_dir: Path) -> str:
        """Find the correct import path for a symbol by searching recursively"""
        for root, dirs, files in os.walk(start_dir):
            root_path = Path(root)
            dirs[:] = [d for d in dirs if not d.startswith('.')]
            # Check Python files in current directory
            python_files = [f for f in files if f.endswith('.py') and f != '__init__.py' and not f.endswith('.backup')]
            for py_file in python_files:
                file_path = root_path / py_file
                symbols = self.extract_symbols(file_path)
                all_symbols = symbols['classes'] | symbols['functions'] | symbols['variables']
                if symbol in all_symbols:
                    # Build relative import path
                    rel_path = root_path.relative_to(root_dir)
                    module_name = Path(py_file).stem
                    if rel_path == Path('.'):
                        return f'.{module_name}'
                    else:
                        return f'.{rel_path.as_posix().replace("/", ".")}.{module_name}'
            # Check __init__.py files
            init_file = root_path / '__init__.py'
            if init_file.exists():
                try:
                    with open(init_file, 'r', encoding='utf-8') as f:
                        content = f.read()
                    tree = ast.parse(content)
                    for node in tree.body:
                        if isinstance(node, ast.Assign):
                            for target in node.targets:
                                if isinstance(target, ast.Name) and target.id == '__all__' and isinstance(node.value, (ast.List, ast.Tuple)):
                                    for item in node.value.elts:
                                        if isinstance(item, ast.Constant) and item.value == symbol:
                                            rel_path = root_path.relative_to(root_dir)
                                            if rel_path == Path('.'):
                                                return '.'
                                            else:
                                                return f'.{rel_path.as_posix().replace("/", ".")}'
                except Exception:
                    pass
        return None

    def generate_init_content(self, directory: Path, is_root: bool = False, skip_exports: bool = False) -> str:
        """Generate __init__.py content for a directory"""
        # Base header
        content_lines = ['"""', 'Generated by Z-Auto Init Generator | Zuko', '"""']
        # If we only want empty init files (just to make it a package), return early
        if skip_exports:
            return '\n'.join(content_lines) + '\n'
        imports = []
        all_exports = []
        # Import from Python files in current directory
        python_files = self.find_python_files(directory)
        for file_path in sorted(python_files):
            module_name = file_path.stem
            symbols = self.extract_symbols(file_path)
            all_symbols = symbols['classes'] | symbols['functions'] | symbols['variables']
            if all_symbols:
                symbol_list = sorted(list(all_symbols))
                imports.append(f'from .{module_name} import {", ".join(symbol_list)}')
                all_exports.extend(symbol_list)
        # Import from subdirectories
        subdirs = self.find_subdirectories(directory)
        for subdir in sorted(subdirs):
            subdir_name = subdir.name
            if is_root:
                # For root directory, collect ALL symbols from subdirectories recursively
                subdir_exports = self.collect_submodule_exports_recursive(subdir)
                if subdir_exports:
                    # Group imports by their source module
                    import_groups = {}
                    for symbol in sorted(subdir_exports):
                        import_path = self.get_import_path_for_symbol(symbol, subdir, self.root_dir)
                        if import_path:
                            if import_path not in import_groups:
                                import_groups[import_path] = []
                            import_groups[import_path].append(symbol)
                    # Add imports for each group
                    for import_path, symbols in sorted(import_groups.items()):
                        if symbols:
                            imports.append(f'from {import_path} import {", ".join(sorted(symbols))}')
                            all_exports.extend(symbols)
                # Also import the package itself
                imports.append(f'from . import {subdir_name}')
                all_exports.append(subdir_name)
            else:
                # For non-root directories, just import the package
                subdir_init = subdir / '__init__.py'
                if subdir_init.exists():
                    imports.append(f'from . import {subdir_name}')
                    all_exports.append(subdir_name)
        # Generate content
        if imports:
            content_lines.extend(imports)
            content_lines.append('')
        if all_exports:
            # Remove duplicates and sort
            unique_exports = sorted(set(all_exports))
            # Format __all__ list
            if len(unique_exports) <= 3:
                all_line = f'__all__ = {unique_exports}'
            else:
                all_line = '__all__ = [\n'
                for export in unique_exports:
                    all_line += f"    '{export}',\n"
                all_line += ']'
            content_lines.append(all_line)
        return '\n'.join(content_lines) + '\n' if content_lines else ''

    def generate_all_inits(self, skip_exports: bool = False):
        """Generate __init__.py files for all directories"""
        directories_processed = []
        # Walk through all directories
        for root, dirs, files in os.walk(self.root_dir):
            root_path = Path(root)
            # Skip hidden directories
            dirs[:] = [d for d in dirs if not d.startswith('.')]
            # Check if directory contains Python files or subdirectories with Python files
            has_python_files = any(f.endswith('.py') and f != '__init__.py' and not f.endswith('.backup') for f in files)
            has_python_subdirs = any((root_path / d).is_dir() and any(f.suffix == '.py' for f in (root_path / d).iterdir() if f.is_file()) for d in dirs)
            if has_python_files or has_python_subdirs:
                init_path = root_path / '__init__.py'
                is_root = root_path == self.root_dir
                # Pass the skip_exports flag
                content = self.generate_init_content(root_path, is_root=is_root, skip_exports=skip_exports)
                if content.strip():  # Only write if there's actual content
                    with open(init_path, 'w', encoding='utf-8') as f:
                        f.write(content)
                    directories_processed.append(str(root_path.relative_to(self.root_dir)))
                    print(f'Generated: {init_path}')
        print(f'\nProcessed {len(directories_processed)} directories:')
        for dir_path in directories_processed:
            print(f'  - {dir_path if dir_path else "root"}')

    def generate_root_only(self):
        """Generate only the root __init__.py with all submodule exports"""
        init_path = self.root_dir / '__init__.py'
        content = self.generate_init_content(self.root_dir, is_root=True)
        if content.strip():
            with open(init_path, 'w', encoding='utf-8') as f:
                f.write(content)
            print(f'Generated root: {init_path}')
        else:
            print('No content to generate for root __init__.py')


def main():
    if len(sys.argv) != 2:
        print('Usage: python generate_init.py <root_directory>')
        print('Example: python generate_init.py ./task')
        sys.exit(1)
    root_dir = sys.argv[1]
    if not os.path.exists(root_dir):
        print(f"Error: Directory '{root_dir}' does not exist")
        sys.exit(1)
    generator = InitGenerator(root_dir)
    # Ask user what they want to do
    print('Choose an option:')
    print('1. Generate all __init__.py files (recursive, with exports)')
    print('2. Generate only root __init__.py with all exports')
    print('3. Generate empty __init__.py files (recursive, no exports)')
    choice = input('Enter choice (1, 2 or 3): ').strip()
    if choice == '2':
        generator.generate_root_only()
    elif choice == '3':
        generator.generate_all_inits(skip_exports=True)
    else:
        generator.generate_all_inits()
    print('\nDone!')


if __name__ == '__main__':
    main()
