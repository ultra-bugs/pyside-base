# CLI Utility Scripts

This project includes several Python scripts in the `scripts/` directory to automate common development tasks. These scripts are typically called via Pixi tasks, but can also be run directly.

## 1. Generators (`generate.py` & `task_generator.py`)

Tools to quick-scaffold new components.

### Generic Generator
Used to create Controllers, Services, and Components.

```bash
# Syntax
pixi run gen <type> <Name>

# Examples
pixi run gen controller UserProfile  # -> app/controllers/UserProfileController.py
pixi run gen service Authentication  # -> app/services/AuthenticationService.py
pixi run gen component CustomBtn     # -> app/components/CustomBtn.py
```

### Task Generator
Used to create Tasks and Steps for the TaskSystem.

```bash
# Create a new Task
python scripts/task_generator.py task DataSync --description "Synchronize data"
# -> services/tasks/DataSyncTask.py

# Create a new Step
python scripts/task_generator.py step DownloadFile --description "Download file from URL"
# -> services/tasks/steps/DownloadFileStep.py
```

## 2. UI Compilation (`compile_ui.py`)

This script scans the entire `resources/` and `app/` directories to compile `.ui` (Qt Designer) and `.qrc` (Resource) files into Python files.

-   **Input**: `*.ui`, `*.qrc`
-   **Output**: `ui_*.py`, `*_rc.py`

```bash
# Run via Pixi (shorthand)
pixi run uic
```

> **Note**: This script should be run every time you modify the interface in Qt Designer. The `pixi run dev` command automatically runs this script before starting the app.

## 3. App Info Configuration (`set_app_info.py`)

A utility script to update application information (Name, Version) in the configuration file without manually editing the code.

```bash
# Update app name
python scripts/set_app_info.py --name "My Super App"

# Update version
python scripts/set_app_info.py --version "1.0.5"
```
