import inspect
import json
import os
import pathlib
import platform
import stat
import subprocess
import sys
import traceback
from dataclasses import asdict, dataclass, is_dataclass
from enum import Enum, auto
from typing import Any, Callable, Dict, List, Optional, TypeVar, Union
from uuid import UUID
import curl_cffi
import numpy as np
import win32process
from PySide6.QtCore import QCoreApplication, QTimer, Qt
from PySide6.QtGui import QIcon
from PySide6.QtWidgets import QMessageBox
from box import Box

T = TypeVar('T')


class PathHelperInternals:
    """
    Internal utility methods for PathHelper.
    These methods directly use pathlib to avoid circular references.
    They should not be used outside of PathHelper.
    """

    @staticmethod
    def create_path_obj(path: Union[str, pathlib.Path]) -> pathlib.Path:
        """Create a pathlib.Path object from a path string or object."""
        return pathlib.Path(path)

    @staticmethod
    def getPathExists(path: Union[str, pathlib.Path]) -> bool:
        """Check if a path exists."""
        return PathHelperInternals.create_path_obj(path).exists()

    @staticmethod
    def getPathIsFile(path: Union[str, pathlib.Path]) -> bool:
        """Check if a path is a file."""
        return PathHelperInternals.create_path_obj(path).is_file()

    @staticmethod
    def getPathIsDir(path: Union[str, pathlib.Path]) -> bool:
        """Check if a path is a directory."""
        return PathHelperInternals.create_path_obj(path).is_dir()

    @staticmethod
    def getPathIsSymlink(path: Union[str, pathlib.Path]) -> bool:
        """Check if a path is a symlink."""
        return PathHelperInternals.create_path_obj(path).is_symlink()

    @staticmethod
    def get_path_name(path: Union[str, pathlib.Path]) -> str:
        """Get the name of a path."""
        return PathHelperInternals.create_path_obj(path).name

    @staticmethod
    def get_path_stem(path: Union[str, pathlib.Path]) -> str:
        """Get the stem (filename without extension) of a path."""
        return PathHelperInternals.create_path_obj(path).stem

    @staticmethod
    def get_path_parent(path: Union[str, pathlib.Path]) -> pathlib.Path:
        """Get the parent directory of a path."""
        return PathHelperInternals.create_path_obj(path).parent

    @staticmethod
    def get_path_resolve(path: Union[str, pathlib.Path]) -> pathlib.Path:
        """Get the resolved path."""
        return PathHelperInternals.create_path_obj(path).resolve()

    @staticmethod
    def get_cwd() -> pathlib.Path:
        """Get the current working directory."""
        return pathlib.Path.cwd().resolve()

    @staticmethod
    def get_executable_dir() -> pathlib.Path:
        """Get directory of the running executable/script."""
        if getattr(sys, 'frozen', False):
            return pathlib.Path(sys.executable).parent.resolve()
        else:
            return pathlib.Path(sys.argv[0]).parent.resolve()

    @staticmethod
    def join_path(base_path: Union[str, pathlib.Path], *paths: str) -> pathlib.Path:
        """Join paths."""
        return PathHelperInternals.create_path_obj(base_path).joinpath(*paths)

    @staticmethod
    def make_dirs(path: Union[str, pathlib.Path], parents: bool = True, exist_ok: bool = True) -> None:
        """Create directories."""
        PathHelperInternals.create_path_obj(path).mkdir(parents=parents, exist_ok=exist_ok)

    @staticmethod
    def glob_path(path: Union[str, pathlib.Path], pattern: str) -> List[pathlib.Path]:
        """Get paths matching a glob pattern."""
        return list(PathHelperInternals.create_path_obj(path).glob(pattern))

    @staticmethod
    def iter_dir(path: Union[str, pathlib.Path]) -> List[pathlib.Path]:
        """List directory contents."""
        return list(PathHelperInternals.create_path_obj(path).iterdir())


