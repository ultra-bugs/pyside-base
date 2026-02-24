import os
import platform
import subprocess
from pathlib import Path


def main():
    # Change to project root (parent of scripts directory)
    project_root = Path(__file__).parent.parent
    os.chdir(project_root)
    # Detect platform and select appropriate fpyglob executable
    system = platform.system()
    if system == 'Windows':
        fpyglob = 'scripts/fpyglob-windows-amd64.exe'
    elif system == 'Linux':
        fpyglob = 'scripts/fpyglob-linux-amd64'
    elif system == 'Darwin':
        fpyglob = 'scripts/fpyglob-macos-amd64'
    else:
        print(f'Unsupported platform: {system}')
        return 1
    # Execute fpyglob to find and delete .pyc files and __pycache__ directories
    try:
        result = subprocess.run([fpyglob], capture_output=True, text=True, check=True)
        print(result.stdout)
        if result.stderr:
            print(result.stderr)
        print('Cleaned .pyc files and __pycache__ directories')
        return 0
    except subprocess.CalledProcessError as e:
        print(f'Error running fpyglob: {e}')
        print(e.stderr)
        return 1
    except FileNotFoundError:
        print(f'fpyglob executable not found: {fpyglob}')
        return 1


if __name__ == '__main__':
    exit(main())
