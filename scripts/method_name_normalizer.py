"""
Enhanced Method Name Normalizer Script
Chuẩn hóa toàn bộ tên method, parameter, variable thành camelCase cho các file Python
"""

import os
import ast
import pathlib
import re
import logging
import keyword
import sys
from pathlib import Path
from typing import List, Tuple

logging.basicConfig(
    level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s', handlers=[logging.FileHandler('method_normalizer.log', encoding='utf-8'), logging.StreamHandler()]
)
logger = logging.getLogger(__name__)
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
    'assets',
    '.run',
    '.vscode',
    '.idea',
    '.ruff_cache',
    'data',
    'packages',
]
skipKeywords = ['PathHelperInternals.createPathObj(path)', *dir(pathlib)]


class EnhancedMethodNormalizer:
    def __init__(self):
        self.changesMade = 0
        self.filesProcessed = 0
        self.builtins = set(dir(__builtins__)) if isinstance(__builtins__, dict) else set(dir(__builtins__))
        self.pythonKeywords = set(keyword.kwlist)
        self.pythonKeywords.update(skipKeywords)

    @staticmethod
    def camelCaseConverter(name: str) -> str:
        """Chuyển đổi tên thành camelCase"""
        if not name:
            return name
        if re.match('^[a-z][a-zA-Z0-9]*$', name) or re.match('^[A-Z][a-zA-Z0-9]*$', name):
            return name
        components = name.split('_')
        if len(components) == 1:
            return name.lower()
        return components[0].lower() + ''.join((word.capitalize() for word in components[1:]))

    def shouldNormalize(self, name: str) -> bool:
        """Kiểm tra có nên chuẩn hóa tên này không"""
        if not name or name in self.pythonKeywords or name in self.builtins:
            return False
        if name.startswith('__') and name.endswith('__'):
            return False
        if name in ['self', 'cls']:
            return False
        if name.startswith('_'):
            return False
        return True

    def normalizeMethodNamesInCode_0(self, code: str) -> Tuple[str, int]:
        """Chuẩn hóa toàn bộ tên method, parameter, variable thành camelCase"""
        logger.debug('Bắt đầu chuẩn hóa toàn bộ tên')
        changesCount = 0
        try:
            tree = ast.parse(code)
            outerSelf = self
            class ComprehensiveNormalizer(ast.NodeTransformer):
                # add Input asking before making any change
                # show source -> dest
                # please note this method is reading source code. not filename/path
                def __init__(self):
                    self.changes = 0
                    self.nameMapping = {}
                    self.builtins = outerSelf.builtins
                    self.pythonKeywords = outerSelf.pythonKeywords
                def shouldNormalize(self, name: str) -> bool:
                    """Kiểm tra có nên chuẩn hóa tên này không"""
                    if not name or name in self.pythonKeywords or name in self.builtins:
                        return False
                    if name.startswith('__') and name.endswith('__'):
                        return False
                    if name in ['self', 'cls']:
                        return False
                    if name.startswith('_'):
                        return False
                    return True
                def normalizeName(self, oldName: str) -> str:
                    """Chuẩn hóa tên và lưu mapping"""
                    if not self.shouldNormalize(oldName):
                        return oldName
                    newName = EnhancedMethodNormalizer.camelCaseConverter(oldName)
                    if oldName != newName:
                        self.nameMapping[oldName] = newName
                        self.changes += 1
                        logger.debug(f'Mapping: {oldName} -> {newName}')
                    return newName
                def visitFunctiondef(self, node):
                    """Xử lý function definitions"""
                    oldName = node.name
                    node.name = self.normalizeName(node.name)
                    for arg in node.args.args:
                        arg.arg = self.normalizeName(arg.arg)
                    for arg in node.args.kwonlyargs:
                        arg.arg = self.normalizeName(arg.arg)
                    if node.args.vararg:
                        node.args.vararg.arg = self.normalizeName(node.args.vararg.arg)
                    if node.args.kwarg:
                        node.args.kwarg.arg = self.normalizeName(node.args.kwarg.arg)
                    return self.genericVisit(node)
                def visitAsyncfunctiondef(self, node):
                    """Xử lý async function definitions"""
                    return self.visitFunctiondef(node)
                def visitClassdef(self, node):
                    """Xử lý class definitions - chỉ chuẩn hóa nội dung, không đổi tên class"""
                    return self.genericVisit(node)
                def visitAssign(self, node):
                    """Xử lý variable assignments"""
                    for target in node.targets:
                        if isinstance(target, ast.Name):
                            target.id = self.normalizeName(target.id)
                        elif isinstance(target, ast.Tuple) or isinstance(target, ast.List):
                            for elt in target.elts:
                                if isinstance(elt, ast.Name):
                                    elt.id = self.normalizeName(elt.id)
                    return self.genericVisit(node)
                def visitAnnassign(self, node):
                    """Xử lý annotated assignments"""
                    if isinstance(node.target, ast.Name):
                        node.target.id = self.normalizeName(node.target.id)
                    return self.genericVisit(node)
                def visitName(self, node):
                    """Xử lý variable references"""
                    if isinstance(node.ctx, (ast.Load, ast.Store, ast.Del)):
                        node.id = self.normalizeName(node.id)
                    return self.genericVisit(node)
                def visitAttribute(self, node):
                    """Xử lý attribute access (object.method_name)"""
                    oldAttr = node.attr
                    node.attr = self.normalizeName(node.attr)
                    return self.genericVisit(node)
                def visitCall(self, node):
                    """Xử lý function calls"""
                    for keyword in node.keywords:
                        if keyword.arg:
                            keyword.arg = self.normalizeName(keyword.arg)
                    return self.genericVisit(node)
                def visitFor(self, node):
                    """Xử lý for loops"""
                    if isinstance(node.target, ast.Name):
                        node.target.id = self.normalizeName(node.target.id)
                    elif isinstance(node.target, (ast.Tuple, ast.List)):
                        for elt in node.target.elts:
                            if isinstance(elt, ast.Name):
                                elt.id = self.normalizeName(elt.id)
                    return self.genericVisit(node)
                def visitComprehension(self, node):
                    """Xử lý list/dict/set comprehensions"""
                    if isinstance(node.target, ast.Name):
                        node.target.id = self.normalizeName(node.target.id)
                    elif isinstance(node.target, (ast.Tuple, ast.List)):
                        for elt in node.target.elts:
                            if isinstance(elt, ast.Name):
                                elt.id = self.normalizeName(elt.id)
                    return self.genericVisit(node)
                def visitExcepthandler(self, node):
                    """Xử lý exception handlers"""
                    if node.name:
                        node.name = self.normalizeName(node.name)
                    return self.genericVisit(node)
                def visitWith(self, node):
                    """Xử lý with statements"""
                    for item in node.items:
                        if item.optionalVars:
                            if isinstance(item.optionalVars, ast.Name):
                                item.optionalVars.id = self.normalizeName(item.optionalVars.id)
                            elif isinstance(item.optionalVars, (ast.Tuple, ast.List)):
                                for elt in item.optionalVars.elts:
                                    if isinstance(elt, ast.Name):
                                        elt.id = self.normalizeName(elt.id)
                    return self.genericVisit(node)
                def visitAsyncwith(self, node):
                    """Xử lý async with statements"""
                    return self.visitWith(node)
                def visitGlobal(self, node):
                    """Xử lý global statements"""
                    node.names = [self.normalizeName(name) for name in node.names]
                    return self.genericVisit(node)
                def visitNonlocal(self, node):
                    """Xử lý nonlocal statements"""
                    node.names = [self.normalizeName(name) for name in node.names]
                    return self.genericVisit(node)
            normalizer = ComprehensiveNormalizer()
            newTree = normalizer.visit(tree)
            changesCount = normalizer.changes
            try:
                import astor
                normalizedCode = astor.toSource(newTree)
                logger.debug('Sử dụng astor để chuyển đổi')
            except ImportError:
                try:
                    normalizedCode = ast.unparse(newTree)
                    logger.debug('Sử dụng ast.unparse để chuyển đổi')
                except AttributeError:
                    logger.warning('Không có astor và Python < 3.9, không thể chuyển đổi AST')
                    return (code, 0)
            logger.debug(f'Hoàn thành chuẩn hóa, thực hiện {changesCount} thay đổi')
            return (normalizedCode, changesCount)
        except Exception as e:
            logger.warning(f'Không thể chuẩn hóa code: {e}. Sử dụng code gốc.')
            return (code, 0)

    def normalizeMethodNamesInCode(self, code: str, file_context: str = 'Unknown File') -> Tuple[str, int]:
        """
        Normalizes method, parameter, and variable names to camelCase with user interaction.
        """
        logger.debug(f'Starting normalization for: {file_context}')
        try:
            tree = ast.parse(code)
            outer_self = self
            class InteractiveNormalizer(ast.NodeTransformer):
                def __init__(self):
                    self.changes = 0
                    self.name_mapping = {}  # Cache accepted renames
                    self.ignore_set = set()  # Cache rejected renames
                    self.auto_accept = False  # Toggle for 'all'
                    self.builtins = outer_self.builtins
                    self.keywords = outer_self.pythonKeywords
                def _get_user_decision(self, old: str, new: str) -> bool:
                    """Handles user input for renaming."""
                    if self.auto_accept:
                        return True
                    print(f'\n[{file_context}] Match found:')
                    print(f'  Source: \033[91m{old}\033[0m')  # Red
                    print(f'  Dest:   \033[92m{new}\033[0m')  # Green
                    while True:
                        choice = input('  Apply change? [y]es, [n]o, [a]ll, [q]uit: ').lower().strip()
                        if choice == 'y':
                            return True
                        elif choice == 'n':
                            return False
                        elif choice == 'a':
                            self.auto_accept = True
                            print('  >> Auto-accepting remaining changes in this file.')
                            return True
                        elif choice == 'q':
                            raise KeyboardInterrupt('User aborted processing.')
                def should_normalize(self, name: str) -> bool:
                    if not name or name in self.keywords or name in self.builtins:
                        return False
                    if name.startswith('__') and name.endswith('__'):
                        return False
                    if name in ['self', 'cls', '_']:
                        return False
                    if name.startswith('_'):
                        return False
                    return True
                def normalize_name(self, old_name: str) -> str:
                    if not self.should_normalize(old_name):
                        return old_name
                    # Check caches first
                    if old_name in self.name_mapping:
                        return self.name_mapping[old_name]
                    if old_name in self.ignore_set:
                        return old_name
                    new_name = EnhancedMethodNormalizer.camelCaseConverter(old_name)
                    if old_name == new_name:
                        return old_name
                    # Ask user
                    if self._get_user_decision(old_name, new_name):
                        self.name_mapping[old_name] = new_name
                        self.changes += 1
                        logger.debug(f'Accepted: {old_name} -> {new_name}')
                        return new_name
                    else:
                        self.ignore_set.add(old_name)
                        logger.debug(f'Ignored: {old_name}')
                        return old_name
                # --- Visitor Methods ---
                def visit_FunctionDef(self, node):
                    node.name = self.normalize_name(node.name)
                    for arg in node.args.args:
                        arg.arg = self.normalize_name(arg.arg)
                    for arg in node.args.kwonlyargs:
                        arg.arg = self.normalize_name(arg.arg)
                    if node.args.vararg:
                        node.args.vararg.arg = self.normalize_name(node.args.vararg.arg)
                    if node.args.kwarg:
                        node.args.kwarg.arg = self.normalize_name(node.args.kwarg.arg)
                    return self.generic_visit(node)
                def visit_AsyncFunctionDef(self, node):
                    return self.visit_FunctionDef(node)
                def visit_ClassDef(self, node):
                    # Only visit body, do not rename Class itself
                    return self.generic_visit(node)
                def visit_Assign(self, node):
                    for target in node.targets:
                        if isinstance(target, ast.Name):
                            target.id = self.normalize_name(target.id)
                        elif isinstance(target, (ast.Tuple, ast.List)):
                            for elt in target.elts:
                                if isinstance(elt, ast.Name):
                                    elt.id = self.normalize_name(elt.id)
                    return self.generic_visit(node)
                def visit_AnnAssign(self, node):
                    if isinstance(node.target, ast.Name):
                        node.target.id = self.normalize_name(node.target.id)
                    return self.generic_visit(node)
                def visit_Name(self, node):
                    if isinstance(node.ctx, (ast.Load, ast.Store, ast.Del)):
                        node.id = self.normalize_name(node.id)
                    return self.generic_visit(node)
                def visit_Attribute(self, node):
                    # Careful with attributes: obj.method() -> attr is 'method'
                    node.attr = self.normalize_name(node.attr)
                    return self.generic_visit(node)
                def visit_Call(self, node):
                    for keyword in node.keywords:
                        if keyword.arg:
                            keyword.arg = self.normalize_name(keyword.arg)
                    return self.generic_visit(node)
                def visit_For(self, node):
                    if isinstance(node.target, ast.Name):
                        node.target.id = self.normalize_name(node.target.id)
                    elif isinstance(node.target, (ast.Tuple, ast.List)):
                        for elt in node.target.elts:
                            if isinstance(elt, ast.Name):
                                elt.id = self.normalize_name(elt.id)
                    return self.generic_visit(node)
                def visit_ExceptHandler(self, node):
                    if node.name:
                        node.name = self.normalize_name(node.name)
                    return self.generic_visit(node)
                def visit_With(self, node):
                    for item in node.items:
                        if item.optional_vars:
                            if isinstance(item.optional_vars, ast.Name):
                                item.optional_vars.id = self.normalize_name(item.optional_vars.id)
                            elif isinstance(item.optional_vars, (ast.Tuple, ast.List)):
                                for elt in item.optional_vars.elts:
                                    if isinstance(elt, ast.Name):
                                        elt.id = self.normalize_name(elt.id)
                    return self.generic_visit(node)
                def visit_AsyncWith(self, node):
                    return self.visit_With(node)
                def visit_Global(self, node):
                    node.names = [self.normalize_name(n) for n in node.names]
                    return self.generic_visit(node)
                def visit_Nonlocal(self, node):
                    node.names = [self.normalize_name(n) for n in node.names]
                    return self.generic_visit(node)
                def visit_Comprehension(self, node):
                    if isinstance(node.target, ast.Name):
                        node.target.id = self.normalize_name(node.target.id)
                    elif isinstance(node.target, (ast.Tuple, ast.List)):
                        for elt in node.target.elts:
                            if isinstance(elt, ast.Name):
                                elt.id = self.normalize_name(elt.id)
                    return self.generic_visit(node)
            normalizer = InteractiveNormalizer()
            new_tree = normalizer.visit(tree)
            changes_count = normalizer.changes
            if changes_count == 0:
                return (code, 0)
            # Code Generation
            try:
                import astor
                normalized_code = astor.to_source(new_tree)
            except ImportError:
                if sys.version_info >= (3, 9):
                    normalized_code = ast.unparse(new_tree)
                else:
                    logger.warning('astor missing and python < 3.9')
                    return (code, 0)
            return (normalized_code, changes_count)
        except KeyboardInterrupt:
            print('\nOperation cancelled by user.')
            sys.exit(0)
        except Exception as e:
            logger.warning(f'Failed to normalize code: {e}')
            return (code, 0)

    def getPythonFiles(self, directory: str) -> List[str]:
        """Lấy danh sách file Python trong thư mục (đệ quy)"""
        logger.info(f'Quét thư mục đệ quy: {directory}')
        pythonFiles = []
        for root, dirs, files in os.walk(directory):
            dirs[:] = [d for d in dirs if d not in EXCLUDES]
            for file in files:
                if file.endswith('.py'):
                    fullPath = os.path.join(root, file)
                    pythonFiles.append(fullPath)
                    logger.debug(f'Tìm thấy file: {fullPath}')
        logger.info(f'Tìm thấy {len(pythonFiles)} file Python')
        return pythonFiles

    def normalizeFile(self, filePath: str) -> bool:
        """Chuẩn hóa một file Python"""
        logger.info(f'Xử lý file: {filePath}')
        try:
            with open(filePath, 'r', encoding='utf-8') as f:
                originalCode = f.read()
            # normalizedCode, changes = self.normalizeMethodNamesInCode(originalCode)
            normalizedCode, changes = self.normalizeMethodNamesInCode(originalCode, file_context=os.path.basename(filePath))
            if changes > 0:
                backupPath = f'{filePath}.backup'
                with open(backupPath, 'w', encoding='utf-8') as f:
                    f.write(originalCode)
                logger.info(f'Tạo backup: {backupPath}')
                with open(filePath, 'w', encoding='utf-8') as f:
                    f.write(normalizedCode)
                logger.info(f'Đã chuẩn hóa {changes} tên trong file: {filePath}')
                self.changesMade += changes
                return True
            else:
                logger.info(f'Không có thay đổi nào trong file: {filePath}')
                return False
        except Exception as e:
            logger.error(f'Lỗi khi xử lý file {filePath}: {e}')
            return False

    def normalizeDirectory(self, directory: str, filePattern: str = '*.py'):
        """Chuẩn hóa tất cả file Python trong thư mục"""
        logger.info(f'==== Bắt đầu chuẩn hóa toàn bộ thư mục: {directory} ====')
        if not os.path.exists(directory):
            logger.error(f'Thư mục không tồn tại: {directory}')
            return
        pythonFiles = self.getPythonFiles(directory)
        if not pythonFiles:
            logger.warning('Không tìm thấy file Python nào!')
            return
        print(f'\nTìm thấy {len(pythonFiles)} file Python trong thư mục:')
        for i, filePath in enumerate(pythonFiles):
            print(f'  {i}. {filePath}')
        print('\n⚠️  CẢNH BÁO: Script sẽ đổi TOÀN BỘ tên variables, methods, parameters thành camelCase')
        print('   Điều này có thể gây lỗi syntax nếu có conflicts với external libraries')
        confirm = input(f'\nBạn có muốn chuẩn hóa toàn bộ {len(pythonFiles)} file? (y/N): ').strip().lower()
        if confirm != 'y':
            logger.info('Người dùng hủy thao tác')
            return
        processedFiles = 0
        failedFiles = 0
        for filePath in pythonFiles:
            try:
                success = self.normalizeFile(filePath)
                if success:
                    processedFiles += 1
                self.filesProcessed += 1
            except Exception as e:
                logger.error(f'Lỗi khi xử lý file {filePath}: {e}')
                failedFiles += 1
        logger.info('==== Hoàn thành chuẩn hóa thư mục ====')
        logger.info(f'Tổng file đã xử lý: {self.filesProcessed}')
        logger.info(f'File có thay đổi: {processedFiles}')
        logger.info(f'File lỗi: {failedFiles}')
        logger.info(f'Tổng số thay đổi: {self.changesMade}')
        print('\n=== Kết quả ===')
        print(f'Tổng file đã xử lý: {self.filesProcessed}')
        print(f'File có thay đổi: {processedFiles}')
        print(f'File lỗi: {failedFiles}')
        print(f'Tổng số thay đổi: {self.changesMade}')
        print('Log chi tiết: method_normalizer.log')
        print('Backup files: *.py.backup')

    def run(self):
        """Chạy script chính"""
        print('=== Enhanced Method Name Normalizer ===')
        print('Script chuẩn hóa TOÀN BỘ tên method, parameter, variable thành camelCase')
        print('Lưu ý: Script sẽ tạo backup cho các file bị thay đổi')
        print('⚠️  CẢNH BÁO: Có thể gây conflicts với external libraries!')
        targetDir = input('\nNhập đường dẫn thư mục cần chuẩn hóa: ').strip()
        if not targetDir:
            print('Đường dẫn không được để trống!')
            return
        if not os.path.exists(targetDir):
            print(f'Thư mục không tồn tại: {targetDir}')
            return
        try:
            self.normalizeDirectory(targetDir)
        except KeyboardInterrupt:
            print('\nĐã hủy bởi người dùng')
            logger.info('Script bị hủy bởi người dùng')
        except Exception as e:
            print(f'Lỗi không mong muốn: {e}')
            logger.error(f'Lỗi không mong muốn: {e}')


def main():
    """Hàm main"""
    try:
        normalizer = EnhancedMethodNormalizer()
        normalizer.run()
    except KeyboardInterrupt:
        print('\nĐã hủy bởi người dùng')
    except Exception as e:
        print(f'Lỗi không mong muốn: {e}')
        logging.error(f'Lỗi không mong muốn: {e}')


if __name__ == '__main__':
    projectRoot = Path(__file__).parent.parent
    sys.path.append(str(projectRoot))
    main()
