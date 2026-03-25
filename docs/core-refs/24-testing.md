# Testing Guide

> [!IMPORTANT]
> This skeleton project used `pixi` for manage dependencies, run CLI tasks. You'll need `pixi` for every LINEs you entering to COMMAND console. So, usage of `pixi` here [22-pixi-guide.md](22-pixi-guide.md)

**IMPORTANT: The test_core directory mentioned below is exclusively for the framework. Application's test cases should be put into the `tests` directory only.**

## Running Tests

### Windows Users

Due to a `pyreadline` compatibility issue with Python 3.10+, use the wrapper script:

```powershell
# Run all tests
pixi run test

# Run overall checks (including lint, type-check, tests)
pixi run check

# Run with coverage
pixi run test-cov
```

### Linux/macOS Users

You can use pytest directly (inside pixi shell or via pixi run):

```bash
pixi run test
pixi run test-cov
```

## Test Structure

```
tests_core/
├── conftest.py                    # Pytest configuration and fixtures
├── pytest.ini                     # Pytest settings
├── requirements.txt               # Test dependencies
└── task_system/
    ├── __init__.py
    ├── test_TaskStatus.py         # TaskStatus enum tests
    ├── test_Exceptions.py         # Exception tests
    └── test_AbstractTask.py       # AbstractTask tests
```

## Writing Tests

### Using Qt Fixtures

```python
def test_with_qt_signals(qtbot):
    """Test Qt signals with qtbot fixture."""
    task = ConcreteTask(name="Test")
    
    with qtbot.waitSignal(task.statusChanged, timeout=1000):
        task.setStatus(TaskStatus.RUNNING)
    
    assert task.status == TaskStatus.RUNNING
```

### Using Mock Config

```python
def test_with_config(mock_config):
    """Test with mocked Config."""
    mock_config.get.return_value = "test_value"
    
    # Your test code
    value = mock_config.get("some.key")
    assert value == "test_value"
```

### Using Mock Publisher

```python
def test_with_publisher(mock_publisher):
    """Test with mocked Publisher."""
    mock_publisher.notify.return_value = None
    
    # Your test code
    mock_publisher.notify("TestEvent", data="test")
    mock_publisher.notify.assert_called_once()
```

## Test Markers

```python
@pytest.mark.slow
def test_slow_operation():
    """Mark test as slow."""
    pass


@pytest.mark.integration
def test_integrationflow():
    """Mark test as integration test."""
    pass


@pytest.mark.qt
def test_qt_feature(qtbot):
    """Mark test as requiring Qt."""
    pass
```

Run specific markers:

```bash
# Skip slow tests
pixi run test -m "not slow"

# Run only integration tests
pixi run test -m "integration"
```

## Coverage Reports

Generate HTML coverage report:

```bash
pixi run test-cov
```

Open `htmlcov/index.html` in browser to view detailed coverage.

## Troubleshooting

### pyreadline Error on Windows

If you see:

```
AttributeError: module 'collections' has no attribute 'Callable'
```

**Solution**: Use `scripts/run_pytest.py` wrapper script:

```powershell
pixi run test [arguments]
```

### Qt Application Already Running

If you see:

```
RuntimeError: A QApplication instance already exists
```

**Solution**: Use the `qapp` fixture which handles this:

```python
def test_my_feature(qapp):
    # qapp is already created and managed
    pass
```

### Import Errors

If tests can't find modules:

**Solution**: The `conftest.py` adds project root to path automatically. If still having issues, check:

```python
import sys
from pathlib import Path

project_root = Path(__file__).parent.parent
assert str(project_root) in sys.path
```

## Best Practices

1. **Test Naming**: Use descriptive names starting with `test_`
2. **One Assertion Per Test**: Keep tests focused
3. **Use Fixtures**: Leverage pytest fixtures for setup/teardown
4. **Mock External Dependencies**: Don't test external services
5. **Test Edge Cases**: Include boundary conditions and error cases
6. **Keep Tests Fast**: Use markers for slow tests
7. **Clean Up**: Ensure tests clean up resources (fixtures help)

## CI/CD Integration

Tests can be run in CI/CD pipelines:

```yaml
# Example GitHub Actions
- name: Run tests
  run: |
    pixi run check
```

## Adding New Tests

1. Create test file in appropriate directory
2. Import necessary fixtures from `conftest.py`
3. Write test functions with descriptive names
4. Use appropriate markers
5. Run tests to verify

Example:

```python
# tests_core/task_system/test_NewFeature.py

import pytest
from ..taskSystem import TaskStatus


def test_new_feature():
    """Test new feature behavior."""
    # Arrange
    # Act
    # Assert
    pass


@pytest.mark.qt
def test_new_feature_with_qt(qtbot):
    """Test new feature with Qt."""
    pass
```

## Resources

- [pytest documentation](https://docs.pytest.org/)
- [pytest-qt documentation](https://pytest-qt.readthedocs.io/)
- [PySide6 testing guide](https://doc.qt.io/qtforpython/tutorials/index.html)
