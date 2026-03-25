# Pixi Guide

This document provides instructions on using **Pixi** for managing environments and dependencies in the project, replacing the traditional `pip` + `venv` workflow.

## 1. What is Pixi?

Pixi is a high-performance package and environment management tool. In this project, Pixi helps to:
- **Synchronize environments**: Ensure all developers are running the same Python version and libraries.
- **Automate tasks**: Run tests, lint, and build UI with a single command.
- **Cross-platform**: Works well on Windows, Linux, and macOS.

You need to install Pixi before starting: [Installation Guide](https://pixi.sh/latest/#installation) | [Official Documentation](https://pixi.sh/latest/)

> **Important Note**: This project uses a `skeleton` structure managed by `pixi`. You must use `pixi` for **EVERY COMMAND** you enter into the console.

## 2. Pixi vs Pip/Venv

If you are used to using `pip` and `venv`, here is a quick comparison table:

| Feature | Pip + Venv | Pixi |
| :--- | :--- | :--- |
| **Create environment** | `python -m venv venv` | Automatic when running `pixi install` or `pixi run` |
| **Activate env** | `venv\Scripts\activate` | `pixi shell` (or `pixi run <cmd>` without needing to activate) |
| **Install library** | `pip install <package>` | `pixi add <package>` |
| **Uninstall library** | `pip uninstall <package>` | `pixi remove <package>` |
| **Config file** | `requirements.txt` | `pixi.toml` (main) & `pixi.lock` (exact versions) |
| **Speed** | Normal | **Super fast** (thanks to using `uv` underneath) |

## 3. Pixi & uv

Pixi uses [uv](https://github.com/astral-sh/uv) - an extremely fast Python package installer and resolver written in Rust. This means installing packages and creating environments happens almost instantly. You don't need to install `uv` separately; Pixi has it built-in.

## 4. Quick Guide (Cheat Sheet)

### Getting Started
```bash
# Install dependencies (creates environment in .pixi/)
pixi install
```

### Running the Application & Tools
Instead of activating the environment, you can run commands directly via `pixi run`:

```bash
# Run the application
pixi run start

# Run in development mode (auto compiles UI)
pixi run dev

# Run tests
pixi run test

# Compile UI
pixi run compile-ui
```

### Managing Dependencies
```bash
# Add python package (from conda-forge or pypi)
pixi add requests
pixi add --pypi python-dotenv

# Add dev package (e.g., pytest)
pixi add --feature dev pytest
```

### Enter Shell (Similar to `activate`)
```bash
# Open a new terminal with the environment activated
pixi shell

# After entering the shell, you can call python directly
python main.py
```

## 5. Troubleshooting for Beginners

- **Q: I typed `python main.py` and it reported a missing library error?**
    - A: You haven't activated the environment. Use `pixi run start` OR type `pixi shell` first.
- **Q: Can I install a library using `pip install`?**
    - A: **You shouldn't**. Use `pixi add --pypi <package-name>` so Pixi records it in `pixi.toml`. If you manually use `pip install`, your co-workers won't have that library.