class PathHelper:
    """
    Utility class for handling file system paths in the application.
    Provides static methods to work with project paths, especially focusing on the data directory.
    """

    _actual_file_path: Optional[pathlib.Path] = None
    _root_dir: Optional[pathlib.Path] = None

    @staticmethod
    def readJsonFile(jsonPath: Union[str, os.PathLike]) -> Union[Dict[str, Box], List[Box], Box]:
        """
        Read a JSON file and return its content as a dictionary.
        Args:
            jsonPath: Path to the JSON file.
        Returns:
            Union[Dict[str, Any], List[Any]]: Content of the JSON file.
        """
        with open(jsonPath, 'r', encoding='utf-8') as f:
            import json
            j = json.load(f)
            if isinstance(j, list):
                return j
            return j

    @staticmethod
    def resolvePath(path: Union[str, os.PathLike]) -> Union[str, os.PathLike]:
        return PathHelperInternals.get_path_resolve(path)

    @staticmethod
    def _get_file_path() -> pathlib.Path:
        """
        Get the actual path of the current file.
        Returns:
            pathlib.Path: The resolved path of the current file.
        """
        if PathHelper._actual_file_path is None:
            PathHelper._actual_file_path = PathHelperInternals.get_path_resolve(pathlib.Path(__file__))
        return PathHelper._actual_file_path

    @staticmethod
    def _detect_symlink() -> bool:
        """
        Detect if the current file is a symlink by checking if its parent's
        absolute path is different from its expected location in the project.
        Returns:
            bool: True if symlink is detected, False otherwise.
        """
        actual_path = PathHelper._get_file_path()
        real_parent = PathHelperInternals.get_path_parent(actual_path)
        try:
            cwd = PathHelperInternals.get_cwd()
            expected_path = cwd
            potential_root_dirs: List[pathlib.Path] = []
            test_dir = cwd
            while len(test_dir.parts) > 1:
                vendor_path = PathHelperInternals.join_path(test_dir, 'vendor')
                data = PathHelperInternals.join_path(test_dir, 'data')
                if PathHelperInternals.getPathExists(vendor_path) or PathHelperInternals.getPathExists(data):
                    potential_root_dirs.append(test_dir)
                test_dir = PathHelperInternals.get_path_parent(test_dir)
            for root_dir in potential_root_dirs:
                core_dir = PathHelperInternals.join_path(root_dir, 'core')
                if PathHelperInternals.getPathExists(core_dir) and PathHelperInternals.getPathIsDir(core_dir):
                    expected_path = core_dir
                    break
            return real_parent != expected_path and 'core' in real_parent.parts
        except (PermissionError, OSError):
            return False

    @staticmethod
    def rootDir() -> pathlib.Path:
        """
        Get the absolute path to the project root directory.
        If running from a symlink, will try to determine the correct project root.
        Returns:
            pathlib.Path: The absolute path to the project root directory.
        """
        if PathHelper._root_dir is not None:
            return PathHelper._root_dir
        if getattr(sys, 'frozen', False):
            exe_dir = pathlib.Path(sys.executable).parent.resolve()
            PathHelper._root_dir = exe_dir
            return PathHelper._root_dir
        current_file = PathHelper._get_file_path()
        if PathHelper._detect_symlink():
            cwd = PathHelperInternals.get_cwd()
            test_dir = cwd
            while len(test_dir.parts) > 1:
                vendor_path = PathHelperInternals.join_path(test_dir, 'vendor')
                data_path = PathHelperInternals.join_path(test_dir, 'data')
                if PathHelperInternals.getPathExists(vendor_path) or PathHelperInternals.getPathExists(data_path):
                    PathHelper._root_dir = test_dir
                    return PathHelper._root_dir
                test_dir = PathHelperInternals.get_path_parent(test_dir)
        PathHelper._root_dir = PathHelperInternals.get_path_parent(PathHelperInternals.get_path_parent(current_file))
        return PathHelper._root_dir

    @staticmethod
    def relativePathFromAbs(absolute_path: Union[str, pathlib.Path], base_path: Optional[Union[str, pathlib.Path]] = None) -> str:
        """
        Get the relative path from a base path to an absolute path.
        Args:
            absolute_path: The absolute path to convert.
            base_path: The base path to calculate the relative path from.
        Returns:
            str: The relative path.
        """
        base_path = base_path or PathHelper.rootDir()
        path_obj = PathHelperInternals.create_path_obj(absolute_path)
        base_obj = PathHelperInternals.create_path_obj(base_path)
        relative = path_obj.relative_to(base_obj)
        if isinstance(relative, pathlib.WindowsPath):
            return relative.as_posix()
        return str(relative)

    @staticmethod
    def relativeModulePathFromAbs(absolute_path: Union[str, pathlib.Path], base_path: Optional[Union[str, pathlib.Path]] = None) -> str:
        """
        Get the relative module path from a base path to an absolute path.
        Args:
            absolute_path: The absolute path to convert.
            base_path: The base path to calculate the relative path from.
        Returns:
            str: The relative module path.
        """
        base_path = base_path or PathHelper.rootDir()
        relative = PathHelper.relativePathFromAbs(absolute_path, base_path)
        return relative.replace('/', '.').replace('\\', '.')

    @staticmethod
    def dataDir() -> pathlib.Path:
        """
        Get the absolute path to the data directory.
        Returns:
            pathlib.Path: The absolute path to the data directory.
        """
        root = PathHelper.rootDir()
        data_dir = PathHelperInternals.join_path(root, 'data')
        if not PathHelperInternals.getPathExists(data_dir) and PathHelperInternals.getPathExists(root):
            try:
                PathHelperInternals.make_dirs(data_dir)
            except (PermissionError, OSError):
                pass
        return data_dir

    @staticmethod
    def assetsDir() -> pathlib.Path:
        """
        Get the absolute path to the assets directory.
        Returns:
            pathlib.Path: The absolute path to the assets directory.
        """
        root = PathHelper.rootDir()
        assets_dir = PathHelperInternals.join_path(root, 'assets')
        if not PathHelperInternals.getPathExists(assets_dir) and PathHelperInternals.getPathExists(root):
            try:
                PathHelperInternals.make_dirs(assets_dir)
            except (PermissionError, OSError):
                pass
        return assets_dir

    @staticmethod
    def vendorDir() -> pathlib.Path:
        """
        Get the absolute path to the vendor directory.
        Returns:
            pathlib.Path: The absolute path to the vendor directory.
        """
        root = PathHelper.rootDir()
        vendor_dir = PathHelperInternals.join_path(root, 'vendor')
        if not PathHelperInternals.getPathExists(vendor_dir) and PathHelperInternals.getPathExists(root):
            try:
                PathHelperInternals.make_dirs(vendor_dir)
            except (PermissionError, OSError):
                pass
        return vendor_dir

    @staticmethod
    def joinPath(base_path: Union[str, pathlib.Path], *paths: str) -> pathlib.Path:
        """
        Join one or more path components to the base path.
        Args:
            base_path: The base path to join with.
            *paths: Additional path components to join.
        Returns:
            pathlib.Path: The joined path.
        """
        return PathHelperInternals.join_path(base_path, *paths)

    @staticmethod
    def ensureDirExists(path: Union[str, pathlib.Path]) -> pathlib.Path:
        """
        Ensure that a directory exists, creating it if necessary.
        Args:
            path: The directory path to check/create.
        Returns:
            pathlib.Path: The path that was checked/created.
        """
        path_obj = PathHelperInternals.create_path_obj(path)
        PathHelperInternals.make_dirs(path_obj)
        return path_obj

    @staticmethod
    def buildBasePath(*paths: str) -> pathlib.Path:
        """
        Build a base path by joining the root directory with additional paths.
        Works correctly with symlinked directories.
        Args:
            *paths: Additional path components to join.
        Returns:
            pathlib.Path: The joined base path.
        """
        root_dir = PathHelper.rootDir()
        if not paths:
            return root_dir
        return PathHelperInternals.join_path(root_dir, *paths)

    @staticmethod
    def buildDataPath(relative_path: Union[str, List[str]], *args: str) -> pathlib.Path:
        """
        Get the absolute path to a file in the data directory.
        Args:
            relative_path: Relative path from the data directory, either as a string or list of path components.
            *args: Additional path components to join if relative_path is a string.
        Returns:
            pathlib.Path: The absolute path to the file.
        """
        if args:
            relative_path = [relative_path] + list(args)
        data_path = PathHelper.dataDir()
        if isinstance(relative_path, list):
            return PathHelperInternals.join_path(data_path, *relative_path)
        return PathHelperInternals.join_path(data_path, relative_path)

    @staticmethod
    def buildAssetPath(relative_path: Union[str, List[str]], *args: str) -> pathlib.Path:
        """
        Get the absolute path to a file in the assets directory.
        Args:
            relative_path: Relative path from the assets directory, either as a string or list of path components.
            *args: Additional path components to join if relative_path is a string.
        Returns:
            pathlib.Path: The absolute path to the file.
        """
        if args:
            relative_path = [relative_path] + list(args)
        assets_path = PathHelper.assetsDir()
        if isinstance(relative_path, list):
            return PathHelperInternals.join_path(assets_path, *relative_path)
        return PathHelperInternals.join_path(assets_path, relative_path)

    @staticmethod
    def buildVendorPath(relative_path: Union[str, List[str]], *args: str) -> pathlib.Path:
        """
        Get the absolute path to a file in the vendor directory.
        Args:
            relative_path: Relative path from the vendor directory, either as a string or list of path components.
            *args: Additional path components to join if relative_path is a string.
        Returns:
            pathlib.Path: The absolute path to the file.
        """
        if args:
            relative_path = [relative_path] + list(args)
        vendor_path = PathHelper.vendorDir()
        if isinstance(relative_path, list):
            return PathHelperInternals.join_path(vendor_path, *relative_path)
        return PathHelperInternals.join_path(vendor_path, relative_path)

    @staticmethod
    def listDir(directory: Union[str, pathlib.Path], pattern: Optional[str] = None) -> List[pathlib.Path]:
        """
        List all files and directories in the specified directory, with optional pattern matching.
        Args:
            directory: The directory to list.
            pattern: Optional glob pattern to filter results (e.g., "*.txt").
        Returns:
            List[pathlib.Path]: List of paths in the directory.
        """
        if pattern:
            return PathHelperInternals.glob_path(directory, pattern)
        return PathHelperInternals.iter_dir(directory)

    @staticmethod
    def isFile(path: Union[str, pathlib.Path]) -> bool:
        """
        Check if the path points to a file.
        Args:
            path: The path to check.
        Returns:
            bool: True if path is a file, False otherwise.
        """
        return PathHelperInternals.getPathIsFile(path)

    @staticmethod
    def isExecutable(path: Union[str, pathlib.Path]) -> bool:
        """
        Check if the path points to an executable file.
        Args:
            path: The path to check.
        Returns:
            bool: True if path is an executable file, False otherwise.
        """
        path = PathHelperInternals.create_path_obj(path)
        if not PathHelperInternals.getPathIsFile(path):
            return False
        if platform.system() == 'Windows':
            extensions = os.environ.get('PATHEXT', '').lower().split(os.pathsep)
            _, ext = os.path.splitext(path)
            return ext.lower() in extensions
        return bool(os.stat(path).st_mode & stat.S_IXUSR)

    @staticmethod
    def isDir(path: Union[str, pathlib.Path]) -> bool:
        """
        Check if the path points to a directory.
        Args:
            path: The path to check.
        Returns:
            bool: True if path is a directory, False otherwise.
        """
        return PathHelperInternals.getPathIsDir(path)

    @staticmethod
    def isFileExists(path: Union[str, pathlib.Path]) -> bool:
        """
        Check if a file exists.
        Args:
            path: The path to check.
        Returns:
            bool: True if file exists, False otherwise.
        """
        return PathHelperInternals.getPathExists(path) and PathHelperInternals.getPathIsFile(path)

    @staticmethod
    def isDirExists(path: Union[str, pathlib.Path]) -> bool:
        """
        Check if a directory exists.
        Args:
            path: The path to check.
        Returns:
            bool: True if directory exists, False otherwise.
        """
        return PathHelperInternals.getPathExists(path) and PathHelperInternals.getPathIsDir(path)

    @staticmethod
    def getFileName(path: Union[str, pathlib.Path]) -> str:
        """
        Get the filename from a path.
        Args:
            path: The path to get the filename from.
        Returns:
            str: The filename.
        """
        return PathHelperInternals.get_path_name(path)

    @staticmethod
    def getFileNameWithoutExtension(path: Union[str, pathlib.Path]) -> str:
        """
        Get the filename without extension from a path.
        Args:
            path: The path to get the filename from.
        Returns:
            str: The filename without extension.
        """
        return PathHelperInternals.get_path_stem(path)

    @staticmethod
    def ensureParentDirExists(file_path: Union[str, pathlib.Path]) -> pathlib.Path:
        """
        Ensure that the parent directory of a file path exists, creating it if necessary.
        Works correctly with symlinked directories.
        Args:
            file_path: The file path whose parent directory should exist.
        Returns:
            pathlib.Path: The parent directory path that was checked/created.
        """
        path_obj = PathHelperInternals.create_path_obj(file_path)
        parent_dir = PathHelperInternals.get_path_parent(path_obj)
        if not PathHelperInternals.getPathExists(parent_dir):
            root_dir = PathHelper.rootDir()
            try:
                try:
                    relative_path = parent_dir.relative_to(root_dir)
                    PathHelperInternals.make_dirs(parent_dir)
                except ValueError:
                    is_in_symlink = False
                    test_path = parent_dir
                    while len(test_path.parts) > 1:
                        if PathHelperInternals.getPathIsSymlink(test_path):
                            is_in_symlink = True
                            break
                        test_path = PathHelperInternals.get_path_parent(test_path)
                    if is_in_symlink:
                        PathHelperInternals.make_dirs(parent_dir)
                    else:
                        import warnings
                        warnings.warn(f'Creating directory outside project root: {parent_dir}')
                        PathHelperInternals.make_dirs(parent_dir)
            except (PermissionError, OSError) as e:
                import warnings
                warnings.warn(f'Failed to create directory: {parent_dir} - {str(e)}')
        return parent_dir

    @staticmethod
    def readJson(param: Union[str, pathlib.Path]) -> Optional[Union[Dict[str, Any], List[Any]]]:
        """
        Read JSON from a file path.
        Args:
            param:Union[str, pathlib.Path]: Path to the JSON file.
        Returns:
            Optional[Union[Dict[str, Any], List[Any]]]: Content of the JSON file or None if error.
        Raises:
            ValueError: If the file path is invalid.
        """
        if str(param).endswith('.json') and PathHelper.isFileExists(param):
            with open(param, 'r', encoding='utf-8') as f:
                return json.load(f)
        else:
            raise ValueError('Invalid JSON file path')

    @staticmethod
    def isSymlink(path: Union[str, pathlib.Path]) -> bool:
        """
        Check if the path is a symlink.
        Args:
            path: The path to check.
        Returns:
            bool: True if path is a symlink, False otherwise.
        """
        return PathHelperInternals.getPathIsSymlink(path)

    @staticmethod
    def getSymlinkTarget(path: Union[str, pathlib.Path]) -> Optional[pathlib.Path]:
        """
        Get the target of a symlink. Returns None if the path is not a symlink.
        Args:
            path: The symlink path to resolve.
        Returns:
            Optional[pathlib.Path]: The target path of the symlink, or None if not a symlink.
        """
        path_obj = PathHelperInternals.create_path_obj(path)
        if PathHelperInternals.getPathIsSymlink(path_obj):
            return PathHelperInternals.get_path_resolve(path_obj)
        return None

    @staticmethod
    def isUsingSymlinkedCore() -> bool:
        """
        Check if the current core directory is a symlink.
        Returns:
            bool: True if the core directory is a symlink, False otherwise.
        """
        return PathHelper._detect_symlink()

    @staticmethod
    def debugPathInfo() -> str:
        """
        Get debug information about the current path configuration.
        Useful for troubleshooting symlink and path issues.
        Returns:
            str: A formatted string with path information.
        """
        file_path = PathHelper._get_file_path()
        root_dir = PathHelper.rootDir()
        is_symlink = PathHelper.isUsingSymlinkedCore()
        cwd = PathHelperInternals.get_cwd()
        info = [
            f'Current working directory: {cwd}',
            f'Utils.py location: {file_path}',
            f'Detected root directory: {root_dir}',
            f'Using symlinked core: {("Yes" if is_symlink else "No")}',
            f'Data directory: {PathHelper.dataDir()}',
            f'Assets directory: {PathHelper.assetsDir()}',
            f'Vendor directory: {PathHelper.vendorDir()}',
        ]
        core_dir = PathHelperInternals.join_path(root_dir, 'core')
        if PathHelperInternals.getPathIsSymlink(core_dir):
            core_target = PathHelperInternals.get_path_resolve(core_dir)
            info.append(f'Core directory is a symlink: {core_dir} -> {core_target}')
        services_dir = PathHelperInternals.join_path(root_dir, 'services')
        if PathHelperInternals.getPathExists(services_dir) and PathHelperInternals.getPathIsSymlink(services_dir):
            services_target = PathHelperInternals.get_path_resolve(services_dir)
            info.append(f'Services directory is a symlink: {services_dir} -> {services_target}')
        return '\n'.join(info)


