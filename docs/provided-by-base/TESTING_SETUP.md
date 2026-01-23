# Testing Setup

## 🚀 Quick Start
This document provides a quick reference for running tests in the Base Framework.

For the **authoritative and detailed guide**, including advanced configuration and troubleshooting, please refer to the [Core Testing Guide](../../core/taskSystem/docs/testing.md).

## Test Organization
- **App Tests (`tests/`)**: Tests for your application logic.
- **Core Tests (`tests_core/`)**: Tests for the base framework internals.

## Running Tests

### Using Pixi (Recommended)
```bash
# Run all tests
pixi run python scripts/run_pytest.py tests/
```

### Using Python/Pytest Directly
```bash
# Run app tests
python scripts/run_pytest.py tests/

# Run core tests (if needed)
python scripts/run_pytest.py tests_core/
```

## Dependencies
Test dependencies are managed in `pyproject.toml`.
- `pytest`
- `pytest-qt`
- `pytest-mock`
- `pytest-cov`
- `pytest-asyncio`

Run `pixi install` to ensure all are available.