class OsHelper:
    @staticmethod
    def openWithDefaultProgram(file_path: Union[str, pathlib.Path]) -> bool:
        """
        Opens a file with the default associated program based on the operating system.
        Args:
            file_path: Path to the file that should be opened
        Returns:
            bool: True if successful, False otherwise
        Raises:
            FileNotFoundError: If the specified file does not exist
        """
        path_obj = PathHelperInternals.create_path_obj(file_path)
        if not PathHelperInternals.getPathExists(path_obj):
            raise FileNotFoundError(f'File not found: {path_obj}')
        try:
            if platform.system() == 'Windows':
                os.startfile(str(path_obj))
            elif platform.system() == 'Darwin':
                subprocess.run(['open', str(path_obj)], check=True)
            elif platform.system() == 'Linux':
                subprocess.run(['xdg-open', str(path_obj)], check=True)
            else:
                return False
            return True
        except Exception as e:
            print(f'Error opening file: {e}')
            return False


class PythonHelper:
    @staticmethod
    def is_type_compatible(value, annotation):
        try:
            return isinstance(value, annotation)
        except TypeError:
            if hasattr(annotation, '__origin__'):
                origin = annotation.__origin__
                return isinstance(value, origin)
            return False

    @staticmethod
    def dataclass2Json(data_object: T, anotherDict: Optional[Dict[str, Any]] = None) -> str:
        """
        Convert a dataclass object to a JSON string.
        Args:
            data_object: The dataclass object to convert.
            anotherDict: Additional dictionary to update the dataclass dict with.
        Returns:
            str: The JSON string representation of the dataclass.
        Raises:
            TypeError: If the provided object is not a dataclass.
        """
        if not is_dataclass(data_object):
            raise TypeError('Expected a dataclass instance')
        data = asdict(data_object)
        if anotherDict:
            data.update(anotherDict)
        return json.dumps(data, ensure_ascii=False, indent=2)

    @staticmethod
    def dataclass2Dict(data_object: T, *anotherDict: Optional[Dict[str, Any]]) -> Dict[str, Any]:
        if not is_dataclass(data_object):
            raise TypeError('Expected a dataclass instance')
        data = asdict(data_object)
        if anotherDict:
            data.update(*anotherDict)
        return data

    @staticmethod
    def getEnvOfProcess(pid):
        try:
            import win32api
            import win32con
            h_process = win32api.OpenProcess(win32con.PROCESS_QUERY_INFORMATION | win32con.PROCESS_VM_READ, False, pid)
            env_block = win32process.GetEnvironmentStrings(h_process)
            return env_block
        except Exception as e:
            return f'Error: {e}'

    @staticmethod
    def killProcessById(pid):
        import os
        if os.name == 'nt':
            subprocess.call(['taskkill', '/F', '/T', '/PID', str(pid)])
        else:
            subprocess.call(['kill', str(pid)])

    @staticmethod
    def killAllProcessByName(name):
        import os
        if os.name == 'nt':
            subprocess.call(['taskkill', '/F', '/IM', name])
        else:
            subprocess.call(['pkill', '-9', name])

    @staticmethod
    def getProcessIdsByName(name):
        import psutil
        return [p.pid for p in psutil.process_iter() if p.name() == name]

    @staticmethod
    def getProcessListByName(name):
        import psutil
        return [p for p in psutil.process_iter() if p.name() == name]

    @staticmethod
    def func_get_args():
        return inspect.getargvalues(inspect.currentframe()).locals.values()

    @staticmethod
    def env(key, type_, default=None):
        from os import environ
        if key not in environ:
            return default
        val = environ[key]
        if type_ == str:
            return val
        elif type_ == bool:
            if val.lower() in ['1', 'true', 'yes', 'y', 'ok', 'on']:
                return True
            if val.lower() in ['0', 'false', 'no', 'n', 'nok', 'off']:
                return False
            raise ValueError("Invalid environment variable '%s' (expected a boolean): '%s'" % (key, val))
        elif type_ == int:
            try:
                return int(val)
            except ValueError:
                raise ValueError("Invalid environment variable '%s' (expected an integer): '%s'" % (key, val)) from None

    @staticmethod
    def mergeDicts(dict1, dict2):
        merged = dict1.copy()
        for key, value in dict2.items():
            if key in merged:
                mergeResult = None
                if isinstance(merged[key], list) and isinstance(value, list):
                    mergeResult = merged[key].extend(value)
                if isinstance(value, dict) and isinstance(merged[key], dict):
                    mergeResult = PythonHelper.mergeDicts(merged[key], value)
                merged[key] = mergeResult if mergeResult else value
            else:
                merged[key] = value
        return merged

    @staticmethod
    def strGetBetween(s: str, before: str, after: str) -> str:
        return s[s.find(before) + len(before) : s.find(after)]

    @staticmethod
    def createFairRandomChooser(items: List[T]) -> Callable[[], T]:
        """
        Tạo một hàm chọn ngẫu nhiên đảm bảo mỗi phần tử được chọn ít nhất một lần
        trước khi bất kỳ phần tử nào được chọn lần thứ hai, sử dụng NumPy.
        Args:
            items: Danh sách các phần tử cần chọn
        Returns:
            Một hàm chọn ngẫu nhiên
        """
        if len(items) == 0:
            raise ValueError('Input list is empty.')
        items = np.array(items)
        counts = np.zeros(len(items), dtype=np.int32)
        def chooser():
            min_count = np.min(counts)
            mask = counts == min_count
            candidate_indices = np.where(mask)[0]
            random_idx = np.random.choice(candidate_indices)
            counts[random_idx] += 1
            return items[random_idx]
        return chooser

    @staticmethod
    def simpleFormatUuid(uuid: Union[str, UUID]) -> str:
        return str(uuid).replace('-', '')[:8]

    @staticmethod
    def simpleFormatCcNumber(num) -> str:
        return str(num)[:4] + '__' + str(num)[-4:]

    @staticmethod
    def generateRandomString(length: int = 8) -> str:
        import random
        import string
        characters = string.ascii_letters + string.digits
        return ''.join((random.choice(characters) for _ in range(length)))


def isInDebugEnv() -> bool:
    """
    Check if application is running in debug mode via PYTHONUNBUFFERED environment variable.
    Returns:
        bool: True if in debug mode, False otherwise.
    """
    return os.getenv('PYTHONUNBUFFERED', '0') == '1'


class WidgetUtils:
    @staticmethod
    def _defaultOkButton(msg_box: QMessageBox):
        return WidgetUtils._defaultButton(msg_box, QMessageBox.Ok, moveCursor=True, keepOnTop=True)

    @staticmethod
    def _defaultButton(msg_box: QMessageBox, button: QMessageBox.StandardButton = QMessageBox.Ok, moveCursor=False, keepOnTop=False):
        msg_box.setWindowIcon(AppHelper.getAppIcon())
        msg_box.setDefaultButton(button)
        msg_box.setEscapeButton(button)
        msg_box.setStandardButtons(button)
        if keepOnTop:
            msg_box.setWindowFlag(Qt.WindowStaysOnTopHint)
        msg_box.setFocus()
        if moveCursor:
            def move_cursor_to_btn():
                ok_button = msg_box.button(button)
                if ok_button:
                    from PySide6.QtGui import QCursor
                    QCursor.setPos(ok_button.mapToGlobal(ok_button.rect().center()))
            QTimer.singleShot(150, move_cursor_to_btn)
        return msg_box

    @staticmethod
    def _createMsgBox(controller=None):
        msg_box = QMessageBox(controller)
        msg_box.setWindowIcon(AppHelper.getAppIcon())
        return msg_box

    @staticmethod
    def _activeMsgBox(msg_box: QMessageBox):
        def focus():
            msg_box.raise_()
            msg_box.activateWindow()
            msg_box.setWindowState(msg_box.windowState() & ~Qt.WindowMinimized | Qt.WindowActive)
        QTimer.singleShot(100, focus)

    @staticmethod
    def showAlertMsgBox(controller: None, msg: str = '', title: str = 'INFO', icon: int = QMessageBox.Information, createOnly=False, placeCursorAtDefaultBtn=False):
        msg_box = WidgetUtils._createMsgBox(controller)
        if placeCursorAtDefaultBtn:
            msg_box = WidgetUtils._defaultOkButton(msg_box)
        msg_box.setIcon(icon)
        msg_box.setWindowTitle(WidgetUtils.transQt(title, 'WidgetUtils'))
        msg_box.setText(WidgetUtils.transQt(msg, 'WidgetUtils'))
        if not createOnly:
            msg_box.exec()
            WidgetUtils._activeMsgBox(msg_box)
        return msg_box

    @staticmethod
    def showErrorMsgBox(
        controller=None, msg: str = 'Opps. Something went wrong', title: str = 'ERROR', icon: int = QMessageBox.Critical, createOnly=False, placeCursorAtDefaultBtn=False
    ):
        msg_box = WidgetUtils._createMsgBox(controller)
        if placeCursorAtDefaultBtn:
            msg_box = WidgetUtils._defaultOkButton(msg_box)
        msg_box.setIcon(icon)
        msg_box.setWindowIcon(AppHelper.getAppIcon())
        msg_box.setWindowTitle(WidgetUtils.transQt(title, 'WidgetUtils'))
        msg_box.setText(WidgetUtils.transQt(msg, 'WidgetUtils'))
        if not createOnly:
            msg_box.exec()
            WidgetUtils._activeMsgBox(msg_box)
        return msg_box

    @staticmethod
    def showYesNoMsgBox(
        controller: None, msg: str = 'Are you sure?', title: str = 'MESSAGE', icon: int = QMessageBox.Question, createOnly=False, defaultYes=False, escapeNo=False
    ) -> bool:
        msg_box = WidgetUtils._createMsgBox(controller)
        msg_box = WidgetUtils._defaultButton(msg_box, QMessageBox.Yes if defaultYes else QMessageBox.No, moveCursor=False, keepOnTop=True)
        msg_box.setIcon(icon)
        msg_box.setWindowTitle(WidgetUtils.transQt(title, 'WidgetUtils'))
        msg_box.setText(WidgetUtils.transQt(msg, 'WidgetUtils'))
        msg_box.setStandardButtons(QMessageBox.Yes | QMessageBox.No)
        if escapeNo:
            msg_box.setEscapeButton(QMessageBox.No)
        if createOnly:
            return msg_box
        result = msg_box.exec()
        WidgetUtils._activeMsgBox(msg_box)
        return bool(result == QMessageBox.Yes)

    @staticmethod
    def transQt(msg: str, name_space: str = None) -> str:
        name_space = name_space if name_space is not None else 'WidgetUtils'
        return QCoreApplication.translate(name_space, msg)


class UrlHelper:
    """
    Helper class for URL operations and manipulations
    """

    @staticmethod
    def getUriComponents(string: str, components: List[URIComponent]) -> Dict[URIComponent, str]:
        """
        Get specified URI components from a string
        Args:
            string: The URI string to parse
            components: List of URI components to extract
        Returns:
            Dictionary with requested components as keys and their values
        """
        from urllib.parse import urlparse
        result = {}
        if not string:
            return result
        parsed = urlparse(string)
        auth = parsed.netloc.split('@')[0] if '@' in parsed.netloc else ''
        username = auth.split(':')[0] if ':' in auth else auth
        password = auth.split(':')[1] if ':' in auth else ''
        for component in components:
            if component == URIComponent.SCHEME:
                result[component] = parsed.scheme
            elif component == URIComponent.HOST:
                host = parsed.netloc
                if '@' in host:
                    host = host.split('@')[1]
                if ':' in host:
                    host = host.split(':')[0]
                result[component] = host
            elif component == URIComponent.PORT:
                port = parsed.netloc.split(':')[-1] if ':' in parsed.netloc.split('@')[-1] else ''
                result[component] = port
            elif component == URIComponent.PATH:
                result[component] = parsed.path
            elif component == URIComponent.QUERY:
                result[component] = parsed.query
            elif component == URIComponent.FRAGMENT:
                result[component] = parsed.fragment
            elif component == URIComponent.USERNAME:
                result[component] = username
            elif component == URIComponent.PASSWORD:
                result[component] = password
        return Box(result, box_dots=True)


class ProxyDeadError(Exception):
    """Exception raised when proxy connection fails"""

    pass


@dataclass
class ProxyInfo:
    """Dataclass containing proxy information"""

    PROTOCOL: str = 'SOCKS5'
    HOST: str = ''
    PORT: str = ''
    USER: str = ''
    PWD: str = ''

    @property
    def TYPE(self) -> str:
        """Alias for PROTOCOL"""
        return self.PROTOCOL


@dataclass
class ProxyCheckResult:
    """Dataclass containing proxy check results"""

    original: str = ''
    proxied: str = ''
    isChanged: bool = False


class ProxyHelper:
    """Helper class for proxy operations"""

    @staticmethod
    def parseProxyString(proxy_string: str) -> ProxyInfo:
        """
        Parse proxy string and return ProxyInfo object.
        Supported formats:
        - "proto://host:port" (e.g., "socks5://127.0.0.1:1080")
        - "proto://user:pwd@host:port" (e.g., "socks5://user:pass@127.0.0.1:1080")
        - "host:port" (e.g., "127.0.0.1:1080")
        - "host:port:user:password" (e.g., "127.0.0.1:1080:user:pass")
        - "user:pwd@host:port" (e.g., "user:pass@127.0.0.1:1080")
        Args:
            proxy_string: Proxy string in various formats
        Returns:
            ProxyInfo: Parsed proxy information
        """
        if not proxy_string:
            raise ValueError('Proxy string cannot be empty')
        proxy_info = ProxyInfo()
        if '://' in proxy_string:
            from urllib.parse import urlparse
            parsed = urlparse(proxy_string)
            if parsed.scheme:
                proxy_info.PROTOCOL = parsed.scheme.upper()
            netloc = parsed.netloc
            if '@' in netloc:
                auth_part, host_part = netloc.split('@', 1)
                if ':' in auth_part:
                    proxy_info.USER, proxy_info.PWD = auth_part.split(':', 1)
                else:
                    proxy_info.USER = auth_part
            else:
                host_part = netloc
            if ':' in host_part:
                proxy_info.HOST, proxy_info.PORT = host_part.split(':', 1)
            else:
                proxy_info.HOST = host_part
                proxy_info.PORT = '1080'
        elif '@' in proxy_string:
            auth_part, host_part = proxy_string.split('@', 1)
            if ':' in auth_part:
                proxy_info.USER, proxy_info.PWD = auth_part.split(':', 1)
            else:
                proxy_info.USER = auth_part
            if ':' in host_part:
                proxy_info.HOST, proxy_info.PORT = host_part.split(':', 1)
            else:
                raise ValueError(f'Invalid proxy format: missing port in {proxy_string}')
        else:
            parts = proxy_string.split(':')
            if len(parts) < 2:
                raise ValueError(f'Invalid proxy format: {proxy_string}')
            proxy_info.HOST = parts[0]
            proxy_info.PORT = parts[1]
            if len(parts) >= 3:
                proxy_info.USER = parts[2]
            if len(parts) >= 4:
                proxy_info.PWD = parts[3]
        return proxy_info

    @staticmethod
    def setChromiumProxy(proxy_string: str, chromium_options: 'DrissionPage._configs.chromium_options.ChromiumOptions') -> Any:
        """
        Set proxy for ChromiumOptions.
        Args:
            proxy_string: Proxy string in various formats:
                - "proto://host:port" (e.g., "socks5://127.0.0.1:1080")
                - "proto://user:pwd@host:port" (e.g., "socks5://user:pass@127.0.0.1:1080")
                - "host:port" (e.g., "127.0.0.1:1080")
                - "host:port:user:password" (e.g., "127.0.0.1:1080:user:pass")
            chromium_options: ChromiumOptions object to configure
        Returns:
            ChromiumOptions: Configured ChromiumOptions object
        """
        proxy_info = ProxyHelper.parseProxyString(proxy_string)
        if not proxy_info.HOST or not proxy_info.PORT:
            return chromium_options
        proxy_str = f'{proxy_info.HOST}:{proxy_info.PORT}'
        protocol = proxy_info.PROTOCOL.lower()
        chromium_options.set_argument(f'--proxy-server={protocol}://{proxy_str}')
        chromium_options.set_argument(f'--host-resolver-rules=MAP * 0.0.0.0 , EXCLUDE {proxy_info.HOST}, EXCLUDE 127.0.0.1')
        if proxy_info.USER and proxy_info.PWD:
            chromium_options.set_pref('gologin.proxy', {'username': proxy_info.USER, 'password': proxy_info.PWD})
        return chromium_options

    @staticmethod
    def checkProxyConnection(proxy_string: str, check_url: str = 'https://api.ipify.org/') -> ProxyCheckResult:
        """
        Check proxy connection and return IP comparison result.
        Args:
            proxy_string: Proxy string in various formats:
                - "proto://host:port" (e.g., "socks5://127.0.0.1:1080")
                - "proto://user:pwd@host:port" (e.g., "socks5://user:pass@127.0.0.1:1080")
                - "host:port" (e.g., "127.0.0.1:1080")
                - "host:port:user:password" (e.g., "127.0.0.1:1080:user:pass")
            check_url: URL to check IP from
        Returns:
            ProxyCheckResult: Result containing original IP, proxied IP, and change status
        Raises:
            ProxyDeadError: If proxy connection fails
        """
        import requests
        try:
            original_response = requests.get(check_url, timeout=5)
            if original_response.status_code != 200:
                raise ProxyDeadError(f'Failed to get original IP: {original_response.status_code}')
            original_ip = original_response.text.strip()
            proxy_info = ProxyHelper.parseProxyString(proxy_string)
            protocol = proxy_info.PROTOCOL.lower()
            if proxy_info.USER and proxy_info.PWD:
                proxy_url = f'{protocol}://{proxy_info.USER}:{proxy_info.PWD}@{proxy_info.HOST}:{proxy_info.PORT}'
            else:
                proxy_url = f'{protocol}://{proxy_info.HOST}:{proxy_info.PORT}'
            proxy_dict = {'http': proxy_url, 'https': proxy_url}
            proxied_response = requests.get(check_url, proxies=proxy_dict, timeout=5)
            if proxied_response.status_code != 200:
                raise ProxyDeadError(f'Failed to get proxied IP: {proxied_response.status_code}')
            proxied_ip = proxied_response.text.strip()
            return ProxyCheckResult(original=original_ip, proxied=proxied_ip, isChanged=original_ip != proxied_ip)
        except ValueError:
            raise
        except (requests.exceptions.RequestException, curl_cffi.curl.CurlError) as e:
            raise ProxyDeadError(f'Proxy connection failed: {str(e)}\n{traceback.format_exc()}')
        except Exception as e:
            raise ProxyDeadError(f'Unexpected error during proxy check: {str(e)}\n{traceback.format_exc()}')


class URIComponent(Enum):
    """URI component types"""

    SCHEME = auto()
    HOST = auto()
    PORT = auto()
    PATH = auto()
    QUERY = auto()
    FRAGMENT = auto()
    USERNAME = auto()
    PASSWORD = auto()


class AppHelper:
    @staticmethod
    def getConfig() -> 'core.Config':
        from core.Config import Config
        config = Config()
        return config

    @staticmethod
    def getAppName() -> str:
        config = AppHelper.getConfig()
        return config.get('app.name', 'Qt Base App - by Zuko')

    @staticmethod
    def getAppVersion() -> str:
        config = AppHelper.getConfig()
        return config.get('app.version', '0.0.01')

    @staticmethod
    def getAppDisplayName() -> str:
        name = AppHelper.getAppName()
        version = AppHelper.getAppVersion()
        return f'{name} | v{version}'

    @staticmethod
    def getAppIconPath():
        return PathHelper.buildAssetPath('icon.png')

    @staticmethod
    def getAppIcon() -> QIcon:
        icon_path = AppHelper.getAppIconPath()
        return QIcon(str(icon_path))
